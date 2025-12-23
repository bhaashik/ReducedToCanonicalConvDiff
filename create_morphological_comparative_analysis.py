#!/usr/bin/env python3
"""
Create comprehensive morphological features comparative analysis across newspapers.

This script integrates morphological transformations into the comparative analysis,
creating tables and visualizations comparing morphological patterns across newspapers.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Any
import numpy as np

class MorphologicalComparativeAnalyzer:
    """Comprehensive morphological features comparison across newspapers."""

    def __init__(self):
        self.newspapers = ['Times-of-India', 'Hindustan-Times', 'The-Hindu']
        self.morphological_data = {}
        self.comparative_tables = {}
        self.project_root = Path(__file__).parent.absolute()
        self.output_dir = self.project_root / 'output' / 'morphological_comparative_analysis'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_morphological_analyses(self):
        """Load morphological analysis for all newspapers."""
        print(f"\n{'='*80}")
        print("LOADING MORPHOLOGICAL ANALYSES")
        print(f"{'='*80}\n")

        for newspaper in self.newspapers:
            morph_path = self.project_root / 'output' / newspaper / 'morphological_analysis' / 'morphological_analysis.json'

            if morph_path.exists():
                with open(morph_path, 'r') as f:
                    self.morphological_data[newspaper] = json.load(f)
                print(f"✅ Loaded {newspaper}")
            else:
                print(f"❌ Missing {newspaper}: {morph_path}")

        print(f"\nLoaded data for {len(self.morphological_data)} newspapers")

    def create_overall_statistics_table(self) -> pd.DataFrame:
        """Create overall morphological statistics comparison table."""
        print(f"\n{'='*80}")
        print("CREATING OVERALL STATISTICS TABLE")
        print(f"{'='*80}\n")

        rows = []
        for newspaper in self.newspapers:
            if newspaper not in self.morphological_data:
                continue

            data = self.morphological_data[newspaper]
            morph_sys = data.get('morph_systematicity', {})

            # Calculate totals from morph_systematicity
            total_morph = 0
            verb_morph = 0
            noun_morph = 0

            verb_features = ['VerbForm', 'Tense', 'Aspect', 'Mood', 'Voice']
            noun_features = ['Number', 'Case', 'Definite', 'Gender']

            for feature, feature_data in morph_sys.items():
                feature_total = feature_data.get('total_instances', 0)
                total_morph += feature_total

                # Count as verb if it's a verb feature OR patterns are mostly @VERB
                if feature in verb_features:
                    # Check if patterns are for VERB POS
                    verb_count = 0
                    for pattern_info in feature_data.get('top_patterns', []):
                        pattern = pattern_info['pattern']
                        if '@VERB' in pattern:
                            verb_count += pattern_info['frequency']
                    verb_morph += verb_count

                # Count as noun if it's a noun feature OR patterns are mostly @NOUN/@PROPN
                if feature in noun_features:
                    noun_count = 0
                    for pattern_info in feature_data.get('top_patterns', []):
                        pattern = pattern_info['pattern']
                        if '@NOUN' in pattern or '@PROPN' in pattern:
                            noun_count += pattern_info['frequency']
                    noun_morph += noun_count

            other_morph = total_morph - verb_morph - noun_morph

            # Load total events from enhanced systematicity if available
            sys_path = self.project_root / 'output' / newspaper / 'rule_analysis' / 'enhanced_systematicity.json'
            total_events = 0
            if sys_path.exists():
                with open(sys_path, 'r') as f:
                    sys_data = json.load(f)
                    total_events = sys_data.get('total_events', total_morph)

            row = {
                'Newspaper': newspaper,
                'Total Events': total_events if total_events > 0 else total_morph,
                'Morph Changes': total_morph,
                'Morph %': f"{100*total_morph/total_events if total_events > 0 else 0:.1f}%",
                'Verb Morph': verb_morph,
                'Verb %': f"{100*verb_morph/total_events if total_events > 0 else 0:.1f}%",
                'Noun Morph': noun_morph,
                'Noun %': f"{100*noun_morph/total_events if total_events > 0 else 0:.1f}%",
                'Other Morph': other_morph,
            }
            rows.append(row)

        df = pd.DataFrame(rows)

        # Add totals row
        if len(rows) > 0:
            total_events = sum(int(r['Total Events']) for r in rows)
            total_morph = sum(int(r['Morph Changes']) for r in rows)
            total_verb = sum(int(r['Verb Morph']) for r in rows)
            total_noun = sum(int(r['Noun Morph']) for r in rows)
            total_other = sum(int(r['Other Morph']) for r in rows)

            totals = {
                'Newspaper': 'TOTAL',
                'Total Events': total_events,
                'Morph Changes': total_morph,
                'Morph %': f"{100*total_morph/total_events if total_events > 0 else 0:.1f}%",
                'Verb Morph': total_verb,
                'Verb %': f"{100*total_verb/total_events if total_events > 0 else 0:.1f}%",
                'Noun Morph': total_noun,
                'Noun %': f"{100*total_noun/total_events if total_events > 0 else 0:.1f}%",
                'Other Morph': total_other,
            }
            df = pd.concat([df, pd.DataFrame([totals])], ignore_index=True)

        # Save
        csv_path = self.output_dir / 'overall_morphological_statistics.csv'
        df.to_csv(csv_path, index=False)
        print(f"✅ Saved to: {csv_path}")

        self.comparative_tables['overall_statistics'] = df
        return df

    def create_verb_morphology_table(self) -> pd.DataFrame:
        """Create detailed verb morphology comparison table."""
        print(f"\n{'='*80}")
        print("CREATING VERB MORPHOLOGY TABLE")
        print(f"{'='*80}\n")

        # Collect all verb transformations
        all_transformations = defaultdict(lambda: defaultdict(int))

        for newspaper in self.newspapers:
            if newspaper not in self.morphological_data:
                continue

            data = self.morphological_data[newspaper]
            morph_sys = data.get('morph_systematicity', {})

            # Extract verb-related features
            verb_features = ['VerbForm', 'Tense', 'Aspect', 'Mood', 'Voice']

            for feature in verb_features:
                if feature not in morph_sys:
                    continue

                feature_data = morph_sys[feature]
                for pattern_info in feature_data.get('top_patterns', []):
                    pattern = pattern_info['pattern']
                    frequency = pattern_info['frequency']

                    # Parse pattern: "Feature::h_value→c_value@POS"
                    try:
                        parts = pattern.split('::')
                        if len(parts) != 2:
                            continue

                        feature_name = parts[0]
                        transformation_and_pos = parts[1].split('@')
                        if len(transformation_and_pos) != 2:
                            continue

                        transformation = transformation_and_pos[0]
                        pos = transformation_and_pos[1]

                        # Only include VERB transformations
                        if pos == 'VERB':
                            key = f"{feature_name}::{transformation}"
                            all_transformations[key][newspaper] = frequency
                    except:
                        continue

        # Create DataFrame
        rows = []
        for key, newspaper_counts in sorted(all_transformations.items(),
                                           key=lambda x: sum(x[1].values()),
                                           reverse=True):
            trans_type, trans = key.split('::', 1)

            row = {
                'Feature': trans_type,
                'Transformation': trans,
                'Times-of-India': newspaper_counts.get('Times-of-India', 0),
                'Hindustan-Times': newspaper_counts.get('Hindustan-Times', 0),
                'The-Hindu': newspaper_counts.get('The-Hindu', 0),
                'Total': sum(newspaper_counts.values())
            }
            rows.append(row)

        df = pd.DataFrame(rows)

        # Save
        csv_path = self.output_dir / 'verb_morphology_comparison.csv'
        df.to_csv(csv_path, index=False)
        print(f"✅ Saved to: {csv_path}")
        print(f"   {len(df)} unique verb transformations")

        self.comparative_tables['verb_morphology'] = df
        return df

    def create_noun_morphology_table(self) -> pd.DataFrame:
        """Create detailed noun morphology comparison table."""
        print(f"\n{'='*80}")
        print("CREATING NOUN MORPHOLOGY TABLE")
        print(f"{'='*80}\n")

        # Collect all noun transformations
        all_transformations = defaultdict(lambda: defaultdict(int))

        for newspaper in self.newspapers:
            if newspaper not in self.morphological_data:
                continue

            data = self.morphological_data[newspaper]
            morph_sys = data.get('morph_systematicity', {})

            # Extract noun-related features
            noun_features = ['Number', 'Case', 'Definite', 'Gender']

            for feature in noun_features:
                if feature not in morph_sys:
                    continue

                feature_data = morph_sys[feature]
                for pattern_info in feature_data.get('top_patterns', []):
                    pattern = pattern_info['pattern']
                    frequency = pattern_info['frequency']

                    # Parse pattern: "Feature::h_value→c_value@POS"
                    try:
                        parts = pattern.split('::')
                        if len(parts) != 2:
                            continue

                        feature_name = parts[0]
                        transformation_and_pos = parts[1].split('@')
                        if len(transformation_and_pos) != 2:
                            continue

                        transformation = transformation_and_pos[0]
                        pos = transformation_and_pos[1]

                        # Only include NOUN and PROPN transformations
                        if pos in ['NOUN', 'PROPN']:
                            key = f"{feature_name}::{transformation}@{pos}"
                            all_transformations[key][newspaper] = frequency
                    except:
                        continue

        # Create DataFrame
        rows = []
        for key, newspaper_counts in sorted(all_transformations.items(),
                                           key=lambda x: sum(x[1].values()),
                                           reverse=True):
            trans_type, trans = key.split('::', 1)

            row = {
                'Feature': trans_type,
                'Transformation': trans,
                'Times-of-India': newspaper_counts.get('Times-of-India', 0),
                'Hindustan-Times': newspaper_counts.get('Hindustan-Times', 0),
                'The-Hindu': newspaper_counts.get('The-Hindu', 0),
                'Total': sum(newspaper_counts.values())
            }
            rows.append(row)

        df = pd.DataFrame(rows)

        # Save
        csv_path = self.output_dir / 'noun_morphology_comparison.csv'
        df.to_csv(csv_path, index=False)
        print(f"✅ Saved to: {csv_path}")
        print(f"   {len(df)} unique noun transformations")

        self.comparative_tables['noun_morphology'] = df
        return df

    def create_morphological_feature_summary(self) -> pd.DataFrame:
        """Create summary table of morphological features by type."""
        print(f"\n{'='*80}")
        print("CREATING MORPHOLOGICAL FEATURE SUMMARY")
        print(f"{'='*80}\n")

        features = ['VerbForm', 'Tense', 'Aspect', 'Mood', 'Voice', 'Person', 'Number', 'Case', 'Definite']

        rows = []
        for newspaper in self.newspapers:
            if newspaper not in self.morphological_data:
                continue

            data = self.morphological_data[newspaper]
            morph_sys = data.get('morph_systematicity', {})

            row = {'Newspaper': newspaper}

            for feature in features:
                if feature in morph_sys:
                    row[feature] = morph_sys[feature].get('total_instances', 0)
                else:
                    row[feature] = 0

            rows.append(row)

        df = pd.DataFrame(rows)

        # Add totals row
        if len(rows) > 0:
            totals = {'Newspaper': 'TOTAL'}
            for feature in features:
                totals[feature] = df[feature].sum()
            df = pd.concat([df, pd.DataFrame([totals])], ignore_index=True)

        # Save
        csv_path = self.output_dir / 'morphological_features_summary.csv'
        df.to_csv(csv_path, index=False)
        print(f"✅ Saved to: {csv_path}")

        self.comparative_tables['feature_summary'] = df
        return df

    def create_systematicity_comparison_table(self) -> pd.DataFrame:
        """Create table comparing systematicity across morphological features."""
        print(f"\n{'='*80}")
        print("CREATING SYSTEMATICITY COMPARISON TABLE")
        print(f"{'='*80}\n")

        rows = []
        for newspaper in self.newspapers:
            if newspaper not in self.morphological_data:
                continue

            data = self.morphological_data[newspaper]
            morph_sys = data.get('morph_systematicity', {})

            for feature, feature_data in morph_sys.items():
                row = {
                    'Newspaper': newspaper,
                    'Feature': feature,
                    'Transformations': feature_data.get('total_transformations', 0),
                    'Unique Patterns': feature_data.get('unique_patterns', 0),
                    'Avg Consistency': f"{feature_data.get('avg_consistency', 0):.1%}",
                    'Top Pattern': '',
                    'Top Frequency': 0
                }

                top_patterns = feature_data.get('top_patterns', [])
                if top_patterns:
                    row['Top Pattern'] = top_patterns[0].get('pattern', '')
                    row['Top Frequency'] = top_patterns[0].get('frequency', 0)

                rows.append(row)

        df = pd.DataFrame(rows)
        df = df.sort_values(['Feature', 'Transformations'], ascending=[True, False])

        # Save
        csv_path = self.output_dir / 'morphological_systematicity.csv'
        df.to_csv(csv_path, index=False)
        print(f"✅ Saved to: {csv_path}")
        print(f"   {len(df)} feature-newspaper combinations")

        self.comparative_tables['systematicity'] = df
        return df

    def visualize_overall_statistics(self):
        """Create visualization of overall morphological statistics."""
        print(f"\n{'='*80}")
        print("CREATING OVERALL STATISTICS VISUALIZATION")
        print(f"{'='*80}\n")

        df = self.comparative_tables.get('overall_statistics')
        if df is None or len(df) == 0:
            print("⚠️  No data available")
            return

        # Remove totals row for visualization
        df_plot = df[df['Newspaper'] != 'TOTAL'].copy()

        # Create figure with 2x2 subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Morphological Transformations: Cross-Newspaper Comparison',
                     fontsize=16, fontweight='bold')

        # 1. Total Events and Morphological Changes
        ax1 = axes[0, 0]
        x = np.arange(len(df_plot))
        width = 0.35

        ax1.bar(x - width/2, df_plot['Total Events'], width,
                label='Total Events', color='steelblue', alpha=0.8)
        ax1.bar(x + width/2, df_plot['Morph Changes'], width,
                label='Morphological Changes', color='coral', alpha=0.8)

        ax1.set_xlabel('Newspaper', fontweight='bold')
        ax1.set_ylabel('Number of Events', fontweight='bold')
        ax1.set_title('Total Events vs Morphological Changes')
        ax1.set_xticks(x)
        ax1.set_xticklabels(df_plot['Newspaper'], rotation=45, ha='right')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)

        # 2. Morphological Percentage
        ax2 = axes[0, 1]
        morph_pct = [float(p.rstrip('%')) for p in df_plot['Morph %']]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']

        bars = ax2.barh(df_plot['Newspaper'], morph_pct, color=colors, alpha=0.8)
        ax2.set_xlabel('Percentage of Events', fontweight='bold')
        ax2.set_title('Morphological Changes as % of Total Events')
        ax2.grid(axis='x', alpha=0.3)

        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, morph_pct)):
            ax2.text(val + 1, i, f'{val:.1f}%', va='center', fontweight='bold')

        # 3. Verb vs Noun vs Other Morphology
        ax3 = axes[1, 0]

        categories = ['Verb Morph', 'Noun Morph', 'Other Morph']
        x = np.arange(len(df_plot))
        width = 0.25

        ax3.bar(x - width, df_plot['Verb Morph'], width,
                label='Verb', color='#FF6B6B', alpha=0.8)
        ax3.bar(x, df_plot['Noun Morph'], width,
                label='Noun', color='#4ECDC4', alpha=0.8)
        ax3.bar(x + width, df_plot['Other Morph'], width,
                label='Other', color='#95E1D3', alpha=0.8)

        ax3.set_xlabel('Newspaper', fontweight='bold')
        ax3.set_ylabel('Number of Changes', fontweight='bold')
        ax3.set_title('Morphological Changes by Category')
        ax3.set_xticks(x)
        ax3.set_xticklabels(df_plot['Newspaper'], rotation=45, ha='right')
        ax3.legend()
        ax3.grid(axis='y', alpha=0.3)

        # 4. Stacked percentage breakdown
        ax4 = axes[1, 1]

        # Calculate percentages
        verb_pct = 100 * df_plot['Verb Morph'] / df_plot['Morph Changes']
        noun_pct = 100 * df_plot['Noun Morph'] / df_plot['Morph Changes']
        other_pct = 100 * df_plot['Other Morph'] / df_plot['Morph Changes']

        x = np.arange(len(df_plot))

        ax4.bar(x, verb_pct, label='Verb', color='#FF6B6B', alpha=0.8)
        ax4.bar(x, noun_pct, bottom=verb_pct,
                label='Noun', color='#4ECDC4', alpha=0.8)
        ax4.bar(x, other_pct, bottom=verb_pct + noun_pct,
                label='Other', color='#95E1D3', alpha=0.8)

        ax4.set_xlabel('Newspaper', fontweight='bold')
        ax4.set_ylabel('Percentage', fontweight='bold')
        ax4.set_title('Morphological Changes: Category Distribution')
        ax4.set_xticks(x)
        ax4.set_xticklabels(df_plot['Newspaper'], rotation=45, ha='right')
        ax4.set_ylim([0, 100])
        ax4.legend(loc='upper right')
        ax4.grid(axis='y', alpha=0.3)

        plt.tight_layout()

        # Save
        output_path = self.output_dir / 'overall_morphological_statistics.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✅ Saved to: {output_path}")

    def visualize_verb_morphology(self):
        """Create visualization of verb morphology patterns."""
        print(f"\n{'='*80}")
        print("CREATING VERB MORPHOLOGY VISUALIZATION")
        print(f"{'='*80}\n")

        df = self.comparative_tables.get('verb_morphology')
        if df is None or len(df) == 0:
            print("⚠️  No data available")
            return

        # Get top transformations by total
        df_top = df.nlargest(20, 'Total')

        # Create figure with 2 subplots
        fig, axes = plt.subplots(1, 2, figsize=(18, 8))
        fig.suptitle('Verb Morphology: Top 20 Transformations',
                     fontsize=16, fontweight='bold')

        # 1. Stacked bar chart by newspaper
        ax1 = axes[0]

        x = np.arange(len(df_top))
        width = 0.25

        ax1.barh(x - width, df_top['Times-of-India'], width,
                label='Times-of-India', color='#FF6B6B', alpha=0.8)
        ax1.barh(x, df_top['Hindustan-Times'], width,
                label='Hindustan-Times', color='#4ECDC4', alpha=0.8)
        ax1.barh(x + width, df_top['The-Hindu'], width,
                label='The-Hindu', color='#95E1D3', alpha=0.8)

        # Create labels
        labels = [f"{row['Feature'][:4]}:{row['Transformation'][:15]}"
                 for _, row in df_top.iterrows()]

        ax1.set_yticks(x)
        ax1.set_yticklabels(labels, fontsize=9)
        ax1.set_xlabel('Number of Transformations', fontweight='bold')
        ax1.set_title('By Newspaper')
        ax1.legend()
        ax1.grid(axis='x', alpha=0.3)
        ax1.invert_yaxis()

        # 2. Grouped by feature type
        ax2 = axes[1]

        feature_counts = df.groupby('Feature')[['Times-of-India', 'Hindustan-Times', 'The-Hindu']].sum()

        x = np.arange(len(feature_counts))
        width = 0.25

        ax2.bar(x - width, feature_counts['Times-of-India'], width,
                label='Times-of-India', color='#FF6B6B', alpha=0.8)
        ax2.bar(x, feature_counts['Hindustan-Times'], width,
                label='Hindustan-Times', color='#4ECDC4', alpha=0.8)
        ax2.bar(x + width, feature_counts['The-Hindu'], width,
                label='The-Hindu', color='#95E1D3', alpha=0.8)

        ax2.set_xticks(x)
        ax2.set_xticklabels(feature_counts.index, rotation=45, ha='right')
        ax2.set_ylabel('Number of Transformations', fontweight='bold')
        ax2.set_title('By Feature Type')
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)

        plt.tight_layout()

        # Save
        output_path = self.output_dir / 'verb_morphology_comparison.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✅ Saved to: {output_path}")

    def visualize_noun_morphology(self):
        """Create visualization of noun morphology patterns."""
        print(f"\n{'='*80}")
        print("CREATING NOUN MORPHOLOGY VISUALIZATION")
        print(f"{'='*80}\n")

        df = self.comparative_tables.get('noun_morphology')
        if df is None or len(df) == 0:
            print("⚠️  No data available")
            return

        # Get top transformations by total
        df_top = df.nlargest(15, 'Total')

        # Create figure
        fig, ax = plt.subplots(1, 1, figsize=(14, 8))
        fig.suptitle('Noun Morphology: Top 15 Transformations',
                     fontsize=16, fontweight='bold')

        x = np.arange(len(df_top))
        width = 0.25

        ax.barh(x - width, df_top['Times-of-India'], width,
                label='Times-of-India', color='#FF6B6B', alpha=0.8)
        ax.barh(x, df_top['Hindustan-Times'], width,
                label='Hindustan-Times', color='#4ECDC4', alpha=0.8)
        ax.barh(x + width, df_top['The-Hindu'], width,
                label='The-Hindu', color='#95E1D3', alpha=0.8)

        # Create labels
        labels = [f"{row['Feature']}:{row['Transformation'][:20]}"
                 for _, row in df_top.iterrows()]

        ax.set_yticks(x)
        ax.set_yticklabels(labels, fontsize=10)
        ax.set_xlabel('Number of Transformations', fontweight='bold')
        ax.legend()
        ax.grid(axis='x', alpha=0.3)
        ax.invert_yaxis()

        plt.tight_layout()

        # Save
        output_path = self.output_dir / 'noun_morphology_comparison.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✅ Saved to: {output_path}")

    def visualize_feature_heatmap(self):
        """Create heatmap of morphological features across newspapers."""
        print(f"\n{'='*80}")
        print("CREATING MORPHOLOGICAL FEATURE HEATMAP")
        print(f"{'='*80}\n")

        df = self.comparative_tables.get('feature_summary')
        if df is None or len(df) == 0:
            print("⚠️  No data available")
            return

        # Remove totals row for heatmap
        df_plot = df[df['Newspaper'] != 'TOTAL'].copy()

        # Prepare data for heatmap
        df_heatmap = df_plot.set_index('Newspaper')

        # Create figure
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))

        # Create heatmap
        sns.heatmap(df_heatmap.T, annot=True, fmt='g', cmap='YlOrRd',
                   cbar_kws={'label': 'Number of Transformations'},
                   linewidths=0.5, ax=ax)

        ax.set_title('Morphological Features Heatmap: Transformations by Feature and Newspaper',
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Newspaper', fontweight='bold')
        ax.set_ylabel('Morphological Feature', fontweight='bold')

        plt.tight_layout()

        # Save
        output_path = self.output_dir / 'morphological_features_heatmap.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✅ Saved to: {output_path}")

    def create_integrated_comparison(self):
        """Create integrated comparison combining morphology with other transformations."""
        print(f"\n{'='*80}")
        print("CREATING INTEGRATED TRANSFORMATION COMPARISON")
        print(f"{'='*80}\n")

        rows = []

        for newspaper in self.newspapers:
            if newspaper not in self.morphological_data:
                continue

            # Get morphological totals from already-created table
            overall_df = self.comparative_tables.get('overall_statistics')
            if overall_df is None:
                continue

            newspaper_row = overall_df[overall_df['Newspaper'] == newspaper]
            if len(newspaper_row) == 0:
                continue

            newspaper_row = newspaper_row.iloc[0]
            total_events = newspaper_row['Total Events']
            morph_changes = newspaper_row['Morph Changes']

            # Load rule analysis data if available
            rule_path = self.project_root / 'output' / newspaper / 'rule_analysis' / 'extracted_rules' / 'rule_summary.csv'

            lexical_rules = 0
            syntactic_rules = 0
            default_rules = 0

            if rule_path.exists():
                rule_df = pd.read_csv(rule_path)
                lexical_rules = len(rule_df[rule_df['Tier'] == 'Lexical'])
                syntactic_rules = len(rule_df[rule_df['Tier'] == 'Syntactic'])
                default_rules = len(rule_df[rule_df['Tier'] == 'Default'])

            # Get morphological rules from morphological analysis
            morph_rules_path = self.project_root / 'output' / newspaper / 'morphological_analysis' / 'morphological_rules.csv'
            morph_rules = 0
            if morph_rules_path.exists():
                morph_rules_df = pd.read_csv(morph_rules_path)
                morph_rules = len(morph_rules_df)

            morph_pct = newspaper_row['Morph %']

            row = {
                'Newspaper': newspaper,
                'Total Events': total_events,
                'Morphological': morph_changes,
                'Morph %': morph_pct,
                'Lexical Rules': lexical_rules,
                'Syntactic Rules': syntactic_rules,
                'Morph Rules': morph_rules,
                'Default Rules': default_rules,
                'Total Rules': lexical_rules + syntactic_rules + morph_rules + default_rules
            }
            rows.append(row)

        df = pd.DataFrame(rows)

        # Save
        csv_path = self.output_dir / 'integrated_transformation_comparison.csv'
        df.to_csv(csv_path, index=False)
        print(f"✅ Saved to: {csv_path}")

        self.comparative_tables['integrated'] = df
        return df

    def visualize_integrated_comparison(self):
        """Visualize integrated transformation comparison."""
        print(f"\n{'='*80}")
        print("CREATING INTEGRATED COMPARISON VISUALIZATION")
        print(f"{'='*80}\n")

        df = self.comparative_tables.get('integrated')
        if df is None or len(df) == 0:
            print("⚠️  No data available")
            return

        # Create figure with 2 subplots
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.suptitle('Integrated Transformation Analysis',
                     fontsize=16, fontweight='bold')

        # 1. Rule counts by type
        ax1 = axes[0]

        x = np.arange(len(df))
        width = 0.2

        ax1.bar(x - 1.5*width, df['Lexical Rules'], width,
                label='Lexical', color='#FF6B6B', alpha=0.8)
        ax1.bar(x - 0.5*width, df['Morph Rules'], width,
                label='Morphological', color='#4ECDC4', alpha=0.8)
        ax1.bar(x + 0.5*width, df['Syntactic Rules'], width,
                label='Syntactic', color='#95E1D3', alpha=0.8)
        ax1.bar(x + 1.5*width, df['Default Rules'], width,
                label='Default', color='#F8B500', alpha=0.8)

        ax1.set_xlabel('Newspaper', fontweight='bold')
        ax1.set_ylabel('Number of Rules', fontweight='bold')
        ax1.set_title('Rule Distribution by Type')
        ax1.set_xticks(x)
        ax1.set_xticklabels(df['Newspaper'], rotation=45, ha='right')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)

        # 2. Morphological transformations vs total events
        ax2 = axes[1]

        x = np.arange(len(df))

        # Stacked bar
        morph_events = df['Morphological']
        other_events = df['Total Events'] - df['Morphological']

        ax2.bar(x, morph_events, label='Morphological', color='#FF6B6B', alpha=0.8)
        ax2.bar(x, other_events, bottom=morph_events,
                label='Other Transformations', color='#E0E0E0', alpha=0.8)

        # Add percentage labels
        for i, (morph, total) in enumerate(zip(df['Morphological'], df['Total Events'])):
            pct = 100 * morph / total if total > 0 else 0
            ax2.text(i, total + 500, f'{pct:.1f}%',
                    ha='center', fontweight='bold', fontsize=10)

        ax2.set_xlabel('Newspaper', fontweight='bold')
        ax2.set_ylabel('Number of Events', fontweight='bold')
        ax2.set_title('Morphological vs Other Transformations')
        ax2.set_xticks(x)
        ax2.set_xticklabels(df['Newspaper'], rotation=45, ha='right')
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)

        plt.tight_layout()

        # Save
        output_path = self.output_dir / 'integrated_comparison.png'
        plt.savefig(output_path, dpi=200)  # Reduced DPI to avoid memory error
        plt.close()

        print(f"✅ Saved to: {output_path}")

    def run_complete_analysis(self):
        """Run complete morphological comparative analysis."""
        print(f"\n{'='*80}")
        print("MORPHOLOGICAL COMPARATIVE ANALYSIS")
        print(f"{'='*80}\n")

        # Load data
        self.load_morphological_analyses()

        # Create tables
        self.create_overall_statistics_table()
        self.create_verb_morphology_table()
        self.create_noun_morphology_table()
        self.create_morphological_feature_summary()
        self.create_systematicity_comparison_table()
        self.create_integrated_comparison()

        # Create visualizations
        self.visualize_overall_statistics()
        self.visualize_verb_morphology()
        self.visualize_noun_morphology()
        self.visualize_feature_heatmap()
        self.visualize_integrated_comparison()

        print(f"\n{'='*80}")
        print("MORPHOLOGICAL COMPARATIVE ANALYSIS COMPLETE")
        print(f"{'='*80}\n")
        print(f"All results saved to: {self.output_dir}")
        print(f"\nGenerated files:")
        print(f"  Tables (6 CSV files):")
        for name in self.comparative_tables.keys():
            print(f"    - {name}")
        print(f"\n  Visualizations (5 PNG files):")
        print(f"    - overall_morphological_statistics.png")
        print(f"    - verb_morphology_comparison.png")
        print(f"    - noun_morphology_comparison.png")
        print(f"    - morphological_features_heatmap.png")
        print(f"    - integrated_comparison.png")


if __name__ == '__main__':
    analyzer = MorphologicalComparativeAnalyzer()
    analyzer.run_complete_analysis()
