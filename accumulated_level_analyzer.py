#!/usr/bin/env python3
"""
Accumulated Level Analyzer

Computes accumulated complexity and similarity by progressively combining
linguistic levels from character to constituency.

Levels (in order):
  L1: character only
  L2: character + token (lexical)
  L3: character + token + morphological
  L4: character + token + morphological + dependency (structural dep)
  L5: character + token + morphological + dependency + constituency (structural const)

For each accumulated level computes:
  Complexity:
    - accumulated_entropy:   average of all per-level entropies up to Li
    - accumulated_diversity: average of TTR/MATTR/MTLD up to Li
    - information_gain:      delta vs accumulated_{i-1}

  Similarity:
    - accumulated_jaccard:   average Jaccard across all levels up to Li
    - accumulated_js_sim:    average JS similarity across all levels up to Li
    - accumulated_wasserstein: average Wasserstein (normalized) across all levels

Takes the results dicts directly from MultiLevelComplexityAnalyzer and
MultiLevelSimilarityAnalyzer so no re-computation is needed.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class AccumulatedLevelAnalyzer:
    """Compute accumulated metrics from char→constituency levels."""

    # Level ordering and human-readable names
    LEVELS: List[Tuple[str, str]] = [
        ('L1', 'character'),
        ('L2', 'token'),
        ('L3', 'morphological'),
        ('L4', 'dependency'),
        ('L5', 'constituency'),
    ]

    def __init__(
        self,
        newspaper: str,
        complexity_results: Dict,
        similarity_results: Dict,
    ):
        self.newspaper = newspaper
        self.cx = complexity_results   # from MultiLevelComplexityAnalyzer.results
        self.sx = similarity_results   # from MultiLevelSimilarityAnalyzer.results

        self.project_root = Path(__file__).parent
        self.output_dir = (self.project_root / 'output' / 'complexity-similarity-study' /
                           'per-newspaper' / newspaper / 'accumulated')
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # EXTRACT PER-LEVEL SCALARS
    # =========================================================================

    def _complexity_scalars_at_level(self, level_key: str) -> Dict:
        """Extract scalar complexity metrics for one linguistic level."""
        scalars = {}

        if level_key == 'character':
            for reg in ['canonical', 'headline']:
                m = self.cx.get('character', {}).get(reg, {})
                scalars[f'{reg}_entropy']  = m.get('char_entropy', 0.0)
                scalars[f'{reg}_diversity'] = m.get('char_mattr', 0.0)

        elif level_key == 'token':
            for reg in ['canonical', 'headline']:
                m = self.cx.get('lexical', {}).get('surface_forms', {}).get(reg, {})
                scalars[f'{reg}_entropy']   = m.get('entropy', 0.0)
                scalars[f'{reg}_diversity'] = m.get('mattr', 0.0)

        elif level_key == 'morphological':
            for reg in ['canonical', 'headline']:
                m = self.cx.get('morphological', {}).get('pos_tags', {}).get(reg, {})
                scalars[f'{reg}_entropy']   = m.get('entropy', 0.0)
                scalars[f'{reg}_diversity'] = m.get('mattr', 0.0)

        elif level_key == 'dependency':
            for reg in ['canonical', 'headline']:
                m = self.cx.get('structural', {}).get('dependency', {}).get(reg, {})
                # Use dep_distance_entropy as entropy proxy; MDD normalized as diversity
                scalars[f'{reg}_entropy']   = m.get('dep_distance_entropy', 0.0)
                scalars[f'{reg}_diversity'] = m.get('mdd_normalized', 0.0)

        elif level_key == 'constituency':
            for reg in ['canonical', 'headline']:
                m = self.cx.get('structural', {}).get('constituency', {}).get(reg, {})
                scalars[f'{reg}_entropy']   = m.get('production_rule_entropy', 0.0)
                scalars[f'{reg}_diversity'] = m.get('avg_branching_factor', 0.0)

        return scalars

    def _similarity_scalars_at_level(self, level_key: str) -> Dict:
        """Extract scalar similarity metrics for one linguistic level."""
        scalars = {}

        if level_key == 'character':
            m = self.sx.get('character', {})
            scalars['jaccard']     = m.get('char_ngram_jaccard_avg', 0.0)
            scalars['js_sim']      = m.get('js_similarity', 0.0)
            scalars['wasserstein'] = m.get('wasserstein_distance_normalized', 0.0)

        elif level_key == 'token':
            m = self.sx.get('lexical', {}).get('surface_forms', {})
            scalars['jaccard']     = m.get('jaccard_similarity', 0.0)
            scalars['js_sim']      = m.get('js_similarity', 0.0)
            scalars['wasserstein'] = m.get('wasserstein_distance_normalized', 0.0)

        elif level_key == 'morphological':
            m = self.sx.get('morphological', {}).get('pos_tags', {})
            scalars['jaccard']     = m.get('jaccard_similarity', 0.0)
            scalars['js_sim']      = m.get('js_similarity', 0.0)
            scalars['wasserstein'] = m.get('wasserstein_distance_normalized', 0.0)

        elif level_key == 'dependency':
            m = self.sx.get('syntactic', {}).get('dependency_relations', {})
            scalars['jaccard']     = m.get('jaccard_similarity', 0.0)
            scalars['js_sim']      = m.get('js_similarity', 0.0)
            scalars['wasserstein'] = m.get('wasserstein_distance_normalized', 0.0)

        elif level_key == 'constituency':
            m = self.sx.get('syntactic', {}).get('constituency_labels', {})
            scalars['jaccard']     = m.get('jaccard_similarity', 0.0)
            scalars['js_sim']      = m.get('js_similarity', 0.0)
            scalars['wasserstein'] = m.get('wasserstein_distance_normalized', 0.0)

        return scalars

    # =========================================================================
    # ACCUMULATED COMPUTATION
    # =========================================================================

    def compute_accumulated_complexity(self) -> pd.DataFrame:
        """Compute accumulated complexity from L1→L5."""
        rows = []
        running_canon_entropy  = []
        running_hl_entropy     = []
        running_canon_diversity = []
        running_hl_diversity    = []

        for label, level_key in self.LEVELS:
            scalars = self._complexity_scalars_at_level(level_key)

            ce = scalars.get('canonical_entropy',  0.0)
            he = scalars.get('headline_entropy',   0.0)
            cd = scalars.get('canonical_diversity', 0.0)
            hd = scalars.get('headline_diversity',  0.0)

            running_canon_entropy.append(ce)
            running_hl_entropy.append(he)
            running_canon_diversity.append(cd)
            running_hl_diversity.append(hd)

            acc_ce  = float(np.mean(running_canon_entropy))
            acc_he  = float(np.mean(running_hl_entropy))
            acc_cd  = float(np.mean(running_canon_diversity))
            acc_hd  = float(np.mean(running_hl_diversity))

            # Information gain: delta entropy (canonical) vs previous level
            prev_acc_ce = float(np.mean(running_canon_entropy[:-1])) if len(running_canon_entropy) > 1 else 0.0
            info_gain   = acc_ce - prev_acc_ce

            rows.append({
                'newspaper':                  self.newspaper,
                'level_label':                label,
                'level_name':                 level_key,
                'level_index':                len(rows) + 1,
                'level_entropy_canonical':    ce,
                'level_entropy_headline':     he,
                'level_diversity_canonical':  cd,
                'level_diversity_headline':   hd,
                'accumulated_entropy_canonical':   acc_ce,
                'accumulated_entropy_headline':    acc_he,
                'accumulated_diversity_canonical': acc_cd,
                'accumulated_diversity_headline':  acc_hd,
                'information_gain':           info_gain,
                'entropy_ratio_CH':           acc_ce / acc_he if acc_he > 0 else 1.0,
            })

        df = pd.DataFrame(rows)
        out_path = self.output_dir / 'accumulated_complexity.csv'
        df.to_csv(out_path, index=False)
        print(f"  ✓ Saved accumulated complexity: {out_path}")
        return df

    def compute_accumulated_similarity(self) -> pd.DataFrame:
        """Compute accumulated similarity from L1→L5."""
        rows = []
        running_jac  = []
        running_js   = []
        running_wass = []

        for label, level_key in self.LEVELS:
            scalars = self._similarity_scalars_at_level(level_key)

            jac  = scalars.get('jaccard',     0.0)
            js   = scalars.get('js_sim',      0.0)
            wass = scalars.get('wasserstein', 0.0)

            running_jac.append(jac)
            running_js.append(js)
            running_wass.append(wass)

            acc_jac  = float(np.mean(running_jac))
            acc_js   = float(np.mean(running_js))
            acc_wass = float(np.mean(running_wass))

            prev_acc_jac = float(np.mean(running_jac[:-1])) if len(running_jac) > 1 else 0.0
            sim_gain     = acc_jac - prev_acc_jac

            rows.append({
                'newspaper':                  self.newspaper,
                'level_label':                label,
                'level_name':                 level_key,
                'level_index':                len(rows) + 1,
                'level_jaccard':              jac,
                'level_js_similarity':        js,
                'level_wasserstein_norm':     wass,
                'accumulated_jaccard':        acc_jac,
                'accumulated_js_similarity':  acc_js,
                'accumulated_wasserstein':    acc_wass,
                'similarity_gain':            sim_gain,
                # Wasserstein is a distance; lower = more similar
                'accumulated_wasserstein_similarity': max(0.0, 1.0 - acc_wass),
            })

        df = pd.DataFrame(rows)
        out_path = self.output_dir / 'accumulated_similarity.csv'
        df.to_csv(out_path, index=False)
        print(f"  ✓ Saved accumulated similarity: {out_path}")
        return df

    def compute_information_gain(self, acc_complexity: pd.DataFrame) -> pd.DataFrame:
        """Return information gain per level (delta accumulated entropy)."""
        if acc_complexity.empty:
            return pd.DataFrame()

        df = acc_complexity[['newspaper', 'level_label', 'level_name',
                              'level_index', 'information_gain',
                              'accumulated_entropy_canonical']].copy()
        df['information_gain_headline'] = (
            acc_complexity['accumulated_entropy_headline'] -
            acc_complexity['accumulated_entropy_headline'].shift(1, fill_value=0)
        )
        out_path = self.output_dir / 'information_gain.csv'
        df.to_csv(out_path, index=False)
        print(f"  ✓ Saved information gain: {out_path}")
        return df

    def compute_all(self) -> Dict:
        """Run all accumulated level analyses."""
        print(f"\n{'='*80}")
        print(f"ACCUMULATED LEVEL ANALYSIS: {self.newspaper}")
        print(f"{'='*80}\n")

        acc_cx = self.compute_accumulated_complexity()
        acc_sx = self.compute_accumulated_similarity()
        ig     = self.compute_information_gain(acc_cx)

        print(f"✓ Accumulated analysis complete for {self.newspaper}")
        return {
            'accumulated_complexity': acc_cx,
            'accumulated_similarity': acc_sx,
            'information_gain':       ig,
        }


def main():
    """Standalone runner — requires running complexity + similarity analyzers first."""
    import argparse
    parser = argparse.ArgumentParser(description="Accumulated Level Analyzer")
    parser.add_argument(
        '--newspaper', default='Times-of-India',
        choices=['Times-of-India', 'Hindustan-Times', 'The-Hindu'],
    )
    args = parser.parse_args()

    # Load pre-existing JSON results
    root = Path(__file__).parent
    cx_json = root / 'output' / 'multilevel_complexity' / args.newspaper / 'multilevel_complexity_analysis.json'
    sx_json = root / 'output' / 'multilevel_similarity' / args.newspaper / 'multilevel_similarity_analysis.json'

    cx_results: Dict = {}
    sx_results: Dict = {}

    if cx_json.exists():
        with open(cx_json, 'r') as f:
            cx_results = json.load(f)
        print(f"Loaded complexity results: {cx_json}")
    else:
        print(f"Warning: {cx_json} not found — run multilevel_complexity_analyzer.py first")

    if sx_json.exists():
        with open(sx_json, 'r') as f:
            sx_results = json.load(f)
        print(f"Loaded similarity results: {sx_json}")
    else:
        print(f"Warning: {sx_json} not found — run multilevel_similarity_analyzer.py first")

    analyzer = AccumulatedLevelAnalyzer(args.newspaper, cx_results, sx_results)
    analyzer.compute_all()


if __name__ == '__main__':
    main()
