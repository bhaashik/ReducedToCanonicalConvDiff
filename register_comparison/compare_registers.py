from pathlib import Path
from typing import List
from conllu import parse_incr
from nltk.tree import Tree
import pandas as pd
# OLD VERSION - INCORRECT: config module not in path when running from subdirectory
# from config import BASE_DIR
# NEW VERSION - CORRECTED: import from parent directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import BASE_DIR
# import paths_config
from pathlib import Path
from paths_config import (
    SCHEMA_PATH,
    NEWSPAPERS,
    REGISTERS,
    TEXT_FILES,
    CONLLU_FILES,
    CONST_FILES
)

print("===========================")
print(os.getcwd())
print("===========================")
print(BASE_DIR)
print("===========================")

from register_comparison.meta_data.schema import FeatureSchema
from register_comparison.aligners.aligner import Aligner
from register_comparison.aggregators.aggregator import Aggregator
from register_comparison.outputs.output_creators import Outputs
from register_comparison.stat_runners.stats import StatsRunner
from register_comparison.extractors.extractor import FeatureExtractor
# OLD VERSION - BROKEN: comparator doesn't detect schema features
# from register_comparison.comparators.comparator import Comparator
# NEW VERSION - FIXED: use schema-based comparator
from register_comparison.comparators.schema_comparator import SchemaBasedComparator as Comparator
from register_comparison.visualizers.visualizer import Visualizer

# readers.py: Load the plain text parallel data of registers
# OLD VERSION - DUPLICATE FUNCTIONS: These are now handled by readers.py module
# def read_plain_text(path: Path) -> List[str]:
#     """Reads a plain text file and returns a list of sentences (stripped)."""
#     with open(path, 'r', encoding='utf-8') as f:
#         return [line.strip() for line in f if line.strip()]
#
# def read_conllu(path: Path):
#     """Reads a CoNLL-U file and yields TokenList objects for each sentence."""
#     with open(path, 'r', encoding='utf-8') as f:
#         for tokenlist in parse_incr(f):
#             yield tokenlist
#
# def read_constituency(path: Path) -> List[Tree]:
#     """Reads bracketed constituency parse strings into NLTK Tree objects."""
#     trees = []
#     with open(path, 'r', encoding='utf-8') as f:
#         for line in f:
#             line = line.strip()
#             if not line:
#                 continue
#             trees.append(Tree.fromstring(line))
#     return trees

# NEW VERSION - CORRECTED: Reader functions now in register_comparison.readers.readers module

# config.py: Load the parallel data of registers

# Base data directory (adjust if needed)
# BASE_DIR = Path(__file__).resolve().parent / "data"

# # Feature schema path
# SCHEMA_PATH = BASE_DIR / "diff-ontology-ver-3.0.json"
#
# # Newspaper names
# NEWSPAPERS = ["Hindustan-Times", "The-Hindu", "Times-of-India"]
#
# # Registers
# REGISTERS = {
#     "canonical": "canonical",
#     "headlines": "headlines"
# }
#
# # File mapping for plain texts
# TEXT_FILES = {
#     "Hindustan-Times": {
#         "canonical": BASE_DIR / "Hindustan-Times-canonical.txt",
#         "headlines": BASE_DIR / "Hindustan-Times-headlines.txt"
#     },
#     "The-Hindu": {
#         "canonical": BASE_DIR / "The-Hindu-corrected-canonical.txt",
#         "headlines": BASE_DIR / "The-Hindu-corrected-headlines.txt"
#     },
#     "Times-of-India": {
#         "canonical": BASE_DIR / "Times-of-India-corrected-canonical.txt",
#         "headlines": BASE_DIR / "Times-of-India-corrected-headlines.txt"
#     }
# }
#
# # File mapping for CoNLL-U dependency parses
# CONLLU_FILES = {
#     "Hindustan-Times": {
#         "canonical": BASE_DIR / "Hindustan-Times-canonical-stanza-parsed-deps.conllu",
#         "headlines": BASE_DIR / "Hindustan-Times-headlines-stanza-parsed-deps.conllu"
#     },
#     "The-Hindu": {
#         "canonical": BASE_DIR / "The-Hindu-canonical-stanza-parsed-deps.conllu",
#         "headlines": BASE_DIR / "The-Hindu-headlines-stanza-parsed-deps.conllu"
#     },
#     "Times-of-India": {
#         "canonical": BASE_DIR / "Times-of-India-canonical-stanza-parsed-deps.conllu",
#         "headlines": BASE_DIR / "Times-of-India-headlines-stanza-parsed-deps.conllu"
#     }
# }
#
# # File mapping for constituency parses (bracketed format)
# CONST_FILES = {
#     "Hindustan-Times": {
#         "canonical": BASE_DIR / "Hindustan-Times-canonical-stanza-parsed-constituency.txt",
#         "headlines": BASE_DIR / "Hindustan-Times-headlines-stanza-parsed-constituency.txt"
#     },
#     "The-Hindu": {
#         "canonical": BASE_DIR / "The-Hindu-canonical-stanza-parsed-constituency.txt",
#         "headlines": BASE_DIR / "The-Hindu-headlines-stanza-parsed-constituency.txt"
#     },
#     "Times-of-India": {
#         "canonical": BASE_DIR / "Times-of-India-canonical-stanza-parsed-constituency.txt",
#         "headlines": BASE_DIR / "Times-of-India-headlines-stanza-parsed-constituency.txt"
#     }
# }

# schema.py: Load the Schema file(s)

# from pathlib import Path
# from schema import FeatureSchema

# schema = FeatureSchema(Path(BASE_DIR / "data/diff-ontology-ver-3.0.json"))
schema = FeatureSchema(SCHEMA_PATH)
schema.load_schema()

# Number of features
print(schema)

# Access by ID
feat = schema.get_feature_by_mnemonic("FW-DEL")
print(feat.mnemonic_code, feat.name, feat.description)

# List its possible values
for val in feat.values:
    print(val.mnemonic, "-", val.value)

# Access specific value description
print(feat.get_value_by_mnemonic("ART-DEL").value)

# from pathlib import Path

# Base data directory (adjust if needed)
# BASE_DIR = Path(__file__).resolve().parent / "data"

# Feature schema path
# SCHEMA_PATH = BASE_DIR / "diff-ontology-ver-3.0.json"

# Newspaper names
# NEWSPAPERS = ["Hindustan-Times", "The-Hindu", "Times-of-India"]

# Registers
# REGISTERS = {
#     "canonical": "canonical",
#     "headlines": "headlines"
# }
#
# # File mapping for plain texts
# TEXT_FILES = {
#     "Hindustan-Times": {
#         "canonical": BASE_DIR / "input/input-single-line-break/Hindustan-Times-canonical.txt",
#         "headlines": BASE_DIR / "input/input-single-line-break/Hindustan-Times-headlines.txt"
#     },
#     "The-Hindu": {
#         "canonical": BASE_DIR / "input/input-single-line-break/The-Hindu-corrected-canonical.txt",
#         "headlines": BASE_DIR / "input/input-single-line-break/The-Hindu-corrected-headlines.txt"
#     },
#     "Times-of-India": {
#         "canonical": BASE_DIR / "input/input-single-line-break/Times-of-India-corrected-canonical.txt",
#         "headlines": BASE_DIR / "input/input-single-line-break/Times-of-India-corrected-headlines.txt"
#     }
# }
#
# # File mapping for CoNLL-U dependency parses
# CONLLU_FILES = {
#     "Hindustan-Times": {
#         "canonical": BASE_DIR / "data/input/dependecy-parsed/Hindustan-Times-canonical-stanza-parsed-deps.conllu",
#         "headlines": BASE_DIR / "data/input/dependecy-parsed/Hindustan-Times-headlines-stanza-parsed-deps.conllu"
#     },
#     "The-Hindu": {
#         "canonical": BASE_DIR / "data/input/dependecy-parsed/The-Hindu-canonical-stanza-parsed-deps.conllu",
#         "headlines": BASE_DIR / "data/input/dependecy-parsed/The-Hindu-headlines-stanza-parsed-deps.conllu"
#     },
#     "Times-of-India": {
#         "canonical": BASE_DIR / "data/input/dependecy-parsed/Times-of-India-canonical-stanza-parsed-deps.conllu",
#         "headlines": BASE_DIR / "data/input/dependecy-parsed/Times-of-India-headlines-stanza-parsed-deps.conllu"
#     }
# }
#
# # File mapping for constituency parses (bracketed format)
# CONST_FILES = {
#     "Hindustan-Times": {
#         "canonical": BASE_DIR / "data/input/constituency-parsed/Hindustan-Times-canonical-stanza-parsed-constituency.txt",
#         "headlines": BASE_DIR / "data/input/constituency-parsed/Hindustan-Times-headlines-stanza-parsed-constituency.txt"
#     },
#     "The-Hindu": {
#         "canonical": BASE_DIR / "data/input/constituency-parsed/The-Hindu-canonical-stanza-parsed-constituency.txt",
#         "headlines": BASE_DIR / "data/input/constituency-parsed/The-Hindu-headlines-stanza-parsed-constituency.txt"
#     },
#     "Times-of-India": {
#         "canonical": BASE_DIR / "data/input/constituency-parsed/Times-of-India-canonical-stanza-parsed-constituency.txt",
#         "headlines": BASE_DIR / "data/input/constituency-parsed/Times-of-India-headlines-stanza-parsed-constituency.txt"
#     }
# }

# aligner.py: Align the sentence pairs of the parallel data

# extractor.py: Extract features representing 'events' of differences from the (naively) word aligned sentence pairs of the parallel data

# comparator.py: Compare the registers in terms of extracted features

# aggregator.py: Aggretate all the compared features for the registers

# 1. Load schema
# schema = FeatureSchema(Path("data/diff-ontology-ver-3.0.json")
# schema.load_schema()

current_news_paper_name = "Times-of-India"

# 2. Prepare aligner and get pairs (example, one newspaper setup)
# OLD VERSION - INCORRECT: schema doesn't have data lists
# aligner = Aligner(
#     texts_canonical=schema.canon_text_list,
#     texts_headlines=schema.head_text_list,
#     deps_canonical=schema.canon_dep_list,
#     deps_headlines=schema.head_dep_list,
#     consts_canonical=schema.canon_const_list,
#     consts_headlines=schema.head_const_list,
#     newspaper_name = current_news_paper_name
# )

# NEW VERSION - CORRECTED: use loaded_data module
from data.loaded_data import loaded_data

# Load data for the newspaper
loaded_data.load_newspaper_data(current_news_paper_name)

# Prepare aligner with loaded data
aligner = Aligner(
    texts_canonical=loaded_data.get_canonical_text(current_news_paper_name),
    texts_headlines=loaded_data.get_headlines_text(current_news_paper_name),
    deps_canonical=loaded_data.get_canonical_deps(current_news_paper_name),
    deps_headlines=loaded_data.get_headlines_deps(current_news_paper_name),
    consts_canonical=loaded_data.get_canonical_const(current_news_paper_name),
    consts_headlines=loaded_data.get_headlines_const(current_news_paper_name),
    newspaper_name=current_news_paper_name
)
pairs = aligner.align()

# 3. Extract features and compare with TED analysis
extractor = FeatureExtractor(schema)
# Import and configure TED algorithms for comprehensive tree edit distance analysis
from register_comparison.ted_config import TEDConfig
ted_config = TEDConfig.default()  # Uses all four TED algorithms
comparator = Comparator(schema, ted_config)
aggregator = Aggregator()

for pair in pairs:
    features = extractor.extract_features(pair)
    events = comparator.compare_pair(pair, features)
    aggregator.add_events(events)

# Collect sentence-level TED scores for distribution analysis
sentence_ted_scores = comparator.get_sentence_level_ted_scores()
print(f"Collected {len(sentence_ted_scores)} sentence-level TED scores")

# 4. Check counts
print("Global counts:", aggregator.global_counts())
print("Counts per newspaper:", aggregator.per_newspaper_counts())

# 5. Convert to matrix for DataFrame/CSV
matrix = aggregator.to_matrix(aggregator.global_events)

# output_creator.py: Save the output in terms of aggregated and pair-wise features

# stats.py: Run some statistical tests etc. on the (aggregated) features for the registers

# Usage:

# from stats import StatsRunner
# import pandas as pd

# Suppose we have feature counts:
# matrix = [
#     {"feature_id": "FV001", "count_a": 15, "total_a": 100, "count_b": 5, "total_b": 100},
#     {"feature_id": "FV002", "count_a": 40, "total_a": 100, "count_b": 60, "total_b": 100},
# ]

df = pd.DataFrame(matrix)

# FIXED VERSION: Use proper data format for StatsRunner
print("Running statistical significance testing...")
stats_runner = StatsRunner()

# Get data in format expected by StatsRunner
stats_data = aggregator.to_stats_runner_format()
stats_df = pd.DataFrame(stats_data)

print(f"Statistical testing data shape: {stats_df.shape}")
print("Statistical testing columns:", stats_df.columns.tolist())

if not stats_df.empty:
    # Run statistical tests
    summary_stats_df = stats_runner.run_for_dataframe(stats_df, "canonical", "headlines")
    print(f"Statistical tests completed for {len(summary_stats_df)} features")
    print("Sample statistical results:")
    print(summary_stats_df[['feature_id', 'chi2', 'chi_p', 'fisher_p', 'odds_ratio']].head())
else:
    print("No data available for statistical testing")
    summary_stats_df = pd.DataFrame()

# visualizer.py: Visualize the statistics and statistical etc. for the registers

# Usage:

# from pathlib import Path
# from visualizer import Visualizer
# # from register_comparison.outputs.output_creator import OutputCreator
# from register_comparison.meta_data.schema import FeatureSchema as schema
# # from register_comparison.aggregators.aggregator import Aggregator

# output_dir = Path("results")
output_dir = BASE_DIR / "output" / current_news_paper_name

outputs = Outputs(output_dir, schema)
visualizer = Visualizer(output_dir, schema)
# from register_comparison.aggregators.aggregator import Aggregator as aggregator, Aggregator

# Save feature frequency CSV
feature_counts = aggregator.global_counts()
# OLD VERSION - INCORRECT: passing Path object instead of filename string
# outputs.save_feature_matrix_csv(feature_counts, output_dir / "feature_freq_global.csv")
# NEW VERSION - CORRECTED: pass just the filename string
outputs.save_feature_matrix_csv(feature_counts, "feature_freq_global.csv")

# Save detailed event table CSV
# OLD VERSION - INCORRECT: passing string literal instead of filename
# outputs.save_events_csv(aggregator.global_events, "output_dir / events_global.csv")
# NEW VERSION - CORRECTED: pass just the filename string
outputs.save_events_csv(aggregator.global_events, "events_global.csv")

# Save summary statistics CSV (suppose from stats.py)
# outputs.save_summary_stats_csv(summary_stats_df, "summary_stats_global.csv")
# OLD VERSION - INCORRECT: passing string literal instead of filename
# outputs.save_summary_stats_csv(summary_stats_df, "output_dir / summary_stats_global.csv")
# NEW VERSION - CORRECTED: pass just the filename string
outputs.save_summary_stats_csv(summary_stats_df, "summary_stats_global.csv")

# Generate basic summaries (for backward compatibility)
print("Generating basic LaTeX and Markdown summaries...")
outputs.generate_latex_summary("summary_features.tex")
outputs.generate_markdown_summary("summary_features.md")

# # Save interpretive notes (prepare as string beforehand)
# outputs.save_interpretive_notes(notes_text, "interpretive_notes.txt")

# ========================================
# COMPREHENSIVE MULTI-DIMENSIONAL ANALYSIS
# ========================================

print("\n" + "="*60)
print("COMPREHENSIVE MULTI-DIMENSIONAL ANALYSIS")
print("="*60)

# Generate comprehensive analysis
print("Generating comprehensive analysis...")
comprehensive_analysis = aggregator.get_comprehensive_analysis()
statistical_summary = aggregator.get_statistical_summary()

# Add sentence-level TED scores to comprehensive analysis
print(f"Adding {len(sentence_ted_scores)} sentence-level TED scores to analysis...")
comprehensive_analysis['sentence_level_ted_scores'] = sentence_ted_scores

print(f"Analysis completed:")
print(f"  - Total events analyzed: {comprehensive_analysis['global']['total_events']}")
print(f"  - Unique features detected: {len(comprehensive_analysis['global']['feature_counts'])}")
print(f"  - Newspapers analyzed: {len(comprehensive_analysis['by_newspaper'])}")
print(f"  - Parse types analyzed: {len(comprehensive_analysis['by_parse_type'])}")

# Save comprehensive analysis to JSON and multiple CSV files
print("\nSaving comprehensive analysis files...")
outputs.save_comprehensive_analysis(comprehensive_analysis, "comprehensive_analysis")

# Save feature-value pairs analysis
print("Saving feature-value pairs analysis...")
outputs.save_feature_value_pairs(comprehensive_analysis, "feature_value_pairs")

# Save statistical summary
print("Saving statistical summary...")
outputs.save_statistical_summary(statistical_summary, "statistical_summary")

# ========================================
# COMPREHENSIVE VISUALIZATIONS
# ========================================

print("\n" + "="*60)
print("GENERATING FEATURE-VALUE ANALYSIS")
print("="*60)

# Generate comprehensive feature-value analysis
print("Generating feature-value analysis...")
feature_value_analysis = aggregator.get_feature_value_analysis()
print(f"Feature-value analysis completed for {len(feature_value_analysis['global_feature_values'])} features")

# Save feature-value analysis
print("Saving feature-value analysis...")
outputs.save_feature_value_analysis(feature_value_analysis, "feature_value_analysis")

print("\n" + "="*60)
print("GENERATING COMPREHENSIVE VISUALIZATIONS")
print("="*60)

# Generate all visualizations
print("Creating comprehensive visualizations...")
visualizer.create_comprehensive_visualizations(comprehensive_analysis, statistical_summary)

# Generate additional statistical summary visualizations
print("Creating statistical summary visualizations...")
visualizer.create_statistical_summary_visualizations(comprehensive_analysis, statistical_summary)

# Generate feature-value visualizations
print("Creating feature-value visualizations...")
visualizer.create_feature_value_visualizations(feature_value_analysis)

# Also keep the original simple visualization
print("Creating additional basic visualizations...")
visualizer.plot_feature_frequencies(feature_counts, "Global Feature Frequencies", "feature_freq_global.png")

# ========================================
# ENHANCED REPORT GENERATION
# ========================================

print("\n" + "="*60)
print("GENERATING COMPREHENSIVE REPORTS")
print("="*60)

# Generate comprehensive reports
print("Generating comprehensive LaTeX report...")
outputs.generate_comprehensive_latex_report(comprehensive_analysis, statistical_summary, "comprehensive_report.tex")

print("Generating comprehensive Markdown report...")
outputs.generate_comprehensive_markdown_report(comprehensive_analysis, statistical_summary, "comprehensive_report.md")

print("\n" + "="*60)
print("COMPREHENSIVE FEATURE-VALUE ANALYSIS COMPLETED!")
print("="*60)
print(f"✅ Generated {len(comprehensive_analysis['global']['feature_counts'])} feature analyses")
print(f"✅ Created comprehensive visualizations")
print(f"✅ Saved detailed CSV and JSON exports")
print(f"✅ Generated comprehensive reports")
print(f"✅ Total linguistic difference events: {comprehensive_analysis['global']['total_events']:,}")
print("✅ Feature-value transformations analysis completed")

# Count total unique transformations
total_transformations = sum(
    len(transforms) for transforms in feature_value_analysis['global_feature_values'].values()
)
print(f"✅ Total unique transformation types: {total_transformations:,}")

# Show most active features
most_active = sorted(
    [(f, len(t)) for f, t in feature_value_analysis['global_feature_values'].items()],
    key=lambda x: x[1], reverse=True
)[:5]
print("✅ Most transformation-diverse features:")
for feature_id, count in most_active:
    print(f"   - {feature_id}: {count} unique transformation types")

print("="*60)




