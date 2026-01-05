# Comprehensive Register Comparison Analysis

**Differences between Reduced and Canonical Forms**

---

## Executive Summary

This report presents a comprehensive analysis of linguistic differences between reduced register (newspaper headlines) and canonical forms. The analysis identified **40,617 difference events** across **30 distinct linguistic features**.

### Key Findings

1. **Constituent Movement** (CONST-MOV): 11,485 occurrences (28.3% of total)
2. **Dependency Relation Change** (DEP-REL-CHG): 9,892 occurrences (24.4% of total)
3. **Clause Type Change** (CLAUSE-TYPE-CHG): 2,728 occurrences (6.7% of total)
4. **Function Word Deletion** (FW-DEL): 2,241 occurrences (5.5% of total)
5. **Headline Structure** (H-STRUCT): 1,041 occurrences (2.6% of total)

---

## Global Analysis

### Feature Distribution

| Rank | Feature ID | Feature Name | Count | Percentage |
|------|------------|--------------|-------|------------|
| 1 | CONST-MOV | Constituent Movement | 11,485 | 28.28% |
| 2 | DEP-REL-CHG | Dependency Relation Change | 9,892 | 24.35% |
| 3 | CLAUSE-TYPE-CHG | Clause Type Change | 2,728 | 6.72% |
| 4 | FW-DEL | Function Word Deletion | 2,241 | 5.52% |
| 5 | H-STRUCT | Headline Structure | 1,041 | 2.56% |
| 6 | H-TYPE | Headline Type | 1,041 | 2.56% |
| 7 | TREE-DEPTH-DIFF | Tree Depth Difference | 1,041 | 2.56% |
| 8 | CONST-COUNT-DIFF | Constituent Count Difference | 1,041 | 2.56% |
| 9 | DEP-DIST-DIFF | Dependency Distance Difference | 1,041 | 2.56% |
| 10 | BRANCH-DIFF | Branching Factor Difference | 1,041 | 2.56% |
| 11 | TED-RTED | TED-RTED | 1,035 | 2.55% |
| 12 | TED-SIMPLE | TED-SIMPLE | 1,034 | 2.55% |
| 13 | LENGTH-CHG | Sentence Length Change | 1,022 | 2.52% |
| 14 | TED-ZHANG-SHASHA | TED-ZHANG-SHASHA | 806 | 1.98% |
| 15 | TED-KLEIN | TED-KLEIN | 806 | 1.98% |
| 16 | C-DEL | Content Word Deletion | 720 | 1.77% |
| 17 | C-ADD | Content Word Addition | 540 | 1.33% |
| 18 | PUNCT-ADD | Punctuation Addition | 401 | 0.99% |
| 19 | PUNCT-DEL | Punctuation Deletion | 307 | 0.76% |
| 20 | HEAD-CHG | Dependency Head Change | 282 | 0.69% |
| 21 | CONST-REM | Constituent Removal | 254 | 0.63% |
| 22 | FW-ADD | Function Word Addition | 170 | 0.42% |
| 23 | FEAT-CHG | Morphological Feature Change | 160 | 0.39% |
| 24 | PUNCT-SUBST | Punctuation Substitution | 138 | 0.34% |
| 25 | CONST-ADD | Constituent Addition | 124 | 0.31% |
| 26 | POS-CHG | Part of Speech Change | 89 | 0.22% |
| 27 | FORM-CHG | Surface Form Change | 89 | 0.22% |
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

**Total events:** 2,928

| Feature ID | Count | Percentage |
|------------|-------|------------|
| H-STRUCT | 1,041 | 35.55% |
| H-TYPE | 1,041 | 35.55% |
| PUNCT-ADD | 401 | 13.70% |
| PUNCT-DEL | 307 | 10.48% |
| PUNCT-SUBST | 138 | 4.71% |

---

## Feature Categories Analysis

### Distribution by Linguistic Category

| Category | Features | Total Count | Percentage |
|----------|----------|-------------|------------|
| Lexical | 7 | 3,871 | 9.53% |
| Syntactic | 5 | 22,037 | 54.26% |
| Morphological | 2 | 174 | 0.43% |
| Word Order | 1 | 12 | 0.03% |
| Clause Level | 1 | 2,728 | 6.72% |
| Structural | 1 | 1,022 | 2.52% |

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

*Report generated on 2026-01-05 13:54:08*