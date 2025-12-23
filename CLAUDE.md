# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **linguistic register comparison system** that analyzes differences between canonical and reduced (headline) text registers from Indian English newspapers. The system performs multi-dimensional analysis using dependency parsing, constituency parsing, and feature extraction to identify systematic linguistic transformations.

## Core Architecture

### Modular Pipeline Design

The system follows a modular pipeline architecture located in `register_comparison/`:

1. **Schema Management** (`meta_data/schema.py`): Loads the linguistic feature ontology from `diff-ontology-ver-3.0.json` that defines 18 features with hierarchical value structures
2. **Data Loading** (`readers/readers.py`, `data/loaded_data.py`): Handles plain text, CoNLL-U dependency parses, and constituency parses for three newspapers
3. **Alignment** (`aligners/aligner.py`): Word-level alignment between canonical and headline sentence pairs
4. **Feature Extraction** (`extractors/extractor.py`): Detects linguistic transformation events from aligned pairs
5. **Comparison** (`comparators/schema_comparator.py`): Analyzes differences using the schema, includes Tree Edit Distance (TED) algorithms
6. **Aggregation** (`aggregators/aggregator.py`): Collects events across dimensions (global, per-newspaper, by-parse-type, cross-combinations)
7. **Statistical Analysis** (`stat_runners/stats.py`): Runs chi-square, Fisher's exact test, odds ratios
8. **Visualization** (`visualizers/visualizer.py`, `visualizers/enhanced_visualizer.py`): Creates comprehensive plots including transformation matrices, flow diagrams, network graphs
9. **Output Generation** (`outputs/output_creators.py`): Exports CSV, JSON, LaTeX, and Markdown reports

### Path Configuration

- **`config.py`**: Finds project root using `project.toml` marker file, handles WSL/Windows path translation
- **`paths_config.py`**: Defines data file mappings for three newspapers (Hindustan-Times, The-Hindu, Times-of-India)
  - Plain text files: `data/input/input-single-line-break/`
  - Dependency parses: `data/input/dependecy-parsed/` (note: typo in directory name)
  - Constituency parses: `data/input/constituency-parsed/`

### Feature Schema (`diff-ontology-ver-3.0.json`)

The ontology defines 18 linguistic features organized into categories:
- **Lexical**: Function word deletion/addition, content word substitution
- **Morphological**: Tense changes, number changes, person changes
- **Syntactic**: Word order changes, clause restructuring
- **Constituency**: Phrasal modifications, tree edit operations

Each feature has:
- `mnemonic_code`: Short identifier (e.g., "FW-DEL")
- `values`: Specific transformation types (e.g., "article deletion", "quantifier deletion")
- `value_mnemonics`: Mnemonics for each value
- `parse_types`: Required parse types ("dependency", "constituency", or both)

## Running the System

### Main Entry Point

```bash
python register_comparison/compare_registers.py
```

This runs the full pipeline for a single newspaper (currently hardcoded to "Times-of-India" on line 233).

### Modular Analysis Interface

```bash
# Basic analysis for specific newspapers
python register_comparison/modular_analysis.py --newspapers "Times-of-India" --analysis basic

# Comprehensive analysis for all newspapers
python register_comparison/modular_analysis.py --newspapers all --analysis comprehensive

# Feature-value analysis with enhanced visualizations
python register_comparison/modular_analysis.py --newspapers all --analysis feature-value --enhance-visuals

# Global cross-newspaper analysis only (requires prior newspaper analysis)
python register_comparison/modular_analysis.py --global-only --analysis feature-value
```

Analysis levels:
- `basic`: Feature counts and simple visualizations (~2-5 min per newspaper)
- `comprehensive`: Multi-dimensional analysis with statistical testing (~5-10 min)
- `feature-value`: Complete value transformation analysis (~10-15 min)

### Testing

```bash
# Test specific components
python test_ted_algorithms.py              # Tree Edit Distance algorithms
python test_improved_visualizations.py     # Visualization generation
python test_cross_entropy_integration.py   # Cross-entropy analysis

# Full pipeline verification
python verify_complete_pipeline.py
python final_integration_test.py
```

## Output Structure

Analysis outputs are written to `output/`:

```
output/
├── [Newspaper-Name]/              # Per-newspaper results
│   ├── feature_freq_global.csv
│   ├── events_global.csv
│   ├── comprehensive_analysis.json
│   ├── comprehensive_analysis.csv
│   ├── feature_value_analysis.json
│   ├── feature_value_analysis.csv
│   ├── bidirectional_cross_entropy_analysis.json
│   ├── visualizations (PNG files)
│   └── reports (LaTeX/Markdown)
└── GLOBAL_ANALYSIS/                # Cross-newspaper aggregation
    └── global_*.{json,csv}
```

## Key Implementation Details

### Multi-Dimensional Aggregation

The `Aggregator` class tracks events across multiple dimensions:
- **Global**: All events combined
- **By newspaper**: Separate counts per newspaper
- **By parse type**: Dependency vs. constituency
- **Cross-combinations**: Newspaper × parse type breakdowns

### Tree Edit Distance (TED) Analysis

Four TED algorithms are implemented (`register_comparison/ted_config.py`):
1. **APTED**: All-Paths Tree Edit Distance
2. **Zhang-Shasha**: Dynamic programming approach
3. **Simple**: Basic recursive algorithm
4. **Depth-Weighted**: Penalizes edits at different tree depths

Configured via `TEDConfig.default()` in the comparison pipeline.

### Statistical Testing

The `StatsRunner` performs:
- Chi-square test for feature distribution independence
- Fisher's exact test for small sample sizes
- Odds ratio calculation with confidence intervals
- Effect size measures

### Cross-Entropy Analysis

Bidirectional cross-entropy measures information asymmetry:
- **Canonical→Headlines**: Information loss in reduction
- **Headlines→Canonical**: Information gain in expansion
- **Asymmetry**: Directional difference in transformations

### Value Transformation Analysis

The system tracks not just feature occurrences but specific value-to-value transformations:
- Example: "article deletion" → "quantifier deletion" (within FW-DEL feature)
- Generates transformation matrices, flow diagrams, and network visualizations

## Important Notes

### Path Handling

This project runs in WSL2 Ubuntu 24.04 with paths mounted from Windows host:
- WSL path format: `/mnt/d/Dropbox/...`
- `config.py` detects WSL environment and uses native Linux paths
- All path operations use `pathlib.Path` for cross-platform compatibility

### Data Format Requirements

- **Plain text**: One sentence per line, UTF-8 encoded
- **CoNLL-U files**: Standard CoNLL-U format for dependency parses
- **Constituency files**: One bracketed tree per line (NLTK Tree format)
- **Parallel alignment**: Canonical and headline files must have matching line counts

### Common Module Import Pattern

Due to nested package structure, most modules use:
```python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import BASE_DIR
```

This ensures `config.py` and `paths_config.py` are accessible from subdirectories.

### Schema-Based Comparator

ALWAYS use `SchemaBasedComparator` (imported as `Comparator`):
```python
from register_comparison.comparators.schema_comparator import SchemaBasedComparator as Comparator
```

The old `comparators/comparator.py` is deprecated and doesn't properly detect schema features.

## Dependencies

Core libraries (see `requirements.txt`):
- `conllu>=4.0`: CoNLL-U parsing
- `nltk>=3.8`: Constituency tree operations
- `pandas>=1.5.0`: Data manipulation
- `scipy>=1.9.0`: Statistical tests
- `numpy>=1.21.0`: Numerical operations
- `matplotlib>=3.5.0`, `seaborn>=0.11.0`: Visualizations

Python version: 3.10.18

## Typical Development Workflow

When adding new features or fixing issues:

1. **Test with single newspaper first**: Modify `compare_registers.py` line 233 to test with one newspaper
2. **Verify schema changes**: If modifying `diff-ontology-ver-3.0.json`, test schema loading immediately
3. **Check output structure**: New analysis types should integrate with existing `Aggregator` methods
4. **Add visualizations incrementally**: Test visualization generation separately before integrating
5. **Update modular analysis**: Ensure new features work with `modular_analysis.py` interface
6. **Run integration tests**: Use `verify_complete_pipeline.py` before committing

## Historical Context

The `older-code/` directory contains previous iterations showing the evolution:
- Early single-file scripts for alignment and comparison
- Development of the modular architecture
- Addition of TED algorithms and enhanced visualizations
- Migration to schema-based feature detection

This historical code should not be used but provides context for architectural decisions.
