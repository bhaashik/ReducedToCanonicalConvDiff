# Comprehensive Register Comparison Analysis

**Differences between Reduced and Canonical Forms**

---

## Executive Summary

This report presents a comprehensive analysis of linguistic differences between reduced register (newspaper headlines) and canonical forms. The analysis identified **30,818 difference events** across **30 distinct linguistic features**.

### Key Findings

1. **Constituent Movement** (CONST-MOV): 5,705 occurrences (18.5% of total)
2. **Dependency Relation Change** (DEP-REL-CHG): 5,284 occurrences (17.1% of total)
3. **Function Word Deletion** (FW-DEL): 1,661 occurrences (5.4% of total)
4. **Clause Type Change** (CLAUSE-TYPE-CHG): 1,500 occurrences (4.9% of total)
5. **Headline Structure** (H-STRUCT): 1,500 occurrences (4.9% of total)

---

## Global Analysis

### Feature Distribution

| Rank | Feature ID | Feature Name | Count | Percentage |
|------|------------|--------------|-------|------------|
| 1 | CONST-MOV | Constituent Movement | 5,705 | 18.51% |
| 2 | DEP-REL-CHG | Dependency Relation Change | 5,284 | 17.15% |
| 3 | FW-DEL | Function Word Deletion | 1,661 | 5.39% |
| 4 | CLAUSE-TYPE-CHG | Clause Type Change | 1,500 | 4.87% |
| 5 | H-STRUCT | Headline Structure | 1,500 | 4.87% |
| 6 | H-TYPE | Headline Type | 1,500 | 4.87% |
| 7 | TREE-DEPTH-DIFF | Tree Depth Difference | 1,500 | 4.87% |
| 8 | CONST-COUNT-DIFF | Constituent Count Difference | 1,500 | 4.87% |
| 9 | DEP-DIST-DIFF | Dependency Distance Difference | 1,500 | 4.87% |
| 10 | BRANCH-DIFF | Branching Factor Difference | 1,500 | 4.87% |
| 11 | TED-RTED | TED-RTED | 1,139 | 3.70% |
| 12 | TED-ZHANG-SHASHA | TED-ZHANG-SHASHA | 1,124 | 3.65% |
| 13 | TED-KLEIN | TED-KLEIN | 1,124 | 3.65% |
| 14 | LENGTH-CHG | Sentence Length Change | 1,117 | 3.62% |
| 15 | TED-SIMPLE | TED-SIMPLE | 1,058 | 3.43% |
| 16 | C-DEL | Content Word Deletion | 447 | 1.45% |
| 17 | CONST-REM | Constituent Removal | 278 | 0.90% |
| 18 | C-ADD | Content Word Addition | 200 | 0.65% |
| 19 | HEAD-CHG | Dependency Head Change | 198 | 0.64% |
| 20 | PUNCT-ADD | Punctuation Addition | 190 | 0.62% |
| 21 | PUNCT-DEL | Punctuation Deletion | 180 | 0.58% |
| 22 | FORM-CHG | Surface Form Change | 158 | 0.51% |
| 23 | FEAT-CHG | Morphological Feature Change | 122 | 0.40% |
| 24 | CONST-ADD | Constituent Addition | 91 | 0.30% |
| 25 | POS-CHG | Part of Speech Change | 83 | 0.27% |
| 26 | PUNCT-SUBST | Punctuation Substitution | 67 | 0.22% |
| 27 | FW-ADD | Function Word Addition | 49 | 0.16% |
| 28 | LEMMA-CHG | Lemma Change | 26 | 0.08% |
| 29 | VERB-FORM-CHG | Verb Form Change | 11 | 0.04% |
| 30 | TOKEN-REORDER | Token Reordering | 6 | 0.02% |

---

## Parse Type Analysis

The analysis examined differences across dependency and constituency parsing:

### Dependency Parsing

**Total events:** 10,862

| Feature ID | Count | Percentage |
|------------|-------|------------|
| DEP-REL-CHG | 5,284 | 48.65% |
| FW-DEL | 1,661 | 15.29% |
| DEP-DIST-DIFF | 1,500 | 13.81% |
| LENGTH-CHG | 1,117 | 10.28% |
| C-DEL | 447 | 4.12% |
| C-ADD | 200 | 1.84% |
| HEAD-CHG | 198 | 1.82% |
| FORM-CHG | 158 | 1.45% |
| FEAT-CHG | 122 | 1.12% |
| POS-CHG | 83 | 0.76% |

### Constituency Parsing

**Total events:** 16,519

| Feature ID | Count | Percentage |
|------------|-------|------------|
| CONST-MOV | 5,705 | 34.54% |
| CLAUSE-TYPE-CHG | 1,500 | 9.08% |
| TREE-DEPTH-DIFF | 1,500 | 9.08% |
| CONST-COUNT-DIFF | 1,500 | 9.08% |
| BRANCH-DIFF | 1,500 | 9.08% |
| TED-RTED | 1,139 | 6.90% |
| TED-ZHANG-SHASHA | 1,124 | 6.80% |
| TED-KLEIN | 1,124 | 6.80% |
| TED-SIMPLE | 1,058 | 6.40% |
| CONST-REM | 278 | 1.68% |

### Both Parsing

**Total events:** 3,437

| Feature ID | Count | Percentage |
|------------|-------|------------|
| H-STRUCT | 1,500 | 43.64% |
| H-TYPE | 1,500 | 43.64% |
| PUNCT-ADD | 190 | 5.53% |
| PUNCT-DEL | 180 | 5.24% |
| PUNCT-SUBST | 67 | 1.95% |

---

## Feature Categories Analysis

### Distribution by Linguistic Category

| Category | Features | Total Count | Percentage |
|----------|----------|-------------|------------|
| Lexical | 7 | 2,624 | 8.51% |
| Syntactic | 5 | 11,556 | 37.50% |
| Morphological | 2 | 133 | 0.43% |
| Word Order | 1 | 6 | 0.02% |
| Clause Level | 1 | 1,500 | 4.87% |
| Structural | 1 | 1,117 | 3.62% |

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

*Report generated on 2026-02-13 13:36:17*