# Register Comparison Pipeline

A linguistic register comparison system that quantitatively analyses morphosyntactic differences between two text registers using feature-value schemas, transformation rules, and information-theoretic complexity metrics. The current corpus is Indian English newspaper text (canonical sentences vs. reduced headlines) from three sources: **Times-of-India**, **Hindustan-Times**, and **The-Hindu**.

---

## Research Tasks

| # | Name | What it does |
|---|------|--------------|
| **Task 1** | Comparative Study | Quantifies morphosyntactic differences using a feature-value ontology (schema v5.0). Produces event distributions, chi-square statistics, odds ratios, and visualizations. |
| **Task 2** | Transformation Study | Extracts canonical→reduced morphological rules, measures coverage, and implements bidirectional sentence transformation (canonical↔headline) with multi-hypothesis ranking. |
| **Task 3** | Complexity & Similarity Study | Multi-level information-theoretic analysis (character → token → morphological → dependency → constituency). Computes MATTR, MTLD, MDD, KL divergence, Wasserstein, chrF, NCD, and accumulated-level curves. |

---

## Prerequisites

- **OS**: Linux, macOS, or WSL2 (Ubuntu 24.04 tested)
- **Python**: 3.13 (managed via conda)
- **Conda**: Miniconda or Anaconda

---

## Installation

```bash
# 1. Clone the repository
git clone <repo-url> ReducedToCanonicalConvDiff
cd ReducedToCanonicalConvDiff

# 2. Create the conda environment
conda env create -f environment.yml

# 3. Activate
conda activate Reduced2Canonical

# 4. Download required NLTK data
python -c "import nltk; nltk.download(['punkt', 'punkt_tab', 'averaged_perceptron_tagger', 'averaged_perceptron_tagger_eng'])"
```

Optional dependencies for Task 3 MT-style evaluation:

```bash
pip install spacy rouge-score sacrebleu
python -m spacy download en_core_web_sm
```

---

## Data Requirements

The pipeline expects three parallel file types per register pair, placed under `data/input/`:

```
data/input/
├── input-single-line-break/      # Plain text, one sentence per line, UTF-8
│   ├── {Newspaper}-canonical.txt
│   └── {Newspaper}-headlines.txt
├── dependecy-parsed/             # CoNLL-U from Stanza (note: directory name typo is intentional)
│   ├── {Newspaper}-canonical-stanza-parsed-deps.conllu
│   └── {Newspaper}-headlines-stanza-parsed-deps.conllu
└── constituency-parsed/          # NLTK bracketed trees, one per line
    ├── {Newspaper}-canonical-stanza-parsed-constituency.txt
    └── {Newspaper}-headlines-stanza-parsed-constituency.txt
```

**Critical**: canonical and headline files must have **identical line counts** (parallel sentence alignment). See `TUTORIAL.md` for how to generate parses from raw text.

---

## Quick-start (5 commands)

```bash
conda activate Reduced2Canonical

# Run Task 1 for all newspapers
python run_task1_all_newspapers.py

# Run Task 2 (transformation rules + bidirectional generation)
python run_task2_transformation_study.py

# Run Task 3 (comprehensive multi-level complexity and similarity)
python comprehensive_task3_runner.py

# Generate markdown / HTML summary tables and figures
python create_morph_deprel_tables_figures.py
```

Outputs land in `output/` (git-ignored).

---

## Task CLI Reference

### Pipeline runner (orchestrates all tasks)

```bash
python run_complete_pipeline.py all          # Full pipeline
python run_complete_pipeline.py task1        # Task 1 only
python run_complete_pipeline.py task2        # Task 2 only
python run_complete_pipeline.py task3        # Task 3 only
python run_complete_pipeline.py setup        # Create output directory layout
python run_complete_pipeline.py organize     # Reorganize outputs into task folders
python run_complete_pipeline.py --dry-run    # Log actions without executing
```

### Task 1 — Comparative Study

```bash
# Single newspaper (fast iteration — edit line 233 of compare_registers.py first)
python register_comparison/compare_registers.py

# All newspapers
python run_task1_all_newspapers.py

# Modular interface
python register_comparison/modular_analysis.py --newspapers "Times-of-India" --analysis basic
python register_comparison/modular_analysis.py --newspapers all --analysis comprehensive
python register_comparison/modular_analysis.py --newspapers all --analysis feature-value --enhance-visuals
```

### Task 2 — Transformation Study

```bash
# Rule extraction + coverage
python run_task2_transformation_study.py
python run_task2_transformation_study.py --newspapers "Times-of-India" "The-Hindu"

# Complete rule analysis
python run_complete_rule_analysis.py

# Bidirectional transformation (canonical ↔ headline)
python run_bidirectional_transformation.py
```

### Task 3 — Complexity & Similarity Study

```bash
# Original Task 3 runner
python run_task3_complexity_similarity.py

# Multi-level extended runners
python run_multilevel_complexity_analysis.py
python run_multilevel_similarity_analysis.py

# Comprehensive runner (all levels + transformation-based + accumulated curves)
python comprehensive_task3_runner.py
```

### Utilities

```bash
# Generate LaTeX/Markdown tables and figures
python create_morph_deprel_tables_figures.py

# Verification scripts (no pytest — standalone print-based)
python quick_verification.py
python verify_complete_pipeline.py
python test_ted_algorithms.py
python test_morphological_analysis.py
python test_transformation_engine.py
python test_cross_entropy_integration.py
```

---

## Output Layout

```
output/
├── comparative-study/          # Task 1
│   ├── {Newspaper}/            # Per-newspaper tables, figures, reports
│   └── global/                 # Aggregated across all newspapers
├── transformation-study/       # Task 2
│   ├── bidirectional-transformation/
│   │   ├── generated/          # c2r_results_*.csv, r2c_results_*.csv
│   │   ├── evaluation/         # Jaccard, BLEU, WER summaries
│   │   ├── tables/             # rule_coverage_analysis.csv, hypothesis_selection_stats.csv
│   │   ├── figures/            # Visualizations
│   │   └── rules/              # Rule JSON exports
│   └── {Newspaper}/            # Per-newspaper rule tables and figures
├── complexity-similarity-study/  # Task 3 comprehensive
│   ├── per-newspaper/
│   │   └── {Newspaper}/
│   │       ├── complexity/     # Per-level complexity CSVs
│   │       ├── similarity/     # Per-level similarity CSVs (C2H + H2C + symmetrized)
│   │       ├── transformation/ # Transformation-based complexity/similarity
│   │       └── accumulated/    # Accumulated curves, information_gain.csv
│   ├── global/                 # Cross-newspaper aggregated CSVs
│   ├── figures/                # 8 publication figures (PNGs)
│   └── tables/                 # comprehensive_metrics_all_levels.csv
├── multilevel_complexity/      # Task 3 extended complexity (per newspaper)
├── multilevel_similarity/      # Task 3 extended similarity (per newspaper)
└── {Newspaper}/                # Legacy per-newspaper results
```

---

## LaTeX Directory Structure

Six subdirectories under `LaTeX/` (git-ignored):

| Directory | Type | Notes |
|-----------|------|-------|
| `Canonical-Reduced-Register-Comparison-Part-1-ACL-ARR/` | Task 1 full paper + source | Compiled PDF; `review` mode (anonymous) |
| `Canonical_Reduced_Register_Complexity_Part_1_ACL_ARR_short_submitted/` | Task 1 short | Submitted; tabularray tables |
| `Canonical_Reduced_Register_Complexity_Part_2_ACL_ARR_short_not_submitted/` | Task 2 short | Not submitted |
| `Canonical-Reduced-Register-Transformation-Part-2-ACL-ARR/` | Task 2 deposit | Figures and tables only (no main .tex) |
| `Canonical-Reduced-Register-Complexity-Part-3-ACL-ARR/` | Task 3 deposit | Figures and tables only (no main .tex) |
| `Canonical_Reduced_Register_Complexity_Part_3_ACL_ARR_short_submiited/` | Task 3 short | Submitted (note typo in dirname) |

**Rule**: directories with underscores contain paper source (main .tex); directories with hyphens are figure/table deposit directories.

---

## Core Architecture

The pipeline lives in `register_comparison/` and follows a modular data flow:

```
Schema (v5.0 ontology)
  → Data Loading (plain text, CoNLL-U, constituency parses)
    → Alignment (word-level)
      → Event Extraction (feature detectors)
        → Comparison (SchemaBasedComparator)
          → Aggregation (global, per-newspaper, per-parse-type)
            → Statistics (chi-square, Fisher's exact, odds ratios)
              → Visualization + Output (CSV, JSON, LaTeX, Markdown)
```

Key modules:
- `register_comparison/comparators/schema_comparator.py` — always use this (not the deprecated `comparator.py`)
- `register_comparison/generation/` — transformation rule extraction and bidirectional engine
- `multilevel_complexity_analyzer.py` / `multilevel_similarity_analyzer.py` — extended v2 analyzers
- `transformation_based_analyzer.py` — complexity/similarity through rule lens
- `accumulated_level_analyzer.py` — accumulated levels L1–L6 with information gain

---

## Developer Notes

See `CLAUDE.md` for:
- Terminology disambiguation (schema feature vs. morphological feature vs. linguistic feature)
- Critical conventions (always use `SchemaBasedComparator`, module import pattern)
- Data file naming inconsistencies (`paths_config.py` is the single source of truth)
- Development workflow and task dependency order

See `TUTORIAL.md` for a complete step-by-step guide to running the pipeline on new data, including how to generate parses and adapt `paths_config.py` for different register pairs.
