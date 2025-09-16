
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
from typing import Dict, Any
from pathlib import Path
from register_comparison.outputs.output_creators import Outputs as output_creator, Outputs


class Visualizer:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_feature_frequencies(self, feature_counts: Dict[str, int], title: str, filename: str):
        """
        Generate a bar chart of feature frequencies.
        """
        keys = list(feature_counts.keys())
        values = [feature_counts[k] for k in keys]

        plt.figure(figsize=(10,6))
        sns.barplot(x=keys, y=values, color='skyblue')
        plt.title(title)
        plt.xlabel("Feature ID")
        plt.ylabel("Frequency")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(self.output_dir / filename)
        plt.close()
        print(f"Saved feature frequency plot to {filename}")

    def plot_histogram(self, data, bins: int, title: str, xlabel: str, filename: str):
        """
        Generic histogram plot.
        """
        plt.figure(figsize=(8,5))
        plt.hist(data, bins=bins, color="green", edgecolor="black")
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig(self.output_dir / filename)
        plt.close()
        print(f"Saved histogram to {filename}")

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

    def plot_parse_type_comparison(self, parse_type_data: Dict, title: str, filename: str):
        """Create side-by-side comparison of features across parse types."""
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

        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

        # Plot 1: Grouped bar chart for top features
        top_features = df.groupby('feature_id')['count'].sum().nlargest(10).index
        df_top = df[df['feature_id'].isin(top_features)]

        df_pivot = df_top.pivot(index='feature_id', columns='parse_type', values='count').fillna(0)
        df_pivot.plot(kind='bar', ax=ax1)
        ax1.set_title("Top 10 Features by Parse Type")
        ax1.set_xlabel("Feature ID")
        ax1.set_ylabel("Count")
        ax1.tick_params(axis='x', rotation=45)
        ax1.legend(title="Parse Type")

        # Plot 2: Stacked bar chart showing proportions
        df_props = df.groupby(['parse_type', 'feature_id'])['count'].sum().unstack().fillna(0)
        df_props_pct = df_props.div(df_props.sum(axis=1), axis=0) * 100

        df_props_pct.T.plot(kind='bar', stacked=True, ax=ax2)
        ax2.set_title("Feature Distribution Proportions")
        ax2.set_xlabel("Feature ID")
        ax2.set_ylabel("Percentage")
        ax2.tick_params(axis='x', rotation=45)
        ax2.legend(title="Parse Type")

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved parse type comparison to {filename}")

    def plot_newspaper_comparison(self, newspaper_data: Dict, title: str, filename: str):
        """Create comparison visualization across newspapers."""
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

        # Create grouped bar chart for top features
        top_features = df.groupby('feature_id')['count'].sum().nlargest(12).index
        df_top = df[df['feature_id'].isin(top_features)]

        plt.figure(figsize=(14, 8))
        df_pivot = df_top.pivot(index='feature_id', columns='newspaper', values='count').fillna(0)
        df_pivot.plot(kind='bar', width=0.8)

        plt.title(title)
        plt.xlabel("Feature ID")
        plt.ylabel("Count")
        plt.xticks(rotation=45, ha='right')
        plt.legend(title="Newspaper")
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

        # Create heatmap
        plt.figure(figsize=(16, 8))
        sns.heatmap(combined_matrix,
                   xticklabels=all_features,
                   yticklabels=combined_labels,
                   annot=False,
                   cmap='YlOrRd',
                   cbar_kws={'label': 'Feature Count'})

        plt.title(title)
        plt.xlabel("Features")
        plt.ylabel("Dimensions")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved feature coverage heatmap to {filename}")

    def plot_top_features_analysis(self, feature_stats: Dict, title: str, filename: str):
        """Create detailed analysis of top features."""
        # Sort features by occurrence
        sorted_features = sorted(feature_stats.items(),
                               key=lambda x: x[1]['total_occurrences'],
                               reverse=True)[:15]

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        # Plot 1: Top features by count
        feature_ids = [item[0] for item in sorted_features]
        counts = [item[1]['total_occurrences'] for item in sorted_features]

        ax1.bar(range(len(feature_ids)), counts, color='steelblue')
        ax1.set_xlabel("Features")
        ax1.set_ylabel("Count")
        ax1.set_title("Top 15 Features by Count")
        ax1.set_xticks(range(len(feature_ids)))
        ax1.set_xticklabels(feature_ids, rotation=45, ha='right')

        # Plot 2: Percentage distribution
        percentages = [item[1]['percentage_of_total'] for item in sorted_features]
        ax2.bar(range(len(feature_ids)), percentages, color='lightcoral')
        ax2.set_xlabel("Features")
        ax2.set_ylabel("Percentage of Total")
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
        """Create visualization of cross-dimensional analysis."""
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

        # Create subplot for each newspaper-parse_type combination
        combinations = df['combination'].unique()
        n_combinations = len(combinations)

        if n_combinations <= 2:
            fig, axes = plt.subplots(1, n_combinations, figsize=(8 * n_combinations, 6))
        else:
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))

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

            axes[i].bar(range(len(top_features)), top_features['count'], color=f'C{i}')
            axes[i].set_title(f"{combination}")
            axes[i].set_xlabel("Top Features")
            axes[i].set_ylabel("Count")
            axes[i].set_xticks(range(len(top_features)))
            axes[i].set_xticklabels(top_features['feature_id'], rotation=45, ha='right')

        plt.suptitle(title)
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved cross-dimensional analysis to {filename}")

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

        # Create pie chart and bar chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Pie chart
        ax1.pie(category_counts.values(),
               labels=category_counts.keys(),
               autopct='%1.1f%%',
               startangle=90)
        ax1.set_title("Distribution by Feature Category (Counts)")

        # Bar chart
        ax2.bar(category_counts.keys(), category_counts.values(),
               color=['steelblue', 'lightcoral', 'mediumseagreen', 'gold', 'mediumpurple', 'orange'])
        ax2.set_title("Feature Category Frequencies")
        ax2.set_xlabel("Category")
        ax2.set_ylabel("Count")
        ax2.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved feature category distribution to {filename}")

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
        """Create statistical comparison charts across newspapers."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        newspapers = list(newspaper_data.keys())

        # 1. Total events comparison
        total_events = [newspaper_data[np]['total_events'] for np in newspapers]
        ax1.bar(newspapers, total_events, color=['steelblue', 'lightcoral', 'mediumseagreen'])
        ax1.set_title("Total Events by Newspaper")
        ax1.set_ylabel("Number of Events")
        ax1.tick_params(axis='x', rotation=45)

        # 2. Average events per sentence
        avg_events = []
        for np in newspapers:
            total = newspaper_data[np]['total_events']
            # Estimate sentences (this could be refined with actual sentence count)
            estimated_sentences = max(1, total // 10)  # Rough estimate
            avg_events.append(total / estimated_sentences)

        ax2.bar(newspapers, avg_events, color=['orange', 'purple', 'brown'])
        ax2.set_title("Average Events per Sentence")
        ax2.set_ylabel("Events/Sentence")
        ax2.tick_params(axis='x', rotation=45)

        # 3. Feature diversity (unique features per newspaper)
        feature_diversity = [len(newspaper_data[np]['feature_counts']) for np in newspapers]
        ax3.bar(newspapers, feature_diversity, color=['teal', 'coral', 'gold'])
        ax3.set_title("Feature Diversity by Newspaper")
        ax3.set_ylabel("Number of Unique Features")
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
                    axes[i].set_title(f"{feature_id}")
                    continue

                # Get top 10 transformations
                top_transformations = sorted(transformations.items(), key=lambda x: x[1], reverse=True)[:10]
                trans_names = [t[0][:15] + '...' if len(t[0]) > 15 else t[0] for t, _ in top_transformations]
                trans_counts = [count for _, count in top_transformations]

                axes[i].barh(range(len(trans_names)), trans_counts, color=f'C{i}')
                axes[i].set_yticks(range(len(trans_names)))
                axes[i].set_yticklabels(trans_names, fontsize=8)
                axes[i].set_title(f"{feature_id}")
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
            ax1.set_title(f"Top Transformations for {feature_id}")
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
        ax2.set_title(f"Transformation Distribution for {feature_id}")

        # 3. Transformation type breakdown
        deletions = sum(1 for t in transformations.keys() if t.endswith('→ABSENT'))
        additions = sum(1 for t in transformations.keys() if t.startswith('ABSENT→'))
        changes = len(transformations) - deletions - additions

        type_counts = [deletions, additions, changes]
        type_labels = ['Deletions', 'Additions', 'Changes']

        ax3.bar(type_labels, type_counts, color=['red', 'green', 'blue'], alpha=0.7)
        ax3.set_title(f"Transformation Types for {feature_id}")
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
        ax4.set_title(f"Statistics for {feature_id}")
        ax4.axis('off')

        plt.suptitle(f"Detailed Analysis: {feature_id}")
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
