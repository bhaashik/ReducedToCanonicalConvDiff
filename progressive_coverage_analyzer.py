"""
Progressive Coverage Analyzer: Analyze trade-off between rule count and coverage.

This module:
1. Extracts ALL possible rules at different confidence/frequency thresholds
2. Analyzes progressive coverage as rules are added
3. Computes F-score to find optimal rule set size
4. Creates visualizations and tables showing the trade-off
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import sys
import os

sys.path.append(os.path.dirname(__file__))

from register_comparison.generation.rule_extractor import RuleExtractor
from register_comparison.generation.morphological_rules import MorphologicalRuleExtractor


class ProgressiveCoverageAnalyzer:
    """
    Analyzes progressive coverage and finds optimal rule set size.

    Uses F-score (or variants) to balance:
    - Precision: How accurate are the rules?
    - Coverage: How many events do they handle?
    - Parsimony: Fewer rules are better
    """

    def __init__(self, schema):
        self.schema = schema
        self.all_rules_data = {}  # Rules extracted at different thresholds

    def extract_rules_at_multiple_thresholds(self,
                                             systematicity_path: Path,
                                             morph_analysis_path: Path,
                                             newspaper: str):
        """Extract rules at multiple confidence/frequency thresholds."""

        print(f"\n{'='*80}")
        print(f"PROGRESSIVE RULE EXTRACTION: {newspaper}")
        print(f"{'='*80}")

        # Define threshold combinations to try
        thresholds = [
            {'conf': 0.95, 'freq': 10, 'name': 'strict'},
            {'conf': 0.90, 'freq': 5, 'name': 'default'},
            {'conf': 0.85, 'freq': 3, 'name': 'moderate'},
            {'conf': 0.80, 'freq': 2, 'name': 'relaxed'},
            {'conf': 0.70, 'freq': 1, 'name': 'permissive'},
        ]

        results = {}

        for threshold in thresholds:
            print(f"\n--- Threshold: {threshold['name']} (conf={threshold['conf']:.0%}, freq={threshold['freq']}) ---")

            # Extract lexical/syntactic rules
            extractor = RuleExtractor(self.schema)
            lex_syn_rules = extractor.extract_from_analysis(
                systematicity_path,
                min_confidence=threshold['conf'],
                min_frequency=threshold['freq']
            )

            # Extract morphological rules
            morph_extractor = MorphologicalRuleExtractor()
            morph_rules = morph_extractor.extract_from_morphological_analysis(
                morph_analysis_path,
                min_confidence=threshold['conf'],
                min_frequency=threshold['freq']
            )

            results[threshold['name']] = {
                'threshold': threshold,
                'lexical_count': len(lex_syn_rules['lexical_rules']),
                'syntactic_count': len(lex_syn_rules['syntactic_rules']),
                'morphological_count': len(morph_rules),
                'default_count': len(lex_syn_rules['default_rules']),
                'total_rules': (len(lex_syn_rules['lexical_rules']) +
                               len(lex_syn_rules['syntactic_rules']) +
                               len(morph_rules) +
                               len(lex_syn_rules['default_rules'])),
                'lexical_coverage': lex_syn_rules['statistics'].get('lexical_coverage', 0),
                'syntactic_coverage': lex_syn_rules['statistics'].get('syntactic_coverage', 0),
                'rules_data': lex_syn_rules,
                'morph_rules': morph_rules
            }

            print(f"   Total rules: {results[threshold['name']]['total_rules']}")

        self.all_rules_data[newspaper] = results
        return results

    def compute_progressive_coverage(self,
                                     rules_data: Dict[str, Any],
                                     total_events: int) -> pd.DataFrame:
        """
        Compute cumulative coverage as we add rules progressively.

        Returns DataFrame with columns: rule_count, coverage, accuracy, f1_score
        """

        # Combine all rules and sort by frequency
        all_rules = []

        # Add lexical rules
        for rule in rules_data['lexical_rules']:
            all_rules.append({
                'type': 'lexical',
                'frequency': rule['frequency'],
                'confidence': rule['confidence']
            })

        # Add morphological rules (if available)
        if 'morphological_rules' in rules_data:
            for rule in rules_data['morphological_rules']:
                all_rules.append({
                    'type': 'morphological',
                    'frequency': rule['frequency'],
                    'confidence': rule['confidence']
                })

        # Add syntactic rules
        for rule in rules_data['syntactic_rules']:
            all_rules.append({
                'type': 'syntactic',
                'frequency': rule['frequency'],
                'confidence': rule['confidence']
            })

        # Add default rules
        for rule in rules_data['default_rules']:
            all_rules.append({
                'type': 'default',
                'frequency': rule['frequency'],
                'confidence': rule['confidence']
            })

        # Sort by frequency (descending)
        all_rules.sort(key=lambda x: x['frequency'], reverse=True)

        # Compute progressive metrics
        progressive_data = []
        cumulative_coverage = 0
        cumulative_weighted_conf = 0

        for i, rule in enumerate(all_rules, 1):
            cumulative_coverage += rule['frequency']
            cumulative_weighted_conf += rule['confidence'] * rule['frequency']

            coverage_pct = (cumulative_coverage / total_events * 100) if total_events > 0 else 0
            avg_confidence = (cumulative_weighted_conf / cumulative_coverage * 100) if cumulative_coverage > 0 else 0

            # F1-score: harmonic mean of coverage and accuracy
            f1_score = (2 * coverage_pct * avg_confidence / (coverage_pct + avg_confidence)) if (coverage_pct + avg_confidence) > 0 else 0

            # Efficiency: coverage per rule
            efficiency = coverage_pct / i if i > 0 else 0

            # Weighted F1: penalize large rule sets
            parsimony_penalty = 1 / np.log(i + 1)  # Logarithmic penalty for rule count
            weighted_f1 = f1_score * parsimony_penalty

            progressive_data.append({
                'rule_count': i,
                'rule_type': rule['type'],
                'coverage_pct': coverage_pct,
                'coverage_events': cumulative_coverage,
                'accuracy_pct': avg_confidence,
                'f1_score': f1_score,
                'efficiency': efficiency,
                'weighted_f1': weighted_f1
            })

        return pd.DataFrame(progressive_data)

    def find_optimal_rule_count(self,
                                progressive_df: pd.DataFrame,
                                metric: str = 'f1_score') -> Dict[str, Any]:
        """
        Find optimal rule count that maximizes the chosen metric.

        Args:
            progressive_df: DataFrame from compute_progressive_coverage
            metric: One of 'f1_score', 'weighted_f1', 'efficiency'

        Returns:
            Dictionary with optimal point information
        """

        # Find maximum
        optimal_idx = progressive_df[metric].idxmax()
        optimal_row = progressive_df.loc[optimal_idx]

        # Also find some standard points
        coverage_70_idx = progressive_df[progressive_df['coverage_pct'] >= 70].index.min() if not progressive_df[progressive_df['coverage_pct'] >= 70].empty else None
        coverage_80_idx = progressive_df[progressive_df['coverage_pct'] >= 80].index.min() if not progressive_df[progressive_df['coverage_pct'] >= 80].empty else None
        coverage_90_idx = progressive_df[progressive_df['coverage_pct'] >= 90].index.min() if not progressive_df[progressive_df['coverage_pct'] >= 90].empty else None

        return {
            'optimal': {
                'rule_count': int(optimal_row['rule_count']),
                'coverage': optimal_row['coverage_pct'],
                'accuracy': optimal_row['accuracy_pct'],
                metric: optimal_row[metric]
            },
            'coverage_70': progressive_df.loc[coverage_70_idx].to_dict() if coverage_70_idx is not None else None,
            'coverage_80': progressive_df.loc[coverage_80_idx].to_dict() if coverage_80_idx is not None else None,
            'coverage_90': progressive_df.loc[coverage_90_idx].to_dict() if coverage_90_idx is not None else None,
        }

    def create_progressive_coverage_plot(self,
                                        progressive_df: pd.DataFrame,
                                        optimal_points: Dict[str, Any],
                                        newspaper: str,
                                        output_dir: Path):
        """Create visualization of progressive coverage."""

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        # Plot 1: Coverage and Accuracy vs Rule Count
        ax1_twin = ax1.twinx()
        ax1.plot(progressive_df['rule_count'], progressive_df['coverage_pct'],
                'b-', linewidth=2, label='Coverage (%)')
        ax1_twin.plot(progressive_df['rule_count'], progressive_df['accuracy_pct'],
                     'r-', linewidth=2, label='Accuracy (%)')

        # Mark optimal point
        opt = optimal_points['optimal']
        ax1.axvline(x=opt['rule_count'], color='green', linestyle='--', alpha=0.5)
        ax1.plot(opt['rule_count'], opt['coverage'], 'go', markersize=10, label=f"Optimal ({opt['rule_count']} rules)")

        ax1.set_xlabel('Number of Rules', fontweight='bold')
        ax1.set_ylabel('Coverage (%)', color='b', fontweight='bold')
        ax1_twin.set_ylabel('Accuracy (%)', color='r', fontweight='bold')
        ax1.set_title(f'{newspaper}: Progressive Coverage & Accuracy', fontweight='bold')
        ax1.legend(loc='lower right')
        ax1_twin.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)

        # Plot 2: F1-Score vs Rule Count
        ax2.plot(progressive_df['rule_count'], progressive_df['f1_score'],
                'purple', linewidth=2, label='F1-Score')
        ax2.plot(progressive_df['rule_count'], progressive_df['weighted_f1'],
                'orange', linewidth=2, label='Weighted F1 (penalized)')

        ax2.axvline(x=opt['rule_count'], color='green', linestyle='--', alpha=0.5, label=f"Optimal")
        ax2.plot(opt['rule_count'], opt['f1_score'], 'go', markersize=10)

        ax2.set_xlabel('Number of Rules', fontweight='bold')
        ax2.set_ylabel('F1-Score', fontweight='bold')
        ax2.set_title(f'{newspaper}: F1-Score Optimization', fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Plot 3: Efficiency (Coverage per Rule)
        ax3.plot(progressive_df['rule_count'], progressive_df['efficiency'],
                'teal', linewidth=2)
        ax3.axvline(x=opt['rule_count'], color='green', linestyle='--', alpha=0.5)

        ax3.set_xlabel('Number of Rules', fontweight='bold')
        ax3.set_ylabel('Efficiency (Coverage % per Rule)', fontweight='bold')
        ax3.set_title(f'{newspaper}: Rule Efficiency', fontweight='bold')
        ax3.grid(True, alpha=0.3)

        # Plot 4: Coverage Milestones
        milestones = [10, 50, 100, 200, 500, 1000]
        milestone_data = []
        for m in milestones:
            if m <= len(progressive_df):
                row = progressive_df.iloc[m-1]
                milestone_data.append({
                    'Rules': m,
                    'Coverage': row['coverage_pct'],
                    'Accuracy': row['accuracy_pct']
                })

        if milestone_data:
            mile_df = pd.DataFrame(milestone_data)
            x = np.arange(len(milestone_data))
            width = 0.35

            ax4.bar(x - width/2, mile_df['Coverage'], width, label='Coverage %', color='steelblue')
            ax4.bar(x + width/2, mile_df['Accuracy'], width, label='Accuracy %', color='coral')

            ax4.set_xlabel('Number of Rules', fontweight='bold')
            ax4.set_ylabel('Percentage', fontweight='bold')
            ax4.set_title(f'{newspaper}: Coverage Milestones', fontweight='bold')
            ax4.set_xticks(x)
            ax4.set_xticklabels(mile_df['Rules'])
            ax4.legend()
            ax4.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_dir / f'progressive_coverage_{newspaper}.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"   ✅ Saved progressive coverage plot to: {output_dir / f'progressive_coverage_{newspaper}.png'}")

    def create_comparison_table(self,
                                newspaper_results: Dict[str, Dict],
                                output_dir: Path):
        """Create table comparing optimal rule counts across newspapers."""

        comparison_data = []

        for newspaper, results in newspaper_results.items():
            opt = results['optimal_f1']['optimal']
            opt_w = results['optimal_weighted_f1']['optimal']

            comparison_data.append({
                'Newspaper': newspaper,
                'Optimal (F1)': int(opt['rule_count']),
                'Coverage @ Opt': f"{opt['coverage']:.1f}%",
                'Accuracy @ Opt': f"{opt['accuracy']:.1f}%",
                'F1-Score': f"{opt['f1_score']:.1f}",
                'Optimal (Weighted F1)': int(opt_w['rule_count']),
                'Coverage @ Weighted': f"{opt_w['coverage']:.1f}%",
                'Accuracy @ Weighted': f"{opt_w['accuracy']:.1f}%"
            })

        df = pd.DataFrame(comparison_data)
        df.to_csv(output_dir / 'optimal_rule_counts.csv', index=False)

        print(f"\n   ✅ Saved optimal rule counts to: {output_dir / 'optimal_rule_counts.csv'}")

        return df


def main():
    """Run progressive coverage analysis for all newspapers."""

    from config import BASE_DIR
    from paths_config import SCHEMA_PATH
    from register_comparison.meta_data.schema import FeatureSchema

    schema = FeatureSchema(SCHEMA_PATH)
    schema.load_schema()

    newspapers = ["Times-of-India", "Hindustan-Times", "The-Hindu"]
    analyzer = ProgressiveCoverageAnalyzer(schema)

    output_dir = BASE_DIR / "output" / "progressive_coverage_analysis"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*80)
    print("PROGRESSIVE COVERAGE ANALYSIS")
    print("="*80)

    all_newspaper_results = {}

    for newspaper in newspapers:
        print(f"\n{'='*80}")
        print(f"ANALYZING: {newspaper}")
        print(f"{'='*80}")

        # Paths
        sys_path = BASE_DIR / "output" / newspaper / "rule_analysis" / "enhanced_systematicity.json"
        morph_path = BASE_DIR / "output" / newspaper / "morphological_analysis" / "morphological_analysis.json"

        if not sys_path.exists() or not morph_path.exists():
            print(f"   ⚠️  Missing analysis files for {newspaper}, skipping...")
            continue

        # Extract rules at multiple thresholds
        threshold_results = analyzer.extract_rules_at_multiple_thresholds(
            sys_path, morph_path, newspaper
        )

        # Use default threshold for detailed analysis
        rules_data = threshold_results['default']['rules_data']

        # Get total events
        with open(sys_path, 'r') as f:
            sys_data = json.load(f)
        total_events = sys_data['by_granularity']['lexical']['total_events']

        # Compute progressive coverage
        print(f"\n   Computing progressive coverage...")
        progressive_df = analyzer.compute_progressive_coverage(rules_data, total_events)

        # Find optimal points
        print(f"\n   Finding optimal rule counts...")
        optimal_f1 = analyzer.find_optimal_rule_count(progressive_df, metric='f1_score')
        optimal_weighted_f1 = analyzer.find_optimal_rule_count(progressive_df, metric='weighted_f1')

        print(f"\n   📊 Optimal Rule Count (F1-Score): {optimal_f1['optimal']['rule_count']}")
        print(f"      Coverage: {optimal_f1['optimal']['coverage']:.1f}%")
        print(f"      Accuracy: {optimal_f1['optimal']['accuracy']:.1f}%")
        print(f"      F1-Score: {optimal_f1['optimal']['f1_score']:.1f}")

        print(f"\n   📊 Optimal Rule Count (Weighted F1): {optimal_weighted_f1['optimal']['rule_count']}")
        print(f"      Coverage: {optimal_weighted_f1['optimal']['coverage']:.1f}%")
        print(f"      Accuracy: {optimal_weighted_f1['optimal']['accuracy']:.1f}%")

        # Create visualizations
        print(f"\n   Creating visualizations...")
        analyzer.create_progressive_coverage_plot(
            progressive_df, optimal_f1, newspaper, output_dir
        )

        # Save progressive data
        progressive_df.to_csv(output_dir / f'progressive_data_{newspaper}.csv', index=False)
        print(f"   ✅ Saved progressive data to: {output_dir / f'progressive_data_{newspaper}.csv'}")

        all_newspaper_results[newspaper] = {
            'optimal_f1': optimal_f1,
            'optimal_weighted_f1': optimal_weighted_f1,
            'progressive_df': progressive_df
        }

    # Create comparison table
    print(f"\n{'='*80}")
    print("CREATING CROSS-NEWSPAPER COMPARISON")
    print(f"{'='*80}")
    analyzer.create_comparison_table(all_newspaper_results, output_dir)

    print(f"\n{'='*80}")
    print("PROGRESSIVE COVERAGE ANALYSIS COMPLETE")
    print(f"{'='*80}")
    print(f"\nAll results saved to: {output_dir}")


if __name__ == "__main__":
    main()
