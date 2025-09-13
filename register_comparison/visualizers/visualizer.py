
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
from typing import Dict
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

    # You can add more visualization functions here for structural differences etc.

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
