
# Version 1

# import pandas as pd
# from pathlib import Path
# from typing import List, Dict, Any
# from register_comparison.meta_data.schema import FeatureSchema
# from register_comparison.comparators.comparator import DifferenceEvent
#
# class OutputCreator:
#     def __init__(self, output_dir: Path, schema: FeatureSchema):
#         self.output_dir = output_dir
#         self.schema = schema
#         self.output_dir.mkdir(parents=True, exist_ok=True)
#
#     def save_feature_matrix_csv(self, feature_counts: Dict[str, int], filename: str):
#         """
#         Save a CSV with feature IDs, mnemonics, names, counts.
#         """
#         rows = []
#         for feat_id, count in feature_counts.items():
#             feat = self.schema.get_feature_by_id(feat_id)
#             rows.append({
#                 "feature_id": feat_id,
#                 "mnemonic": feat.mnemonic if feat else None,
#                 "name": feat.name if feat else None,
#                 "count": count
#             })
#         df = pd.DataFrame(rows).sort_values(by="count", ascending=False)
#         df.to_csv(self.output_dir / filename, index=False)
#         print(f"Saved feature matrix CSV to {filename}")
#
#     def save_events_csv(self, events: List[DifferenceEvent], filename: str):
#         """
#         Save detailed event tables with lexical and syntactic context.
#         """
#         rows = [ev.to_dict() for ev in events]
#         df = pd.DataFrame(rows)
#         df.to_csv(self.output_dir / filename, index=False)
#         print(f"Saved detailed events CSV to {filename}")
#
#     def save_summary_stats_csv(self, stats_df: pd.DataFrame, filename: str):
#         """
#         Save summary statistics CSV (e.g., output from stats.py).
#         """
#         stats_df.to_csv(self.output_dir / filename, index=False)
#         print(f"Saved summary statistics CSV to {filename}")
#
#     def generate_latex_summary(self, filename: str):
#         """
#         Generate a LaTeX summary linking features to linguistic principles.
#         """
#         features = self.schema.list_all_features()
#         lines = [
#             "\\begin{tabular}{lll}",
#             "\\hline",
#             "Feature ID & Mnemonic & Description \\\\",
#             "\\hline"
#         ]
#         for f in features:
#             desc = f.description.replace("&", "\\&") if f.description else ""
#             lines.append(f"{f.id} & {f.mnemonic} & {desc} \\\\")
#         lines.append("\\hline")
#         lines.append("\\end{tabular}")
#
#         with open(self.output_dir / filename, 'w', encoding='utf-8') as f:
#             f.write("\n".join(lines))
#         print(f"Saved LaTeX summary to {filename}")
#
#     def generate_markdown_summary(self, filename: str):
#         """
#         Generate a Markdown summary linking features to linguistic principles.
#         """
#         features = self.schema.list_all_features()
#         lines = [
#             "| Feature ID | Mnemonic | Description |",
#             "|------------|----------|-------------|"
#         ]
#         for f in features:
#             desc = f.description or ""
#             lines.append(f"| {f.id} | {f.mnemonic} | {desc} |")
#
#         with open(self.output_dir / filename, 'w', encoding='utf-8') as f:
#             f.write("\n".join(lines))
#         print(f"Saved Markdown summary to {filename}")
#
#     def save_interpretive_notes(self, notes: str, filename: str):
#         """
#         Save interpretive notes as a plain text file.
#         """
#         with open(self.output_dir / filename, 'w', encoding='utf-8') as f:
#             f.write(notes)
#         print(f"Saved interpretive notes to {filename}")

# Usage:
# ...

# Version 2

import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from register_comparison.meta_data.schema import FeatureSchema
from register_comparison.comparators.comparator import DifferenceEvent

class Outputs:
    def __init__(self, output_dir: Path, schema: FeatureSchema):
        self.output_dir = output_dir
        self.schema = schema
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_feature_matrix_csv(self, feature_counts: Dict[str, int], filename: str):
        """
        Save a CSV with feature IDs, mnemonics, names, counts.
        """
        rows = []
        for feat_id, count in feature_counts.items():
            feat = self.schema.get_feature_by_id(feat_id)
            rows.append({
                "feature_id": feat_id,
                "mnemonic": feat.mnemonic if feat else None,
                "name": feat.name if feat else None,
                "count": count
            })
        df = pd.DataFrame(rows).sort_values(by="count", ascending=False)
        df.to_csv(self.output_dir / filename, index=False)
        print(f"Saved feature matrix CSV to {filename}")

    def save_events_csv(self, events: List[DifferenceEvent], filename: str):
        """
        Save detailed event tables with lexical and syntactic context.
        """
        rows = [ev.to_dict() for ev in events]
        df = pd.DataFrame(rows)
        df.to_csv(self.output_dir / filename, index=False)
        print(f"Saved detailed events CSV to {filename}")

    def save_summary_stats_csv(self, stats_df: pd.DataFrame, filename: str):
        """
        Save summary statistics CSV (e.g., output from stats.py).
        """
        stats_df.to_csv(self.output_dir / filename, index=False)
        print(f"Saved summary statistics CSV to {filename}")

    def generate_latex_summary(self, filename: str):
        """
        Generate a LaTeX summary linking features to linguistic principles.
        """
        features = self.schema.list_all_features()
        lines = [
            "\\begin{tabular}{lll}",
            "\\hline",
            "Feature ID & Mnemonic & Description \\\\",
            "\\hline"
        ]
        for f in features:
            desc = f.description.replace("&", "\\&") if f.description else ""
            lines.append(f"{f.id} & {f.mnemonic} & {desc} \\\\")
        lines.append("\\hline")
        lines.append("\\end{tabular}")

        with open(self.output_dir / filename, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        print(f"Saved LaTeX summary to {filename}")

    def generate_markdown_summary(self, filename: str):
        """
        Generate a Markdown summary linking features to linguistic principles.
        """
        features = self.schema.list_all_features()
        lines = [
            "| Feature ID | Mnemonic | Description |",
            "|------------|----------|-------------|"
        ]
        for f in features:
            desc = f.description or ""
            lines.append(f"| {f.id} | {f.mnemonic} | {desc} |")

        with open(self.output_dir / filename, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        print(f"Saved Markdown summary to {filename}")

    def save_interpretive_notes(self, notes: str, filename: str):
        """
        Save interpretive notes as a plain text file.
        """
        with open(self.output_dir / filename, 'w', encoding='utf-8') as f:
            f.write(notes)
        print(f"Saved interpretive notes to {filename}")
