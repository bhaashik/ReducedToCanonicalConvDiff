#!/usr/bin/env python3
"""
Comprehensive Task 3 Runner

Unified runner for all Task 3 (Complexity & Similarity Study) analyses:
  1. Extended multi-level complexity (MultiLevelComplexityAnalyzer v2)
  2. Extended multi-level similarity (MultiLevelSimilarityAnalyzer v2)
  3. Transformation-based analysis (TransformationBasedAnalyzer)
  4. Accumulated level analysis (AccumulatedLevelAnalyzer)
  5. Cross-newspaper aggregation and visualization

Output directory:
  output/complexity-similarity-study/
    per-newspaper/{Newspaper}/
      complexity/        — per-level CSV summaries
      similarity/        — per-level CSV summaries + bidirectional metrics
      transformation/    — transformation-based metrics
      accumulated/       — L1..L5 accumulated curves
    global/
      cross_newspaper_complexity.csv
      cross_newspaper_similarity.csv
      accumulated_levels_comparison.csv
      comprehensive_summary.csv
    figures/
      complexity_by_level_and_newspaper.png
      similarity_by_level_and_newspaper.png
      accumulated_complexity_curve.png
      accumulated_similarity_curve.png
      information_gain_by_level.png
      directional_asymmetry_heatmap.png
      transformation_density_by_type.png
      lexical_diversity_comparison.png
"""

import sys
import json
import shutil
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from multilevel_complexity_analyzer import MultiLevelComplexityAnalyzer
from multilevel_similarity_analyzer  import MultiLevelSimilarityAnalyzer
from transformation_based_analyzer   import TransformationBasedAnalyzer
from accumulated_level_analyzer      import AccumulatedLevelAnalyzer


sns.set_style('whitegrid')
plt.rcParams.update({'figure.figsize': (12, 8), 'font.size': 11})

NEWSPAPERS = ['Times-of-India', 'Hindustan-Times', 'The-Hindu']
PAPER_SHORT = {'Times-of-India': 'ToI', 'Hindustan-Times': 'HT', 'The-Hindu': 'TH'}


class ComprehensiveTask3Runner:
    """Orchestrates all Task 3 analyses and produces unified outputs."""

    def __init__(self, newspapers: Optional[List[str]] = None):
        self.newspapers  = newspapers or NEWSPAPERS
        self.project_root = Path(__file__).parent
        self.output_dir  = self.project_root / 'output' / 'complexity-similarity-study'
        self.global_dir  = self.output_dir / 'global'
        self.figures_dir = self.output_dir / 'figures'
        self.tables_dir  = self.output_dir / 'tables'

        for d in [self.global_dir, self.figures_dir, self.tables_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.all_cx_results:   Dict[str, Dict] = {}
        self.all_sx_results:   Dict[str, Dict] = {}
        self.all_tf_results:   Dict[str, Dict] = {}
        self.all_acc_cx:       Dict[str, pd.DataFrame] = {}
        self.all_acc_sx:       Dict[str, pd.DataFrame] = {}

    # =========================================================================
    # LOGGING
    # =========================================================================

    def log(self, msg: str, level: str = "INFO"):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] [{level}] {msg}")

    # =========================================================================
    # PER-NEWSPAPER PIPELINE
    # =========================================================================

    def _run_newspaper(self, newspaper: str):
        self.log(f"{'='*60}")
        self.log(f"Processing: {newspaper}")
        self.log(f"{'='*60}")

        per_dir = self.output_dir / 'per-newspaper' / newspaper
        per_dir.mkdir(parents=True, exist_ok=True)

        # ------ Step 1: Complexity ------
        self.log(f"[{newspaper}] Step 1 — Extended complexity analysis")
        try:
            cx_analyzer = MultiLevelComplexityAnalyzer(newspaper)
            cx_analyzer.run_complete_analysis()
            self.all_cx_results[newspaper] = cx_analyzer.results

            # Copy summary CSV to per-newspaper folder
            src = cx_analyzer.output_dir / 'multilevel_complexity_summary.csv'
            dst_dir = per_dir / 'complexity'
            dst_dir.mkdir(parents=True, exist_ok=True)
            if src.exists():
                shutil.copy2(src, dst_dir / 'complexity_summary.csv')

            self.log(f"[{newspaper}] ✓ Complexity done", "SUCCESS")
        except Exception as e:
            self.log(f"[{newspaper}] ✗ Complexity failed: {e}", "ERROR")

        # ------ Step 2: Similarity ------
        self.log(f"[{newspaper}] Step 2 — Extended similarity analysis")
        try:
            sx_analyzer = MultiLevelSimilarityAnalyzer(newspaper)
            sx_analyzer.run_complete_analysis()
            self.all_sx_results[newspaper] = sx_analyzer.results

            src_dir = sx_analyzer.output_dir
            dst_dir = per_dir / 'similarity'
            dst_dir.mkdir(parents=True, exist_ok=True)
            for fname in ['multilevel_similarity_summary.csv', 'bidirectional_metrics.csv']:
                src = src_dir / fname
                if src.exists():
                    shutil.copy2(src, dst_dir / fname)

            self.log(f"[{newspaper}] ✓ Similarity done", "SUCCESS")
        except Exception as e:
            self.log(f"[{newspaper}] ✗ Similarity failed: {e}", "ERROR")

        # ------ Step 3: Transformation-based ------
        self.log(f"[{newspaper}] Step 3 — Transformation-based analysis")
        try:
            tf_analyzer = TransformationBasedAnalyzer(newspaper)
            tf_results  = tf_analyzer.analyze()
            self.all_tf_results[newspaper] = tf_results

            tf_dir = per_dir / 'transformation'
            tf_dir.mkdir(parents=True, exist_ok=True)
            with open(tf_dir / 'transformation_based_metrics.json', 'w') as f:
                json.dump(tf_results, f, indent=2, default=str)

            self.log(f"[{newspaper}] ✓ Transformation analysis done", "SUCCESS")
        except Exception as e:
            self.log(f"[{newspaper}] ✗ Transformation analysis failed: {e}", "ERROR")

        # ------ Step 4: Accumulated levels ------
        self.log(f"[{newspaper}] Step 4 — Accumulated level analysis")
        try:
            cx_res = self.all_cx_results.get(newspaper, {})
            sx_res = self.all_sx_results.get(newspaper, {})
            acc = AccumulatedLevelAnalyzer(newspaper, cx_res, sx_res)
            acc_results = acc.compute_all()
            self.all_acc_cx[newspaper] = acc_results.get('accumulated_complexity', pd.DataFrame())
            self.all_acc_sx[newspaper] = acc_results.get('accumulated_similarity', pd.DataFrame())

            self.log(f"[{newspaper}] ✓ Accumulated analysis done", "SUCCESS")
        except Exception as e:
            self.log(f"[{newspaper}] ✗ Accumulated analysis failed: {e}", "ERROR")

    # =========================================================================
    # CROSS-NEWSPAPER AGGREGATION
    # =========================================================================

    def _aggregate_global(self):
        self.log("Aggregating global cross-newspaper results...")

        # --- Complexity global table ---
        cx_rows = []
        for newspaper in self.newspapers:
            cx_csv = (self.project_root / 'output' / 'multilevel_complexity' /
                      newspaper / 'multilevel_complexity_summary.csv')
            if cx_csv.exists():
                try:
                    df = pd.read_csv(cx_csv)
                    df['newspaper'] = newspaper
                    cx_rows.append(df)
                except Exception:
                    pass

        if cx_rows:
            global_cx = pd.concat(cx_rows, ignore_index=True)
            global_cx.to_csv(self.global_dir / 'cross_newspaper_complexity.csv', index=False)
            self.log(f"  ✓ Saved global complexity CSV")
        else:
            global_cx = pd.DataFrame()

        # --- Similarity global table ---
        sx_rows = []
        for newspaper in self.newspapers:
            sx_csv = (self.project_root / 'output' / 'multilevel_similarity' /
                      newspaper / 'multilevel_similarity_summary.csv')
            if sx_csv.exists():
                try:
                    df = pd.read_csv(sx_csv)
                    df['newspaper'] = newspaper
                    sx_rows.append(df)
                except Exception:
                    pass

        if sx_rows:
            global_sx = pd.concat(sx_rows, ignore_index=True)
            global_sx.to_csv(self.global_dir / 'cross_newspaper_similarity.csv', index=False)
            self.log(f"  ✓ Saved global similarity CSV")
        else:
            global_sx = pd.DataFrame()

        # --- Accumulated levels global table ---
        acc_rows = []
        for newspaper in self.newspapers:
            acc_cx = self.all_acc_cx.get(newspaper, pd.DataFrame())
            acc_sx = self.all_acc_sx.get(newspaper, pd.DataFrame())
            if not acc_cx.empty and not acc_sx.empty:
                merged = acc_cx.merge(
                    acc_sx[['level_label', 'accumulated_jaccard',
                             'accumulated_js_similarity', 'accumulated_wasserstein']],
                    on='level_label', how='left'
                )
                acc_rows.append(merged)

        if acc_rows:
            global_acc = pd.concat(acc_rows, ignore_index=True)
            global_acc.to_csv(self.global_dir / 'accumulated_levels_comparison.csv', index=False)
            self.log(f"  ✓ Saved accumulated levels CSV")
        else:
            global_acc = pd.DataFrame()

        # --- Comprehensive summary ---
        self._write_comprehensive_summary(global_cx, global_sx)

        return global_cx, global_sx, global_acc

    def _write_comprehensive_summary(self, cx: pd.DataFrame, sx: pd.DataFrame):
        rows = []
        for newspaper in self.newspapers:
            row = {'newspaper': newspaper}

            if not cx.empty and 'newspaper' in cx.columns:
                news_cx = cx[cx['newspaper'] == newspaper]
                if not news_cx.empty:
                    if 'entropy' in news_cx.columns:
                        for reg in ['canonical', 'headline']:
                            sub = news_cx[news_cx.get('register', pd.Series()) == reg] if 'register' in news_cx.columns else pd.DataFrame()
                            if not sub.empty:
                                row[f'avg_entropy_{reg}'] = float(sub['entropy'].mean())

            if not sx.empty and 'newspaper' in sx.columns:
                news_sx = sx[sx['newspaper'] == newspaper]
                if not news_sx.empty:
                    for col in ['jaccard_similarity', 'js_similarity']:
                        if col in news_sx.columns:
                            row[f'avg_{col}'] = float(news_sx[col].mean())

            # Transformation metrics
            tf = self.all_tf_results.get(newspaper, {})
            cx_tf = tf.get('complexity', {})
            if 'transformation_density' in cx_tf:
                row['avg_events_per_sent'] = cx_tf['transformation_density'].get('avg_events_per_sentence', 0)
            if 'rule_entropy' in cx_tf:
                row['rule_entropy'] = cx_tf['rule_entropy'].get('rule_entropy', 0)

            rows.append(row)

        if rows:
            summary_df = pd.DataFrame(rows)
            summary_df.to_csv(self.tables_dir / 'comprehensive_summary.csv', index=False)
            self.log(f"  ✓ Saved comprehensive summary")

    # =========================================================================
    # VISUALIZATIONS
    # =========================================================================

    def _create_visualizations(
        self,
        global_cx: pd.DataFrame,
        global_sx: pd.DataFrame,
        global_acc: pd.DataFrame
    ):
        self.log("Creating figures...")

        self._fig_complexity_by_level(global_cx)
        self._fig_similarity_by_level(global_sx)
        self._fig_accumulated_complexity(global_acc)
        self._fig_accumulated_similarity(global_acc)
        self._fig_information_gain(global_acc)
        self._fig_directional_asymmetry(global_sx)
        self._fig_transformation_density()
        self._fig_lexical_diversity(global_cx)

    def _save_fig(self, name: str):
        path = self.figures_dir / name
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        self.log(f"  ✓ Saved figure: {path.name}")

    # ------------------------------------------------------------------
    def _fig_complexity_by_level(self, df: pd.DataFrame):
        if df.empty or 'entropy' not in df.columns:
            return
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Complexity (Entropy) by Linguistic Level and Newspaper', fontweight='bold')

        for ax, register in zip(axes, ['canonical', 'headline']):
            sub = df[df.get('register', pd.Series()) == register] if 'register' in df.columns else df
            if sub.empty:
                continue
            try:
                pivot = sub.pivot_table(values='entropy', index='level',
                                        columns='newspaper', aggfunc='mean')
                if not pivot.empty:
                    pivot.plot(kind='bar', ax=ax)
                    ax.set_title(f'{register.capitalize()} Register')
                    ax.set_xlabel('Level')
                    ax.set_ylabel('Entropy (bits)')
                    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha='right')
                    ax.legend(title='Newspaper', fontsize=8)
            except Exception:
                pass

        plt.tight_layout()
        self._save_fig('complexity_by_level_and_newspaper.png')

    # ------------------------------------------------------------------
    def _fig_similarity_by_level(self, df: pd.DataFrame):
        if df.empty or 'jaccard_similarity' not in df.columns:
            return
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Similarity by Linguistic Level and Newspaper', fontweight='bold')

        for ax, metric, title in zip(
            axes,
            ['jaccard_similarity', 'js_similarity'],
            ['Jaccard Similarity', 'JS Similarity']
        ):
            if metric not in df.columns:
                continue
            sub = df[df[metric].notna()]
            if sub.empty:
                continue
            try:
                pivot = sub.pivot_table(values=metric, index='level',
                                        columns='newspaper', aggfunc='mean')
                if not pivot.empty:
                    pivot.plot(kind='bar', ax=ax)
                    ax.set_title(title)
                    ax.set_xlabel('Level')
                    ax.set_ylabel(title)
                    ax.set_ylim([0, 1])
                    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha='right')
                    ax.legend(title='Newspaper', fontsize=8)
            except Exception:
                pass

        plt.tight_layout()
        self._save_fig('similarity_by_level_and_newspaper.png')

    # ------------------------------------------------------------------
    def _fig_accumulated_complexity(self, df: pd.DataFrame):
        if df.empty or 'accumulated_entropy_canonical' not in df.columns:
            return

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Accumulated Complexity Curve (char→constituency)', fontweight='bold')

        for ax, col, title in zip(
            axes,
            ['accumulated_entropy_canonical', 'accumulated_entropy_headline'],
            ['Canonical Register', 'Headline Register']
        ):
            if col not in df.columns:
                continue
            for newspaper in self.newspapers:
                sub = df[df['newspaper'] == newspaper] if 'newspaper' in df.columns else df
                if sub.empty:
                    continue
                sub = sub.sort_values('level_index')
                ax.plot(sub['level_label'], sub[col],
                        marker='o', label=PAPER_SHORT.get(newspaper, newspaper))
            ax.set_title(title)
            ax.set_xlabel('Accumulated Level')
            ax.set_ylabel('Accumulated Entropy (avg, bits)')
            ax.legend(title='Newspaper')
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        self._save_fig('accumulated_complexity_curve.png')

    # ------------------------------------------------------------------
    def _fig_accumulated_similarity(self, df: pd.DataFrame):
        if df.empty or 'accumulated_jaccard' not in df.columns:
            return

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Accumulated Similarity Curve (char→constituency)', fontweight='bold')

        for ax, col, title in zip(
            axes,
            ['accumulated_jaccard', 'accumulated_js_similarity'],
            ['Accumulated Jaccard', 'Accumulated JS Similarity']
        ):
            if col not in df.columns:
                continue
            for newspaper in self.newspapers:
                sub = df[df['newspaper'] == newspaper] if 'newspaper' in df.columns else df
                if sub.empty:
                    continue
                sub = sub.sort_values('level_index')
                ax.plot(sub['level_label'], sub[col],
                        marker='o', label=PAPER_SHORT.get(newspaper, newspaper))
            ax.set_title(title)
            ax.set_xlabel('Accumulated Level')
            ax.set_ylabel(title)
            ax.set_ylim([0, 1])
            ax.legend(title='Newspaper')
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        self._save_fig('accumulated_similarity_curve.png')

    # ------------------------------------------------------------------
    def _fig_information_gain(self, df: pd.DataFrame):
        if df.empty or 'information_gain' not in df.columns:
            return

        fig, ax = plt.subplots(figsize=(10, 6))
        fig.suptitle('Information Gain per Linguistic Level', fontweight='bold')

        level_labels = df['level_label'].unique() if 'level_label' in df.columns else []
        newspapers   = df['newspaper'].unique() if 'newspaper' in df.columns else []

        x = np.arange(len(level_labels))
        width = 0.25

        for i, newspaper in enumerate(newspapers):
            sub = df[df['newspaper'] == newspaper].sort_values('level_index') if 'newspaper' in df.columns else df
            if sub.empty:
                continue
            gains = sub['information_gain'].values
            ax.bar(x + i * width, gains, width,
                   label=PAPER_SHORT.get(newspaper, newspaper), alpha=0.8)

        ax.set_xticks(x + width)
        ax.set_xticklabels(level_labels)
        ax.set_xlabel('Linguistic Level')
        ax.set_ylabel('Information Gain (delta accumulated entropy, bits)')
        ax.axhline(0, color='black', linewidth=0.8)
        ax.legend(title='Newspaper')
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        self._save_fig('information_gain_by_level.png')

    # ------------------------------------------------------------------
    def _fig_directional_asymmetry(self, df: pd.DataFrame):
        asym_cols = [c for c in df.columns if 'asymmetry' in c.lower() or
                     ('C2H' in c and c.replace('C2H', 'H2C') in df.columns)]
        if df.empty or not asym_cols:
            # Build from kl_divergence if available
            if 'kl_divergence_C2H' in df.columns and 'kl_divergence_H2C' in df.columns:
                df['kl_asymmetry'] = abs(df['kl_divergence_C2H'] - df['kl_divergence_H2C'])
                asym_cols = ['kl_asymmetry']
            else:
                return

        fig, ax = plt.subplots(figsize=(10, 6))
        fig.suptitle('Directional Asymmetry |Metric(C→H) - Metric(H→C)|', fontweight='bold')

        if 'level' in df.columns and 'newspaper' in df.columns and asym_cols:
            try:
                pivot = df.pivot_table(values=asym_cols[0], index='level',
                                       columns='newspaper', aggfunc='mean')
                sns.heatmap(pivot, annot=True, fmt='.3f', cmap='YlOrRd',
                            ax=ax, cbar_kws={'label': 'Asymmetry'})
                ax.set_title(f'Asymmetry: {asym_cols[0]}')
            except Exception:
                pass

        plt.tight_layout()
        self._save_fig('directional_asymmetry_heatmap.png')

    # ------------------------------------------------------------------
    def _fig_transformation_density(self):
        """Stacked bar: transformation type proportions per newspaper."""
        rows = []
        for newspaper in self.newspapers:
            tf = self.all_tf_results.get(newspaper, {})
            td = tf.get('complexity', {}).get('type_distribution', {})
            proportions = td.get('proportions', {})
            if proportions:
                rows.append({'newspaper': PAPER_SHORT.get(newspaper, newspaper),
                              **proportions})

        if not rows:
            return

        df = pd.DataFrame(rows).set_index('newspaper')
        cols = [c for c in ['lexical', 'morphological', 'syntactic', 'structural'] if c in df.columns]
        if not cols:
            return

        fig, ax = plt.subplots(figsize=(10, 6))
        fig.suptitle('Transformation Type Distribution by Newspaper', fontweight='bold')
        df[cols].plot(kind='bar', stacked=True, ax=ax, colormap='Set2')
        ax.set_xlabel('Newspaper')
        ax.set_ylabel('Proportion of Transformations')
        ax.set_ylim([0, 1])
        ax.legend(title='Type', bbox_to_anchor=(1.05, 1))
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
        plt.tight_layout()
        self._save_fig('transformation_density_by_type.png')

    # ------------------------------------------------------------------
    def _fig_lexical_diversity(self, cx: pd.DataFrame):
        """Compare MATTR, MTLD, HD-D across newspapers and registers."""
        if cx.empty:
            return

        metrics = ['mattr', 'mtld', 'hdd', 'yules_k']
        available = [m for m in metrics if m in cx.columns]
        if not available:
            return

        n_metrics = len(available)
        fig, axes = plt.subplots(1, n_metrics, figsize=(4 * n_metrics, 6))
        if n_metrics == 1:
            axes = [axes]
        fig.suptitle('Lexical Diversity Metrics by Newspaper and Register', fontweight='bold')

        for ax, metric in zip(axes, available):
            sub = cx[cx[metric].notna()].copy()
            if sub.empty:
                continue
            try:
                plot_cols = [c for c in ['level', 'sublevel', 'register', 'newspaper', metric]
                             if c in sub.columns]
                if 'register' in sub.columns and 'newspaper' in sub.columns:
                    pivot = sub.pivot_table(values=metric, index='newspaper',
                                            columns='register', aggfunc='mean')
                    if not pivot.empty:
                        pivot.plot(kind='bar', ax=ax)
                        ax.set_title(metric.upper())
                        ax.set_xlabel('Newspaper')
                        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
                        ax.legend(title='Register')
            except Exception:
                pass

        plt.tight_layout()
        self._save_fig('lexical_diversity_comparison.png')

    # =========================================================================
    # MASTER METRICS TABLE
    # =========================================================================

    def _write_master_table(self, global_cx: pd.DataFrame, global_sx: pd.DataFrame):
        """Write master table: comprehensive_metrics_all_levels.csv"""
        rows = []
        LEVELS = ['character', 'lexical', 'morphological', 'syntactic', 'structural']

        for newspaper in self.newspapers:
            for level in LEVELS:
                row = {'newspaper': newspaper, 'level': level}

                # Complexity
                if not global_cx.empty and 'newspaper' in global_cx.columns:
                    cx_sub = global_cx[
                        (global_cx['newspaper'] == newspaper) &
                        (global_cx.get('level', pd.Series()) == level)
                    ] if 'level' in global_cx.columns else pd.DataFrame()
                    for col in ['entropy', 'mattr', 'mtld', 'hdd']:
                        if not cx_sub.empty and col in cx_sub.columns:
                            for reg in ['canonical', 'headline']:
                                reg_sub = cx_sub[cx_sub.get('register', pd.Series()) == reg] \
                                    if 'register' in cx_sub.columns else cx_sub
                                if not reg_sub.empty:
                                    row[f'{col}_{reg}'] = float(reg_sub[col].mean())

                # Similarity
                if not global_sx.empty and 'newspaper' in global_sx.columns:
                    sx_sub = global_sx[
                        (global_sx['newspaper'] == newspaper) &
                        (global_sx.get('level', pd.Series()) == level)
                    ] if 'level' in global_sx.columns else pd.DataFrame()
                    for col in ['jaccard_similarity', 'js_similarity',
                                'wasserstein_distance_normalized']:
                        if not sx_sub.empty and col in sx_sub.columns:
                            row[col] = float(sx_sub[col].mean())

                rows.append(row)

        if rows:
            master_df = pd.DataFrame(rows)
            path = self.tables_dir / 'comprehensive_metrics_all_levels.csv'
            master_df.to_csv(path, index=False)
            self.log(f"  ✓ Saved master table: {path.name}")

    # =========================================================================
    # MAIN ENTRY POINT
    # =========================================================================

    def run(self):
        print('=' * 80)
        print('COMPREHENSIVE TASK 3 RUNNER')
        print('Complexity & Similarity Study — All Levels')
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print('=' * 80)
        print(f"\nNewspapers: {', '.join(self.newspapers)}")
        print(f"Output dir: {self.output_dir}\n")

        # Per-newspaper analyses
        results_ok = []
        for newspaper in self.newspapers:
            try:
                self._run_newspaper(newspaper)
                results_ok.append(newspaper)
            except Exception as e:
                self.log(f"Error processing {newspaper}: {e}", "ERROR")

        if not results_ok:
            self.log("No newspapers completed. Exiting.", "ERROR")
            return False

        # Global aggregation
        print(f"\n{'='*80}")
        print("CROSS-NEWSPAPER AGGREGATION")
        print('=' * 80)
        global_cx, global_sx, global_acc = self._aggregate_global()

        # Figures
        print(f"\n{'='*80}")
        print("GENERATING FIGURES")
        print('=' * 80)
        self._create_visualizations(global_cx, global_sx, global_acc)

        # Master table
        self._write_master_table(global_cx, global_sx)

        # Summary
        print(f"\n{'='*80}")
        print("TASK 3 COMPLETE")
        print('=' * 80)
        print(f"\n✅ {len(results_ok)}/{len(self.newspapers)} newspapers completed")
        print(f"\n📁 Results at:")
        print(f"  - Per-newspaper: {self.output_dir}/per-newspaper/")
        print(f"  - Global tables: {self.global_dir}/")
        print(f"  - Figures:       {self.figures_dir}/")
        print(f"  - Master table:  {self.tables_dir}/comprehensive_metrics_all_levels.csv")
        return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Comprehensive Task 3 Runner")
    parser.add_argument(
        '--newspapers', nargs='+',
        default=['Times-of-India', 'Hindustan-Times', 'The-Hindu'],
        choices=['Times-of-India', 'Hindustan-Times', 'The-Hindu'],
        help='Newspapers to process',
    )
    args = parser.parse_args()

    runner = ComprehensiveTask3Runner(newspapers=args.newspapers)
    success = runner.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
