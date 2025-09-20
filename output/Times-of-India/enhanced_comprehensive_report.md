# Enhanced Register Comparison Analysis

**Feature-Value Transformations in Reduced vs Canonical Forms**

---

## Executive Summary

This enhanced report presents a comprehensive feature-value analysis of linguistic differences between reduced register (newspaper headlines) and canonical forms. The analysis identified **30,847 difference events** across **18 distinct linguistic features** with **1,197 unique transformation types**.

### Key Feature-Value Insights

1. **Dependency Relation Change** (DEP-REL-CHG): 821 unique transformations, most frequent: `det→compound` (272 cases)
2. **Sentence Length Change** (LENGTH-CHG): 140 unique transformations, most frequent: `13→10` (39 cases)
3. **Surface Form Change** (FORM-CHG): 77 unique transformations, most frequent: `said→says` (4 cases)
4. **Dependency Head Change** (HEAD-CHG): 56 unique transformations, most frequent: `3→2` (58 cases)
5. **Lemma Change** (LEMMA-CHG): 20 unique transformations, most frequent: `United→Unite` (2 cases)

---

## Feature-Value Transformation Analysis

### Transformation Diversity Overview

| Feature | Total Transformations | Unique Types | Canonical Diversity | Headline Diversity | Top3 Concentration |
|---------|----------------------|--------------|--------------------|--------------------|-------------------|
| CONST-MOV | 11,485 | 2 | 2 | 2 | 1.000 |
| DEP-REL-CHG | 9,892 | 821 | 44 | 43 | 0.067 |
| CLAUSE-TYPE-CHG | 2,728 | 7 | 5 | 5 | 0.779 |
| FW-DEL | 2,241 | 6 | 6 | 1 | 0.862 |
| TED | 1,034 | 10 | 10 | 10 | 0.983 |
| LENGTH-CHG | 1,022 | 140 | 25 | 22 | 0.113 |
| C-DEL | 720 | 4 | 4 | 1 | 0.986 |
| C-ADD | 540 | 4 | 1 | 4 | 0.981 |
| HEAD-CHG | 282 | 56 | 17 | 15 | 0.440 |
| CONST-REM | 254 | 6 | 6 | 1 | 0.803 |
| FW-ADD | 170 | 6 | 1 | 6 | 0.871 |
| FEAT-CHG | 129 | 19 | 13 | 13 | 0.535 |
| CONST-ADD | 124 | 5 | 1 | 5 | 0.855 |
| POS-CHG | 89 | 6 | 3 | 3 | 0.798 |
| FORM-CHG | 89 | 77 | 74 | 75 | 0.101 |
| LEMMA-CHG | 22 | 20 | 20 | 20 | 0.227 |
| VERB-FORM-CHG | 14 | 6 | 4 | 3 | 0.786 |
| TOKEN-REORDER | 12 | 2 | 2 | 2 | 1.000 |

### Most Frequent Transformations by Feature

| Feature | Transformation | Count |
|---------|----------------|-------|
| FW-DEL | `ART-DEL→ABSENT` | 920 |
| FW-DEL | `AUX-DEL→ABSENT` | 844 |
| FW-DEL | `ADP-DEL→ABSENT` | 167 |
| DEP-REL-CHG | `det→compound` | 272 |
| DEP-REL-CHG | `nsubj→root` | 212 |
| DEP-REL-CHG | `aux→root` | 176 |
| LENGTH-CHG | `13→10` | 39 |
| LENGTH-CHG | `16→12` | 39 |
| LENGTH-CHG | `15→11` | 37 |
| CONST-REM | `SBAR-REM→ABSENT` | 130 |
| CONST-REM | `VP-REM→ABSENT` | 40 |
| CONST-REM | `PP-REM→ABSENT` | 34 |
| CONST-MOV | `CONST-FRONT→CONST-FRONT` | 10,743 |
| CONST-MOV | `CONST-POST→CONST-POST` | 742 |
| CLAUSE-TYPE-CHG | `Part→Fin` | 986 |
| CLAUSE-TYPE-CHG | `Fin→Part` | 631 |
| CLAUSE-TYPE-CHG | `Fin→Inf` | 507 |
| TED | `10→10` | 997 |
| TED | `1→1` | 13 |
| TED | `5→5` | 6 |
| HEAD-CHG | `3→2` | 58 |
| HEAD-CHG | `4→3` | 42 |
| HEAD-CHG | `5→4` | 24 |
| C-DEL | `NOUN-DEL→ABSENT` | 340 |
| C-DEL | `VERB-DEL→ABSENT` | 264 |
| C-DEL | `ADJ-DEL→ABSENT` | 106 |
| C-ADD | `ABSENT→NOUN-ADD` | 379 |
| C-ADD | `ABSENT→VERB-ADD` | 93 |
| C-ADD | `ABSENT→ADJ-ADD` | 58 |
| POS-CHG | `VERB→NOUN` | 41 |
| POS-CHG | `NOUN→VERB` | 21 |
| POS-CHG | `NOUN→ADJ` | 9 |
| FORM-CHG | `said→says` | 4 |
| FORM-CHG | `‘→’` | 3 |
| FORM-CHG | `Passengers→passengers` | 2 |
| FEAT-CHG | `Tense=Past→Tense=Pres` | 46 |
| FEAT-CHG | `Number=None→Number=Sing` | 13 |
| FEAT-CHG | `Number=Plur→Number=Sing` | 10 |
| CONST-ADD | `ABSENT→ADJP-ADD` | 44 |
| CONST-ADD | `ABSENT→SBAR-ADD` | 40 |
| CONST-ADD | `ABSENT→ADVP-ADD` | 22 |
| FW-ADD | `ABSENT→ADP-ADD` | 79 |
| FW-ADD | `ABSENT→PRON-PERS-ADD` | 35 |
| FW-ADD | `ABSENT→AUX-ADD` | 34 |
| LEMMA-CHG | `United→Unite` | 2 |
| LEMMA-CHG | `Mumbaikars→mumbaikar` | 2 |
| LEMMA-CHG | `shareef→Shareef` | 1 |
| VERB-FORM-CHG | `Part→Fin` | 7 |
| VERB-FORM-CHG | `Fin→Part` | 2 |
| VERB-FORM-CHG | `Fin→Inf` | 2 |
| TOKEN-REORDER | `FRONT→FRONT` | 8 |
| TOKEN-REORDER | `POST→POST` | 4 |

---

## Enhanced Feature-Value Visualizations

The analysis includes comprehensive visualizations showing specific value-to-value transformations:

### Standard Analysis Visualizations

- **Global Feature Frequencies**: `feature_freq_global.png`
- **Parse Type Comparison**: `parse_type_comparison.png`
- **Feature Coverage Heatmap**: `feature_coverage_heatmap.png`
- **Top Features Analysis**: `top_features_analysis.png`
- **Cross-Dimensional Analysis**: `cross_dimensional_analysis.png`
- **Feature Category Distribution**: `feature_category_distribution.png`

### Feature-Value Transformation Visualizations

- **Individual Feature Analysis**: `feature_analysis_[FEATURE].png` (18 files)
- **Transformation Patterns Overview**: `transformation_patterns_overview.png`
- **Value Diversity Analysis**: `value_diversity_analysis.png`
- **Top Transformations per Feature**: `top_transformations_per_feature.png`
- **Transformation Entropy Analysis**: `transformation_entropy.png`

### Enhanced Value→Value Visualizations

- **Transformation Matrices**: `[FEATURE]_transformation_matrix.png`
- **Flow Diagrams**: `[FEATURE]_transformation_flow.png`
- **Detailed Analysis**: `[FEATURE]_detailed_analysis.png`
- **Network Graphs**: `[FEATURE]_transformation_network.png`
- **Overall Network**: `overall_transformation_network.png`
- **Flow Summary**: `transformation_flow_summary.png`

---

## Modular Analysis Framework

This analysis was conducted using an enhanced modular framework supporting:

### Analysis Levels

- **Basic**: Feature counts, basic statistics, simple visualizations
- **Comprehensive**: Multi-dimensional analysis, statistical testing, comprehensive visualizations
- **Feature-Value**: Complete value transformation analysis with detailed breakdowns

### Modular Execution Options

- Independent per-newspaper analysis
- Global cross-newspaper aggregation
- Enhanced value→value transformation visualizations
- Scalable to additional newspapers and features

### Usage Examples

```bash
# Basic analysis for specific newspaper
python register_comparison/modular_analysis.py --newspapers 'Times-of-India' --analysis basic

# Feature-value analysis with enhanced visualizations
python register_comparison/modular_analysis.py --newspapers all --analysis feature-value --enhance-visuals

# Global cross-newspaper analysis
python register_comparison/modular_analysis.py --global-only --analysis feature-value
```

---

## Enhanced Linguistic Interpretation

### Value-Level Register Differences

The feature-value analysis reveals specific transformation patterns:

- **Dependency Relations**: Complex restructuring with `det→compound` as most frequent change
- **Part-of-Speech Changes**: `VERB→NOUN` (46%) dominates over `NOUN→VERB` (24%)
- **Function Word Deletion**: `ART-DEL→ABSENT` represents 41% of all function word deletions
- **Constituent Movement**: Highly concentrated with 93.5% being `CONST-FRONT→CONST-FRONT`

### Transformation Complexity

Feature diversity analysis shows:
- **High diversity**: DEP-REL-CHG with 821 unique transformation types
- **Low diversity**: CONST-MOV with 2 transformation types but 11,485 total occurrences
- **Balanced diversity**: Features showing moderate transformation variety with functional specialization

### Implications for Register Theory

These findings support theories of register variation that emphasize:

1. **Functional pressure**: Headlines prioritize information density through systematic value transformations
2. **Cognitive processing**: Reduced forms facilitate rapid comprehension via predictable transformation patterns
3. **Stylistic conventions**: Newspaper genre constraints shape specific value-to-value mappings

---

## Enhanced Methodology

### Data Processing Pipeline

1. Texts parsed using Stanza NLP toolkit
2. Dependency and constituency parses generated
3. Schema-based feature extraction (18 features)
4. Feature-value transformation analysis
5. Statistical testing with contingency tables
6. Multi-dimensional aggregation and visualization

### Feature-Value Analysis Framework

Analysis based on 18 predefined linguistic features with value-level granularity:

- **Transformation mapping**: Canonical→Headline value pairs
- **Statistical metrics**: Entropy, diversity, concentration ratios
- **Pattern classification**: Deletions, additions, changes, null changes
- **Visualization enhancement**: Matrices, flows, networks, detailed breakdowns

---

*Enhanced report generated on 2025-09-16 21:42:38 using modular feature-value analysis framework.*