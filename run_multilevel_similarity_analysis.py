#!/usr/bin/env python3
"""
Comprehensive Multi-Level Similarity Analysis Runner

Runs multi-level similarity analysis across all newspapers and creates
comparative visualizations and reports.

Analyzes similarity at:
1. Lexical level (surface forms, lemmas)
2. Morphological level (POS tags, morphological features)
3. Syntactic level (dependency relations, constituency labels)
4. Structural level (tree alignment and correlation)

Uses comprehensive metrics from SIMILARITY-METRICS.md:
- Cross-entropy (both directions)
- Relative entropy / KL divergence (both directions)
- Jensen-Shannon divergence (symmetric, bounded)
- Symmetrized KL
- Bhattacharyya coefficient
- Hellinger distance
- Jaccard, Dice, Overlap coefficients
- Pearson and Spearman correlations
"""

import subprocess
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime


class MultiLevelSimilarityRunner:
    """Runs multi-level similarity analysis across all newspapers."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.newspapers = ['Times-of-India', 'Hindustan-Times', 'The-Hindu']
        self.output_dir = self.project_root / 'output' / 'multilevel_similarity'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.global_output = self.output_dir / 'GLOBAL_ANALYSIS'
        self.global_output.mkdir(parents=True, exist_ok=True)

        # Set plotting style
        sns.set_style('whitegrid')
        plt.rcParams['figure.figsize'] = (12, 8)

    def log(self, message: str, level: str = "INFO"):
        """Log messages."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def run_analysis_for_newspaper(self, newspaper: str) -> bool:
        """Run multi-level similarity analysis for a single newspaper."""
        self.log(f"Running similarity analysis for {newspaper}...", "INFO")

        script_file = self.project_root / 'multilevel_similarity_analyzer.py'

        try:
            result = subprocess.run(
                [sys.executable, str(script_file), '--newspaper', newspaper],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            if result.returncode == 0:
                self.log(f"✓ Completed: {newspaper}", "SUCCESS")
                return True
            else:
                self.log(f"✗ Failed: {newspaper}", "ERROR")
                if result.stderr:
                    self.log(f"Error: {result.stderr[:300]}", "ERROR")
                return False

        except subprocess.TimeoutExpired:
            self.log(f"✗ Timeout: {newspaper}", "ERROR")
            return False
        except Exception as e:
            self.log(f"✗ Exception: {newspaper} - {str(e)}", "ERROR")
            return False

    def aggregate_results(self) -> pd.DataFrame:
        """Aggregate results from all newspapers."""
        self.log("Aggregating similarity results from all newspapers...", "INFO")

        all_data = []

        for newspaper in self.newspapers:
            csv_path = self.output_dir / newspaper / 'multilevel_similarity_summary.csv'

            if csv_path.exists():
                try:
                    df = pd.read_csv(csv_path)
                    if not df.empty:
                        df['newspaper'] = newspaper
                        all_data.append(df)
                    else:
                        self.log(f"Warning: Empty CSV for {newspaper}", "WARNING")
                except (pd.errors.EmptyDataError, pd.errors.ParserError) as e:
                    self.log(f"Warning: Could not parse CSV for {newspaper}: {e}", "WARNING")
            else:
                self.log(f"Warning: No results found for {newspaper}", "WARNING")

        if not all_data:
            self.log("No data to aggregate", "ERROR")
            return pd.DataFrame()

        combined_df = pd.concat(all_data, ignore_index=True)

        # Save aggregated data
        agg_path = self.global_output / 'aggregated_similarity_metrics.csv'
        combined_df.to_csv(agg_path, index=False)
        self.log(f"✓ Saved aggregated data: {agg_path}", "SUCCESS")

        return combined_df

    def create_comparative_visualizations(self, df: pd.DataFrame):
        """Create comparative visualizations across newspapers."""
        self.log("Creating comparative visualizations...", "INFO")

        if df.empty:
            self.log("No data for visualization", "WARNING")
            return

        # 1. Jaccard similarity comparison
        self._plot_jaccard_similarity(df)

        # 2. Cross-entropy comparison
        self._plot_cross_entropy(df)

        # 3. KL divergence comparison (both directions)
        self._plot_kl_divergence(df)

        # 4. Jensen-Shannon similarity
        self._plot_js_similarity(df)

        # 5. Similarity heatmaps
        self._plot_similarity_heatmaps(df)

        # 6. Directional asymmetry analysis
        self._plot_directional_asymmetry(df)

        # 7. Correlation-based similarity
        self._plot_correlation_similarity(df)

        self.log("✓ All visualizations created", "SUCCESS")

    def _plot_jaccard_similarity(self, df: pd.DataFrame):
        """Plot Jaccard similarity comparison."""
        if 'jaccard_similarity' not in df.columns:
            return

        jaccard_data = df[df['jaccard_similarity'].notna()].copy()

        if jaccard_data.empty:
            return

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Jaccard Similarity Across Linguistic Levels', fontsize=16, fontweight='bold')

        # Plot 1: Jaccard by level
        ax = axes[0, 0]
        if not jaccard_data.empty:
            sns.barplot(data=jaccard_data, x='level', y='jaccard_similarity', ax=ax)
            ax.set_title('Jaccard Similarity by Linguistic Level')
            ax.set_xlabel('Linguistic Level')
            ax.set_ylabel('Jaccard Similarity (0=different, 1=identical)')
            ax.set_ylim([0, 1])

        # Plot 2: Jaccard by sublevel
        ax = axes[0, 1]
        if not jaccard_data.empty:
            sns.barplot(data=jaccard_data, x='sublevel', y='jaccard_similarity', ax=ax)
            ax.set_title('Jaccard Similarity by Sublevel')
            ax.set_xlabel('Sublevel')
            ax.set_ylabel('Jaccard Similarity')
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
            ax.set_ylim([0, 1])

        # Plot 3: Jaccard by newspaper
        ax = axes[1, 0]
        if not jaccard_data.empty:
            sns.boxplot(data=jaccard_data, x='newspaper', y='jaccard_similarity', ax=ax)
            ax.set_title('Jaccard Similarity Distribution by Newspaper')
            ax.set_xlabel('Newspaper')
            ax.set_ylabel('Jaccard Similarity')
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
            ax.set_ylim([0, 1])

        # Plot 4: Level comparison across newspapers
        ax = axes[1, 1]
        if not jaccard_data.empty:
            pivot_data = jaccard_data.pivot_table(
                values='jaccard_similarity',
                index='level',
                columns='newspaper',
                aggfunc='mean'
            )
            if not pivot_data.empty:
                pivot_data.plot(kind='bar', ax=ax)
                ax.set_title('Average Jaccard Similarity: Level × Newspaper')
                ax.set_xlabel('Linguistic Level')
                ax.set_ylabel('Average Jaccard Similarity')
                ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
                ax.legend(title='Newspaper', bbox_to_anchor=(1.05, 1))
                ax.set_ylim([0, 1])

        plt.tight_layout()
        save_path = self.global_output / 'jaccard_similarity_comparison.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        self.log(f"  ✓ Saved: {save_path}", "INFO")

    def _plot_cross_entropy(self, df: pd.DataFrame):
        """Plot cross-entropy comparison (both directions)."""
        has_ce = 'cross_entropy_1_to_2' in df.columns and 'cross_entropy_2_to_1' in df.columns

        if not has_ce:
            return

        ce_data = df[df['cross_entropy_1_to_2'].notna() & df['cross_entropy_2_to_1'].notna()].copy()

        if ce_data.empty:
            return

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Cross-Entropy Analysis (Lower = More Similar)', fontsize=16, fontweight='bold')

        # Plot 1: Canonical→Headline cross-entropy
        ax = axes[0, 0]
        sns.barplot(data=ce_data, x='level', y='cross_entropy_1_to_2', ax=ax)
        ax.set_title('Cross-Entropy: Canonical → Headline')
        ax.set_xlabel('Linguistic Level')
        ax.set_ylabel('Cross-Entropy H(C,H) (bits)')

        # Plot 2: Headline→Canonical cross-entropy
        ax = axes[0, 1]
        sns.barplot(data=ce_data, x='level', y='cross_entropy_2_to_1', ax=ax)
        ax.set_title('Cross-Entropy: Headline → Canonical')
        ax.set_xlabel('Linguistic Level')
        ax.set_ylabel('Cross-Entropy H(H,C) (bits)')

        # Plot 3: Bidirectional comparison
        ax = axes[1, 0]
        ce_melted = ce_data.melt(
            id_vars=['level', 'sublevel', 'newspaper'],
            value_vars=['cross_entropy_1_to_2', 'cross_entropy_2_to_1'],
            var_name='direction',
            value_name='cross_entropy'
        )
        ce_melted['direction'] = ce_melted['direction'].map({
            'cross_entropy_1_to_2': 'C→H',
            'cross_entropy_2_to_1': 'H→C'
        })
        sns.boxplot(data=ce_melted, x='level', y='cross_entropy', hue='direction', ax=ax)
        ax.set_title('Cross-Entropy: Bidirectional Comparison')
        ax.set_xlabel('Linguistic Level')
        ax.set_ylabel('Cross-Entropy (bits)')
        ax.legend(title='Direction')

        # Plot 4: Cross-entropy by newspaper
        ax = axes[1, 1]
        sns.boxplot(data=ce_melted, x='newspaper', y='cross_entropy', hue='direction', ax=ax)
        ax.set_title('Cross-Entropy by Newspaper')
        ax.set_xlabel('Newspaper')
        ax.set_ylabel('Cross-Entropy (bits)')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        ax.legend(title='Direction')

        plt.tight_layout()
        save_path = self.global_output / 'cross_entropy_comparison.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        self.log(f"  ✓ Saved: {save_path}", "INFO")

    def _plot_kl_divergence(self, df: pd.DataFrame):
        """Plot KL divergence comparison (asymmetric measure)."""
        has_kl = 'kl_divergence_1_to_2' in df.columns and 'kl_divergence_2_to_1' in df.columns

        if not has_kl:
            return

        kl_data = df[df['kl_divergence_1_to_2'].notna() & df['kl_divergence_2_to_1'].notna()].copy()

        if kl_data.empty:
            return

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('KL Divergence Analysis (Lower = More Similar)', fontsize=16, fontweight='bold')

        # Plot 1: KL divergence by level
        ax = axes[0, 0]
        kl_melted = kl_data.melt(
            id_vars=['level', 'sublevel', 'newspaper'],
            value_vars=['kl_divergence_1_to_2', 'kl_divergence_2_to_1'],
            var_name='direction',
            value_name='kl_divergence'
        )
        kl_melted['direction'] = kl_melted['direction'].map({
            'kl_divergence_1_to_2': 'D_KL(C||H)',
            'kl_divergence_2_to_1': 'D_KL(H||C)'
        })
        sns.barplot(data=kl_melted, x='level', y='kl_divergence', hue='direction', ax=ax)
        ax.set_title('KL Divergence by Linguistic Level')
        ax.set_xlabel('Linguistic Level')
        ax.set_ylabel('KL Divergence (bits)')
        ax.legend(title='Direction')

        # Plot 2: Symmetrized KL
        ax = axes[0, 1]
        if 'symmetrized_kl' in kl_data.columns:
            kl_sym = kl_data[kl_data['symmetrized_kl'].notna()]
            if not kl_sym.empty:
                sns.barplot(data=kl_sym, x='level', y='symmetrized_kl', ax=ax)
                ax.set_title('Symmetrized KL Divergence')
                ax.set_xlabel('Linguistic Level')
                ax.set_ylabel('D_sym(C,H) = D_KL(C||H) + D_KL(H||C)')

        # Plot 3: KL asymmetry (difference between directions)
        ax = axes[1, 0]
        kl_data['kl_asymmetry'] = abs(kl_data['kl_divergence_1_to_2'] - kl_data['kl_divergence_2_to_1'])
        sns.barplot(data=kl_data, x='level', y='kl_asymmetry', ax=ax)
        ax.set_title('KL Divergence Asymmetry')
        ax.set_xlabel('Linguistic Level')
        ax.set_ylabel('|D_KL(C||H) - D_KL(H||C)|')

        # Plot 4: KL by newspaper
        ax = axes[1, 1]
        sns.boxplot(data=kl_melted, x='newspaper', y='kl_divergence', hue='direction', ax=ax)
        ax.set_title('KL Divergence by Newspaper')
        ax.set_xlabel('Newspaper')
        ax.set_ylabel('KL Divergence (bits)')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        ax.legend(title='Direction')

        plt.tight_layout()
        save_path = self.global_output / 'kl_divergence_comparison.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        self.log(f"  ✓ Saved: {save_path}", "INFO")

    def _plot_js_similarity(self, df: pd.DataFrame):
        """Plot Jensen-Shannon similarity (symmetric, bounded)."""
        if 'js_similarity' not in df.columns:
            return

        js_data = df[df['js_similarity'].notna()].copy()

        if js_data.empty:
            return

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Jensen-Shannon Similarity (Symmetric, Bounded [0,1])', fontsize=14, fontweight='bold')

        # Plot 1: JS similarity by level
        ax = axes[0]
        sns.barplot(data=js_data, x='level', y='js_similarity', ax=ax)
        ax.set_title('JS Similarity by Linguistic Level')
        ax.set_xlabel('Linguistic Level')
        ax.set_ylabel('JS Similarity (1=identical, 0=different)')
        ax.set_ylim([0, 1])

        # Plot 2: JS similarity by newspaper
        ax = axes[1]
        sns.boxplot(data=js_data, x='newspaper', y='js_similarity', ax=ax)
        ax.set_title('JS Similarity Distribution by Newspaper')
        ax.set_xlabel('Newspaper')
        ax.set_ylabel('JS Similarity')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        ax.set_ylim([0, 1])

        plt.tight_layout()
        save_path = self.global_output / 'js_similarity_comparison.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        self.log(f"  ✓ Saved: {save_path}", "INFO")

    def _plot_similarity_heatmaps(self, df: pd.DataFrame):
        """Create heatmaps of similarity metrics."""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Similarity Heatmaps (Level × Newspaper)', fontsize=14, fontweight='bold')

        metrics = [
            ('jaccard_similarity', 'Jaccard Similarity', 'YlGn'),
            ('js_similarity', 'Jensen-Shannon Similarity', 'YlGnBu'),
            ('hellinger_similarity', 'Hellinger Similarity', 'RdYlGn'),
            ('bhattacharyya_coefficient', 'Bhattacharyya Coefficient', 'Purples')
        ]

        for idx, (metric, title, cmap) in enumerate(metrics):
            ax = axes[idx // 2, idx % 2]

            if metric in df.columns:
                metric_data = df[df[metric].notna()]
                if not metric_data.empty:
                    pivot = metric_data.pivot_table(
                        values=metric,
                        index='level',
                        columns='newspaper',
                        aggfunc='mean'
                    )
                    if not pivot.empty:
                        sns.heatmap(pivot, annot=True, fmt='.3f', cmap=cmap, ax=ax,
                                    vmin=0, vmax=1, cbar_kws={'label': title})
                        ax.set_title(title)
                        ax.set_xlabel('Newspaper')
                        ax.set_ylabel('Linguistic Level')

        plt.tight_layout()
        save_path = self.global_output / 'similarity_heatmaps.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        self.log(f"  ✓ Saved: {save_path}", "INFO")

    def _plot_directional_asymmetry(self, df: pd.DataFrame):
        """Plot directional asymmetry in cross-entropy and KL divergence."""
        has_metrics = all(col in df.columns for col in [
            'cross_entropy_1_to_2', 'cross_entropy_2_to_1',
            'kl_divergence_1_to_2', 'kl_divergence_2_to_1'
        ])

        if not has_metrics:
            return

        asym_data = df[df['cross_entropy_1_to_2'].notna()].copy()

        if asym_data.empty:
            return

        # Compute asymmetries
        asym_data['ce_asymmetry'] = abs(asym_data['cross_entropy_1_to_2'] - asym_data['cross_entropy_2_to_1'])
        asym_data['kl_asymmetry'] = abs(asym_data['kl_divergence_1_to_2'] - asym_data['kl_divergence_2_to_1'])

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Directional Asymmetry Analysis', fontsize=14, fontweight='bold')

        # Plot 1: Cross-entropy asymmetry
        ax = axes[0]
        sns.boxplot(data=asym_data, x='level', y='ce_asymmetry', ax=ax)
        ax.set_title('Cross-Entropy Asymmetry |H(C,H) - H(H,C)|')
        ax.set_xlabel('Linguistic Level')
        ax.set_ylabel('Asymmetry (bits)')

        # Plot 2: KL divergence asymmetry
        ax = axes[1]
        sns.boxplot(data=asym_data, x='level', y='kl_asymmetry', ax=ax)
        ax.set_title('KL Divergence Asymmetry |D_KL(C||H) - D_KL(H||C)|')
        ax.set_xlabel('Linguistic Level')
        ax.set_ylabel('Asymmetry (bits)')

        plt.tight_layout()
        save_path = self.global_output / 'directional_asymmetry.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        self.log(f"  ✓ Saved: {save_path}", "INFO")

    def _plot_correlation_similarity(self, df: pd.DataFrame):
        """Plot correlation-based similarity measures."""
        corr_cols = [col for col in df.columns if 'correlation' in col.lower() and '_p_value' not in col.lower()]

        if not corr_cols:
            return

        corr_data = df[df[corr_cols].notna().any(axis=1)].copy()

        if corr_data.empty:
            return

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Correlation-Based Similarity', fontsize=14, fontweight='bold')

        # Plot 1: Pearson correlation
        ax = axes[0]
        pearson_cols = [col for col in corr_cols if 'pearson' in col.lower()]
        if pearson_cols:
            for col in pearson_cols:
                data = corr_data[corr_data[col].notna()]
                if not data.empty:
                    sns.boxplot(data=data, x='level', y=col, ax=ax)
                    break
            ax.set_title('Pearson Correlation (Structural Similarity)')
            ax.set_xlabel('Linguistic Level')
            ax.set_ylabel('Correlation Coefficient')
            ax.set_ylim([-1, 1])
            ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)

        # Plot 2: Spearman correlation
        ax = axes[1]
        spearman_cols = [col for col in corr_cols if 'spearman' in col.lower()]
        if spearman_cols:
            for col in spearman_cols:
                data = corr_data[corr_data[col].notna()]
                if not data.empty:
                    sns.boxplot(data=data, x='level', y=col, ax=ax)
                    break
            ax.set_title('Spearman Correlation (Rank Similarity)')
            ax.set_xlabel('Linguistic Level')
            ax.set_ylabel('Correlation Coefficient')
            ax.set_ylim([-1, 1])
            ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)

        plt.tight_layout()
        save_path = self.global_output / 'correlation_similarity.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        self.log(f"  ✓ Saved: {save_path}", "INFO")

    def generate_summary_report(self, df: pd.DataFrame):
        """Generate comprehensive summary report."""
        self.log("Generating summary report...", "INFO")

        report_path = self.global_output / 'MULTILEVEL_SIMILARITY_REPORT.md'

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Multi-Level Similarity Analysis - Summary Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Newspapers**: {', '.join(self.newspapers)}\n\n")

            f.write("## Theoretical Framework\n\n")
            f.write("This analysis employs comprehensive similarity and divergence metrics ")
            f.write("from information theory and statistics (see SIMILARITY-METRICS.md):\n\n")

            f.write("### Entropy-Based Measures\n\n")
            f.write("- **Cross-Entropy** H(P,Q): Expected code length using Q to encode P\n")
            f.write("  - Asymmetric: H(P,Q) ≠ H(Q,P)\n")
            f.write("  - Decomposition: H(P,Q) = H(P) + D_KL(P||Q)\n")
            f.write("  - Lower values indicate more similar distributions\n\n")

            f.write("- **Relative Entropy / KL Divergence** D_KL(P||Q):\n")
            f.write("  - Information lost when Q is used to approximate P\n")
            f.write("  - Asymmetric divergence measure\n")
            f.write("  - D_KL(P||Q) ≥ 0, with equality iff P = Q\n\n")

            f.write("- **Jensen-Shannon Divergence** JSD(P,Q):\n")
            f.write("  - Symmetric: JSD(P,Q) = JSD(Q,P)\n")
            f.write("  - Bounded: 0 ≤ JSD ≤ 1 (with base-2 logs)\n")
            f.write("  - Square root forms a metric (triangle inequality)\n\n")

            f.write("### Set-Based Measures\n\n")
            f.write("- **Jaccard Similarity**: |A ∩ B| / |A ∪ B|\n")
            f.write("- **Dice Coefficient**: 2|A ∩ B| / (|A| + |B|)\n")
            f.write("- **Overlap Coefficient**: |A ∩ B| / min(|A|, |B|)\n\n")

            f.write("### Statistical Measures\n\n")
            f.write("- **Bhattacharyya Coefficient**: ∑√(P(x)Q(x))\n")
            f.write("- **Hellinger Distance**: √(½∑(√P(x) - √Q(x))²)\n")
            f.write("- **Pearson Correlation**: Linear relationship\n")
            f.write("- **Spearman Correlation**: Rank-order relationship\n\n")

            if not df.empty:
                f.write("## Summary Statistics\n\n")

                # Jaccard similarity
                if 'jaccard_similarity' in df.columns:
                    avg_jaccard = df['jaccard_similarity'].mean()
                    f.write(f"- **Average Jaccard Similarity**: {avg_jaccard:.4f}\n")

                # JS similarity
                if 'js_similarity' in df.columns:
                    avg_js = df['js_similarity'].mean()
                    f.write(f"- **Average JS Similarity**: {avg_js:.4f}\n")

                # Cross-entropy
                if 'cross_entropy_1_to_2' in df.columns and 'cross_entropy_2_to_1' in df.columns:
                    avg_ce_c2h = df['cross_entropy_1_to_2'].mean()
                    avg_ce_h2c = df['cross_entropy_2_to_1'].mean()
                    f.write(f"- **Average Cross-Entropy (C→H)**: {avg_ce_c2h:.4f} bits\n")
                    f.write(f"- **Average Cross-Entropy (H→C)**: {avg_ce_h2c:.4f} bits\n")

                # KL divergence
                if 'kl_divergence_1_to_2' in df.columns and 'kl_divergence_2_to_1' in df.columns:
                    avg_kl_c2h = df['kl_divergence_1_to_2'].mean()
                    avg_kl_h2c = df['kl_divergence_2_to_1'].mean()
                    f.write(f"- **Average KL Divergence (C→H)**: {avg_kl_c2h:.4f} bits\n")
                    f.write(f"- **Average KL Divergence (H→C)**: {avg_kl_h2c:.4f} bits\n")

                f.write("\n### Similarity by Linguistic Level\n\n")
                f.write("| Level | Jaccard | JS-Sim | Cross-Ent (C→H) | KL-Div (C→H) |\n")
                f.write("|-------|---------|--------|-----------------|-------------|\n")

                for level in df['level'].unique():
                    level_data = df[df['level'] == level]
                    jaccard = level_data['jaccard_similarity'].mean() if 'jaccard_similarity' in level_data.columns else 0
                    js_sim = level_data['js_similarity'].mean() if 'js_similarity' in level_data.columns else 0
                    ce = level_data['cross_entropy_1_to_2'].mean() if 'cross_entropy_1_to_2' in level_data.columns else 0
                    kl = level_data['kl_divergence_1_to_2'].mean() if 'kl_divergence_1_to_2' in level_data.columns else 0
                    f.write(f"| {level:15s} | {jaccard:7.4f} | {js_sim:6.4f} | {ce:15.4f} | {kl:11.4f} |\n")

                f.write("\n")

            f.write("## Interpretation Guide\n\n")
            f.write("### Similarity Metrics (Higher = More Similar)\n")
            f.write("- **Jaccard, JS-Similarity**: Range [0,1], higher values indicate greater overlap/similarity\n")
            f.write("- **Bhattacharyya, Hellinger Similarity**: Range [0,1], 1 = identical distributions\n")
            f.write("- **Correlations**: Range [-1,1], values near 1 indicate strong positive relationship\n\n")

            f.write("### Divergence Metrics (Lower = More Similar)\n")
            f.write("- **Cross-Entropy, KL Divergence**: Unbounded, lower values indicate more similar distributions\n")
            f.write("- **Hellinger Distance**: Range [0,1], 0 = identical distributions\n\n")

            f.write("### Directional Asymmetry\n")
            f.write("- **H(C,H) vs H(H,C)**: Different because of entropy difference H(C) ≠ H(H)\n")
            f.write("- **D_KL(C||H) vs D_KL(H||C)**: Asymmetry indicates which direction is \"harder\" to model\n")
            f.write("- **Large asymmetry**: Indicates fundamental distributional differences\n\n")

            f.write("## Generated Outputs\n\n")
            f.write("```\n")
            f.write("output/multilevel_similarity/\n")
            f.write("├── [Newspaper]/                        # Per-newspaper analysis\n")
            f.write("│   ├── multilevel_similarity_analysis.json\n")
            f.write("│   ├── multilevel_similarity_summary.csv\n")
            f.write("│   └── combined_similarity_scores.csv\n")
            f.write("│\n")
            f.write("└── GLOBAL_ANALYSIS/                    # Cross-newspaper comparison\n")
            f.write("    ├── aggregated_similarity_metrics.csv\n")
            f.write("    ├── jaccard_similarity_comparison.png\n")
            f.write("    ├── cross_entropy_comparison.png\n")
            f.write("    ├── kl_divergence_comparison.png\n")
            f.write("    ├── js_similarity_comparison.png\n")
            f.write("    ├── similarity_heatmaps.png\n")
            f.write("    ├── directional_asymmetry.png\n")
            f.write("    ├── correlation_similarity.png\n")
            f.write("    └── MULTILEVEL_SIMILARITY_REPORT.md  # This file\n")
            f.write("```\n\n")

            f.write("## References\n\n")
            f.write("See SIMILARITY-METRICS.md for comprehensive theoretical background and references.\n\n")

        self.log(f"✓ Summary report saved: {report_path}", "SUCCESS")

    def run(self):
        """Run complete multi-level similarity analysis pipeline."""
        print("="*80)
        print("MULTI-LEVEL SIMILARITY ANALYSIS")
        print("="*80)
        print("\nMeasuring register similarity at multiple linguistic levels:")
        print("  1. Lexical (surface forms, lemmas)")
        print("  2. Morphological (POS tags, features)")
        print("  3. Syntactic (dependency/constituency)")
        print("  4. Structural (tree alignment)")
        print("\nComprehensive metrics (from SIMILARITY-METRICS.md):")
        print("  - Cross-entropy (both directions)")
        print("  - KL divergence (relative entropy)")
        print("  - Jensen-Shannon divergence")
        print("  - Jaccard, Dice, Overlap coefficients")
        print("  - Bhattacharyya, Hellinger measures")
        print("  - Pearson and Spearman correlations")
        print(f"\nNewspapers: {', '.join(self.newspapers)}")
        print("="*80)
        print()

        # Run analysis for each newspaper
        results = {}
        for newspaper in self.newspapers:
            print(f"\n{'='*80}")
            success = self.run_analysis_for_newspaper(newspaper)
            results[newspaper] = success

        # Summary of per-newspaper analysis
        print(f"\n{'='*80}")
        print("PER-NEWSPAPER ANALYSIS SUMMARY")
        print("="*80)

        successful = sum(1 for s in results.values() if s)
        for newspaper, success in results.items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            print(f"  {newspaper:20s}: {status}")

        print(f"\nTotal: {successful}/{len(self.newspapers)} newspapers completed")

        if successful == 0:
            print("\n⚠️  No analyses completed successfully")
            return False

        # Aggregate and visualize
        print(f"\n{'='*80}")
        print("CROSS-NEWSPAPER ANALYSIS")
        print("="*80)

        df = self.aggregate_results()
        if not df.empty:
            self.create_comparative_visualizations(df)
            self.generate_summary_report(df)

        print(f"\n{'='*80}")
        print("ANALYSIS COMPLETE")
        print("="*80)
        print(f"\n✅ Multi-level similarity analysis completed!")
        print(f"\n📁 Results available at:")
        print(f"  - Per-newspaper: {self.output_dir}/[Newspaper]/")
        print(f"  - Global analysis: {self.global_output}/")
        print(f"\n📊 Generated visualizations:")
        print(f"  - Jaccard similarity comparisons")
        print(f"  - Cross-entropy analysis (bidirectional)")
        print(f"  - KL divergence (with asymmetry)")
        print(f"  - Jensen-Shannon similarity")
        print(f"  - Similarity heatmaps (4 metrics)")
        print(f"  - Directional asymmetry analysis")
        print(f"  - Correlation-based similarity")

        return True


def main():
    runner = MultiLevelSimilarityRunner()
    success = runner.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
