# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A **linguistic register comparison system** that analyzes morphosyntactic differences between canonical (full sentence) and reduced (headline) text registers from Indian English newspapers. Three newspapers: Times-of-India, Hindustan-Times, The-Hindu.

**Three research tasks**:
1. **Comparative Study** (Task 1): Quantitative analysis of morphosyntactic differences using a feature-value schema
2. **Transformation Study** (Task 2): Extraction and coverage analysis of morphological transformation rules
3. **Complexity & Similarity Study** (Task 3): Information-theoretic complexity analysis across lexical, morphological, syntactic, and structural levels

## Running the System

```bash
# Complete pipeline
python run_complete_pipeline.py all

# Individual tasks
python run_complete_pipeline.py task1
python run_complete_pipeline.py task2
python run_complete_pipeline.py task3

# Pipeline management
python run_complete_pipeline.py setup          # Set up output layout
python run_complete_pipeline.py organize       # Reorganize outputs into task folders
python run_complete_pipeline.py --dry-run      # Log actions without executing

# Task 1: Single newspaper (fastest iteration)
# Change current_news_paper_name at line 233 of register_comparison/compare_registers.py
python register_comparison/compare_registers.py

# Task 1: All newspapers
python run_task1_all_newspapers.py

# Task 2
python run_task2_transformation_study.py
python run_task2_transformation_study.py --newspapers "Times-of-India" "The-Hindu"

# Task 3
python run_task3_complexity_similarity.py

# Task 2 extended: Complete rule analysis
python run_complete_rule_analysis.py

# Task 3 extended: Multi-level complexity and similarity
python run_multilevel_complexity_analysis.py
python run_multilevel_similarity_analysis.py

# Task 3 comprehensive: All levels + transformation-based + accumulated curves
python comprehensive_task3_runner.py

# Bidirectional transformation (canonical ↔ reduced)
python run_bidirectional_transformation.py

# Generate tables and figures (markdown/HTML per task)
python create_morph_deprel_tables_figures.py

# Modular analysis interface
python register_comparison/modular_analysis.py --newspapers "Times-of-India" --analysis basic
python register_comparison/modular_analysis.py --newspapers all --analysis comprehensive
python register_comparison/modular_analysis.py --newspapers all --analysis feature-value --enhance-visuals
```

### Verification Scripts

There is no formal test framework (no pytest/unittest). All `test_*.py` files are standalone verification scripts using print statements and basic assertions:

```bash
python test_ted_algorithms.py
python test_morphological_analysis.py
python test_transformation_engine.py
python test_cross_entropy_integration.py
python verify_complete_pipeline.py
python quick_verification.py
```

## Core Architecture

### Pipeline (register_comparison/)

Modular pipeline with this data flow:

1. **Schema** (`meta_data/schema.py`) → loads feature ontology from `data/diff-ontology-ver-5.0.json`
2. **Data Loading** (`readers/readers.py`, `data/loaded_data.py`) → plain text, CoNLL-U, constituency parses
3. **Alignment** (`aligners/aligner.py`) → word-level alignment between canonical and headline pairs
4. **Extraction** (`extractors/extractor.py`) → detects linguistic transformation events
5. **Comparison** (`comparators/schema_comparator.py`) → schema-based difference analysis + TED algorithms
6. **Aggregation** (`aggregators/aggregator.py`) → multi-dimensional event collection (global, per-newspaper, by-parse-type, cross-combinations)
7. **Statistics** (`stat_runners/stats.py`) → chi-square, Fisher's exact, odds ratios
8. **Visualization** (`visualizers/visualizer.py`, `visualizers/enhanced_visualizer.py`) → plots, matrices, flow diagrams
9. **Output** (`outputs/output_creators.py`) → CSV, JSON, LaTeX, Markdown

### Key Architectural Components

- **`ted_config.py`**: Configures four Tree Edit Distance algorithms (simple, zhang_shasha, klein, rted). Use `TEDConfig.default()` for all four, `TEDConfig.simple_only()` for fast iteration, or `TEDConfig.performance_optimized()` for large trees.
- **`comparators/v5_feature_detector.py`**: Detects schema v5.0 features (punctuation changes, headline typology, structural complexity). Used internally by `SchemaBasedComparator`.
- **`utils/context_extractor.py`** and **`utils/event_enricher.py`**: Provide windowed context extraction (±2-7 tokens) and metadata enrichment for events.

### Transformation Generation (register_comparison/generation/)

Rule extraction, morphological analysis, transformation engine, systematicity analysis, and evaluation for Task 2. Key modules: `rule_extractor.py`, `morphological_analyzer.py`, `transformation_engine.py`, `systematicity_analyzer.py`, `evaluator.py`. Newer additions for bidirectional transformation: `bidirectional_rules.py`, `sentence_transformer.py`, `constraint_resolver.py`, `surface_realizer.py`.

### Key Configuration

- **`config.py`**: Finds project root by walking up from script location looking for `project.toml` (a marker file, not a real TOML config). Detects WSL and uses native Linux paths. Prints `BASE_DIR` on import (expected console noise).
- **`paths_config.py`**: Maps newspaper names to data files. Schema path: `data/diff-ontology-ver-5.0.json`.

## Terminology

The term **"feature"** is overloaded in this project with three distinct meanings:

1. **Schema/Ontology Feature** (broadest): A type of difference defined in `diff-ontology-ver-5.0.json`. Each entry is a "feature" that represents a category of observed differences between canonical and reduced registers (e.g., FW-DEL, FEAT-CHG, DEP-REL-CHG, TED-SIMPLE, LENGTH-CHG). These include both transformational differences and aggregate measures. Each schema feature has a mnemonic code, values, and applicable parse types. An "event" is a single observed instance of a schema feature.

2. **Morphological Feature** (subset of #1): A linguistic property of a word's morphology as annotated in the CoNLL-U FEATS column (e.g., Tense=Past, Number=Sing, VerbForm=Fin). These appear as values within the `FEAT-CHG` schema feature. A morphological feature *change* (FEAT-CHG event) records when a morphological feature differs between the canonical and reduced register for an aligned token.

3. **Linguistic Feature** (mono-register): A property of a single sentence in one register, independent of any comparison. E.g., "this canonical sentence has Tense=Past on its main verb." Used when computing entropy or distributional statistics within a single register.

Similarly, **"feature-value pair"** has two senses:
- **Schema level**: A (feature_id, value) pair from the ontology, e.g., (FW-DEL, ART-DEL) meaning "function word deletion of an article."
- **Morphological level**: A (feature_name, feature_value) pair from CoNLL-U, e.g., (Tense, Past).

## Critical Conventions

### Always Use SchemaBasedComparator

```python
from register_comparison.comparators.schema_comparator import SchemaBasedComparator as Comparator
```

The old `comparators/comparator.py` is deprecated and doesn't properly detect schema features.

### Module Import Pattern

Due to nested package structure, most modules use:
```python
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import BASE_DIR
```

### Feature Schema

**Current version**: v5.0 (`data/diff-ontology-ver-5.0.json`). Historical versions (v3.0, v4.0, v4.1) also exist in `data/`.

The ontology defines linguistic features with:
- `mnemonic_code`: Short identifier (e.g., "FW-DEL")
- `values`: Specific transformation types
- `value_mnemonics`: Mnemonics per value
- `parse_types`: "dependency", "constituency", or both

### Data Files

Located under `data/input/`:
- Plain text: `input-single-line-break/` — one sentence per line, UTF-8
- Dependency parses: `dependecy-parsed/` (note: typo in directory name is intentional — do not rename) — CoNLL-U format from Stanza
- Constituency parses: `constituency-parsed/` — one bracketed tree per line (NLTK Tree format)

Canonical and headline files must have **matching line counts** (parallel alignment).

**Naming inconsistency**: The-Hindu and Times-of-India plain text files use "corrected-" prefix (e.g., `The-Hindu-corrected-canonical.txt`), but Hindustan-Times does not, and no parsed files use it. All file paths are defined in `paths_config.py` — always reference that file rather than constructing paths manually.

**Parser bias caveat**: the current parses were produced by an off-the-shelf Stanza model trained on canonical (well-formed) text. This model may perform worse on reduced/headline text, which means some observed register differences may partly be parsing artefacts rather than true linguistic differences. For controlled experiments, finetune or retrain Stanza on matched UD treebank data (same quantity from each register) before re-parsing. See `TUTORIAL.md` §12 for the full procedure.

## Output Structure

Outputs go to `output/` (git-ignored), organized by task:
- `task-1-comparative-study/` — per-newspaper + global tables, visualizations, reports (Task 1)
- `task-2-transformation-study/` — coverage analysis, morphological rules, visualizations (Task 2)
- `task-3-complexity-similarity-study/` — bidirectional transformations, perplexity, correlations (Task 3)
- `perhaps-useful/multilevel-complexity-legacy/` — multi-level complexity from extended runner (legacy)
- `perhaps-useful/multilevel-similarity-legacy/` — multi-level similarity from extended runner (legacy)
- `common/` — placeholder for shared cross-task resources

## Environment

- **WSL2 Ubuntu 24.04** with data mounted from Windows host
- **Python 3.13.11** (conda env `Reduced2Canonical`)
- All paths use Linux format (`/mnt/d/...`)
- `config.py` detects WSL and uses native Linux paths (no UNC conversion)

### Dependencies

```bash
pip install -r requirements.txt

# For Task 3 transformation evaluation (optional)
pip install spacy rouge-score sacrebleu
python -m spacy download en_core_web_sm
```

Core: `conllu`, `nltk`, `pandas`, `scipy`, `numpy`, `matplotlib`, `seaborn`, `typing_extensions`.

## Git-Ignored Directories

`older-code/`, `ver-5.0-output/`, `claude-conversation-history/`, `LaTeX/`, `output/`, `Samapika-Thesis/`, `test_output/`, `test_*/`.

- `older-code/`: Historical development iterations (do not use, but provides architectural context)
- `LaTeX/`: Publication LaTeX sources. Six subdirectories:
  - `Canonical-Reduced-Register-Comparison-Part-1-ACL-ARR/` — Task 1 full paper source + compiled PDF; `review` mode (anonymous)
  - `Canonical_Reduced_Register_Complexity_Part_1_ACL_ARR_short_submitted/` — Task 1 short paper source; submitted; tabularray tables
  - `Canonical_Reduced_Register_Complexity_Part_2_ACL_ARR_short_not_submitted/` — Task 2 short paper source; NOT submitted
  - `Canonical-Reduced-Register-Transformation-Part-2-ACL-ARR/` — Task 2 figure/table deposit directory (no main .tex)
  - `Canonical-Reduced-Register-Complexity-Part-3-ACL-ARR/` — Task 3 figure/table deposit directory (no main .tex)
  - `Canonical_Reduced_Register_Complexity_Part_3_ACL_ARR_short_submiited/` — Task 3 short paper source; submitted (note typo in dirname)
  - **Rule**: underscore dirs = paper source dirs (have main .tex); hyphen dirs = figure/table deposit dirs (no main .tex)
- `TABLES-FIGURES-ALL-MD/`: Comprehensive markdown/HTML reports with inline tables and figures per task

## Development Workflow

1. **Test with single newspaper first**: Change `current_news_paper_name` at line 233 of `register_comparison/compare_registers.py`
2. **Verify schema changes**: Test schema loading immediately after modification
3. **Check output structure**: New analysis types should integrate with existing `Aggregator` methods
4. **Run verification**: `python quick_verification.py` then `python verify_complete_pipeline.py`
5. **Task dependency order**: Task 1 → Task 2 (uses Task 1 events) → Task 3 (uses events + rules)
