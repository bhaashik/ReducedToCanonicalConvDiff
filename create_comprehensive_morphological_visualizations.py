#!/usr/bin/env python3
"""
Comprehensive Morphological Feature Visualizations.

Creates detailed visualizations for:
1. Morphological feature usage across newspapers
2. Transformation patterns using morphological features
3. Cross-newspaper comparative analysis
4. Progressive coverage breakdown by feature type
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Any
import numpy as np
from collections import defaultdict, Counter

# Set matplotlib backend and style
import matplotlib
matplotlib.use('Agg')
sns.set_style("whitegrid")


class ComprehensiveMorphologicalVisualizer:
    """Creates comprehensive morphological feature visualizations."""

    def __init__(self):
        self.newspapers = ['Times-of-India', 'Hindustan-Times', 'The-Hindu']
        self.project_root = Path(__file__).parent.absolute()
        self.output_dir = self.project_root / 'output' / 'comprehensive_morphological_visualizations'
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Color schemes
        self.newspaper_colors = {
            'Times-of-India': '#FF6B6B',
            'Hindustan-Times': '#4ECDC4',
            'The-Hindu': '#95E1D3'
        }

        self.feature_colors = {
            'VerbForm': '#FF6B6B',
            'Tense': '#4ECDC4',
            'Number': '#95E1D3',
            'Mood': '#F8B500',
            'Voice': '#A8E6CF',
            'Person': '#FFD93D',
            'Aspect': '#FF8B94',
            'Case': '#B4A7D6',
            'Definite': '#C7CEEA'
        }

        # Load data
        self.morphological_data = {}
        self.progressive_data = {}
        self.load_all_data()

    def load_all_data(self):
        """Load all morphological and progressive coverage data."""
        print(f"\n{'='*80}")
        print("LOADING DATA")
        print(f"{'='*80}\n")

        for newspaper in self.newspapers:
            # Load morphological analysis - try new format first
            morph_path = self.project_root / 'output' / newspaper / 'morphological_analysis' / 'morphological_rules.json'
            if morph_path.exists():
                with open(morph_path, 'r') as f:
                    rules_data = json.load(f)
                # Convert to expected format
                self.morphological_data[newspaper] = self._convert_rules_to_systematicity_format(rules_data)
                print(f"✅ Loaded morphological data for {newspaper}")
            else:
                # Try legacy format
                legacy_path = self.project_root / 'output' / newspaper / 'morphological_analysis' / 'morphological_analysis.json'
                if legacy_path.exists():
                    with open(legacy_path, 'r') as f:
                        self.morphological_data[newspaper] = json.load(f)
                    print(f"✅ Loaded morphological data for {newspaper} (legacy format)")

            # Load progressive coverage with morphology
            prog_path = self.project_root / 'output' / 'progressive_coverage_with_morphology' / f'progressive_data_with_morphology_{newspaper}.csv'
            if prog_path.exists():
                self.progressive_data[newspaper] = pd.read_csv(prog_path)
                print(f"✅ Loaded progressive data for {newspaper}")

    def _convert_rules_to_systematicity_format(self, rules_data: Dict) -> Dict:
        """Convert morphological_rules.json format to morph_systematicity format."""
        morph_systematicity = {}

        rules_by_feature = rules_data.get('rules_by_feature', {})

        for feature, feature_data in rules_by_feature.items():
            total_instances = feature_data.get('total_instances', 0)
            rules = feature_data.get('rules', [])

            # Convert rules to top_patterns format
            top_patterns = []
            for rule in rules:
                h_val = rule.get('headline_value', '')
                c_val = rule.get('canonical_value', '')
                freq = rule.get('frequency', 0)

                # Infer POS from feature type
                pos = self._infer_pos_from_feature(feature)

                pattern = f"{feature}::{h_val}→{c_val}@{pos}"

                top_patterns.append({
                    'pattern': pattern,
                    'frequency': freq
                })

            # Sort by frequency
            top_patterns.sort(key=lambda x: x['frequency'], reverse=True)

            unique_patterns = len(rules)
            total_transformations = total_instances
            avg_consistency = rules[0].get('confidence', 0) if rules else 0

            morph_systematicity[feature] = {
                'total_instances': total_instances,
                'top_patterns': top_patterns,
                'unique_patterns': unique_patterns,
                'avg_consistency': avg_consistency,
                'total_transformations': total_transformations
            }

        return {'morph_systematicity': morph_systematicity}

    def _infer_pos_from_feature(self, feature: str) -> str:
        """Infer POS tag from feature name."""
        verb_features = ['VerbForm', 'Tense', 'Aspect', 'Mood', 'Voice']
        noun_features = ['Number', 'Case', 'Definite', 'Gender']

        if feature in verb_features:
            return 'VERB'
        elif feature in noun_features:
            return 'NOUN'
        else:
            return 'UNKNOWN'

    def create_feature_transformation_sankey(self):
        """Create Sankey-like visualization showing feature transformations."""
        print(f"\n{'='*80}")
        print("CREATING FEATURE TRANSFORMATION FLOW VISUALIZATION")
        print(f"{'='*80}\n")

        for newspaper in self.newspapers:
            if newspaper not in self.morphological_data:
                continue

            morph_data = self.morphological_data[newspaper]
            morph_sys = morph_data.get('morph_systematicity', {})

            # Create figure
            fig, axes = plt.subplots(3, 3, figsize=(20, 16))
            fig.suptitle(f'Morphological Feature Transformations: {newspaper}',
                        fontsize=18, fontweight='bold', y=0.995)

            features = ['VerbForm', 'Tense', 'Number', 'Mood', 'Voice', 'Person', 'Aspect', 'Case', 'Definite']

            for idx, feature in enumerate(features):
                row = idx // 3
                col = idx % 3
                ax = axes[row, col]

                if feature not in morph_sys:
                    ax.text(0.5, 0.5, f'{feature}\nNo Data', ha='center', va='center',
                           fontsize=14, color='gray')
                    ax.set_xlim(0, 1)
                    ax.set_ylim(0, 1)
                    ax.axis('off')
                    continue

                feature_data = morph_sys[feature]
                patterns = feature_data.get('top_patterns', [])[:10]  # Top 10

                if not patterns:
                    ax.text(0.5, 0.5, f'{feature}\nNo Patterns', ha='center', va='center',
                           fontsize=14, color='gray')
                    ax.set_xlim(0, 1)
                    ax.set_ylim(0, 1)
                    ax.axis('off')
                    continue

                # Extract transformations
                transformations = []
                frequencies = []
                for pattern_info in patterns:
                    pattern = pattern_info['pattern']
                    frequency = pattern_info['frequency']

                    # Parse: "Feature::h_value→c_value@POS"
                    try:
                        parts = pattern.split('::')
                        if len(parts) == 2:
                            trans_part = parts[1].split('@')[0]
                            transformations.append(trans_part)
                            frequencies.append(frequency)
                    except:
                        continue

                if not transformations:
                    ax.text(0.5, 0.5, f'{feature}\nParse Error', ha='center', va='center',
                           fontsize=14, color='gray')
                    ax.set_xlim(0, 1)
                    ax.set_ylim(0, 1)
                    ax.axis('off')
                    continue

                # Create horizontal bar chart
                y_pos = np.arange(len(transformations))
                bars = ax.barh(y_pos, frequencies, color=self.feature_colors.get(feature, '#999999'), alpha=0.8)

                ax.set_yticks(y_pos)
                ax.set_yticklabels([t[:20] for t in transformations], fontsize=9)
                ax.set_xlabel('Frequency', fontsize=10, fontweight='bold')
                ax.set_title(f'{feature}\n({feature_data.get("total_instances", 0)} total)',
                           fontsize=11, fontweight='bold', pad=10)
                ax.grid(axis='x', alpha=0.3)
                ax.invert_yaxis()

                # Add value labels
                for i, (bar, val) in enumerate(zip(bars, frequencies)):
                    ax.text(val + max(frequencies)*0.02, i, str(val),
                           va='center', fontsize=8, fontweight='bold')

            plt.tight_layout()

            # Save
            output_path = self.output_dir / f'feature_transformations_{newspaper}.png'
            plt.savefig(output_path, dpi=200, bbox_inches='tight')
            plt.close()

            print(f"✅ Saved to: {output_path}")

    def create_transformation_direction_analysis(self):
        """Analyze and visualize directionality of transformations."""
        print(f"\n{'='*80}")
        print("CREATING TRANSFORMATION DIRECTION ANALYSIS")
        print(f"{'='*80}\n")

        # Collect transformation directions
        direction_data = defaultdict(lambda: defaultdict(int))

        for newspaper in self.newspapers:
            if newspaper not in self.morphological_data:
                continue

            morph_data = self.morphological_data[newspaper]
            morph_sys = morph_data.get('morph_systematicity', {})

            for feature, feature_data in morph_sys.items():
                patterns = feature_data.get('top_patterns', [])

                for pattern_info in patterns:
                    pattern = pattern_info['pattern']
                    frequency = pattern_info['frequency']

                    # Parse transformation
                    try:
                        parts = pattern.split('::')
                        if len(parts) == 2:
                            trans = parts[1].split('@')[0]
                            values = trans.split('→')
                            if len(values) == 2:
                                h_val, c_val = values

                                # Categorize direction
                                if h_val == 'ABSENT' and c_val != 'ABSENT':
                                    direction = 'Addition'
                                elif h_val != 'ABSENT' and c_val == 'ABSENT':
                                    direction = 'Removal'
                                elif h_val != 'ABSENT' and c_val != 'ABSENT':
                                    direction = 'Change'
                                else:
                                    continue

                                direction_data[feature][direction] += frequency
                    except:
                        continue

        # Create visualization
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Morphological Transformation Directionality Analysis',
                    fontsize=16, fontweight='bold')

        # 1. Overall direction distribution
        ax1 = axes[0, 0]
        total_directions = defaultdict(int)
        for feature_directions in direction_data.values():
            for direction, count in feature_directions.items():
                total_directions[direction] += count

        directions = list(total_directions.keys())
        counts = [total_directions[d] for d in directions]
        colors_map = {'Addition': '#4ECDC4', 'Removal': '#FF6B6B', 'Change': '#F8B500'}
        colors = [colors_map.get(d, '#999999') for d in directions]

        ax1.pie(counts, labels=directions, autopct='%1.1f%%',
               colors=colors, startangle=90, textprops={'fontsize': 12, 'fontweight': 'bold'})
        ax1.set_title('Overall Transformation Directions', fontsize=13, fontweight='bold', pad=15)

        # 2. Direction by feature (stacked bar)
        ax2 = axes[0, 1]
        features = list(direction_data.keys())

        if len(features) > 0:
            addition_counts = [direction_data[f]['Addition'] for f in features]
            removal_counts = [direction_data[f]['Removal'] for f in features]
            change_counts = [direction_data[f]['Change'] for f in features]

            x = np.arange(len(features))
            width = 0.6

            ax2.bar(x, addition_counts, width, label='Addition', color='#4ECDC4', alpha=0.8)
            ax2.bar(x, removal_counts, width, bottom=addition_counts,
                   label='Removal', color='#FF6B6B', alpha=0.8)
            ax2.bar(x, change_counts, width,
                   bottom=np.array(addition_counts) + np.array(removal_counts),
                   label='Change', color='#F8B500', alpha=0.8)

            ax2.set_xticks(x)
            ax2.set_xticklabels(features, rotation=45, ha='right')
            ax2.set_ylabel('Frequency', fontweight='bold')
            ax2.set_title('Transformation Directions by Feature', fontsize=13, fontweight='bold')
            ax2.legend()
            ax2.grid(axis='y', alpha=0.3)
        else:
            ax2.text(0.5, 0.5, 'No data available', ha='center', va='center',
                    transform=ax2.transAxes, fontsize=14)
            ax2.set_title('Transformation Directions by Feature', fontsize=13, fontweight='bold')

        # 3. Feature-specific direction percentages
        ax3 = axes[1, 0]
        direction_pcts = []
        for feature in features:
            total = sum(direction_data[feature].values())
            if total > 0:
                pct_addition = 100 * direction_data[feature]['Addition'] / total
                pct_removal = 100 * direction_data[feature]['Removal'] / total
                pct_change = 100 * direction_data[feature]['Change'] / total
            else:
                pct_addition = pct_removal = pct_change = 0

            direction_pcts.append([pct_addition, pct_removal, pct_change])

        direction_pcts = np.array(direction_pcts)

        x = np.arange(len(features))
        ax3.bar(x, direction_pcts[:, 0], width, label='Addition', color='#4ECDC4', alpha=0.8)
        ax3.bar(x, direction_pcts[:, 1], width, bottom=direction_pcts[:, 0],
               label='Removal', color='#FF6B6B', alpha=0.8)
        ax3.bar(x, direction_pcts[:, 2], width,
               bottom=direction_pcts[:, 0] + direction_pcts[:, 1],
               label='Change', color='#F8B500', alpha=0.8)

        ax3.set_xticks(x)
        ax3.set_xticklabels(features, rotation=45, ha='right')
        ax3.set_ylabel('Percentage (%)', fontweight='bold')
        ax3.set_title('Direction Distribution by Feature (Normalized)', fontsize=13, fontweight='bold')
        ax3.set_ylim([0, 100])
        ax3.legend()
        ax3.grid(axis='y', alpha=0.3)

        # 4. Top transformations by direction
        ax4 = axes[1, 1]
        ax4.axis('tight')
        ax4.axis('off')

        # Get top 5 for each direction
        top_additions = []
        top_removals = []
        top_changes = []

        for newspaper in self.newspapers:
            if newspaper not in self.morphological_data:
                continue

            morph_data = self.morphological_data[newspaper]
            morph_sys = morph_data.get('morph_systematicity', {})

            for feature, feature_data in morph_sys.items():
                patterns = feature_data.get('top_patterns', [])[:3]

                for pattern_info in patterns:
                    pattern = pattern_info['pattern']
                    frequency = pattern_info['frequency']

                    try:
                        parts = pattern.split('::')
                        if len(parts) == 2:
                            trans = parts[1].split('@')[0]
                            values = trans.split('→')
                            if len(values) == 2:
                                h_val, c_val = values

                                if h_val == 'ABSENT' and c_val != 'ABSENT':
                                    top_additions.append((f"{feature}:{trans}", frequency))
                                elif h_val != 'ABSENT' and c_val == 'ABSENT':
                                    top_removals.append((f"{feature}:{trans}", frequency))
                                elif h_val != 'ABSENT' and c_val != 'ABSENT':
                                    top_changes.append((f"{feature}:{trans}", frequency))
                    except:
                        continue

        # Sort and get top 5
        top_additions = sorted(top_additions, key=lambda x: x[1], reverse=True)[:5]
        top_removals = sorted(top_removals, key=lambda x: x[1], reverse=True)[:5]
        top_changes = sorted(top_changes, key=lambda x: x[1], reverse=True)[:5]

        table_data = [
            ['Direction', 'Top Transformation', 'Frequency'],
            ['', '', ''],
            ['Addition', top_additions[0][0][:30] if top_additions else '-',
             top_additions[0][1] if top_additions else 0],
            ['', top_additions[1][0][:30] if len(top_additions) > 1 else '-',
             top_additions[1][1] if len(top_additions) > 1 else 0],
            ['', '', ''],
            ['Removal', top_removals[0][0][:30] if top_removals else '-',
             top_removals[0][1] if top_removals else 0],
            ['', top_removals[1][0][:30] if len(top_removals) > 1 else '-',
             top_removals[1][1] if len(top_removals) > 1 else 0],
            ['', '', ''],
            ['Change', top_changes[0][0][:30] if top_changes else '-',
             top_changes[0][1] if top_changes else 0],
            ['', top_changes[1][0][:30] if len(top_changes) > 1 else '-',
             top_changes[1][1] if len(top_changes) > 1 else 0]
        ]

        table = ax4.table(cellText=table_data, cellLoc='left', loc='center',
                         colWidths=[0.2, 0.6, 0.2])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)

        # Style header
        for i in range(3):
            table[(0, i)].set_facecolor('#4ECDC4')
            table[(0, i)].set_text_props(weight='bold', color='white')

        ax4.set_title('Top Transformations by Direction', fontsize=13, fontweight='bold', pad=20)

        plt.tight_layout()

        # Save
        output_path = self.output_dir / 'transformation_directionality.png'
        plt.savefig(output_path, dpi=200, bbox_inches='tight')
        plt.close()

        print(f"✅ Saved to: {output_path}")

    def create_progressive_coverage_by_feature_type(self):
        """Create progressive coverage breakdown showing contribution by rule type."""
        print(f"\n{'='*80}")
        print("CREATING PROGRESSIVE COVERAGE BY FEATURE TYPE")
        print(f"{'='*80}\n")

        for newspaper in self.newspapers:
            if newspaper not in self.progressive_data:
                continue

            df = self.progressive_data[newspaper]

            # Create figure with 2x2 subplots
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle(f'Progressive Coverage Breakdown by Rule Type: {newspaper}',
                        fontsize=16, fontweight='bold')

            # 1. Cumulative coverage by rule type (area chart)
            ax1 = axes[0, 0]

            # Calculate cumulative coverage by type
            rule_types = ['lexical', 'morphological', 'syntactic', 'default']
            type_data = {rt: [] for rt in rule_types}
            cumulative = {rt: 0 for rt in rule_types}

            for _, row in df.iterrows():
                rule_type = row['rule_type']
                coverage_pct = row['coverage_pct']

                for rt in rule_types:
                    if rt == rule_type:
                        type_data[rt].append(coverage_pct - cumulative[rt])
                        cumulative[rt] = coverage_pct
                    else:
                        type_data[rt].append(0)

            # Create stacked area chart
            x = df['rule_count']
            colors = ['#FF6B6B', '#4ECDC4', '#95E1D3', '#F8B500']

            ax1.stackplot(x,
                         np.cumsum([type_data['lexical']], axis=0)[0],
                         np.cumsum([type_data['lexical'], type_data['morphological']], axis=0)[1],
                         np.cumsum([type_data['lexical'], type_data['morphological'], type_data['syntactic']], axis=0)[2],
                         np.cumsum([type_data['lexical'], type_data['morphological'], type_data['syntactic'], type_data['default']], axis=0)[3],
                         labels=['Lexical', 'Morphological', 'Syntactic', 'Default'],
                         colors=colors, alpha=0.7)

            ax1.set_xlabel('Number of Rules', fontweight='bold')
            ax1.set_ylabel('Cumulative Coverage (%)', fontweight='bold')
            ax1.set_title('Cumulative Coverage by Rule Type', fontsize=13, fontweight='bold')
            ax1.legend(loc='upper left')
            ax1.grid(alpha=0.3)

            # 2. Rule type distribution (pie chart)
            ax2 = axes[0, 1]
            type_counts = df.groupby('rule_type')['rule_count'].count()
            ax2.pie(type_counts.values, labels=type_counts.index,
                   autopct='%1.1f%%', colors=colors[:len(type_counts)],
                   startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
            ax2.set_title('Rule Distribution by Type', fontsize=13, fontweight='bold')

            # 3. Coverage contribution by type (bar chart)
            ax3 = axes[1, 0]

            final_coverage = {}
            for rule_type in rule_types:
                type_rows = df[df['rule_type'] == rule_type]
                if len(type_rows) > 0:
                    final_coverage[rule_type] = type_rows['coverage_pct'].iloc[-1]
                else:
                    final_coverage[rule_type] = 0

            # Calculate incremental coverage
            incremental = []
            prev = 0
            for rt in rule_types:
                inc = final_coverage[rt] - prev
                incremental.append(inc)
                prev = final_coverage[rt]

            x_pos = np.arange(len(rule_types))
            bars = ax3.bar(x_pos, incremental, color=colors, alpha=0.8)
            ax3.set_xticks(x_pos)
            ax3.set_xticklabels([rt.capitalize() for rt in rule_types])
            ax3.set_ylabel('Coverage Contribution (%)', fontweight='bold')
            ax3.set_title('Coverage Contribution by Rule Type', fontsize=13, fontweight='bold')
            ax3.grid(axis='y', alpha=0.3)

            # Add value labels
            for bar, val in zip(bars, incremental):
                if val > 0:
                    ax3.text(bar.get_x() + bar.get_width()/2, val + 1,
                           f'{val:.1f}%', ha='center', fontweight='bold')

            # 4. F1-score by rule type
            ax4 = axes[1, 1]

            # Get F1 at each rule type milestone
            f1_by_type = {}
            for rule_type in rule_types:
                type_rows = df[df['rule_type'] == rule_type]
                if len(type_rows) > 0:
                    f1_by_type[rule_type] = type_rows['f1_score'].iloc[-1]
                else:
                    f1_by_type[rule_type] = 0

            x = df['rule_count']
            ax4.plot(x, df['f1_score'], color='#4ECDC4', linewidth=2.5, label='F1-Score')
            ax4.set_xlabel('Number of Rules', fontweight='bold')
            ax4.set_ylabel('F1-Score', fontweight='bold')
            ax4.set_title('F1-Score Progression', fontsize=13, fontweight='bold')
            ax4.grid(alpha=0.3)

            # Mark milestones
            cumulative_count = 0
            for i, rt in enumerate(rule_types):
                type_rows = df[df['rule_type'] == rt]
                if len(type_rows) > 0:
                    cumulative_count += len(type_rows)
                    if cumulative_count <= len(df):
                        milestone_row = df.iloc[min(cumulative_count-1, len(df)-1)]
                        ax4.axvline(x=milestone_row['rule_count'], color=colors[i],
                                   linestyle='--', alpha=0.5, linewidth=1.5)
                        ax4.text(milestone_row['rule_count'], ax4.get_ylim()[1] * 0.95,
                               rt.capitalize()[:4], ha='center', fontsize=9,
                               color=colors[i], fontweight='bold')

            plt.tight_layout()

            # Save
            output_path = self.output_dir / f'progressive_coverage_breakdown_{newspaper}.png'
            plt.savefig(output_path, dpi=200, bbox_inches='tight')
            plt.close()

            print(f"✅ Saved to: {output_path}")

    def create_cross_newspaper_feature_comparison(self):
        """Create comprehensive cross-newspaper feature comparison."""
        print(f"\n{'='*80}")
        print("CREATING CROSS-NEWSPAPER FEATURE COMPARISON")
        print(f"{'='*80}\n")

        # Collect feature data
        feature_totals = defaultdict(lambda: defaultdict(int))

        for newspaper in self.newspapers:
            if newspaper not in self.morphological_data:
                continue

            morph_data = self.morphological_data[newspaper]
            morph_sys = morph_data.get('morph_systematicity', {})

            for feature, feature_data in morph_sys.items():
                total = feature_data.get('total_instances', 0)
                feature_totals[feature][newspaper] = total

        # Create figure with 2x2 subplots
        fig, axes = plt.subplots(2, 2, figsize=(18, 14))
        fig.suptitle('Cross-Newspaper Morphological Feature Comparison',
                    fontsize=18, fontweight='bold')

        # 1. Feature usage by newspaper (grouped bar)
        ax1 = axes[0, 0]
        features = list(feature_totals.keys())
        x = np.arange(len(features))
        width = 0.25

        for i, newspaper in enumerate(self.newspapers):
            counts = [feature_totals[f][newspaper] for f in features]
            ax1.bar(x + i*width, counts, width,
                   label=newspaper, color=self.newspaper_colors[newspaper], alpha=0.8)

        ax1.set_xticks(x + width)
        ax1.set_xticklabels(features, rotation=45, ha='right')
        ax1.set_ylabel('Number of Transformations', fontweight='bold')
        ax1.set_title('Feature Usage by Newspaper', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)

        # 2. Normalized feature distribution (100% stacked)
        ax2 = axes[0, 1]

        # Calculate percentages
        newspaper_totals = {n: sum(feature_totals[f][n] for f in features)
                           for n in self.newspapers}

        feature_pcts = defaultdict(list)
        for feature in features:
            for newspaper in self.newspapers:
                total = newspaper_totals[newspaper]
                pct = 100 * feature_totals[feature][newspaper] / total if total > 0 else 0
                feature_pcts[feature].append(pct)

        x = np.arange(len(self.newspapers))
        bottom = np.zeros(len(self.newspapers))

        for i, feature in enumerate(features):
            ax2.bar(x, feature_pcts[feature], bottom=bottom,
                   label=feature, color=self.feature_colors.get(feature, '#999999'), alpha=0.8)
            bottom += np.array(feature_pcts[feature])

        ax2.set_xticks(x)
        ax2.set_xticklabels(self.newspapers, rotation=15, ha='right')
        ax2.set_ylabel('Percentage (%)', fontweight='bold')
        ax2.set_title('Feature Distribution (Normalized)', fontsize=14, fontweight='bold')
        ax2.set_ylim([0, 100])
        ax2.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=9)
        ax2.grid(axis='y', alpha=0.3)

        # 3. Feature consistency heatmap
        ax3 = axes[1, 0]

        # Create consistency matrix
        consistency_matrix = []
        for feature in features:
            row = [feature_totals[feature][n] for n in self.newspapers]
            consistency_matrix.append(row)

        consistency_matrix = np.array(consistency_matrix)

        im = ax3.imshow(consistency_matrix, cmap='YlOrRd', aspect='auto')
        ax3.set_xticks(np.arange(len(self.newspapers)))
        ax3.set_yticks(np.arange(len(features)))
        ax3.set_xticklabels(self.newspapers, rotation=45, ha='right')
        ax3.set_yticklabels(features)
        ax3.set_title('Feature Frequency Heatmap', fontsize=14, fontweight='bold')

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax3)
        cbar.set_label('Transformations', fontweight='bold')

        # Add text annotations
        for i in range(len(features)):
            for j in range(len(self.newspapers)):
                text = ax3.text(j, i, int(consistency_matrix[i, j]),
                              ha="center", va="center", color="black", fontsize=9,
                              fontweight='bold')

        # 4. Total transformations by newspaper
        ax4 = axes[1, 1]

        newspaper_totals_list = [newspaper_totals[n] for n in self.newspapers]
        colors = [self.newspaper_colors[n] for n in self.newspapers]

        bars = ax4.barh(self.newspapers, newspaper_totals_list, color=colors, alpha=0.8)
        ax4.set_xlabel('Total Morphological Transformations', fontweight='bold')
        ax4.set_title('Total Transformations by Newspaper', fontsize=14, fontweight='bold')
        ax4.grid(axis='x', alpha=0.3)

        # Add value labels
        for bar, val in zip(bars, newspaper_totals_list):
            ax4.text(val + max(newspaper_totals_list)*0.02, bar.get_y() + bar.get_height()/2,
                   f'{val:,}', va='center', fontweight='bold', fontsize=11)

        plt.tight_layout()

        # Save
        output_path = self.output_dir / 'cross_newspaper_feature_comparison.png'
        plt.savefig(output_path, dpi=200, bbox_inches='tight')
        plt.close()

        print(f"✅ Saved to: {output_path}")

    def create_morphological_impact_visualization(self):
        """Create visualization showing morphological tier impact on progressive coverage."""
        print(f"\n{'='*80}")
        print("CREATING MORPHOLOGICAL IMPACT VISUALIZATION")
        print(f"{'='*80}\n")

        # Create figure
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('Impact of Morphological Tier on Progressive Coverage',
                    fontsize=18, fontweight='bold')

        for idx, newspaper in enumerate(self.newspapers):
            if newspaper not in self.progressive_data:
                continue

            df = self.progressive_data[newspaper]

            # Load previous data (without morphology)
            prev_path = self.project_root / 'output' / 'progressive_coverage_analysis' / f'progressive_data_{newspaper}.csv'
            if prev_path.exists():
                df_prev = pd.read_csv(prev_path)
            else:
                df_prev = pd.DataFrame()

            # Top row: Coverage improvement
            ax_top = axes[0, idx]

            if len(df_prev) > 0:
                ax_top.plot(df_prev['rule_count'], df_prev['coverage_pct'],
                          label='Without Morphology', color='steelblue',
                          linewidth=2.5, linestyle='--')

            ax_top.plot(df['rule_count'], df['coverage_pct'],
                       label='With Morphology', color='coral',
                       linewidth=2.5)

            ax_top.set_xlabel('Number of Rules', fontweight='bold')
            ax_top.set_ylabel('Coverage (%)', fontweight='bold')
            ax_top.set_title(f'{newspaper}\nCoverage Impact', fontsize=12, fontweight='bold')
            ax_top.legend(fontsize=9)
            ax_top.grid(alpha=0.3)

            # Bottom row: F1-score improvement
            ax_bottom = axes[1, idx]

            if len(df_prev) > 0:
                ax_bottom.plot(df_prev['rule_count'], df_prev['f1_score'],
                             label='Without Morphology', color='steelblue',
                             linewidth=2.5, linestyle='--')

            ax_bottom.plot(df['rule_count'], df['f1_score'],
                          label='With Morphology', color='coral',
                          linewidth=2.5)

            # Mark optimal points
            if len(df_prev) > 0:
                opt_prev_idx = df_prev['f1_score'].idxmax()
                opt_prev = df_prev.loc[opt_prev_idx]
                ax_bottom.scatter([opt_prev['rule_count']], [opt_prev['f1_score']],
                                color='steelblue', s=100, marker='*', zorder=5,
                                label=f'Optimal (No Morph): {opt_prev["f1_score"]:.1f}')

            opt_idx = df['f1_score'].idxmax()
            opt = df.loc[opt_idx]
            ax_bottom.scatter([opt['rule_count']], [opt['f1_score']],
                            color='coral', s=100, marker='*', zorder=5,
                            label=f'Optimal (With Morph): {opt["f1_score"]:.1f}')

            ax_bottom.set_xlabel('Number of Rules', fontweight='bold')
            ax_bottom.set_ylabel('F1-Score', fontweight='bold')
            ax_bottom.set_title(f'F1-Score Impact', fontsize=12, fontweight='bold')
            ax_bottom.legend(fontsize=8)
            ax_bottom.grid(alpha=0.3)

        plt.tight_layout()

        # Save
        output_path = self.output_dir / 'morphological_impact_comparison.png'
        plt.savefig(output_path, dpi=200, bbox_inches='tight')
        plt.close()

        print(f"✅ Saved to: {output_path}")

    def run_all_visualizations(self):
        """Run all visualization generators."""
        print(f"\n{'='*80}")
        print("COMPREHENSIVE MORPHOLOGICAL VISUALIZATIONS")
        print(f"{'='*80}\n")

        self.create_feature_transformation_sankey()
        self.create_transformation_direction_analysis()
        self.create_progressive_coverage_by_feature_type()
        self.create_cross_newspaper_feature_comparison()
        self.create_morphological_impact_visualization()

        print(f"\n{'='*80}")
        print("ALL VISUALIZATIONS COMPLETE")
        print(f"{'='*80}\n")
        print(f"All results saved to: {self.output_dir}")
        print(f"\nGenerated visualizations:")
        print(f"  1. Feature transformation patterns (3 files, one per newspaper)")
        print(f"  2. Transformation directionality analysis (1 file)")
        print(f"  3. Progressive coverage breakdown by feature type (3 files)")
        print(f"  4. Cross-newspaper feature comparison (1 file)")
        print(f"  5. Morphological impact on progressive coverage (1 file)")
        print(f"\nTotal: 11 visualization files")


if __name__ == '__main__':
    visualizer = ComprehensiveMorphologicalVisualizer()
    visualizer.run_all_visualizations()
