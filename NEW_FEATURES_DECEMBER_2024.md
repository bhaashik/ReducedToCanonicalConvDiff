# New Features - December 2024

## Overview

This document summarizes the new features and improvements added to the register comparison system on December 25, 2024.

## Task-2: CLI Runner Implementation

### New File: `run_task2_transformation_study.py`

A comprehensive CLI runner for Task 2 (Transformation Study) that:

**Features**:
- Runs complete transformation study pipeline
- Verifies Task 1 outputs before starting
- Orchestrates rule extraction, coverage analysis, and visualizations
- Organizes outputs into structured directories
- Generates summary reports

**Usage**:
```bash
# Run complete Task 2 for all newspapers
python run_task2_transformation_study.py

# Run for specific newspapers only
python run_task2_transformation_study.py --newspapers "Times-of-India" "The-Hindu"

# Skip rule extraction (if already done)
python run_task2_transformation_study.py --skip-extraction

# Skip visualization generation
python run_task2_transformation_study.py --skip-visualization
```

**Pipeline Steps**:
1. Verification of Task 1 outputs (events_global.csv)
2. Rule extraction from difference events
3. Progressive coverage analysis with morphological integration
4. Morphological comparative analysis
5. Comprehensive visualization generation
6. Output organization into transformation-study directory
7. Summary report generation

**Outputs**:
- `output/transformation-study/coverage-analysis/` - Progressive coverage data
- `output/transformation-study/morphological-rules/` - Extracted rules
- `output/transformation-study/visualizations/` - Comprehensive visualizations
- `output/transformation-study/TASK2_SUMMARY_REPORT.md` - Summary report

## Task-3 Extended: Multi-Level Complexity Analysis

### New File: `multilevel_complexity_analyzer.py`

A comprehensive analyzer that examines register complexity at multiple linguistic levels.

**Levels Analyzed**:

1. **Lexical Level**:
   - Surface form analysis (Type-Token Ratio, entropy, perplexity)
   - Lemma-based analysis
   - Hapax legomena (words appearing once)
   - Cross-register divergence (KL divergence, JS divergence, overlap coefficient)

2. **Morphological Level**:
   - POS tag distribution and entropy
   - Morphological feature analysis (20 UD features)
   - Per-feature-type complexity
   - Feature-specific divergence measures

3. **Syntactic Level**:
   - Dependency relation distribution
   - Constituency label patterns
   - Syntactic construction diversity

4. **Structural Level**:
   - Constituency tree metrics (depth, branching factor)
   - Dependency tree metrics (sentence length, dependency distance)
   - Tree depth analysis

**Key Metrics**:
- **Entropy**: Unpredictability/diversity of linguistic units
- **Type-Token Ratio (TTR)**: Lexical diversity (with variants: Root TTR, Log TTR)
- **Perplexity**: Information-theoretic complexity (2^entropy)
- **Divergence**: KL divergence (both directions), JS divergence
- **Structural metrics**: Tree depth, branching factor, dependency distance

**Usage**:
```bash
# Analyze single newspaper
python multilevel_complexity_analyzer.py --newspaper "Times-of-India"

# Other newspapers
python multilevel_complexity_analyzer.py --newspaper "Hindustan-Times"
python multilevel_complexity_analyzer.py --newspaper "The-Hindu"
```

**Outputs Per Newspaper**:
- `multilevel_complexity_analysis.json` - Complete detailed results
- `multilevel_complexity_summary.csv` - Tabular summary
- `combined_complexity_scores.csv` - Aggregate scores across levels

### New File: `run_multilevel_complexity_analysis.py`

Comprehensive runner that analyzes all newspapers and creates comparative visualizations.

**Features**:
- Runs multi-level analysis for all newspapers
- Aggregates results across newspapers
- Creates comprehensive comparative visualizations
- Generates cross-newspaper analysis reports

**Usage**:
```bash
python run_multilevel_complexity_analysis.py
```

**Visualizations Generated**:

1. **Entropy Comparison** (`entropy_comparison.png`):
   - Entropy by linguistic level and register
   - Entropy by sublevel
   - Entropy distribution by newspaper
   - Level-specific canonical vs headline comparison

2. **TTR Comparison** (`ttr_comparison.png`):
   - Type-Token Ratio by sublevel
   - TTR distribution by newspaper
   - Lexical diversity patterns

3. **Structural Comparison** (`structural_comparison.png`):
   - Average tree depth
   - Average sentence length
   - Average dependency distance
   - Average branching factor

4. **Complexity Heatmaps** (`complexity_heatmaps.png`):
   - Canonical register entropy heatmap (level × newspaper)
   - Headline register entropy heatmap (level × newspaper)

5. **Complexity Ratios** (`complexity_ratios.png`):
   - Canonical/Headline complexity ratios by level
   - Ratio by metric type
   - Shows which register is more complex at each level

**Global Analysis Outputs**:
- `aggregated_complexity_metrics.csv` - All metrics across all newspapers
- `complexity_ratios.csv` - Canonical/Headline complexity ratios
- 5 comprehensive visualization PNG files
- `MULTILEVEL_ANALYSIS_REPORT.md` - Detailed research summary

## Integration with Existing System

### Updated `CLAUDE.md`

The main documentation file has been updated to include:

1. **Task 2 CLI Runner**:
   - Command-line interface and options
   - Pipeline description
   - Output structure

2. **Task 3 Extended Features**:
   - Multi-level complexity analysis description
   - Commands for running extended analysis
   - Output structure for multilevel analysis

3. **Enhanced Output Structure**:
   - New `multilevel_complexity/` directory
   - Per-newspaper and global analysis organization
   - Comprehensive visualization outputs

### Workflow Integration

The new features integrate seamlessly with the existing three-task workflow:

1. **Task 1**: Generate difference events (unchanged)
2. **Task 2**: Now has CLI runner (`run_task2_transformation_study.py`)
3. **Task 3**: Extended with multi-level analysis (`run_multilevel_complexity_analysis.py`)

## Key Improvements

### 1. Completeness

- Task 2 now has a complete CLI interface matching Tasks 1 and 3
- Task 3 extended with comprehensive multi-level analysis
- All linguistic levels now systematically analyzed

### 2. Granularity

The system now analyzes complexity at multiple granularities:
- **Surface level**: Word forms
- **Lemma level**: Base forms
- **POS level**: Part-of-speech categories
- **Morphological level**: Fine-grained features (20 types)
- **Syntactic level**: Dependency/constituency patterns
- **Structural level**: Tree-based metrics

### 3. Metrics Diversity

Multiple complementary metrics for each level:
- Entropy (unpredictability)
- Type-Token Ratio (diversity)
- Perplexity (complexity)
- Divergence (cross-register differences)
- Structural metrics (depth, distance, branching)

### 4. Comparative Analysis

Cross-newspaper comparison at all levels:
- Heatmaps showing patterns across newspapers and levels
- Statistical comparisons
- Complexity ratio analysis (canonical vs headline)

### 5. Visualization Quality

Comprehensive publication-ready visualizations:
- Multi-panel comparison plots
- Heatmaps for cross-newspaper patterns
- Statistical distributions
- Ratio plots showing relative complexity

## Research Implications

The new multi-level analysis enables answering questions such as:

1. **At which linguistic levels are the registers most different?**
   - Compare entropy/divergence across levels
   - Identify levels with highest canonical/headline differences

2. **Is morphological complexity higher in one register?**
   - Analyze POS entropy and morphological feature diversity
   - Compare feature-specific patterns

3. **How does structural complexity differ?**
   - Tree depth, branching factor, dependency distance
   - Identify structural simplification patterns in headlines

4. **Are patterns consistent across newspapers?**
   - Cross-newspaper heatmaps
   - Variation in register differences

5. **Which complexity measures correlate with transformation difficulty?**
   - Can integrate with Task 2 coverage results
   - Predict which transformations are hardest

## Usage Examples

### Complete Three-Task Analysis with Extended Features

```bash
# Step 1: Run Task 1 (comparative study)
python run_task1_all_newspapers.py

# Step 2: Run Task 2 (transformation study) with new CLI
python run_task2_transformation_study.py

# Step 3a: Run original Task 3 (complexity & similarity)
python run_task3_complexity_similarity.py

# Step 3b: Run extended multi-level complexity analysis
python run_multilevel_complexity_analysis.py
```

### Selective Analysis

```bash
# Only Task 2 for specific newspapers
python run_task2_transformation_study.py --newspapers "Times-of-India"

# Multi-level analysis for single newspaper (for testing)
python multilevel_complexity_analyzer.py --newspaper "Times-of-India"
```

### Quick Workflow Testing

```bash
# Task 2 without time-consuming visualizations
python run_task2_transformation_study.py --skip-visualization

# Task 2 assuming rules already extracted
python run_task2_transformation_study.py --skip-extraction
```

## Technical Details

### Dependencies

No new dependencies required. Uses existing libraries:
- `pandas`, `numpy` for data processing
- `scipy` for statistical measures (entropy, divergence)
- `matplotlib`, `seaborn` for visualizations
- `conllu` for parsing dependency trees
- `nltk` for constituency trees

### Performance

- Single newspaper multi-level analysis: ~2-5 minutes
- All newspapers multi-level analysis: ~10-15 minutes
- Visualization generation: ~1-2 minutes

### Data Requirements

The multi-level analyzer requires:
- Plain text files (canonical and headlines)
- CoNLL-U dependency parses
- Constituency parse trees

All of which are already available from Task 1 data preparation.

## Future Extensions

Potential future enhancements based on this foundation:

1. **Semantic Level Analysis**:
   - Word embedding distances
   - Semantic role patterns
   - Argument structure complexity

2. **Pragmatic Level Analysis**:
   - Discourse marker usage
   - Cohesion metrics
   - Information structure patterns

3. **Cross-Linguistic Extension**:
   - Apply same multi-level framework to other languages
   - Compare complexity patterns across languages

4. **Predictive Modeling**:
   - Use multi-level metrics to predict transformation difficulty
   - Identify which levels correlate most with MT metrics

5. **Theoretical Integration**:
   - Map findings to register theory (Halliday, Biber)
   - Compare with corpus linguistics findings
   - Publication-ready comparative tables

---

**Date**: December 25, 2024
**Version**: 5.1
**Impact**: Major enhancement to Task 2 and Task 3 capabilities
**Status**: Implemented and documented
