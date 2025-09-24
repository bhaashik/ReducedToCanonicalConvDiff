
# Version 1

# import matplotlib.pyplot as plt
# import seaborn as sns
# from typing import Dict
# from pathlib import Path
#
# from register_comparison.outputs.output_creator import OutputCreator
#
#
# class Visualizer:
#     def __init__(self, output_dir: Path):
#         self.output_dir = output_dir
#         self.output_dir.mkdir(parents=True, exist_ok=True)
#
#     def plot_feature_frequencies(self, feature_counts: Dict[str, int], title: str, filename: str):
#         """
#         Generate a bar chart of feature frequencies.
#         """
#         keys = list(feature_counts.keys())
#         values = [feature_counts[k] for k in keys]
#
#         plt.figure(figsize=(10,6))
#         sns.barplot(x=keys, y=values, color='skyblue')
#         plt.title(title)
#         plt.xlabel("Feature ID")
#         plt.ylabel("Frequency")
#         plt.xticks(rotation=45, ha="right")
#         plt.tight_layout()
#         plt.savefig(self.output_dir / filename)
#         plt.close()
#         print(f"Saved feature frequency plot to {filename}")
#
#     def plot_histogram(self, data, bins: int, title: str, xlabel: str, filename: str):
#         """
#         Generic histogram plot.
#         """
#         plt.figure(figsize=(8,5))
#         plt.hist(data, bins=bins, color="green", edgecolor="black")
#         plt.title(title)
#         plt.xlabel(xlabel)
#         plt.ylabel("Count")
#         plt.tight_layout()
#         plt.savefig(self.output_dir / filename)
#         plt.close()
#         print(f"Saved histogram to {filename}")
#
#     # You can add more visualization functions here for structural differences etc.
#
# # Usage:
#
# from pathlib import Path
# from register_comparison.outputs import output_creator
# from visualizer import Visualizer
# from register_comparison.meta_data.schema import FeatureSchema as schema
# from register_comparison.aggregators.aggregator import Aggregator
#
# output_dir = Path("results")
# outputs = OutputCreator(output_dir, schema)
# visualizer = Visualizer(output_dir)
#
# # Save feature frequency CSV
# feature_counts = Aggregator.global_counts()
# outputs.save_feature_matrix_csv(feature_counts, "feature_freq_global.csv")
#
# # Save detailed event table CSV
# outputs.save_events_csv(Aggregator.global_events, "events_global.csv")
#
# # Save summary statistics CSV (suppose from stats.py)
# # outputs.save_summary_stats_csv(summary_stats_df, "summary_stats_global.csv")
#
# # Generate LaTeX and Markdown summaries
# outputs.generate_latex_summary("summary_features.tex")
# outputs.generate_markdown_summary("summary_features.md")
#
# # Save interpretive notes (prepare as string beforehand)
# # outputs.save_interpretive_notes(notes_text, "interpretive_notes.txt")
#
# # Create visualization plots
# visualizer.plot_feature_frequencies(feature_counts, "Global Feature Frequencies", "feature_freq_global.png")
#
# # Similarly for newspapers or parse-types, pass their counts to plotting functions

# Usage:

# Version

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, Any, List
from pathlib import Path
from register_comparison.outputs.output_creators import Outputs as output_creator, Outputs


class Visualizer:
    def __init__(self, output_dir: Path, schema=None):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.schema = schema
        self._create_mnemonic_mappings()

    def _create_mnemonic_mappings(self):
        """Create mappings from feature IDs to readable names using schema mnemonics."""
        self.feature_labels = {}
        self.value_labels = {}

        if self.schema:
            for feature in self.schema.features:
                # Check if feature is a string or Feature object
                if isinstance(feature, str):
                    # If it's a string, just use it as the ID
                    feature_id = feature
                    readable_name = f"{feature}\n(Feature)"
                    self.feature_labels[feature_id] = readable_name
                else:
                    # If it's a Feature object, use its properties
                    feature_id = feature.mnemonic_code
                    readable_name = f"{feature.mnemonic_code}\n({feature.name})"
                    self.feature_labels[feature_id] = readable_name

                    # Map values to mnemonics
                    if hasattr(feature, 'values'):
                        for value in feature.values:
                            value_id = value.value
                            value_mnemonic = value.mnemonic
                            self.value_labels[value_id] = value_mnemonic

        # Fallback for common abbreviations
        default_labels = {
            'FW-DEL': 'FW-DEL\n(Function Word\nDeletion)',
            'FW-ADD': 'FW-ADD\n(Function Word\nAddition)',
            'C-DEL': 'C-DEL\n(Content Word\nDeletion)',
            'C-ADD': 'C-ADD\n(Content Word\nAddition)',
            'POS-CHG': 'POS-CHG\n(POS Change)',
            'LEMMA-CHG': 'LEMMA-CHG\n(Lemma Change)',
            'FORM-CHG': 'FORM-CHG\n(Surface Form\nChange)',
            'DEP-REL-CHG': 'DEP-REL-CHG\n(Dependency\nRelation Change)',
            'HEAD-CHG': 'HEAD-CHG\n(Dependency\nHead Change)',
            'FEAT-CHG': 'FEAT-CHG\n(Morphological\nFeature Change)',
            'VERB-FORM-CHG': 'VERB-FORM-CHG\n(Verb Form\nChange)',
            'LENGTH-CHG': 'LENGTH-CHG\n(Sentence Length\nChange)',
            'CONST-ADD': 'CONST-ADD\n(Constituent\nAddition)',
            'CONST-REM': 'CONST-REM\n(Constituent\nRemoval)',
            'CONST-MOV': 'CONST-MOV\n(Constituent\nMovement)',
            'CLAUSE-TYPE-CHG': 'CLAUSE-TYPE-CHG\n(Clause Type\nChange)',
            'TOKEN-REORDER': 'TOKEN-REORDER\n(Token\nReordering)',
            'TED': 'TED\n(Token Edit\nDistance)'
        }

        # Use default labels for any missing mappings
        for key, label in default_labels.items():
            if key not in self.feature_labels:
                self.feature_labels[key] = label

    def _get_feature_label(self, feature_id):
        """Get readable label for feature ID."""
        return self.feature_labels.get(feature_id, feature_id)

    def _get_value_label(self, value_id):
        """Get readable label for value ID."""
        return self.value_labels.get(value_id, value_id)

    def plot_feature_frequencies(self, feature_counts: Dict[str, int], title: str, filename: str):
        """
        Generate a bar chart of feature frequencies with improved clarity using mnemonics.
        """
        keys = list(feature_counts.keys())
        values = [feature_counts[k] for k in keys]

        # Sort by frequency for better readability
        sorted_pairs = sorted(zip(keys, values), key=lambda x: x[1], reverse=True)
        keys, values = zip(*sorted_pairs) if sorted_pairs else ([], [])

        plt.figure(figsize=(16, 10))

        # Create color palette for better distinction
        colors = sns.color_palette("Set3", len(keys))
        bars = plt.bar(range(len(keys)), values, color=colors, edgecolor='black', linewidth=0.8)

        # Enhanced title and labels with mnemonics
        plt.title(title, fontsize=18, fontweight='bold', pad=25)
        plt.xlabel("Linguistic Features (Mnemonics)", fontsize=14, fontweight='bold')
        plt.ylabel("Frequency (Number of Occurrences)", fontsize=14, fontweight='bold')

        # Use mnemonic labels for x-axis
        readable_labels = [self._get_feature_label(key) for key in keys]
        plt.xticks(range(len(keys)), readable_labels, rotation=45, ha="right", fontsize=10)
        plt.yticks(fontsize=12)

        # Add value labels on bars for clarity
        for i, (bar, value) in enumerate(zip(bars, values)):
            if value > 0:  # Only show non-zero values
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.015,
                        f'{value:,}', ha='center', va='bottom', fontsize=9, fontweight='bold')

        # Improve axis scaling when values are close
        if values and max(values) > 0:
            y_range = max(values) - min(values)
            if y_range < max(values) * 0.1:  # If range is small relative to max
                y_min = max(0, min(values) - y_range * 0.1)
                y_max = max(values) + y_range * 0.2
                plt.ylim(y_min, y_max)
            else:
                # Standard scaling with some padding
                plt.ylim(0, max(values) * 1.1)

        # Add grid for better readability
        plt.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)

        # Add legend with feature counts for clarity
        legend_text = f"Total Features: {len(keys)}\nTotal Events: {sum(values):,}"
        plt.text(0.98, 0.98, legend_text, transform=plt.gca().transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8),
                verticalalignment='top', horizontalalignment='right', fontsize=10)

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved feature frequency plot to {filename}")

    def plot_histogram(self, data, bins: int, title: str, xlabel: str, filename: str):
        """
        Enhanced histogram plot with improved formatting.
        """
        plt.figure(figsize=(12, 8))

        # Create histogram with better styling
        n, bins_edges, patches = plt.hist(data, bins=bins, color="steelblue",
                                         edgecolor="black", linewidth=0.7, alpha=0.8)

        # Enhanced titles and labels
        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        plt.xlabel(xlabel, fontsize=14, fontweight='bold')
        plt.ylabel("Frequency (Count)", fontsize=14, fontweight='bold')

        # Improve axis formatting
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)

        # Add value labels on bars for clarity
        for i, (patch, count) in enumerate(zip(patches, n)):
            if count > 0:  # Only show non-zero values
                plt.text(patch.get_x() + patch.get_width()/2, patch.get_height() + max(n)*0.01,
                        f'{int(count)}', ha='center', va='bottom', fontsize=9, fontweight='bold')

        # Add statistics text
        mean_val = np.mean(data) if len(data) > 0 else 0
        std_val = np.std(data) if len(data) > 0 else 0
        stats_text = f"Mean: {mean_val:.2f}\nStd: {std_val:.2f}\nN: {len(data)}"
        plt.text(0.98, 0.98, stats_text, transform=plt.gca().transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8),
                verticalalignment='top', horizontalalignment='right', fontsize=10)

        # Add grid for better readability
        plt.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved enhanced histogram to {filename}")

    def create_comprehensive_visualizations(self, analysis: Dict, summary: Dict):
        """
        Create all relevant visualizations for comprehensive analysis.
        """
        # 1. Global feature distribution
        self.plot_feature_frequencies(
            analysis['global']['feature_counts'],
            "Global Feature Distribution",
            "global_features.png"
        )

        # 2. Parse type comparison
        self.plot_parse_type_comparison(
            analysis['by_parse_type'],
            "Features by Parse Type",
            "parse_type_comparison.png"
        )

        # 3. Newspaper comparison (if multiple newspapers)
        if len(analysis['by_newspaper']) > 1:
            self.plot_newspaper_comparison(
                analysis['by_newspaper'],
                "Features by Newspaper",
                "newspaper_comparison.png"
            )

        # 4. Feature coverage heatmap
        self.plot_feature_coverage_heatmap(
            analysis,
            "Feature Coverage Across Dimensions",
            "feature_coverage_heatmap.png"
        )

        # 5. Top features analysis
        self.plot_top_features_analysis(
            summary['feature_statistics'],
            "Top 15 Most Frequent Features",
            "top_features_analysis.png"
        )

        # 6. Cross-dimensional analysis
        self.plot_cross_dimensional_analysis(
            analysis['cross_analysis'],
            "Cross-Dimensional Feature Distribution",
            "cross_dimensional_analysis.png"
        )

        # 7. Feature category distribution
        self.plot_feature_category_distribution(
            summary['feature_statistics'],
            "Distribution by Feature Category",
            "feature_categories.png"
        )

        # 8. Tree Edit Distance (TED) analysis visualizations
        self.create_ted_visualizations(analysis, summary)

        # 9. Sentence-level TED distribution analysis
        self.create_ted_sentence_level_visualizations(analysis, summary)

    def plot_parse_type_comparison(self, parse_type_data: Dict, title: str, filename: str):
        """Create enhanced side-by-side comparison of features across parse types with mnemonics."""
        import pandas as pd

        # Prepare data for plotting
        plot_data = []
        for parse_type, data in parse_type_data.items():
            for feature_id, count in data['feature_counts'].items():
                plot_data.append({
                    'parse_type': parse_type,
                    'feature_id': feature_id,
                    'count': count
                })

        if not plot_data:
            return

        df = pd.DataFrame(plot_data)

        # Create figure with enhanced subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
        fig.suptitle(title, fontsize=18, fontweight='bold')

        # Plot 1: Grouped bar chart for top features with mnemonics
        top_features = df.groupby('feature_id')['count'].sum().nlargest(12).index
        df_top = df[df['feature_id'].isin(top_features)]

        df_pivot = df_top.pivot(index='feature_id', columns='parse_type', values='count').fillna(0)

        # Use mnemonic labels for x-axis
        readable_labels = [self._get_feature_label(feat).replace('\n', ' ') for feat in df_pivot.index]

        bars = df_pivot.plot(kind='bar', ax=ax1, width=0.8, edgecolor='black', linewidth=0.5)
        ax1.set_title("Top 12 Features by Parse Type", fontweight='bold', fontsize=14)
        ax1.set_xlabel("Linguistic Features (Mnemonics)", fontweight='bold', fontsize=12)
        ax1.set_ylabel("Event Count", fontweight='bold', fontsize=12)
        ax1.set_xticklabels(readable_labels, rotation=45, ha='right', fontsize=10)
        ax1.legend(title="Parse Type", fontsize=11, title_fontsize=12)
        ax1.grid(axis='y', alpha=0.3, linestyle='--')

        # Plot 2: Stacked bar chart showing proportions
        df_props = df.groupby(['parse_type', 'feature_id'])['count'].sum().unstack().fillna(0)
        df_props_pct = df_props.div(df_props.sum(axis=1), axis=0) * 100

        bars2 = df_props_pct.T.plot(kind='bar', stacked=True, ax=ax2, width=0.8, edgecolor='black', linewidth=0.5)
        ax2.set_title("Feature Distribution Proportions by Parse Type", fontweight='bold', fontsize=14)
        ax2.set_xlabel("Linguistic Features (Mnemonics)", fontweight='bold', fontsize=12)
        ax2.set_ylabel("Percentage of Total Events (%)", fontweight='bold', fontsize=12)

        # Use mnemonic labels for second plot
        readable_labels_2 = [self._get_feature_label(feat).replace('\n', ' ') for feat in df_props_pct.index]
        ax2.set_xticks(range(len(df_props_pct.index)))
        ax2.set_xticklabels(readable_labels_2, rotation=45, ha='right', fontsize=10)
        ax2.legend(title="Parse Type", fontsize=11, title_fontsize=12)
        ax2.grid(axis='y', alpha=0.3, linestyle='--')

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved enhanced parse type comparison to {filename}")

    def plot_newspaper_comparison(self, newspaper_data: Dict, title: str, filename: str):
        """Create enhanced comparison visualization across newspapers with mnemonics."""
        import pandas as pd

        plot_data = []
        for newspaper, data in newspaper_data.items():
            for feature_id, count in data['feature_counts'].items():
                plot_data.append({
                    'newspaper': newspaper,
                    'feature_id': feature_id,
                    'count': count
                })

        if not plot_data:
            return

        df = pd.DataFrame(plot_data)

        # Create enhanced grouped bar chart for top features
        top_features = df.groupby('feature_id')['count'].sum().nlargest(15).index
        df_top = df[df['feature_id'].isin(top_features)]

        plt.figure(figsize=(18, 10))
        df_pivot = df_top.pivot(index='feature_id', columns='newspaper', values='count').fillna(0)

        # Use mnemonic labels for x-axis
        readable_labels = [self._get_feature_label(feat).replace('\n', ' ') for feat in df_pivot.index]

        # Create enhanced bar plot
        ax = df_pivot.plot(kind='bar', width=0.8, edgecolor='black', linewidth=0.5,
                          colormap='Set2', figsize=(18, 10))

        plt.title(title, fontsize=18, fontweight='bold', pad=25)
        plt.xlabel("Linguistic Features (Mnemonics)", fontsize=14, fontweight='bold')
        plt.ylabel("Event Count", fontsize=14, fontweight='bold')

        # Enhanced axis formatting
        plt.xticks(range(len(readable_labels)), readable_labels, rotation=45, ha='right', fontsize=11)
        plt.yticks(fontsize=12)

        # Enhanced legend
        plt.legend(title="Newspaper", fontsize=12, title_fontsize=13,
                  bbox_to_anchor=(1.05, 1), loc='upper left')

        # Add grid and statistics
        plt.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)

        # Add summary statistics
        total_events = df['count'].sum()
        n_newspapers = len(newspaper_data)
        stats_text = f"Total Events: {total_events:,}\nNewspapers: {n_newspapers}\nTop Features: {len(top_features)}"
        plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.8),
                verticalalignment='top', horizontalalignment='left', fontsize=10)

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved newspaper comparison to {filename}")

    def plot_feature_coverage_heatmap(self, analysis: Dict, title: str, filename: str):
        """Create heatmap showing feature coverage across dimensions."""
        import pandas as pd
        import numpy as np

        # Collect all features
        all_features = set()
        for dimension_data in [analysis['by_newspaper'], analysis['by_parse_type']]:
            for data in dimension_data.values():
                all_features.update(data['feature_counts'].keys())

        all_features = sorted(list(all_features))

        # Create matrix for newspapers
        newspaper_matrix = []
        newspaper_labels = []
        for newspaper, data in analysis['by_newspaper'].items():
            row = [data['feature_counts'].get(feat, 0) for feat in all_features]
            newspaper_matrix.append(row)
            newspaper_labels.append(newspaper)

        # Create matrix for parse types
        parse_type_matrix = []
        parse_type_labels = []
        for parse_type, data in analysis['by_parse_type'].items():
            row = [data['feature_counts'].get(feat, 0) for feat in all_features]
            parse_type_matrix.append(row)
            parse_type_labels.append(parse_type)

        # Combine matrices
        combined_matrix = np.vstack([newspaper_matrix, parse_type_matrix])
        combined_labels = newspaper_labels + parse_type_labels

        # Create heatmap with improved formatting
        plt.figure(figsize=(20, 10))

        # Use feature mnemonics for better readability
        readable_features = [self._get_feature_label(feat).replace('\n', ' ') for feat in all_features]

        # Create heatmap with better styling
        ax = sns.heatmap(combined_matrix,
                        xticklabels=readable_features,
                        yticklabels=combined_labels,
                        annot=True,  # Show values for clarity
                        fmt='d',     # Integer format
                        cmap='YlOrRd',
                        cbar_kws={'label': 'Feature Count (Number of Events)', 'shrink': 0.8})

        plt.title(title, fontsize=18, fontweight='bold', pad=20)
        plt.xlabel("Linguistic Features (Mnemonics)", fontsize=14, fontweight='bold')
        plt.ylabel("Analysis Dimensions", fontsize=14, fontweight='bold')

        # Improve axis formatting
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.yticks(rotation=0, fontsize=12)

        # Add border around heatmap
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(1)

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved feature coverage heatmap to {filename}")

    def plot_top_features_analysis(self, feature_stats: Dict, title: str, filename: str):
        """Create detailed analysis of top features with improved clarity."""
        # Sort features by occurrence
        sorted_features = sorted(feature_stats.items(),
                               key=lambda x: x[1]['total_occurrences'],
                               reverse=True)[:15]

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 14))
        fig.suptitle(title, fontsize=16, fontweight='bold')

        # Plot 1: Top features by count with mnemonic labels
        feature_ids = [item[0] for item in sorted_features]
        counts = [item[1]['total_occurrences'] for item in sorted_features]
        readable_labels = [self._get_feature_label(fid).replace('\n', ' ') for fid in feature_ids]

        bars1 = ax1.bar(range(len(feature_ids)), counts, color='steelblue', edgecolor='black', linewidth=0.5)
        ax1.set_xlabel("Linguistic Features (Mnemonics)", fontweight='bold')
        ax1.set_ylabel("Event Count", fontweight='bold')
        ax1.set_title("Top 15 Features by Count", fontweight='bold')
        ax1.set_xticks(range(len(feature_ids)))
        ax1.set_xticklabels(readable_labels, rotation=45, ha='right', fontsize=9)

        # Add value labels on bars
        for bar, count in zip(bars1, counts):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(counts)*0.01,
                    f'{count:,}', ha='center', va='bottom', fontsize=8, fontweight='bold')

        # Improve y-axis scaling
        if counts:
            y_range = max(counts) - min(counts)
            if y_range < max(counts) * 0.1:
                y_min = max(0, min(counts) - y_range * 0.1)
                ax1.set_ylim(y_min, max(counts) * 1.15)

        ax1.grid(axis='y', alpha=0.3, linestyle='--')

        # Plot 2: Percentage distribution
        percentages = [item[1]['percentage_of_total'] for item in sorted_features]
        bars2 = ax2.bar(range(len(feature_ids)), percentages, color='lightcoral', edgecolor='black', linewidth=0.5)
        ax2.set_xlabel("Linguistic Features (Mnemonics)", fontweight='bold')
        ax2.set_ylabel("Percentage of Total Events (%)", fontweight='bold')
        ax2.set_title("Feature Distribution (%)")
        ax2.set_xticks(range(len(feature_ids)))
        ax2.set_xticklabels(feature_ids, rotation=45, ha='right')

        # Plot 3: Coverage across newspapers
        newspaper_coverage = [item[1]['newspapers_found_in'] for item in sorted_features]
        ax3.bar(range(len(feature_ids)), newspaper_coverage, color='mediumseagreen')
        ax3.set_xlabel("Features")
        ax3.set_ylabel("Number of Newspapers")
        ax3.set_title("Feature Coverage Across Newspapers")
        ax3.set_xticks(range(len(feature_ids)))
        ax3.set_xticklabels(feature_ids, rotation=45, ha='right')

        # Plot 4: Coverage across parse types
        parse_type_coverage = [item[1]['parse_types_found_in'] for item in sorted_features]
        ax4.bar(range(len(feature_ids)), parse_type_coverage, color='mediumpurple')
        ax4.set_xlabel("Features")
        ax4.set_ylabel("Number of Parse Types")
        ax4.set_title("Feature Coverage Across Parse Types")
        ax4.set_xticks(range(len(feature_ids)))
        ax4.set_xticklabels(feature_ids, rotation=45, ha='right')

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved top features analysis to {filename}")

    def plot_cross_dimensional_analysis(self, cross_data: Dict, title: str, filename: str):
        """Create enhanced visualization of cross-dimensional analysis with mnemonics."""
        if not cross_data:
            return

        # Prepare data
        plot_data = []
        for combination, data in cross_data.items():
            newspaper, parse_type = combination.split('_', 1)
            for feature_id, count in data['feature_counts'].items():
                plot_data.append({
                    'combination': combination,
                    'newspaper': newspaper,
                    'parse_type': parse_type,
                    'feature_id': feature_id,
                    'count': count
                })

        if not plot_data:
            return

        import pandas as pd
        df = pd.DataFrame(plot_data)

        # Create enhanced subplot layout for each newspaper-parse_type combination
        combinations = df['combination'].unique()
        n_combinations = len(combinations)

        if n_combinations <= 2:
            fig, axes = plt.subplots(1, n_combinations, figsize=(12 * n_combinations, 8))
        else:
            fig, axes = plt.subplots(2, 2, figsize=(20, 16))

        fig.suptitle(title, fontsize=18, fontweight='bold', y=0.98)

        if n_combinations == 1:
            axes = [axes]
        elif n_combinations <= 2:
            pass  # axes is already correct
        else:
            axes = axes.flatten()

        for i, combination in enumerate(combinations[:4]):  # Limit to 4 combinations
            if i >= len(axes):
                break

            combo_data = df[df['combination'] == combination]
            top_features = combo_data.nlargest(10, 'count')

            # Enhanced styling for each subplot
            colors = sns.color_palette("Set2", len(top_features))
            bars = axes[i].bar(range(len(top_features)), top_features['count'],
                              color=colors, edgecolor='black', linewidth=0.5)

            # Enhanced titles and labels with mnemonics
            axes[i].set_title(f"{combination.replace('_', ' + ')}", fontweight='bold', fontsize=12)
            axes[i].set_xlabel("Top Linguistic Features", fontweight='bold', fontsize=10)
            axes[i].set_ylabel("Event Count", fontweight='bold', fontsize=10)

            # Use mnemonic labels
            readable_labels = [self._get_feature_label(feat).replace('\n', ' ')
                             for feat in top_features['feature_id']]
            axes[i].set_xticks(range(len(top_features)))
            axes[i].set_xticklabels(readable_labels, rotation=45, ha='right', fontsize=9)

            # Add value labels on bars
            for bar, count in zip(bars, top_features['count']):
                axes[i].text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(top_features['count'])*0.01,
                           f'{count:,}', ha='center', va='bottom', fontsize=8, fontweight='bold')

            # Add grid for better readability
            axes[i].grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)

        # Hide unused subplots
        for j in range(len(combinations), len(axes)):
            if j < len(axes):
                axes[j].set_visible(False)

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved enhanced cross-dimensional analysis to {filename}")

    def plot_feature_category_distribution(self, feature_stats: Dict, title: str, filename: str):
        """Create visualization showing distribution by feature categories."""
        # Categorize features based on their IDs
        categories = {
            'Lexical': ['FW-DEL', 'FW-ADD', 'C-DEL', 'C-ADD', 'POS-CHG', 'LEMMA-CHG', 'FORM-CHG'],
            'Syntactic': ['DEP-REL-CHG', 'HEAD-CHG', 'CONST-REM', 'CONST-ADD', 'CONST-MOV'],
            'Morphological': ['FEAT-CHG', 'VERB-FORM-CHG'],
            'Word Order': ['TOKEN-REORDER'],
            'Clause Level': ['CLAUSE-TYPE-CHG'],
            'Structural': ['TED', 'LENGTH-CHG']
        }

        category_counts = {}
        category_percentages = {}

        for category, feature_list in categories.items():
            total_count = sum(feature_stats.get(feat, {}).get('total_occurrences', 0)
                            for feat in feature_list)
            total_percentage = sum(feature_stats.get(feat, {}).get('percentage_of_total', 0)
                                 for feat in feature_list)

            category_counts[category] = total_count
            category_percentages[category] = total_percentage

        # Create enhanced pie chart and bar chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle(title, fontsize=16, fontweight='bold')

        # Enhanced pie chart with better colors and formatting
        colors = ['steelblue', 'lightcoral', 'mediumseagreen', 'gold', 'mediumpurple', 'orange']
        wedges, texts, autotexts = ax1.pie(category_counts.values(),
                                          labels=category_counts.keys(),
                                          autopct='%1.1f%%',
                                          startangle=90,
                                          colors=colors,
                                          explode=[0.05] * len(category_counts),  # Small separation
                                          shadow=True)

        # Enhance text formatting
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)

        for text in texts:
            text.set_fontsize(11)
            text.set_fontweight('bold')

        ax1.set_title("Distribution by Feature Category (Counts)", fontweight='bold', fontsize=12)

        # Enhanced bar chart
        bars = ax2.bar(category_counts.keys(), category_counts.values(),
                      color=colors, edgecolor='black', linewidth=0.8)
        ax2.set_title("Feature Category Frequencies", fontweight='bold', fontsize=12)
        ax2.set_xlabel("Linguistic Category", fontweight='bold', fontsize=11)
        ax2.set_ylabel("Total Event Count", fontweight='bold', fontsize=11)
        ax2.tick_params(axis='x', rotation=45, labelsize=10)
        ax2.tick_params(axis='y', labelsize=10)

        # Add value labels on bars
        for bar, count in zip(bars, category_counts.values()):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(category_counts.values())*0.01,
                    f'{count:,}', ha='center', va='bottom', fontsize=9, fontweight='bold')

        # Add grid for better readability
        ax2.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)

        # Add summary statistics
        total_events = sum(category_counts.values())
        stats_text = f"Total Events: {total_events:,}\nCategories: {len(category_counts)}"
        ax2.text(0.98, 0.98, stats_text, transform=ax2.transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8),
                verticalalignment='top', horizontalalignment='right', fontsize=10)

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved enhanced feature category distribution to {filename}")

    def create_statistical_summary_visualizations(self, analysis: Dict, summary: Dict):
        """Create comprehensive statistical summary visualizations for all dimensional combinations."""
        print("Creating statistical summary visualizations...")

        # 1. Statistical comparison across newspapers
        if 'by_newspaper' in analysis and analysis['by_newspaper']:
            self.plot_newspaper_statistical_comparison(
                analysis['by_newspaper'],
                summary.get('by_newspaper', {}),
                "Statistical Comparison Across Newspapers",
                "newspaper_statistical_comparison.png"
            )

        # 2. Parse type statistical differences
        if 'by_parse_type' in analysis and analysis['by_parse_type']:
            self.plot_parse_type_statistical_differences(
                analysis['by_parse_type'],
                summary.get('by_parse_type', {}),
                "Statistical Differences by Parse Type",
                "parse_type_statistical_differences.png"
            )

        # 3. Cross-dimensional statistical variance
        if 'cross_analysis' in analysis and analysis['cross_analysis']:
            self.plot_cross_dimensional_statistics(
                analysis['cross_analysis'],
                summary.get('cross_analysis', {}),
                "Cross-Dimensional Statistical Analysis",
                "cross_dimensional_statistics.png"
            )

        # 4. Feature distribution statistics
        if 'global' in analysis and 'feature_counts' in analysis['global']:
            self.plot_feature_distribution_statistics(
                analysis['global']['feature_counts'],
                summary.get('global', {}),
                "Feature Distribution Statistics",
                "feature_distribution_statistics.png"
            )

        # 5. Comparative variance analysis
        self.plot_comparative_variance_analysis(
            analysis, summary,
            "Comparative Variance Analysis Across All Dimensions",
            "comparative_variance_analysis.png"
        )

        # 6. Statistical significance heatmap
        self.plot_statistical_significance_heatmap(
            analysis, summary,
            "Statistical Significance Across Combinations",
            "statistical_significance_heatmap.png"
        )

        print("Statistical summary visualizations completed!")

    def plot_newspaper_statistical_comparison(self, newspaper_data: Dict, newspaper_summary: Dict, title: str, filename: str):
        """Create enhanced statistical comparison charts across newspapers with improved formatting."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 14))
        fig.suptitle(title, fontsize=18, fontweight='bold')

        newspapers = list(newspaper_data.keys())
        colors = sns.color_palette("Set2", len(newspapers))

        # 1. Enhanced total events comparison
        total_events = [newspaper_data[np]['total_events'] for np in newspapers]
        bars1 = ax1.bar(newspapers, total_events, color=colors, edgecolor='black', linewidth=0.8)
        ax1.set_title("Total Events by Newspaper", fontweight='bold', fontsize=14)
        ax1.set_xlabel("Newspaper", fontweight='bold', fontsize=12)
        ax1.set_ylabel("Number of Events", fontweight='bold', fontsize=12)
        ax1.tick_params(axis='x', rotation=45, labelsize=11)
        ax1.tick_params(axis='y', labelsize=11)

        # Add value labels on bars
        for bar, count in zip(bars1, total_events):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(total_events)*0.01,
                    f'{count:,}', ha='center', va='bottom', fontsize=10, fontweight='bold')

        ax1.grid(axis='y', alpha=0.3, linestyle='--')

        # 2. Enhanced average events per sentence
        avg_events = []
        for np in newspapers:
            total = newspaper_data[np]['total_events']
            # Estimate sentences (this could be refined with actual sentence count)
            estimated_sentences = max(1, total // 10)  # Rough estimate
            avg_events.append(total / estimated_sentences)

        bars2 = ax2.bar(newspapers, avg_events, color=colors, edgecolor='black', linewidth=0.8)
        ax2.set_title("Average Events per Sentence", fontweight='bold', fontsize=14)
        ax2.set_xlabel("Newspaper", fontweight='bold', fontsize=12)
        ax2.set_ylabel("Events/Sentence (Estimated)", fontweight='bold', fontsize=12)
        ax2.tick_params(axis='x', rotation=45, labelsize=11)
        ax2.tick_params(axis='y', labelsize=11)

        # Add value labels
        for bar, avg in zip(bars2, avg_events):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(avg_events)*0.01,
                    f'{avg:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

        ax2.grid(axis='y', alpha=0.3, linestyle='--')

        # 3. Enhanced feature diversity (unique features per newspaper)
        feature_diversity = [len(newspaper_data[np]['feature_counts']) for np in newspapers]
        bars3 = ax3.bar(newspapers, feature_diversity, color=colors, edgecolor='black', linewidth=0.8)
        ax3.set_title("Feature Diversity by Newspaper", fontweight='bold', fontsize=14)
        ax3.set_xlabel("Newspaper", fontweight='bold', fontsize=12)
        ax3.set_ylabel("Number of Unique Features", fontweight='bold', fontsize=12)
        ax3.tick_params(axis='x', rotation=45)

        # 4. Top feature comparison
        top_features_per_newspaper = {}
        for np in newspapers:
            feature_counts = newspaper_data[np]['feature_counts']
            if feature_counts:
                top_feature = max(feature_counts.items(), key=lambda x: x[1])
                top_features_per_newspaper[np] = top_feature[1]

        if top_features_per_newspaper:
            ax4.bar(top_features_per_newspaper.keys(), top_features_per_newspaper.values(),
                   color=['darkblue', 'darkred', 'darkgreen'])
            ax4.set_title("Most Frequent Feature Count by Newspaper")
            ax4.set_ylabel("Count of Most Frequent Feature")
            ax4.tick_params(axis='x', rotation=45)

        plt.suptitle(title)
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved newspaper statistical comparison to {filename}")

    def plot_parse_type_statistical_differences(self, parse_type_data: Dict, parse_summary: Dict, title: str, filename: str):
        """Create statistical difference visualizations by parse type."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        parse_types = list(parse_type_data.keys())

        # 1. Events distribution by parse type
        events_by_type = [parse_type_data[pt]['total_events'] for pt in parse_types]
        ax1.pie(events_by_type, labels=parse_types, autopct='%1.1f%%', startangle=90)
        ax1.set_title("Event Distribution by Parse Type")

        # 2. Feature coverage comparison
        coverage_data = []
        for pt in parse_types:
            feature_counts = parse_type_data[pt]['feature_counts']
            coverage_data.append(len([f for f, count in feature_counts.items() if count > 0]))

        ax2.bar(parse_types, coverage_data, color=['skyblue', 'lightgreen'])
        ax2.set_title("Feature Coverage by Parse Type")
        ax2.set_ylabel("Number of Active Features")
        ax2.tick_params(axis='x', rotation=45)

        # 3. Average event intensity
        intensity_data = []
        for pt in parse_types:
            feature_counts = parse_type_data[pt]['feature_counts']
            active_features = [count for count in feature_counts.values() if count > 0]
            avg_intensity = np.mean(active_features) if active_features else 0
            intensity_data.append(avg_intensity)

        ax3.bar(parse_types, intensity_data, color=['salmon', 'lightblue'])
        ax3.set_title("Average Event Intensity by Parse Type")
        ax3.set_ylabel("Average Events per Active Feature")
        ax3.tick_params(axis='x', rotation=45)

        # 4. Feature variance comparison
        variance_data = []
        for pt in parse_types:
            feature_counts = parse_type_data[pt]['feature_counts']
            counts = list(feature_counts.values())
            variance = np.var(counts) if len(counts) > 1 else 0
            variance_data.append(variance)

        ax4.bar(parse_types, variance_data, color=['mediumorchid', 'lightcoral'])
        ax4.set_title("Feature Count Variance by Parse Type")
        ax4.set_ylabel("Variance in Feature Counts")
        ax4.tick_params(axis='x', rotation=45)

        plt.suptitle(title)
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved parse type statistical differences to {filename}")

    def plot_cross_dimensional_statistics(self, cross_data: Dict, cross_summary: Dict, title: str, filename: str):
        """Create cross-dimensional statistical analysis visualizations."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        # Prepare data for cross-dimensional analysis
        combinations = []
        total_events = []
        unique_features = []
        max_feature_counts = []

        for combo_key, combo_data in cross_data.items():
            combinations.append(combo_key)
            total_events.append(combo_data['total_events'])
            unique_features.append(len(combo_data['feature_counts']))

            if combo_data['feature_counts']:
                max_count = max(combo_data['feature_counts'].values())
                max_feature_counts.append(max_count)
            else:
                max_feature_counts.append(0)

        # 1. Total events across combinations
        ax1.bar(range(len(combinations)), total_events, color=plt.cm.viridis(np.linspace(0, 1, len(combinations))))
        ax1.set_title("Total Events Across Combinations")
        ax1.set_ylabel("Number of Events")
        ax1.set_xticks(range(len(combinations)))
        ax1.set_xticklabels(combinations, rotation=45, ha='right')

        # 2. Feature diversity across combinations
        ax2.bar(range(len(combinations)), unique_features, color=plt.cm.plasma(np.linspace(0, 1, len(combinations))))
        ax2.set_title("Feature Diversity Across Combinations")
        ax2.set_ylabel("Number of Unique Features")
        ax2.set_xticks(range(len(combinations)))
        ax2.set_xticklabels(combinations, rotation=45, ha='right')

        # 3. Maximum feature intensity
        ax3.bar(range(len(combinations)), max_feature_counts, color=plt.cm.inferno(np.linspace(0, 1, len(combinations))))
        ax3.set_title("Peak Feature Intensity Across Combinations")
        ax3.set_ylabel("Max Feature Count")
        ax3.set_xticks(range(len(combinations)))
        ax3.set_xticklabels(combinations, rotation=45, ha='right')

        # 4. Combination efficiency (events per unique feature)
        efficiency = [te/uf if uf > 0 else 0 for te, uf in zip(total_events, unique_features)]
        ax4.bar(range(len(combinations)), efficiency, color=plt.cm.coolwarm(np.linspace(0, 1, len(combinations))))
        ax4.set_title("Combination Efficiency (Events per Unique Feature)")
        ax4.set_ylabel("Events/Feature Ratio")
        ax4.set_xticks(range(len(combinations)))
        ax4.set_xticklabels(combinations, rotation=45, ha='right')

        plt.suptitle(title)
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved cross-dimensional statistics to {filename}")

    def plot_feature_distribution_statistics(self, feature_counts: Dict, global_summary: Dict, title: str, filename: str):
        """Create feature distribution statistical visualizations."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        # Prepare data
        features = list(feature_counts.keys())
        counts = list(feature_counts.values())

        if not counts:
            print("No feature data available for distribution statistics")
            return

        # 1. Feature count distribution (histogram)
        ax1.hist(counts, bins=min(20, len(counts)), alpha=0.7, color='steelblue', edgecolor='black')
        ax1.set_title("Distribution of Feature Counts")
        ax1.set_xlabel("Feature Count")
        ax1.set_ylabel("Frequency")
        ax1.axvline(np.mean(counts), color='red', linestyle='--', label=f'Mean: {np.mean(counts):.1f}')
        ax1.axvline(np.median(counts), color='green', linestyle='--', label=f'Median: {np.median(counts):.1f}')
        ax1.legend()

        # 2. Cumulative distribution
        sorted_counts = sorted(counts)
        cumulative = np.cumsum(sorted_counts) / np.sum(sorted_counts) * 100
        ax2.plot(sorted_counts, cumulative, marker='o', markersize=3, color='darkblue')
        ax2.set_title("Cumulative Distribution of Feature Counts")
        ax2.set_xlabel("Feature Count")
        ax2.set_ylabel("Cumulative Percentage")
        ax2.grid(True, alpha=0.3)

        # 3. Box plot of feature counts
        ax3.boxplot(counts, vert=True, patch_artist=True,
                   boxprops=dict(facecolor='lightblue', alpha=0.7))
        ax3.set_title("Feature Count Distribution (Box Plot)")
        ax3.set_ylabel("Feature Count")
        ax3.set_xticklabels(['All Features'])

        # 4. Top vs Bottom features comparison
        n_top = min(5, len(counts))
        top_features = sorted(zip(features, counts), key=lambda x: x[1], reverse=True)[:n_top]
        bottom_features = sorted(zip(features, counts), key=lambda x: x[1])[:n_top]

        top_names, top_counts = zip(*top_features) if top_features else ([], [])
        bottom_names, bottom_counts = zip(*bottom_features) if bottom_features else ([], [])

        x_pos = np.arange(n_top)
        width = 0.35

        if top_counts and bottom_counts:
            ax4.bar(x_pos - width/2, top_counts, width, label='Top Features', color='darkgreen', alpha=0.8)
            ax4.bar(x_pos + width/2, bottom_counts, width, label='Bottom Features', color='darkred', alpha=0.8)
            ax4.set_title("Top vs Bottom Features")
            ax4.set_ylabel("Count")
            ax4.set_xticks(x_pos)
            ax4.set_xticklabels([f"Pos {i+1}" for i in range(n_top)])
            ax4.legend()

        plt.suptitle(title)
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved feature distribution statistics to {filename}")

    def plot_comparative_variance_analysis(self, analysis: Dict, summary: Dict, title: str, filename: str):
        """Create comparative variance analysis across all dimensions."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        # Collect variance data from different dimensions
        dimensions = ['global', 'by_newspaper', 'by_parse_type', 'cross_analysis']
        dimension_variances = {}
        dimension_means = {}
        dimension_stds = {}

        for dim in dimensions:
            if dim in analysis and analysis[dim]:
                if dim == 'global':
                    if 'feature_counts' in analysis[dim]:
                        counts = list(analysis[dim]['feature_counts'].values())
                        if counts:
                            dimension_variances[dim] = np.var(counts)
                            dimension_means[dim] = np.mean(counts)
                            dimension_stds[dim] = np.std(counts)
                elif dim in ['by_newspaper', 'by_parse_type']:
                    all_counts = []
                    for sub_key, sub_data in analysis[dim].items():
                        if 'feature_counts' in sub_data:
                            all_counts.extend(list(sub_data['feature_counts'].values()))
                    if all_counts:
                        dimension_variances[dim] = np.var(all_counts)
                        dimension_means[dim] = np.mean(all_counts)
                        dimension_stds[dim] = np.std(all_counts)
                elif dim == 'cross_analysis':
                    all_counts = []
                    for combo_data in analysis[dim].values():
                        if 'feature_counts' in combo_data:
                            all_counts.extend(list(combo_data['feature_counts'].values()))
                    if all_counts:
                        dimension_variances[dim] = np.var(all_counts)
                        dimension_means[dim] = np.mean(all_counts)
                        dimension_stds[dim] = np.std(all_counts)

        # 1. Variance comparison across dimensions
        if dimension_variances:
            dims = list(dimension_variances.keys())
            variances = list(dimension_variances.values())
            ax1.bar(dims, variances, color=['steelblue', 'lightcoral', 'mediumseagreen', 'gold'])
            ax1.set_title("Variance Across Dimensions")
            ax1.set_ylabel("Variance")
            ax1.tick_params(axis='x', rotation=45)

        # 2. Mean comparison across dimensions
        if dimension_means:
            dims = list(dimension_means.keys())
            means = list(dimension_means.values())
            ax2.bar(dims, means, color=['purple', 'orange', 'teal', 'crimson'])
            ax2.set_title("Mean Values Across Dimensions")
            ax2.set_ylabel("Mean Count")
            ax2.tick_params(axis='x', rotation=45)

        # 3. Standard deviation comparison
        if dimension_stds:
            dims = list(dimension_stds.keys())
            stds = list(dimension_stds.values())
            ax3.bar(dims, stds, color=['navy', 'maroon', 'darkgreen', 'darkgoldenrod'])
            ax3.set_title("Standard Deviation Across Dimensions")
            ax3.set_ylabel("Standard Deviation")
            ax3.tick_params(axis='x', rotation=45)

        # 4. Coefficient of variation (CV = std/mean)
        if dimension_means and dimension_stds:
            cvs = {dim: dimension_stds[dim]/dimension_means[dim] if dimension_means[dim] > 0 else 0
                   for dim in dimension_means.keys() if dim in dimension_stds}
            if cvs:
                dims = list(cvs.keys())
                cv_values = list(cvs.values())
                ax4.bar(dims, cv_values, color=['darkblue', 'darkred', 'darkgreen', 'darkorange'])
                ax4.set_title("Coefficient of Variation Across Dimensions")
                ax4.set_ylabel("CV (Std/Mean)")
                ax4.tick_params(axis='x', rotation=45)

        plt.suptitle(title)
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved comparative variance analysis to {filename}")

    def plot_statistical_significance_heatmap(self, analysis: Dict, summary: Dict, title: str, filename: str):
        """Create statistical significance heatmap across combinations."""
        # Collect data for heatmap
        newspapers = []
        parse_types = []
        combinations_data = {}

        # Extract newspaper and parse type combinations
        if 'cross_analysis' in analysis:
            for combo_key, combo_data in analysis['cross_analysis'].items():
                if '_' in combo_key:
                    parts = combo_key.split('_')
                    if len(parts) >= 2:
                        newspaper = parts[0]
                        parse_type = '_'.join(parts[1:])

                        if newspaper not in newspapers:
                            newspapers.append(newspaper)
                        if parse_type not in parse_types:
                            parse_types.append(parse_type)

                        combinations_data[combo_key] = combo_data.get('total_events', 0)

        if not newspapers or not parse_types:
            print("Insufficient cross-combination data for heatmap")
            return

        # Create matrix for heatmap
        matrix = np.zeros((len(newspapers), len(parse_types)))

        for i, newspaper in enumerate(newspapers):
            for j, parse_type in enumerate(parse_types):
                combo_key = f"{newspaper}_{parse_type}"
                if combo_key in combinations_data:
                    matrix[i, j] = combinations_data[combo_key]

        # Create heatmap
        fig, ax = plt.subplots(figsize=(12, 8))

        im = ax.imshow(matrix, cmap='viridis', aspect='auto')

        # Add colorbar
        cbar = plt.colorbar(im)
        cbar.set_label('Number of Events')

        # Set ticks and labels
        ax.set_xticks(np.arange(len(parse_types)))
        ax.set_yticks(np.arange(len(newspapers)))
        ax.set_xticklabels(parse_types, rotation=45, ha='right')
        ax.set_yticklabels(newspapers)

        # Add text annotations
        for i in range(len(newspapers)):
            for j in range(len(parse_types)):
                text = ax.text(j, i, f'{int(matrix[i, j])}',
                             ha="center", va="center", color="white", fontweight='bold')

        ax.set_title(title)
        ax.set_xlabel('Parse Type')
        ax.set_ylabel('Newspaper')

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved statistical significance heatmap to {filename}")

    def create_feature_value_visualizations(self, feature_value_analysis: Dict[str, Any]):
        """Create comprehensive visualizations for feature-value analysis."""
        print("Creating feature-value visualizations...")

        # 1. Overall transformation pattern visualization
        self.plot_transformation_patterns_overview(
            feature_value_analysis['transformation_patterns'],
            "Transformation Patterns Overview",
            "transformation_patterns_overview.png"
        )

        # 2. Value diversity analysis
        self.plot_value_diversity_analysis(
            feature_value_analysis['value_statistics'],
            "Value Diversity Analysis",
            "value_diversity_analysis.png"
        )

        # 3. Top transformations per feature
        self.plot_top_transformations_per_feature(
            feature_value_analysis['global_feature_values'],
            "Top Transformations per Feature",
            "top_transformations_per_feature.png"
        )

        # 4. Transformation entropy analysis
        self.plot_transformation_entropy(
            feature_value_analysis['value_statistics'],
            "Transformation Entropy Analysis",
            "transformation_entropy.png"
        )

        # 5. Individual feature visualizations for all features
        self.create_individual_feature_visualizations(
            feature_value_analysis['global_feature_values'],
            feature_value_analysis['value_statistics']
        )

        print("Feature-value visualizations completed!")

    def plot_transformation_patterns_overview(self, transformation_patterns: Dict, title: str, filename: str):
        """Create overview of transformation patterns."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        # 1. Transformation types distribution
        pattern_types = transformation_patterns['transformation_types']
        type_counts = {ptype: len(transformations) for ptype, transformations in pattern_types.items()}

        ax1.pie(type_counts.values(), labels=type_counts.keys(), autopct='%1.1f%%', startangle=90)
        ax1.set_title("Distribution of Transformation Types")

        # 2. Most active features (by transformation count)
        feature_activity = {}
        for feature_id, transformations in transformation_patterns['most_common_transformations'].items():
            feature_activity[feature_id] = sum(count for _, count in transformations)

        top_features = sorted(feature_activity.items(), key=lambda x: x[1], reverse=True)[:10]
        if top_features:
            features, counts = zip(*top_features)
            ax2.barh(range(len(features)), counts, color='steelblue')
            ax2.set_yticks(range(len(features)))
            ax2.set_yticklabels(features)
            ax2.set_title("Most Active Features (by Transformation Count)")
            ax2.set_xlabel("Total Transformations")

        # 3. Deletion vs Addition vs Change patterns
        deletion_count = sum(transformation_patterns['transformation_types']['deletions'].values())
        addition_count = sum(transformation_patterns['transformation_types']['additions'].values())
        change_count = sum(transformation_patterns['transformation_types']['changes'].values())

        categories = ['Deletions', 'Additions', 'Changes']
        counts = [deletion_count, addition_count, change_count]
        ax3.bar(categories, counts, color=['red', 'green', 'blue'], alpha=0.7)
        ax3.set_title("Deletion vs Addition vs Change Patterns")
        ax3.set_ylabel("Count")

        # 4. Top 10 most frequent transformations overall
        all_transformations = {}
        for pattern_type, transformations in pattern_types.items():
            all_transformations.update(transformations)

        top_transformations = sorted(all_transformations.items(), key=lambda x: x[1], reverse=True)[:10]
        if top_transformations:
            trans_names = [t[0][:20] + '...' if len(t[0]) > 20 else t[0] for t, _ in top_transformations]
            trans_counts = [count for _, count in top_transformations]
            ax4.barh(range(len(trans_names)), trans_counts, color='orange')
            ax4.set_yticks(range(len(trans_names)))
            ax4.set_yticklabels(trans_names, fontsize=8)
            ax4.set_title("Top 10 Most Frequent Transformations")
            ax4.set_xlabel("Count")

        plt.suptitle(title)
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved transformation patterns overview to {filename}")

    def plot_value_diversity_analysis(self, value_statistics: Dict, title: str, filename: str):
        """Create value diversity analysis visualization."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        features = list(value_statistics.keys())
        if not features:
            print("No value statistics available for diversity analysis")
            return

        # 1. Canonical vs Headline Value Diversity
        canonical_diversity = [value_statistics[f]['canonical_value_diversity'] for f in features]
        headline_diversity = [value_statistics[f]['headline_value_diversity'] for f in features]

        x = np.arange(len(features))
        width = 0.35

        ax1.bar(x - width/2, canonical_diversity, width, label='Canonical', alpha=0.8)
        ax1.bar(x + width/2, headline_diversity, width, label='Headline', alpha=0.8)
        ax1.set_xlabel('Features')
        ax1.set_ylabel('Value Diversity')
        ax1.set_title('Canonical vs Headline Value Diversity')
        ax1.set_xticks(x)
        ax1.set_xticklabels(features, rotation=45, ha='right')
        ax1.legend()

        # 2. Transformation Entropy
        entropy_values = [value_statistics[f]['transformation_entropy'] for f in features]
        ax2.bar(features, entropy_values, color='green', alpha=0.7)
        ax2.set_title('Transformation Entropy by Feature')
        ax2.set_ylabel('Entropy')
        ax2.tick_params(axis='x', rotation=45)

        # 3. Top3 Concentration Ratio
        concentration_ratios = [value_statistics[f]['top3_concentration_ratio'] for f in features]
        ax3.bar(features, concentration_ratios, color='purple', alpha=0.7)
        ax3.set_title('Top 3 Transformation Concentration')
        ax3.set_ylabel('Concentration Ratio')
        ax3.tick_params(axis='x', rotation=45)

        # 4. Unique Transformation Types
        unique_types = [value_statistics[f]['unique_transformation_types'] for f in features]
        ax4.bar(features, unique_types, color='orange', alpha=0.7)
        ax4.set_title('Unique Transformation Types per Feature')
        ax4.set_ylabel('Number of Unique Types')
        ax4.tick_params(axis='x', rotation=45)

        plt.suptitle(title)
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved value diversity analysis to {filename}")

    def plot_top_transformations_per_feature(self, global_feature_values: Dict, title: str, filename: str):
        """Create visualization of top transformations for each feature."""
        features = list(global_feature_values.keys())
        n_features = len(features)

        if n_features == 0:
            print("No feature data available for transformation visualization")
            return

        # Create subplots (max 6 features per figure)
        features_per_fig = 6
        n_figs = (n_features + features_per_fig - 1) // features_per_fig

        for fig_idx in range(n_figs):
            start_idx = fig_idx * features_per_fig
            end_idx = min(start_idx + features_per_fig, n_features)
            fig_features = features[start_idx:end_idx]

            n_cols = min(3, len(fig_features))
            n_rows = (len(fig_features) + n_cols - 1) // n_cols

            fig, axes = plt.subplots(n_rows, n_cols, figsize=(6*n_cols, 4*n_rows))
            if n_rows == 1 and n_cols == 1:
                axes = [axes]
            elif n_rows == 1 or n_cols == 1:
                axes = axes.flatten()
            else:
                axes = axes.flatten()

            for i, feature_id in enumerate(fig_features):
                if i >= len(axes):
                    break

                transformations = global_feature_values[feature_id]
                if not transformations:
                    axes[i].text(0.5, 0.5, 'No transformations', ha='center', va='center')
                    feature_label = self._get_feature_label(feature_id)
                    axes[i].set_title(f"{feature_label}")
                    continue

                # Get top 10 transformations
                top_transformations = sorted(transformations.items(), key=lambda x: x[1], reverse=True)[:10]
                trans_names = [t[0][:15] + '...' if len(t[0]) > 15 else t[0] for t, _ in top_transformations]
                trans_counts = [count for _, count in top_transformations]

                axes[i].barh(range(len(trans_names)), trans_counts, color=f'C{i}')
                axes[i].set_yticks(range(len(trans_names)))
                axes[i].set_yticklabels(trans_names, fontsize=8)
                feature_label = self._get_feature_label(feature_id)
                axes[i].set_title(f"{feature_label}")
                axes[i].set_xlabel("Count")

            # Hide unused subplots
            for i in range(len(fig_features), len(axes)):
                axes[i].set_visible(False)

            fig_title = f"{title} - Figure {fig_idx + 1}"
            if n_figs > 1:
                fig_filename = f"top_transformations_per_feature_fig{fig_idx + 1}.png"
            else:
                fig_filename = filename

            plt.suptitle(fig_title)
            plt.tight_layout()
            plt.savefig(self.output_dir / fig_filename, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"Saved top transformations figure {fig_idx + 1} to {fig_filename}")

    def plot_transformation_entropy(self, value_statistics: Dict, title: str, filename: str):
        """Create transformation entropy visualization."""
        features = list(value_statistics.keys())
        if not features:
            print("No value statistics available for entropy analysis")
            return

        entropies = [value_statistics[f]['transformation_entropy'] for f in features]
        total_transformations = [value_statistics[f]['total_transformations'] for f in features]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # 1. Entropy vs Total Transformations scatter plot
        ax1.scatter(total_transformations, entropies, alpha=0.7, s=50)
        ax1.set_xlabel('Total Transformations')
        ax1.set_ylabel('Transformation Entropy')
        ax1.set_title('Entropy vs Total Transformations')

        # Add feature labels for high entropy features
        high_entropy_threshold = np.percentile(entropies, 75)
        for i, feature in enumerate(features):
            if entropies[i] > high_entropy_threshold:
                ax1.annotate(feature, (total_transformations[i], entropies[i]),
                           xytext=(5, 5), textcoords='offset points', fontsize=8)

        # 2. Entropy ranking
        entropy_ranking = sorted(zip(features, entropies), key=lambda x: x[1], reverse=True)
        ranked_features, ranked_entropies = zip(*entropy_ranking)

        ax2.barh(range(len(ranked_features)), ranked_entropies, color='purple', alpha=0.7)
        ax2.set_yticks(range(len(ranked_features)))
        ax2.set_yticklabels(ranked_features)
        ax2.set_title('Features Ranked by Transformation Entropy')
        ax2.set_xlabel('Entropy')

        plt.suptitle(title)
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved transformation entropy analysis to {filename}")

    def create_individual_feature_visualizations(self, global_feature_values: Dict, value_statistics: Dict):
        """Create individual detailed visualizations for each feature."""
        print("Creating individual feature visualizations...")

        for feature_id, transformations in global_feature_values.items():
            if not transformations:
                continue

            self.plot_individual_feature_analysis(
                feature_id, transformations, value_statistics.get(feature_id, {}),
                f"feature_analysis_{feature_id}.png"
            )

        print("Individual feature visualizations completed!")

    def plot_individual_feature_analysis(self, feature_id: str, transformations: Dict[str, int],
                                       feature_stats: Dict, filename: str):
        """Create detailed analysis for a single feature."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        # 1. Top transformations bar chart
        top_transformations = sorted(transformations.items(), key=lambda x: x[1], reverse=True)[:15]
        if top_transformations:
            trans_names = [t[0] for t, _ in top_transformations]
            trans_counts = [count for _, count in top_transformations]

            ax1.barh(range(len(trans_names)), trans_counts, color='steelblue')
            ax1.set_yticks(range(len(trans_names)))
            ax1.set_yticklabels(trans_names, fontsize=8)
            feature_label = self._get_feature_label(feature_id)
            ax1.set_title(f"Top Transformations for {feature_label}")
            ax1.set_xlabel("Count")

        # 2. Transformation distribution pie chart (top 8)
        top8_transformations = top_transformations[:8]
        other_count = sum(count for _, count in top_transformations[8:])

        pie_labels = [t[0][:20] for t, _ in top8_transformations]
        pie_counts = [count for _, count in top8_transformations]

        if other_count > 0:
            pie_labels.append('Others')
            pie_counts.append(other_count)

        ax2.pie(pie_counts, labels=pie_labels, autopct='%1.1f%%', startangle=90)
        feature_label = self._get_feature_label(feature_id)
        ax2.set_title(f"Transformation Distribution for {feature_label}")

        # 3. Transformation type breakdown
        deletions = sum(1 for t in transformations.keys() if t.endswith('→ABSENT'))
        additions = sum(1 for t in transformations.keys() if t.startswith('ABSENT→'))
        changes = len(transformations) - deletions - additions

        type_counts = [deletions, additions, changes]
        type_labels = ['Deletions', 'Additions', 'Changes']

        ax3.bar(type_labels, type_counts, color=['red', 'green', 'blue'], alpha=0.7)
        feature_label = self._get_feature_label(feature_id)
        ax3.set_title(f"Transformation Types for {feature_label}")
        ax3.set_ylabel("Count")

        # 4. Feature statistics summary
        stats_text = []
        if feature_stats:
            stats_text.extend([
                f"Total Transformations: {feature_stats.get('total_transformations', 0)}",
                f"Unique Types: {feature_stats.get('unique_transformation_types', 0)}",
                f"Canonical Diversity: {feature_stats.get('canonical_value_diversity', 0)}",
                f"Headline Diversity: {feature_stats.get('headline_value_diversity', 0)}",
                f"Top3 Concentration: {feature_stats.get('top3_concentration_ratio', 0):.3f}",
                f"Entropy: {feature_stats.get('transformation_entropy', 0):.3f}"
            ])

            most_freq = feature_stats.get('most_frequent_transformation')
            if most_freq:
                transformation, count = most_freq
                stats_text.append(f"Most Frequent: {transformation} ({count})")

        ax4.text(0.1, 0.9, '\n'.join(stats_text), transform=ax4.transAxes,
                fontsize=10, verticalalignment='top', fontfamily='monospace')
        feature_label = self._get_feature_label(feature_id)
        ax4.set_title(f"Statistics for {feature_label}")
        ax4.axis('off')

        plt.suptitle(f"Detailed Analysis: {feature_id}")
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()

    def create_ted_visualizations(self, analysis: Dict, summary: Dict):
        """Create comprehensive visualizations for Tree Edit Distance algorithms focusing on complementary structural perspectives."""
        print("Creating TED algorithm structural analysis visualizations...")

        # Extract TED-specific data
        ted_data = self._extract_ted_data(analysis)

        if not ted_data:
            print("No TED data found for visualization")
            return

        # 1. Combined register difference analysis (KEY VISUALIZATION)
        self.plot_ted_register_differences_combined(ted_data,
                                                  "Tree Edit Distance: Register Differences Across Algorithms",
                                                  "ted_register_differences_combined.png")

        # 2. Algorithm agreement analysis
        self.plot_ted_algorithm_agreement(ted_data,
                                        "TED Algorithm Agreement in Detecting Register Differences",
                                        "ted_algorithm_agreement.png")

        # 3. Complementary structural perspectives
        self.plot_ted_complementary_analysis(ted_data,
                                           "TED Algorithms: Complementary Structural Perspectives",
                                           "ted_complementary_analysis.png")

        # 4. Newspaper-specific register patterns
        self.plot_ted_newspaper_register_patterns(ted_data,
                                                "Register Patterns by Newspaper (TED Analysis)",
                                                "ted_newspaper_register_patterns.png")

        # 5. Structural sensitivity analysis
        self.plot_ted_structural_sensitivity(ted_data,
                                           "TED Algorithm Structural Sensitivity Analysis",
                                           "ted_structural_sensitivity.png")

        print("TED structural analysis visualizations completed!")

    def _extract_ted_data(self, analysis: Dict) -> Dict:
        """Extract TED-specific data from analysis results."""
        ted_data = {
            'by_newspaper': {},
            'by_algorithm': {},
            'global_total': 0,
            'algorithm_names': {
                'TED-SIMPLE': 'String-based Approximation',
                'TED-ZHANG-SHASHA': 'Zhang-Shasha (Formal TED)',
                'TED-KLEIN': 'Klein (Pattern Recognition)',
                'TED-RTED': 'RTED (Adaptive Structure)'
            }
        }

        # Extract from global analysis
        if 'global' in analysis:
            global_data = analysis['global']
            for feature_id, count in global_data.items():
                if feature_id.startswith('TED-'):
                    ted_data['by_algorithm'][feature_id] = count
                    ted_data['global_total'] += count

        # Extract from newspaper analysis
        if 'by_newspaper' in analysis:
            for newspaper, newspaper_data in analysis['by_newspaper'].items():
                ted_data['by_newspaper'][newspaper] = {}
                for feature_id, count in newspaper_data.items():
                    if feature_id.startswith('TED-'):
                        ted_data['by_newspaper'][newspaper][feature_id] = count

        return ted_data

    def plot_ted_register_differences_combined(self, ted_data: Dict, title: str, filename: str):
        """KEY VISUALIZATION: Combined register differences showing algorithm agreement and newspaper patterns."""
        fig = plt.figure(figsize=(20, 14))

        # Create a complex grid layout
        gs = fig.add_gridspec(3, 4, height_ratios=[1, 1, 0.8], width_ratios=[1, 1, 1, 0.8])

        fig.suptitle(title, fontsize=18, fontweight='bold', y=0.98)

        # 1. MAIN VISUALIZATION: All newspapers combined (top left)
        ax_main = fig.add_subplot(gs[0, :3])

        if ted_data['by_algorithm']:
            algorithms = list(ted_data['by_algorithm'].keys())
            algorithm_labels = [ted_data['algorithm_names'].get(alg, alg) for alg in algorithms]
            counts = list(ted_data['by_algorithm'].values())

            # Create enhanced bar chart
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'][:len(algorithms)]
            bars = ax_main.bar(algorithm_labels, counts, color=colors,
                              edgecolor='black', linewidth=1.5, alpha=0.8)

            ax_main.set_title("Combined Register Differences: All Newspapers",
                             fontsize=14, fontweight='bold', pad=20)
            ax_main.set_ylabel("Structural Difference Events", fontsize=12, fontweight='bold')
            ax_main.tick_params(axis='x', rotation=15, labelsize=10)

            # Add value labels and percentages
            total = sum(counts)
            for bar, count in zip(bars, counts):
                percentage = (count / total * 100) if total > 0 else 0
                ax_main.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(counts)*0.02,
                           f'{count:,}\n({percentage:.1f}%)', ha='center', va='bottom',
                           fontweight='bold', fontsize=10)

            # Add grid for better readability
            ax_main.grid(axis='y', alpha=0.3, linestyle='--')
            ax_main.set_axisbelow(True)

        # 2. Algorithm Agreement Heatmap (top right)
        ax_agreement = fig.add_subplot(gs[0, 3])

        if ted_data['by_newspaper'] and len(ted_data['by_algorithm']) > 1:
            newspapers = list(ted_data['by_newspaper'].keys())
            algorithms = list(ted_data['by_algorithm'].keys())

            # Create agreement matrix (normalized by newspaper)
            agreement_matrix = []
            for newspaper in newspapers:
                newspaper_data = ted_data['by_newspaper'][newspaper]
                total_newspaper = sum(newspaper_data.values()) if newspaper_data.values() else 1
                row = [newspaper_data.get(alg, 0) / total_newspaper * 100 for alg in algorithms]
                agreement_matrix.append(row)

            im = ax_agreement.imshow(agreement_matrix, cmap='RdYlBu_r', aspect='auto')
            ax_agreement.set_title("Algorithm Agreement\n(% by Newspaper)", fontsize=11, fontweight='bold')
            ax_agreement.set_xticks(range(len(algorithms)))
            ax_agreement.set_xticklabels([alg.replace('TED-', '') for alg in algorithms], rotation=45, fontsize=8)
            ax_agreement.set_yticks(range(len(newspapers)))
            ax_agreement.set_yticklabels(newspapers, fontsize=9)

            # Add percentage annotations
            for i in range(len(newspapers)):
                for j in range(len(algorithms)):
                    value = agreement_matrix[i][j]
                    color = 'white' if value > 50 else 'black'
                    ax_agreement.text(j, i, f'{value:.1f}%', ha='center', va='center',
                                    color=color, fontsize=8, fontweight='bold')

        # 3. Individual newspaper comparisons (middle row)
        newspapers = list(ted_data['by_newspaper'].keys()) if ted_data['by_newspaper'] else []

        for i, newspaper in enumerate(newspapers[:3]):  # Limit to 3 newspapers
            ax_news = fig.add_subplot(gs[1, i])

            newspaper_data = ted_data['by_newspaper'][newspaper]
            if newspaper_data:
                alg_names = [ted_data['algorithm_names'].get(alg, alg) for alg in newspaper_data.keys()]
                alg_counts = list(newspaper_data.values())

                # Create newspaper-specific bars
                bars = ax_news.bar(range(len(alg_names)), alg_counts,
                                  color=colors[:len(alg_names)], alpha=0.7,
                                  edgecolor='black', linewidth=1.0)

                ax_news.set_title(f"{newspaper}\nRegister Differences", fontsize=11, fontweight='bold')
                ax_news.set_xticks(range(len(alg_names)))
                ax_news.set_xticklabels([name.split()[0] for name in alg_names], rotation=45, fontsize=9)
                ax_news.set_ylabel("Events", fontsize=10, fontweight='bold')

                # Add value labels
                for bar, count in zip(bars, alg_counts):
                    if count > 0:
                        ax_news.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(alg_counts)*0.02,
                                   f'{count}', ha='center', va='bottom', fontweight='bold', fontsize=9)

                ax_news.grid(axis='y', alpha=0.3, linestyle='--')

        # 4. Algorithm Consensus Analysis (bottom left, spanning 2 columns)
        ax_consensus = fig.add_subplot(gs[2, :2])

        if ted_data['by_algorithm'] and len(ted_data['by_algorithm']) > 1:
            algorithms = list(ted_data['by_algorithm'].keys())
            counts = list(ted_data['by_algorithm'].values())

            # Calculate consensus metrics
            max_count = max(counts)
            min_count = min(counts)
            consensus_ratio = min_count / max_count if max_count > 0 else 0

            # Create consensus visualization
            normalized_counts = [count / max_count for count in counts]

            bars = ax_consensus.barh(range(len(algorithms)), normalized_counts,
                                   color=['#ff4444' if nc < 0.5 else '#44ff44' if nc > 0.8 else '#ffaa44'
                                         for nc in normalized_counts],
                                   edgecolor='black', linewidth=1.0, alpha=0.8)

            ax_consensus.set_title("Algorithm Consensus in Register Detection", fontsize=12, fontweight='bold')
            ax_consensus.set_yticks(range(len(algorithms)))
            ax_consensus.set_yticklabels([alg.replace('TED-', '') for alg in algorithms], fontsize=10)
            ax_consensus.set_xlabel("Relative Detection Strength", fontsize=11, fontweight='bold')

            # Add consensus interpretation
            for i, (bar, count, norm_count) in enumerate(zip(bars, counts, normalized_counts)):
                label = f'{count:,} ({norm_count:.2f})'
                ax_consensus.text(norm_count + 0.02, bar.get_y() + bar.get_height()/2,
                                label, va='center', fontweight='bold', fontsize=9)

            # Add vertical lines for consensus thresholds
            ax_consensus.axvline(x=0.5, color='red', linestyle='--', alpha=0.7, label='Low Agreement')
            ax_consensus.axvline(x=0.8, color='green', linestyle='--', alpha=0.7, label='High Agreement')
            ax_consensus.legend(loc='lower right', fontsize=9)

        # 5. Summary Statistics (bottom right)
        ax_summary = fig.add_subplot(gs[2, 2:])

        # Calculate comprehensive statistics
        total_events = ted_data['global_total']
        num_algorithms = len(ted_data['by_algorithm'])
        num_newspapers = len(ted_data['by_newspaper'])

        summary_stats = [
            f"REGISTER DIFFERENCE ANALYSIS",
            f"",
            f"Total Structural Events: {total_events:,}",
            f"TED Algorithms: {num_algorithms}",
            f"Newspapers Analyzed: {num_newspapers}",
            f""
        ]

        if ted_data['by_algorithm']:
            counts = list(ted_data['by_algorithm'].values())
            dominant_alg = max(ted_data['by_algorithm'].items(), key=lambda x: x[1])
            summary_stats.extend([
                f"Dominant Algorithm:",
                f"  {ted_data['algorithm_names'].get(dominant_alg[0], dominant_alg[0])}",
                f"  ({dominant_alg[1]:,} events)",
                f"",
                f"Algorithm Agreement:",
                f"  Range: {min(counts):,} - {max(counts):,}",
                f"  Ratio: {min(counts)/max(counts):.3f}" if max(counts) > 0 else "  Ratio: N/A"
            ])

        ax_summary.text(0.05, 0.95, '\n'.join(summary_stats),
                       transform=ax_summary.transAxes, fontsize=10,
                       verticalalignment='top', fontfamily='monospace',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8))
        ax_summary.set_title("Analysis Summary", fontsize=12, fontweight='bold')
        ax_summary.axis('off')

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()

    def plot_ted_algorithm_agreement(self, ted_data: Dict, title: str, filename: str):
        """Analyze agreement between TED algorithms in detecting register differences."""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(title, fontsize=16, fontweight='bold')

        if not ted_data['by_algorithm']:
            for ax in axes.flatten():
                ax.text(0.5, 0.5, 'No TED data available', ha='center', va='center',
                       transform=ax.transAxes, fontsize=14)
            plt.tight_layout()
            plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
            plt.close()
            return

        algorithms = list(ted_data['by_algorithm'].keys())
        algorithm_labels = [ted_data['algorithm_names'].get(alg, alg) for alg in algorithms]
        counts = list(ted_data['by_algorithm'].values())

        # 1. Agreement strength visualization
        if len(counts) > 1:
            max_count = max(counts)
            agreement_scores = [count / max_count for count in counts]

            colors = ['#ff4444' if score < 0.3 else '#ffaa44' if score < 0.7 else '#44ff44'
                     for score in agreement_scores]

            bars = axes[0, 0].bar(algorithm_labels, agreement_scores, color=colors,
                                edgecolor='black', linewidth=1.2, alpha=0.8)
            axes[0, 0].set_title("Algorithm Agreement Strength", fontweight='bold')
            axes[0, 0].set_ylabel("Relative Agreement (0-1)", fontweight='bold')
            axes[0, 0].tick_params(axis='x', rotation=30)
            axes[0, 0].set_ylim(0, 1.1)

            # Add agreement zones
            axes[0, 0].axhline(y=0.3, color='red', linestyle='--', alpha=0.5, label='Low Agreement')
            axes[0, 0].axhline(y=0.7, color='orange', linestyle='--', alpha=0.5, label='Moderate Agreement')
            axes[0, 0].legend()

            for bar, score in zip(bars, agreement_scores):
                axes[0, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                               f'{score:.3f}', ha='center', va='bottom', fontweight='bold')

        # 2. Pairwise algorithm comparison
        if len(algorithms) > 1:
            comparison_data = []
            comparison_labels = []

            for i in range(len(algorithms)):
                for j in range(i+1, len(algorithms)):
                    ratio = min(counts[i], counts[j]) / max(counts[i], counts[j]) if max(counts[i], counts[j]) > 0 else 0
                    comparison_data.append(ratio)
                    alg1_short = algorithms[i].replace('TED-', '')
                    alg2_short = algorithms[j].replace('TED-', '')
                    comparison_labels.append(f"{alg1_short}\nvs\n{alg2_short}")

            bars = axes[0, 1].bar(range(len(comparison_data)), comparison_data,
                                color=sns.color_palette("viridis", len(comparison_data)),
                                edgecolor='black', linewidth=1.0)
            axes[0, 1].set_title("Pairwise Algorithm Agreement", fontweight='bold')
            axes[0, 1].set_ylabel("Agreement Ratio", fontweight='bold')
            axes[0, 1].set_xticks(range(len(comparison_data)))
            axes[0, 1].set_xticklabels(comparison_labels, fontsize=9)

            for bar, ratio in zip(bars, comparison_data):
                axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                               f'{ratio:.3f}', ha='center', va='bottom', fontweight='bold', fontsize=9)

        # 3. Newspaper consistency analysis
        if ted_data['by_newspaper']:
            newspapers = list(ted_data['by_newspaper'].keys())

            # Calculate coefficient of variation for each newspaper
            cv_data = []
            for newspaper in newspapers:
                newspaper_data = ted_data['by_newspaper'][newspaper]
                if newspaper_data:
                    newspaper_counts = [newspaper_data.get(alg, 0) for alg in algorithms]
                    mean_count = np.mean(newspaper_counts)
                    std_count = np.std(newspaper_counts)
                    cv = std_count / mean_count if mean_count > 0 else 0
                    cv_data.append(cv)
                else:
                    cv_data.append(0)

            bars = axes[1, 0].bar(newspapers, cv_data,
                                color=sns.color_palette("plasma", len(newspapers)),
                                edgecolor='black', linewidth=1.0)
            axes[1, 0].set_title("Algorithm Consistency by Newspaper", fontweight='bold')
            axes[1, 0].set_ylabel("Coefficient of Variation", fontweight='bold')
            axes[1, 0].tick_params(axis='x', rotation=45)

            for bar, cv in zip(bars, cv_data):
                consistency = "High" if cv < 0.5 else "Medium" if cv < 1.0 else "Low"
                axes[1, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(cv_data)*0.02,
                               f'{cv:.2f}\n({consistency})', ha='center', va='bottom',
                               fontweight='bold', fontsize=9)

        # 4. Overall agreement summary
        agreement_summary = []
        if len(counts) > 1:
            overall_cv = np.std(counts) / np.mean(counts) if np.mean(counts) > 0 else 0
            min_max_ratio = min(counts) / max(counts) if max(counts) > 0 else 0

            agreement_summary = [
                "ALGORITHM AGREEMENT ANALYSIS",
                "",
                f"Total Algorithms: {len(algorithms)}",
                f"Event Range: {min(counts):,} - {max(counts):,}",
                f"Overall CV: {overall_cv:.3f}",
                f"Min/Max Ratio: {min_max_ratio:.3f}",
                "",
                "INTERPRETATION:",
                f"• CV < 0.5: High Agreement" + (" ✓" if overall_cv < 0.5 else ""),
                f"• CV 0.5-1.0: Moderate Agreement" + (" ✓" if 0.5 <= overall_cv < 1.0 else ""),
                f"• CV > 1.0: Low Agreement" + (" ✓" if overall_cv >= 1.0 else ""),
                "",
                "This indicates algorithms detect",
                "different structural aspects of",
                "register differences (complementary)"
            ]

        axes[1, 1].text(0.05, 0.95, '\n'.join(agreement_summary),
                       transform=axes[1, 1].transAxes, fontsize=10,
                       verticalalignment='top', fontfamily='monospace')
        axes[1, 1].set_title("Agreement Summary", fontweight='bold')
        axes[1, 1].axis('off')

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()

    def plot_ted_complementary_analysis(self, ted_data: Dict, title: str, filename: str):
        """Analyze how TED algorithms provide complementary structural perspectives."""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(title, fontsize=16, fontweight='bold')

        if not ted_data['by_algorithm']:
            for ax in axes.flatten():
                ax.text(0.5, 0.5, 'No TED data available', ha='center', va='center',
                       transform=ax.transAxes, fontsize=14)
            plt.tight_layout()
            plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
            plt.close()
            return

        algorithms = list(ted_data['by_algorithm'].keys())
        algorithm_labels = [ted_data['algorithm_names'].get(alg, alg) for alg in algorithms]
        counts = list(ted_data['by_algorithm'].values())

        # 1. Structural sensitivity radar chart
        categories = ['String Similarity', 'Tree Operations', 'Pattern Recognition', 'Adaptive Detection']

        # Map algorithms to sensitivity scores (0-1) for each category
        sensitivity_mapping = {
            'TED-SIMPLE': [1.0, 0.2, 0.1, 0.3],
            'TED-ZHANG-SHASHA': [0.3, 1.0, 0.5, 0.4],
            'TED-KLEIN': [0.4, 0.8, 1.0, 0.6],
            'TED-RTED': [0.5, 0.9, 0.7, 1.0]
        }

        # Create radar chart
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]  # Complete the circle

        ax_radar = plt.subplot(2, 2, 1, projection='polar')
        ax_radar.set_theta_offset(np.pi / 2)
        ax_radar.set_theta_direction(-1)

        colors_radar = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        for i, algorithm in enumerate(algorithms[:4]):  # Limit to 4 algorithms
            if algorithm in sensitivity_mapping:
                values = sensitivity_mapping[algorithm]
                values += values[:1]  # Complete the circle

                ax_radar.plot(angles, values, 'o-', linewidth=2,
                            label=algorithm.replace('TED-', ''), color=colors_radar[i])
                ax_radar.fill(angles, values, alpha=0.25, color=colors_radar[i])

        ax_radar.set_xticks(angles[:-1])
        ax_radar.set_xticklabels(categories, fontsize=9)
        ax_radar.set_ylim(0, 1)
        ax_radar.set_title("Algorithm Structural Sensitivity", fontweight='bold', pad=20)
        ax_radar.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=9)

        # 2. Complementarity matrix
        if len(algorithms) > 1:
            # Calculate complementarity scores (how different algorithms are)
            complement_matrix = np.zeros((len(algorithms), len(algorithms)))

            for i in range(len(algorithms)):
                for j in range(len(algorithms)):
                    if i != j and algorithms[i] in sensitivity_mapping and algorithms[j] in sensitivity_mapping:
                        sens_i = np.array(sensitivity_mapping[algorithms[i]])
                        sens_j = np.array(sensitivity_mapping[algorithms[j]])
                        # Calculate complementarity as 1 - correlation
                        correlation = np.corrcoef(sens_i, sens_j)[0, 1]
                        complement_matrix[i, j] = 1 - abs(correlation) if not np.isnan(correlation) else 0.5
                    elif i == j:
                        complement_matrix[i, j] = 0

            im = axes[0, 1].imshow(complement_matrix, cmap='RdYlGn', vmin=0, vmax=1)
            axes[0, 1].set_title("Algorithm Complementarity Matrix", fontweight='bold')
            axes[0, 1].set_xticks(range(len(algorithms)))
            axes[0, 1].set_xticklabels([alg.replace('TED-', '') for alg in algorithms], rotation=45, fontsize=9)
            axes[0, 1].set_yticks(range(len(algorithms)))
            axes[0, 1].set_yticklabels([alg.replace('TED-', '') for alg in algorithms], fontsize=9)

            # Add complementarity values
            for i in range(len(algorithms)):
                for j in range(len(algorithms)):
                    value = complement_matrix[i, j]
                    color = 'white' if value > 0.5 else 'black'
                    axes[0, 1].text(j, i, f'{value:.2f}', ha='center', va='center',
                                   color=color, fontweight='bold', fontsize=9)

            plt.colorbar(im, ax=axes[0, 1], label='Complementarity Score (0=Same, 1=Opposite)')

        # 3. Structural aspect coverage
        structural_aspects = {
            'Character-level changes': {'TED-SIMPLE': 0.9, 'TED-ZHANG-SHASHA': 0.3, 'TED-KLEIN': 0.4, 'TED-RTED': 0.5},
            'Node operations': {'TED-SIMPLE': 0.2, 'TED-ZHANG-SHASHA': 0.95, 'TED-KLEIN': 0.8, 'TED-RTED': 0.9},
            'Subtree patterns': {'TED-SIMPLE': 0.1, 'TED-ZHANG-SHASHA': 0.5, 'TED-KLEIN': 0.9, 'TED-RTED': 0.7},
            'Adaptive strategies': {'TED-SIMPLE': 0.0, 'TED-ZHANG-SHASHA': 0.3, 'TED-KLEIN': 0.6, 'TED-RTED': 1.0}
        }

        aspect_names = list(structural_aspects.keys())
        x_pos = np.arange(len(aspect_names))
        bar_width = 0.2

        for i, algorithm in enumerate(algorithms[:4]):
            if algorithm in structural_aspects[aspect_names[0]]:
                values = [structural_aspects[aspect][algorithm] for aspect in aspect_names]
                axes[1, 0].bar(x_pos + i * bar_width, values, bar_width,
                             label=algorithm.replace('TED-', ''), color=colors_radar[i], alpha=0.8)

        axes[1, 0].set_title("Structural Aspect Coverage", fontweight='bold')
        axes[1, 0].set_xlabel("Structural Aspects", fontweight='bold')
        axes[1, 0].set_ylabel("Coverage Score (0-1)", fontweight='bold')
        axes[1, 0].set_xticks(x_pos + bar_width * 1.5)
        axes[1, 0].set_xticklabels(aspect_names, rotation=45, ha='right', fontsize=9)
        axes[1, 0].legend(fontsize=9)
        axes[1, 0].grid(axis='y', alpha=0.3)

        # 4. Algorithm interpretation guide
        interpretation_text = [
            "COMPLEMENTARY ALGORITHM PERSPECTIVES:",
            "",
            "String-based (SIMPLE):",
            "• Fast approximation via character similarity",
            "• Captures surface-level textual changes",
            "• Best for: Quick screening, large datasets",
            "",
            "Zhang-Shasha (ZSHA):",
            "• Formal tree edit distance operations",
            "• Precise structural transformation costs",
            "• Best for: Academic rigor, exact comparisons",
            "",
            "Klein (KLEN):",
            "• Pattern recognition with memoization",
            "• Efficient for repeated structures",
            "• Best for: Similar trees, common patterns",
            "",
            "RTED (RTED):",
            "• Adaptive strategy selection",
            "• Optimized for tree characteristics",
            "• Best for: Mixed datasets, general use"
        ]

        axes[1, 1].text(0.05, 0.95, '\n'.join(interpretation_text),
                       transform=axes[1, 1].transAxes, fontsize=9,
                       verticalalignment='top', fontfamily='monospace')
        axes[1, 1].set_title("Algorithm Interpretation Guide", fontweight='bold')
        axes[1, 1].axis('off')

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()

    def plot_ted_newspaper_register_patterns(self, ted_data: Dict, title: str, filename: str):
        """Plot newspaper-specific register patterns using TED analysis."""
        if not ted_data['by_newspaper']:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No newspaper-specific TED data available',
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title(title)
            plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
            plt.close()
            return

        newspapers = list(ted_data['by_newspaper'].keys())
        n_newspapers = len(newspapers)

        fig, axes = plt.subplots(2, max(2, (n_newspapers + 1) // 2),
                               figsize=(6 * max(2, (n_newspapers + 1) // 2), 12))
        if n_newspapers <= 2:
            axes = axes.reshape(2, -1)
        fig.suptitle(title, fontsize=16, fontweight='bold')

        algorithms = list(ted_data['by_algorithm'].keys()) if ted_data['by_algorithm'] else []
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'][:len(algorithms)]

        for i, newspaper in enumerate(newspapers):
            row = i // axes.shape[1]
            col = i % axes.shape[1]

            if row >= axes.shape[0] or col >= axes.shape[1]:
                break

            newspaper_data = ted_data['by_newspaper'][newspaper]

            # Top row: Algorithm distribution
            if newspaper_data:
                alg_names = [ted_data['algorithm_names'].get(alg, alg) for alg in algorithms
                           if alg in newspaper_data]
                alg_counts = [newspaper_data.get(alg, 0) for alg in algorithms
                            if alg in newspaper_data]
                alg_colors = colors[:len(alg_names)]

                if alg_counts and any(count > 0 for count in alg_counts):
                    # Bar chart
                    bars = axes[0, col].bar(range(len(alg_names)), alg_counts,
                                          color=alg_colors, alpha=0.8,
                                          edgecolor='black', linewidth=1.0)
                    axes[0, col].set_title(f"{newspaper}\nAlgorithm Distribution", fontweight='bold')
                    axes[0, col].set_xticks(range(len(alg_names)))
                    axes[0, col].set_xticklabels([name.split()[0] for name in alg_names],
                                               rotation=45, fontsize=9)
                    axes[0, col].set_ylabel("Register Difference Events", fontweight='bold')

                    # Add value labels
                    for bar, count in zip(bars, alg_counts):
                        if count > 0:
                            axes[0, col].text(bar.get_x() + bar.get_width()/2,
                                            bar.get_height() + max(alg_counts)*0.02,
                                            f'{count}', ha='center', va='bottom',
                                            fontweight='bold', fontsize=10)

                    axes[0, col].grid(axis='y', alpha=0.3, linestyle='--')

                    # Bottom row: Pie chart with percentages
                    total = sum(alg_counts)
                    if total > 0:
                        wedges, texts, autotexts = axes[1, col].pie(
                            alg_counts, labels=[name.split()[0] for name in alg_names],
                            colors=alg_colors, autopct='%1.1f%%', startangle=90,
                            textprops={'fontsize': 9, 'fontweight': 'bold'})
                        axes[1, col].set_title(f"{newspaper}\nAlgorithm Proportions", fontweight='bold')

                        # Add count annotations
                        for autotext, count in zip(autotexts, alg_counts):
                            autotext.set_text(f'{autotext.get_text()}\n({count})')

            else:
                axes[0, col].text(0.5, 0.5, 'No data', ha='center', va='center',
                                transform=axes[0, col].transAxes, fontsize=12)
                axes[0, col].set_title(f"{newspaper}\nNo TED Data", fontweight='bold')
                axes[1, col].text(0.5, 0.5, 'No data', ha='center', va='center',
                                transform=axes[1, col].transAxes, fontsize=12)
                axes[1, col].set_title(f"{newspaper}\nNo Proportions", fontweight='bold')

        # Hide unused subplots
        for i in range(len(newspapers), axes.shape[0] * axes.shape[1]):
            row = i // axes.shape[1]
            col = i % axes.shape[1]
            if row < axes.shape[0] and col < axes.shape[1]:
                axes[row, col].set_visible(False)

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()

    def plot_ted_structural_sensitivity(self, ted_data: Dict, title: str, filename: str):
        """Plot structural sensitivity analysis of TED algorithms."""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(title, fontsize=16, fontweight='bold')

        if not ted_data['by_algorithm']:
            for ax in axes.flatten():
                ax.text(0.5, 0.5, 'No TED data available', ha='center', va='center',
                       transform=ax.transAxes, fontsize=14)
            plt.tight_layout()
            plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
            plt.close()
            return

        algorithms = list(ted_data['by_algorithm'].keys())
        counts = list(ted_data['by_algorithm'].values())

        # 1. Sensitivity ranking
        algorithm_sensitivity = sorted(zip(algorithms, counts), key=lambda x: x[1], reverse=True)
        ranked_algorithms = [alg.replace('TED-', '') for alg, _ in algorithm_sensitivity]
        ranked_counts = [count for _, count in algorithm_sensitivity]

        # Color coding by sensitivity level
        max_count = max(ranked_counts) if ranked_counts else 1
        colors = []
        for count in ranked_counts:
            ratio = count / max_count
            if ratio > 0.8:
                colors.append('#d62728')  # High sensitivity - red
            elif ratio > 0.5:
                colors.append('#ff7f0e')  # Medium sensitivity - orange
            elif ratio > 0.2:
                colors.append('#2ca02c')  # Low sensitivity - green
            else:
                colors.append('#1f77b4')  # Very low sensitivity - blue

        bars = axes[0, 0].bar(range(len(ranked_algorithms)), ranked_counts, color=colors,
                            edgecolor='black', linewidth=1.2, alpha=0.8)
        axes[0, 0].set_title("Algorithm Sensitivity Ranking", fontweight='bold')
        axes[0, 0].set_ylabel("Structural Events Detected", fontweight='bold')
        axes[0, 0].set_xticks(range(len(ranked_algorithms)))
        axes[0, 0].set_xticklabels(ranked_algorithms, rotation=45)

        # Add sensitivity labels
        for i, (bar, count) in enumerate(zip(bars, ranked_counts)):
            sensitivity_level = "High" if count/max_count > 0.8 else "Med" if count/max_count > 0.5 else "Low"
            axes[0, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(ranked_counts)*0.02,
                           f'{count:,}\n({sensitivity_level})', ha='center', va='bottom',
                           fontweight='bold', fontsize=9)

        # 2. Relative sensitivity analysis
        if len(counts) > 1:
            baseline = min(counts)
            relative_sensitivity = [(count - baseline) / baseline * 100 if baseline > 0 else 0 for count in counts]

            bars2 = axes[0, 1].bar([alg.replace('TED-', '') for alg in algorithms], relative_sensitivity,
                                 color=sns.color_palette("viridis", len(algorithms)),
                                 edgecolor='black', linewidth=1.0)
            axes[0, 1].set_title("Relative Sensitivity (% above baseline)", fontweight='bold')
            axes[0, 1].set_ylabel("Relative Increase (%)", fontweight='bold')
            axes[0, 1].tick_params(axis='x', rotation=45)

            for bar, rel_sens in zip(bars2, relative_sensitivity):
                axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(relative_sensitivity)*0.02,
                               f'{rel_sens:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)

        # 3. Cross-newspaper sensitivity variation
        if ted_data['by_newspaper']:
            newspapers = list(ted_data['by_newspaper'].keys())

            # Calculate sensitivity variation across newspapers for each algorithm
            algorithm_variations = {}
            for algorithm in algorithms:
                newspaper_counts = [ted_data['by_newspaper'][newspaper].get(algorithm, 0)
                                  for newspaper in newspapers]
                if newspaper_counts:
                    variation = np.std(newspaper_counts) / np.mean(newspaper_counts) if np.mean(newspaper_counts) > 0 else 0
                    algorithm_variations[algorithm] = variation

            if algorithm_variations:
                alg_names = [alg.replace('TED-', '') for alg in algorithm_variations.keys()]
                variations = list(algorithm_variations.values())

                bars3 = axes[1, 0].bar(alg_names, variations,
                                     color=sns.color_palette("plasma", len(alg_names)),
                                     edgecolor='black', linewidth=1.0)
                axes[1, 0].set_title("Cross-Newspaper Sensitivity Variation", fontweight='bold')
                axes[1, 0].set_ylabel("Coefficient of Variation", fontweight='bold')
                axes[1, 0].tick_params(axis='x', rotation=45)

                for bar, var in zip(bars3, variations):
                    stability = "Stable" if var < 0.5 else "Variable" if var < 1.0 else "Highly Variable"
                    axes[1, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(variations)*0.02,
                                   f'{var:.2f}\n({stability})', ha='center', va='bottom',
                                   fontweight='bold', fontsize=9)

        # 4. Sensitivity interpretation and recommendations
        sensitivity_analysis = []
        if ted_data['by_algorithm']:
            dominant_alg = max(ted_data['by_algorithm'].items(), key=lambda x: x[1])
            weakest_alg = min(ted_data['by_algorithm'].items(), key=lambda x: x[1])

            sensitivity_analysis = [
                "STRUCTURAL SENSITIVITY ANALYSIS",
                "",
                f"Most Sensitive Algorithm:",
                f"  {ted_data['algorithm_names'].get(dominant_alg[0], dominant_alg[0])}",
                f"  {dominant_alg[1]:,} structural events detected",
                "",
                f"Least Sensitive Algorithm:",
                f"  {ted_data['algorithm_names'].get(weakest_alg[0], weakest_alg[0])}",
                f"  {weakest_alg[1]:,} structural events detected",
                "",
                f"Sensitivity Ratio: {dominant_alg[1]/weakest_alg[1]:.2f}:1" if weakest_alg[1] > 0 else "Sensitivity Ratio: ∞",
                "",
                "RECOMMENDATIONS:",
                "• High sensitivity = detects subtle changes",
                "• Low sensitivity = focuses on major changes",
                "• Use multiple algorithms for comprehensive",
                "  analysis of register differences",
                "• Complementary perspectives provide",
                "  more complete structural understanding"
            ]

        axes[1, 1].text(0.05, 0.95, '\n'.join(sensitivity_analysis),
                       transform=axes[1, 1].transAxes, fontsize=10,
                       verticalalignment='top', fontfamily='monospace')
        axes[1, 1].set_title("Sensitivity Analysis Summary", fontweight='bold')
        axes[1, 1].axis('off')

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()

    def create_ted_sentence_level_visualizations(self, analysis: Dict, summary: Dict):
        """Create sentence-level TED distribution visualizations."""
        print("Creating sentence-level TED distribution visualizations...")

        # This requires access to sentence-level scores, which would need to be passed
        # from the comparator. For now, create placeholder that can be populated later.

        # Check if sentence-level data is available in analysis
        if 'sentence_level_ted_scores' in analysis:
            sentence_scores = analysis['sentence_level_ted_scores']

            # 1. TED score distributions by algorithm
            self.plot_ted_score_distributions(sentence_scores,
                                            "TED Score Distributions by Algorithm",
                                            "ted_score_distributions.png")

            # 2. TED score distributions by newspaper
            self.plot_ted_score_distributions_by_newspaper(sentence_scores,
                                                          "TED Score Distributions by Newspaper",
                                                          "ted_score_distributions_by_newspaper.png")

            # 3. Sentence-pair analysis
            self.plot_ted_sentence_pair_analysis(sentence_scores,
                                                "Individual Sentence-Pair TED Analysis",
                                                "ted_sentence_pair_analysis.png")

            # 4. TED score correlation analysis
            self.plot_ted_score_correlations(sentence_scores,
                                           "TED Algorithm Score Correlations",
                                           "ted_score_correlations.png")

            # 5. Tree size vs TED score analysis
            self.plot_ted_tree_size_analysis(sentence_scores,
                                           "Tree Size vs TED Score Analysis",
                                           "ted_tree_size_analysis.png")

            print("Sentence-level TED visualizations completed!")
        else:
            print("No sentence-level TED data available for visualization")

    def plot_ted_score_distributions(self, sentence_scores: List[Dict], title: str, filename: str):
        """Plot TED score distributions by algorithm."""
        import pandas as pd

        if not sentence_scores:
            return

        # Convert to DataFrame
        df = pd.DataFrame(sentence_scores)

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(title, fontsize=16, fontweight='bold')

        algorithms = df['algorithm'].unique()
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'][:len(algorithms)]

        # 1. Histograms by algorithm
        for i, algorithm in enumerate(algorithms):
            row, col = i // 2, i % 2
            if row < 2 and col < 2:
                alg_data = df[df['algorithm'] == algorithm]['ted_score']

                axes[row, col].hist(alg_data, bins=20, color=colors[i], alpha=0.7,
                                  edgecolor='black', linewidth=1.0)
                axes[row, col].set_title(f"TED Score Distribution\n{algorithm.replace('_', '-').upper()}",
                                       fontweight='bold')
                axes[row, col].set_xlabel("TED Score", fontweight='bold')
                axes[row, col].set_ylabel("Frequency", fontweight='bold')
                axes[row, col].grid(alpha=0.3)

                # Add statistics
                mean_score = alg_data.mean()
                std_score = alg_data.std()
                axes[row, col].axvline(mean_score, color='red', linestyle='--', alpha=0.8,
                                     label=f'Mean: {mean_score:.2f}')
                axes[row, col].legend()

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()

    def plot_ted_score_distributions_by_newspaper(self, sentence_scores: List[Dict], title: str, filename: str):
        """Plot TED score distributions by newspaper."""
        import pandas as pd

        if not sentence_scores:
            return

        df = pd.DataFrame(sentence_scores)
        newspapers = df['newspaper'].unique()
        algorithms = df['algorithm'].unique()

        fig, axes = plt.subplots(len(newspapers), len(algorithms),
                               figsize=(5*len(algorithms), 4*len(newspapers)))
        fig.suptitle(title, fontsize=16, fontweight='bold')

        if len(newspapers) == 1:
            axes = axes.reshape(1, -1)

        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

        for i, newspaper in enumerate(newspapers):
            for j, algorithm in enumerate(algorithms):
                data = df[(df['newspaper'] == newspaper) & (df['algorithm'] == algorithm)]['ted_score']

                if len(data) > 0:
                    axes[i, j].hist(data, bins=15, color=colors[j], alpha=0.7,
                                  edgecolor='black', linewidth=0.8)
                    axes[i, j].set_title(f"{newspaper}\n{algorithm.replace('_', '-').upper()}",
                                       fontweight='bold', fontsize=10)
                    axes[i, j].set_xlabel("TED Score", fontsize=9)
                    axes[i, j].set_ylabel("Frequency", fontsize=9)
                    axes[i, j].grid(alpha=0.3)

                    # Add statistics
                    if len(data) > 1:
                        mean_score = data.mean()
                        axes[i, j].axvline(mean_score, color='red', linestyle='--', alpha=0.8)
                        axes[i, j].text(0.7, 0.8, f'μ={mean_score:.2f}',
                                       transform=axes[i, j].transAxes,
                                       bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()

    def plot_ted_sentence_pair_analysis(self, sentence_scores: List[Dict], title: str, filename: str):
        """Plot analysis of individual sentence pairs."""
        import pandas as pd

        if not sentence_scores:
            return

        df = pd.DataFrame(sentence_scores)

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(title, fontsize=16, fontweight='bold')

        # 1. Top scoring sentence pairs
        algorithms = df['algorithm'].unique()

        # Get top 10 sentence pairs for first algorithm
        first_alg = algorithms[0]
        top_pairs = df[df['algorithm'] == first_alg].nlargest(10, 'ted_score')

        if len(top_pairs) > 0:
            bars = axes[0, 0].barh(range(len(top_pairs)), top_pairs['ted_score'],
                                 color='skyblue', edgecolor='black', linewidth=0.8)
            axes[0, 0].set_title(f"Top 10 Sentence Pairs by TED Score\n({first_alg.replace('_', '-').upper()})",
                               fontweight='bold')
            axes[0, 0].set_xlabel("TED Score", fontweight='bold')
            axes[0, 0].set_yticks(range(len(top_pairs)))
            axes[0, 0].set_yticklabels([f"Sent {sid}" for sid in top_pairs['sent_id']], fontsize=9)

            # Add values
            for i, (bar, score) in enumerate(zip(bars, top_pairs['ted_score'])):
                axes[0, 0].text(bar.get_width() + max(top_pairs['ted_score'])*0.01, bar.get_y() + bar.get_height()/2,
                               f'{score:.1f}', va='center', fontweight='bold', fontsize=9)

        # 2. TED score vs sentence length
        sentence_lengths = df['canonical_text'].str.len() + df['headline_text'].str.len()

        for i, algorithm in enumerate(algorithms[:3]):  # Limit to 3 algorithms
            alg_data = df[df['algorithm'] == algorithm]
            alg_lengths = alg_data['canonical_text'].str.len() + alg_data['headline_text'].str.len()

            scatter_ax = axes[0, 1] if i == 0 else axes[1, 0] if i == 1 else axes[1, 1]
            scatter_ax.scatter(alg_lengths, alg_data['ted_score'], alpha=0.6, s=30,
                             color=['#1f77b4', '#ff7f0e', '#2ca02c'][i])
            scatter_ax.set_title(f"TED Score vs Text Length\n{algorithm.replace('_', '-').upper()}",
                                fontweight='bold')
            scatter_ax.set_xlabel("Combined Text Length (chars)", fontweight='bold')
            scatter_ax.set_ylabel("TED Score", fontweight='bold')
            scatter_ax.grid(alpha=0.3)

            # Add correlation coefficient
            if len(alg_lengths) > 1:
                correlation = alg_lengths.corr(alg_data['ted_score'])
                scatter_ax.text(0.05, 0.95, f'r = {correlation:.3f}',
                               transform=scatter_ax.transAxes,
                               bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()

    def plot_ted_score_correlations(self, sentence_scores: List[Dict], title: str, filename: str):
        """Plot correlations between different TED algorithms."""
        import pandas as pd

        if not sentence_scores:
            return

        df = pd.DataFrame(sentence_scores)

        # Pivot to get algorithms as columns
        pivot_df = df.pivot_table(index=['newspaper', 'sent_id'],
                                columns='algorithm',
                                values='ted_score',
                                fill_value=0)

        if pivot_df.empty:
            return

        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle(title, fontsize=16, fontweight='bold')

        # 1. Correlation matrix
        corr_matrix = pivot_df.corr()
        im = axes[0].imshow(corr_matrix, cmap='RdBu_r', vmin=-1, vmax=1)
        axes[0].set_title("TED Algorithm Correlation Matrix", fontweight='bold')

        algorithms = list(corr_matrix.columns)
        axes[0].set_xticks(range(len(algorithms)))
        axes[0].set_xticklabels([alg.replace('_', '-').upper() for alg in algorithms], rotation=45)
        axes[0].set_yticks(range(len(algorithms)))
        axes[0].set_yticklabels([alg.replace('_', '-').upper() for alg in algorithms])

        # Add correlation values
        for i in range(len(algorithms)):
            for j in range(len(algorithms)):
                value = corr_matrix.iloc[i, j]
                color = 'white' if abs(value) > 0.5 else 'black'
                axes[0].text(j, i, f'{value:.2f}', ha='center', va='center',
                           color=color, fontweight='bold')

        plt.colorbar(im, ax=axes[0], label='Correlation Coefficient')

        # 2. Scatter plot of two most different algorithms
        if len(algorithms) >= 2:
            # Find the pair with lowest correlation
            min_corr_pair = None
            min_corr_value = 1.0

            for i in range(len(algorithms)):
                for j in range(i+1, len(algorithms)):
                    corr_val = corr_matrix.iloc[i, j]
                    if corr_val < min_corr_value:
                        min_corr_value = corr_val
                        min_corr_pair = (algorithms[i], algorithms[j])

            if min_corr_pair:
                alg1, alg2 = min_corr_pair
                x_data = pivot_df[alg1]
                y_data = pivot_df[alg2]

                axes[1].scatter(x_data, y_data, alpha=0.6, s=30, color='purple')
                axes[1].set_title(f"Least Correlated Algorithms\n{alg1.replace('_', '-').upper()} vs {alg2.replace('_', '-').upper()}",
                                fontweight='bold')
                axes[1].set_xlabel(f"{alg1.replace('_', '-').upper()} TED Score", fontweight='bold')
                axes[1].set_ylabel(f"{alg2.replace('_', '-').upper()} TED Score", fontweight='bold')
                axes[1].grid(alpha=0.3)

                # Add correlation line
                z = np.polyfit(x_data, y_data, 1)
                p = np.poly1d(z)
                axes[1].plot(x_data, p(x_data), "r--", alpha=0.8)
                axes[1].text(0.05, 0.95, f'r = {min_corr_value:.3f}',
                           transform=axes[1].transAxes,
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()

    def plot_ted_tree_size_analysis(self, sentence_scores: List[Dict], title: str, filename: str):
        """Plot analysis of TED scores vs tree sizes."""
        import pandas as pd

        if not sentence_scores:
            return

        df = pd.DataFrame(sentence_scores)

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(title, fontsize=16, fontweight='bold')

        algorithms = df['algorithm'].unique()
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

        # 1. TED score vs max tree size
        for i, algorithm in enumerate(algorithms[:4]):
            row, col = i // 2, i % 2
            alg_data = df[df['algorithm'] == algorithm]
            max_tree_sizes = alg_data[['tree1_size', 'tree2_size']].max(axis=1)

            axes[row, col].scatter(max_tree_sizes, alg_data['ted_score'],
                                 alpha=0.6, s=30, color=colors[i])
            axes[row, col].set_title(f"TED Score vs Max Tree Size\n{algorithm.replace('_', '-').upper()}",
                                   fontweight='bold')
            axes[row, col].set_xlabel("Maximum Tree Size (nodes)", fontweight='bold')
            axes[row, col].set_ylabel("TED Score", fontweight='bold')
            axes[row, col].grid(alpha=0.3)

            # Add correlation and trend line
            if len(max_tree_sizes) > 1:
                correlation = max_tree_sizes.corr(alg_data['ted_score'])
                z = np.polyfit(max_tree_sizes, alg_data['ted_score'], 1)
                p = np.poly1d(z)
                axes[row, col].plot(max_tree_sizes, p(max_tree_sizes), "r--", alpha=0.8)
                axes[row, col].text(0.05, 0.95, f'r = {correlation:.3f}',
                                   transform=axes[row, col].transAxes,
                                   bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()

# # Usage:
#
# from pathlib import Path
# from visualizer import Visualizer
# # from register_comparison.outputs.output_creator import OutputCreator
# from register_comparison.meta_data.schema import FeatureSchema as schema
# # from register_comparison.aggregators.aggregator import Aggregator
#
# output_dir = Path("results")
# outputs = Outputs(output_dir, schema)
# visualizer = Visualizer(output_dir)
# from register_comparison.aggregators.aggregator import Aggregator as aggregator
#
# # Save feature frequency CSV
# feature_counts = aggregator.global_counts()
# outputs.save_feature_matrix_csv(feature_counts, "feature_freq_global.csv")
#
# # Save detailed event table CSV
# outputs.save_events_csv(aggregator.global_events, "events_global.csv")
#
# # # Save summary statistics CSV (suppose from stats.py)
# # outputs.save_summary_stats_csv(summary_stats_df, "summary_stats_global.csv")
#
# # Generate LaTeX and Markdown summaries
# outputs.generate_latex_summary("summary_features.tex")
# outputs.generate_markdown_summary("summary_features.md")
#
# # Save interpretive notes (prepare as string beforehand)
# # outputs.save_interpretive_notes(notes_text, "interpretive_notes.txt")
#
# # Create visualization plots
# visualizer.plot_feature_frequencies(feature_counts, "Global Feature Frequencies", "feature_freq_global.png")
#
# # Similarly for newspapers or parse-types, pass their counts to plotting functions

    def create_feature_value_pair_visualizations(self, pair_analysis: Dict[str, Any]):
        """Create comprehensive visualizations for feature-value pairs as atomic units."""
        print("Creating feature-value pair unit visualizations...")

        # 1. Feature-value pair frequency distribution
        self.plot_feature_value_pair_distribution(
            pair_analysis["global_feature_value_pairs"],
            "Feature-Value Pair Frequency Distribution",
            "feature_value_pair_distribution.png"
        )

        # 2. Top transformation pairs
        self.plot_top_transformation_pairs(
            pair_analysis["pair_statistics"],
            "Top Feature-Value Transformation Pairs",
            "top_transformation_pairs.png"
        )

        print("✅ Feature-value pair visualizations created")

    def plot_feature_value_pair_distribution(self, global_pairs: Dict[str, int], title: str, filename: str):
        """Plot distribution of feature-value pairs."""
        if not global_pairs:
            return

        # Get top 20 pairs for visualization
        sorted_pairs = sorted(global_pairs.items(), key=lambda x: x[1], reverse=True)[:20]

        if not sorted_pairs:
            return

        pair_names = [pair[0] for pair in sorted_pairs]
        counts = [pair[1] for pair in sorted_pairs]

        # Create shortened labels for readability
        short_labels = []
        for pair_name in pair_names:
            if ":" in pair_name and "→" in pair_name:
                feature, transformation = pair_name.split(":", 1)
                # Get feature mnemonic if available
                feature_label = self.feature_labels.get(feature, feature)
                short_labels.append(f"{feature_label}: {transformation}")
            else:
                short_labels.append(pair_name[:30] + "..." if len(pair_name) > 30 else pair_name)

        fig, ax = plt.subplots(figsize=(16, 10))

        bars = ax.barh(range(len(short_labels)), counts, color="steelblue", alpha=0.8)

        ax.set_yticks(range(len(short_labels)))
        ax.set_yticklabels(short_labels, fontsize=10)
        ax.set_xlabel("Frequency", fontweight="bold", fontsize=12)
        ax.set_title(title, fontweight="bold", fontsize=14, pad=20)

        # Add value labels on bars
        for i, (bar, count) in enumerate(zip(bars, counts)):
            width = bar.get_width()
            ax.text(width + max(counts) * 0.01, bar.get_y() + bar.get_height()/2,
                   str(count), ha="left", va="center", fontweight="bold")

        # Add statistics text
        total_pairs = len(global_pairs)
        total_occurrences = sum(global_pairs.values())
        ax.text(0.02, 0.98, f"Total unique pairs: {total_pairs:,}\nTotal occurrences: {total_occurrences:,}",
                transform=ax.transAxes, fontsize=11, verticalalignment="top",
                bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))

        plt.grid(axis="x", alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches="tight")
        plt.close()

    def plot_top_transformation_pairs(self, pair_stats: Dict[str, Any], title: str, filename: str):
        """Plot top transformation pairs with statistics."""
        if "most_frequent_pairs" not in pair_stats or not pair_stats["most_frequent_pairs"]:
            return

        top_pairs = pair_stats["most_frequent_pairs"][:15]

        pair_names = [pair[0] for pair in top_pairs]
        counts = [pair[1] for pair in top_pairs]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

        # Left plot: Bar chart of top pairs
        bars = ax1.bar(range(len(pair_names)), counts, color="darkgreen", alpha=0.7)

        # Create readable labels
        short_labels = []
        for pair_name in pair_names:
            if ":" in pair_name and "→" in pair_name:
                feature, transformation = pair_name.split(":", 1)
                feature_label = self.feature_labels.get(feature, feature)
                short_labels.append(f"{feature_label}:\n{transformation}")
            else:
                short_labels.append(pair_name)

        ax1.set_xticks(range(len(short_labels)))
        ax1.set_xticklabels(short_labels, rotation=45, ha="right", fontsize=9)
        ax1.set_ylabel("Frequency", fontweight="bold")
        ax1.set_title("Top Feature-Value Transformation Pairs", fontweight="bold")
        ax1.grid(axis="y", alpha=0.3)

        # Add value labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + max(counts) * 0.01,
                    str(count), ha="center", va="bottom", fontweight="bold")

        # Right plot: Statistics overview
        ax2.axis("off")
        if "pair_concentration_metrics" in pair_stats:
            concentration = pair_stats["pair_concentration_metrics"]
            stats_text = f"""
Pair Statistics Summary:

Total Unique Pairs: {pair_stats.get("total_unique_pairs", 0):,}
Average Frequency: {pair_stats.get("average_pair_frequency", 0):.2f}

Concentration Metrics:
• Total Occurrences: {concentration.get("total_pair_occurrences", 0):,}
• Entropy: {concentration.get("entropy", 0):.3f}
• Top-5 Concentration: {concentration.get("concentration_ratio", 0):.1%}

Most Active Transformation:
{top_pairs[0][0] if top_pairs else "N/A"}
(Frequency: {top_pairs[0][1] if top_pairs else 0})
            """
            ax2.text(0.05, 0.95, stats_text, transform=ax2.transAxes,
                    fontsize=12, verticalalignment="top",
                    bbox=dict(boxstyle="round", facecolor="lightcyan", alpha=0.8))

        plt.suptitle(title, fontsize=16, fontweight="bold")
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches="tight")
        plt.close()


    def create_bidirectional_cross_entropy_visualizations(self, cross_entropy_analysis: Dict[str, Any]):
        """Create comprehensive visualizations for bidirectional cross-entropy analysis."""
        print("Creating bidirectional cross-entropy visualizations...")

        # 1. Global cross-entropy metrics overview
        self.plot_global_cross_entropy_metrics(
            cross_entropy_analysis.get("global_cross_entropy", {}),
            "Global Cross-Entropy Metrics",
            "global_cross_entropy_metrics.png"
        )

        # 2. Newspaper comparison
        self.plot_newspaper_cross_entropy_comparison(
            cross_entropy_analysis.get("by_newspaper_cross_entropy", {}),
            "Cross-Entropy Comparison by Newspaper",
            "newspaper_cross_entropy_comparison.png"
        )

        # 3. Bidirectional analysis
        self.plot_bidirectional_analysis(
            cross_entropy_analysis.get("by_newspaper_cross_entropy", {}),
            "Bidirectional Cross-Entropy Analysis",
            "bidirectional_cross_entropy_analysis.png"
        )

        # 4. Feature-level cross-entropy ranking
        self.plot_feature_cross_entropy_ranking(
            cross_entropy_analysis.get("feature_level_cross_entropy", {}),
            "Feature-Level Cross-Entropy Ranking",
            "feature_cross_entropy_ranking.png"
        )

        # 5. Information asymmetry analysis
        self.plot_information_asymmetry_analysis(
            cross_entropy_analysis,
            "Information Asymmetry Analysis",
            "information_asymmetry_analysis.png"
        )

        # 6. Cross-dimensional heatmap
        self.plot_cross_dimensional_entropy_heatmap(
            cross_entropy_analysis.get("cross_dimensional_cross_entropy", {}),
            "Cross-Dimensional Entropy Heatmap",
            "cross_dimensional_entropy_heatmap.png"
        )

        print("✅ Bidirectional cross-entropy visualizations created")

    def plot_global_cross_entropy_metrics(self, global_ce: Dict[str, Any], title: str, filename: str):
        """Plot global cross-entropy metrics overview."""
        if not global_ce:
            return

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        # 1. Bidirectional cross-entropy comparison
        metrics = ["Canonical → Headlines", "Headlines → Canonical", "Bidirectional Sum"]
        values = [
            global_ce.get("canonical_to_headline_cross_entropy", 0),
            global_ce.get("headline_to_canonical_cross_entropy", 0),
            global_ce.get("bidirectional_cross_entropy_sum", 0)
        ]
        colors = ["steelblue", "lightcoral", "darkgreen"]

        bars = ax1.bar(metrics, values, color=colors, alpha=0.8)
        ax1.set_title("Cross-Entropy in Both Directions", fontweight="bold")
        ax1.set_ylabel("Cross-Entropy (bits)", fontweight="bold")
        ax1.tick_params(axis="x", rotation=45)

        # Add value labels
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f"{value:.3f}", ha="center", va="bottom", fontweight="bold")

        # 2. Information-theoretic measures
        measures = ["Jensen-Shannon\\nDivergence", "Register\\nOverlap Ratio", "Information\\nAsymmetry"]
        measure_values = [
            global_ce.get("jensen_shannon_divergence", 0),
            global_ce.get("register_overlap_ratio", 0),
            abs(global_ce.get("canonical_to_headline_cross_entropy", 0) - 
                global_ce.get("headline_to_canonical_cross_entropy", 0))
        ]
        colors2 = ["purple", "orange", "red"]

        bars2 = ax2.bar(measures, measure_values, color=colors2, alpha=0.8)
        ax2.set_title("Information-Theoretic Measures", fontweight="bold")
        ax2.set_ylabel("Value", fontweight="bold")

        for bar, value in zip(bars2, measure_values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f"{value:.3f}", ha="center", va="bottom", fontweight="bold")

        # 3. Register statistics
        ax3.axis("off")
        stats_text = f"""
Global Cross-Entropy Statistics:

Canonical → Headlines: {global_ce.get("canonical_to_headline_cross_entropy", 0):.4f} bits
Headlines → Canonical: {global_ce.get("headline_to_canonical_cross_entropy", 0):.4f} bits
Bidirectional Sum: {global_ce.get("bidirectional_cross_entropy_sum", 0):.4f} bits

Individual Register Entropies:
• Canonical Entropy: {global_ce.get("canonical_entropy", 0):.4f} bits
• Headlines Entropy: {global_ce.get("headline_entropy", 0):.4f} bits

Divergence Measures:
• KL(Canonical || Headlines): {global_ce.get("kl_canonical_to_headline", 0):.4f}
• KL(Headlines || Canonical): {global_ce.get("kl_headline_to_canonical", 0):.4f}
• KL Divergence Sum: {global_ce.get("kl_divergence_sum", 0):.4f}

Value Distribution:
• Unique Canonical Values: {global_ce.get("unique_canonical_values", 0):,}
• Unique Headlines Values: {global_ce.get("unique_headline_values", 0):,}
• Total Unique Values: {global_ce.get("unique_combined_values", 0):,}
• Register Overlap: {global_ce.get("register_overlap_ratio", 0):.1%}
        """
        ax3.text(0.05, 0.95, stats_text, transform=ax3.transAxes,
                fontsize=11, verticalalignment="top",
                bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.8))

        # 4. KL divergences comparison
        kl_metrics = ["KL(Can → Head)", "KL(Head → Can)", "KL Sum"]
        kl_values = [
            global_ce.get("kl_canonical_to_headline", 0),
            global_ce.get("kl_headline_to_canonical", 0),
            global_ce.get("kl_divergence_sum", 0)
        ]
        
        bars4 = ax4.bar(kl_metrics, kl_values, color=["darkblue", "darkred", "purple"], alpha=0.8)
        ax4.set_title("Kullback-Leibler Divergences", fontweight="bold")
        ax4.set_ylabel("KL Divergence", fontweight="bold")
        ax4.tick_params(axis="x", rotation=45)

        for bar, value in zip(bars4, kl_values):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f"{value:.3f}", ha="center", va="bottom", fontweight="bold")

        plt.suptitle(title, fontsize=16, fontweight="bold")
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches="tight")
        plt.close()

    def plot_newspaper_cross_entropy_comparison(self, newspaper_ce: Dict[str, Dict[str, Any]], title: str, filename: str):
        """Plot cross-entropy comparison across newspapers."""
        if not newspaper_ce:
            return

        newspapers = list(newspaper_ce.keys())
        if not newspapers:
            return

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 12))

        # 1. Bidirectional cross-entropy sum comparison
        bidirectional_sums = [newspaper_ce[np].get("bidirectional_cross_entropy_sum", 0) for np in newspapers]
        bars1 = ax1.bar(newspapers, bidirectional_sums, color="steelblue", alpha=0.8)
        ax1.set_title("Bidirectional Cross-Entropy Sum by Newspaper", fontweight="bold")
        ax1.set_ylabel("Cross-Entropy Sum (bits)", fontweight="bold")
        ax1.tick_params(axis="x", rotation=45)

        for bar, value in zip(bars1, bidirectional_sums):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f"{value:.3f}", ha="center", va="bottom", fontweight="bold")

        # 2. Directional comparison
        canonical_to_headline = [newspaper_ce[np].get("canonical_to_headline_cross_entropy", 0) for np in newspapers]
        headline_to_canonical = [newspaper_ce[np].get("headline_to_canonical_cross_entropy", 0) for np in newspapers]

        x = range(len(newspapers))
        width = 0.35

        bars2a = ax2.bar([i - width/2 for i in x], canonical_to_headline, width, 
                        label="Canonical → Headlines", color="lightcoral", alpha=0.8)
        bars2b = ax2.bar([i + width/2 for i in x], headline_to_canonical, width,
                        label="Headlines → Canonical", color="lightblue", alpha=0.8)

        ax2.set_title("Directional Cross-Entropy Comparison", fontweight="bold")
        ax2.set_ylabel("Cross-Entropy (bits)", fontweight="bold")
        ax2.set_xticks(x)
        ax2.set_xticklabels(newspapers, rotation=45)
        ax2.legend()

        # Add value labels
        for bars in [bars2a, bars2b]:
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f"{height:.2f}", ha="center", va="bottom", fontsize=9)

        # 3. Jensen-Shannon divergence
        js_divergences = [newspaper_ce[np].get("jensen_shannon_divergence", 0) for np in newspapers]
        bars3 = ax3.bar(newspapers, js_divergences, color="darkgreen", alpha=0.8)
        ax3.set_title("Jensen-Shannon Divergence by Newspaper", fontweight="bold")
        ax3.set_ylabel("JS Divergence", fontweight="bold")
        ax3.tick_params(axis="x", rotation=45)

        for bar, value in zip(bars3, js_divergences):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f"{value:.3f}", ha="center", va="bottom", fontweight="bold")

        # 4. Register overlap ratio
        overlap_ratios = [newspaper_ce[np].get("register_overlap_ratio", 0) for np in newspapers]
        bars4 = ax4.bar(newspapers, overlap_ratios, color="orange", alpha=0.8)
        ax4.set_title("Register Overlap Ratio by Newspaper", fontweight="bold")
        ax4.set_ylabel("Overlap Ratio", fontweight="bold")
        ax4.tick_params(axis="x", rotation=45)

        for bar, value in zip(bars4, overlap_ratios):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f"{value:.3f}", ha="center", va="bottom", fontweight="bold")

        plt.suptitle(title, fontsize=16, fontweight="bold")
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches="tight")
        plt.close()

    def plot_bidirectional_analysis(self, newspaper_ce: Dict[str, Dict[str, Any]], title: str, filename: str):
        """Plot detailed bidirectional analysis."""
        if not newspaper_ce:
            return

        newspapers = list(newspaper_ce.keys())
        if not newspapers:
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

        # 1. Bidirectional flow visualization
        canonical_to_headline = [newspaper_ce[np].get("canonical_to_headline_cross_entropy", 0) for np in newspapers]
        headline_to_canonical = [newspaper_ce[np].get("headline_to_canonical_cross_entropy", 0) for np in newspapers]

        # Create arrow plot showing information flow
        for i, newspaper in enumerate(newspapers):
            c_to_h = canonical_to_headline[i]
            h_to_c = headline_to_canonical[i]
            
            # Plot bidirectional arrows
            ax1.arrow(i-0.3, 0, 0, c_to_h, head_width=0.1, head_length=c_to_h*0.05, 
                     fc="lightcoral", ec="lightcoral", alpha=0.7, label="Can→Head" if i == 0 else "")
            ax1.arrow(i+0.3, h_to_c, 0, -h_to_c, head_width=0.1, head_length=h_to_c*0.05,
                     fc="lightblue", ec="lightblue", alpha=0.7, label="Head→Can" if i == 0 else "")
            
            # Add values
            ax1.text(i-0.3, c_to_h/2, f"{c_to_h:.2f}", ha="center", va="center", 
                    fontweight="bold", fontsize=10)
            ax1.text(i+0.3, h_to_c/2, f"{h_to_c:.2f}", ha="center", va="center",
                    fontweight="bold", fontsize=10)

        ax1.set_xlim(-0.5, len(newspapers)-0.5)
        ax1.set_ylim(0, max(max(canonical_to_headline), max(headline_to_canonical)) * 1.1)
        ax1.set_xticks(range(len(newspapers)))
        ax1.set_xticklabels(newspapers, rotation=45)
        ax1.set_ylabel("Cross-Entropy (bits)", fontweight="bold")
        ax1.set_title("Bidirectional Information Flow", fontweight="bold")
        ax1.legend()
        ax1.grid(alpha=0.3)

        # 2. Asymmetry analysis
        asymmetries = [abs(c_to_h - h_to_c) for c_to_h, h_to_c in zip(canonical_to_headline, headline_to_canonical)]
        bars = ax2.bar(newspapers, asymmetries, color="purple", alpha=0.8)
        
        ax2.set_title("Information Asymmetry by Newspaper", fontweight="bold")
        ax2.set_ylabel("Asymmetry (|CE(Can→Head) - CE(Head→Can)|)", fontweight="bold")
        ax2.tick_params(axis="x", rotation=45)

        for bar, value in zip(bars, asymmetries):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f"{value:.3f}", ha="center", va="bottom", fontweight="bold")

        # Add asymmetry interpretation
        max_asymmetry = max(asymmetries) if asymmetries else 0
        if max_asymmetry > 0:
            most_asymmetric = newspapers[asymmetries.index(max_asymmetry)]
            ax2.text(0.02, 0.98, f"Most Asymmetric: {most_asymmetric}\nAsymmetry: {max_asymmetry:.3f}",
                    transform=ax2.transAxes, fontsize=10, verticalalignment="top",
                    bbox=dict(boxstyle="round", facecolor="yellow", alpha=0.8))

        plt.suptitle(title, fontsize=16, fontweight="bold")
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches="tight")
        plt.close()


    def plot_feature_cross_entropy_ranking(self, feature_ce: Dict[str, Dict[str, Any]], title: str, filename: str):
        """Plot feature-level cross-entropy ranking."""
        if not feature_ce:
            return

        # Sort features by bidirectional cross-entropy sum
        sorted_features = sorted(feature_ce.items(), 
                               key=lambda x: x[1].get("bidirectional_cross_entropy_sum", 0), 
                               reverse=True)[:15]  # Top 15 features

        if not sorted_features:
            return

        feature_ids = [item[0] for item in sorted_features]
        feature_data = [item[1] for item in sorted_features]

        # Use feature mnemonics if available
        feature_labels = [self.feature_labels.get(fid, fid) for fid in feature_ids]

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 12))

        # 1. Bidirectional sum ranking
        bidirectional_sums = [data.get("bidirectional_cross_entropy_sum", 0) for data in feature_data]
        bars1 = ax1.barh(range(len(feature_labels)), bidirectional_sums, color="steelblue", alpha=0.8)
        ax1.set_yticks(range(len(feature_labels)))
        ax1.set_yticklabels(feature_labels, fontsize=10)
        ax1.set_xlabel("Bidirectional Cross-Entropy Sum (bits)", fontweight="bold")
        ax1.set_title("Top Features by Cross-Entropy", fontweight="bold")

        for i, (bar, value) in enumerate(zip(bars1, bidirectional_sums)):
            width = bar.get_width()
            ax1.text(width + max(bidirectional_sums) * 0.01, bar.get_y() + bar.get_height()/2,
                    f"{value:.3f}", ha="left", va="center", fontweight="bold")

        # 2. Directional comparison for top features
        top_5_features = sorted_features[:5]
        top_5_labels = [self.feature_labels.get(item[0], item[0]) for item in top_5_features]
        canonical_to_headline = [item[1].get("canonical_to_headline_cross_entropy", 0) for item in top_5_features]
        headline_to_canonical = [item[1].get("headline_to_canonical_cross_entropy", 0) for item in top_5_features]

        x = range(len(top_5_labels))
        width = 0.35

        bars2a = ax2.bar([i - width/2 for i in x], canonical_to_headline, width,
                        label="Canonical → Headlines", color="lightcoral", alpha=0.8)
        bars2b = ax2.bar([i + width/2 for i in x], headline_to_canonical, width,
                        label="Headlines → Canonical", color="lightblue", alpha=0.8)

        ax2.set_title("Top 5 Features: Directional Cross-Entropy", fontweight="bold")
        ax2.set_ylabel("Cross-Entropy (bits)", fontweight="bold")
        ax2.set_xticks(x)
        ax2.set_xticklabels(top_5_labels, rotation=45, ha="right")
        ax2.legend()

        # 3. Jensen-Shannon divergence
        js_divergences = [data.get("jensen_shannon_divergence", 0) for data in feature_data]
        bars3 = ax3.barh(range(len(feature_labels)), js_divergences, color="darkgreen", alpha=0.8)
        ax3.set_yticks(range(len(feature_labels)))
        ax3.set_yticklabels(feature_labels, fontsize=10)
        ax3.set_xlabel("Jensen-Shannon Divergence", fontweight="bold")
        ax3.set_title("Features by JS Divergence", fontweight="bold")

        # 4. Register overlap vs total events scatter
        overlap_ratios = [data.get("register_overlap_ratio", 0) for data in feature_data]
        total_events = [data.get("total_events", 0) for data in feature_data]

        scatter = ax4.scatter(overlap_ratios, total_events, 
                            c=bidirectional_sums, cmap="viridis", alpha=0.7, s=100)
        ax4.set_xlabel("Register Overlap Ratio", fontweight="bold")
        ax4.set_ylabel("Total Events", fontweight="bold")
        ax4.set_title("Overlap vs Events (colored by CE)", fontweight="bold")

        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax4)
        cbar.set_label("Bidirectional CE Sum", fontweight="bold")

        # Add feature labels to scatter points
        for i, label in enumerate(feature_labels):
            if i < 8:  # Only label top 8 to avoid crowding
                ax4.annotate(label, (overlap_ratios[i], total_events[i]),
                           xytext=(5, 5), textcoords="offset points", fontsize=8)

        plt.suptitle(title, fontsize=16, fontweight="bold")
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches="tight")
        plt.close()

    def plot_information_asymmetry_analysis(self, cross_entropy_analysis: Dict[str, Any], title: str, filename: str):
        """Plot comprehensive information asymmetry analysis."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        # 1. Newspaper asymmetry comparison
        newspaper_ce = cross_entropy_analysis.get("by_newspaper_cross_entropy", {})
        if newspaper_ce:
            newspapers = list(newspaper_ce.keys())
            asymmetries = []
            for newspaper in newspapers:
                ce_data = newspaper_ce[newspaper]
                c_to_h = ce_data.get("canonical_to_headline_cross_entropy", 0)
                h_to_c = ce_data.get("headline_to_canonical_cross_entropy", 0)
                asymmetry = abs(c_to_h - h_to_c)
                asymmetries.append(asymmetry)

            bars1 = ax1.bar(newspapers, asymmetries, color="purple", alpha=0.8)
            ax1.set_title("Information Asymmetry by Newspaper", fontweight="bold")
            ax1.set_ylabel("Asymmetry (bits)", fontweight="bold")
            ax1.tick_params(axis="x", rotation=45)

            for bar, value in zip(bars1, asymmetries):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f"{value:.3f}", ha="center", va="bottom", fontweight="bold")

        # 2. Feature asymmetry ranking
        feature_ce = cross_entropy_analysis.get("feature_level_cross_entropy", {})
        if feature_ce:
            feature_asymmetries = []
            for feature_id, ce_data in feature_ce.items():
                c_to_h = ce_data.get("canonical_to_headline_cross_entropy", 0)
                h_to_c = ce_data.get("headline_to_canonical_cross_entropy", 0)
                asymmetry = abs(c_to_h - h_to_c)
                feature_asymmetries.append((feature_id, asymmetry))

            # Sort and take top 10
            feature_asymmetries.sort(key=lambda x: x[1], reverse=True)
            top_features = feature_asymmetries[:10]

            if top_features:
                feature_ids = [item[0] for item in top_features]
                asymmetry_values = [item[1] for item in top_features]
                feature_labels = [self.feature_labels.get(fid, fid) for fid in feature_ids]

                bars2 = ax2.barh(range(len(feature_labels)), asymmetry_values, color="red", alpha=0.8)
                ax2.set_yticks(range(len(feature_labels)))
                ax2.set_yticklabels(feature_labels, fontsize=10)
                ax2.set_xlabel("Information Asymmetry (bits)", fontweight="bold")
                ax2.set_title("Top Features by Asymmetry", fontweight="bold")

                for i, (bar, value) in enumerate(zip(bars2, asymmetry_values)):
                    width = bar.get_width()
                    ax2.text(width + max(asymmetry_values) * 0.01, bar.get_y() + bar.get_height()/2,
                            f"{value:.3f}", ha="left", va="center", fontweight="bold")

        # 3. Asymmetry vs total cross-entropy scatter
        if newspaper_ce:
            total_ces = []
            asymmetries_scatter = []
            newspaper_labels = []

            for newspaper, ce_data in newspaper_ce.items():
                total_ce = ce_data.get("bidirectional_cross_entropy_sum", 0)
                c_to_h = ce_data.get("canonical_to_headline_cross_entropy", 0)
                h_to_c = ce_data.get("headline_to_canonical_cross_entropy", 0)
                asymmetry = abs(c_to_h - h_to_c)
                
                total_ces.append(total_ce)
                asymmetries_scatter.append(asymmetry)
                newspaper_labels.append(newspaper)

            scatter = ax3.scatter(total_ces, asymmetries_scatter, s=150, alpha=0.7, 
                                c=["steelblue", "lightcoral", "mediumseagreen"][:len(newspaper_labels)])
            ax3.set_xlabel("Total Cross-Entropy (bits)", fontweight="bold")
            ax3.set_ylabel("Information Asymmetry (bits)", fontweight="bold")
            ax3.set_title("Total CE vs Asymmetry", fontweight="bold")

            # Add newspaper labels
            for i, label in enumerate(newspaper_labels):
                ax3.annotate(label, (total_ces[i], asymmetries_scatter[i]),
                           xytext=(5, 5), textcoords="offset points", fontweight="bold")

        # 4. Summary statistics
        ax4.axis("off")
        
        # Calculate overall statistics
        global_ce = cross_entropy_analysis.get("global_cross_entropy", {})
        stats_text = f"""
Information Asymmetry Analysis Summary:

Global Measures:
• Global Asymmetry: {abs(global_ce.get("canonical_to_headline_cross_entropy", 0) - global_ce.get("headline_to_canonical_cross_entropy", 0)):.4f} bits
• Jensen-Shannon Divergence: {global_ce.get("jensen_shannon_divergence", 0):.4f}
• Register Overlap Ratio: {global_ce.get("register_overlap_ratio", 0):.1%}

Interpretation:
• Higher asymmetry indicates unequal information flow
• Asymmetry near 0 suggests balanced registers  
• JS divergence provides symmetric distance measure
• Overlap ratio shows register similarity

Cross-Entropy Components:
• Canonical → Headlines: {global_ce.get("canonical_to_headline_cross_entropy", 0):.4f} bits
• Headlines → Canonical: {global_ce.get("headline_to_canonical_cross_entropy", 0):.4f} bits
• Bidirectional Sum: {global_ce.get("bidirectional_cross_entropy_sum", 0):.4f} bits
        """

        if newspaper_ce:
            # Find most/least asymmetric newspapers
            newspaper_asymmetries = {}
            for newspaper, ce_data in newspaper_ce.items():
                c_to_h = ce_data.get("canonical_to_headline_cross_entropy", 0)
                h_to_c = ce_data.get("headline_to_canonical_cross_entropy", 0)
                newspaper_asymmetries[newspaper] = abs(c_to_h - h_to_c)
            
            most_asymmetric = max(newspaper_asymmetries.items(), key=lambda x: x[1])
            least_asymmetric = min(newspaper_asymmetries.items(), key=lambda x: x[1])

            stats_text += f"""

Newspaper Ranking:
• Most Asymmetric: {most_asymmetric[0]} ({most_asymmetric[1]:.3f} bits)
• Least Asymmetric: {least_asymmetric[0]} ({least_asymmetric[1]:.3f} bits)
            """

        ax4.text(0.05, 0.95, stats_text, transform=ax4.transAxes,
                fontsize=11, verticalalignment="top",
                bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))

        plt.suptitle(title, fontsize=16, fontweight="bold")
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches="tight")
        plt.close()

    def plot_cross_dimensional_entropy_heatmap(self, cross_dim_ce: Dict[str, Dict[str, Any]], title: str, filename: str):
        """Plot cross-dimensional entropy heatmap."""
        if not cross_dim_ce:
            return

        # Extract newspapers and parse types
        dimensions = list(cross_dim_ce.keys())
        newspapers = set()
        parse_types = set()

        for dim in dimensions:
            if "_" in dim:
                newspaper, parse_type = dim.split("_", 1)
                newspapers.add(newspaper)
                parse_types.add(parse_type)

        newspapers = sorted(list(newspapers))
        parse_types = sorted(list(parse_types))

        if not newspapers or not parse_types:
            return

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        # 1. Bidirectional cross-entropy heatmap
        ce_matrix = []
        for newspaper in newspapers:
            row = []
            for parse_type in parse_types:
                dim_key = f"{newspaper}_{parse_type}"
                ce_value = cross_dim_ce.get(dim_key, {}).get("bidirectional_cross_entropy_sum", 0)
                row.append(ce_value)
            ce_matrix.append(row)

        import numpy as np
        ce_array = np.array(ce_matrix)
        
        im1 = ax1.imshow(ce_array, cmap="YlOrRd", aspect="auto")
        ax1.set_xticks(range(len(parse_types)))
        ax1.set_xticklabels(parse_types, rotation=45)
        ax1.set_yticks(range(len(newspapers)))
        ax1.set_yticklabels(newspapers)
        ax1.set_title("Bidirectional Cross-Entropy", fontweight="bold")

        # Add text annotations
        for i in range(len(newspapers)):
            for j in range(len(parse_types)):
                value = ce_array[i, j]
                ax1.text(j, i, f"{value:.2f}", ha="center", va="center",
                        color="white" if value > np.max(ce_array) * 0.6 else "black",
                        fontweight="bold")

        plt.colorbar(im1, ax=ax1, label="Cross-Entropy (bits)")

        # 2. Jensen-Shannon divergence heatmap
        js_matrix = []
        for newspaper in newspapers:
            row = []
            for parse_type in parse_types:
                dim_key = f"{newspaper}_{parse_type}"
                js_value = cross_dim_ce.get(dim_key, {}).get("jensen_shannon_divergence", 0)
                row.append(js_value)
            js_matrix.append(row)

        js_array = np.array(js_matrix)
        im2 = ax2.imshow(js_array, cmap="viridis", aspect="auto")
        ax2.set_xticks(range(len(parse_types)))
        ax2.set_xticklabels(parse_types, rotation=45)
        ax2.set_yticks(range(len(newspapers)))
        ax2.set_yticklabels(newspapers)
        ax2.set_title("Jensen-Shannon Divergence", fontweight="bold")

        for i in range(len(newspapers)):
            for j in range(len(parse_types)):
                value = js_array[i, j]
                ax2.text(j, i, f"{value:.3f}", ha="center", va="center",
                        color="white" if value > np.max(js_array) * 0.6 else "black",
                        fontweight="bold")

        plt.colorbar(im2, ax=ax2, label="JS Divergence")

        # 3. Register overlap heatmap
        overlap_matrix = []
        for newspaper in newspapers:
            row = []
            for parse_type in parse_types:
                dim_key = f"{newspaper}_{parse_type}"
                overlap_value = cross_dim_ce.get(dim_key, {}).get("register_overlap_ratio", 0)
                row.append(overlap_value)
            overlap_matrix.append(row)

        overlap_array = np.array(overlap_matrix)
        im3 = ax3.imshow(overlap_array, cmap="RdYlBu", aspect="auto")
        ax3.set_xticks(range(len(parse_types)))
        ax3.set_xticklabels(parse_types, rotation=45)
        ax3.set_yticks(range(len(newspapers)))
        ax3.set_yticklabels(newspapers)
        ax3.set_title("Register Overlap Ratio", fontweight="bold")

        for i in range(len(newspapers)):
            for j in range(len(parse_types)):
                value = overlap_array[i, j]
                ax3.text(j, i, f"{value:.2f}", ha="center", va="center",
                        color="white" if value < np.mean(overlap_array) else "black",
                        fontweight="bold")

        plt.colorbar(im3, ax=ax3, label="Overlap Ratio")

        # 4. Summary statistics by dimension
        ax4.axis("off")
        
        # Find most/least divergent dimensions
        dimension_ces = [(dim, data.get("bidirectional_cross_entropy_sum", 0)) 
                        for dim, data in cross_dim_ce.items()]
        dimension_ces.sort(key=lambda x: x[1], reverse=True)

        summary_text = f"""
Cross-Dimensional Analysis Summary:

Most Divergent Combinations:
"""
        for i, (dim, ce_value) in enumerate(dimension_ces[:3]):
            newspaper, parse_type = dim.split("_", 1)
            summary_text += f"• {newspaper} ({parse_type}): {ce_value:.3f} bits\n"

        summary_text += f"""

Least Divergent Combinations:
"""
        for i, (dim, ce_value) in enumerate(dimension_ces[-3:]):
            newspaper, parse_type = dim.split("_", 1)
            summary_text += f"• {newspaper} ({parse_type}): {ce_value:.3f} bits\n"

        # Calculate averages
        avg_ce = np.mean([data.get("bidirectional_cross_entropy_sum", 0) for data in cross_dim_ce.values()])
        avg_js = np.mean([data.get("jensen_shannon_divergence", 0) for data in cross_dim_ce.values()])
        avg_overlap = np.mean([data.get("register_overlap_ratio", 0) for data in cross_dim_ce.values()])

        summary_text += f"""

Average Measures:
• Average Cross-Entropy: {avg_ce:.3f} bits
• Average JS Divergence: {avg_js:.3f}
• Average Overlap Ratio: {avg_overlap:.3f}
        """

        ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes,
                fontsize=10, verticalalignment="top",
                bbox=dict(boxstyle="round", facecolor="lightcyan", alpha=0.8))

        plt.suptitle(title, fontsize=16, fontweight="bold")
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches="tight")
        plt.close()

