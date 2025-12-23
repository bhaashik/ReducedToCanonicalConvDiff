#!/usr/bin/env python3
"""
Progressive Coverage Analysis WITH Morphological Features.

This script integrates morphological rules into the transformation engine
and compares progressive coverage before/after morphological integration.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Any
import numpy as np

# Set matplotlib backend
import matplotlib
matplotlib.use('Agg')


class ProgressiveCoverageWithMorphology:
    """Analyzes progressive coverage with morphological features integrated."""

    def __init__(self):
        self.newspapers = ['Times-of-India', 'Hindustan-Times', 'The-Hindu']
        self.project_root = Path(__file__).parent.absolute()
        self.output_dir = self.project_root / 'output' / 'progressive_coverage_with_morphology'
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Store results
        self.results = {}
        self.comparison_data = {}

    def load_previous_results(self, newspaper: str) -> pd.DataFrame:
        """Load previous progressive coverage results (without morphology)."""
        prev_path = self.project_root / 'output' / 'progressive_coverage_analysis' / f'progressive_data_{newspaper}.csv'

        if prev_path.exists():
            return pd.read_csv(prev_path)
        else:
            return pd.DataFrame()

    def extract_morphological_rules(self, newspaper: str) -> List[Dict]:
        """Extract morphological rules from morphological analysis."""
        morph_path = self.project_root / 'output' / newspaper / 'morphological_analysis' / 'morphological_rules.csv'

        if not morph_path.exists():
            print(f"⚠️  No morphological rules found for {newspaper}")
            return []

        df = pd.read_csv(morph_path)

        rules = []
        for i, row in enumerate(df.iterrows(), 1):
            _, row_data = row
            rule = {
                'rule_id': f"MORPH_{i:04d}",
                'pos': row_data['pos'],
                'morph_feature': row_data['feature'],
                'headline_value': row_data['headline_value'],
                'canonical_value': row_data['canonical_value'],
                'confidence': 1.0,  # Morphological rules have 100% consistency
                'frequency': row_data['frequency'],
                'rule_type': 'morphological'
            }
            rules.append(rule)

        return rules

    def extract_lexical_syntactic_rules(self, newspaper: str) -> Dict[str, List[Dict]]:
        """Extract lexical and syntactic rules from rule analysis."""
        rules_path = self.project_root / 'output' / newspaper / 'rule_analysis' / 'extracted_rules' / 'extracted_rules.json'

        if not rules_path.exists():
            print(f"⚠️  No extracted rules found for {newspaper}")
            return {'lexical': [], 'syntactic': [], 'default': []}

        with open(rules_path, 'r') as f:
            rules_data = json.load(f)

        return {
            'lexical': rules_data.get('lexical_rules', []),
            'syntactic': rules_data.get('syntactic_rules', []),
            'default': rules_data.get('default_rules', [])
        }

    def compute_progressive_coverage_with_morphology(self, newspaper: str) -> pd.DataFrame:
        """Compute progressive coverage with morphological rules integrated."""
        print(f"\n{'='*80}")
        print(f"COMPUTING PROGRESSIVE COVERAGE WITH MORPHOLOGY: {newspaper}")
        print(f"{'='*80}\n")

        # Extract all rules
        other_rules = self.extract_lexical_syntactic_rules(newspaper)
        morph_rules = self.extract_morphological_rules(newspaper)

        # Combine all rules
        all_rules = []

        # Add lexical rules
        for i, rule in enumerate(other_rules['lexical'], 1):
            all_rules.append({
                'rule_id': f"LEX_{i:04d}",
                'rule_type': 'lexical',
                'frequency': rule['frequency'],
                'confidence': rule['confidence']
            })

        # Add morphological rules
        for rule in morph_rules:
            all_rules.append({
                'rule_id': rule['rule_id'],
                'rule_type': 'morphological',
                'frequency': rule['frequency'],
                'confidence': rule['confidence']
            })

        # Add syntactic rules
        for i, rule in enumerate(other_rules['syntactic'], 1):
            all_rules.append({
                'rule_id': f"SYN_{i:04d}",
                'rule_type': 'syntactic',
                'frequency': rule['frequency'],
                'confidence': rule['confidence']
            })

        # Add default rules
        for i, rule in enumerate(other_rules['default'], 1):
            all_rules.append({
                'rule_id': f"DEF_{i:04d}",
                'rule_type': 'default',
                'frequency': rule['frequency'],
                'confidence': rule['confidence']
            })

        # Sort by frequency (highest first)
        all_rules.sort(key=lambda r: r['frequency'], reverse=True)

        # Get total events from enhanced systematicity
        sys_path = self.project_root / 'output' / newspaper / 'rule_analysis' / 'enhanced_systematicity.json'
        total_events = 0
        if sys_path.exists():
            with open(sys_path, 'r') as f:
                sys_data = json.load(f)
                # Use lexical granularity total events
                if 'by_granularity' in sys_data and 'lexical' in sys_data['by_granularity']:
                    total_events = sys_data['by_granularity']['lexical'].get('total_events', 0)
                else:
                    total_events = sys_data.get('total_events', 0)

        if total_events == 0:
            print(f"⚠️  Could not determine total events for {newspaper}")
            return pd.DataFrame()

        print(f"Total rules: {len(all_rules)}")
        print(f"  - Lexical: {len(other_rules['lexical'])}")
        print(f"  - Morphological: {len(morph_rules)}")
        print(f"  - Syntactic: {len(other_rules['syntactic'])}")
        print(f"  - Default: {len(other_rules['default'])}")
        print(f"Total events: {total_events}")

        # Compute progressive coverage
        rows = []
        cumulative_coverage = 0
        cumulative_weighted_confidence = 0

        for i, rule in enumerate(all_rules, 1):
            cumulative_coverage += rule['frequency']
            cumulative_weighted_confidence += rule['frequency'] * rule['confidence']

            coverage_pct = 100 * cumulative_coverage / total_events
            accuracy_pct = 100 * (cumulative_weighted_confidence / cumulative_coverage if cumulative_coverage > 0 else 0)

            # F1-score
            if coverage_pct + accuracy_pct > 0:
                f1_score = 2 * coverage_pct * accuracy_pct / (coverage_pct + accuracy_pct)
            else:
                f1_score = 0

            # Efficiency
            efficiency = coverage_pct / i

            # Weighted F1 with parsimony penalty
            parsimony_penalty = 1 / np.log(i + 1)
            weighted_f1 = f1_score * parsimony_penalty

            row = {
                'rule_count': i,
                'rule_type': rule['rule_type'],
                'coverage_pct': coverage_pct,
                'coverage_events': cumulative_coverage,
                'accuracy_pct': accuracy_pct,
                'f1_score': f1_score,
                'efficiency': efficiency,
                'weighted_f1': weighted_f1
            }
            rows.append(row)

        df = pd.DataFrame(rows)

        print(f"\n✅ Progressive coverage computed")
        print(f"   Rule count: {len(df)}")
        print(f"   Max coverage: {df['coverage_pct'].max():.1f}%")
        print(f"   Max F1-score: {df['f1_score'].max():.1f}")

        return df

    def find_optimal_points(self, progressive_df: pd.DataFrame) -> Dict[str, Any]:
        """Find optimal rule counts using different metrics."""
        if len(progressive_df) == 0:
            return {}

        # Find optimal F1
        optimal_f1_idx = progressive_df['f1_score'].idxmax()
        optimal_f1_row = progressive_df.loc[optimal_f1_idx]

        # Find optimal weighted F1
        optimal_weighted_idx = progressive_df['weighted_f1'].idxmax()
        optimal_weighted_row = progressive_df.loc[optimal_weighted_idx]

        # Coverage milestones
        milestones = {}
        for target in [70, 80, 90]:
            milestone_rows = progressive_df[progressive_df['coverage_pct'] >= target]
            if len(milestone_rows) > 0:
                milestones[target] = milestone_rows.iloc[0]['rule_count']
            else:
                milestones[target] = len(progressive_df)

        return {
            'optimal_f1': {
                'rule_count': optimal_f1_row['rule_count'],
                'coverage': optimal_f1_row['coverage_pct'],
                'accuracy': optimal_f1_row['accuracy_pct'],
                'f1_score': optimal_f1_row['f1_score']
            },
            'optimal_weighted_f1': {
                'rule_count': optimal_weighted_row['rule_count'],
                'coverage': optimal_weighted_row['coverage_pct'],
                'accuracy': optimal_weighted_row['accuracy_pct'],
                'weighted_f1': optimal_weighted_row['weighted_f1']
            },
            'milestones': milestones
        }

    def create_comparison_visualization(self, newspaper: str):
        """Create visualization comparing before/after morphology integration."""
        print(f"\n{'='*80}")
        print(f"CREATING COMPARISON VISUALIZATION: {newspaper}")
        print(f"{'='*80}\n")

        # Load data
        df_with_morph = self.results.get(newspaper)
        df_without_morph = self.load_previous_results(newspaper)

        if df_with_morph is None or len(df_with_morph) == 0:
            print(f"⚠️  No results with morphology for {newspaper}")
            return

        if df_without_morph is None or len(df_without_morph) == 0:
            print(f"⚠️  No previous results for {newspaper}")
            return

        # Create figure with 3x2 subplots
        fig, axes = plt.subplots(3, 2, figsize=(16, 18))
        fig.suptitle(f'Progressive Coverage: Before vs After Morphological Integration\n{newspaper}',
                     fontsize=16, fontweight='bold')

        # 1. Coverage comparison
        ax1 = axes[0, 0]
        ax1.plot(df_without_morph['rule_count'], df_without_morph['coverage_pct'],
                label='Without Morphology', color='steelblue', linewidth=2)
        ax1.plot(df_with_morph['rule_count'], df_with_morph['coverage_pct'],
                label='With Morphology', color='coral', linewidth=2)
        ax1.set_xlabel('Number of Rules', fontweight='bold')
        ax1.set_ylabel('Coverage (%)', fontweight='bold')
        ax1.set_title('Coverage vs Rule Count')
        ax1.legend()
        ax1.grid(alpha=0.3)

        # 2. Accuracy comparison
        ax2 = axes[0, 1]
        ax2.plot(df_without_morph['rule_count'], df_without_morph['accuracy_pct'],
                label='Without Morphology', color='steelblue', linewidth=2)
        ax2.plot(df_with_morph['rule_count'], df_with_morph['accuracy_pct'],
                label='With Morphology', color='coral', linewidth=2)
        ax2.set_xlabel('Number of Rules', fontweight='bold')
        ax2.set_ylabel('Accuracy (%)', fontweight='bold')
        ax2.set_title('Accuracy vs Rule Count')
        ax2.legend()
        ax2.grid(alpha=0.3)

        # 3. F1-score comparison
        ax3 = axes[1, 0]
        ax3.plot(df_without_morph['rule_count'], df_without_morph['f1_score'],
                label='Without Morphology', color='steelblue', linewidth=2)
        ax3.plot(df_with_morph['rule_count'], df_with_morph['f1_score'],
                label='With Morphology', color='coral', linewidth=2)
        ax3.set_xlabel('Number of Rules', fontweight='bold')
        ax3.set_ylabel('F1-Score', fontweight='bold')
        ax3.set_title('F1-Score vs Rule Count')
        ax3.legend()
        ax3.grid(alpha=0.3)

        # 4. Efficiency comparison
        ax4 = axes[1, 1]
        ax4.plot(df_without_morph['rule_count'], df_without_morph['efficiency'],
                label='Without Morphology', color='steelblue', linewidth=2)
        ax4.plot(df_with_morph['rule_count'], df_with_morph['efficiency'],
                label='With Morphology', color='coral', linewidth=2)
        ax4.set_xlabel('Number of Rules', fontweight='bold')
        ax4.set_ylabel('Efficiency (Coverage per Rule)', fontweight='bold')
        ax4.set_title('Efficiency vs Rule Count')
        ax4.legend()
        ax4.grid(alpha=0.3)

        # 5. Rule type distribution (with morphology only)
        ax5 = axes[2, 0]
        rule_type_counts = df_with_morph.groupby('rule_type')['rule_count'].count()
        colors_map = {
            'lexical': '#FF6B6B',
            'morphological': '#4ECDC4',
            'syntactic': '#95E1D3',
            'default': '#F8B500'
        }
        colors = [colors_map.get(rt, '#999999') for rt in rule_type_counts.index]
        ax5.pie(rule_type_counts.values, labels=rule_type_counts.index,
               autopct='%1.1f%%', colors=colors, startangle=90)
        ax5.set_title('Rule Type Distribution\n(With Morphology)')

        # 6. Improvement metrics table
        ax6 = axes[2, 1]
        ax6.axis('tight')
        ax6.axis('off')

        # Calculate improvement metrics
        max_coverage_without = df_without_morph['coverage_pct'].max()
        max_coverage_with = df_with_morph['coverage_pct'].max()
        coverage_improvement = max_coverage_with - max_coverage_without

        max_f1_without = df_without_morph['f1_score'].max()
        max_f1_with = df_with_morph['f1_score'].max()
        f1_improvement = max_f1_with - max_f1_without

        # Rules at optimal F1
        optimal_without = df_without_morph.loc[df_without_morph['f1_score'].idxmax()]
        optimal_with = df_with_morph.loc[df_with_morph['f1_score'].idxmax()]

        table_data = [
            ['Metric', 'Without Morph', 'With Morph', 'Improvement'],
            ['Max Coverage', f"{max_coverage_without:.1f}%", f"{max_coverage_with:.1f}%", f"+{coverage_improvement:.1f}%"],
            ['Max F1-Score', f"{max_f1_without:.1f}", f"{max_f1_with:.1f}", f"+{f1_improvement:.1f}"],
            ['Rules @ Optimal F1', f"{optimal_without['rule_count']:.0f}", f"{optimal_with['rule_count']:.0f}", f"{optimal_with['rule_count'] - optimal_without['rule_count']:+.0f}"],
            ['Coverage @ Opt F1', f"{optimal_without['coverage_pct']:.1f}%", f"{optimal_with['coverage_pct']:.1f}%", f"+{optimal_with['coverage_pct'] - optimal_without['coverage_pct']:.1f}%"],
            ['Accuracy @ Opt F1', f"{optimal_without['accuracy_pct']:.1f}%", f"{optimal_with['accuracy_pct']:.1f}%", f"+{optimal_with['accuracy_pct'] - optimal_without['accuracy_pct']:.1f}%"]
        ]

        table = ax6.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.3, 0.23, 0.23, 0.24])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)

        # Style header row
        for i in range(4):
            table[(0, i)].set_facecolor('#4ECDC4')
            table[(0, i)].set_text_props(weight='bold', color='white')

        ax6.set_title('Improvement Summary', fontweight='bold', pad=20)

        plt.tight_layout()

        # Save
        output_path = self.output_dir / f'comparison_{newspaper}.png'
        plt.savefig(output_path, dpi=200)
        plt.close()

        print(f"✅ Saved to: {output_path}")

    def create_summary_table(self):
        """Create summary comparison table across all newspapers."""
        print(f"\n{'='*80}")
        print("CREATING SUMMARY TABLE")
        print(f"{'='*80}\n")

        rows = []

        for newspaper in self.newspapers:
            df_with = self.results.get(newspaper)
            df_without = self.load_previous_results(newspaper)

            if df_with is None or df_without is None:
                continue

            # Calculate metrics
            max_coverage_without = df_without['coverage_pct'].max()
            max_coverage_with = df_with['coverage_pct'].max()
            coverage_improvement = max_coverage_with - max_coverage_without

            max_f1_without = df_without['f1_score'].max()
            max_f1_with = df_with['f1_score'].max()
            f1_improvement = max_f1_with - max_f1_without

            optimal_without = df_without.loc[df_without['f1_score'].idxmax()]
            optimal_with = df_with.loc[df_with['f1_score'].idxmax()]

            # Count morphological rules
            morph_rules = len(df_with[df_with['rule_type'] == 'morphological'])

            row = {
                'Newspaper': newspaper,
                'Morph Rules': morph_rules,
                'Coverage (No Morph)': f"{max_coverage_without:.1f}%",
                'Coverage (With Morph)': f"{max_coverage_with:.1f}%",
                'Coverage Improvement': f"+{coverage_improvement:.1f}%",
                'F1 (No Morph)': f"{max_f1_without:.1f}",
                'F1 (With Morph)': f"{max_f1_with:.1f}",
                'F1 Improvement': f"+{f1_improvement:.1f}",
                'Opt Rules (No Morph)': int(optimal_without['rule_count']),
                'Opt Rules (With Morph)': int(optimal_with['rule_count'])
            }
            rows.append(row)

        df = pd.DataFrame(rows)

        # Save
        csv_path = self.output_dir / 'improvement_summary.csv'
        df.to_csv(csv_path, index=False)
        print(f"✅ Saved to: {csv_path}")

        return df

    def run_complete_analysis(self):
        """Run complete progressive coverage analysis with morphology."""
        print(f"\n{'='*80}")
        print("PROGRESSIVE COVERAGE ANALYSIS WITH MORPHOLOGICAL FEATURES")
        print(f"{'='*80}\n")

        for newspaper in self.newspapers:
            # Compute progressive coverage with morphology
            df = self.compute_progressive_coverage_with_morphology(newspaper)

            if len(df) > 0:
                self.results[newspaper] = df

                # Find optimal points
                optimal = self.find_optimal_points(df)
                self.comparison_data[newspaper] = optimal

                # Save progressive data
                csv_path = self.output_dir / f'progressive_data_with_morphology_{newspaper}.csv'
                df.to_csv(csv_path, index=False)
                print(f"✅ Saved progressive data to: {csv_path}")

                # Create comparison visualization
                self.create_comparison_visualization(newspaper)

        # Create summary table
        if len(self.results) > 0:
            self.create_summary_table()

        print(f"\n{'='*80}")
        print("ANALYSIS COMPLETE")
        print(f"{'='*80}\n")
        print(f"All results saved to: {self.output_dir}")


if __name__ == '__main__':
    analyzer = ProgressiveCoverageWithMorphology()
    analyzer.run_complete_analysis()
