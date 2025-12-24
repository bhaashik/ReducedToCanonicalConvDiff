#!/usr/bin/env python3
"""
Comprehensive Multi-Level Complexity Analysis Runner

Runs multi-level complexity analysis across all newspapers and creates
comparative visualizations and reports.

Analyzes:
1. Lexical level (surface forms, lemmas)
2. Morphological level (POS tags, morphological features)
3. Syntactic level (dependency relations, constituency labels)
4. Structural level (tree metrics)

Outputs:
- Per-newspaper detailed analysis
- Cross-newspaper comparative analysis
- Comprehensive visualizations
- Research summary report
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


class MultiLevelAnalysisRunner:
    """Runs multi-level complexity analysis across all newspapers."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.newspapers = ['Times-of-India', 'Hindustan-Times', 'The-Hindu']
        self.output_dir = self.project_root / 'output' / 'multilevel_complexity'
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
        """Run multi-level analysis for a single newspaper."""
        self.log(f"Running multi-level analysis for {newspaper}...", "INFO")

        script_file = self.project_root / 'multilevel_complexity_analyzer.py'

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
        self.log("Aggregating results from all newspapers...", "INFO")

        all_data = []

        for newspaper in self.newspapers:
            csv_path = self.output_dir / newspaper / 'multilevel_complexity_summary.csv'

            if csv_path.exists():
                df = pd.read_csv(csv_path)
                df['newspaper'] = newspaper
                all_data.append(df)
            else:
                self.log(f"Warning: No results found for {newspaper}", "WARNING")

        if not all_data:
            self.log("No data to aggregate", "ERROR")
            return pd.DataFrame()

        combined_df = pd.concat(all_data, ignore_index=True)

        # Save aggregated data
        agg_path = self.global_output / 'aggregated_complexity_metrics.csv'
        combined_df.to_csv(agg_path, index=False)
        self.log(f"✓ Saved aggregated data: {agg_path}", "SUCCESS")

        return combined_df

    def create_comparative_visualizations(self, df: pd.DataFrame):
        """Create comparative visualizations across newspapers."""
        self.log("Creating comparative visualizations...", "INFO")

        if df.empty:
            self.log("No data for visualization", "WARNING")
            return

        # 1. Entropy comparison across levels and sublevels
        self._plot_entropy_comparison(df)

        # 2. TTR comparison (lexical complexity)
        self._plot_ttr_comparison(df)

        # 3. Structural complexity comparison
        self._plot_structural_comparison(df)

        # 4. Cross-newspaper heatmaps
        self._plot_complexity_heatmaps(df)

        # 5. Register complexity ratios
        self._plot_complexity_ratios(df)

        self.log("✓ All visualizations created", "SUCCESS")

    def _plot_entropy_comparison(self, df: pd.DataFrame):
        """Plot entropy comparison across all levels."""
        if 'entropy' not in df.columns:
            return

        entropy_data = df[df['entropy'].notna()].copy()

        if entropy_data.empty:
            return

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Entropy Comparison Across Linguistic Levels', fontsize=16, fontweight='bold')

        levels = ['lexical', 'morphological', 'syntactic']

        # Plot 1: Entropy by level and register
        ax = axes[0, 0]
        level_data = entropy_data[entropy_data['level'].isin(levels)]
        if not level_data.empty:
            sns.barplot(data=level_data, x='level', y='entropy', hue='register', ax=ax)
            ax.set_title('Entropy by Linguistic Level')
            ax.set_xlabel('Linguistic Level')
            ax.set_ylabel('Entropy (bits)')
            ax.legend(title='Register')

        # Plot 2: Entropy by sublevel
        ax = axes[0, 1]
        if not entropy_data.empty:
            sns.barplot(data=entropy_data, x='sublevel', y='entropy', hue='register', ax=ax)
            ax.set_title('Entropy by Sublevel')
            ax.set_xlabel('Sublevel')
            ax.set_ylabel('Entropy (bits)')
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
            ax.legend(title='Register')

        # Plot 3: Entropy by newspaper
        ax = axes[1, 0]
        if not entropy_data.empty:
            sns.boxplot(data=entropy_data, x='newspaper', y='entropy', hue='register', ax=ax)
            ax.set_title('Entropy Distribution by Newspaper')
            ax.set_xlabel('Newspaper')
            ax.set_ylabel('Entropy (bits)')
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
            ax.legend(title='Register')

        # Plot 4: Level-specific comparison
        ax = axes[1, 1]
        if not level_data.empty:
            pivot_data = level_data.pivot_table(
                values='entropy',
                index='level',
                columns='register',
                aggfunc='mean'
            )
            if not pivot_data.empty:
                pivot_data.plot(kind='bar', ax=ax)
                ax.set_title('Average Entropy: Canonical vs Headline')
                ax.set_xlabel('Linguistic Level')
                ax.set_ylabel('Average Entropy (bits)')
                ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
                ax.legend(title='Register')

        plt.tight_layout()
        save_path = self.global_output / 'entropy_comparison.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        self.log(f"  ✓ Saved: {save_path}", "INFO")

    def _plot_ttr_comparison(self, df: pd.DataFrame):
        """Plot Type-Token Ratio comparison."""
        if 'ttr' not in df.columns:
            return

        ttr_data = df[df['ttr'].notna()].copy()

        if ttr_data.empty:
            return

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Type-Token Ratio Comparison (Lexical Diversity)', fontsize=14, fontweight='bold')

        # Plot 1: TTR by sublevel
        ax = axes[0]
        sns.barplot(data=ttr_data, x='sublevel', y='ttr', hue='register', ax=ax)
        ax.set_title('TTR by Sublevel')
        ax.set_xlabel('Sublevel')
        ax.set_ylabel('Type-Token Ratio')
        ax.legend(title='Register')

        # Plot 2: TTR by newspaper
        ax = axes[1]
        sns.boxplot(data=ttr_data, x='newspaper', y='ttr', hue='register', ax=ax)
        ax.set_title('TTR Distribution by Newspaper')
        ax.set_xlabel('Newspaper')
        ax.set_ylabel('Type-Token Ratio')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        ax.legend(title='Register')

        plt.tight_layout()
        save_path = self.global_output / 'ttr_comparison.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        self.log(f"  ✓ Saved: {save_path}", "INFO")

    def _plot_structural_comparison(self, df: pd.DataFrame):
        """Plot structural complexity metrics."""
        structural = df[df['level'] == 'structural'].copy()

        if structural.empty:
            return

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Structural Complexity Comparison', fontsize=14, fontweight='bold')

        # Plot 1: Average tree depth
        ax = axes[0, 0]
        depth_data = structural[structural['avg_depth'].notna()]
        if not depth_data.empty:
            sns.barplot(data=depth_data, x='sublevel', y='avg_depth', hue='register', ax=ax)
            ax.set_title('Average Tree Depth')
            ax.set_xlabel('Tree Type')
            ax.set_ylabel('Average Depth')
            ax.legend(title='Register')

        # Plot 2: Average sentence length
        ax = axes[0, 1]
        length_data = structural[structural['avg_sentence_length'].notna()]
        if not length_data.empty:
            sns.barplot(data=length_data, x='newspaper', y='avg_sentence_length', hue='register', ax=ax)
            ax.set_title('Average Sentence Length')
            ax.set_xlabel('Newspaper')
            ax.set_ylabel('Average Length (tokens)')
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
            ax.legend(title='Register')

        # Plot 3: Average dependency distance
        ax = axes[1, 0]
        dist_data = structural[structural['avg_dependency_distance'].notna()]
        if not dist_data.empty:
            sns.barplot(data=dist_data, x='newspaper', y='avg_dependency_distance', hue='register', ax=ax)
            ax.set_title('Average Dependency Distance')
            ax.set_xlabel('Newspaper')
            ax.set_ylabel('Average Distance')
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
            ax.legend(title='Register')

        # Plot 4: Average branching factor
        ax = axes[1, 1]
        branch_data = structural[structural['avg_branching_factor'].notna()]
        if not branch_data.empty:
            sns.barplot(data=branch_data, x='newspaper', y='avg_branching_factor', hue='register', ax=ax)
            ax.set_title('Average Branching Factor')
            ax.set_xlabel('Newspaper')
            ax.set_ylabel('Average Branching Factor')
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
            ax.legend(title='Register')

        plt.tight_layout()
        save_path = self.global_output / 'structural_comparison.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        self.log(f"  ✓ Saved: {save_path}", "INFO")

    def _plot_complexity_heatmaps(self, df: pd.DataFrame):
        """Create heatmaps of complexity metrics."""
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle('Complexity Heatmaps', fontsize=14, fontweight='bold')

        # Canonical complexity heatmap
        ax = axes[0]
        canonical = df[df['register'] == 'canonical'].copy()
        if not canonical.empty and 'entropy' in canonical.columns:
            pivot = canonical.pivot_table(
                values='entropy',
                index='level',
                columns='newspaper',
                aggfunc='mean'
            )
            if not pivot.empty:
                sns.heatmap(pivot, annot=True, fmt='.3f', cmap='YlOrRd', ax=ax, cbar_kws={'label': 'Entropy'})
                ax.set_title('Canonical Register - Entropy by Level & Newspaper')
                ax.set_xlabel('Newspaper')
                ax.set_ylabel('Linguistic Level')

        # Headline complexity heatmap
        ax = axes[1]
        headline = df[df['register'] == 'headline'].copy()
        if not headline.empty and 'entropy' in headline.columns:
            pivot = headline.pivot_table(
                values='entropy',
                index='level',
                columns='newspaper',
                aggfunc='mean'
            )
            if not pivot.empty:
                sns.heatmap(pivot, annot=True, fmt='.3f', cmap='YlGnBu', ax=ax, cbar_kws={'label': 'Entropy'})
                ax.set_title('Headline Register - Entropy by Level & Newspaper')
                ax.set_xlabel('Newspaper')
                ax.set_ylabel('Linguistic Level')

        plt.tight_layout()
        save_path = self.global_output / 'complexity_heatmaps.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        self.log(f"  ✓ Saved: {save_path}", "INFO")

    def _plot_complexity_ratios(self, df: pd.DataFrame):
        """Plot canonical/headline complexity ratios."""
        # Compute ratios for each metric
        ratios_data = []

        for newspaper in self.newspapers:
            news_data = df[df['newspaper'] == newspaper]

            for level in news_data['level'].unique():
                for sublevel in news_data['sublevel'].unique():
                    subset = news_data[(news_data['level'] == level) & (news_data['sublevel'] == sublevel)]

                    canonical = subset[subset['register'] == 'canonical']
                    headline = subset[subset['register'] == 'headline']

                    if not canonical.empty and not headline.empty:
                        for metric in ['entropy', 'ttr', 'perplexity']:
                            if metric in subset.columns:
                                c_val = canonical[metric].values[0] if len(canonical) > 0 else 0
                                h_val = headline[metric].values[0] if len(headline) > 0 else 0

                                if h_val > 0:
                                    ratio = c_val / h_val
                                    ratios_data.append({
                                        'newspaper': newspaper,
                                        'level': level,
                                        'sublevel': sublevel,
                                        'metric': metric,
                                        'ratio': ratio
                                    })

        if not ratios_data:
            return

        ratios_df = pd.DataFrame(ratios_data)

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Canonical/Headline Complexity Ratios (>1 = Canonical more complex)',
                     fontsize=14, fontweight='bold')

        # Plot 1: Ratio by level
        ax = axes[0]
        sns.boxplot(data=ratios_df, x='level', y='ratio', ax=ax)
        ax.axhline(y=1.0, color='red', linestyle='--', label='Equal complexity')
        ax.set_title('Complexity Ratio by Linguistic Level')
        ax.set_xlabel('Linguistic Level')
        ax.set_ylabel('Canonical/Headline Ratio')
        ax.legend()

        # Plot 2: Ratio by metric
        ax = axes[1]
        sns.boxplot(data=ratios_df, x='metric', y='ratio', ax=ax)
        ax.axhline(y=1.0, color='red', linestyle='--', label='Equal complexity')
        ax.set_title('Complexity Ratio by Metric Type')
        ax.set_xlabel('Metric')
        ax.set_ylabel('Canonical/Headline Ratio')
        ax.legend()

        plt.tight_layout()
        save_path = self.global_output / 'complexity_ratios.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        self.log(f"  ✓ Saved: {save_path}", "INFO")

        # Save ratios to CSV
        ratios_path = self.global_output / 'complexity_ratios.csv'
        ratios_df.to_csv(ratios_path, index=False)
        self.log(f"  ✓ Saved: {ratios_path}", "INFO")

    def generate_summary_report(self, df: pd.DataFrame):
        """Generate comprehensive summary report."""
        self.log("Generating summary report...", "INFO")

        report_path = self.global_output / 'MULTILEVEL_ANALYSIS_REPORT.md'

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Multi-Level Complexity Analysis - Summary Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Newspapers**: {', '.join(self.newspapers)}\n\n")

            f.write("## Research Framework\n\n")
            f.write("This analysis examines register complexity and similarity across multiple linguistic levels:\n\n")
            f.write("1. **Lexical Level**: Surface forms and lemmas\n")
            f.write("2. **Morphological Level**: POS tags and morphological features\n")
            f.write("3. **Syntactic Level**: Dependency relations and constituency labels\n")
            f.write("4. **Structural Level**: Tree-based metrics (depth, branching, distances)\n\n")

            f.write("## Key Metrics\n\n")
            f.write("For each level, we compute:\n")
            f.write("- **Entropy**: Unpredictability/diversity of linguistic units\n")
            f.write("- **Type-Token Ratio (TTR)**: Lexical diversity\n")
            f.write("- **Perplexity**: Information-theoretic complexity\n")
            f.write("- **Divergence**: Cross-register differences (KL, JS divergence)\n")
            f.write("- **Structural metrics**: Tree depth, dependency distance, branching factor\n\n")

            if not df.empty:
                f.write("## Summary Statistics\n\n")

                # Overall statistics
                canonical_entropy = df[df['register'] == 'canonical']['entropy'].mean()
                headline_entropy = df[df['register'] == 'headline']['entropy'].mean()

                f.write(f"- **Average Canonical Entropy**: {canonical_entropy:.4f} bits\n")
                f.write(f"- **Average Headline Entropy**: {headline_entropy:.4f} bits\n")
                f.write(f"- **Entropy Ratio (C/H)**: {canonical_entropy/headline_entropy:.4f}\n\n")

                # Per-level summary
                f.write("### Entropy by Linguistic Level\n\n")
                f.write("| Level | Canonical | Headline | Ratio (C/H) |\n")
                f.write("|-------|-----------|----------|-------------|\n")

                for level in df['level'].unique():
                    level_data = df[df['level'] == level]
                    c_ent = level_data[level_data['register'] == 'canonical']['entropy'].mean()
                    h_ent = level_data[level_data['register'] == 'headline']['entropy'].mean()
                    ratio = c_ent / h_ent if h_ent > 0 else 0
                    f.write(f"| {level:15s} | {c_ent:9.4f} | {h_ent:8.4f} | {ratio:11.4f} |\n")

                f.write("\n")

            f.write("## Interpretation\n\n")
            f.write("- **Entropy** measures the unpredictability/diversity of linguistic choices\n")
            f.write("- **Higher entropy** = more diverse, less predictable, potentially more complex\n")
            f.write("- **Ratio > 1** indicates canonical register is more complex at that level\n")
            f.write("- **Ratio < 1** indicates headline register is more complex at that level\n\n")

            f.write("## Generated Outputs\n\n")
            f.write("```\n")
            f.write("output/multilevel_complexity/\n")
            f.write("├── [Newspaper]/                    # Per-newspaper detailed analysis\n")
            f.write("│   ├── multilevel_complexity_analysis.json\n")
            f.write("│   ├── multilevel_complexity_summary.csv\n")
            f.write("│   └── combined_complexity_scores.csv\n")
            f.write("│\n")
            f.write("└── GLOBAL_ANALYSIS/                # Cross-newspaper comparison\n")
            f.write("    ├── aggregated_complexity_metrics.csv\n")
            f.write("    ├── complexity_ratios.csv\n")
            f.write("    ├── entropy_comparison.png\n")
            f.write("    ├── ttr_comparison.png\n")
            f.write("    ├── structural_comparison.png\n")
            f.write("    ├── complexity_heatmaps.png\n")
            f.write("    ├── complexity_ratios.png\n")
            f.write("    └── MULTILEVEL_ANALYSIS_REPORT.md  # This file\n")
            f.write("```\n\n")

            f.write("## Future Directions\n\n")
            f.write("- Semantic-level complexity analysis\n")
            f.write("- Pragmatic complexity (discourse markers, cohesion)\n")
            f.write("- Cross-linguistic comparison\n")
            f.write("- Integration with transformation studies (Task 2)\n")
            f.write("- Correlation with transformation difficulty\n\n")

        self.log(f"✓ Summary report saved: {report_path}", "SUCCESS")

    def run(self):
        """Run complete multi-level analysis pipeline."""
        print("="*80)
        print("MULTI-LEVEL COMPLEXITY ANALYSIS")
        print("="*80)
        print("\nAnalyzing complexity at multiple linguistic levels:")
        print("  1. Lexical (surface forms, lemmas)")
        print("  2. Morphological (POS tags, features)")
        print("  3. Syntactic (dependency/constituency)")
        print("  4. Structural (tree metrics)")
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
        print(f"\n✅ Multi-level complexity analysis completed!")
        print(f"\n📁 Results available at:")
        print(f"  - Per-newspaper: {self.output_dir}/[Newspaper]/")
        print(f"  - Global analysis: {self.global_output}/")
        print(f"\n📊 Generated visualizations:")
        print(f"  - Entropy comparisons")
        print(f"  - TTR (lexical diversity)")
        print(f"  - Structural complexity")
        print(f"  - Complexity heatmaps")
        print(f"  - Canonical/Headline ratios")

        return True


def main():
    runner = MultiLevelAnalysisRunner()
    success = runner.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
