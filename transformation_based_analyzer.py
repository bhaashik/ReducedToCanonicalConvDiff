#!/usr/bin/env python3
"""
Transformation-Based Analyzer

Computes complexity and similarity metrics through the lens of morphosyntactic
transformation rules extracted by Task 1 (events_global.csv) and applied in
Task 2 (bidirectional transformation results).

Complexity metrics (per register / direction):
  - Transformation density: avg events per sentence pair
  - Rule entropy: H(distribution of event feature_ids)
  - Transformation type distribution: lexical / morphological / syntactic / structural
  - Transformation difficulty: avg rule actions, avg rule confidence
  - Hypothesis diversity: Shannon entropy of hypothesis selection distribution

Similarity metrics (cross-register via transformations):
  - Transformation-based similarity: 1 - normalized transformation density
  - Transformation coverage: fraction of token differences explained by rules
  - Directional asymmetry: C2R vs R2C comparison

Data sources:
  - output/{newspaper}/events_global.csv             (Task 1)
  - output/transformation-study/bidirectional-transformation/generated/c2r_results_{newspaper}.csv
  - output/transformation-study/bidirectional-transformation/generated/r2c_results_{newspaper}.csv
  - output/transformation-study/bidirectional-transformation/tables/rule_coverage_analysis.csv
  - output/transformation-study/bidirectional-transformation/tables/hypothesis_selection_stats.csv
"""

import math
import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter
from typing import Dict, List, Optional
from scipy.stats import entropy


# ---------------------------------------------------------------------------
# Feature-ID to category mapping
# ---------------------------------------------------------------------------
LEXICAL_FEATURES      = {'FW-DEL', 'ART-DEL', 'PREP-DEL', 'AUX-DEL', 'SCONJ-DEL',
                          'PRON-DEL', 'DET-DEL', 'PART-DEL', 'C-DEL', 'PUNCT-DEL'}
MORPHOLOGICAL_FEATURES = {'FEAT-CHG', 'FORM-CHG', 'LEMMA-CHG', 'TENSE-CHG', 'NUM-CHG'}
SYNTACTIC_FEATURES    = {'DEP-REL-CHG', 'CONST-MOV', 'ARG-SWAP'}
STRUCTURAL_FEATURES   = {'TED-SIMPLE', 'TED-ZS', 'TED-KLEIN', 'TED-RTED',
                          'LENGTH-CHG', 'STRUCT-CHG', 'REORDER'}


def _categorize(feature_id: str) -> str:
    fi = str(feature_id).upper()
    if fi in MORPHOLOGICAL_FEATURES:
        return 'morphological'
    if fi in SYNTACTIC_FEATURES:
        return 'syntactic'
    if fi in STRUCTURAL_FEATURES:
        return 'structural'
    # Default: any DEL-type falls to lexical
    return 'lexical'


class TransformationBasedAnalyzer:
    """Complexity and similarity metrics through transformation rules."""

    def __init__(self, newspaper: str):
        self.newspaper = newspaper
        self.project_root = Path(__file__).parent
        self.bidir_dir = (self.project_root / 'output' / 'transformation-study' /
                          'bidirectional-transformation')

    # =========================================================================
    # DATA LOADERS
    # =========================================================================

    def _load_events(self) -> pd.DataFrame:
        path = self.project_root / 'output' / self.newspaper / 'events_global.csv'
        if not path.exists():
            return pd.DataFrame()
        try:
            return pd.read_csv(path)
        except Exception:
            return pd.DataFrame()

    def _load_results(self, direction: str) -> pd.DataFrame:
        """direction: 'C2R' or 'R2C'"""
        fname = f'{direction.lower()}_results_{self.newspaper}.csv'
        path = self.bidir_dir / 'generated' / fname
        if not path.exists():
            return pd.DataFrame()
        try:
            return pd.read_csv(path)
        except Exception:
            return pd.DataFrame()

    def _load_coverage(self) -> pd.DataFrame:
        path = self.bidir_dir / 'tables' / 'rule_coverage_analysis.csv'
        if not path.exists():
            return pd.DataFrame()
        try:
            return pd.read_csv(path)
        except Exception:
            return pd.DataFrame()

    def _load_hypothesis_stats(self) -> pd.DataFrame:
        path = self.bidir_dir / 'tables' / 'hypothesis_selection_stats.csv'
        if not path.exists():
            return pd.DataFrame()
        try:
            return pd.read_csv(path)
        except Exception:
            return pd.DataFrame()

    # =========================================================================
    # MAIN ANALYSIS
    # =========================================================================

    def analyze(self) -> Dict:
        """Run all transformation-based analyses."""
        print(f"\n{'='*80}")
        print(f"TRANSFORMATION-BASED ANALYSIS: {self.newspaper}")
        print(f"{'='*80}\n")

        events   = self._load_events()
        c2r      = self._load_results('C2R')
        r2c      = self._load_results('R2C')
        coverage = self._load_coverage()
        hyp_stats = self._load_hypothesis_stats()

        results = {
            'newspaper': self.newspaper,
            'complexity': {
                'transformation_density':     self._transformation_density(events),
                'rule_entropy':               self._rule_entropy(events),
                'type_distribution':          self._transformation_type_distribution(events),
                'transformation_difficulty':  self._transformation_difficulty(c2r, r2c),
                'hypothesis_diversity':       self._hypothesis_diversity(hyp_stats),
            },
            'similarity': {
                'transformation_based_similarity': self._transformation_based_similarity(events),
                'transformation_coverage':         self._transformation_coverage(coverage),
                'directional_asymmetry':           self._directional_asymmetry(c2r, r2c, events),
            }
        }

        print(f"✓ Transformation-based analysis complete for {self.newspaper}")
        return results

    # =========================================================================
    # COMPLEXITY METRICS
    # =========================================================================

    def _transformation_density(self, events: pd.DataFrame) -> Dict:
        """Average number of transformation events per sentence pair."""
        if events.empty or 'sentence_id' not in events.columns:
            return {}

        events_per_sent = events.groupby('sentence_id').size()
        density = float(events_per_sent.mean())
        density_std = float(events_per_sent.std())
        total_events = int(events_per_sent.sum())
        n_sentences  = int(len(events_per_sent))

        print(f"  Transformation density:  {density:.3f} events/sentence  "
              f"(total={total_events}, sents={n_sentences})")

        return {
            'avg_events_per_sentence': density,
            'std_events_per_sentence': density_std,
            'total_events':            total_events,
            'n_sentences':             n_sentences,
        }

    def _rule_entropy(self, events: pd.DataFrame) -> Dict:
        """Entropy of the distribution of rule types applied (feature_id)."""
        if events.empty or 'feature_id' not in events.columns:
            return {}

        counts = Counter(events['feature_id'].dropna().tolist())
        if not counts:
            return {}

        probs = np.array(list(counts.values()), dtype=float)
        probs /= probs.sum()
        h = float(entropy(probs, base=2))
        max_h = math.log2(len(counts)) if len(counts) > 1 else 1.0
        norm_h = h / max_h if max_h > 0 else 0.0

        print(f"  Rule entropy: {h:.3f} bits  (normalized={norm_h:.3f}, "
              f"n_rule_types={len(counts)})")

        return {
            'rule_entropy':            h,
            'rule_entropy_normalized': norm_h,
            'n_distinct_rule_types':   len(counts),
            'top_rules':               dict(counts.most_common(5)),
        }

    def _transformation_type_distribution(self, events: pd.DataFrame) -> Dict:
        """Proportion breakdown by transformation category."""
        if events.empty or 'feature_id' not in events.columns:
            return {}

        category_counts = Counter()
        for fid in events['feature_id'].dropna():
            category_counts[_categorize(str(fid))] += 1

        total = sum(category_counts.values())
        proportions = {cat: cnt / total for cat, cnt in category_counts.items()} if total > 0 else {}

        # Type distribution entropy
        if proportions:
            probs = np.array(list(proportions.values()))
            type_entropy = float(entropy(probs, base=2))
        else:
            type_entropy = 0.0

        print(f"  Type distribution: "
              + ', '.join(f"{k}={v:.2%}" for k, v in sorted(proportions.items())))

        return {
            'counts':          dict(category_counts),
            'proportions':     proportions,
            'type_entropy':    type_entropy,
            'total_events':    total,
        }

    def _transformation_difficulty(self, c2r: pd.DataFrame, r2c: pd.DataFrame) -> Dict:
        """Difficulty indicators from Task 2 per-sentence results."""
        out: Dict[str, Dict] = {}

        for label, df in [('C2R', c2r), ('R2C', r2c)]:
            if df.empty:
                out[label] = {}
                continue

            entry: Dict = {}
            if 'actions' in df.columns:
                acts = df['actions'].dropna()
                entry['avg_actions'] = float(acts.mean())
                entry['std_actions'] = float(acts.std())

            if 'token_jaccard' in df.columns:
                jac = df['token_jaccard'].dropna()
                entry['avg_jaccard']  = float(jac.mean())
                entry['avg_wer']      = float(df['wer'].mean())   if 'wer'  in df.columns else 0.0
                entry['avg_bleu']     = float(df['bleu'].mean())  if 'bleu' in df.columns else 0.0

            out[label] = entry
            if entry:
                print(f"  Difficulty {label}: avg_actions={entry.get('avg_actions', 0):.2f}, "
                      f"avg_jaccard={entry.get('avg_jaccard', 0):.3f}, "
                      f"avg_bleu={entry.get('avg_bleu', 0):.3f}")

        return out

    def _hypothesis_diversity(self, hyp_stats: pd.DataFrame) -> Dict:
        """Shannon entropy of hypothesis selection distribution."""
        if hyp_stats.empty or 'percentage' not in hyp_stats.columns:
            return {}

        percentages = hyp_stats['percentage'].dropna().values
        if percentages.sum() == 0:
            return {}

        probs = percentages / percentages.sum()
        h = float(entropy(probs, base=2))
        max_h = math.log2(len(probs)) if len(probs) > 1 else 1.0

        labels = hyp_stats.get('label', hyp_stats.get('hypothesis_id', pd.Series())).tolist()
        dominant = labels[int(np.argmax(percentages))] if labels else 'unknown'

        print(f"  Hypothesis diversity: {h:.3f} bits  (max={max_h:.3f}), "
              f"dominant='{dominant}'")

        return {
            'hypothesis_entropy':            h,
            'hypothesis_entropy_normalized': h / max_h if max_h > 0 else 0.0,
            'n_hypotheses':                  int(len(probs)),
            'dominant_hypothesis':           dominant,
            'selection_distribution':        dict(zip(
                [str(l) for l in labels],
                [float(p) for p in percentages]
            )),
        }

    # =========================================================================
    # SIMILARITY METRICS
    # =========================================================================

    def _transformation_based_similarity(self, events: pd.DataFrame) -> Dict:
        """1 - normalized transformation density as a proxy for similarity.
        More transformations needed ↔ less similar registers."""
        if events.empty or 'sentence_id' not in events.columns:
            return {}

        # We need sentence lengths to normalize — try loading canonical parse
        conllu_path = (self.project_root / 'data' / 'input' / 'dependecy-parsed' /
                       f'{self.newspaper}-canonical-stanza-parsed-deps.conllu')

        sent_lengths: Dict[int, int] = {}
        if conllu_path.exists():
            try:
                from conllu import parse_incr
                with open(conllu_path, 'r', encoding='utf-8') as f:
                    for idx, sentence in enumerate(parse_incr(f), start=1):
                        sent_lengths[idx] = len(sentence)
            except Exception:
                pass

        events_per_sent = events.groupby('sentence_id').size().to_dict()

        if sent_lengths:
            # Normalized density per sentence
            norm_densities = []
            for sid, cnt in events_per_sent.items():
                n = sent_lengths.get(sid, 0)
                if n > 0:
                    norm_densities.append(cnt / n)
            avg_norm_density = float(np.mean(norm_densities)) if norm_densities else 0.0
        else:
            avg_norm_density = 0.0

        avg_density = float(np.mean(list(events_per_sent.values()))) if events_per_sent else 0.0

        # Simple similarity proxy
        # Clip to [0,1]: if density is 0, registers are identical
        trans_similarity = max(0.0, 1.0 - min(avg_norm_density, 1.0))

        print(f"  Transform-based similarity: {trans_similarity:.4f}  "
              f"(avg_density={avg_density:.3f})")

        return {
            'transformation_based_similarity': trans_similarity,
            'avg_events_per_sentence':          avg_density,
            'avg_normalized_density':           avg_norm_density,
        }

    def _transformation_coverage(self, coverage: pd.DataFrame) -> Dict:
        """Rule coverage from rule_coverage_analysis.csv."""
        if coverage.empty:
            return {}

        news_cov = coverage[coverage['newspaper'] == self.newspaper] \
            if 'newspaper' in coverage.columns else coverage

        if news_cov.empty:
            return {}

        out: Dict[str, Dict] = {}
        for _, row in news_cov.iterrows():
            direction = str(row.get('direction', 'UNKNOWN'))
            entry: Dict = {}
            for col in ['total_rules', 'feature_rules', 'deletion_rules',
                        'form_rules', 'structural_rules', 'avg_confidence']:
                if col in row.index:
                    entry[col] = float(row[col]) if col == 'avg_confidence' else int(row[col])
            out[direction] = entry
            print(f"  Coverage {direction}: total_rules={entry.get('total_rules', 0)}, "
                  f"avg_conf={entry.get('avg_confidence', 0):.3f}")

        return out

    def _directional_asymmetry(
        self,
        c2r: pd.DataFrame,
        r2c: pd.DataFrame,
        events: pd.DataFrame
    ) -> Dict:
        """Compare C2R vs R2C transformation characteristics."""

        def _metric_dict(df: pd.DataFrame) -> Dict:
            out: Dict = {}
            for col in ['token_jaccard', 'bleu', 'wer', 'actions']:
                if col in df.columns:
                    vals = df[col].dropna()
                    out[f'avg_{col}'] = float(vals.mean())
            return out

        c2r_metrics = _metric_dict(c2r) if not c2r.empty else {}
        r2c_metrics = _metric_dict(r2c) if not r2c.empty else {}

        # Asymmetry indices
        asym = {}
        for key in set(c2r_metrics) & set(r2c_metrics):
            asym[f'{key}_asymmetry'] = abs(c2r_metrics[key] - r2c_metrics[key])

        print(f"  Directional asymmetry:  "
              + ', '.join(f"{k}={v:.3f}" for k, v in list(asym.items())[:3]))

        return {
            'C2R': c2r_metrics,
            'R2C': r2c_metrics,
            'asymmetry_indices': asym,
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Transformation-Based Analyzer")
    parser.add_argument(
        '--newspaper', default='Times-of-India',
        choices=['Times-of-India', 'Hindustan-Times', 'The-Hindu'],
    )
    args = parser.parse_args()

    analyzer = TransformationBasedAnalyzer(args.newspaper)
    results  = analyzer.analyze()

    out_dir = (Path(__file__).parent / 'output' / 'complexity-similarity-study' /
               'per-newspaper' / args.newspaper / 'transformation')
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / 'transformation_based_metrics.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n✓ Saved: {json_path}")


if __name__ == '__main__':
    main()
