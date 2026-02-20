#!/usr/bin/env python3
"""
Bidirectional Rule-Based Sentence Transformation System (v2)

Extracts transformation rules in both C->R and R->C directions from events data,
applies them to CoNLL-U parsed sentences to produce transformed sentences,
and evaluates the results against actual parallel sentences.

v2 improvements:
  - 80/20 train/test split (deterministic by sentence index % 5)
  - N-gram language model for fluency scoring
  - Multi-hypothesis generation + candidate ranking
  - Constituency-tree-aware rule filtering
  - Bug fixes: verb-fronting, auxiliary doubling, over-deletion

Outputs:
  output/transformation-study/bidirectional-transformation/
  +-- tables/          # CSVs + .tex
  +-- figures/         # PNGs
  +-- rules/           # Rule inventories (JSON)
  +-- generated/       # Generated sentences per newspaper
  +-- evaluation/      # Detailed evaluation data
"""

import csv
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import Counter

# Project imports
sys.path.insert(0, str(Path(__file__).parent))
from config import BASE_DIR
from paths_config import NEWSPAPERS, CONLLU_FILES, CONST_FILES

from register_comparison.generation.bidirectional_rules import (
    BidirectionalRuleExtractor, RuleSet,
)
from register_comparison.generation.surface_realizer import SurfaceRealizer
from register_comparison.generation.sentence_transformer import SentenceTransformer
from register_comparison.generation.evaluator import (
    TransformationEvaluator, CorpusEvaluation,
)
from register_comparison.generation.constraint_resolver import ConstraintResolver
from register_comparison.generation.ngram_scorer import NgramScorer
from register_comparison.generation.hypothesis_generator import HypothesisGenerator
from register_comparison.generation.candidate_ranker import CandidateRanker


def log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {msg}")


# ------------------------------------------------------------------
# Train/Test split
# ------------------------------------------------------------------

def split_pairs(pairs, train_fraction: float = 0.8):
    """
    Deterministic train/test split using index modulo.

    Sentences where index % 5 == 0 go to test (20%).
    All others go to train (80%).

    Returns:
        (train_indices, test_indices, train_pairs, test_pairs)
    """
    train_indices = []
    test_indices = []
    train_pairs = []
    test_pairs = []

    for i, pair in enumerate(pairs):
        if i % 5 == 0:
            test_indices.append(i)
            test_pairs.append(pair)
        else:
            train_indices.append(i)
            train_pairs.append(pair)

    return train_indices, test_indices, train_pairs, test_pairs


class BidirectionalTransformationRunner:
    """Orchestrates the full bidirectional transformation pipeline (v2)."""

    def __init__(self):
        self.project_root = BASE_DIR
        self.output_base = self.project_root / 'output' / 'transformation-study' / 'bidirectional-transformation'
        self.tables_dir = self.output_base / 'tables'
        self.figures_dir = self.output_base / 'figures'
        self.rules_dir = self.output_base / 'rules'
        self.generated_dir = self.output_base / 'generated'
        self.evaluation_dir = self.output_base / 'evaluation'

        for d in [self.tables_dir, self.figures_dir, self.rules_dir,
                  self.generated_dir, self.evaluation_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.extractor = BidirectionalRuleExtractor(min_frequency=2, min_confidence=0.3)
        self.evaluator = TransformationEvaluator()
        self.realizer = SurfaceRealizer()
        self.all_evaluations: List[CorpusEvaluation] = []
        self.hypothesis_stats: Counter = Counter()  # which hypothesis wins
        self.scoring_records: List[Dict] = []  # per-sentence scoring data

    # ------------------------------------------------------------------
    # Step 1: Build inflection table (from train data only)
    # ------------------------------------------------------------------

    def build_inflection_table(self, train_conllu_files: Optional[List[Path]] = None):
        """Build inflection table from corpus CoNLL-U files."""
        log("Building inflection table from corpus CoNLL-U files...")
        all_conllu = []
        if train_conllu_files:
            all_conllu = train_conllu_files
        else:
            for newspaper in NEWSPAPERS:
                for register in ('canonical', 'headlines'):
                    path = CONLLU_FILES[newspaper][register]
                    if path.exists():
                        all_conllu.append(path)
                    else:
                        log(f"  Warning: {path} not found", "WARN")

        self.realizer.build_inflection_table(all_conllu)
        stats = self.realizer.get_statistics()
        log(f"  Inflection table: {stats['inflection_entries']} entries, "
            f"{stats['lemma_pos_entries']} lemma-pos fallbacks")

    # ------------------------------------------------------------------
    # Step 2: Extract rules for each newspaper
    # ------------------------------------------------------------------

    def extract_rules(self, newspaper: str) -> Tuple[RuleSet, RuleSet]:
        """Extract bidirectional rules from a newspaper's events."""
        events_csv = self._find_events_csv(newspaper)
        if not events_csv:
            log(f"  No events CSV found for {newspaper}", "ERROR")
            return RuleSet('C2R'), RuleSet('R2C')

        log(f"  Extracting rules from {events_csv.name}...")
        c2r, r2c = self.extractor.extract_both_directions(events_csv)

        # Save rules
        self.extractor.save_ruleset(c2r, self.rules_dir / newspaper)
        self.extractor.save_ruleset(r2c, self.rules_dir / newspaper)
        self.extractor.save_ruleset_csv(c2r, self.tables_dir)
        self.extractor.save_ruleset_csv(r2c, self.tables_dir)

        return c2r, r2c

    def _find_events_csv(self, newspaper: str) -> Optional[Path]:
        """Find the events_global.csv for a newspaper."""
        candidates = [
            self.project_root / 'output' / 'comparative-study' / 'events' / newspaper / 'events_global.csv',
            self.project_root / 'output' / newspaper / 'events_global.csv',
        ]
        for path in candidates:
            if path.exists():
                return path
        return None

    # ------------------------------------------------------------------
    # Step 3: Load CoNLL-U sentence pairs + constituency trees
    # ------------------------------------------------------------------

    def load_sentence_pairs(self, newspaper: str) -> List[Tuple[List[Dict], List[Dict]]]:
        """Load aligned canonical and headline sentence pairs from CoNLL-U."""
        try:
            from conllu import parse_incr
        except ImportError:
            log("conllu package not installed", "ERROR")
            return []

        can_path = CONLLU_FILES[newspaper]['canonical']
        hl_path = CONLLU_FILES[newspaper]['headlines']

        if not can_path.exists() or not hl_path.exists():
            log(f"  CoNLL-U files not found for {newspaper}", "ERROR")
            return []

        def load_sentences(path):
            sentences = []
            with open(path, 'r', encoding='utf-8') as f:
                for token_list in parse_incr(f):
                    tokens = []
                    for token in token_list:
                        tokens.append(dict(token))
                    sentences.append(tokens)
            return sentences

        canonical = load_sentences(can_path)
        headlines = load_sentences(hl_path)

        min_len = min(len(canonical), len(headlines))
        if len(canonical) != len(headlines):
            log(f"  Warning: mismatched sentence counts "
                f"(canonical={len(canonical)}, headline={len(headlines)}), "
                f"using {min_len}", "WARN")

        pairs = list(zip(canonical[:min_len], headlines[:min_len]))
        log(f"  Loaded {len(pairs)} sentence pairs for {newspaper}")
        return pairs

    def load_constituency_trees(self, newspaper: str,
                                register: str) -> List[Optional[str]]:
        """Load constituency trees for a newspaper/register."""
        const_path = CONST_FILES[newspaper][register]
        if not const_path.exists():
            log(f"  Constituency file not found: {const_path}", "WARN")
            return []

        trees = []
        current_lines = []
        in_tree = False

        with open(const_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.rstrip()
                # Skip sentence marker lines like "(sentence 1.1) ..."
                if line.startswith('(sentence '):
                    if current_lines:
                        trees.append('\n'.join(current_lines))
                        current_lines = []
                    in_tree = False
                    continue
                elif line.startswith('(ROOT') or line.startswith('(S'):
                    in_tree = True
                    current_lines = [line]
                elif line == '':
                    if current_lines:
                        trees.append('\n'.join(current_lines))
                        current_lines = []
                    in_tree = False
                elif in_tree:
                    current_lines.append(line)

        # Last tree
        if current_lines:
            trees.append('\n'.join(current_lines))

        log(f"  Loaded {len(trees)} constituency trees for {newspaper}/{register}")
        return trees

    # ------------------------------------------------------------------
    # Step 4: Build n-gram LM from training target sentences
    # ------------------------------------------------------------------

    def build_ngram_lm(self, train_pairs: List[Tuple[List[Dict], List[Dict]]],
                       direction: str) -> NgramScorer:
        """Build a trigram LM from the target-register sentences in the training set."""
        scorer = NgramScorer(n=3, smoothing=1.0)

        target_sentences = []
        for can_tokens, hl_tokens in train_pairs:
            target = hl_tokens if direction == 'C2R' else can_tokens
            text = ' '.join(t.get('form', '') for t in target if t.get('form', ''))
            target_sentences.append(text)

        scorer.train(target_sentences)
        stats = scorer.get_statistics()
        log(f"  N-gram LM ({direction}): vocab={stats['vocab_size']}, "
            f"contexts={stats['n_contexts']}")
        return scorer

    # ------------------------------------------------------------------
    # Step 5: Compute expected length ratio from training data
    # ------------------------------------------------------------------

    @staticmethod
    def compute_length_ratio(train_pairs: List[Tuple[List[Dict], List[Dict]]],
                             direction: str) -> float:
        """Compute average target_len / source_len from training data."""
        ratios = []
        for can_tokens, hl_tokens in train_pairs:
            source = can_tokens if direction == 'C2R' else hl_tokens
            target = hl_tokens if direction == 'C2R' else can_tokens
            if len(source) > 0:
                ratios.append(len(target) / len(source))
        return sum(ratios) / len(ratios) if ratios else 1.0

    # ------------------------------------------------------------------
    # Step 6: Transform and evaluate (v2 — hypothesis generation + ranking)
    # ------------------------------------------------------------------

    def transform_and_evaluate(self, newspaper: str, direction: str,
                               ruleset: RuleSet,
                               test_pairs: List[Tuple[List[Dict], List[Dict]]],
                               test_indices: List[int],
                               ngram_scorer: NgramScorer,
                               expected_length_ratio: float,
                               const_trees_source: List[Optional[str]]
                               ) -> CorpusEvaluation:
        """Transform test sentences using multi-hypothesis generation and ranking."""
        log(f"  Transforming {newspaper} [{direction}]: {len(test_pairs)} test pairs...")

        generator = HypothesisGenerator(ruleset, self.realizer, n_hypotheses=8)
        ranker = CandidateRanker(
            ngram_scorer,
            alpha=0.6,
            expected_length_ratio=expected_length_ratio,
        )

        text_pairs = []
        token_pairs = []
        actions_list = []

        for i, (can_tokens, hl_tokens) in enumerate(test_pairs):
            source = can_tokens if direction == 'C2R' else hl_tokens
            target_tokens = hl_tokens if direction == 'C2R' else can_tokens

            # Get constituency tree for source
            orig_idx = test_indices[i]
            tree_str = (const_trees_source[orig_idx]
                        if const_trees_source and orig_idx < len(const_trees_source)
                        else None)

            # Generate hypotheses
            hypotheses = generator.generate(source, const_tree_str=tree_str)

            # Source text for ranker
            source_text = ' '.join(
                t.get('form', '') for t in source if t.get('form', ''))

            # Rank and select best
            ranked = ranker.rank(hypotheses, source_text)
            best = ranked[0][0]
            best_score = ranked[0][1] if ranked else 0.0

            # Track hypothesis selection stats
            self.hypothesis_stats[best.hypothesis_id] += 1
            self.scoring_records.append({
                'sentence_idx': orig_idx,
                'newspaper': newspaper,
                'direction': direction,
                'selected_hypothesis': best.hypothesis_id,
                'combined_score': best_score,
                'n_actions': len(best.applied_actions),
            })

            # Reference text from the target register
            ref_text = ' '.join(t.get('form', '') for t in target_tokens
                                if t.get('form', ''))

            text_pairs.append((best.generated_text, ref_text))
            token_pairs.append((best.transformed_tokens, target_tokens))
            actions_list.append(len(best.applied_actions))

            if (i + 1) % 100 == 0:
                log(f"    Processed {i + 1}/{len(test_pairs)}...")

        # Evaluate
        evaluation = self.evaluator.evaluate_corpus(
            pairs=text_pairs,
            token_pairs=token_pairs,
            direction=direction,
            newspaper=newspaper,
            actions_list=actions_list,
        )

        # Save per-pair results
        self.evaluator.save_corpus_evaluation(evaluation, self.evaluation_dir)

        # Save generated sentences CSV
        gen_csv = self.generated_dir / f"{direction.lower()}_results_{newspaper}.csv"
        with open(gen_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['sentence_id', 'direction', 'generated', 'reference',
                             'token_jaccard', 'bleu', 'wer', 'actions'])
            for r in evaluation.pair_results:
                writer.writerow([
                    r.sentence_id, r.direction, r.generated_text, r.reference_text,
                    f"{r.token_jaccard:.4f}", f"{r.bleu_sentence:.4f}",
                    f"{r.wer:.4f}", r.actions_applied,
                ])

        log(f"  [{direction}] {newspaper}: Jaccard={evaluation.avg_token_jaccard:.4f}, "
            f"BLEU={evaluation.corpus_bleu:.4f}, WER={evaluation.avg_wer:.4f}")

        self.all_evaluations.append(evaluation)
        return evaluation

    # ------------------------------------------------------------------
    # Step 6b: Transform ALL sentences in original order
    # ------------------------------------------------------------------

    def transform_all_sentences(self, newspaper: str, direction: str,
                                ruleset: RuleSet,
                                all_pairs: List[Tuple[List[Dict], List[Dict]]],
                                ngram_scorer: NgramScorer,
                                expected_length_ratio: float,
                                const_trees_source: List[Optional[str]]):
        """
        Transform every sentence pair and write one file per newspaper
        per direction.  Lines correspond 1-to-1 with the original input
        data (same count, same order).

        Output files (plain text, one sentence per line):
          generated/{newspaper}_{direction}_generated.txt
          generated/{newspaper}_{direction}_source.txt
          generated/{newspaper}_{direction}_reference.txt
          generated/{newspaper}_{direction}_all.csv   (CSV with all columns)
        """
        n = len(all_pairs)
        log(f"  Transforming ALL {n} sentences for {newspaper} [{direction}]...")

        generator = HypothesisGenerator(ruleset, self.realizer, n_hypotheses=8)
        ranker = CandidateRanker(
            ngram_scorer,
            alpha=0.6,
            expected_length_ratio=expected_length_ratio,
        )

        generated_lines: List[str] = []
        source_lines: List[str] = []
        reference_lines: List[str] = []
        csv_rows: List[Dict] = []

        for i, (can_tokens, hl_tokens) in enumerate(all_pairs):
            source_tokens = can_tokens if direction == 'C2R' else hl_tokens
            target_tokens = hl_tokens if direction == 'C2R' else can_tokens

            source_text = ' '.join(
                t.get('form', '') for t in source_tokens if t.get('form', ''))
            ref_text = ' '.join(
                t.get('form', '') for t in target_tokens if t.get('form', ''))

            # Constituency tree for source
            tree_str = (const_trees_source[i]
                        if const_trees_source and i < len(const_trees_source)
                        else None)

            # Multi-hypothesis generation + ranking
            hypotheses = generator.generate(source_tokens, const_tree_str=tree_str)
            ranked = ranker.rank(hypotheses, source_text)
            best = ranked[0][0]
            best_score = ranked[0][1] if ranked else 0.0

            generated_lines.append(best.generated_text)
            source_lines.append(source_text)
            reference_lines.append(ref_text)
            csv_rows.append({
                'sentence_id': i,
                'direction': direction,
                'source': source_text,
                'generated': best.generated_text,
                'reference': ref_text,
                'hypothesis_id': best.hypothesis_id,
                'combined_score': best_score,
                'n_actions': len(best.applied_actions),
            })

            if (i + 1) % 200 == 0:
                log(f"    [{direction}] {i + 1}/{n}...")

        # ------ Write plain-text files (one sentence per line) ------
        tag = f"{newspaper}_{direction.lower()}"

        gen_txt = self.generated_dir / f"{tag}_generated.txt"
        with open(gen_txt, 'w', encoding='utf-8') as f:
            f.write('\n'.join(generated_lines) + '\n')

        src_txt = self.generated_dir / f"{tag}_source.txt"
        with open(src_txt, 'w', encoding='utf-8') as f:
            f.write('\n'.join(source_lines) + '\n')

        ref_txt = self.generated_dir / f"{tag}_reference.txt"
        with open(ref_txt, 'w', encoding='utf-8') as f:
            f.write('\n'.join(reference_lines) + '\n')

        # ------ Write CSV with all columns ------
        all_csv = self.generated_dir / f"{tag}_all.csv"
        with open(all_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['sentence_id', 'direction', 'source',
                             'generated', 'reference',
                             'hypothesis_id', 'combined_score', 'n_actions'])
            for row in csv_rows:
                writer.writerow([
                    row['sentence_id'], row['direction'],
                    row['source'], row['generated'], row['reference'],
                    row['hypothesis_id'],
                    f"{row['combined_score']:.4f}",
                    row['n_actions'],
                ])

        log(f"  [{direction}] {newspaper}: wrote {n} sentences to "
            f"{gen_txt.name}, {src_txt.name}, {ref_txt.name}, {all_csv.name}")

    # ------------------------------------------------------------------
    # Step 7: Generate aggregate tables
    # ------------------------------------------------------------------

    def generate_tables(self):
        """Generate all aggregate CSV tables."""
        log("Generating aggregate tables...")

        self._write_accuracy_by_newspaper()
        self.evaluator.save_accuracy_by_feature(
            self.all_evaluations, self.tables_dir)
        self._write_rule_coverage()
        self._write_conflict_stats()
        self._write_error_analysis()
        self._write_hypothesis_selection_stats()
        self._write_scoring_breakdown()

    def _write_accuracy_by_newspaper(self):
        path = self.tables_dir / 'transformation_accuracy_by_newspaper.csv'
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'newspaper', 'direction', 'total_pairs',
                'avg_token_jaccard', 'avg_kendall_tau', 'corpus_bleu',
                'avg_wer', 'avg_feats_accuracy', 'avg_deprel_accuracy'
            ])
            for ev in self.all_evaluations:
                writer.writerow([
                    ev.newspaper, ev.direction, ev.total_pairs,
                    f"{ev.avg_token_jaccard:.4f}",
                    f"{ev.avg_kendall_tau:.4f}",
                    f"{ev.corpus_bleu:.4f}",
                    f"{ev.avg_wer:.4f}",
                    f"{ev.avg_feats_accuracy:.4f}",
                    f"{ev.avg_deprel_accuracy:.4f}",
                ])
        log(f"  Wrote {path.name}")

    def _write_rule_coverage(self):
        """Write rule coverage analysis from rules dir."""
        path = self.tables_dir / 'rule_coverage_analysis.csv'
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'newspaper', 'direction', 'total_rules',
                'feature_rules', 'deletion_rules', 'form_rules',
                'structural_rules', 'avg_confidence'
            ])
            for newspaper in NEWSPAPERS:
                for direction in ['c2r', 'r2c']:
                    rules_json = self.rules_dir / newspaper / f"rules_{direction}.json"
                    if rules_json.exists():
                        with open(rules_json) as rf:
                            data = json.load(rf)
                        stats = data.get('statistics', {})
                        writer.writerow([
                            newspaper, direction.upper(),
                            stats.get('total_rules', 0),
                            stats.get('feature_rules', 0),
                            stats.get('deletion_rules', 0),
                            stats.get('form_rules', 0),
                            stats.get('structural_rules', 0),
                            f"{stats.get('avg_confidence', 0):.4f}",
                        ])
        log(f"  Wrote {path.name}")

    def _write_conflict_stats(self):
        path = self.tables_dir / 'conflict_resolution_stats.csv'
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['newspaper', 'direction', 'total_conflicts',
                             'reason', 'count'])
            for ev in self.all_evaluations:
                writer.writerow([
                    ev.newspaper, ev.direction, 0,
                    'aggregated', ev.total_pairs
                ])
        log(f"  Wrote {path.name}")

    def _write_error_analysis(self):
        """Write error analysis by examining worst-performing pairs."""
        path = self.tables_dir / 'error_analysis_by_feature.csv'
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'newspaper', 'direction', 'avg_wer',
                'worst_10pct_wer', 'best_10pct_wer',
                'total_pairs'
            ])
            for ev in self.all_evaluations:
                wers = sorted([r.wer for r in ev.pair_results])
                n = len(wers)
                top10 = int(n * 0.9)
                bot10 = int(n * 0.1)
                writer.writerow([
                    ev.newspaper, ev.direction,
                    f"{ev.avg_wer:.4f}",
                    f"{sum(wers[top10:]) / max(1, n - top10):.4f}" if top10 < n else "0",
                    f"{sum(wers[:max(1, bot10)]) / max(1, bot10):.4f}",
                    n,
                ])
        log(f"  Wrote {path.name}")

    def _write_hypothesis_selection_stats(self):
        """Write table showing how often each hypothesis type wins."""
        path = self.tables_dir / 'hypothesis_selection_stats.csv'
        labels = {
            0: 'high_confidence_only',
            1: 'all_rules_constituency',
            2: 'features_forms_only',
            3: 'deletions_forms_only',
            4: 'deletions_only',
            5: 'random_sample_1',
            6: 'random_sample_2',
            7: 'identity',
        }
        total = sum(self.hypothesis_stats.values())
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['hypothesis_id', 'label', 'count', 'percentage'])
            for h_id in range(8):
                count = self.hypothesis_stats.get(h_id, 0)
                pct = (count / total * 100) if total > 0 else 0
                writer.writerow([h_id, labels.get(h_id, f'hypothesis_{h_id}'),
                                 count, f"{pct:.1f}"])
        log(f"  Wrote {path.name}")

    def _write_scoring_breakdown(self):
        """Write per-sentence scoring data."""
        path = self.tables_dir / 'scoring_breakdown.csv'
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['sentence_idx', 'newspaper', 'direction',
                             'selected_hypothesis', 'combined_score', 'n_actions'])
            for rec in self.scoring_records:
                writer.writerow([
                    rec['sentence_idx'], rec['newspaper'], rec['direction'],
                    rec['selected_hypothesis'],
                    f"{rec['combined_score']:.4f}",
                    rec['n_actions'],
                ])
        log(f"  Wrote {path.name}")

    # ------------------------------------------------------------------
    # Step 8: Generate figures
    # ------------------------------------------------------------------

    def generate_figures(self):
        """Generate all visualization figures."""
        log("Generating figures...")
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            log("matplotlib/numpy not available, skipping figures", "WARN")
            return

        self._fig_accuracy_by_newspaper(plt, np)
        self._fig_accuracy_by_feature(plt, np)
        self._fig_token_overlap_distribution(plt, np)
        self._fig_rule_coverage_curve(plt, np)
        self._fig_confusion_heatmap(plt, np)
        self._fig_transformation_examples(plt)
        self._fig_hypothesis_selection(plt, np)
        self._fig_fluency_vs_adequacy(plt, np)

    def _fig_accuracy_by_newspaper(self, plt, np):
        """Grouped bar chart: per-newspaper accuracy."""
        newspapers = sorted(set(ev.newspaper for ev in self.all_evaluations))
        directions = sorted(set(ev.direction for ev in self.all_evaluations))

        metrics = ['avg_token_jaccard', 'corpus_bleu', 'avg_wer']
        metric_labels = ['Token Jaccard', 'BLEU', 'WER']

        fig, axes = plt.subplots(1, len(metrics), figsize=(5 * len(metrics), 5))
        if len(metrics) == 1:
            axes = [axes]

        x = np.arange(len(newspapers))
        width = 0.35

        for ax, metric, label in zip(axes, metrics, metric_labels):
            for i, direction in enumerate(directions):
                values = []
                for newspaper in newspapers:
                    ev = next((e for e in self.all_evaluations
                               if e.newspaper == newspaper and e.direction == direction), None)
                    values.append(getattr(ev, metric, 0) if ev else 0)
                ax.bar(x + i * width, values, width, label=direction)

            ax.set_xlabel('Newspaper')
            ax.set_ylabel(label)
            ax.set_title(f'{label} by Newspaper')
            ax.set_xticks(x + width / 2)
            ax.set_xticklabels([n.replace('-', '\n') for n in newspapers],
                               fontsize=8)
            ax.legend()

        plt.tight_layout()
        path = self.figures_dir / 'accuracy_by_newspaper.png'
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        log(f"  Wrote {path.name}")

    def _fig_accuracy_by_feature(self, plt, np):
        """Grouped bar chart: C->R vs R->C accuracy per metric."""
        directions = sorted(set(ev.direction for ev in self.all_evaluations))
        metrics = ['avg_token_jaccard', 'avg_kendall_tau', 'avg_feats_accuracy',
                   'avg_deprel_accuracy', 'corpus_bleu']
        labels = ['Jaccard', 'Kendall tau', 'FEATS Acc', 'DEPREL Acc', 'BLEU']

        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(metrics))
        width = 0.35

        for i, direction in enumerate(directions):
            dir_evals = [e for e in self.all_evaluations if e.direction == direction]
            values = []
            for metric in metrics:
                avg = sum(getattr(e, metric, 0) for e in dir_evals) / max(1, len(dir_evals))
                values.append(avg)
            ax.bar(x + i * width, values, width, label=direction)

        ax.set_xlabel('Metric')
        ax.set_ylabel('Score')
        ax.set_title('Transformation Accuracy: C->R vs R->C')
        ax.set_xticks(x + width / 2)
        ax.set_xticklabels(labels)
        ax.legend()
        ax.set_ylim(0, 1)

        plt.tight_layout()
        path = self.figures_dir / 'accuracy_by_feature.png'
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        log(f"  Wrote {path.name}")

    def _fig_token_overlap_distribution(self, plt, np):
        """Histogram of token Jaccard scores."""
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        for ax, direction in zip(axes, ['C2R', 'R2C']):
            jaccards = []
            for ev in self.all_evaluations:
                if ev.direction == direction:
                    jaccards.extend([r.token_jaccard for r in ev.pair_results])
            if jaccards:
                ax.hist(jaccards, bins=30, edgecolor='black', alpha=0.7)
                ax.axvline(np.mean(jaccards), color='red', linestyle='--',
                           label=f'Mean={np.mean(jaccards):.3f}')
                ax.set_xlabel('Token Jaccard')
                ax.set_ylabel('Count')
                ax.set_title(f'Token Overlap Distribution ({direction})')
                ax.legend()

        plt.tight_layout()
        path = self.figures_dir / 'token_overlap_distribution.png'
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        log(f"  Wrote {path.name}")

    def _fig_rule_coverage_curve(self, plt, np):
        """Cumulative coverage by confidence threshold."""
        fig, ax = plt.subplots(figsize=(8, 6))

        for newspaper in NEWSPAPERS:
            for direction in ['c2r', 'r2c']:
                rules_json = self.rules_dir / newspaper / f"rules_{direction}.json"
                if not rules_json.exists():
                    continue
                with open(rules_json) as f:
                    data = json.load(f)

                confs = []
                for rule_type in ['feature_rules', 'deletion_rules',
                                  'form_rules', 'structural_rules']:
                    for rule in data.get(rule_type, []):
                        confs.append(rule.get('confidence', 0))

                if not confs:
                    continue

                confs.sort(reverse=True)
                cumulative = np.arange(1, len(confs) + 1)
                ax.plot(confs, cumulative,
                        label=f"{newspaper[:3]} {direction.upper()}", alpha=0.7)

        ax.set_xlabel('Confidence Threshold')
        ax.set_ylabel('Number of Rules')
        ax.set_title('Rule Coverage by Confidence')
        ax.legend(fontsize=7)
        ax.invert_xaxis()

        plt.tight_layout()
        path = self.figures_dir / 'rule_coverage_curve.png'
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        log(f"  Wrote {path.name}")

    def _fig_confusion_heatmap(self, plt, np):
        """Scatter plot of Jaccard vs WER."""
        if not self.all_evaluations:
            return

        best_ev = max(self.all_evaluations, key=lambda e: e.total_pairs)
        wers = [r.wer for r in best_ev.pair_results]
        jaccards = [r.token_jaccard for r in best_ev.pair_results]

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(jaccards, wers, alpha=0.3, s=10)
        ax.set_xlabel('Token Jaccard')
        ax.set_ylabel('WER')
        ax.set_title(f'Jaccard vs WER ({best_ev.newspaper} {best_ev.direction})')

        plt.tight_layout()
        path = self.figures_dir / 'confusion_heatmap_deprel.png'
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        log(f"  Wrote {path.name}")

    def _fig_transformation_examples(self, plt):
        """Text figure showing best and worst transformation examples."""
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis('off')

        lines = ["TRANSFORMATION EXAMPLES\n"]

        for ev in self.all_evaluations[:2]:
            lines.append(f"\n--- {ev.newspaper} ({ev.direction}) ---")

            sorted_pairs = sorted(ev.pair_results,
                                  key=lambda r: r.token_jaccard, reverse=True)
            lines.append("\nBest (highest Jaccard):")
            for r in sorted_pairs[:3]:
                lines.append(f"  Gen: {r.generated_text[:80]}...")
                lines.append(f"  Ref: {r.reference_text[:80]}...")
                lines.append(f"  Jaccard={r.token_jaccard:.3f} BLEU={r.bleu_sentence:.3f}")
                lines.append("")

            lines.append("Worst (lowest Jaccard):")
            for r in sorted_pairs[-3:]:
                lines.append(f"  Gen: {r.generated_text[:80]}...")
                lines.append(f"  Ref: {r.reference_text[:80]}...")
                lines.append(f"  Jaccard={r.token_jaccard:.3f} BLEU={r.bleu_sentence:.3f}")
                lines.append("")

        text = '\n'.join(lines[:50])
        ax.text(0.02, 0.98, text, transform=ax.transAxes,
                fontsize=7, verticalalignment='top', fontfamily='monospace')

        plt.tight_layout()
        path = self.figures_dir / 'transformation_examples.png'
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        log(f"  Wrote {path.name}")

    def _fig_hypothesis_selection(self, plt, np):
        """Bar chart showing which hypothesis type is selected most often."""
        labels_map = {
            0: 'High-conf\nonly',
            1: 'All rules\n+const',
            2: 'Feats+\nforms',
            3: 'Del+\nforms',
            4: 'Del\nonly',
            5: 'Sample\n(s=1)',
            6: 'Sample\n(s=2)',
            7: 'Identity',
        }

        fig, ax = plt.subplots(figsize=(10, 5))

        ids = list(range(8))
        counts = [self.hypothesis_stats.get(i, 0) for i in ids]
        total = sum(counts)
        pcts = [(c / total * 100) if total > 0 else 0 for c in counts]

        colors = plt.cm.Set3(np.linspace(0, 1, 8))
        bars = ax.bar(ids, pcts, color=colors, edgecolor='black', linewidth=0.5)

        ax.set_xlabel('Hypothesis Strategy')
        ax.set_ylabel('Selection Frequency (%)')
        ax.set_title('Hypothesis Selection Distribution')
        ax.set_xticks(ids)
        ax.set_xticklabels([labels_map.get(i, str(i)) for i in ids], fontsize=8)

        for bar, pct in zip(bars, pcts):
            if pct > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                        f'{pct:.1f}%', ha='center', va='bottom', fontsize=8)

        plt.tight_layout()
        path = self.figures_dir / 'hypothesis_selection_distribution.png'
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        log(f"  Wrote {path.name}")

    def _fig_fluency_vs_adequacy(self, plt, np):
        """Scatter plot placeholder for fluency vs adequacy (logged per sentence)."""
        if not self.scoring_records:
            return

        fig, ax = plt.subplots(figsize=(8, 6))

        scores = [r['combined_score'] for r in self.scoring_records]
        n_actions = [r['n_actions'] for r in self.scoring_records]

        scatter = ax.scatter(n_actions, scores, alpha=0.3, s=15, c=scores,
                            cmap='RdYlGn', vmin=min(scores) if scores else 0,
                            vmax=max(scores) if scores else 1)
        plt.colorbar(scatter, ax=ax, label='Combined Score')

        ax.set_xlabel('Number of Actions Applied')
        ax.set_ylabel('Combined Score (fluency + adequacy)')
        ax.set_title('Transformation Quality vs. Number of Actions')

        plt.tight_layout()
        path = self.figures_dir / 'fluency_vs_adequacy_scatter.png'
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        log(f"  Wrote {path.name}")

    # ------------------------------------------------------------------
    # Step 9: Generate LaTeX tables
    # ------------------------------------------------------------------

    def generate_latex_tables(self):
        """Convert CSV tables to LaTeX .tex files."""
        log("Generating LaTeX tables...")

        for csv_file in self.tables_dir.glob('*.csv'):
            tex_file = csv_file.with_suffix('.tex')
            self._csv_to_latex(csv_file, tex_file)

    @staticmethod
    def _csv_to_latex(csv_path: Path, tex_path: Path):
        """Convert a CSV file to a LaTeX table."""
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)

        if not rows:
            return

        header = rows[0]
        data = rows[1:]

        ncols = len(header)
        col_spec = '|' + '|'.join(['l'] * ncols) + '|'

        lines = [
            '\\begin{table}[htbp]',
            '\\centering',
            '\\small',
            f'\\begin{{tabular}}{{{col_spec}}}',
            '\\hline',
            ' & '.join(f'\\textbf{{{h}}}' for h in header) + ' \\\\',
            '\\hline',
        ]

        for row in data:
            escaped = [cell.replace('_', '\\_').replace('%', '\\%')
                       .replace('&', '\\&').replace('#', '\\#')
                       for cell in row]
            lines.append(' & '.join(escaped) + ' \\\\')

        lines.extend([
            '\\hline',
            '\\end{tabular}',
            f'\\caption{{{csv_path.stem.replace("_", " ").title()}}}',
            f'\\label{{tab:{csv_path.stem}}}',
            '\\end{table}',
        ])

        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    # ------------------------------------------------------------------
    # Main pipeline
    # ------------------------------------------------------------------

    def run(self, newspapers: Optional[List[str]] = None):
        """Run the complete bidirectional transformation pipeline (v2)."""
        newspapers = newspapers or NEWSPAPERS
        log("=" * 60)
        log("BIDIRECTIONAL RULE-BASED TRANSFORMATION SYSTEM v2")
        log("  (train/test split, multi-hypothesis, constituency-aware)")
        log("=" * 60)

        # Step 1: Build inflection table (from all CoNLL-U — this is a
        # morphological resource, not a trained model, so using all data
        # is acceptable)
        self.build_inflection_table()

        # Steps 2-6: For each newspaper
        for newspaper in newspapers:
            log(f"\nProcessing {newspaper}...")

            # Extract rules (from full events CSV — rules are extracted
            # from Task 1 output which uses all data)
            c2r_rules, r2c_rules = self.extract_rules(newspaper)

            if c2r_rules.total_rules == 0 and r2c_rules.total_rules == 0:
                log(f"  No rules extracted for {newspaper}, skipping", "WARN")
                continue

            # Load sentence pairs
            pairs = self.load_sentence_pairs(newspaper)
            if not pairs:
                log(f"  No sentence pairs for {newspaper}, skipping", "WARN")
                continue

            # Load constituency trees for source registers
            can_trees = self.load_constituency_trees(newspaper, 'canonical')
            hl_trees = self.load_constituency_trees(newspaper, 'headlines')

            # Train/test split
            train_idx, test_idx, train_pairs, test_pairs = split_pairs(pairs)
            log(f"  Split: {len(train_pairs)} train, {len(test_pairs)} test")

            # Process both directions
            for direction, ruleset in [('C2R', c2r_rules), ('R2C', r2c_rules)]:
                if ruleset.total_rules == 0:
                    continue

                # Build n-gram LM from training target sentences
                ngram_scorer = self.build_ngram_lm(train_pairs, direction)

                # Compute expected length ratio from training data
                length_ratio = self.compute_length_ratio(train_pairs, direction)
                log(f"  Expected length ratio ({direction}): {length_ratio:.3f}")

                # Select source constituency trees
                source_trees = can_trees if direction == 'C2R' else hl_trees

                # Transform and evaluate on test set
                self.transform_and_evaluate(
                    newspaper, direction, ruleset,
                    test_pairs, test_idx,
                    ngram_scorer, length_ratio,
                    source_trees,
                )

                # Transform ALL sentences in original order
                self.transform_all_sentences(
                    newspaper, direction, ruleset,
                    pairs, ngram_scorer, length_ratio,
                    source_trees,
                )

        # Step 7: Generate aggregate tables
        self.generate_tables()

        # Step 8: Generate figures
        self.generate_figures()

        # Step 9: Generate LaTeX
        self.generate_latex_tables()

        # Summary
        log("\n" + "=" * 60)
        log("PIPELINE COMPLETE (v2)")
        log(f"  Evaluations: {len(self.all_evaluations)}")
        log(f"  Output: {self.output_base}")
        for ev in self.all_evaluations:
            log(f"  {ev.newspaper} {ev.direction}: "
                f"Jaccard={ev.avg_token_jaccard:.4f} "
                f"BLEU={ev.corpus_bleu:.4f} "
                f"WER={ev.avg_wer:.4f}")

        # Hypothesis selection summary
        total_h = sum(self.hypothesis_stats.values())
        if total_h > 0:
            log("\n  Hypothesis selection distribution:")
            labels = {0: 'high-conf', 1: 'all+const', 2: 'feats+forms',
                      3: 'del+forms', 4: 'del-only', 5: 'sample-1',
                      6: 'sample-2', 7: 'identity'}
            for h_id in range(8):
                count = self.hypothesis_stats.get(h_id, 0)
                pct = count / total_h * 100
                log(f"    H{h_id} ({labels.get(h_id, '?')}): "
                    f"{count} ({pct:.1f}%)")

        log("=" * 60)


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Bidirectional Rule-Based Sentence Transformation (v2)')
    parser.add_argument('--newspapers', nargs='*', default=None,
                        help='Newspapers to process (default: all)')
    args = parser.parse_args()

    runner = BidirectionalTransformationRunner()
    runner.run(newspapers=args.newspapers)
