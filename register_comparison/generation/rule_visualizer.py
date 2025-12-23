"""
Rule Visualization Module: Creates plots and tables for rule analysis.

Generates:
1. Coverage vs rule count curves
2. Rule type comparison tables
3. Per-newspaper analysis
4. Cross-newspaper aggregation
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import numpy as np


class RuleVisualizer:
    """
    Creates comprehensive visualizations for rule extraction analysis.

    Generates plots and tables showing:
    - Coverage vs rule count curves
    - Rule type effectiveness
    - Per-newspaper comparisons
    - Global statistics
    """

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10

    def plot_coverage_curve(self,
                           rules_data: Dict[str, Any],
                           total_events: int,
                           output_name: str = "coverage_curve.png"):
        """
        Plot coverage vs rule count curve for different rule types.

        Shows cumulative coverage as we add more rules, separately for:
        - Lexical rules
        - Syntactic rules
        - Combined (lexical + syntactic)
        """

        lexical_rules = rules_data.get('lexical_rules', [])
        syntactic_rules = rules_data.get('syntactic_rules', [])

        # Calculate cumulative coverage for lexical rules
        lex_coverage = []
        cumulative = 0
        for i, rule in enumerate(lexical_rules, 1):
            cumulative += rule['frequency']
            coverage_pct = (cumulative / total_events * 100) if total_events > 0 else 0
            lex_coverage.append((i, coverage_pct))

        # Calculate for syntactic rules
        syn_coverage = []
        cumulative = 0
        for i, rule in enumerate(syntactic_rules, 1):
            cumulative += rule['frequency']
            coverage_pct = (cumulative / total_events * 100) if total_events > 0 else 0
            syn_coverage.append((i, coverage_pct))

        # Calculate combined coverage
        combined_rules = sorted(
            lexical_rules + syntactic_rules,
            key=lambda x: x['frequency'],
            reverse=True
        )
        combined_coverage = []
        cumulative = 0
        for i, rule in enumerate(combined_rules, 1):
            cumulative += rule['frequency']
            coverage_pct = (cumulative / total_events * 100) if total_events > 0 else 0
            combined_coverage.append((i, coverage_pct))

        # Create plot
        fig, ax = plt.subplots(figsize=(12, 7))

        if lex_coverage:
            lex_x, lex_y = zip(*lex_coverage)
            ax.plot(lex_x, lex_y, 'b-', linewidth=2, label='Lexical Rules', marker='o', markersize=4, markevery=max(1, len(lex_x)//20))

        if syn_coverage:
            syn_x, syn_y = zip(*syn_coverage)
            ax.plot(syn_x, syn_y, 'r-', linewidth=2, label='Syntactic Rules', marker='s', markersize=4, markevery=max(1, len(syn_x)//20))

        if combined_coverage:
            comb_x, comb_y = zip(*combined_coverage)
            ax.plot(comb_x, comb_y, 'g-', linewidth=2.5, label='Combined (Lexical + Syntactic)', marker='^', markersize=5, markevery=max(1, len(comb_x)//20))

        # Add reference lines
        ax.axhline(y=70, color='gray', linestyle='--', alpha=0.5, label='70% Coverage Target')
        ax.axhline(y=80, color='gray', linestyle=':', alpha=0.5, label='80% Coverage Target')

        ax.set_xlabel('Number of Rules', fontsize=12, fontweight='bold')
        ax.set_ylabel('Coverage (%)', fontsize=12, fontweight='bold')
        ax.set_title('Rule Coverage Curve: Coverage vs Number of Rules', fontsize=14, fontweight='bold')
        ax.legend(loc='lower right', fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / output_name, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"\n✅ Saved coverage curve to: {self.output_dir / output_name}")

    def plot_accuracy_vs_coverage(self,
                                   rules_data: Dict[str, Any],
                                   total_events: int,
                                   output_name: str = "accuracy_coverage.png"):
        """
        Plot weighted accuracy vs coverage for lexical rules.

        Shows how accuracy changes as we add more rules.
        """

        lexical_rules = rules_data.get('lexical_rules', [])

        if not lexical_rules:
            print("⚠️  No lexical rules to visualize")
            return

        # Calculate cumulative coverage and weighted accuracy
        points = []
        cumulative_freq = 0
        cumulative_weighted_conf = 0

        for i, rule in enumerate(lexical_rules, 1):
            cumulative_freq += rule['frequency']
            cumulative_weighted_conf += rule['confidence'] * rule['frequency']

            coverage_pct = (cumulative_freq / total_events * 100) if total_events > 0 else 0
            avg_conf = (cumulative_weighted_conf / cumulative_freq * 100) if cumulative_freq > 0 else 0

            points.append((i, coverage_pct, avg_conf))

        # Create plot with dual y-axis
        fig, ax1 = plt.subplots(figsize=(12, 7))

        rule_counts, coverages, accuracies = zip(*points)

        # Coverage on left y-axis
        color1 = 'tab:blue'
        ax1.set_xlabel('Number of Lexical Rules', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Coverage (%)', fontsize=12, fontweight='bold', color=color1)
        ax1.plot(rule_counts, coverages, color=color1, linewidth=2, marker='o', markersize=4, markevery=max(1, len(rule_counts)//20))
        ax1.tick_params(axis='y', labelcolor=color1)
        ax1.grid(True, alpha=0.3)

        # Accuracy on right y-axis
        ax2 = ax1.twinx()
        color2 = 'tab:red'
        ax2.set_ylabel('Average Confidence (%)', fontsize=12, fontweight='bold', color=color2)
        ax2.plot(rule_counts, accuracies, color=color2, linewidth=2, marker='s', markersize=4, markevery=max(1, len(rule_counts)//20))
        ax2.tick_params(axis='y', labelcolor=color2)

        plt.title('Lexical Rules: Coverage vs Confidence Trade-off', fontsize=14, fontweight='bold')

        fig.tight_layout()
        plt.savefig(self.output_dir / output_name, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✅ Saved accuracy-coverage plot to: {self.output_dir / output_name}")

    def create_rule_statistics_table(self,
                                     rules_data: Dict[str, Any],
                                     output_name: str = "rule_statistics.csv"):
        """Create comprehensive statistics table for all rule types."""

        stats = rules_data.get('statistics', {})

        # Create summary table
        summary_data = {
            'Rule Type': ['Lexical', 'Syntactic', 'Defaults', 'TOTAL'],
            'Count': [
                stats.get('lexical_count', 0),
                stats.get('syntactic_count', 0),
                stats.get('default_count', 0),
                stats.get('total_rules', 0)
            ],
            'Avg Confidence': [
                f"{stats.get('avg_lexical_confidence', 0):.1%}",
                f"{stats.get('avg_syntactic_confidence', 0):.1%}",
                'N/A',
                'N/A'
            ],
            'Coverage (events)': [
                f"{stats.get('lexical_coverage', 0):,}",
                f"{stats.get('syntactic_coverage', 0):,}",
                'N/A',
                'N/A'
            ],
            'Features Covered': [
                stats.get('features_with_lexical_rules', 0),
                stats.get('features_with_syntactic_rules', 0),
                stats.get('features_with_defaults', 0),
                'N/A'
            ]
        }

        df = pd.DataFrame(summary_data)
        df.to_csv(self.output_dir / output_name, index=False)

        print(f"✅ Saved statistics table to: {self.output_dir / output_name}")

        return df

    def create_top_rules_table(self,
                               rules_data: Dict[str, Any],
                               n: int = 20,
                               output_name: str = "top_rules.csv"):
        """Create table of top N most frequent rules."""

        lexical_rules = rules_data.get('lexical_rules', [])
        syntactic_rules = rules_data.get('syntactic_rules', [])

        # Get top lexical rules
        top_lex = sorted(lexical_rules, key=lambda x: x['frequency'], reverse=True)[:n]

        # Get top syntactic rules
        top_syn = sorted(syntactic_rules, key=lambda x: x['frequency'], reverse=True)[:n]

        # Create combined table
        lex_df = pd.DataFrame(top_lex)
        if not lex_df.empty:
            lex_df['type'] = 'Lexical'
            lex_df['rule_description'] = lex_df.apply(
                lambda r: f"{r['lemma']}({r['pos']}) → {r['transformation']}",
                axis=1
            )

        syn_df = pd.DataFrame(top_syn)
        if not syn_df.empty:
            syn_df['type'] = 'Syntactic'
            syn_df['rule_description'] = syn_df.apply(
                lambda r: f"{r['pos_pattern']} → {r['transformation']}",
                axis=1
            )

        # Combine and save
        combined = pd.concat([lex_df, syn_df], ignore_index=True)

        if not combined.empty:
            output_columns = ['type', 'rule_description', 'frequency', 'confidence', 'feature_id']
            available_columns = [col for col in output_columns if col in combined.columns]
            combined[available_columns].to_csv(self.output_dir / output_name, index=False)

            print(f"✅ Saved top rules table to: {self.output_dir / output_name}")

        return combined

    def plot_rules_by_feature(self,
                              rules_data: Dict[str, Any],
                              output_name: str = "rules_by_feature.png"):
        """Plot number of rules per feature type."""

        lexical_rules = rules_data.get('lexical_rules', [])
        syntactic_rules = rules_data.get('syntactic_rules', [])

        # Count rules per feature
        lex_by_feature = defaultdict(int)
        for rule in lexical_rules:
            lex_by_feature[rule['feature_id']] += 1

        syn_by_feature = defaultdict(int)
        for rule in syntactic_rules:
            syn_by_feature[rule['feature_id']] += 1

        # Get all features
        all_features = sorted(set(list(lex_by_feature.keys()) + list(syn_by_feature.keys())))

        if not all_features:
            print("⚠️  No features to visualize")
            return

        # Prepare data
        lex_counts = [lex_by_feature[f] for f in all_features]
        syn_counts = [syn_by_feature[f] for f in all_features]

        # Create stacked bar plot
        fig, ax = plt.subplots(figsize=(14, 8))

        x = np.arange(len(all_features))
        width = 0.6

        ax.bar(x, lex_counts, width, label='Lexical', color='steelblue')
        ax.bar(x, syn_counts, width, bottom=lex_counts, label='Syntactic', color='coral')

        ax.set_xlabel('Feature', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Rules', fontsize=12, fontweight='bold')
        ax.set_title('Rules Distribution by Feature Type', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(all_features, rotation=45, ha='right', fontsize=9)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / output_name, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✅ Saved rules by feature plot to: {self.output_dir / output_name}")

    def create_coverage_milestones_table(self,
                                         rules_data: Dict[str, Any],
                                         total_events: int,
                                         milestones: List[int] = [10, 50, 100, 200, 500],
                                         output_name: str = "coverage_milestones.csv"):
        """Create table showing coverage at specific rule count milestones."""

        lexical_rules = rules_data.get('lexical_rules', [])

        milestone_data = []
        cumulative = 0
        rule_idx = 0

        for milestone in milestones:
            if rule_idx >= len(lexical_rules):
                break

            # Add rules until we reach milestone
            while rule_idx < len(lexical_rules) and rule_idx < milestone:
                cumulative += lexical_rules[rule_idx]['frequency']
                rule_idx += 1

            coverage_pct = (cumulative / total_events * 100) if total_events > 0 else 0

            # Calculate average confidence for rules up to this point
            avg_conf = sum(r['confidence'] * r['frequency'] for r in lexical_rules[:rule_idx]) / cumulative if cumulative > 0 else 0

            milestone_data.append({
                'Rules': milestone,
                'Events Covered': cumulative,
                'Coverage (%)': f"{coverage_pct:.1f}",
                'Avg Confidence (%)': f"{avg_conf * 100:.1f}"
            })

        df = pd.DataFrame(milestone_data)
        df.to_csv(self.output_dir / output_name, index=False)

        print(f"✅ Saved coverage milestones to: {self.output_dir / output_name}")

        return df

    def generate_all_visualizations(self,
                                    rules_data: Dict[str, Any],
                                    total_events: int):
        """Generate complete set of visualizations."""

        print(f"\n{'='*80}")
        print("GENERATING RULE VISUALIZATIONS")
        print(f"{'='*80}")

        # 1. Coverage curve
        print("\n1. Creating coverage curve...")
        self.plot_coverage_curve(rules_data, total_events)

        # 2. Accuracy vs coverage
        print("2. Creating accuracy-coverage plot...")
        self.plot_accuracy_vs_coverage(rules_data, total_events)

        # 3. Statistics table
        print("3. Creating statistics table...")
        self.create_rule_statistics_table(rules_data)

        # 4. Top rules table
        print("4. Creating top rules table...")
        self.create_top_rules_table(rules_data, n=30)

        # 5. Rules by feature
        print("5. Creating rules by feature plot...")
        self.plot_rules_by_feature(rules_data)

        # 6. Coverage milestones
        print("6. Creating coverage milestones table...")
        self.create_coverage_milestones_table(rules_data, total_events)

        print(f"\n{'='*80}")
        print("VISUALIZATION COMPLETE")
        print(f"{'='*80}")
        print(f"\nAll visualizations saved to: {self.output_dir}")


def visualize_per_newspaper_comparison(newspaper_results: Dict[str, Dict[str, Any]],
                                       output_dir: Path):
    """
    Create cross-newspaper comparison visualizations.

    Args:
        newspaper_results: Dict mapping newspaper name to rules_data dict
        output_dir: Where to save visualizations
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*80}")
    print("CROSS-NEWSPAPER COMPARISON")
    print(f"{'='*80}")

    # Extract statistics for each newspaper
    comparison_data = []

    for newspaper, data in newspaper_results.items():
        stats = data.get('statistics', {})
        comparison_data.append({
            'Newspaper': newspaper,
            'Lexical Rules': stats.get('lexical_count', 0),
            'Syntactic Rules': stats.get('syntactic_count', 0),
            'Total Rules': stats.get('total_rules', 0),
            'Lexical Coverage': stats.get('lexical_coverage', 0),
            'Avg Lexical Conf': f"{stats.get('avg_lexical_confidence', 0):.1%}",
            'Avg Syntactic Conf': f"{stats.get('avg_syntactic_confidence', 0):.1%}"
        })

    # Create comparison table
    df = pd.DataFrame(comparison_data)
    df.to_csv(output_dir / "newspaper_comparison.csv", index=False)
    print(f"\n✅ Saved newspaper comparison to: {output_dir / 'newspaper_comparison.csv'}")

    # Plot rule counts comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    newspapers = df['Newspaper'].tolist()
    lex_counts = df['Lexical Rules'].tolist()
    syn_counts = df['Syntactic Rules'].tolist()

    x = np.arange(len(newspapers))
    width = 0.35

    # Rule counts
    ax1.bar(x - width/2, lex_counts, width, label='Lexical', color='steelblue')
    ax1.bar(x + width/2, syn_counts, width, label='Syntactic', color='coral')
    ax1.set_xlabel('Newspaper', fontweight='bold')
    ax1.set_ylabel('Number of Rules', fontweight='bold')
    ax1.set_title('Rule Counts by Newspaper', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(newspapers, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)

    # Coverage
    coverages = df['Lexical Coverage'].tolist()
    ax2.bar(newspapers, coverages, color='forestgreen')
    ax2.set_xlabel('Newspaper', fontweight='bold')
    ax2.set_ylabel('Events Covered', fontweight='bold')
    ax2.set_title('Lexical Rule Coverage by Newspaper', fontweight='bold')
    ax2.set_xticklabels(newspapers, rotation=45, ha='right')
    ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / "newspaper_comparison.png", dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✅ Saved newspaper comparison plot to: {output_dir / 'newspaper_comparison.png'}")

    print(f"\n{'='*80}")
    print("COMPARISON COMPLETE")
    print(f"{'='*80}")
