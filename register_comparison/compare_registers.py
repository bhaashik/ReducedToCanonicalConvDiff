from pathlib import Path
from typing import List
from conllu import parse_incr
from nltk.tree import Tree
import pandas as pd

from register_comparison.meta_data.schema import FeatureSchema
from aligners.aligner import Aligner
from register_comparison.aggregators.aggregator import Aggregator
from register_comparison.outputs.output_creators import Outputs
from register_comparison.stat_runners.stats import StatsRunner
from register_comparison.visualizers.visualizer import Visualizer

# from pathlib import Path
from register_comparison.meta_data.schema import FeatureSchema
from register_comparison.aggregators.aggregator import Aggregator as aggregator, Aggregator

# from stat_runners.stats import StatsRunner
# from register_comparison.outputs.output_creator import OutputCreator
from register_comparison.meta_data.schema import FeatureSchema as schema
# from register_comparison.aggregators.aggregator import Aggregator

# readers.py: Load the plain text parallel data of registers

# from pathlib import Path
# from typing import List
# from conllu import parse_incr
# from nltk.tree import Tree

def read_plain_text(path: Path) -> List[str]:
    """Reads a plain text file and returns a list of sentences (stripped)."""
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def read_conllu(path: Path):
    """Reads a CoNLL-U file and yields TokenList objects for each sentence."""
    with open(path, 'r', encoding='utf-8') as f:
        for tokenlist in parse_incr(f):
            yield tokenlist

def read_constituency(path: Path) -> List[Tree]:
    """Reads bracketed constituency parse strings into NLTK Tree objects."""
    trees = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            trees.append(Tree.fromstring(line))
    return trees

# config.py: Load the parallel data of registers

from pathlib import Path

# Base data directory (adjust if needed)
BASE_DIR = Path(__file__).resolve().parent / "data"

# Feature schema path
SCHEMA_PATH = BASE_DIR / "diff-ontology-ver-3.0.json"

# Newspaper names
NEWSPAPERS = ["Hindustan-Times", "The-Hindu", "Times-of-India"]

# Registers
REGISTERS = {
    "canonical": "canonical",
    "headlines": "headlines"
}

# File mapping for plain texts
TEXT_FILES = {
    "Hindustan-Times": {
        "canonical": BASE_DIR / "Hindustan-Times-canonical.txt",
        "headlines": BASE_DIR / "Hindustan-Times-headlines.txt"
    },
    "The-Hindu": {
        "canonical": BASE_DIR / "The-Hindu-corrected-canonical.txt",
        "headlines": BASE_DIR / "The-Hindu-corrected-headlines.txt"
    },
    "Times-of-India": {
        "canonical": BASE_DIR / "Times-of-India-corrected-canonical.txt",
        "headlines": BASE_DIR / "Times-of-India-corrected-headlines.txt"
    }
}

# File mapping for CoNLL-U dependency parses
CONLLU_FILES = {
    "Hindustan-Times": {
        "canonical": BASE_DIR / "Hindustan-Times-canonical-stanza-parsed-deps.conllu",
        "headlines": BASE_DIR / "Hindustan-Times-headlines-stanza-parsed-deps.conllu"
    },
    "The-Hindu": {
        "canonical": BASE_DIR / "The-Hindu-canonical-stanza-parsed-deps.conllu",
        "headlines": BASE_DIR / "The-Hindu-headlines-stanza-parsed-deps.conllu"
    },
    "Times-of-India": {
        "canonical": BASE_DIR / "Times-of-India-canonical-stanza-parsed-deps.conllu",
        "headlines": BASE_DIR / "Times-of-India-headlines-stanza-parsed-deps.conllu"
    }
}

# File mapping for constituency parses (bracketed format)
CONST_FILES = {
    "Hindustan-Times": {
        "canonical": BASE_DIR / "Hindustan-Times-canonical-stanza-parsed-constituency.txt",
        "headlines": BASE_DIR / "Hindustan-Times-headlines-stanza-parsed-constituency.txt"
    },
    "The-Hindu": {
        "canonical": BASE_DIR / "The-Hindu-canonical-stanza-parsed-constituency.txt",
        "headlines": BASE_DIR / "The-Hindu-headlines-stanza-parsed-constituency.txt"
    },
    "Times-of-India": {
        "canonical": BASE_DIR / "Times-of-India-canonical-stanza-parsed-constituency.txt",
        "headlines": BASE_DIR / "Times-of-India-headlines-stanza-parsed-constituency.txt"
    }
}

# schema.py: Load the Schema file(s)

# from pathlib import Path
# from schema import FeatureSchema

schema = FeatureSchema(Path("data/diff-ontology-ver-3.0.json"))
schema.load_schema()

# Number of features
print(schema)

# Access by ID
feat = schema.get_feature_by_id("FV001")
print(feat.id, feat.mnemonic, feat.name, feat.description)

# List its possible values
for val in feat.values:
    print(val.code, "-", val.desc)

# Access specific value description
print(feat.get_value_by_code("1").desc)


# from pathlib import Path

# Base data directory (adjust if needed)
BASE_DIR = Path(__file__).resolve().parent / "data"

# Feature schema path
SCHEMA_PATH = BASE_DIR / "diff-ontology-ver-3.0.json"

# Newspaper names
# NEWSPAPERS = ["Hindustan-Times", "The-Hindu", "Times-of-India"]

# Registers
REGISTERS = {
    "canonical": "canonical",
    "headlines": "headlines"
}

# File mapping for plain texts
TEXT_FILES = {
    "Hindustan-Times": {
        "canonical": BASE_DIR / "input/input-single-line-break/Hindustan-Times-canonical.txt",
        "headlines": BASE_DIR / "input/input-single-line-break/Hindustan-Times-headlines.txt"
    },
    "The-Hindu": {
        "canonical": BASE_DIR / "input/input-single-line-break/The-Hindu-corrected-canonical.txt",
        "headlines": BASE_DIR / "input/input-single-line-break/The-Hindu-corrected-headlines.txt"
    },
    "Times-of-India": {
        "canonical": BASE_DIR / "input/input-single-line-break/Times-of-India-corrected-canonical.txt",
        "headlines": BASE_DIR / "input/input-single-line-break/Times-of-India-corrected-headlines.txt"
    }
}

# File mapping for CoNLL-U dependency parses
CONLLU_FILES = {
    "Hindustan-Times": {
        "canonical": BASE_DIR / "data/input/dependecy-parsed/Hindustan-Times-canonical-stanza-parsed-deps.conllu",
        "headlines": BASE_DIR / "data/input/dependecy-parsed/Hindustan-Times-headlines-stanza-parsed-deps.conllu"
    },
    "The-Hindu": {
        "canonical": BASE_DIR / "data/input/dependecy-parsed/The-Hindu-canonical-stanza-parsed-deps.conllu",
        "headlines": BASE_DIR / "data/input/dependecy-parsed/The-Hindu-headlines-stanza-parsed-deps.conllu"
    },
    "Times-of-India": {
        "canonical": BASE_DIR / "data/input/dependecy-parsed/Times-of-India-canonical-stanza-parsed-deps.conllu",
        "headlines": BASE_DIR / "data/input/dependecy-parsed/Times-of-India-headlines-stanza-parsed-deps.conllu"
    }
}

# File mapping for constituency parses (bracketed format)
CONST_FILES = {
    "Hindustan-Times": {
        "canonical": BASE_DIR / "data/input/constituency-parsed/Hindustan-Times-canonical-stanza-parsed-constituency.txt",
        "headlines": BASE_DIR / "data/input/constituency-parsed/Hindustan-Times-headlines-stanza-parsed-constituency.txt"
    },
    "The-Hindu": {
        "canonical": BASE_DIR / "data/input/constituency-parsed/The-Hindu-canonical-stanza-parsed-constituency.txt",
        "headlines": BASE_DIR / "data/input/constituency-parsed/The-Hindu-headlines-stanza-parsed-constituency.txt"
    },
    "Times-of-India": {
        "canonical": BASE_DIR / "data/input/constituency-parsed/Times-of-India-canonical-stanza-parsed-constituency.txt",
        "headlines": BASE_DIR / "data/input/constituency-parsed/Times-of-India-headlines-stanza-parsed-constituency.txt"
    }
}

# aligner.py: Align the sentence pairs of the parallel data

# extractor.py: Extract features representing 'events' of differences from the (naively) word aligned sentence pairs of the parallel data

# comparator.py: Compare the registers in terms of extracted features

# aggregator.py: Aggretate all the compared features for the registers

# 1. Load schema
schema = FeatureSchema("data/diff-ontology-ver-3.0.json")
schema.load_schema()

current_news_paper_name = "Times-of-India"

# 2. Prepare aligner and get pairs (example, one newspaper setup)
aligner = Aligner(
    texts_canonical=schema.canon_text_list,
    texts_headlines=schema.head_text_list,
    deps_canonical=schema.canon_dep_list,
    deps_headlines=schema.head_dep_list,
    consts_canonical=schema.canon_const_list,
    consts_headlines=schema.head_const_list,
    # newspaper_name="Times-of-India"
    newspaper_name = current_news_paper_name
)
pairs = aligner.align()

# 3. Extract features
extractor = FeatureExtractor(schema)
comparator = Comparator(schema)
aggregator = Aggregator()

for pair in pairs:
    features = extractor.extract_features(pair)
    events = comparator.compare_pair(pair, features)
    aggregator.add_events(events)

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

stats_runner = StatsRunner()
summary_stats_df = stats_runner.run_for_dataframe(df, "canonical", "headlines")

print(summary_stats_df)

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
visualizer = Visualizer(output_dir)
# from register_comparison.aggregators.aggregator import Aggregator as aggregator, Aggregator

# Save feature frequency CSV
feature_counts = aggregator.global_counts()
outputs.save_feature_matrix_csv(feature_counts, output_dir / "feature_freq_global.csv")

# Save detailed event table CSV
outputs.save_events_csv(aggregator.global_events, "output_dir / events_global.csv")

# Save summary statistics CSV (suppose from stats.py)
# outputs.save_summary_stats_csv(summary_stats_df, "summary_stats_global.csv")
outputs.save_summary_stats_csv(summary_stats_df, "output_dir / summary_stats_global.csv")

# Generate LaTeX and Markdown summaries
outputs.generate_latex_summary("output_dir / summary_features.tex")
outputs.generate_markdown_summary("output_dir / summary_features.md")

# # Save interpretive notes (prepare as string beforehand)
# outputs.save_interpretive_notes(notes_text, "interpretive_notes.txt")

# Create visualization plots
visualizer.plot_feature_frequencies(feature_counts, "Global Feature Frequencies", output_dir / "feature_freq_global.png")

# Similarly for newspapers or parse-types, pass their counts to plotting functions




