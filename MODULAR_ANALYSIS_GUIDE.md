# Modular Register Comparison Analysis System

## Overview

This system provides **modular, independent analysis** at different levels of granularity with **enhanced value→value transformation visualizations**. It supports multi-newspaper analysis with global aggregation and detailed feature-value transformation analysis.

## ✅ Key Features Implemented

### 1. **Modular Analysis Levels**
- **Basic**: Feature counts, statistics, simple visualizations
- **Comprehensive**: Multi-dimensional analysis, statistical testing
- **Feature-Value**: Complete value transformation analysis

### 2. **Multi-Newspaper Support**
- Independent per-newspaper analysis
- Global cross-newspaper aggregation
- Comparative analysis across newspapers
- Support for all newspapers in `paths_config.py`

### 3. **Enhanced Value→Value Visualizations**
- **Transformation matrices**: Heatmaps showing canonical→headline value changes
- **Flow diagrams**: Sankey-style visualizations of value transformations
- **Network graphs**: Relationship networks between values
- **Detailed breakdowns**: Per-feature transformation analysis with statistics

## 🚀 Usage Examples

### Run Analysis for Specific Newspapers

```bash
# Basic analysis for Times-of-India only
python register_comparison/modular_analysis.py \\
    --newspapers "Times-of-India" \\
    --analysis basic

# Comprehensive analysis for specific newspapers
python register_comparison/modular_analysis.py \\
    --newspapers "Times-of-India,The-Hindu" \\
    --analysis comprehensive

# Feature-value analysis for all newspapers
python register_comparison/modular_analysis.py \\
    --newspapers all \\
    --analysis feature-value
```

### Enhanced Visualizations

```bash
# Feature-value analysis with enhanced value→value visualizations
python register_comparison/modular_analysis.py \\
    --newspapers all \\
    --analysis feature-value \\
    --enhance-visuals
```

### Global Analysis Only

```bash
# Run only global analysis (requires previous newspaper analysis)
python register_comparison/modular_analysis.py \\
    --global-only \\
    --analysis feature-value
```

## 📊 Enhanced Visualizations Created

### 1. **Value Transformation Matrices**
- **Purpose**: Show which canonical values transform to which headline values
- **Files**: `[FEATURE]_transformation_matrix.png`
- **Features**: Heatmap with counts, log-scale for large differences
- **Example**: Shows that `det→compound` is the most frequent DEP-REL-CHG transformation

### 2. **Transformation Flow Diagrams**
- **Purpose**: Sankey-style flow showing value transformations
- **Files**: `[FEATURE]_transformation_flow.png`
- **Features**: Arrow width proportional to frequency, clear value mapping
- **Example**: Visualizes how VERB→NOUN (46%) vs NOUN→VERB (24%) in POS-CHG

### 3. **Detailed Feature Analysis**
- **Files**: `[FEATURE]_detailed_analysis.png`
- **Features**: Bar chart + statistics panel
- **Content**:
  - Top 20 transformations with percentages
  - Value diversity metrics
  - Transformation type breakdown (deletions/additions/changes)
  - Most frequent transformation details

### 4. **Network Graphs**
- **Files**: `[FEATURE]_transformation_network.png`
- **Purpose**: Show transformation relationships as networks
- **Features**: Node colors (canonical=blue, headline=red), edge weights

### 5. **Cross-Newspaper Analysis**
- **Files**: `cross_newspaper_analysis.png`
- **Purpose**: Compare analysis results across newspapers
- **Features**: Total events, feature diversity, top features, efficiency metrics

## 📁 Output Structure

```
output/
├── Times-of-India/                    # Per-newspaper analysis
│   ├── feature_freq_global.csv
│   ├── events_global.csv
│   ├── summary_stats_global.csv
│   ├── comprehensive_analysis*.csv
│   ├── feature_value_analysis*.csv
│   ├── feature_analysis_[FEATURE].png # Individual feature visualizations (18 files)
│   └── *.png                          # Standard visualizations
├── The-Hindu/                         # Another newspaper
├── Hindustan-Times/                   # Third newspaper
├── GLOBAL_ANALYSIS/                   # Cross-newspaper analysis
│   ├── global_comprehensive_analysis*.csv
│   ├── cross_newspaper_comparison.csv
│   ├── cross_newspaper_analysis.png
│   └── global_*.png
└── ENHANCED_TRANSFORMATIONS/          # Enhanced value→value visualizations
    ├── DEP-REL-CHG_transformation_matrix.png
    ├── DEP-REL-CHG_transformation_flow.png
    ├── DEP-REL-CHG_detailed_analysis.png
    ├── POS-CHG_transformation_matrix.png
    ├── [FEATURE]_transformation_network.png (for complex features)
    ├── overall_transformation_network.png
    └── transformation_flow_summary.png
```

## 🔬 Scientific Value

### Fine-Grained Transformation Analysis
Instead of just knowing "DEP-REL-CHG has 9,892 occurrences", we now know:
- **821 unique transformation types**
- **`det→compound`** is most frequent (272 cases, 2.7%)
- **Canonical diversity**: 44 values → **Headline diversity**: 43 values
- **Top 3 concentration**: Only 6.7% (high diversity)

### Linguistic Insights Revealed
- **POS-CHG**: VERB→NOUN transformations (46%) vs NOUN→VERB (24%)
- **Function Word Patterns**: ART-DEL→ABSENT dominates (41% of FW-DEL)
- **Dependency Relations**: Complex restructuring with high diversity
- **Constituent Movement**: Highly concentrated (93.5% CONST-FRONT→CONST-FRONT)

## 🛠 Technical Architecture

### Modular Components
1. **`ModularAnalysisRunner`**: Main orchestrator class
2. **`EnhancedVisualizer`**: Specialized value→value visualizations
3. **Level-specific analysis**: Basic → Comprehensive → Feature-Value
4. **Multi-newspaper aggregation**: Independent + global analysis

### Key Methods Added
- **`get_feature_value_analysis()`**: Complete value-level analysis
- **`create_value_to_value_transformations()`**: Detailed transformation visualizations
- **`create_transformation_networks()`**: Network analysis of relationships
- **`_create_cross_newspaper_analysis()`**: Multi-newspaper comparison

## 🎯 Research Applications

### 1. **Independent Analysis Runs**
- Analyze specific newspapers without full dataset processing
- Different analysis levels based on research needs
- Modular approach saves time for focused investigations

### 2. **Value-Level Linguistic Analysis**
- Understand **what changes to what** not just **what changes**
- Quantify specific transformation patterns
- Compare transformation diversity across features

### 3. **Cross-Newspaper Comparative Studies**
- Systematic comparison across multiple data sources
- Global patterns vs newspaper-specific variations
- Scalable to additional newspapers

### 4. **Enhanced Academic Visualizations**
- Publication-ready transformation matrices
- Clear value→value mapping diagrams
- Professional network visualizations
- Comprehensive statistical breakdowns

This system transforms the analysis from **"feature counting"** to **"transformation mapping"**, providing the granular insights needed for linguistic register research.