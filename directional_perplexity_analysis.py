#!/usr/bin/env python3
"""
Directional Perplexity Analysis.

Compares complexity in both transformation directions:
- C→H (Canonical to Headline): Reduction/Compression
- H→C (Headline to Canonical): Expansion/Restoration

This reveals which direction is inherently more complex/difficult.
"""

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("KMP_AFFINITY", "disabled")
os.environ.setdefault("KMP_INIT_AT_FORK", "FALSE")

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 200
plt.rcParams['font.size'] = 10


class PerplexityCalculator:
    """Calculates perplexity metrics."""

    def calculate_distribution_perplexity(self, counter: Counter) -> Dict[str, float]:
        """Calculate perplexity metrics from a frequency counter."""
        total = sum(counter.values())
        if total == 0:
            return {
                'entropy': 0.0,
                'perplexity': 0.0,
                'normalized_perplexity': 0.0,
                'num_types': 0,
                'num_tokens': 0
            }

        # Convert to probabilities
        probabilities = [count / total for count in counter.values()]

        # Calculate entropy
        entropy = 0.0
        for p in probabilities:
            if p > 0:
                entropy -= p * np.log2(p)

        # Calculate perplexity
        PP = 2 ** entropy
        PP_norm = PP ** (1.0 / len(counter)) if len(counter) > 0 else PP

        return {
            'entropy': entropy,
            'perplexity': PP,
            'normalized_perplexity': PP_norm,
            'num_types': len(counter),
            'num_tokens': total
        }


class DirectionalPerplexityAnalyzer:
    """Analyzes perplexity in both transformation directions."""

    def __init__(self, newspaper: str, project_root: Path):
        self.newspaper = newspaper
        self.project_root = project_root
        self.calculator = PerplexityCalculator()

        # Load data
        self.events_df = self.load_events_data()

        # Results
        self.results = {}

    def load_events_data(self) -> pd.DataFrame:
        """Load events data."""
        events_path = self.project_root / 'output' / self.newspaper / 'events_global.csv'

        if not events_path.exists():
            print(f"⚠️  Events file not found: {events_path}")
            return pd.DataFrame()

        df = pd.read_csv(events_path)
        print(f"✅ Loaded {len(df)} events for {self.newspaper}")
        return df

    def classify_transformation_direction(self, canonical_val: str, headline_val: str) -> str:
        """
        Classify transformation direction based on value changes.

        C→H patterns (reduction):
        - Value → ABSENT (deletion/removal)
        - Complex → Simple (simplification)

        H→C patterns (expansion):
        - ABSENT → Value (addition/restoration)
        - Simple → Complex (expansion)
        """
        c_val = str(canonical_val).upper()
        h_val = str(headline_val).upper()

        # Deletion patterns (C→H)
        if c_val != 'ABSENT' and h_val == 'ABSENT':
            return 'C→H'

        # Addition patterns (H→C)
        if c_val == 'ABSENT' and h_val != 'ABSENT':
            return 'H→C'

        # Both present - check for simplification
        if c_val != 'ABSENT' and h_val != 'ABSENT':
            # If values different, it's a change
            # Direction depends on event type context
            # Default: treat as C→H if canonical seems more complex
            if len(c_val) > len(h_val):
                return 'C→H'
            elif len(c_val) < len(h_val):
                return 'H→C'
            else:
                return 'Bidirectional'

        return 'Unclear'

    def analyze_directional_complexity(self) -> Dict:
        """Analyze complexity by transformation direction."""
        print(f"\n{'='*80}")
        print(f"DIRECTIONAL PERPLEXITY ANALYSIS: {self.newspaper}")
        print(f"{'='*80}\n")

        results = {}

        # Classify each event
        c2h_transformations = Counter()
        h2c_transformations = Counter()
        bidirectional = Counter()

        for _, row in self.events_df.iterrows():
            c_val = row.get('canonical_value', 'NULL')
            h_val = row.get('headline_value', 'NULL')
            feature = row.get('feature_id', 'UNKNOWN')

            direction = self.classify_transformation_direction(c_val, h_val)

            transformation = f"{feature}:{c_val}→{h_val}"

            if direction == 'C→H':
                c2h_transformations[transformation] += 1
            elif direction == 'H→C':
                h2c_transformations[transformation] += 1
            else:
                bidirectional[transformation] += 1

        # Calculate perplexity for each direction
        results['c2h'] = self.calculator.calculate_distribution_perplexity(c2h_transformations)
        results['h2c'] = self.calculator.calculate_distribution_perplexity(h2c_transformations)
        results['bidirectional'] = self.calculator.calculate_distribution_perplexity(bidirectional)

        print(f"C→H (Canonical to Headline - Reduction):")
        print(f"  Transformations: {results['c2h']['num_tokens']}")
        print(f"  Patterns: {results['c2h']['num_types']}")
        print(f"  Perplexity: {results['c2h']['perplexity']:.3f}")
        print(f"  Normalized PP: {results['c2h']['normalized_perplexity']:.3f}")
        print(f"  Entropy: {results['c2h']['entropy']:.3f} bits")

        print(f"\nH→C (Headline to Canonical - Expansion):")
        print(f"  Transformations: {results['h2c']['num_tokens']}")
        print(f"  Patterns: {results['h2c']['num_types']}")
        print(f"  Perplexity: {results['h2c']['perplexity']:.3f}")
        print(f"  Normalized PP: {results['h2c']['normalized_perplexity']:.3f}")
        print(f"  Entropy: {results['h2c']['entropy']:.3f} bits")

        print(f"\nBidirectional (Change between non-ABSENT values):")
        print(f"  Transformations: {results['bidirectional']['num_tokens']}")
        print(f"  Patterns: {results['bidirectional']['num_types']}")
        print(f"  Perplexity: {results['bidirectional']['perplexity']:.3f}")
        print(f"  Normalized PP: {results['bidirectional']['normalized_perplexity']:.3f}")
        print(f"  Entropy: {results['bidirectional']['entropy']:.3f} bits")

        # Calculate complexity ratio
        if results['h2c']['perplexity'] > 0:
            ratio = results['c2h']['perplexity'] / results['h2c']['perplexity']
            print(f"\nComplexity Ratio (C→H / H→C): {ratio:.3f}")
            if ratio > 1.1:
                print(f"  → C→H is {ratio:.1f}x MORE complex than H→C")
            elif ratio < 0.9:
                print(f"  → H→C is {1/ratio:.1f}x MORE complex than C→H")
            else:
                print(f"  → Similar complexity in both directions")

        self.results = results
        return results

    def analyze_event_level_directionality(self) -> Dict:
        """Analyze directionality for each event type."""
        print(f"\n{'='*80}")
        print(f"EVENT-LEVEL DIRECTIONAL ANALYSIS: {self.newspaper}")
        print(f"{'='*80}\n")

        event_results = {}

        grouped = self.events_df.groupby('feature_id')

        for feature_id, group in grouped:
            c2h = Counter()
            h2c = Counter()
            bidir = Counter()

            for _, row in group.iterrows():
                c_val = row.get('canonical_value', 'NULL')
                h_val = row.get('headline_value', 'NULL')

                direction = self.classify_transformation_direction(c_val, h_val)
                pattern = f"{c_val}→{h_val}"

                if direction == 'C→H':
                    c2h[pattern] += 1
                elif direction == 'H→C':
                    h2c[pattern] += 1
                else:
                    bidir[pattern] += 1

            c2h_metrics = self.calculator.calculate_distribution_perplexity(c2h)
            h2c_metrics = self.calculator.calculate_distribution_perplexity(h2c)

            event_results[feature_id] = {
                'c2h_count': c2h_metrics['num_tokens'],
                'h2c_count': h2c_metrics['num_tokens'],
                'c2h_pp': c2h_metrics['perplexity'],
                'h2c_pp': h2c_metrics['perplexity'],
                'c2h_pp_norm': c2h_metrics['normalized_perplexity'],
                'h2c_pp_norm': h2c_metrics['normalized_perplexity'],
                'dominant_direction': 'C→H' if c2h_metrics['num_tokens'] > h2c_metrics['num_tokens'] else 'H→C'
            }

            if c2h_metrics['num_tokens'] > 0 or h2c_metrics['num_tokens'] > 0:
                print(f"{feature_id:20s}: "
                      f"C→H={c2h_metrics['num_tokens']:5d} (PP={c2h_metrics['perplexity']:6.2f}), "
                      f"H→C={h2c_metrics['num_tokens']:5d} (PP={h2c_metrics['perplexity']:6.2f}) "
                      f"[{event_results[feature_id]['dominant_direction']}]")

        return event_results

    def create_summary_table(self) -> pd.DataFrame:
        """Create summary table."""
        rows = []

        for direction in ['c2h', 'h2c', 'bidirectional']:
            if direction in self.results:
                data = self.results[direction]
                rows.append({
                    'Newspaper': self.newspaper,
                    'Direction': direction.upper().replace('2', '→'),
                    'Direction_Label': {
                        'c2h': 'Reduction',
                        'h2c': 'Expansion',
                        'bidirectional': 'Change'
                    }[direction],
                    'Num_Transformations': data['num_tokens'],
                    'Num_Patterns': data['num_types'],
                    'Perplexity': data['perplexity'],
                    'Normalized_PP': data['normalized_perplexity'],
                    'Entropy': data['entropy']
                })

        return pd.DataFrame(rows)


class CrossNewspaperDirectionalAnalyzer:
    """Analyzes directional complexity across newspapers."""

    def __init__(self):
        self.newspapers = ['Times-of-India', 'Hindustan-Times', 'The-Hindu']
        self.project_root = Path(__file__).parent.absolute()
        self.output_dir = self.project_root / 'output' / 'directional_perplexity'
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.all_results = {}

    def run_all_newspapers(self):
        """Run directional analysis on all newspapers."""
        print(f"\n{'='*80}")
        print("CROSS-NEWSPAPER DIRECTIONAL PERPLEXITY ANALYSIS")
        print(f"{'='*80}\n")

        for newspaper in self.newspapers:
            analyzer = DirectionalPerplexityAnalyzer(newspaper, self.project_root)
            results = analyzer.analyze_directional_complexity()
            event_results = analyzer.analyze_event_level_directionality()

            self.all_results[newspaper] = {
                'overall': results,
                'event_level': event_results,
                'summary_table': analyzer.create_summary_table()
            }

        # Create combined tables
        self.create_combined_tables()

        # Create visualizations
        self.create_visualizations()

        print(f"\n{'='*80}")
        print("DIRECTIONAL ANALYSIS COMPLETE")
        print(f"{'='*80}\n")
        print(f"Results saved to: {self.output_dir}")

    def create_combined_tables(self):
        """Create combined comparison tables."""
        print(f"\n{'='*80}")
        print("CREATING COMBINED TABLES")
        print(f"{'='*80}\n")

        # Combine all summary tables
        all_summaries = []
        for newspaper, results in self.all_results.items():
            all_summaries.append(results['summary_table'])

        combined_df = pd.concat(all_summaries, ignore_index=True)

        # Save
        combined_path = self.output_dir / 'directional_perplexity_analysis.csv'
        combined_df.to_csv(combined_path, index=False)
        print(f"✅ Saved directional analysis: {combined_path}")

        # Print summary
        print(f"\n{combined_df.to_string(index=False)}")

        return combined_df

    def create_visualizations(self):
        """Create visualizations."""
        print(f"\n{'='*80}")
        print("CREATING VISUALIZATIONS")
        print(f"{'='*80}\n")

        df = pd.read_csv(self.output_dir / 'directional_perplexity_analysis.csv')

        # 1. Directional comparison
        self.plot_directional_comparison(df)

        # 2. Complexity ratio
        self.plot_complexity_ratios(df)

        # 3. Pattern diversity
        self.plot_pattern_diversity(df)

    def plot_directional_comparison(self, df: pd.DataFrame):
        """Plot directional perplexity comparison."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Directional Transformation Complexity', fontsize=16, fontweight='bold')

        # Filter to C→H and H→C only
        directional_df = df[df['Direction'].isin(['C→H', 'H→C'])]

        # 1. Perplexity comparison
        ax = axes[0, 0]
        pivot = directional_df.pivot(index='Direction', columns='Newspaper', values='Perplexity')
        pivot.plot(kind='bar', ax=ax, color=['#FF6B6B', '#4ECDC4', '#95E1D3'], alpha=0.8, width=0.7)
        ax.set_title('Perplexity by Direction', fontweight='bold')
        ax.set_xlabel('Direction', fontweight='bold')
        ax.set_ylabel('Perplexity', fontweight='bold')
        ax.legend(title='Newspaper')
        ax.grid(True, alpha=0.3)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=0)

        # 2. Normalized Perplexity
        ax = axes[0, 1]
        pivot_norm = directional_df.pivot(index='Direction', columns='Newspaper', values='Normalized_PP')
        pivot_norm.plot(kind='bar', ax=ax, color=['#FF6B6B', '#4ECDC4', '#95E1D3'], alpha=0.8, width=0.7)
        ax.set_title('Normalized Perplexity by Direction', fontweight='bold')
        ax.set_xlabel('Direction', fontweight='bold')
        ax.set_ylabel('Normalized Perplexity', fontweight='bold')
        ax.legend(title='Newspaper')
        ax.grid(True, alpha=0.3)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=0)

        # 3. Entropy comparison
        ax = axes[1, 0]
        pivot_ent = directional_df.pivot(index='Direction', columns='Newspaper', values='Entropy')
        pivot_ent.plot(kind='bar', ax=ax, color=['#FF6B6B', '#4ECDC4', '#95E1D3'], alpha=0.8, width=0.7)
        ax.set_title('Entropy by Direction', fontweight='bold')
        ax.set_xlabel('Direction', fontweight='bold')
        ax.set_ylabel('Entropy (bits)', fontweight='bold')
        ax.legend(title='Newspaper')
        ax.grid(True, alpha=0.3)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=0)

        # 4. Pattern count
        ax = axes[1, 1]
        pivot_patterns = directional_df.pivot(index='Direction', columns='Newspaper', values='Num_Patterns')
        pivot_patterns.plot(kind='bar', ax=ax, color=['#FF6B6B', '#4ECDC4', '#95E1D3'], alpha=0.8, width=0.7)
        ax.set_title('Number of Distinct Patterns', fontweight='bold')
        ax.set_xlabel('Direction', fontweight='bold')
        ax.set_ylabel('Pattern Count', fontweight='bold')
        ax.legend(title='Newspaper')
        ax.grid(True, alpha=0.3)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=0)

        plt.tight_layout()
        path = self.output_dir / 'directional_complexity_comparison.png'
        plt.savefig(path, dpi=200, bbox_inches='tight')
        plt.close()
        print(f"✅ Saved directional comparison: {path}")

    def plot_complexity_ratios(self, df: pd.DataFrame):
        """Plot complexity ratios between directions."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('C→H vs H→C Complexity Ratios', fontsize=16, fontweight='bold')

        # Calculate ratios
        ratios = []
        for newspaper in self.newspapers:
            c2h = df[(df['Newspaper'] == newspaper) & (df['Direction'] == 'C→H')]
            h2c = df[(df['Newspaper'] == newspaper) & (df['Direction'] == 'H→C')]

            if len(c2h) > 0 and len(h2c) > 0:
                pp_ratio = c2h['Perplexity'].values[0] / h2c['Perplexity'].values[0]
                ppnorm_ratio = c2h['Normalized_PP'].values[0] / h2c['Normalized_PP'].values[0]

                ratios.append({
                    'Newspaper': newspaper,
                    'PP_Ratio': pp_ratio,
                    'PP_Norm_Ratio': ppnorm_ratio
                })

        ratio_df = pd.DataFrame(ratios)

        # PP Ratio
        ax = axes[0]
        bars = ax.bar(range(len(ratio_df)), ratio_df['PP_Ratio'].values,
                      color=['#FF6B6B', '#4ECDC4', '#95E1D3'], alpha=0.8)
        ax.axhline(y=1.0, color='red', linestyle='--', linewidth=2, label='Equal Complexity')
        ax.set_xticks(range(len(ratio_df)))
        ax.set_xticklabels([n.replace('-', '\n') for n in ratio_df['Newspaper'].values])
        ax.set_ylabel('Ratio (C→H / H→C)', fontweight='bold')
        ax.set_title('Perplexity Ratio', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, ratio_df['PP_Ratio'].values)):
            ax.text(bar.get_x() + bar.get_width()/2, val, f'{val:.3f}',
                   ha='center', va='bottom', fontweight='bold')

        # PP Norm Ratio
        ax = axes[1]
        bars = ax.bar(range(len(ratio_df)), ratio_df['PP_Norm_Ratio'].values,
                      color=['#FF6B6B', '#4ECDC4', '#95E1D3'], alpha=0.8)
        ax.axhline(y=1.0, color='red', linestyle='--', linewidth=2, label='Equal Complexity')
        ax.set_xticks(range(len(ratio_df)))
        ax.set_xticklabels([n.replace('-', '\n') for n in ratio_df['Newspaper'].values])
        ax.set_ylabel('Ratio (C→H / H→C)', fontweight='bold')
        ax.set_title('Normalized Perplexity Ratio', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, ratio_df['PP_Norm_Ratio'].values)):
            ax.text(bar.get_x() + bar.get_width()/2, val, f'{val:.3f}',
                   ha='center', va='bottom', fontweight='bold')

        plt.tight_layout()
        path = self.output_dir / 'complexity_ratios.png'
        plt.savefig(path, dpi=200, bbox_inches='tight')
        plt.close()
        print(f"✅ Saved complexity ratios: {path}")

    def plot_pattern_diversity(self, df: pd.DataFrame):
        """Plot pattern diversity comparison."""
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        fig.suptitle('Pattern Diversity: C→H vs H→C', fontsize=16, fontweight='bold')

        directional_df = df[df['Direction'].isin(['C→H', 'H→C'])]

        # Scatter plot
        for newspaper in self.newspapers:
            data = directional_df[directional_df['Newspaper'] == newspaper]

            c2h_data = data[data['Direction'] == 'C→H']
            h2c_data = data[data['Direction'] == 'H→C']

            if len(c2h_data) > 0 and len(h2c_data) > 0:
                ax.scatter(c2h_data['Num_Patterns'].values[0],
                          h2c_data['Num_Patterns'].values[0],
                          s=200, label=newspaper, alpha=0.7)

        # Diagonal line
        max_val = directional_df['Num_Patterns'].max()
        ax.plot([0, max_val], [0, max_val], 'r--', linewidth=2, label='Equal Patterns')

        ax.set_xlabel('C→H Pattern Count', fontweight='bold')
        ax.set_ylabel('H→C Pattern Count', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        path = self.output_dir / 'pattern_diversity_comparison.png'
        plt.savefig(path, dpi=200, bbox_inches='tight')
        plt.close()
        print(f"✅ Saved pattern diversity: {path}")


if __name__ == '__main__':
    print("\n" + "="*80)
    print("DIRECTIONAL PERPLEXITY ANALYSIS")
    print("="*80)
    print("\nComparing transformation complexity in both directions:")
    print("  - C→H (Canonical → Headline): Reduction/Compression")
    print("  - H→C (Headline → Canonical): Expansion/Restoration")
    print("\nThis reveals which direction is inherently more difficult.")
    print("="*80 + "\n")

    analyzer = CrossNewspaperDirectionalAnalyzer()
    analyzer.run_all_newspapers()
