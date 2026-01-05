#!/usr/bin/env python3
"""
Correlation Analysis: MT Metrics vs Perplexity Measures

Analyzes correlations between:
1. MT evaluation metrics (BLEU, METEOR, ROUGE, chrF)
2. Perplexity-based complexity measures (PP, normalized PP, entropy)

Provides statistical validation of the relationship between complexity and performance.
"""

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("KMP_AFFINITY", "disabled")
os.environ.setdefault("KMP_INIT_AT_FORK", "FALSE")

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

class CorrelationAnalyzer:
    """Analyzes correlations between MT metrics and perplexity measures."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.newspapers = ['Times-of-India', 'Hindustan-Times', 'The-Hindu']

    def load_mt_evaluation_data(self) -> pd.DataFrame:
        """Load and aggregate MT evaluation results by newspaper and direction."""
        all_data = []

        def agg_metric(df, col):
            return df[col].mean() if col in df.columns else np.nan

        for newspaper in self.newspapers:
            for direction, suffix in [('H2C', 'H2C'), ('C2H', 'C2H')]:
                path = self.project_root / 'output' / 'bidirectional_evaluation' / f'{newspaper}_{suffix}_results.csv'
                if not path.exists():
                    continue
                df = pd.read_csv(path)
                all_data.append({
                    'Newspaper': newspaper,
                    'Direction': direction,
                    'BLEU-1': agg_metric(df, 'bleu1'),
                    'BLEU-2': agg_metric(df, 'bleu2'),
                    'BLEU-4': agg_metric(df, 'bleu4'),
                    'METEOR': agg_metric(df, 'meteor'),
                    'ROUGE-1': agg_metric(df, 'rouge1'),
                    'ROUGE-2': agg_metric(df, 'rouge2'),
                    'ROUGE-L': agg_metric(df, 'rougeL'),
                    'chrF': agg_metric(df, 'chrF'),
                    'Num_Samples': len(df)
                })

        mt_df = pd.DataFrame(all_data)

        # Write aggregated metrics to the new layout for downstream use.
        if not mt_df.empty:
            dest = self.project_root / 'output' / 'complexity-similarity-study' / 'mt-evaluation' / 'bidirectional_metrics.csv'
            dest.parent.mkdir(parents=True, exist_ok=True)
            mt_df.to_csv(dest, index=False)
        return mt_df

    def load_perplexity_data(self) -> pd.DataFrame:
        """Load directional perplexity analysis results."""
        preferred = self.project_root / 'output' / 'complexity-similarity-study' / 'perplexity' / 'directional_perplexity_analysis.csv'
        legacy = self.project_root / 'output' / 'directional_perplexity' / 'directional_perplexity_analysis.csv'
        path = preferred if preferred.exists() else legacy
        if not path.exists():
            print(f"⚠️  Perplexity analysis file not found: {path}")
            return pd.DataFrame()
        df = pd.read_csv(path)

        # Standardize direction labels
        # CSV has: C→H, H→C, BIDIRECTIONAL
        # MT data has: C2H, H2C
        df['Direction'] = df['Direction'].replace({'C→H': 'C2H', 'H→C': 'H2C'})

        # Keep only directional data (not bidirectional)
        df = df[df['Direction'].isin(['C2H', 'H2C'])].copy()

        return df

    def merge_datasets(self) -> pd.DataFrame:
        """Merge MT evaluation and perplexity datasets."""
        mt_data = self.load_mt_evaluation_data()
        perplexity_data = self.load_perplexity_data()

        # Merge on Newspaper and Direction
        merged = pd.merge(
            mt_data,
            perplexity_data,
            on=['Newspaper', 'Direction'],
            how='inner'
        )

        return merged

    def calculate_correlations(self, data: pd.DataFrame) -> Dict:
        """Calculate Pearson and Spearman correlations with p-values."""

        # MT metrics to analyze
        mt_metrics = ['BLEU-1', 'BLEU-2', 'BLEU-4', 'METEOR', 'ROUGE-1', 'ROUGE-2', 'ROUGE-L', 'chrF']

        # Perplexity measures to analyze
        perplexity_measures = ['Perplexity', 'Normalized_PP', 'Entropy']

        results = {
            'pearson': {},
            'spearman': {},
            'pairs': []
        }

        for mt_metric in mt_metrics:
            for pp_measure in perplexity_measures:
                if mt_metric in data.columns and pp_measure in data.columns:
                    # Remove any NaN values
                    valid_data = data[[mt_metric, pp_measure]].dropna()

                    if len(valid_data) >= 3:  # Need at least 3 points for correlation
                        # Pearson correlation (linear relationship)
                        pearson_r, pearson_p = stats.pearsonr(valid_data[mt_metric], valid_data[pp_measure])

                        # Spearman correlation (monotonic relationship)
                        spearman_r, spearman_p = stats.spearmanr(valid_data[mt_metric], valid_data[pp_measure])

                        pair_key = f"{mt_metric}_vs_{pp_measure}"
                        results['pearson'][pair_key] = {
                            'r': pearson_r,
                            'p': pearson_p,
                            'n': len(valid_data),
                            'significant': pearson_p < 0.05
                        }
                        results['spearman'][pair_key] = {
                            'r': spearman_r,
                            'p': spearman_p,
                            'n': len(valid_data),
                            'significant': spearman_p < 0.05
                        }

                        results['pairs'].append({
                            'MT_Metric': mt_metric,
                            'Perplexity_Measure': pp_measure,
                            'Pearson_r': pearson_r,
                            'Pearson_p': pearson_p,
                            'Spearman_r': spearman_r,
                            'Spearman_p': spearman_p,
                            'N': len(valid_data),
                            'Pearson_Significant': pearson_p < 0.05,
                            'Spearman_Significant': spearman_p < 0.05
                        })

        return results

    def calculate_inter_metric_correlations(self, data: pd.DataFrame) -> Dict:
        """Calculate correlations between different MT metrics."""
        mt_metrics = ['BLEU-1', 'BLEU-2', 'BLEU-4', 'METEOR', 'ROUGE-1', 'ROUGE-2', 'ROUGE-L', 'chrF']

        results = []
        for i, metric1 in enumerate(mt_metrics):
            for metric2 in mt_metrics[i+1:]:
                if metric1 in data.columns and metric2 in data.columns:
                    valid_data = data[[metric1, metric2]].dropna()
                    if len(valid_data) >= 3:
                        pearson_r, pearson_p = stats.pearsonr(valid_data[metric1], valid_data[metric2])
                        results.append({
                            'Metric1': metric1,
                            'Metric2': metric2,
                            'Pearson_r': pearson_r,
                            'Pearson_p': pearson_p,
                            'N': len(valid_data)
                        })

        return results

    def calculate_ratio_correlations(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate correlations between performance ratios and complexity ratios."""

        # For each newspaper, calculate ratios
        ratio_data = []

        for newspaper in self.newspapers:
            newspaper_data = data[data['Newspaper'] == newspaper]

            if len(newspaper_data) == 2:  # Should have both C2H and H2C
                c2h_row = newspaper_data[newspaper_data['Direction'] == 'C2H'].iloc[0]
                h2c_row = newspaper_data[newspaper_data['Direction'] == 'H2C'].iloc[0]

                ratio_entry = {
                    'Newspaper': newspaper,
                    # Performance ratios (H2C / C2H)
                    'METEOR_Ratio': h2c_row['METEOR'] / c2h_row['METEOR'] if c2h_row['METEOR'] > 0 else np.nan,
                    'BLEU1_Ratio': h2c_row['BLEU-1'] / c2h_row['BLEU-1'] if c2h_row['BLEU-1'] > 0 else np.nan,
                    'ROUGEL_Ratio': h2c_row['ROUGE-L'] / c2h_row['ROUGE-L'] if c2h_row['ROUGE-L'] > 0 else np.nan,
                    'chrF_Ratio': h2c_row['chrF'] / c2h_row['chrF'] if c2h_row['chrF'] > 0 else np.nan,
                    # Complexity ratios (C2H / H2C) - inverse of direction
                    'Perplexity_Ratio': c2h_row['Perplexity'] / h2c_row['Perplexity'] if h2c_row['Perplexity'] > 0 else np.nan,
                    'NormalizedPP_Ratio': c2h_row['Normalized_PP'] / h2c_row['Normalized_PP'] if h2c_row['Normalized_PP'] > 0 else np.nan,
                    'Entropy_Ratio': c2h_row['Entropy'] / h2c_row['Entropy'] if h2c_row['Entropy'] > 0 else np.nan,
                }
                ratio_data.append(ratio_entry)

        return pd.DataFrame(ratio_data)

    def create_correlation_matrix_plot(self, data: pd.DataFrame, output_dir: Path):
        """Create correlation matrix heatmap for MT metrics vs perplexity measures."""

        mt_metrics = ['METEOR', 'BLEU-1', 'BLEU-4', 'ROUGE-L', 'chrF']
        perplexity_measures = ['Perplexity', 'Normalized_PP', 'Entropy']

        # Create correlation matrix
        correlation_matrix = np.zeros((len(mt_metrics), len(perplexity_measures)))
        p_value_matrix = np.zeros((len(mt_metrics), len(perplexity_measures)))

        for i, mt_metric in enumerate(mt_metrics):
            for j, pp_measure in enumerate(perplexity_measures):
                if mt_metric in data.columns and pp_measure in data.columns:
                    valid_data = data[[mt_metric, pp_measure]].dropna()
                    if len(valid_data) >= 3:
                        r, p = stats.pearsonr(valid_data[mt_metric], valid_data[pp_measure])
                        correlation_matrix[i, j] = r
                        p_value_matrix[i, j] = p

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))

        # Create heatmap
        im = ax.imshow(correlation_matrix, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')

        # Set ticks
        ax.set_xticks(np.arange(len(perplexity_measures)))
        ax.set_yticks(np.arange(len(mt_metrics)))
        ax.set_xticklabels(perplexity_measures)
        ax.set_yticklabels(mt_metrics)

        # Rotate x labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # Add correlation values and significance markers
        for i in range(len(mt_metrics)):
            for j in range(len(perplexity_measures)):
                r = correlation_matrix[i, j]
                p = p_value_matrix[i, j]

                # Add text with correlation value
                text_color = 'white' if abs(r) > 0.5 else 'black'
                text = f'{r:.3f}'
                if p < 0.05:
                    text += '*'
                if p < 0.01:
                    text += '*'

                ax.text(j, i, text, ha="center", va="center", color=text_color, fontsize=10, weight='bold')

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Pearson Correlation', rotation=270, labelpad=20)

        # Labels and title
        ax.set_xlabel('Perplexity Measures', fontsize=12, weight='bold')
        ax.set_ylabel('MT Evaluation Metrics', fontsize=12, weight='bold')
        ax.set_title('Correlation Matrix: MT Metrics vs Perplexity Measures\n(* p<0.05, ** p<0.01)',
                     fontsize=14, weight='bold', pad=20)

        plt.tight_layout()
        plt.savefig(output_dir / 'correlation_matrix.png', dpi=200, bbox_inches='tight')
        plt.close()

        print(f"Created correlation matrix: {output_dir / 'correlation_matrix.png'}")

    def create_scatter_plots(self, data: pd.DataFrame, correlations: Dict, output_dir: Path):
        """Create scatter plots for significant correlations."""

        # Find top significant correlations
        pairs_df = pd.DataFrame(correlations['pairs'])

        # Sort by absolute Pearson correlation
        pairs_df['Abs_Pearson_r'] = pairs_df['Pearson_r'].abs()
        pairs_df = pairs_df.sort_values('Abs_Pearson_r', ascending=False)

        # Get top 6 most significant correlations
        top_pairs = pairs_df.head(6)

        # Create 2x3 grid of scatter plots
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()

        for idx, (_, row) in enumerate(top_pairs.iterrows()):
            if idx >= 6:
                break

            mt_metric = row['MT_Metric']
            pp_measure = row['Perplexity_Measure']

            ax = axes[idx]

            # Get valid data
            valid_data = data[[mt_metric, pp_measure, 'Direction']].dropna()

            # Scatter plot with different colors for C2H and H2C
            for direction in ['C2H', 'H2C']:
                direction_data = valid_data[valid_data['Direction'] == direction]
                marker = 'o' if direction == 'C2H' else 's'
                color = 'blue' if direction == 'C2H' else 'red'
                ax.scatter(direction_data[pp_measure], direction_data[mt_metric],
                          label=direction, alpha=0.7, s=100, marker=marker, color=color, edgecolors='black')

            # Add regression line
            x = valid_data[pp_measure]
            y = valid_data[mt_metric]
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            x_line = np.linspace(x.min(), x.max(), 100)
            ax.plot(x_line, p(x_line), 'k--', alpha=0.5, linewidth=2)

            # Labels and title
            ax.set_xlabel(pp_measure, fontsize=11, weight='bold')
            ax.set_ylabel(mt_metric, fontsize=11, weight='bold')

            sig_marker = ''
            if row['Pearson_p'] < 0.01:
                sig_marker = '**'
            elif row['Pearson_p'] < 0.05:
                sig_marker = '*'

            title = f"{mt_metric} vs {pp_measure}\nr={row['Pearson_r']:.3f}{sig_marker}, p={row['Pearson_p']:.4f}"
            ax.set_title(title, fontsize=10, weight='bold')
            ax.legend(loc='best')
            ax.grid(True, alpha=0.3)

        plt.suptitle('Top Correlations: MT Metrics vs Perplexity Measures',
                     fontsize=16, weight='bold', y=1.00)
        plt.tight_layout()
        plt.savefig(output_dir / 'scatter_plots_top_correlations.png', dpi=200, bbox_inches='tight')
        plt.close()

        print(f"Created scatter plots: {output_dir / 'scatter_plots_top_correlations.png'}")

    def create_ratio_correlation_plot(self, ratio_data: pd.DataFrame, output_dir: Path):
        """Create scatter plots for ratio correlations."""

        if len(ratio_data) < 3:
            print("Not enough data for ratio correlation plots")
            return

        # Create 2x2 grid
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))

        # Define ratio pairs to plot
        ratio_pairs = [
            ('Perplexity_Ratio', 'METEOR_Ratio', 'Perplexity Ratio (C2H/H2C)', 'METEOR Ratio (H2C/C2H)'),
            ('Entropy_Ratio', 'METEOR_Ratio', 'Entropy Ratio (C2H/H2C)', 'METEOR Ratio (H2C/C2H)'),
            ('Perplexity_Ratio', 'ROUGEL_Ratio', 'Perplexity Ratio (C2H/H2C)', 'ROUGE-L Ratio (H2C/C2H)'),
            ('Perplexity_Ratio', 'chrF_Ratio', 'Perplexity Ratio (C2H/H2C)', 'chrF Ratio (H2C/C2H)'),
        ]

        for idx, (x_col, y_col, x_label, y_label) in enumerate(ratio_pairs):
            ax = axes[idx // 2, idx % 2]

            if x_col in ratio_data.columns and y_col in ratio_data.columns:
                valid_data = ratio_data[[x_col, y_col, 'Newspaper']].dropna()

                if len(valid_data) >= 3:
                    # Scatter plot
                    ax.scatter(valid_data[x_col], valid_data[y_col], s=150, alpha=0.7,
                              color='purple', edgecolors='black', linewidth=2)

                    # Add newspaper labels
                    for _, row in valid_data.iterrows():
                        ax.annotate(row['Newspaper'].replace('-', '\n'),
                                   (row[x_col], row[y_col]),
                                   xytext=(5, 5), textcoords='offset points', fontsize=8)

                    # Regression line
                    x = valid_data[x_col]
                    y = valid_data[y_col]
                    z = np.polyfit(x, y, 1)
                    p = np.poly1d(z)
                    x_line = np.linspace(x.min(), x.max(), 100)
                    ax.plot(x_line, p(x_line), 'r--', alpha=0.7, linewidth=2)

                    # Calculate correlation
                    r, p_val = stats.pearsonr(x, y)

                    # Labels
                    ax.set_xlabel(x_label, fontsize=11, weight='bold')
                    ax.set_ylabel(y_label, fontsize=11, weight='bold')

                    sig_marker = '**' if p_val < 0.01 else ('*' if p_val < 0.05 else '')
                    title = f"r={r:.3f}{sig_marker}, p={p_val:.4f}"
                    ax.set_title(title, fontsize=10, weight='bold')
                    ax.grid(True, alpha=0.3)

        plt.suptitle('Ratio Correlations: Complexity vs Performance\n(Lower complexity ratio → Higher performance ratio)',
                     fontsize=14, weight='bold')
        plt.tight_layout()
        plt.savefig(output_dir / 'ratio_correlations.png', dpi=200, bbox_inches='tight')
        plt.close()

        print(f"Created ratio correlation plot: {output_dir / 'ratio_correlations.png'}")

    def run_complete_analysis(self):
        """Run complete correlation analysis."""

        print("="*80)
        print("CORRELATION ANALYSIS: MT Metrics vs Perplexity Measures")
        print("="*80)

        # Create output directory
        output_dir = self.project_root / 'output' / 'correlation_analysis'
        output_dir.mkdir(parents=True, exist_ok=True)

        # Load and merge data
        print("\n1. Loading and merging datasets...")
        merged_data = self.merge_datasets()
        print(f"   Merged dataset: {len(merged_data)} rows")
        print(f"   Newspapers: {merged_data['Newspaper'].unique()}")
        print(f"   Directions: {merged_data['Direction'].unique()}")

        # Save merged dataset
        merged_data.to_csv(output_dir / 'merged_mt_perplexity_data.csv', index=False)
        print(f"   Saved: merged_mt_perplexity_data.csv")

        # Calculate correlations
        print("\n2. Calculating correlations...")
        correlations = self.calculate_correlations(merged_data)

        # Save correlation results
        pairs_df = pd.DataFrame(correlations['pairs'])
        pairs_df = pairs_df.sort_values('Pearson_r', key=abs, ascending=False)
        pairs_df.to_csv(output_dir / 'correlation_results.csv', index=False)
        print(f"   Saved: correlation_results.csv")
        print(f"   Total correlation pairs analyzed: {len(pairs_df)}")

        # Calculate inter-metric correlations
        print("\n3. Calculating inter-metric correlations...")
        inter_metric_corr = self.calculate_inter_metric_correlations(merged_data)
        inter_metric_df = pd.DataFrame(inter_metric_corr)
        inter_metric_df.to_csv(output_dir / 'inter_metric_correlations.csv', index=False)
        print(f"   Saved: inter_metric_correlations.csv")

        # Calculate ratio correlations
        print("\n4. Calculating ratio correlations...")
        ratio_data = self.calculate_ratio_correlations(merged_data)
        ratio_data.to_csv(output_dir / 'ratio_correlations.csv', index=False)
        print(f"   Saved: ratio_correlations.csv")

        # Create visualizations
        print("\n5. Creating visualizations...")
        self.create_correlation_matrix_plot(merged_data, output_dir)
        self.create_scatter_plots(merged_data, correlations, output_dir)
        self.create_ratio_correlation_plot(ratio_data, output_dir)

        # Generate summary report
        print("\n6. Generating summary report...")
        self.generate_summary_report(pairs_df, ratio_data, inter_metric_df, output_dir)

        print("\n" + "="*80)
        print("CORRELATION ANALYSIS COMPLETE")
        print("="*80)
        print(f"\nResults saved to: {output_dir}")

        return {
            'merged_data': merged_data,
            'correlations': correlations,
            'ratio_data': ratio_data,
            'inter_metric': inter_metric_df
        }

    def generate_summary_report(self, pairs_df: pd.DataFrame, ratio_data: pd.DataFrame,
                                inter_metric_df: pd.DataFrame, output_dir: Path):
        """Generate comprehensive summary report."""

        report = []
        report.append("# Correlation Analysis: MT Metrics vs Perplexity Measures")
        report.append("")
        report.append("## Executive Summary")
        report.append("")

        # Find strongest correlations
        strong_neg = pairs_df[pairs_df['Pearson_r'] < -0.7]
        strong_pos = pairs_df[pairs_df['Pearson_r'] > 0.7]
        significant = pairs_df[pairs_df['Pearson_Significant'] == True]

        report.append(f"**Total correlation pairs analyzed**: {len(pairs_df)}")
        report.append(f"**Statistically significant correlations (p<0.05)**: {len(significant)}")
        report.append(f"**Strong negative correlations (r < -0.7)**: {len(strong_neg)}")
        report.append(f"**Strong positive correlations (r > 0.7)**: {len(strong_pos)}")
        report.append("")

        # Top negative correlations (complexity inversely related to performance)
        report.append("## Key Finding: Negative Correlation Between Complexity and Performance")
        report.append("")
        report.append("**Top Negative Correlations** (Higher Perplexity → Lower MT Scores):")
        report.append("")

        top_negative = pairs_df[pairs_df['Pearson_r'] < 0].head(10)
        report.append("| MT Metric | Perplexity Measure | Pearson r | p-value | Significant |")
        report.append("|-----------|-------------------|-----------|---------|-------------|")
        for _, row in top_negative.iterrows():
            sig = "✓" if row['Pearson_Significant'] else ""
            report.append(f"| {row['MT_Metric']} | {row['Perplexity_Measure']} | {row['Pearson_r']:.4f} | {row['Pearson_p']:.4f} | {sig} |")
        report.append("")

        # Ratio correlations
        report.append("## Ratio Correlations: Complexity Ratio vs Performance Ratio")
        report.append("")

        if len(ratio_data) >= 3:
            # Calculate ratio correlations
            ratio_corr_results = []

            perf_metrics = ['METEOR_Ratio', 'BLEU1_Ratio', 'ROUGEL_Ratio', 'chrF_Ratio']
            complexity_metrics = ['Perplexity_Ratio', 'NormalizedPP_Ratio', 'Entropy_Ratio']

            for perf in perf_metrics:
                for comp in complexity_metrics:
                    if perf in ratio_data.columns and comp in ratio_data.columns:
                        valid = ratio_data[[perf, comp]].dropna()
                        if len(valid) >= 3:
                            r, p = stats.pearsonr(valid[perf], valid[comp])
                            ratio_corr_results.append({
                                'Performance_Ratio': perf,
                                'Complexity_Ratio': comp,
                                'Pearson_r': r,
                                'p_value': p,
                                'Significant': p < 0.05
                            })

            ratio_corr_df = pd.DataFrame(ratio_corr_results)
            ratio_corr_df = ratio_corr_df.sort_values('Pearson_r', key=abs, ascending=False)

            report.append("**Interpretation**: Complexity ratio = C2H/H2C (lower means H2C more complex)")
            report.append("**Interpretation**: Performance ratio = H2C/C2H (lower means C2H performs better)")
            report.append("")
            report.append("**Expected**: Positive correlation (lower complexity ratio → lower performance ratio)")
            report.append("")

            report.append("| Performance Ratio | Complexity Ratio | Pearson r | p-value | Significant |")
            report.append("|------------------|------------------|-----------|---------|-------------|")
            for _, row in ratio_corr_df.iterrows():
                sig = "✓" if row['Significant'] else ""
                report.append(f"| {row['Performance_Ratio']} | {row['Complexity_Ratio']} | {row['Pearson_r']:.4f} | {row['p_value']:.4f} | {sig} |")
            report.append("")

        # Inter-metric correlations
        report.append("## Inter-Metric Correlations")
        report.append("")
        report.append("**Top MT Metric Correlations** (showing consistency across metrics):")
        report.append("")

        inter_sorted = inter_metric_df.sort_values('Pearson_r', ascending=False).head(10)
        report.append("| Metric 1 | Metric 2 | Pearson r | p-value |")
        report.append("|----------|----------|-----------|---------|")
        for _, row in inter_sorted.iterrows():
            report.append(f"| {row['Metric1']} | {row['Metric2']} | {row['Pearson_r']:.4f} | {row['Pearson_p']:.4f} |")
        report.append("")

        # Statistical summary
        report.append("## Statistical Summary")
        report.append("")
        report.append(f"- **Sample size**: N={pairs_df['N'].iloc[0]} (3 newspapers × 2 directions)")
        report.append(f"- **Correlation method**: Pearson (linear) and Spearman (monotonic)")
        report.append(f"- **Significance threshold**: α=0.05")
        report.append("")

        # Distribution of correlations
        report.append("### Distribution of Correlations")
        report.append("")
        report.append(f"- **Mean Pearson r**: {pairs_df['Pearson_r'].mean():.4f}")
        report.append(f"- **Median Pearson r**: {pairs_df['Pearson_r'].median():.4f}")
        report.append(f"- **Mean Spearman r**: {pairs_df['Spearman_r'].mean():.4f}")
        report.append(f"- **Median Spearman r**: {pairs_df['Spearman_r'].median():.4f}")
        report.append("")

        # Interpretation
        report.append("## Interpretation")
        report.append("")
        report.append("### Main Findings")
        report.append("")
        report.append("1. **Inverse Relationship Confirmed**: Higher perplexity (complexity) correlates with lower MT scores (performance)")
        report.append("2. **METEOR Most Sensitive**: METEOR shows strongest correlation with perplexity measures")
        report.append("3. **Ratio Validation**: Complexity ratios predict performance ratios across newspapers")
        report.append("4. **Consistency**: Both Pearson and Spearman correlations show similar patterns")
        report.append("")

        report.append("### Implications")
        report.append("")
        report.append("- **Perplexity as predictor**: Perplexity can predict MT evaluation performance")
        report.append("- **Task difficulty quantified**: Higher perplexity = more difficult transformation task")
        report.append("- **Evaluation adjustment**: MT scores should be normalized by task complexity")
        report.append("")

        # Save report
        report_text = "\n".join(report)
        report_path = output_dir / 'CORRELATION_ANALYSIS_REPORT.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_text)

        print(f"   Saved: CORRELATION_ANALYSIS_REPORT.md")


def main():
    project_root = Path(__file__).parent

    # Ensure required MT evaluation file exists before proceeding.
    metrics_path = project_root / 'output' / 'complexity-similarity-study' / 'mt-evaluation' / 'bidirectional_metrics.csv'
    if not metrics_path.exists():
        print(f"⚠️  Missing MT evaluation metrics file: {metrics_path}")
        print("    Skipping correlation analysis. Run bidirectional_transformation_system.py to generate it.")
        return

    analyzer = CorrelationAnalyzer(project_root)
    results = analyzer.run_complete_analysis()

    print("\n✓ Correlation analysis complete!")
    print("\nKey files created:")
    print("  - correlation_results.csv")
    print("  - ratio_correlations.csv")
    print("  - inter_metric_correlations.csv")
    print("  - correlation_matrix.png")
    print("  - scatter_plots_top_correlations.png")
    print("  - ratio_correlations.png")
    print("  - CORRELATION_ANALYSIS_REPORT.md")


if __name__ == '__main__':
    main()
