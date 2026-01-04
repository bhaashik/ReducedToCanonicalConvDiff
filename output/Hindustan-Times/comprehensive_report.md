# Comprehensive Register Comparison Analysis

**Differences between Reduced and Canonical Forms**

---

## Executive Summary

This report presents a comprehensive analysis of linguistic differences between reduced register (newspaper headlines) and canonical forms. The analysis identified **49,567 difference events** across **30 distinct linguistic features**.

### Key Findings

1. **Constituent Movement** (CONST-MOV): 13,099 occurrences (26.4% of total)
2. **Dependency Relation Change** (DEP-REL-CHG): 11,759 occurrences (23.7% of total)
3. **Clause Type Change** (CLAUSE-TYPE-CHG): 3,408 occurrences (6.9% of total)
4. **Function Word Deletion** (FW-DEL): 3,210 occurrences (6.5% of total)
5. **Punctuation Deletion** (PUNCT-DEL): 1,515 occurrences (3.1% of total)

---

## Global Analysis

### Feature Distribution

| Rank | Feature ID | Feature Name | Count | Percentage |
|------|------------|--------------|-------|------------|
| 1 | CONST-MOV | Constituent Movement | 13,099 | 26.43% |
| 2 | DEP-REL-CHG | Dependency Relation Change | 11,759 | 23.72% |
| 3 | CLAUSE-TYPE-CHG | Clause Type Change | 3,408 | 6.88% |
| 4 | FW-DEL | Function Word Deletion | 3,210 | 6.48% |
| 5 | PUNCT-DEL | Punctuation Deletion | 1,515 | 3.06% |
| 6 | C-DEL | Content Word Deletion | 1,405 | 2.83% |
| 7 | H-STRUCT | Headline Structure | 1,148 | 2.32% |
| 8 | H-TYPE | Headline Type | 1,148 | 2.32% |
| 9 | TREE-DEPTH-DIFF | Tree Depth Difference | 1,148 | 2.32% |
| 10 | CONST-COUNT-DIFF | Constituent Count Difference | 1,148 | 2.32% |
| 11 | DEP-DIST-DIFF | Dependency Distance Difference | 1,148 | 2.32% |
| 12 | BRANCH-DIFF | Branching Factor Difference | 1,148 | 2.32% |
| 13 | TED-SIMPLE | TED-SIMPLE | 1,142 | 2.30% |
| 14 | TED-RTED | TED-RTED | 1,142 | 2.30% |
| 15 | LENGTH-CHG | Sentence Length Change | 1,137 | 2.29% |
| 16 | TED-ZHANG-SHASHA | TED-ZHANG-SHASHA | 783 | 1.58% |
| 17 | TED-KLEIN | TED-KLEIN | 783 | 1.58% |
| 18 | PUNCT-ADD | Punctuation Addition | 753 | 1.52% |
| 19 | C-ADD | Content Word Addition | 690 | 1.39% |
| 20 | CONST-REM | Constituent Removal | 476 | 0.96% |
| 21 | PUNCT-SUBST | Punctuation Substitution | 413 | 0.83% |
| 22 | HEAD-CHG | Dependency Head Change | 280 | 0.56% |
| 23 | FW-ADD | Function Word Addition | 266 | 0.54% |
| 24 | FEAT-CHG | Morphological Feature Change | 126 | 0.25% |
| 25 | CONST-ADD | Constituent Addition | 114 | 0.23% |
| 26 | POS-CHG | Part of Speech Change | 84 | 0.17% |
| 27 | FORM-CHG | Surface Form Change | 61 | 0.12% |
| 28 | LEMMA-CHG | Lemma Change | 17 | 0.03% |
| 29 | VERB-FORM-CHG | Verb Form Change | 13 | 0.03% |
| 30 | TOKEN-REORDER | Token Reordering | 3 | 0.01% |

---

## Parse Type Analysis

The analysis examined differences across dependency and constituency parsing:

### Dependency Parsing

**Total events:** 20,199

| Feature ID | Count | Percentage |
|------------|-------|------------|
| DEP-REL-CHG | 11,759 | 58.22% |
| FW-DEL | 3,210 | 15.89% |
| C-DEL | 1,405 | 6.96% |
| DEP-DIST-DIFF | 1,148 | 5.68% |
| LENGTH-CHG | 1,137 | 5.63% |
| C-ADD | 690 | 3.42% |
| HEAD-CHG | 280 | 1.39% |
| FW-ADD | 266 | 1.32% |
| FEAT-CHG | 126 | 0.62% |
| POS-CHG | 84 | 0.42% |

### Constituency Parsing

**Total events:** 24,391

| Feature ID | Count | Percentage |
|------------|-------|------------|
| CONST-MOV | 13,099 | 53.70% |
| CLAUSE-TYPE-CHG | 3,408 | 13.97% |
| TREE-DEPTH-DIFF | 1,148 | 4.71% |
| CONST-COUNT-DIFF | 1,148 | 4.71% |
| BRANCH-DIFF | 1,148 | 4.71% |
| TED-SIMPLE | 1,142 | 4.68% |
| TED-RTED | 1,142 | 4.68% |
| TED-ZHANG-SHASHA | 783 | 3.21% |
| TED-KLEIN | 783 | 3.21% |
| CONST-REM | 476 | 1.95% |

### Both Parsing

**Total events:** 4,977

| Feature ID | Count | Percentage |
|------------|-------|------------|
| PUNCT-DEL | 1,515 | 30.44% |
| H-STRUCT | 1,148 | 23.07% |
| H-TYPE | 1,148 | 23.07% |
| PUNCT-ADD | 753 | 15.13% |
| PUNCT-SUBST | 413 | 8.30% |

---

## Feature Categories Analysis

### Distribution by Linguistic Category

| Category | Features | Total Count | Percentage |
|----------|----------|-------------|------------|
| Lexical | 7 | 5,733 | 11.57% |
| Syntactic | 5 | 25,728 | 51.91% |
| Morphological | 2 | 139 | 0.28% |
| Word Order | 1 | 3 | 0.01% |
| Clause Level | 1 | 3,408 | 6.88% |
| Structural | 1 | 1,137 | 2.29% |

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

*Report generated on 2026-01-03 13:41:37*