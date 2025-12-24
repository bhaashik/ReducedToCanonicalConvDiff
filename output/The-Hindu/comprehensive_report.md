# Comprehensive Register Comparison Analysis

**Differences between Reduced and Canonical Forms**

---

## Executive Summary

This report presents a comprehensive analysis of linguistic differences between reduced register (newspaper headlines) and canonical forms. The analysis identified **21,381 difference events** across **21 distinct linguistic features**.

### Key Findings

1. **Constituent Movement** (CONST-MOV): 5,705 occurrences (26.7% of total)
2. **Dependency Relation Change** (DEP-REL-CHG): 5,284 occurrences (24.7% of total)
3. **Function Word Deletion** (FW-DEL): 1,661 occurrences (7.8% of total)
4. **Clause Type Change** (CLAUSE-TYPE-CHG): 1,500 occurrences (7.0% of total)
5. **TED-RTED** (TED-RTED): 1,139 occurrences (5.3% of total)

---

## Global Analysis

### Feature Distribution

| Rank | Feature ID | Feature Name | Count | Percentage |
|------|------------|--------------|-------|------------|
| 1 | CONST-MOV | Constituent Movement | 5,705 | 26.68% |
| 2 | DEP-REL-CHG | Dependency Relation Change | 5,284 | 24.71% |
| 3 | FW-DEL | Function Word Deletion | 1,661 | 7.77% |
| 4 | CLAUSE-TYPE-CHG | Clause Type Change | 1,500 | 7.02% |
| 5 | TED-RTED | TED-RTED | 1,139 | 5.33% |
| 6 | TED-ZHANG-SHASHA | TED-ZHANG-SHASHA | 1,124 | 5.26% |
| 7 | TED-KLEIN | TED-KLEIN | 1,124 | 5.26% |
| 8 | LENGTH-CHG | Sentence Length Change | 1,117 | 5.22% |
| 9 | TED-SIMPLE | TED-SIMPLE | 1,058 | 4.95% |
| 10 | C-DEL | Content Word Deletion | 447 | 2.09% |
| 11 | CONST-REM | Constituent Removal | 278 | 1.30% |
| 12 | C-ADD | Content Word Addition | 200 | 0.94% |
| 13 | HEAD-CHG | Dependency Head Change | 198 | 0.93% |
| 14 | FORM-CHG | Surface Form Change | 158 | 0.74% |
| 15 | FEAT-CHG | Morphological Feature Change | 122 | 0.57% |
| 16 | CONST-ADD | Constituent Addition | 91 | 0.43% |
| 17 | POS-CHG | Part of Speech Change | 83 | 0.39% |
| 18 | FW-ADD | Function Word Addition | 49 | 0.23% |
| 19 | LEMMA-CHG | Lemma Change | 26 | 0.12% |
| 20 | VERB-FORM-CHG | Verb Form Change | 11 | 0.05% |
| 21 | TOKEN-REORDER | Token Reordering | 6 | 0.03% |

---

## Parse Type Analysis

The analysis examined differences across dependency and constituency parsing:

### Dependency Parsing

**Total events:** 9,362

| Feature ID | Count | Percentage |
|------------|-------|------------|
| DEP-REL-CHG | 5,284 | 56.44% |
| FW-DEL | 1,661 | 17.74% |
| LENGTH-CHG | 1,117 | 11.93% |
| C-DEL | 447 | 4.77% |
| C-ADD | 200 | 2.14% |
| HEAD-CHG | 198 | 2.11% |
| FORM-CHG | 158 | 1.69% |
| FEAT-CHG | 122 | 1.30% |
| POS-CHG | 83 | 0.89% |
| FW-ADD | 49 | 0.52% |

### Constituency Parsing

**Total events:** 12,019

| Feature ID | Count | Percentage |
|------------|-------|------------|
| CONST-MOV | 5,705 | 47.47% |
| CLAUSE-TYPE-CHG | 1,500 | 12.48% |
| TED-RTED | 1,139 | 9.48% |
| TED-ZHANG-SHASHA | 1,124 | 9.35% |
| TED-KLEIN | 1,124 | 9.35% |
| TED-SIMPLE | 1,058 | 8.80% |
| CONST-REM | 278 | 2.31% |
| CONST-ADD | 91 | 0.76% |

---

## Feature Categories Analysis

### Distribution by Linguistic Category

| Category | Features | Total Count | Percentage |
|----------|----------|-------------|------------|
| Lexical | 7 | 2,624 | 12.27% |
| Syntactic | 5 | 11,556 | 54.05% |
| Morphological | 2 | 133 | 0.62% |
| Word Order | 1 | 6 | 0.03% |
| Clause Level | 1 | 1,500 | 7.02% |
| Structural | 1 | 1,117 | 5.22% |

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

*Report generated on 2025-12-23 14:21:36*