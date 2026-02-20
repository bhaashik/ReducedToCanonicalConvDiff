"""
Transformation Evaluator: Evaluates generated sentences against gold-standard
reference sentences using multiple metrics.

Metrics:
  - Token Jaccard: |intersection| / |union| of token sets
  - Kendall's tau: order correlation between shared tokens
  - FEATS accuracy: morphological feature match rate
  - DEPREL accuracy: dependency relation match rate
  - BLEU: corpus-level BLEU score (1-4 grams)
  - WER: word error rate
"""

import csv
import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from collections import Counter
from dataclasses import dataclass, field

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


@dataclass
class PairEvaluation:
    """Evaluation result for a single generated-vs-reference sentence pair."""
    sentence_id: int
    direction: str
    generated_text: str
    reference_text: str
    token_jaccard: float
    kendall_tau: float
    feats_accuracy: float
    deprel_accuracy: float
    bleu_sentence: float
    wer: float
    gen_length: int
    ref_length: int
    actions_applied: int


@dataclass
class CorpusEvaluation:
    """Aggregate evaluation over an entire corpus."""
    direction: str
    newspaper: str
    total_pairs: int
    avg_token_jaccard: float
    avg_kendall_tau: float
    avg_feats_accuracy: float
    avg_deprel_accuracy: float
    corpus_bleu: float
    avg_wer: float
    avg_gen_length: float
    avg_ref_length: float
    avg_actions: float
    pair_results: List[PairEvaluation] = field(default_factory=list)


class TransformationEvaluator:
    """Evaluates quality of generated sentences against reference."""

    # ------------------------------------------------------------------
    # Pair-level evaluation
    # ------------------------------------------------------------------

    def evaluate_pair(self, generated: str, reference: str,
                      gen_tokens: Optional[List[Dict]] = None,
                      ref_tokens: Optional[List[Dict]] = None,
                      sentence_id: int = 0,
                      direction: str = '',
                      actions_applied: int = 0) -> PairEvaluation:
        """Evaluate a single generated-vs-reference pair."""
        gen_words = generated.lower().split()
        ref_words = reference.lower().split()

        return PairEvaluation(
            sentence_id=sentence_id,
            direction=direction,
            generated_text=generated,
            reference_text=reference,
            token_jaccard=self._token_jaccard(gen_words, ref_words),
            kendall_tau=self._kendall_tau(gen_words, ref_words),
            feats_accuracy=self._feats_accuracy(gen_tokens, ref_tokens),
            deprel_accuracy=self._deprel_accuracy(gen_tokens, ref_tokens),
            bleu_sentence=self._sentence_bleu(gen_words, ref_words),
            wer=self._wer(gen_words, ref_words),
            gen_length=len(gen_words),
            ref_length=len(ref_words),
            actions_applied=actions_applied,
        )

    # ------------------------------------------------------------------
    # Corpus-level evaluation
    # ------------------------------------------------------------------

    def evaluate_corpus(self, pairs: List[Tuple[str, str]],
                        token_pairs: Optional[List[Tuple[List[Dict], List[Dict]]]] = None,
                        direction: str = '',
                        newspaper: str = '',
                        actions_list: Optional[List[int]] = None) -> CorpusEvaluation:
        """
        Evaluate a list of (generated, reference) text pairs.

        Optionally accepts parallel lists of token dicts for structural metrics.
        """
        results = []
        for i, (gen_text, ref_text) in enumerate(pairs):
            gen_tokens = token_pairs[i][0] if token_pairs and i < len(token_pairs) else None
            ref_tokens = token_pairs[i][1] if token_pairs and i < len(token_pairs) else None
            actions = actions_list[i] if actions_list and i < len(actions_list) else 0

            result = self.evaluate_pair(
                gen_text, ref_text,
                gen_tokens, ref_tokens,
                sentence_id=i,
                direction=direction,
                actions_applied=actions,
            )
            results.append(result)

        # Aggregate
        n = len(results)
        if n == 0:
            return CorpusEvaluation(
                direction=direction, newspaper=newspaper, total_pairs=0,
                avg_token_jaccard=0, avg_kendall_tau=0, avg_feats_accuracy=0,
                avg_deprel_accuracy=0, corpus_bleu=0, avg_wer=0,
                avg_gen_length=0, avg_ref_length=0, avg_actions=0,
            )

        # Corpus BLEU (computed across all pairs)
        all_gen = [r.generated_text.lower().split() for r in results]
        all_ref = [r.reference_text.lower().split() for r in results]
        corpus_bleu = self._corpus_bleu(all_gen, all_ref)

        return CorpusEvaluation(
            direction=direction,
            newspaper=newspaper,
            total_pairs=n,
            avg_token_jaccard=sum(r.token_jaccard for r in results) / n,
            avg_kendall_tau=sum(r.kendall_tau for r in results) / n,
            avg_feats_accuracy=sum(r.feats_accuracy for r in results) / n,
            avg_deprel_accuracy=sum(r.deprel_accuracy for r in results) / n,
            corpus_bleu=corpus_bleu,
            avg_wer=sum(r.wer for r in results) / n,
            avg_gen_length=sum(r.gen_length for r in results) / n,
            avg_ref_length=sum(r.ref_length for r in results) / n,
            avg_actions=sum(r.actions_applied for r in results) / n,
            pair_results=results,
        )

    # ------------------------------------------------------------------
    # Individual metrics
    # ------------------------------------------------------------------

    @staticmethod
    def _token_jaccard(gen_words: List[str], ref_words: List[str]) -> float:
        """Token-level Jaccard similarity: |intersection| / |union|."""
        gen_set = set(gen_words)
        ref_set = set(ref_words)
        if not gen_set and not ref_set:
            return 1.0
        intersection = gen_set & ref_set
        union = gen_set | ref_set
        return len(intersection) / len(union) if union else 0.0

    @staticmethod
    def _kendall_tau(gen_words: List[str], ref_words: List[str]) -> float:
        """
        Kendall's tau for shared tokens: measures order preservation.

        Only considers tokens that appear in both sequences.
        Returns a value in [-1, 1] where 1 = perfect order agreement.
        """
        # Find shared tokens and their positions in each sequence
        shared = set(gen_words) & set(ref_words)
        if len(shared) < 2:
            return 1.0  # Not enough shared tokens to measure order

        # Position maps (first occurrence)
        gen_pos = {}
        for i, w in enumerate(gen_words):
            if w in shared and w not in gen_pos:
                gen_pos[w] = i
        ref_pos = {}
        for i, w in enumerate(ref_words):
            if w in shared and w not in ref_pos:
                ref_pos[w] = i

        common = sorted(shared)
        if len(common) < 2:
            return 1.0

        # Count concordant and discordant pairs
        concordant = 0
        discordant = 0
        for i in range(len(common)):
            for j in range(i + 1, len(common)):
                a, b = common[i], common[j]
                gen_order = gen_pos[a] < gen_pos[b]
                ref_order = ref_pos[a] < ref_pos[b]
                if gen_order == ref_order:
                    concordant += 1
                else:
                    discordant += 1

        total = concordant + discordant
        if total == 0:
            return 1.0
        return (concordant - discordant) / total

    @staticmethod
    def _feats_accuracy(gen_tokens: Optional[List[Dict]],
                        ref_tokens: Optional[List[Dict]]) -> float:
        """
        Compare morphological features between generated and reference tokens.

        Aligns by lemma, then compares feats dicts.
        """
        if not gen_tokens or not ref_tokens:
            return 0.0

        # Build lemma → feats maps
        gen_feats = {}
        for t in gen_tokens:
            lemma = (t.get('lemma', '') or '').lower()
            if lemma:
                gen_feats[lemma] = t.get('feats') or {}

        ref_feats = {}
        for t in ref_tokens:
            lemma = (t.get('lemma', '') or '').lower()
            if lemma:
                ref_feats[lemma] = t.get('feats') or {}

        shared_lemmas = set(gen_feats) & set(ref_feats)
        if not shared_lemmas:
            return 0.0

        correct = 0
        total = 0
        for lemma in shared_lemmas:
            gf = gen_feats[lemma]
            rf = ref_feats[lemma]
            all_keys = set(gf) | set(rf)
            for key in all_keys:
                total += 1
                if gf.get(key) == rf.get(key):
                    correct += 1

        return correct / total if total > 0 else 1.0

    @staticmethod
    def _deprel_accuracy(gen_tokens: Optional[List[Dict]],
                         ref_tokens: Optional[List[Dict]]) -> float:
        """Compare dependency relations by aligning on lemma."""
        if not gen_tokens or not ref_tokens:
            return 0.0

        gen_deprel = {}
        for t in gen_tokens:
            lemma = (t.get('lemma', '') or '').lower()
            if lemma:
                gen_deprel[lemma] = t.get('deprel', '')

        ref_deprel = {}
        for t in ref_tokens:
            lemma = (t.get('lemma', '') or '').lower()
            if lemma:
                ref_deprel[lemma] = t.get('deprel', '')

        shared = set(gen_deprel) & set(ref_deprel)
        if not shared:
            return 0.0

        correct = sum(1 for l in shared if gen_deprel[l] == ref_deprel[l])
        return correct / len(shared)

    @staticmethod
    def _sentence_bleu(gen_words: List[str], ref_words: List[str],
                       max_n: int = 4) -> float:
        """Sentence-level BLEU (smoothed) for a single pair."""
        if not gen_words or not ref_words:
            return 0.0

        # Brevity penalty
        bp = min(1.0, math.exp(1 - len(ref_words) / len(gen_words))) if gen_words else 0.0

        log_avg = 0.0
        for n in range(1, max_n + 1):
            gen_ngrams = Counter()
            for i in range(len(gen_words) - n + 1):
                gen_ngrams[tuple(gen_words[i:i + n])] += 1

            ref_ngrams = Counter()
            for i in range(len(ref_words) - n + 1):
                ref_ngrams[tuple(ref_words[i:i + n])] += 1

            clipped = sum(min(gen_ngrams[ng], ref_ngrams[ng])
                          for ng in gen_ngrams)
            total = sum(gen_ngrams.values())

            # Add-1 smoothing for sentence-level
            precision = (clipped + 1) / (total + 1) if total > 0 else 0.0
            if precision <= 0:
                return 0.0
            log_avg += math.log(precision) / max_n

        return bp * math.exp(log_avg)

    @staticmethod
    def _corpus_bleu(all_gen: List[List[str]], all_ref: List[List[str]],
                     max_n: int = 4) -> float:
        """Corpus-level BLEU (no smoothing)."""
        if not all_gen or not all_ref:
            return 0.0

        total_gen_len = sum(len(g) for g in all_gen)
        total_ref_len = sum(len(r) for r in all_ref)

        if total_gen_len == 0:
            return 0.0

        bp = min(1.0, math.exp(1 - total_ref_len / total_gen_len))

        log_avg = 0.0
        for n in range(1, max_n + 1):
            clipped_total = 0
            gen_total = 0

            for gen_words, ref_words in zip(all_gen, all_ref):
                gen_ngrams = Counter()
                for i in range(len(gen_words) - n + 1):
                    gen_ngrams[tuple(gen_words[i:i + n])] += 1

                ref_ngrams = Counter()
                for i in range(len(ref_words) - n + 1):
                    ref_ngrams[tuple(ref_words[i:i + n])] += 1

                clipped_total += sum(min(gen_ngrams[ng], ref_ngrams[ng])
                                     for ng in gen_ngrams)
                gen_total += sum(gen_ngrams.values())

            precision = clipped_total / gen_total if gen_total > 0 else 0.0
            if precision <= 0:
                return 0.0
            log_avg += math.log(precision) / max_n

        return bp * math.exp(log_avg)

    @staticmethod
    def _wer(gen_words: List[str], ref_words: List[str]) -> float:
        """Word Error Rate via edit distance."""
        if not ref_words:
            return 0.0 if not gen_words else 1.0

        m, n = len(ref_words), len(gen_words)
        # Use 1D DP for memory efficiency
        prev = list(range(n + 1))
        for i in range(1, m + 1):
            curr = [i] + [0] * n
            for j in range(1, n + 1):
                cost = 0 if ref_words[i - 1] == gen_words[j - 1] else 1
                curr[j] = min(curr[j - 1] + 1,        # insertion
                              prev[j] + 1,             # deletion
                              prev[j - 1] + cost)      # substitution
            prev = curr

        return prev[n] / m

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------

    def save_corpus_evaluation(self, evaluation: CorpusEvaluation,
                               output_dir: Path):
        """Save evaluation results to CSV and JSON."""
        output_dir.mkdir(parents=True, exist_ok=True)

        prefix = f"{evaluation.newspaper}_{evaluation.direction}".lower()

        # Summary JSON
        summary = {
            'direction': evaluation.direction,
            'newspaper': evaluation.newspaper,
            'total_pairs': evaluation.total_pairs,
            'avg_token_jaccard': round(evaluation.avg_token_jaccard, 4),
            'avg_kendall_tau': round(evaluation.avg_kendall_tau, 4),
            'avg_feats_accuracy': round(evaluation.avg_feats_accuracy, 4),
            'avg_deprel_accuracy': round(evaluation.avg_deprel_accuracy, 4),
            'corpus_bleu': round(evaluation.corpus_bleu, 4),
            'avg_wer': round(evaluation.avg_wer, 4),
            'avg_gen_length': round(evaluation.avg_gen_length, 2),
            'avg_ref_length': round(evaluation.avg_ref_length, 2),
            'avg_actions': round(evaluation.avg_actions, 2),
        }
        with open(output_dir / f"{prefix}_summary.json", 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        # Per-pair CSV
        csv_path = output_dir / f"{prefix}_pairs.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'sentence_id', 'direction', 'token_jaccard', 'kendall_tau',
                'feats_accuracy', 'deprel_accuracy', 'bleu_sentence', 'wer',
                'gen_length', 'ref_length', 'actions_applied',
                'generated_text', 'reference_text'
            ])
            for r in evaluation.pair_results:
                writer.writerow([
                    r.sentence_id, r.direction,
                    f"{r.token_jaccard:.4f}", f"{r.kendall_tau:.4f}",
                    f"{r.feats_accuracy:.4f}", f"{r.deprel_accuracy:.4f}",
                    f"{r.bleu_sentence:.4f}", f"{r.wer:.4f}",
                    r.gen_length, r.ref_length, r.actions_applied,
                    r.generated_text, r.reference_text,
                ])

        print(f"  Saved evaluation: {csv_path}")

    def save_accuracy_by_feature(self, all_evaluations: List[CorpusEvaluation],
                                 output_dir: Path):
        """Save transformation accuracy by feature type CSV."""
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / 'transformation_accuracy_by_direction.csv'

        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'direction', 'newspaper', 'total_pairs',
                'avg_token_jaccard', 'avg_kendall_tau',
                'avg_feats_accuracy', 'avg_deprel_accuracy',
                'corpus_bleu', 'avg_wer'
            ])
            for ev in all_evaluations:
                writer.writerow([
                    ev.direction, ev.newspaper, ev.total_pairs,
                    f"{ev.avg_token_jaccard:.4f}",
                    f"{ev.avg_kendall_tau:.4f}",
                    f"{ev.avg_feats_accuracy:.4f}",
                    f"{ev.avg_deprel_accuracy:.4f}",
                    f"{ev.corpus_bleu:.4f}",
                    f"{ev.avg_wer:.4f}",
                ])
        print(f"  Saved accuracy by direction: {path}")
