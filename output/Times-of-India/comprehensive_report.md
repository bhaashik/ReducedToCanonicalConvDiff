# Comprehensive Register Comparison Analysis

**Differences between Reduced and Canonical Forms**

---

## Executive Summary

This report presents a comprehensive analysis of linguistic differences between reduced register (newspaper headlines) and canonical forms. The analysis identified **41,616 difference events** across **30 distinct linguistic features**.

### Key Findings

1. **Constituent Movement** (CONST-MOV): 11,485 occurrences (27.6% of total)
2. **Dependency Relation Change** (DEP-REL-CHG): 9,892 occurrences (23.8% of total)
3. **Clause Type Change** (CLAUSE-TYPE-CHG): 2,728 occurrences (6.6% of total)
4. **Function Word Deletion** (FW-DEL): 2,241 occurrences (5.4% of total)
5. **Punctuation Deletion** (PUNCT-DEL): 1,306 occurrences (3.1% of total)

---

## Global Analysis

### Feature Distribution

| Rank | Feature ID | Feature Name | Count | Percentage |
|------|------------|--------------|-------|------------|
| 1 | CONST-MOV | Constituent Movement | 11,485 | 27.60% |
| 2 | DEP-REL-CHG | Dependency Relation Change | 9,892 | 23.77% |
| 3 | CLAUSE-TYPE-CHG | Clause Type Change | 2,728 | 6.56% |
| 4 | FW-DEL | Function Word Deletion | 2,241 | 5.38% |
| 5 | PUNCT-DEL | Punctuation Deletion | 1,306 | 3.14% |
| 6 | H-STRUCT | Headline Structure | 1,041 | 2.50% |
| 7 | H-TYPE | Headline Type | 1,041 | 2.50% |
| 8 | TREE-DEPTH-DIFF | Tree Depth Difference | 1,041 | 2.50% |
| 9 | CONST-COUNT-DIFF | Constituent Count Difference | 1,041 | 2.50% |
| 10 | DEP-DIST-DIFF | Dependency Distance Difference | 1,041 | 2.50% |
| 11 | BRANCH-DIFF | Branching Factor Difference | 1,041 | 2.50% |
| 12 | TED-RTED | TED-RTED | 1,035 | 2.49% |
| 13 | TED-SIMPLE | TED-SIMPLE | 1,034 | 2.48% |
| 14 | LENGTH-CHG | Sentence Length Change | 1,022 | 2.46% |
| 15 | TED-ZHANG-SHASHA | TED-ZHANG-SHASHA | 806 | 1.94% |
| 16 | TED-KLEIN | TED-KLEIN | 806 | 1.94% |
| 17 | C-DEL | Content Word Deletion | 720 | 1.73% |
| 18 | C-ADD | Content Word Addition | 540 | 1.30% |
| 19 | PUNCT-ADD | Punctuation Addition | 401 | 0.96% |
| 20 | HEAD-CHG | Dependency Head Change | 282 | 0.68% |
| 21 | CONST-REM | Constituent Removal | 254 | 0.61% |
| 22 | FW-ADD | Function Word Addition | 170 | 0.41% |
| 23 | FEAT-CHG | Morphological Feature Change | 160 | 0.38% |
| 24 | PUNCT-SUBST | Punctuation Substitution | 138 | 0.33% |
| 25 | CONST-ADD | Constituent Addition | 124 | 0.30% |
| 26 | POS-CHG | Part of Speech Change | 89 | 0.21% |
| 27 | FORM-CHG | Surface Form Change | 89 | 0.21% |
| 28 | LEMMA-CHG | Lemma Change | 22 | 0.05% |
| 29 | VERB-FORM-CHG | Verb Form Change | 14 | 0.03% |
| 30 | TOKEN-REORDER | Token Reordering | 12 | 0.03% |

---

## Parse Type Analysis

The analysis examined differences across dependency and constituency parsing:

### Dependency Parsing

**Total events:** 16,294

| Feature ID | Count | Percentage |
|------------|-------|------------|
| DEP-REL-CHG | 9,892 | 60.71% |
| FW-DEL | 2,241 | 13.75% |
| DEP-DIST-DIFF | 1,041 | 6.39% |
| LENGTH-CHG | 1,022 | 6.27% |
| C-DEL | 720 | 4.42% |
| C-ADD | 540 | 3.31% |
| HEAD-CHG | 282 | 1.73% |
| FW-ADD | 170 | 1.04% |
| FEAT-CHG | 160 | 0.98% |
| POS-CHG | 89 | 0.55% |

### Constituency Parsing

**Total events:** 21,395

| Feature ID | Count | Percentage |
|------------|-------|------------|
| CONST-MOV | 11,485 | 53.68% |
| CLAUSE-TYPE-CHG | 2,728 | 12.75% |
| TREE-DEPTH-DIFF | 1,041 | 4.87% |
| CONST-COUNT-DIFF | 1,041 | 4.87% |
| BRANCH-DIFF | 1,041 | 4.87% |
| TED-RTED | 1,035 | 4.84% |
| TED-SIMPLE | 1,034 | 4.83% |
| TED-ZHANG-SHASHA | 806 | 3.77% |
| TED-KLEIN | 806 | 3.77% |
| CONST-REM | 254 | 1.19% |

### Both Parsing

**Total events:** 3,927

| Feature ID | Count | Percentage |
|------------|-------|------------|
| PUNCT-DEL | 1,306 | 33.26% |
| H-STRUCT | 1,041 | 26.51% |
| H-TYPE | 1,041 | 26.51% |
| PUNCT-ADD | 401 | 10.21% |
| PUNCT-SUBST | 138 | 3.51% |

---

## Feature Categories Analysis

### Distribution by Linguistic Category

| Category | Features | Total Count | Percentage |
|----------|----------|-------------|------------|
| Lexical | 7 | 3,871 | 9.30% |
| Syntactic | 5 | 22,037 | 52.95% |
| Morphological | 2 | 174 | 0.42% |
| Word Order | 1 | 12 | 0.03% |
| Clause Level | 1 | 2,728 | 6.56% |
| Structural | 1 | 1,022 | 2.46% |

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

Analysis based on 30 predefined linguistic features covering:

- Lexical differences (word additions, deletions, changes)
- Syntactic variations (dependency and constituency changes)
- Morphological modifications
- Word order alterations
- Structural transformations

---

*Report generated on 2026-01-04 15:49:11*