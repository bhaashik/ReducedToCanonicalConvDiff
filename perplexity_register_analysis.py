#!/usr/bin/env python3
"""
Perplexity-based Register Complexity Analysis.

Analyzes language complexity using perplexity in:
1. Mono-register contexts (event distributions within each register)
2. Cross-register contexts (transformation patterns)

Perplexity measures:
- Non-normalized: PP = 2^H where H = entropy
- Normalized: PP_norm = PP^(1/N) where N = vocabulary size

This reveals:
- Which register has higher intrinsic complexity
- How predictable transformations are
- Which event types contribute most to complexity
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
from typing import Dict, List, Tuple, Any
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 200
plt.rcParams['font.size'] = 10


class PerplexityCalculator:
    """Calculates perplexity metrics."""

    def entropy(self, probabilities: List[float]) -> float:
        """Calculate Shannon entropy: H = -∑ p(x) log₂ p(x)"""
        entropy = 0.0
        for p in probabilities:
            if p > 0:
                entropy -= p * np.log2(p)
        return entropy

    def perplexity(self, probabilities: List[float]) -> float:
        """Calculate perplexity: PP = 2^H"""
        H = self.entropy(probabilities)
        return 2 ** H

    def normalized_perplexity(self, probabilities: List[float], N: int) -> float:
        """Calculate normalized perplexity: PP_norm = PP^(1/N)"""
        PP = self.perplexity(probabilities)
        if N > 0:
            return PP ** (1.0 / N)
        return PP

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

        # Calculate metrics
        H = self.entropy(probabilities)
        PP = 2 ** H
        PP_norm = PP ** (1.0 / len(counter)) if len(counter) > 0 else PP

        return {
            'entropy': H,
            'perplexity': PP,
            'normalized_perplexity': PP_norm,
            'num_types': len(counter),  # Vocabulary size
            'num_tokens': total  # Total events
        }


class RegisterPerplexityAnalyzer:
    """Analyzes register complexity using perplexity."""

    def __init__(self, newspaper: str, project_root: Path):
        self.newspaper = newspaper
        self.project_root = project_root
        self.calculator = PerplexityCalculator()

        # Load data
        self.events_df = self.load_events_data()
        self.morph_df = self.load_morphological_rules()

        # Results storage
        self.results = {}

    def load_events_data(self) -> pd.DataFrame:
        """Load events data with direction tags (C2H/H2C)."""
        # Preferred: directional events generated into complexity-similarity-study/events
        directional_path = self.project_root / 'output' / 'complexity-similarity-study' / 'events' / f"{self.newspaper}_events.csv"
        fallback_path = self.project_root / 'output' / self.newspaper / 'events_global.csv'

        path_to_use = None
        if directional_path.exists():
            path_to_use = directional_path
        elif fallback_path.exists():
            path_to_use = fallback_path
        else:
            print(f"⚠️  Events file not found for {self.newspaper} (looked for {directional_path} and {fallback_path})")
            return pd.DataFrame()

        df = pd.read_csv(path_to_use)
        if 'Direction' not in df.columns:
            df['Direction'] = 'C2H'
        print(f"✅ Loaded {len(df)} events for {self.newspaper} from {path_to_use}")
        return df

    def load_morphological_rules(self) -> pd.DataFrame:
        """Load morphological rules."""
        morph_path = self.project_root / 'output' / self.newspaper / 'morphological_analysis' / 'morphological_rules.csv'

        if not morph_path.exists():
            return pd.DataFrame()

        df = pd.read_csv(morph_path)
        print(f"✅ Loaded {len(df)} morphological rules for {self.newspaper}")
        return df

    def analyze_mono_register_complexity(self) -> Dict:
        """
        Analyze mono-register complexity.

        Compares complexity within each register:
        - Event type distributions
        - Value distributions
        """
        print(f"\n{'='*80}")
        print(f"MONO-REGISTER COMPLEXITY ANALYSIS: {self.newspaper}")
        print(f"{'='*80}\n")

        results = {}

        # 1. Event type distribution (by Direction if available)
        if 'Direction' in self.events_df.columns:
            for direction, group in self.events_df.groupby('Direction'):
                event_types = Counter(group['feature_id'].values)
                key = f"event_types_{direction}"
                results[key] = self.calculator.calculate_distribution_perplexity(event_types)
                print(f"Event Type Distribution ({direction}):")
                print(f"  PP={results[key]['perplexity']:.3f}, "
                      f"PP_norm={results[key]['normalized_perplexity']:.3f}, "
                      f"Types={results[key]['num_types']}, "
                      f"Tokens={results[key]['num_tokens']}")
        else:
            event_types = Counter(self.events_df['feature_id'].values)
            results['event_types'] = self.calculator.calculate_distribution_perplexity(event_types)
            print(f"Event Type Distribution:")
            print(f"  PP={results['event_types']['perplexity']:.3f}, "
                  f"PP_norm={results['event_types']['normalized_perplexity']:.3f}, "
                  f"Types={results['event_types']['num_types']}, "
                  f"Tokens={results['event_types']['num_tokens']}")

        # 2/3. Register-specific value distributions (by Direction)
        if 'Direction' in self.events_df.columns:
            for direction, group in self.events_df.groupby('Direction'):
                canonical_values = Counter(group['canonical_value'].dropna().values)
                headline_values = Counter(group['headline_value'].dropna().values)
                results[f'canonical_values_{direction}'] = self.calculator.calculate_distribution_perplexity(canonical_values)
                results[f'headline_values_{direction}'] = self.calculator.calculate_distribution_perplexity(headline_values)
                print(f"\nCanonical Value Distribution ({direction}):")
                print(f"  PP={results[f'canonical_values_{direction}']['perplexity']:.3f}, "
                      f"PP_norm={results[f'canonical_values_{direction}']['normalized_perplexity']:.3f}, "
                      f"Types={results[f'canonical_values_{direction}']['num_types']}")
                print(f"\nHeadline Value Distribution ({direction}):")
                print(f"  PP={results[f'headline_values_{direction}']['perplexity']:.3f}, "
                      f"PP_norm={results[f'headline_values_{direction}']['normalized_perplexity']:.3f}, "
                      f"Types={results[f'headline_values_{direction}']['num_types']}")
        else:
            canonical_values = Counter(self.events_df['canonical_value'].dropna().values)
            results['canonical_values'] = self.calculator.calculate_distribution_perplexity(canonical_values)
            print(f"\nCanonical Value Distribution:")
            print(f"  PP={results['canonical_values']['perplexity']:.3f}, "
                  f"PP_norm={results['canonical_values']['normalized_perplexity']:.3f}, "
                  f"Types={results['canonical_values']['num_types']}")

            headline_values = Counter(self.events_df['headline_value'].dropna().values)
            results['headline_values'] = self.calculator.calculate_distribution_perplexity(headline_values)
            print(f"\nHeadline Value Distribution:")
            print(f"  PP={results['headline_values']['perplexity']:.3f}, "
                  f"PP_norm={results['headline_values']['normalized_perplexity']:.3f}, "
                  f"Types={results['headline_values']['num_types']}")

        self.results['mono_register'] = results
        return results

    def analyze_cross_register_complexity(self) -> Dict:
        """
        Analyze cross-register transformation complexity.

        Measures:
        - Transformation pattern diversity
        - Predictability of transformations
        """
        print(f"\n{'='*80}")
        print(f"CROSS-REGISTER TRANSFORMATION COMPLEXITY: {self.newspaper}")
        print(f"{'='*80}\n")

        results = {}

        # 1. Value transformation patterns (canonical_value → headline_value)
        transformations = Counter()
        for _, row in self.events_df.iterrows():
            c_val = str(row.get('canonical_value', 'NULL'))
            h_val = str(row.get('headline_value', 'NULL'))
            transformations[f"{c_val}→{h_val}"] += 1

        results['value_transformations'] = self.calculator.calculate_distribution_perplexity(transformations)

        print(f"Value Transformation Patterns:")
        print(f"  PP={results['value_transformations']['perplexity']:.3f}, "
              f"PP_norm={results['value_transformations']['normalized_perplexity']:.3f}, "
              f"Patterns={results['value_transformations']['num_types']}")

        # 2. Feature-specific transformations
        feature_transformations = Counter()
        for _, row in self.events_df.iterrows():
            feature = row.get('feature_id', 'UNKNOWN')
            c_val = str(row.get('canonical_value', 'NULL'))
            h_val = str(row.get('headline_value', 'NULL'))
            feature_transformations[f"{feature}:{c_val}→{h_val}"] += 1

        results['feature_transformations'] = self.calculator.calculate_distribution_perplexity(feature_transformations)

        print(f"\nFeature-Specific Transformations:")
        print(f"  PP={results['feature_transformations']['perplexity']:.3f}, "
              f"PP_norm={results['feature_transformations']['normalized_perplexity']:.3f}, "
              f"Patterns={results['feature_transformations']['num_types']}")

        # 3. Morphological transformations (if available)
        if not self.morph_df.empty:
            morph_transformations = Counter()
            for _, row in self.morph_df.iterrows():
                pos_val = row.get('pos', 'NA')
                pattern = f"{row.get('feature', 'UNK')}:{row.get('headline_value', 'NULL')}→{row.get('canonical_value', 'NULL')}@{pos_val}"
                freq = row.get('frequency', 0)
                morph_transformations[pattern] = freq

            results['morph_transformations'] = self.calculator.calculate_distribution_perplexity(morph_transformations)

            print(f"\nMorphological Transformations:")
            print(f"  PP={results['morph_transformations']['perplexity']:.3f}, "
                  f"PP_norm={results['morph_transformations']['normalized_perplexity']:.3f}, "
                  f"Patterns={results['morph_transformations']['num_types']}")

        self.results['cross_register'] = results
        return results

    def analyze_event_level_complexity(self) -> Dict:
        """Analyze complexity for each event type."""
        print(f"\n{'='*80}")
        print(f"EVENT-LEVEL COMPLEXITY ANALYSIS: {self.newspaper}")
        print(f"{'='*80}\n")

        results = {}

        # Group by feature_id
        grouped = self.events_df.groupby('feature_id')

        for feature_id, group in grouped:
            # Transformation patterns for this feature
            transformations = Counter()
            for _, row in group.iterrows():
                c_val = str(row.get('canonical_value', 'NULL'))
                h_val = str(row.get('headline_value', 'NULL'))
                transformations[f"{c_val}→{h_val}"] += 1

            metrics = self.calculator.calculate_distribution_perplexity(transformations)
            results[feature_id] = {
                'count': len(group),
                **metrics
            }

            print(f"{feature_id:20s}: Count={len(group):5d}, "
                  f"PP={metrics['perplexity']:7.3f}, "
                  f"PP_norm={metrics['normalized_perplexity']:6.3f}, "
                  f"Patterns={metrics['num_types']:4d}")

        self.results['event_level'] = results
        return results

    def create_summary_table(self) -> pd.DataFrame:
        """Create comprehensive summary table."""
        rows = []

        # Mono-register
        if 'mono_register' in self.results:
            for aspect, data in self.results['mono_register'].items():
                rows.append({
                    'Newspaper': self.newspaper,
                    'Analysis_Type': 'Mono-Register',
                    'Aspect': aspect.replace('_', ' ').title(),
                    'Perplexity': data['perplexity'],
                    'Normalized_PP': data['normalized_perplexity'],
                    'Entropy': data['entropy'],
                    'Num_Types': data['num_types'],
                    'Num_Tokens': data['num_tokens']
                })

        # Cross-register
        if 'cross_register' in self.results:
            for aspect, data in self.results['cross_register'].items():
                rows.append({
                    'Newspaper': self.newspaper,
                    'Analysis_Type': 'Cross-Register',
                    'Aspect': aspect.replace('_', ' ').title(),
                    'Perplexity': data['perplexity'],
                    'Normalized_PP': data['normalized_perplexity'],
                    'Entropy': data['entropy'],
                    'Num_Types': data['num_types'],
                    'Num_Tokens': data['num_tokens']
                })

        return pd.DataFrame(rows)

    def run_complete_analysis(self) -> Dict:
        """Run all analyses."""
        self.analyze_mono_register_complexity()
        self.analyze_cross_register_complexity()
        self.analyze_event_level_complexity()

        summary_df = self.create_summary_table()

        return {
            'mono_register': self.results.get('mono_register', {}),
            'cross_register': self.results.get('cross_register', {}),
            'event_level': self.results.get('event_level', {}),
            'summary_table': summary_df
        }


class CrossNewspaperPerplexityAnalyzer:
    """Analyzes perplexity across newspapers."""

    def __init__(self):
        self.newspapers = ['Times-of-India', 'Hindustan-Times', 'The-Hindu']
        self.project_root = Path(__file__).parent.absolute()
        self.output_dir = self.project_root / 'output' / 'perplexity_analysis'
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.all_results = {}

    def run_all_newspapers(self):
        """Run perplexity analysis on all newspapers."""
        print(f"\n{'='*80}")
        print("CROSS-NEWSPAPER PERPLEXITY ANALYSIS")
        print(f"{'='*80}\n")

        for newspaper in self.newspapers:
            analyzer = RegisterPerplexityAnalyzer(newspaper, self.project_root)
            results = analyzer.run_complete_analysis()
            self.all_results[newspaper] = results

        # Create combined tables
        self.create_combined_tables()

        # Create visualizations
        self.create_visualizations()

        print(f"\n{'='*80}")
        print("ANALYSIS COMPLETE")
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

        # Save complete table
        combined_path = self.output_dir / 'perplexity_complete_analysis.csv'
        combined_df.to_csv(combined_path, index=False)
        print(f"✅ Saved complete analysis: {combined_path}")

        # Create detailed event-level table
        event_rows = []
        for newspaper, results in self.all_results.items():
            for event_type, metrics in results['event_level'].items():
                event_rows.append({
                    'Newspaper': newspaper,
                    'Event_Type': event_type,
                    'Count': metrics['count'],
                    'Perplexity': metrics['perplexity'],
                    'Normalized_PP': metrics['normalized_perplexity'],
                    'Entropy': metrics['entropy'],
                    'Num_Patterns': metrics['num_types']
                })

        event_df = pd.DataFrame(event_rows)
        event_path = self.output_dir / 'event_level_perplexity.csv'
        event_df.to_csv(event_path, index=False)
        print(f"✅ Saved event-level analysis: {event_path}")

        return combined_df

    def create_visualizations(self):
        """Create comprehensive visualizations."""
        print(f"\n{'='*80}")
        print("CREATING VISUALIZATIONS")
        print(f"{'='*80}\n")

        # Load data
        combined_df = pd.read_csv(self.output_dir / 'perplexity_complete_analysis.csv')
        event_df = pd.read_csv(self.output_dir / 'event_level_perplexity.csv')

        # 1. Mono vs Cross-register comparison
        self.plot_mono_vs_cross_comparison(combined_df)

        # 2. Detailed aspect comparison
        self.plot_detailed_aspect_comparison(combined_df)

        # 3. Event-level complexity
        self.plot_event_level_complexity(event_df)

        # 4. Complexity heatmaps
        self.plot_complexity_heatmaps(combined_df)

        # 5. Normalized vs Non-normalized
        self.plot_normalization_effects(combined_df)

    def plot_mono_vs_cross_comparison(self, df: pd.DataFrame):
        """Plot mono-register vs cross-register comparison."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Mono-Register vs Cross-Register Complexity', fontsize=16, fontweight='bold')

        # Perplexity
        ax = axes[0]
        pivot = df.pivot_table(index='Analysis_Type', columns='Newspaper', values='Perplexity', aggfunc='mean')
        pivot.plot(kind='bar', ax=ax, color=['#FF6B6B', '#4ECDC4', '#95E1D3'], alpha=0.8)
        ax.set_title('Average Perplexity', fontweight='bold')
        ax.set_xlabel('Analysis Type', fontweight='bold')
        ax.set_ylabel('Perplexity', fontweight='bold')
        ax.legend(title='Newspaper')
        ax.grid(True, alpha=0.3)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=0)

        # Normalized Perplexity
        ax = axes[1]
        pivot_norm = df.pivot_table(index='Analysis_Type', columns='Newspaper', values='Normalized_PP', aggfunc='mean')
        pivot_norm.plot(kind='bar', ax=ax, color=['#FF6B6B', '#4ECDC4', '#95E1D3'], alpha=0.8)
        ax.set_title('Average Normalized Perplexity', fontweight='bold')
        ax.set_xlabel('Analysis Type', fontweight='bold')
        ax.set_ylabel('Normalized Perplexity', fontweight='bold')
        ax.legend(title='Newspaper')
        ax.grid(True, alpha=0.3)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=0)

        plt.tight_layout()
        path = self.output_dir / 'mono_vs_cross_register_comparison.png'
        plt.savefig(path, dpi=200, bbox_inches='tight')
        plt.close()
        print(f"✅ Saved mono vs cross comparison: {path}")

    def plot_detailed_aspect_comparison(self, df: pd.DataFrame):
        """Plot detailed aspect-by-aspect comparison."""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Detailed Aspect-Level Complexity Analysis', fontsize=16, fontweight='bold')

        # 1. Mono-register aspects
        ax = axes[0, 0]
        mono_df = df[df['Analysis_Type'] == 'Mono-Register']
        if not mono_df.empty:
            pivot = mono_df.pivot(index='Aspect', columns='Newspaper', values='Normalized_PP')
            pivot.plot(kind='barh', ax=ax, color=['#FF6B6B', '#4ECDC4', '#95E1D3'], alpha=0.8)
            ax.set_title('Mono-Register Complexity by Aspect', fontweight='bold')
            ax.set_xlabel('Normalized Perplexity', fontweight='bold')
            ax.legend(title='Newspaper')
            ax.grid(True, alpha=0.3, axis='x')

        # 2. Cross-register aspects
        ax = axes[0, 1]
        cross_df = df[df['Analysis_Type'] == 'Cross-Register']
        if not cross_df.empty:
            pivot = cross_df.pivot(index='Aspect', columns='Newspaper', values='Normalized_PP')
            pivot.plot(kind='barh', ax=ax, color=['#FF6B6B', '#4ECDC4', '#95E1D3'], alpha=0.8)
            ax.set_title('Cross-Register Complexity by Aspect', fontweight='bold')
            ax.set_xlabel('Normalized Perplexity', fontweight='bold')
            ax.legend(title='Newspaper')
            ax.grid(True, alpha=0.3, axis='x')

        # 3. Entropy comparison
        ax = axes[1, 0]
        pivot_entropy = df.pivot_table(index='Aspect', columns='Newspaper', values='Entropy', aggfunc='mean')
        sns.heatmap(pivot_entropy, annot=True, fmt='.2f', cmap='YlOrRd', ax=ax,
                   cbar_kws={'label': 'Entropy (bits)'})
        ax.set_title('Entropy by Aspect', fontweight='bold')

        # 4. Vocabulary size comparison
        ax = axes[1, 1]
        pivot_types = df.pivot_table(index='Aspect', columns='Newspaper', values='Num_Types', aggfunc='mean')
        sns.heatmap(pivot_types, annot=True, fmt='.0f', cmap='Blues', ax=ax,
                   cbar_kws={'label': 'Vocabulary Size'})
        ax.set_title('Vocabulary Size by Aspect', fontweight='bold')

        plt.tight_layout()
        path = self.output_dir / 'detailed_aspect_comparison.png'
        plt.savefig(path, dpi=200, bbox_inches='tight')
        plt.close()
        print(f"✅ Saved detailed aspect comparison: {path}")

    def plot_event_level_complexity(self, event_df: pd.DataFrame):
        """Plot event-level complexity."""
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('Event-Level Complexity by Newspaper', fontsize=16, fontweight='bold')

        for idx, newspaper in enumerate(self.newspapers):
            ax = axes[idx]

            # Filter for this newspaper and top events
            data = event_df[event_df['Newspaper'] == newspaper].nlargest(15, 'Count')

            if not data.empty:
                # Create bar plot
                colors = plt.cm.viridis(data['Count'].values / data['Count'].max())
                bars = ax.barh(range(len(data)), data['Normalized_PP'].values, color=colors, alpha=0.8)

                ax.set_yticks(range(len(data)))
                ax.set_yticklabels(data['Event_Type'].values, fontsize=9)
                ax.set_xlabel('Normalized Perplexity', fontweight='bold')
                ax.set_title(newspaper.replace('-', ' '), fontweight='bold')
                ax.grid(True, alpha=0.3, axis='x')

                # Add count labels
                for i, (bar, count) in enumerate(zip(bars, data['Count'].values)):
                    ax.text(bar.get_width(), i, f' {count}',
                           va='center', fontsize=7, alpha=0.7)

        plt.tight_layout()
        path = self.output_dir / 'event_level_complexity.png'
        plt.savefig(path, dpi=200, bbox_inches='tight')
        plt.close()
        print(f"✅ Saved event-level complexity: {path}")

    def plot_complexity_heatmaps(self, df: pd.DataFrame):
        """Create complexity heatmaps."""
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle('Register Complexity Heatmaps', fontsize=16, fontweight='bold')

        # Perplexity heatmap
        ax = axes[0]
        pivot = df.pivot_table(index=['Analysis_Type', 'Aspect'], columns='Newspaper', values='Perplexity')
        sns.heatmap(pivot, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax,
                   cbar_kws={'label': 'Perplexity'})
        ax.set_title('Perplexity Heatmap', fontweight='bold')

        # Normalized Perplexity heatmap
        ax = axes[1]
        pivot_norm = df.pivot_table(index=['Analysis_Type', 'Aspect'], columns='Newspaper', values='Normalized_PP')
        sns.heatmap(pivot_norm, annot=True, fmt='.3f', cmap='YlGnBu', ax=ax,
                   cbar_kws={'label': 'Normalized Perplexity'})
        ax.set_title('Normalized Perplexity Heatmap', fontweight='bold')

        plt.tight_layout()
        path = self.output_dir / 'complexity_heatmaps.png'
        plt.savefig(path, dpi=200, bbox_inches='tight')
        plt.close()
        print(f"✅ Saved complexity heatmaps: {path}")

    def plot_normalization_effects(self, df: pd.DataFrame):
        """Plot effects of normalization."""
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))
        fig.suptitle('Normalization Effects on Perplexity', fontsize=16, fontweight='bold')

        # Scatter plot
        colors = {'Times-of-India': '#FF6B6B', 'Hindustan-Times': '#4ECDC4', 'The-Hindu': '#95E1D3'}
        markers = {'Mono-Register': 'o', 'Cross-Register': 's'}

        for newspaper in self.newspapers:
            for analysis_type in ['Mono-Register', 'Cross-Register']:
                data = df[(df['Newspaper'] == newspaper) & (df['Analysis_Type'] == analysis_type)]
                ax.scatter(data['Perplexity'], data['Normalized_PP'],
                          label=f'{newspaper.replace("-", " ")} - {analysis_type}',
                          color=colors[newspaper], marker=markers[analysis_type],
                          s=100, alpha=0.7)

        ax.set_xlabel('Perplexity (Non-Normalized)', fontweight='bold')
        ax.set_ylabel('Normalized Perplexity', fontweight='bold')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        path = self.output_dir / 'normalization_effects.png'
        plt.savefig(path, dpi=200, bbox_inches='tight')
        plt.close()
        print(f"✅ Saved normalization effects: {path}")


if __name__ == '__main__':
    print("\n" + "="*80)
    print("PERPLEXITY-BASED REGISTER COMPLEXITY ANALYSIS")
    print("="*80)
    print("\nAnalyzing language complexity using perplexity:")
    print("  - Mono-register: Complexity within same register")
    print("  - Cross-register: Transformation complexity")
    print("  - Event-level: Perplexity by event type")
    print("\nMetrics:")
    print("  - Perplexity: 2^H (higher = more complex/less predictable)")
    print("  - Normalized Perplexity: PP^(1/N) (normalized by vocabulary size)")
    print("  - Entropy: -∑ p(x) log₂ p(x)")
    print("="*80 + "\n")

    analyzer = CrossNewspaperPerplexityAnalyzer()
    analyzer.run_all_newspapers()
