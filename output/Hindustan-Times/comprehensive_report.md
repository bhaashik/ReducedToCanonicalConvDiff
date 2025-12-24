# Comprehensive Register Comparison Analysis

**Differences between Reduced and Canonical Forms**

---

## Executive Summary

This report presents a comprehensive analysis of linguistic differences between reduced register (newspaper headlines) and canonical forms. The analysis identified **39,998 difference events** across **21 distinct linguistic features**.

### Key Findings

1. **Constituent Movement** (CONST-MOV): 13,099 occurrences (32.7% of total)
2. **Dependency Relation Change** (DEP-REL-CHG): 11,759 occurrences (29.4% of total)
3. **Clause Type Change** (CLAUSE-TYPE-CHG): 3,408 occurrences (8.5% of total)
4. **Function Word Deletion** (FW-DEL): 3,210 occurrences (8.0% of total)
5. **Content Word Deletion** (C-DEL): 1,405 occurrences (3.5% of total)

---

## Global Analysis

### Feature Distribution

| Rank | Feature ID | Feature Name | Count | Percentage |
|------|------------|--------------|-------|------------|
| 1 | CONST-MOV | Constituent Movement | 13,099 | 32.75% |
| 2 | DEP-REL-CHG | Dependency Relation Change | 11,759 | 29.40% |
| 3 | CLAUSE-TYPE-CHG | Clause Type Change | 3,408 | 8.52% |
| 4 | FW-DEL | Function Word Deletion | 3,210 | 8.03% |
| 5 | C-DEL | Content Word Deletion | 1,405 | 3.51% |
| 6 | TED-SIMPLE | TED-SIMPLE | 1,142 | 2.86% |
| 7 | TED-RTED | TED-RTED | 1,142 | 2.86% |
| 8 | LENGTH-CHG | Sentence Length Change | 1,137 | 2.84% |
| 9 | TED-ZHANG-SHASHA | TED-ZHANG-SHASHA | 783 | 1.96% |
| 10 | TED-KLEIN | TED-KLEIN | 783 | 1.96% |
| 11 | C-ADD | Content Word Addition | 690 | 1.73% |
| 12 | CONST-REM | Constituent Removal | 476 | 1.19% |
| 13 | HEAD-CHG | Dependency Head Change | 280 | 0.70% |
| 14 | FW-ADD | Function Word Addition | 266 | 0.67% |
| 15 | FEAT-CHG | Morphological Feature Change | 126 | 0.32% |
| 16 | CONST-ADD | Constituent Addition | 114 | 0.29% |
| 17 | POS-CHG | Part of Speech Change | 84 | 0.21% |
| 18 | FORM-CHG | Surface Form Change | 61 | 0.15% |
| 19 | LEMMA-CHG | Lemma Change | 17 | 0.04% |
| 20 | VERB-FORM-CHG | Verb Form Change | 13 | 0.03% |
| 21 | TOKEN-REORDER | Token Reordering | 3 | 0.01% |

---

## Parse Type Analysis

The analysis examined differences across dependency and constituency parsing:

### Dependency Parsing

**Total events:** 19,051

| Feature ID | Count | Percentage |
|------------|-------|------------|
| DEP-REL-CHG | 11,759 | 61.72% |
| FW-DEL | 3,210 | 16.85% |
| C-DEL | 1,405 | 7.37% |
| LENGTH-CHG | 1,137 | 5.97% |
| C-ADD | 690 | 3.62% |
| HEAD-CHG | 280 | 1.47% |
| FW-ADD | 266 | 1.40% |
| FEAT-CHG | 126 | 0.66% |
| POS-CHG | 84 | 0.44% |
| FORM-CHG | 61 | 0.32% |

### Constituency Parsing

**Total events:** 20,947

| Feature ID | Count | Percentage |
|------------|-------|------------|
| CONST-MOV | 13,099 | 62.53% |
| CLAUSE-TYPE-CHG | 3,408 | 16.27% |
| TED-SIMPLE | 1,142 | 5.45% |
| TED-RTED | 1,142 | 5.45% |
| TED-ZHANG-SHASHA | 783 | 3.74% |
| TED-KLEIN | 783 | 3.74% |
| CONST-REM | 476 | 2.27% |
| CONST-ADD | 114 | 0.54% |

---

## Feature Categories Analysis

### Distribution by Linguistic Category

| Category | Features | Total Count | Percentage |
|----------|----------|-------------|------------|
| Lexical | 7 | 5,733 | 14.33% |
| Syntactic | 5 | 25,728 | 64.32% |
| Morphological | 2 | 139 | 0.35% |
| Word Order | 1 | 3 | 0.01% |
| Clause Level | 1 | 3,408 | 8.52% |
| Structural | 1 | 1,137 | 2.84% |

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

*Report generated on 2025-12-23 14:20:36*