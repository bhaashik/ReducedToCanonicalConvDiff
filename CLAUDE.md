# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **linguistic register comparison system** that analyzes morphosyntactic differences between canonical (full sentence) and reduced (headline) text registers from Indian English newspapers. The system performs multi-dimensional analysis using dependency parsing, constituency parsing, and feature extraction to identify systematic linguistic transformations.

**Research Questions**:
1. What are the systematic morphosyntactic differences between registers?
2. How regular are transformations, and which direction is easier/more complex?
3. Are linguistic complexities of different registers systematically different?

**Scope**: This project focuses exclusively on **morphosyntactic** complexity and similarity (not semantic or pragmatic aspects). Future work may extend to phonological, semantic, and pragmatic levels.

## Three Research Tasks

### Task 1: Comparative Study
**Objective**: Quantitative analysis of morphosyntactic differences between registers.

**Methods**:
- Feature-value schema for difference classification (18 features, enriched to 20 morphological feature types in v4.0)
- Constituency and dependency parse comparison
- Event-level statistical analysis

**Output**: `output/comparative-study/` or `output/<newspaper>/events_global.csv`

### Task 2: Transformation Study
**Objective**: How many transformation rules capture how many difference events? Which direction (C→H or H→C) is easier and why?

**Methods**:
- Morphological rule extraction from difference events
- Progressive coverage analysis (adding rules incrementally)
- Rule effectiveness measurement
- Both constituency and dependency-based rules

**Output**: `output/transformation-study/`

### Task 3: Complexity & Similarity Study
**Objective**: Which transformation direction is more complex in information-theoretic terms?

**Methods**:
- Bidirectional MT-like transformation scenario
- Perplexity analysis (mono-register, cross-register, directional)
- Correlation analysis (complexity metrics vs. transformation performance)
- **EXTENDED**: Multi-level complexity analysis across:
  - **Lexical level**: Surface forms and lemmas (Type-Token Ratio, entropy)
  - **Morphological level**: POS tags and morphological features
  - **Syntactic level**: Dependency relations and constituency labels
  - **Structural level**: Tree metrics (depth, branching factor, dependency distance)

**Key Finding**: H→C (headline expansion to canonical) is 1.6-2.2x more complex than C→H (reduction)

**Output**:
- `output/complexity-similarity-study/` - Original bidirectional analysis
- `output/multilevel_complexity/` - Extended multi-level complexity analysis
- `output/multilevel_similarity/` - Extended multi-level similarity analysis

## Running the System

### Complete Pipeline (All Three Tasks)

```bash
# Run complete three-task pipeline
python run_complete_pipeline.py
```

This executes Task 1, Task 2, and Task 3 sequentially for all newspapers and generates a master report.

### Task-Specific Execution

```bash
# Task 1: Run comparative study for all newspapers
python run_task1_all_newspapers.py

# Task 1: Single newspaper (modify line 233 in compare_registers.py)
python register_comparison/compare_registers.py

# Task 2: Complete transformation study with CLI
python run_task2_transformation_study.py

# Task 2: Individual scripts
python progressive_coverage_with_morphology.py
python create_morphological_comparative_analysis.py
python create_comprehensive_morphological_visualizations.py
python extract_morphological_rules.py

# Task 2: CLI options
python run_task2_transformation_study.py --newspapers "Times-of-India" "The-Hindu"
python run_task2_transformation_study.py --skip-extraction
python run_task2_transformation_study.py --skip-visualization

# Task 3: Complete complexity & similarity study
python run_task3_complexity_similarity.py

# Task 3: Individual scripts
python bidirectional_transformation_with_traces.py
python bidirectional_transformation_system.py
python perplexity_register_analysis.py
python directional_perplexity_analysis.py
python correlation_analysis.py
python create_correlation_summary_viz.py

# Task 3 EXTENDED: Multi-level complexity analysis
# Analyzes complexity at lexical, morphological, syntactic, and structural levels
python run_multilevel_complexity_analysis.py

# Single newspaper complexity analysis
python multilevel_complexity_analyzer.py --newspaper "Times-of-India"

# Task 3 EXTENDED: Multi-level similarity analysis
# Comprehensive similarity/divergence metrics from information theory
python run_multilevel_similarity_analysis.py

# Single newspaper similarity analysis
python multilevel_similarity_analyzer.py --newspaper "Times-of-India"
```

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

### Verification and Testing

```bash
# Test specific components
python test_ted_algorithms.py              # Tree Edit Distance algorithms
python test_improved_visualizations.py     # Visualization generation
python test_cross_entropy_integration.py   # Cross-entropy analysis
python test_morphological_analysis.py      # Morphological analysis
python test_systematicity_analysis.py      # Systematicity analysis
python test_transformation_engine.py       # Transformation engine

# Full pipeline verification
python verify_complete_pipeline.py
python final_integration_test.py
python quick_verification.py
```

## Core Architecture

### Modular Pipeline Design

The system follows a modular pipeline architecture located in `register_comparison/`:

1. **Schema Management** (`meta_data/schema.py`): Loads the linguistic feature ontology from `diff-ontology-ver-3.0.json` (or v4.0) that defines 18 features with hierarchical value structures
2. **Data Loading** (`readers/readers.py`, `data/loaded_data.py`): Handles plain text, CoNLL-U dependency parses, and constituency parses for three newspapers
3. **Alignment** (`aligners/aligner.py`): Word-level alignment between canonical and headline sentence pairs
4. **Feature Extraction** (`extractors/extractor.py`): Detects linguistic transformation events from aligned pairs
5. **Comparison** (`comparators/schema_comparator.py`): Analyzes differences using the schema, includes Tree Edit Distance (TED) algorithms
6. **Aggregation** (`aggregators/aggregator.py`): Collects events across dimensions (global, per-newspaper, by-parse-type, cross-combinations)
7. **Statistical Analysis** (`stat_runners/stats.py`): Runs chi-square, Fisher's exact test, odds ratios
8. **Visualization** (`visualizers/visualizer.py`, `visualizers/enhanced_visualizer.py`): Creates comprehensive plots including transformation matrices, flow diagrams, network graphs
9. **Output Generation** (`outputs/output_creators.py`): Exports CSV, JSON, LaTeX, and Markdown reports

### Transformation Generation System

Located in `register_comparison/generation/`:

- **Rule Extraction** (`rule_extractor.py`): Extracts transformation rules from difference events
- **Morphological Analysis** (`morphological_analyzer.py`, `morphological_rules.py`): Analyzes morphological patterns
- **Transformation Engine** (`transformation_engine.py`, `transformation_engine_with_morphology.py`): Applies rules to generate transformed text
- **Systematicity Analysis** (`systematicity_analyzer.py`): Measures transformation regularity
- **Rule Visualization** (`rule_visualizer.py`): Visualizes rule patterns and coverage
- **Evaluation** (`evaluator.py`): Evaluates transformation quality

### Path Configuration

- **`config.py`**: Finds project root using `project.toml` marker file, handles WSL/Windows path translation
- **`paths_config.py`**: Defines data file mappings for three newspapers (Hindustan-Times, The-Hindu, Times-of-India)
  - Plain text files: `data/input/input-single-line-break/`
  - Dependency parses: `data/input/dependecy-parsed/` (note: typo in directory name)
  - Constituency parses: `data/input/constituency-parsed/`

### Feature Schema

**Current Version**: v3.0 (`diff-ontology-ver-3.0.json`)
**Future Version**: v4.0 (planned, see `SCHEMA_CHANGELOG_v4.0.md`)

The ontology defines 18 linguistic features organized into categories:
- **Lexical**: Function word deletion/addition, content word substitution
- **Morphological**: Tense changes, number changes, person changes (v4.0 enriches to 20 feature types)
- **Syntactic**: Word order changes, clause restructuring
- **Constituency**: Phrasal modifications, tree edit operations

Each feature has:
- `mnemonic_code`: Short identifier (e.g., "FW-DEL")
- `values`: Specific transformation types (e.g., "article deletion", "quantifier deletion")
- `value_mnemonics`: Mnemonics for each value
- `parse_types`: Required parse types ("dependency", "constituency", or both)

**Version 4.0 Enhancements** (planned):
- Expands morphological feature changes from 7 to 20 types
- Adds: person, gender, definiteness, pronoun type, possessive, number type, number form, polarity, reflexive, verbform, abbreviation, external pos, foreign
- Provides complete coverage of Universal Dependencies morphological features

## Output Structure

Analysis outputs are written to `output/`:

```
output/
├── comparative-study/           # Task 1: Difference analysis
│   ├── events/                  # Event-level data per newspaper
│   ├── statistics/              # Statistical summaries
│   └── visualizations/          # Comparative visualizations
│
├── transformation-study/        # Task 2: Rule coverage
│   ├── morphological-rules/     # Morphological rule patterns
│   ├── coverage-analysis/       # Progressive coverage
│   ├── visualizations/          # Transformation visualizations
│   └── TASK2_SUMMARY_REPORT.md  # Summary report
│
├── complexity-similarity-study/ # Task 3: Bidirectional analysis
│   ├── bidirectional-transformation/  # Transformed sentences
│   ├── transformation-traces/         # Rule application traces
│   ├── mt-evaluation/                 # MT metric scores (BLEU, ROUGE, etc.)
│   ├── perplexity-analysis/           # Complexity measures
│   └── correlation-analysis/          # Statistical validation
│
├── multilevel_complexity/       # Task 3 EXTENDED: Multi-level complexity
│   ├── [Newspaper-Name]/        # Per-newspaper detailed analysis
│   │   ├── multilevel_complexity_analysis.json
│   │   ├── multilevel_complexity_summary.csv
│   │   └── combined_complexity_scores.csv
│   │
│   └── GLOBAL_ANALYSIS/         # Cross-newspaper comparison
│       ├── aggregated_complexity_metrics.csv
│       ├── complexity_ratios.csv
│       ├── entropy_comparison.png
│       ├── ttr_comparison.png
│       ├── structural_comparison.png
│       ├── complexity_heatmaps.png
│       ├── complexity_ratios.png
│       └── MULTILEVEL_ANALYSIS_REPORT.md
│
├── multilevel_similarity/       # Task 3 EXTENDED: Multi-level similarity
│   ├── [Newspaper-Name]/        # Per-newspaper detailed analysis
│   │   ├── multilevel_similarity_analysis.json
│   │   ├── multilevel_similarity_summary.csv
│   │   └── combined_similarity_scores.csv
│   │
│   └── GLOBAL_ANALYSIS/         # Cross-newspaper comparison
│       ├── aggregated_similarity_metrics.csv
│       ├── jaccard_similarity_comparison.png
│       ├── cross_entropy_comparison.png
│       ├── kl_divergence_comparison.png
│       ├── js_similarity_comparison.png
│       ├── similarity_heatmaps.png
│       ├── directional_asymmetry.png
│       ├── correlation_similarity.png
│       └── MULTILEVEL_SIMILARITY_REPORT.md
│
└── [Newspaper-Name]/            # Per-newspaper results (legacy structure)
    ├── feature_freq_global.csv
    ├── events_global.csv
    ├── comprehensive_analysis.json
    ├── comprehensive_analysis.csv
    ├── feature_value_analysis.json
    ├── feature_value_analysis.csv
    ├── bidirectional_cross_entropy_analysis.json
    └── visualizations/
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

### Perplexity & Complexity Metrics

Three types of perplexity measurements:
- **Mono-register**: How predictable is each register individually?
- **Cross-register**: How well does one register predict the other?
- **Directional**: Which transformation direction has higher complexity?

Correlation with MT metrics (BLEU, ROUGE) validates information-theoretic predictions (r=-0.92, p<0.01).

### Multi-Level Complexity Analysis (Task 3 Extended)

Comprehensive analysis at multiple linguistic levels:

**Lexical Level**:
- Surface form diversity (Type-Token Ratio, entropy, perplexity)
- Lemma-based analysis
- Hapax legomena ratio
- Cross-register lexical divergence (KL, JS divergence)

**Morphological Level**:
- POS tag distribution and entropy
- Morphological feature diversity (20 UD features from v4.0 schema)
- Per-feature-type complexity analysis
- Feature-specific divergence measures

**Syntactic Level**:
- Dependency relation distribution
- Constituency label patterns
- Syntactic construction diversity

**Structural Level**:
- Tree depth (constituency and dependency)
- Average branching factor
- Dependency distance
- Sentence length distribution

**Combined Metrics**:
- Aggregate complexity scores across all levels
- Canonical/Headline complexity ratios
- Level-specific register differences

### Multi-Level Similarity Analysis (Task 3 Extended)

Comprehensive similarity/divergence metrics from information theory (based on SIMILARITY-METRICS.md):

**Entropy-Based Measures**:
- **Cross-Entropy** (both directions): H(P,Q) and H(Q,P)
  - Expected code length using one distribution to encode another
  - Decomposition: H(P,Q) = H(P) + D_KL(P||Q)
- **Relative Entropy / KL Divergence** (both directions): D_KL(P||Q) and D_KL(Q||P)
  - Information lost when approximating one distribution with another
  - Asymmetric divergence measure
- **Symmetrized KL**: D_sym(P,Q) = D_KL(P||Q) + D_KL(Q||P)
- **Jensen-Shannon Divergence**: Symmetric, bounded [0,1]
  - Square root forms a metric (triangle inequality holds)
- **Normalized variants**: Per-token, per-character, vocabulary-normalized

**Set-Based Similarity**:
- **Jaccard Similarity**: Set overlap measure
- **Dice Coefficient**: Harmonic mean-based similarity
- **Overlap Coefficient**: Minimum-based overlap

**Statistical Measures**:
- **Bhattacharyya Coefficient**: Distribution overlap via geometric mean
- **Hellinger Distance**: Bounded metric [0,1]
- **Pearson Correlation**: Linear frequency correlation
- **Spearman Correlation**: Rank-order correlation

**Perplexity Measures**:
- Self-perplexity (per register)
- Cross-perplexity (both directions)
- Normalized perplexity (by vocabulary size)

**Analyzed at All Levels**:
- Lexical: Surface forms, lemmas, sentence-level edit distance
- Morphological: POS tags, morphological features (per-feature-type analysis)
- Syntactic: Dependency relations, constituency labels, dependency bigrams
- Structural: Tree correlation, depth/size/distance similarity

## Important Notes

### Path Handling

This project runs in WSL2 Ubuntu 24.04 with paths mounted from Windows host:
- WSL path format: `/mnt/d/Dropbox/...`
- `config.py` detects WSL environment and uses native Linux paths
- All path operations use `pathlib.Path` for cross-platform compatibility
- **No Windows UNC path conversion** - Python inside WSL uses Linux paths natively

### Data Format Requirements

- **Plain text**: One sentence per line, UTF-8 encoded
- **CoNLL-U files**: Standard CoNLL-U format for dependency parses (from Stanza)
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

### Newspaper Data

Three newspapers analyzed:
- **Times-of-India** (default in `compare_registers.py` line 233)
- **Hindustan-Times**
- **The-Hindu**

Each has parallel canonical and headline text with corresponding parses.

## Dependencies

Core libraries (see `requirements.txt`):
- `conllu>=4.0`: CoNLL-U parsing
- `nltk>=3.8`: Constituency tree operations
- `pandas>=1.5.0`: Data manipulation
- `scipy>=1.9.0`: Statistical tests
- `numpy>=1.21.0`: Numerical operations
- `matplotlib>=3.5.0`, `seaborn>=0.11.0`: Visualizations
- `spacy>=3.0.0`: NLP processing
- `rouge-score>=0.1.2`: MT evaluation metrics

Python version: 3.10.18

## Typical Development Workflow

When adding new features or fixing issues:

1. **Test with single newspaper first**: Modify `compare_registers.py` line 233 to test with one newspaper
2. **Verify schema changes**: If modifying schema, test schema loading immediately
3. **Check output structure**: New analysis types should integrate with existing `Aggregator` methods
4. **Add visualizations incrementally**: Test visualization generation separately before integrating
5. **Update modular analysis**: Ensure new features work with `modular_analysis.py` interface
6. **Run integration tests**: Use `verify_complete_pipeline.py` before committing
7. **Update documentation**: Modify relevant markdown files in the root directory

## Workflow for Three-Task Analysis

1. **Run Task 1** (or verify existing results in `output/<newspaper>/events_global.csv`)
2. **Manual verification**: User reviews events_global.csv to ensure quality
3. **Run Task 2**: Uses events from Task 1 to extract and test transformation rules
4. **Run Task 3**: Uses events from Task 1 and rules from Task 2 for complexity analysis
5. **Aggregate results**: Cross-newspaper analysis combining all three tasks
6. **Generate master report**: `output/MASTER_ANALYSIS_REPORT.md`

## Historical Context

The `older-code/` directory contains previous iterations showing the evolution:
- Early single-file scripts for alignment and comparison
- Development of the modular architecture
- Addition of TED algorithms and enhanced visualizations
- Migration to schema-based feature detection

This historical code should not be used but provides context for architectural decisions.

## Documentation Files

Extensive documentation is available in markdown files:
- `BIDIRECTIONAL_CROSS_ENTROPY_SUMMARY.md`: Cross-entropy analysis results
- `BIDIRECTIONAL_TRANSFORMATION_EVALUATION.md`: Transformation system evaluation
- `COMPLETE_SYSTEM_DOCUMENTATION.md`: Full system documentation
- `COMPREHENSIVE_MORPHOLOGICAL_VISUALIZATIONS.md`: Morphological visualization guide
- `CORRELATION_EXECUTIVE_SUMMARY.md`: Correlation analysis summary
- `DIRECTIONAL_COMPLEXITY_ANALYSIS.md`: Directional complexity findings
- `FINAL_RESEARCH_FINDINGS.md`: Overall research conclusions
- `GENERATION_ARCHITECTURE.md`: Transformation generation system architecture
- `MODULAR_ANALYSIS_GUIDE.md`: Guide to modular analysis interface
- `MORPHOLOGICAL_FINDINGS.md`: Morphological analysis results
- `PERPLEXITY_REGISTER_COMPLEXITY_ANALYSIS.md`: Perplexity analysis results
- `SCHEMA_CHANGELOG_v4.0.md`: Schema version 4.0 changes
- `TED_ALGORITHMS_DOCUMENTATION.md`: Tree Edit Distance algorithms
- Various publication-ready summaries and LaTeX tables

## Related Work

The `related-work/` directory contains analyses of relevant papers and theoretical background for contextualizing this research within the broader field of register analysis, text transformation, and linguistic complexity.

## Future Extensions

This project currently focuses on morphosyntactic analysis. Future work may extend to:
- **Phonological** complexity (prosody, stress patterns)
- **Semantic** complexity (ambiguity, semantic density)
- **Pragmatic** complexity (honorifics, Gricean maxims)
- Cross-linguistic comparison (other languages/dialects)
- Other register pairs (formal-informal, technical-popular, etc.)
