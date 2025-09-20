# Comprehensive Register Comparison Analysis

**Differences between Reduced and Canonical Forms**

---

## Executive Summary

This report presents a comprehensive analysis of linguistic differences between reduced register (newspaper headlines) and canonical forms. The analysis identified **30,847 difference events** across **18 distinct linguistic features**.

### Key Findings

1. **Constituent Movement** (CONST-MOV): 11,485 occurrences (37.2% of total)
2. **Dependency Relation Change** (DEP-REL-CHG): 9,892 occurrences (32.1% of total)
3. **Clause Type Change** (CLAUSE-TYPE-CHG): 2,728 occurrences (8.8% of total)
4. **Function Word Deletion** (FW-DEL): 2,241 occurrences (7.3% of total)
5. **Tree Edit Distance** (TED): 1,034 occurrences (3.4% of total)

---

## Global Analysis

### Feature Distribution

| Rank | Feature ID | Feature Name | Count | Percentage |
|------|------------|--------------|-------|------------|
| 1 | CONST-MOV | Constituent Movement | 11,485 | 37.23% |
| 2 | DEP-REL-CHG | Dependency Relation Change | 9,892 | 32.07% |
| 3 | CLAUSE-TYPE-CHG | Clause Type Change | 2,728 | 8.84% |
| 4 | FW-DEL | Function Word Deletion | 2,241 | 7.26% |
| 5 | TED | Tree Edit Distance | 1,034 | 3.35% |
| 6 | LENGTH-CHG | Sentence Length Change | 1,022 | 3.31% |
| 7 | C-DEL | Content Word Deletion | 720 | 2.33% |
| 8 | C-ADD | Content Word Addition | 540 | 1.75% |
| 9 | HEAD-CHG | Dependency Head Change | 282 | 0.91% |
| 10 | CONST-REM | Constituent Removal | 254 | 0.82% |
| 11 | FW-ADD | Function Word Addition | 170 | 0.55% |
| 12 | FEAT-CHG | Morphological Feature Change | 129 | 0.42% |
| 13 | CONST-ADD | Constituent Addition | 124 | 0.40% |
| 14 | POS-CHG | Part of Speech Change | 89 | 0.29% |
| 15 | FORM-CHG | Surface Form Change | 89 | 0.29% |
| 16 | LEMMA-CHG | Lemma Change | 22 | 0.07% |
| 17 | VERB-FORM-CHG | Verb Form Change | 14 | 0.05% |
| 18 | TOKEN-REORDER | Token Reordering | 12 | 0.04% |

---

## Parse Type Analysis

The analysis examined differences across dependency and constituency parsing:

### Dependency Parsing

**Total events:** 15,222

| Feature ID | Count | Percentage |
|------------|-------|------------|
| DEP-REL-CHG | 9,892 | 64.98% |
| FW-DEL | 2,241 | 14.72% |
| LENGTH-CHG | 1,022 | 6.71% |
| C-DEL | 720 | 4.73% |
| C-ADD | 540 | 3.55% |
| HEAD-CHG | 282 | 1.85% |
| FW-ADD | 170 | 1.12% |
| FEAT-CHG | 129 | 0.85% |
| POS-CHG | 89 | 0.58% |
| FORM-CHG | 89 | 0.58% |

### Constituency Parsing

**Total events:** 15,625

| Feature ID | Count | Percentage |
|------------|-------|------------|
| CONST-MOV | 11,485 | 73.50% |
| CLAUSE-TYPE-CHG | 2,728 | 17.46% |
| TED | 1,034 | 6.62% |
| CONST-REM | 254 | 1.63% |
| CONST-ADD | 124 | 0.79% |

---

## Feature Categories Analysis

### Distribution by Linguistic Category

| Category | Features | Total Count | Percentage |
|----------|----------|-------------|------------|
| Lexical | 7 | 3,871 | 12.55% |
| Syntactic | 5 | 22,037 | 71.44% |
| Morphological | 2 | 143 | 0.46% |
| Word Order | 1 | 12 | 0.04% |
| Clause Level | 1 | 2,728 | 8.84% |
| Structural | 2 | 2,056 | 6.67% |

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

*Report generated on 2025-09-15 22:08:35*