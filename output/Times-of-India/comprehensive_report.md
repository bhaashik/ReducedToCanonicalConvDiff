# Comprehensive Register Comparison Analysis

**Differences between Reduced and Canonical Forms**

---

## Executive Summary

This report presents a comprehensive analysis of linguistic differences between reduced register (newspaper headlines) and canonical forms. The analysis identified **33,525 difference events** across **21 distinct linguistic features**.

### Key Findings

1. **Constituent Movement** (CONST-MOV): 11,485 occurrences (34.3% of total)
2. **Dependency Relation Change** (DEP-REL-CHG): 9,892 occurrences (29.5% of total)
3. **Clause Type Change** (CLAUSE-TYPE-CHG): 2,728 occurrences (8.1% of total)
4. **Function Word Deletion** (FW-DEL): 2,241 occurrences (6.7% of total)
5. **TED-RTED** (TED-RTED): 1,035 occurrences (3.1% of total)

---

## Global Analysis

### Feature Distribution

| Rank | Feature ID | Feature Name | Count | Percentage |
|------|------------|--------------|-------|------------|
| 1 | CONST-MOV | Constituent Movement | 11,485 | 34.26% |
| 2 | DEP-REL-CHG | Dependency Relation Change | 9,892 | 29.51% |
| 3 | CLAUSE-TYPE-CHG | Clause Type Change | 2,728 | 8.14% |
| 4 | FW-DEL | Function Word Deletion | 2,241 | 6.68% |
| 5 | TED-RTED | TED-RTED | 1,035 | 3.09% |
| 6 | TED-SIMPLE | TED-SIMPLE | 1,034 | 3.08% |
| 7 | LENGTH-CHG | Sentence Length Change | 1,022 | 3.05% |
| 8 | TED-ZHANG-SHASHA | TED-ZHANG-SHASHA | 806 | 2.40% |
| 9 | TED-KLEIN | TED-KLEIN | 806 | 2.40% |
| 10 | C-DEL | Content Word Deletion | 720 | 2.15% |
| 11 | C-ADD | Content Word Addition | 540 | 1.61% |
| 12 | HEAD-CHG | Dependency Head Change | 282 | 0.84% |
| 13 | CONST-REM | Constituent Removal | 254 | 0.76% |
| 14 | FW-ADD | Function Word Addition | 170 | 0.51% |
| 15 | FEAT-CHG | Morphological Feature Change | 160 | 0.48% |
| 16 | CONST-ADD | Constituent Addition | 124 | 0.37% |
| 17 | POS-CHG | Part of Speech Change | 89 | 0.27% |
| 18 | FORM-CHG | Surface Form Change | 89 | 0.27% |
| 19 | LEMMA-CHG | Lemma Change | 22 | 0.07% |
| 20 | VERB-FORM-CHG | Verb Form Change | 14 | 0.04% |
| 21 | TOKEN-REORDER | Token Reordering | 12 | 0.04% |

---

## Parse Type Analysis

The analysis examined differences across dependency and constituency parsing:

### Dependency Parsing

**Total events:** 15,253

| Feature ID | Count | Percentage |
|------------|-------|------------|
| DEP-REL-CHG | 9,892 | 64.85% |
| FW-DEL | 2,241 | 14.69% |
| LENGTH-CHG | 1,022 | 6.70% |
| C-DEL | 720 | 4.72% |
| C-ADD | 540 | 3.54% |
| HEAD-CHG | 282 | 1.85% |
| FW-ADD | 170 | 1.11% |
| FEAT-CHG | 160 | 1.05% |
| POS-CHG | 89 | 0.58% |
| FORM-CHG | 89 | 0.58% |

### Constituency Parsing

**Total events:** 18,272

| Feature ID | Count | Percentage |
|------------|-------|------------|
| CONST-MOV | 11,485 | 62.86% |
| CLAUSE-TYPE-CHG | 2,728 | 14.93% |
| TED-RTED | 1,035 | 5.66% |
| TED-SIMPLE | 1,034 | 5.66% |
| TED-ZHANG-SHASHA | 806 | 4.41% |
| TED-KLEIN | 806 | 4.41% |
| CONST-REM | 254 | 1.39% |
| CONST-ADD | 124 | 0.68% |

---

## Feature Categories Analysis

### Distribution by Linguistic Category

| Category | Features | Total Count | Percentage |
|----------|----------|-------------|------------|
| Lexical | 7 | 3,871 | 11.55% |
| Syntactic | 5 | 22,037 | 65.73% |
| Morphological | 2 | 174 | 0.52% |
| Word Order | 1 | 12 | 0.04% |
| Clause Level | 1 | 2,728 | 8.14% |
| Structural | 1 | 1,022 | 3.05% |

---

## Linguistic Interpretation

### Register Differences

The analysis reveals systematic differences between reduced and canonical registers:

- **Lexical Simplification**: High frequency of function word deletions and content word changes
- **Syntactic Compression**: Significant constituent removal and dependency relation changes
- **Structural Modifications**: Tree edit distance indicates substantial restructuring
- **Morphological Variation**: Changes in verb forms and morphological features

### Implications for Register Theory

These findings support theories of register variation that emphasize:

1. **Functional pressure**: Headlines prioritize information density
2. **Cognitive processing**: Reduced forms facilitate rapid comprehension
3. **Stylistic conventions**: Newspaper genre constraints shape linguistic choices

---

## Statistical Visualizations

The following comprehensive visualizations provide statistical summaries across all dimensional combinations:

### Comprehensive Analysis Visualizations

- **Global Feature Frequencies**: `feature_freq_global.png`
- **Parse Type Comparison**: `parse_type_comparison.png`
- **Feature Coverage Heatmap**: `feature_coverage_heatmap.png`
- **Top Features Analysis**: `top_features_analysis.png`
- **Cross-Dimensional Analysis**: `cross_dimensional_analysis.png`
- **Feature Category Distribution**: `feature_category_distribution.png`

### Statistical Summary Visualizations

- **Newspaper Statistical Comparison**: `newspaper_statistical_comparison.png`
- **Parse Type Statistical Differences**: `parse_type_statistical_differences.png`
- **Cross-Dimensional Statistics**: `cross_dimensional_statistics.png`
- **Feature Distribution Statistics**: `feature_distribution_statistics.png`
- **Comparative Variance Analysis**: `comparative_variance_analysis.png`
- **Statistical Significance Heatmap**: `statistical_significance_heatmap.png`

### Key Insights from Visualizations

These visualizations reveal important patterns:

- **Feature frequency distributions** across different dimensional breakdowns
- **Statistical significance** of differences between newspapers and parse types
- **Variance patterns** in cross-dimensional feature combinations
- **Distributional characteristics** of linguistic difference events
- **Comparative analysis** showing systematic patterns across dimensions

---

## Methodology

### Data Processing

- Texts parsed using Stanza NLP toolkit
- Dependency and constituency parses generated
- Feature extraction based on linguistic schema
- Statistical analysis and visualization

### Feature Schema

Analysis based on 18 predefined linguistic features covering:

- Lexical differences (word additions, deletions, changes)
- Syntactic variations (dependency and constituency changes)
- Morphological modifications
- Word order alterations
- Structural transformations

---

*Report generated on 2025-12-23 14:19:31*