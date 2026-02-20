# Comprehensive to Selected Migration Plan
## Summary-Level Tables and Figures for 8-Page ACL ARR Long Papers

**Date:** 2026-01-07
**Paper Format:** 8 pages main content + unlimited references/appendices
**Directory Structure:** global/ and per-newspaper subdirectories in both comprehensive and selected
**Critical Focus:** Normalized values for fair cross-newspaper comparison (esp. Task 3)

---

## Executive Summary

### Current Status Overview

| Task | Comp Tables | Sel Tables | Comp Figs (Global) | Sel Figs (Global) | Gap Analysis |
|------|-------------|------------|-------------------|-------------------|--------------|
| Task 1 | 108 | 0 (embedded) | 90 | 16 | **74 global figures missing** |
| Task 2 | 16 | 0 (embedded) | 19 | 0 (no global dir) | **All 19 global figures missing** |
| Task 3 | 44 | 0 (embedded) | 12 | 12 | **Tables missing, figures complete** |

**Key Finding:** Task 1 and Task 2 are missing majority of global summary figures. All three tasks lack standalone summary tables.

---

## TASK 1: Comparative Study (Morphosyntactic Differences)

### Directory Analysis

**Comprehensive:**
- Tables: `latex-comprehensive/tables/` (108 files, NO subdirectories)
- Figures: `latex-comprehensive/figures/{global, Hindustan-Times, The-Hindu, Times-of-India}/`
  - Global: 90 figures
  - Per-newspaper: ~70-80 each

**Selected:**
- Tables: None (all embedded in main .tex)
- Figures: `latex-selected/{global, Hindustan-Times, The-Hindu, Times-of-India}/`
  - Global: 16 figures only
  - Per-newspaper: 11 each

### CRITICAL MISSING ITEMS

#### Tables to Add (Create `latex-selected/tables/`)

##### PRIORITY 1: Global Summary Tables (Main Paper)

1. **global_comprehensive_analysis_global.tex**
   - Overall feature frequency across all newspapers
   - ~30 rows (all features)
   - **Placement:** Main paper, Section 4 (Results)

2. **cross_newspaper_comparison.tex**
   - Statistical comparison across three newspapers
   - Shows consistency/variation
   - **Placement:** Main paper, Section 4.2 (Cross-newspaper analysis)

3. **global_statistical_summary_features.tex**
   - Chi-square, Fisher's exact test, p-values
   - Statistical validation of significance
   - **Placement:** Main paper, Section 4.3 (Statistical validation)

4. **global_bidirectional_cross_entropy_analysis_global_metrics.tex**
   - Cross-entropy, KL divergence, asymmetry metrics
   - Information-theoretic measures
   - **Placement:** Main paper, Section 5 (Information asymmetry)

5. **global_feature_value_pair_analysis_top_pairs.tex**
   - Top 10-15 most frequent transformation patterns
   - Dominant transformation types
   - **Placement:** Main paper, Section 4.4 (Transformation patterns)

##### PRIORITY 2: Supporting Tables (Appendix)

6. **global_comprehensive_analysis_by_parse_type.tex**
   - Dependency vs constituency breakdown
   - Validates parse-type consistency
   - **Placement:** Appendix A

7. **global_comprehensive_analysis_by_newspaper.tex**
   - Detailed per-newspaper breakdown
   - **Placement:** Appendix B

8. **morphological_features_cross_newspaper.tex**
   - Morphological-specific cross-newspaper analysis
   - **Placement:** Appendix C

9. **global_feature_value_pair_analysis_concentration_metrics.tex**
   - Gini, entropy, diversity measures for transformation concentration
   - **Placement:** Appendix D

#### Figures to Add - CRITICAL GAPS

**Current Selected Global:** 16 figures
**Comprehensive Global:** 90 figures
**Recommended additions:** 10-15 more global figures

##### PRIORITY 1: Cross-Newspaper Comparisons (Main Paper)

1. **cross_newspaper_event_counts.png** ← **MISSING, CRITICAL**
   - Source: `latex-comprehensive/figures/global/cross_newspaper_event_counts.png`
   - Shows total events per newspaper
   - **Why critical:** Direct visual comparison of data sizes

2. **cross_newspaper_normalized_comparison.png** ← **PARTIAL (in selected)**
   - Already in selected, KEEP
   - Normalized feature frequencies for fair comparison
   - **Why critical:** Controls for corpus size differences

3. **cross_newspaper_feature_heatmap.png** ← **PARTIAL (in selected)**
   - Already in selected, KEEP
   - Feature distribution matrix across newspapers

4. **cross_newspaper_top_features_comparison.png** ← **MISSING, HIGH PRIORITY**
   - Source: `latex-comprehensive/figures/global/cross_newspaper_top_features_comparison.png`
   - Top features comparison across newspapers
   - **Why important:** Shows which features are universally important

5. **cross_newspaper_parse_types.png** ← **MISSING, MEDIUM PRIORITY**
   - Source: `latex-comprehensive/figures/global/cross_newspaper_parse_types.png`
   - Parse type breakdown across newspapers

##### PRIORITY 2: Statistical Visualizations (Main Paper)

6. **statistical_significance_heatmap.png** ← **MISSING, HIGH PRIORITY**
   - Source: `latex-comprehensive/figures/global/statistical_significance_heatmap.png`
   - (Note: Actually per-newspaper, need to check if global version exists)
   - P-value heatmap for feature significance
   - **Why important:** Visual validation of statistical tests

7. **feature_distribution_statistics.png** ← **MISSING, MEDIUM PRIORITY**
   - Source: Need to check if global version exists
   - Statistical distribution of features

##### PRIORITY 3: TED Algorithm Comparisons (Appendix)

8. **ted_score_correlations.png** ← **PARTIAL (in selected)**
   - Already in selected global/, KEEP
   - Correlation among four TED algorithms

9. **ted_algorithm_agreement.png** ← **MISSING, FOR APPENDIX**
   - Source: Per-newspaper versions exist, check if global exists
   - Agreement/disagreement among TED algorithms

10. **ted_newspaper_register_patterns.png** ← **MISSING, FOR APPENDIX**
    - Source: Per-newspaper versions exist
    - TED patterns across newspapers and registers

##### PRIORITY 4: Information-Theoretic Visualizations (Main Paper)

11. **global_cross_entropy_metrics.png** ← **MISSING, HIGH PRIORITY**
    - Source: Per-newspaper versions exist (`Hindustan-Times/global_cross_entropy_metrics.png`)
    - Check if aggregated global version exists
    - Cross-entropy across all newspapers

12. **information_asymmetry_analysis.png** ← **MISSING, HIGH PRIORITY**
    - Source: Per-newspaper versions exist
    - Directional information asymmetry (C→H vs H→C)

13. **feature_cross_entropy_ranking.png** ← **MISSING, MEDIUM PRIORITY**
    - Source: Per-newspaper versions exist
    - Features ranked by cross-entropy contribution

---

## TASK 2: Transformation Study (Rule Coverage & Systematicity)

### Directory Analysis

**Comprehensive:**
- Tables: `latex-comprehensive/tables/` (16 files, NO subdirectories)
- Figures: `latex-comprehensive/figures/{global, Hindustan-Times, The-Hindu, Times-of-India}/`
  - Global: 19 figures
  - Per-newspaper: 2 each (only progressive coverage and feature transformations)

**Selected:**
- Tables: None (all embedded in main .tex)
- Figures: `latex-selected/figures/{Hindustan-Times, The-Hindu, Times-of-India}/` + root
  - **NO global/ subdirectory!** ← **CRITICAL ISSUE**
  - Per-newspaper: 10 each
  - Root level: 10 figures (likely should be in global/)

### CRITICAL MISSING ITEMS

#### Tables to Add (Create `latex-selected/tables/`)

##### PRIORITY 1: Core Summary Tables (Main Paper)

1. **integrated_transformation_comparison.tex** ← **MOST CRITICAL**
   - Cross-newspaper comparison: events, morphological %, rule counts
   - Only 3 rows but ESSENTIAL summary
   - **Placement:** Main paper, Section 3 (Overview) or Section 4.1 (Summary results)
   - **Why critical:** Single table summarizing entire Task 2

2. **overall_morphological_statistics.tex**
   - Aggregated morphological transformation statistics
   - ~15 rows of global statistics
   - **Placement:** Main paper, Section 4.2 (Morphological analysis)

3. **morphological_systematicity.tex**
   - Systematicity metrics (regularity, coverage, effectiveness)
   - Answers RQ2 directly
   - **Placement:** Main paper, Section 5 (Systematicity)

##### PRIORITY 2: POS-Specific Analysis (Main Paper or Appendix)

4. **noun_morphology_comparison.tex**
   - Noun-specific patterns across newspapers
   - ~12 rows
   - **Placement:** Main paper Section 4.3 or Appendix A

5. **verb_morphology_comparison.tex**
   - Verb-specific patterns across newspapers
   - ~12 rows
   - **Placement:** Main paper Section 4.3 or Appendix A

6. **morphological_features_summary.tex**
   - Summary of all 20 morphological feature types (v4.0 schema)
   - **Placement:** Appendix B

##### PRIORITY 3: Value Pair Analysis (Appendix)

7. **feature_value_pair_analysis_top_pairs.tex**
   - Top transformation pairs
   - **Placement:** Appendix C

8. **feature_value_pair_analysis_transformation_complexity.tex**
   - Complexity metrics for pairs
   - **Placement:** Appendix C

9. **feature_value_pair_analysis_concentration_metrics.tex**
   - Gini, entropy for transformation concentration
   - **Placement:** Appendix D

#### Figures to Add - CRITICAL GAPS

**Current Selected:** 40 figures (30 per-newspaper + 10 root level)
**NO global/ subdirectory** ← **Must create and populate**
**Comprehensive Global:** 19 figures
**Recommendation:** Move root-level figures to global/ + add missing ones

##### PRIORITY 1: Restructure Existing Files

**ACTION REQUIRED:** Create `latex-selected/figures/global/` directory

**Move these from root to global/:**
1. accuracy_coverage.png → global/
2. coverage_curve.png → global/
3. rules_by_feature.png → global/
4. top_transformation_pairs.png → global/
5. transformation_entropy.png → global/
6. transformation_patterns_overview.png → global/
7. top_transformations_per_feature_fig1.png → global/
8. top_transformations_per_feature_fig2.png → global/

##### PRIORITY 2: Add Missing Global Figures

1. **task2_coverage_curve.png** ← **MISSING, CRITICAL**
   - Source: `latex-comprehensive/figures/global/task2_coverage_curve.png`
   - Progressive coverage across all newspapers
   - **Why critical:** Shows rule accumulation pattern

2. **task2_newspaper_comparison.png** ← **MISSING, CRITICAL**
   - Source: `latex-comprehensive/figures/global/task2_newspaper_comparison.png`
   - Direct visual comparison of newspaper statistics
   - **Why critical:** Cross-newspaper summary

3. **task2_morphological_rules.png** ← **MISSING, HIGH PRIORITY**
   - Source: `latex-comprehensive/figures/global/task2_morphological_rules.png`
   - Morphological rule patterns
   - **Why important:** Visualizes morphological rule space

4. **task2_punctuation_rules.png** ← **MISSING, MEDIUM PRIORITY**
   - Source: `latex-comprehensive/figures/global/task2_punctuation_rules.png`
   - Punctuation transformation rules

5. **task2_rule_hierarchy.png** ← **MISSING, MEDIUM PRIORITY**
   - Source: `latex-comprehensive/figures/global/task2_rule_hierarchy.png`
   - Hierarchical rule organization

6. **integrated_comparison.png** ← **MISSING, HIGH PRIORITY**
   - Source: `latex-comprehensive/figures/global/integrated_comparison.png`
   - Integrated view of morphological and non-morphological rules

7. **morphological_features_heatmap.png** ← **MISSING, HIGH PRIORITY**
   - Source: `latex-comprehensive/figures/global/morphological_features_heatmap.png`
   - Heatmap of morphological feature occurrences

8. **morphological_impact_comparison.png** ← **MISSING, MEDIUM PRIORITY**
   - Source: `latex-comprehensive/figures/global/morphological_impact_comparison.png`
   - Impact of morphological rules on coverage

9. **noun_morphology_comparison.png** ← **MISSING, MEDIUM PRIORITY**
   - Source: `latex-comprehensive/figures/global/noun_morphology_comparison.png`
   - Noun morphology patterns

10. **verb_morphology_comparison.png** ← **MISSING, MEDIUM PRIORITY**
    - Source: `latex-comprehensive/figures/global/verb_morphology_comparison.png`
    - Verb morphology patterns

11. **overall_morphological_statistics.png** ← **MISSING, MEDIUM PRIORITY**
    - Source: `latex-comprehensive/figures/global/overall_morphological_statistics.png`
    - Overall morphological statistics visualization

12. **transformation_directionality.png** ← **MISSING, HIGH PRIORITY**
    - Source: `latex-comprehensive/figures/global/transformation_directionality.png`
    - C→H vs H→C transformation patterns

13. **cross_newspaper_feature_comparison.png** ← **MISSING, HIGH PRIORITY**
    - Source: `latex-comprehensive/figures/global/cross_newspaper_feature_comparison.png`
    - Feature comparison across newspapers

---

## TASK 3: Complexity & Similarity Study

### Directory Analysis

**Comprehensive:**
- Tables: `latex-comprehensive/tables/` (44 files: 33 per-newspaper + 11 global)
  - Per-newspaper: `{Newspaper}_*.tex` (11 each × 3 = 33)
  - Global: 11 files (bidirectional_*, correlation_*, cross_newspaper_*, etc.)
- Figures: `latex-comprehensive/figures/{global, Hindustan-Times, The-Hindu, Times-of-India}/` + root
  - Global: 12 figures
  - Per-newspaper: 3 each (entropy, cross-entropy, directional asymmetry)
  - Root: 5 similarity figures

**Selected:**
- Tables: None (all embedded in main .tex)
- Figures: Complete match with comprehensive (32 files)
  - Global: 12 figures ✓
  - Per-newspaper: 3 each ✓
  - Root: 5 figures ✓

### KEY INSIGHT: NORMALIZATION IS CRITICAL

Task 3 must emphasize **normalized values** for fair comparison because:
- Newspapers have different corpus sizes
- Sentence length distributions vary
- Feature occurrence frequencies differ

**Normalized metrics needed:**
- Per-token perplexity
- Per-character perplexity
- Vocabulary-normalized cross-entropy
- Normalized similarity scores (Jaccard, Dice, etc.)
- Relative complexity ratios (H→C / C→H)

### CRITICAL MISSING ITEMS

#### Tables to Add (Create `latex-selected/tables/`)

##### PRIORITY 1: Core Metrics (Main Paper)

1. **bidirectional_metrics.tex** ← **MOST CRITICAL**
   - BLEU, ROUGE, chrF for H→C and C→H
   - 6 rows (3 newspapers × 2 directions)
   - **Placement:** Main paper, Section 4 (Results)
   - **Why critical:** Core evaluation metrics, answers RQ3

2. **directional_perplexity_analysis.tex** ← **MOST CRITICAL**
   - Perplexity for C→H vs H→C transformations
   - **MUST include normalized values**
   - **Placement:** Main paper, Section 4.2 (Complexity analysis)
   - **Why critical:** Answers "which direction is more complex?"

3. **cross_newspaper_comparison.tex** ← **HIGH PRIORITY**
   - Cross-newspaper statistical comparison
   - **Should include normalized metrics**
   - **Placement:** Main paper, Section 4.3 (Cross-newspaper analysis)

##### PRIORITY 2: Correlation & Validation (Main Paper)

4. **correlation_results.tex** ← **HIGH PRIORITY**
   - Correlation between complexity and performance
   - **KEY FINDING:** Perplexity vs BLEU: r=-0.92, p<0.01
   - **Placement:** Main paper, Section 5 (Validation)
   - **Why important:** Validates information-theoretic predictions

5. **inter_metric_correlations.tex**
   - Correlation matrix among metrics
   - Shows which metrics capture similar aspects
   - **Placement:** Main paper Section 5.2 or Appendix A

6. **ratio_correlations.tex**
   - Correlations with complexity ratios (H→C/C→H)
   - Tests directional asymmetry
   - **Placement:** Appendix A

##### PRIORITY 3: Detailed Analysis (Appendix)

7. **perplexity_complete_analysis.tex**
   - Complete breakdown: mono-register, cross-register, directional
   - **MUST include normalized variants**
   - **Placement:** Appendix B

8. **merged_mt_perplexity_data.tex**
   - Integrated MT metrics + perplexity
   - **Placement:** Appendix C

9. **event_level_perplexity.tex**
   - Fine-grained event-level analysis
   - **Placement:** Appendix D

##### PRIORITY 4: Normalized Complexity Tables (CRITICAL FOR FAIRNESS)

**RECOMMENDATION:** Create new normalized tables if they don't exist

10. **normalized_complexity_comparison.tex** ← **CREATE IF MISSING**
    - Per-token, per-character complexity metrics
    - Vocabulary-normalized measures
    - Fair cross-newspaper comparison
    - **Placement:** Main paper, Section 4.4 (Normalized analysis)
    - **Why critical:** Essential for fair comparison across newspapers

11. **complexity_ratios_normalized.tex** ← **CREATE IF MISSING**
    - H→C / C→H complexity ratios
    - Normalized by sentence length, vocabulary size
    - **Placement:** Main paper, Section 4.5 (Directional asymmetry)

#### Figures Status - COMPLETE BUT CHECK NORMALIZATION

**Current Status:** All 32 comprehensive figures copied to selected ✓

**Verification Needed:**
1. Check if normalized variants exist:
   - `ttr_comparison.png` - Is this normalized?
   - `entropy_comparison.png` - Raw or normalized?
   - `cross_entropy_comparison.png` - Raw or normalized?
   - `kl_divergence_comparison.png` - Raw or normalized?

2. **If normalized versions missing, CREATE THEM:**
   - `normalized_entropy_comparison.png` ← **CREATE**
   - `normalized_cross_entropy_comparison.png` ← **CREATE**
   - `normalized_perplexity_comparison.png` ← **CREATE**
   - `normalized_complexity_ratios.png` ← **CREATE**

**Current Selected Global Figures (12):**
1. complexity_performance_by_direction.png ✓
2. complexity_ratios.png ✓ (check if normalized)
3. correlation_significance_summary.png ✓
4. cross_entropy_comparison.png ✓ (verify normalization)
5. directional_asymmetry.png ✓
6. directional_complexity_comparison.png ✓
7. entropy_comparison.png ✓ (verify normalization)
8. kl_divergence_comparison.png ✓ (verify normalization)
9. pattern_diversity_comparison.png ✓
10. similarity_heatmaps.png ✓
11. task3_feature_complexity.png ✓
12. ttr_comparison.png ✓ (verify normalization)

**Action Item:** Verify all have normalized counterparts or versions

---

## Implementation Action Plan

### Phase 1: Directory Structure Setup

```bash
# Task 1
mkdir -p /mnt/d/.../Part_1.../latex-selected/tables/

# Task 2
mkdir -p /mnt/d/.../Part_2.../latex/latex-selected/tables/
mkdir -p /mnt/d/.../Part_2.../latex/latex-selected/figures/global/

# Task 3
mkdir -p /mnt/d/.../Part_3.../latex-selected/tables/
```

### Phase 2: Task 1 - Tables (5 CRITICAL)

```bash
cd /mnt/d/.../Part_1.../

# PRIORITY 1: Main paper tables
cp latex-comprehensive/tables/global_comprehensive_analysis_global.tex latex-selected/tables/
cp latex-comprehensive/tables/cross_newspaper_comparison.tex latex-selected/tables/
cp latex-comprehensive/tables/global_statistical_summary_features.tex latex-selected/tables/
cp latex-comprehensive/tables/global_bidirectional_cross_entropy_analysis_global_metrics.tex latex-selected/tables/
cp latex-comprehensive/tables/global_feature_value_pair_analysis_top_pairs.tex latex-selected/tables/
```

### Phase 3: Task 1 - Figures (10-13 CRITICAL)

```bash
cd /mnt/d/.../Part_1.../

# PRIORITY 1: Cross-newspaper comparisons
cp latex-comprehensive/figures/global/cross_newspaper_event_counts.png latex-selected/global/
cp latex-comprehensive/figures/global/cross_newspaper_top_features_comparison.png latex-selected/global/
cp latex-comprehensive/figures/global/cross_newspaper_parse_types.png latex-selected/global/

# PRIORITY 2: Statistical visualizations
# Check if global version exists, otherwise adapt from per-newspaper
# cp latex-comprehensive/figures/global/statistical_significance_heatmap.png latex-selected/global/

# PRIORITY 3: Information-theoretic
# Check if aggregated global versions exist
# cp latex-comprehensive/figures/global/global_cross_entropy_metrics.png latex-selected/global/
# cp latex-comprehensive/figures/global/information_asymmetry_analysis.png latex-selected/global/

# May need to generate aggregated versions from per-newspaper data
```

### Phase 4: Task 2 - Tables (3 CRITICAL + 6 HIGH)

```bash
cd /mnt/d/.../Part_2.../latex/

# PRIORITY 1: CRITICAL tables
cp latex-comprehensive/tables/integrated_transformation_comparison.tex latex-selected/tables/
cp latex-comprehensive/tables/overall_morphological_statistics.tex latex-selected/tables/
cp latex-comprehensive/tables/morphological_systematicity.tex latex-selected/tables/

# PRIORITY 2: POS-specific
cp latex-comprehensive/tables/noun_morphology_comparison.tex latex-selected/tables/
cp latex-comprehensive/tables/verb_morphology_comparison.tex latex-selected/tables/
cp latex-comprehensive/tables/morphological_features_summary.tex latex-selected/tables/
```

### Phase 5: Task 2 - Figures (Restructure + Add 13)

```bash
cd /mnt/d/.../Part_2.../latex/

# CRITICAL: Move existing root figures to global/
mkdir -p latex-selected/figures/global/
mv latex-selected/figures/accuracy_coverage.png latex-selected/figures/global/
mv latex-selected/figures/coverage_curve.png latex-selected/figures/global/
mv latex-selected/figures/rules_by_feature.png latex-selected/figures/global/
mv latex-selected/figures/top_transformation_pairs.png latex-selected/figures/global/
mv latex-selected/figures/transformation_entropy.png latex-selected/figures/global/
mv latex-selected/figures/transformation_patterns_overview.png latex-selected/figures/global/
mv latex-selected/figures/top_transformations_per_feature_fig1.png latex-selected/figures/global/
mv latex-selected/figures/top_transformations_per_feature_fig2.png latex-selected/figures/global/

# Add missing global figures
cp latex-comprehensive/figures/global/task2_coverage_curve.png latex-selected/figures/global/
cp latex-comprehensive/figures/global/task2_newspaper_comparison.png latex-selected/figures/global/
cp latex-comprehensive/figures/global/task2_morphological_rules.png latex-selected/figures/global/
cp latex-comprehensive/figures/global/task2_punctuation_rules.png latex-selected/figures/global/
cp latex-comprehensive/figures/global/task2_rule_hierarchy.png latex-selected/figures/global/
cp latex-comprehensive/figures/global/integrated_comparison.png latex-selected/figures/global/
cp latex-comprehensive/figures/global/morphological_features_heatmap.png latex-selected/figures/global/
cp latex-comprehensive/figures/global/morphological_impact_comparison.png latex-selected/figures/global/
cp latex-comprehensive/figures/global/noun_morphology_comparison.png latex-selected/figures/global/
cp latex-comprehensive/figures/global/verb_morphology_comparison.png latex-selected/figures/global/
cp latex-comprehensive/figures/global/overall_morphological_statistics.png latex-selected/figures/global/
cp latex-comprehensive/figures/global/transformation_directionality.png latex-selected/figures/global/
cp latex-comprehensive/figures/global/cross_newspaper_feature_comparison.png latex-selected/figures/global/
```

### Phase 6: Task 3 - Tables (3 CRITICAL + 6 HIGH)

```bash
cd /mnt/d/.../Part_3.../

# PRIORITY 1: CRITICAL tables
cp latex-comprehensive/tables/bidirectional_metrics.tex latex-selected/tables/
cp latex-comprehensive/tables/directional_perplexity_analysis.tex latex-selected/tables/
cp latex-comprehensive/tables/cross_newspaper_comparison.tex latex-selected/tables/

# PRIORITY 2: Correlation & validation
cp latex-comprehensive/tables/correlation_results.tex latex-selected/tables/
cp latex-comprehensive/tables/inter_metric_correlations.tex latex-selected/tables/
cp latex-comprehensive/tables/ratio_correlations.tex latex-selected/tables/

# PRIORITY 3: Detailed analysis (for appendix)
cp latex-comprehensive/tables/perplexity_complete_analysis.tex latex-selected/tables/
cp latex-comprehensive/tables/merged_mt_perplexity_data.tex latex-selected/tables/
cp latex-comprehensive/tables/event_level_perplexity.tex latex-selected/tables/
```

### Phase 7: Task 3 - Verify Normalization

```bash
cd /mnt/d/.../Part_3.../

# ACTION: Manually verify each figure for normalization
# Check figure titles, axis labels, captions in comprehensive versions

# IF MISSING, generate normalized versions:
# - Use analysis scripts to create normalized variants
# - Update figure generation code to produce both raw and normalized
# - Priority: entropy, cross-entropy, perplexity, complexity ratios

# Verify these specifically:
# - ttr_comparison.png (Type-Token Ratio is inherently normalized)
# - entropy_comparison.png (bits per token vs total bits?)
# - cross_entropy_comparison.png (normalized by sequence length?)
# - kl_divergence_comparison.png (bits per token?)
```

---

## Priority Summary for Immediate Action

### HIGHEST PRIORITY (Do First)

**Task 2:**
1. Create `latex-selected/figures/global/` directory
2. Move 8 root figures to global/
3. Copy `integrated_transformation_comparison.tex` table
4. Copy 5 critical global figures (task2_*.png)

**Task 1:**
1. Create `latex-selected/tables/` directory
2. Copy 5 PRIORITY 1 tables
3. Copy 3-5 missing critical global figures

**Task 3:**
1. Create `latex-selected/tables/` directory
2. Copy 3 CRITICAL tables (bidirectional_metrics, directional_perplexity, cross_newspaper)
3. Verify normalization of all existing figures
4. Generate normalized variants if missing

### HIGH PRIORITY (Do Second)

**Task 1:**
- Add 5-8 more global figures (information-theoretic, statistical)
- Add 4 PRIORITY 2 appendix tables

**Task 2:**
- Copy 8 more global figures (morphological analysis, POS-specific)
- Add 6 PRIORITY 2 tables (POS-specific, value pairs)

**Task 3:**
- Add 3 correlation/validation tables
- Create normalized tables if missing
- Generate normalized figure variants

### MEDIUM PRIORITY (Do Third)

**All Tasks:**
- Appendix tables (detailed breakdowns)
- Additional supporting figures
- Per-newspaper detailed tables (if space allows)

---

## Page Budget Allocation (8 pages main + appendices)

### Main Paper (8 pages target)

**Task 1:**
- Tables: 5 in main (1.5 pages)
- Figures: 10-12 global (2 pages)
- Per-newspaper figures: Select best 2-3 per newspaper (1 page)
- **Total: ~4.5 pages for tables/figures**

**Task 2:**
- Tables: 3 in main (0.75 pages)
- Figures: 8-10 global (1.5 pages)
- Per-newspaper figures: Select best 2 per newspaper (0.5 pages)
- **Total: ~2.75 pages for tables/figures**

**Task 3:**
- Tables: 3-4 in main (1 page)
- Figures: 10-12 global (2 pages) + normalized variants
- Per-newspaper figures: 2-3 per newspaper (0.75 pages)
- **Total: ~3.75 pages for tables/figures**

### Appendices (Unlimited but reasonable)

**Task 1:**
- 4 detailed tables
- Additional per-feature breakdowns
- TED algorithm comparisons

**Task 2:**
- 6 detailed tables
- Progressive coverage per newspaper
- Value pair analysis

**Task 3:**
- 6 detailed tables
- Complete perplexity analysis
- Event-level breakdowns

---

## Verification Checklist

### Before Paper Submission

**Task 1:**
- [ ] All 5 PRIORITY 1 tables copied
- [ ] At least 10 global figures in selected
- [ ] cross_newspaper_normalized_comparison.png present
- [ ] Information-theoretic figures present
- [ ] Statistical validation figures present

**Task 2:**
- [ ] `latex-selected/figures/global/` directory created
- [ ] All root figures moved to global/
- [ ] integrated_transformation_comparison.tex copied
- [ ] task2_*.png figures (5) copied
- [ ] Morphological analysis figures copied

**Task 3:**
- [ ] bidirectional_metrics.tex copied
- [ ] directional_perplexity_analysis.tex copied
- [ ] ALL figures verified for normalization
- [ ] Normalized variants created if missing
- [ ] Complexity ratios table includes normalized values
- [ ] Cross-newspaper comparison uses normalized metrics

### Cross-Task Consistency

- [ ] All three tasks have tables/ subdirectories
- [ ] All three tasks have consistent global/ figure organization
- [ ] Normalized values used for all cross-newspaper comparisons
- [ ] Figure/table numbering is consistent
- [ ] Cross-references work across tasks
- [ ] Captions explicitly state "normalized" where applicable

---

## Final Recommendations

### For 8-Page Long Papers with Appendices:

1. **Main paper should focus on:**
   - Global/cross-newspaper summary tables (3-5 per task)
   - Normalized comparisons (critical for Task 3)
   - Key summary figures (10-12 per task)
   - Statistical validation

2. **Appendices should contain:**
   - Detailed per-newspaper breakdowns
   - Per-feature analysis
   - Complete statistical tables
   - Methodological details (TED algorithms, rule extraction)

3. **Normalization is CRITICAL for:**
   - Task 3 complexity/similarity metrics (per-token, per-char, vocab-normalized)
   - Task 1 cross-newspaper feature frequency (per 1000 tokens)
   - Task 2 rule coverage (percentage, not raw counts)

4. **Directory structure must be consistent:**
   ```
   latex-selected/
   ├── tables/           # All summary tables
   ├── figures/
   │   ├── global/       # Cross-newspaper summaries
   │   ├── Hindustan-Times/
   │   ├── The-Hindu/
   │   └── Times-of-India/
   └── main.tex
   ```

---

## Document End

**Total Recommended Additions:**
- **Task 1:** 9 tables + 10-13 figures
- **Task 2:** 9 tables + 13 figures + directory restructure
- **Task 3:** 9-11 tables + verify/create normalized variants

**Most Critical Actions:**
1. Task 2: Create global/ directory and reorganize
2. Task 3: Verify normalization, create missing variants
3. Task 1: Add cross-newspaper comparison figures
4. All tasks: Copy PRIORITY 1 tables (9 total)

**Timeline Estimate:**
- Phase 1-3 (Task 1): 2-3 hours
- Phase 4-5 (Task 2): 3-4 hours (includes restructure)
- Phase 6-7 (Task 3): 2-3 hours + normalization verification
- **Total: 7-10 hours**
