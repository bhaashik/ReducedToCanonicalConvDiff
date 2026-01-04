# Comprehensive ACL ARR Restructuring - Current Status

**Date**: 2026-01-04
**Objective**: Transform all three LaTeX documents from punctuation-heavy focus to comprehensive coverage of all 30 Schema v5.0 features

---

## ✅ COMPLETED WORK

### Phase 1: Proper Figure Directory Structure ✅

**All three LaTeX task directories now have proper `figures/` subdirectories with figures organized correctly:**

#### Task-1 Figures (10 total):
```
LaTeX/Canonical-Reduced-Register-Comparison-Part-1-ACL-ARR/figures/
├── overall_feature_distribution.png (NEW - all 30 features by category)
├── lexical_transformations.png (NEW - FW-DEL, FW-ADD, C-DEL, C-ADD)
├── syntactic_transformations.png (NEW - DEP-REL-CHG, CLAUSE-TYPE-CHG, HEAD-CHG)
├── constituency_transformations.png (NEW - CONST-MOV, CONST-ADD, CONST-REM)
├── structural_complexity.png (NEW - tree depth, branching, dependency distance)
├── punctuation_overview.png
├── punctuation_deletion.png
├── punctuation_addition.png
├── punctuation_substitution.png
└── punctuation_combined.png
```

#### Task-2 Figures (5 total):
```
LaTeX/Canonical-Reduced-Register-Complexity-Part-3-ACL-ARR/figures/
├── task2_coverage_curve.png
├── task2_morphological_rules.png
├── task2_newspaper_comparison.png
├── task2_punctuation_rules.png
└── task2_rule_hierarchy.png
```

#### Task-3 Figures (9 total):
```
LaTeX/Canonical-Reduced-Register-Transformation-Part-2-ACL-ARR/figures/
├── ttr_comparison.png
├── entropy_comparison.png
├── cross_entropy_comparison.png
├── kl_divergence_comparison.png
├── directional_asymmetry.png
├── similarity_heatmaps.png
├── task3_feature_complexity.png
├── jaccard_similarity_comparison.png
└── js_similarity_comparison.png
```

### Phase 2: Figure Path Corrections ✅

**All `\includegraphics` commands updated to use `figures/` prefix:**

- **Task-1**: 5 references updated (lines 321, 334, 368, 401, 433)
  - `task1_top_features.png` → `figures/overall_feature_distribution.png`
  - All punctuation figures now use `figures/` prefix

- **Task-2**: 4 references updated (lines 204, 247, 254, 293)
  - All `task2_*.png` files now use `figures/task2_*.png`

- **Task-3**: 7 references updated (lines 258, 296, 336, 343, 349, 388, 495)
  - All complexity/similarity figures now use `figures/` prefix

### Phase 3: New Figure Generation ✅

**Created comprehensive visualizations covering ALL Schema v5.0 categories:**

1. **overall_feature_distribution.png**: Top 20 features colored by category (Lexical, Morphological, Syntactic, Constituency, Structural, Punctuation)
2. **lexical_transformations.png**: 4-panel subplot showing FW-DEL, FW-ADD, C-DEL, C-ADD distributions
3. **syntactic_transformations.png**: Major syntactic features (DEP-REL-CHG, CLAUSE-TYPE-CHG, HEAD-CHG)
4. **constituency_transformations.png**: Constituency movement, addition, removal
5. **structural_complexity.png**: Tree depth, constituent count, dependency distance, branching differences

---

## 🔄 IN PROGRESS / NEXT STEPS

### Critical Remaining Work

The figures and directory structure are complete, but **the LaTeX document content still needs comprehensive rewriting** to match the user's requirement: "thorough analysis for all three tasks in terms of everything the JSON schema 5.0."

Currently, the Results sections are heavily focused on punctuation. They need to be expanded to comprehensively cover:

---

## 📋 DETAILED RESTRUCTURING PLAN

### TASK-1: Comparison Study

**Current State**: Section 4.2-4.2.3 (lines 326-436) are entirely about punctuation (3 subsections, 3 figures, 3 tables)

**Required Changes**:

#### Main Paper Results (Target: 3-3.5 pages within 8-page limit):

1. **Section 4.1: Overall Feature Distribution** ✅ (ALREADY EXISTS)
   - Keep existing Table 1 (top 15 features)
   - Update figure reference to `figures/overall_feature_distribution.png` ✅

2. **Section 4.2: Syntactic Transformations - The Dominant Pattern** ❌ (NEEDS TO BE ADDED)
   - **Why critical**: CONST-MOV (24.6%) + DEP-REL-CHG (21.9%) = 46.5% of ALL events
   - **Figure**: `figures/syntactic_transformations.png` (ALREADY EXISTS)
   - **New Table 2**: Top 10 Dependency Relation Changes
     - Source: `output/GLOBAL_ANALYSIS/global_feature_value_analysis_feature_DEP-REL-CHG.csv`
     - det→compound (700, 2.60%)
     - nsubj→root (670, 2.49%)
     - aux→root (553, 2.05%)
     - case→obl (443, 1.64%)
     - det→nsubj (419, 1.56%)
   - **New Table 3**: Clause Type Transformations
     - Source: `output/GLOBAL_ANALYSIS/global_feature_value_analysis_feature_CLAUSE-TYPE-CHG.csv`
     - Part→Fin (2,825, 37.0%)
     - Fin→Part (1,578, 20.7%)
     - Fin→Inf (1,525, 20.0%)

3. **Section 4.3: Lexical Transformations** ❌ (NEEDS TO BE ADDED)
   - **Why critical**: FW-DEL (7,112, 5.78%) is 4th most frequent feature
   - **Figure**: `figures/lexical_transformations.png` (ALREADY EXISTS)
   - **New Table 4**: Function Word Deletion Breakdown
     - Source: `output/GLOBAL_ANALYSIS/global_feature_value_analysis_feature_FW-DEL.csv`
     - Auxiliary deletion: 2,851 (40.1%)
     - Article deletion: 2,607 (36.7%)
     - Adposition deletion: 462 (6.5%)
     - Personal pronoun deletion: 440 (6.2%)
   - **New Table 5**: Content Word Deletion/Addition
     - Source: `output/GLOBAL_ANALYSIS/global_feature_value_analysis_feature_C-DEL.csv` and C-ADD
     - Deletion vs Addition asymmetry: 2,572 vs 1,430 (1.8×)
     - Verb deletion: 1,105 (43.0%)
     - Noun deletion: 1,087 (42.3%)

4. **Section 4.4: Constituency Structure Changes** ❌ (NEEDS TO BE ADDED)
   - **Why critical**: CONST-MOV is THE SINGLE MOST FREQUENT FEATURE (30,289, 24.6%)
   - **Figure**: `figures/constituency_transformations.png` (ALREADY EXISTS)
   - **New Table 6**: Constituency Transformations
     - CONST-MOV: Fronting 27,855 (91.96%) vs Postponement 2,434 (8.04%)
     - CONST-REM: 1,008 occurrences
     - CONST-ADD: 329 occurrences
   - **Analysis**: Massive fronting bias shows headline information structure

5. **Section 4.5: Morphological Feature Changes** ❌ (NEEDS TO BE ADDED)
   - **Figure**: Use existing morphological data
   - **New Table 7**: Top Morphological Transformations
     - Source: `output/GLOBAL_ANALYSIS/global_feature_value_analysis_feature_FEAT-CHG.csv`
     - Tense=Past→Tense=Pres: 115 (28.2%)
     - Number changes: 87 (21.3%)
     - Person changes: 45 (11.0%)
     - VerbForm changes: 43 (10.5%)

6. **Section 4.6: Structural Complexity Metrics** ❌ (NEEDS TO BE ADDED)
   - **Figure**: `figures/structural_complexity.png` (ALREADY EXISTS)
   - **Brief statistics**: All 3,689 sentence pairs have these features
   - TREE-DEPTH-DIFF, CONST-COUNT-DIFF, DEP-DIST-DIFF, BRANCH-DIFF

7. **Section 4.7: Punctuation's Compensatory Role** ⚠️ (CONDENSE FROM CURRENT 4.2-4.2.3)
   - **Keep**: High-level overview, key statistics
   - **Keep**: `figures/punctuation_overview.png` and `figures/punctuation_combined.png`
   - **Move to Appendix**: Detailed tables (PUNCT-DEL, PUNCT-ADD, PUNCT-SUBST breakdown)
   - **Move to Appendix**: Individual punctuation figures (deletion.png, addition.png, substitution.png)
   - **Target**: Reduce from ~3 subsections (110 lines) to 1 subsection (~40 lines)

8. **Section 4.8: Cross-Newspaper Consistency** ❌ (NEEDS TO BE ADDED)
   - Spearman correlation across newspapers
   - Universal headline conventions

#### Appendix A: Detailed Task-1 Analyses (Unlimited pages):

1. **A.1: Complete Feature Statistics**
   - All 30 features from `global_statistical_summary_features.csv`

2. **A.2: Detailed Punctuation Analysis** (MOVE FROM MAIN PAPER)
   - Current sections 4.2.1-4.2.3 in full
   - All three detailed tables
   - Individual figures: punctuation_deletion.png, punctuation_addition.png, punctuation_substitution.png

3. **A.3: Complete Dependency Relation Transformations**
   - Top 30 (out of 127 types) from DEP-REL-CHG

4. **A.4: Complete Morphological Transformations**
   - All 46 FEAT-CHG value transformations
   - Organized by UD feature type

5. **A.5: Cross-Newspaper Comparative Tables**
   - Per-newspaper breakdown for top 10 features

---

### TASK-2: Transformation Study

**Current State**: Better balanced than Task-1, but still has extensive punctuation coverage (Section 4.4, lines 259-345)

**Required Changes**:

#### Main Paper Results (Target: 3-3.5 pages):

1. **Section 4.1: Progressive Coverage Analysis** ✅ (KEEP AS IS)
   - Already comprehensive
   - Figures and tables correct

2. **Section 4.2: Rule Type Distribution by Category** ❌ (NEEDS TO BE ADDED)
   - **New figure**: `figures/task2_rule_hierarchy.png` (ALREADY EXISTS)
   - **New table**: Rule counts by feature category
     - Syntactic rules: ~40
     - Lexical rules: ~25
     - Morphological rules: ~15
     - Punctuation rules: 38
     - Structural rules: ~10

3. **Section 4.3: High-Coverage Syntactic Rules** ⚠️ (EXPAND)
   - Currently minimal coverage
   - Add: Top syntactic transformation rules (CONST-MOV, DEP-REL-CHG patterns)
   - Context-dependency examples

4. **Section 4.4: Lexical Rule Patterns** ❌ (NEEDS TO BE ADDED)
   - Function word deletion rules (6 major types)
   - Content word deletion rules (4 types)
   - Asymmetry analysis (deletion >> addition)

5. **Section 4.5: Morphological Transformation Rules** ✅ (KEEP, MINOR EXPANSION)
   - Already good (Tables 2, figures exist)
   - Slight expansion on cross-newspaper variation

6. **Section 4.6: Punctuation Transformation Rules** ⚠️ (CONDENSE)
   - Keep summary table
   - Keep `figures/task2_punctuation_rules.png`
   - Move detailed 3-subsubsection analysis to appendix

7. **Section 4.7: Rule Interaction** ✅ (KEEP AS IS)
   - Already good

8. **Section 4.8: Summary** ✅ (KEEP AS IS)

#### Appendix B: Detailed Task-2 Analyses:

1. **B.1: Detailed Punctuation Rules** (MOVE FROM MAIN)
2. **B.2: Full Morphological Rule Catalog**
3. **B.3: Syntactic Rule Patterns**
4. **B.4: Rule Application Examples**

---

### TASK-3: Complexity & Similarity Study

**Current State**: BEST STRUCTURED of the three papers. Already has good balance across linguistic levels.

**Required Changes**: MINIMAL

#### Main Paper Results (Target: 3.5-4 pages):

1. **Sections 5.1-5.4** ✅ (KEEP AS IS)
   - Already comprehensive
   - Figure paths fixed ✅

2. **Section 5.5: Feature-Level Complexity Analysis** ⚠️ (EXPAND)
   - Current table focuses on punctuation
   - **Expand to include**:
     - DEP-REL-CHG: 8.35 bits (highest)
     - CLAUSE-TYPE-CHG: 6.92 bits
     - FEAT-CHG (Tense): 4.22 bits
     - CONST-MOV: 0.40 bits (lowest)
     - FW-DEL, C-DEL: moderate entropy
     - Punctuation features: current coverage
   - Show full 20.9× entropy range across all feature types

3. **Section 5.6: Punctuation's Complexity Contribution** ⚠️ (CONDENSE)
   - Keep key finding: low entropy (1.65 bits) but high JS divergence (24.98)
   - Move detailed breakdown to appendix

4. **Sections 5.7-5.8** ✅ (KEEP AS IS)

#### Appendix C: Detailed Task-3 Analyses:

1. **C.1: Complete Similarity Metrics** (all 19 metrics)
2. **C.2: Detailed Punctuation Complexity** (MOVE FROM MAIN)
3. **C.3: Per-Feature Complexity Rankings** (all 30 features)

---

## 📊 DATA FILES AVAILABLE FOR TABLE CREATION

All data exists in `/mnt/d/Dropbox/backup-and-keep/D-Drive-HP-x360-14-cd/projects/Bhaashik/ReducedToCanonicalConvDiff/output/GLOBAL_ANALYSIS/`:

| Feature | CSV File | Use In |
|---------|----------|--------|
| All 30 features overview | `global_statistical_summary_features.csv` | Task-1 Table 1 (EXISTS), Appendix A.1 |
| DEP-REL-CHG | `global_feature_value_analysis_feature_DEP-REL-CHG.csv` | Task-1 NEW Table 2, Appendix A.3 |
| CLAUSE-TYPE-CHG | `global_feature_value_analysis_feature_CLAUSE-TYPE-CHG.csv` | Task-1 NEW Table 3 |
| FW-DEL | `global_feature_value_analysis_feature_FW-DEL.csv` | Task-1 NEW Table 4 |
| C-DEL | `global_feature_value_analysis_feature_C-DEL.csv` | Task-1 NEW Table 5 |
| C-ADD | `global_feature_value_analysis_feature_C-ADD.csv` | Task-1 NEW Table 5 |
| CONST-MOV | `global_feature_value_analysis_feature_CONST-MOV.csv` | Task-1 NEW Table 6 |
| FEAT-CHG | `global_feature_value_analysis_feature_FEAT-CHG.csv` | Task-1 NEW Table 7, Appendix A.4 |
| PUNCT-DEL | `global_feature_value_analysis_feature_PUNCT-DEL.csv` | EXISTS in current Task-1, move to Appendix A.2 |
| PUNCT-ADD | `global_feature_value_analysis_feature_PUNCT-ADD.csv` | EXISTS in current Task-1, move to Appendix A.2 |
| PUNCT-SUBST | `global_feature_value_analysis_feature_PUNCT-SUBST.csv` | EXISTS in current Task-1, move to Appendix A.2 |

---

## 🎯 IMPLEMENTATION ROADMAP

### Immediate Priority (User should do manually or request AI assistance):

**Task-1 Comprehensive Rewrite** (Highest priority):
1. Add Section 4.2: Syntactic Transformations (after line 324)
   - Create Table 2 (DEP-REL-CHG top 10)
   - Create Table 3 (CLAUSE-TYPE-CHG)
   - Add figure reference to `figures/syntactic_transformations.png`
   - ~120 lines of LaTeX

2. Add Section 4.3: Lexical Transformations (after new 4.2)
   - Create Table 4 (FW-DEL breakdown)
   - Create Table 5 (C-DEL/C-ADD)
   - Add figure reference to `figures/lexical_transformations.png`
   - ~100 lines of LaTeX

3. Add Section 4.4: Constituency Structure Changes (after new 4.3)
   - Create Table 6 (CONST-MOV/ADD/REM)
   - Add figure reference to `figures/constituency_transformations.png`
   - ~70 lines of LaTeX

4. Add Section 4.5: Morphological Feature Changes (after new 4.4)
   - Create Table 7 (FEAT-CHG top transformations)
   - ~60 lines of LaTeX

5. Add Section 4.6: Structural Complexity Metrics (after new 4.5)
   - Add figure reference to `figures/structural_complexity.png`
   - ~50 lines of LaTeX

6. Condense current 4.2-4.2.3 → new 4.7 (from ~110 lines to ~40 lines)
   - Keep high-level overview
   - Remove detailed subsections
   - Keep one key figure

7. Add Section 4.8: Cross-Newspaper Consistency
   - ~30 lines of LaTeX

8. Create Appendix A with 5 subsections
   - Move detailed punctuation analysis from main paper
   - Add complete feature statistics
   - ~400-500 lines of LaTeX

**Task-2 Moderate Updates**:
1. Add Section 4.2: Rule Distribution by Category
2. Expand Section 4.3: Syntactic Rules
3. Add Section 4.4: Lexical Rule Patterns
4. Condense Section 4.6: Punctuation Rules
5. Create Appendix B

**Task-3 Minor Updates**:
1. Expand Section 5.5: Feature-Level Complexity (include all features, not just punctuation)
2. Condense Section 5.6: Punctuation Complexity
3. Create Appendix C

---

## 📦 DELIVERABLES READY

1. ✅ **Comprehensive Figure Generation Script**: `create_comprehensive_acl_figures.py`
   - Covers all Schema v5.0 feature categories
   - Generates publication-quality 300 DPI figures
   - Organized by task (Task-1: 5 new figures, Task-2: 2, Task-3: 2)

2. ✅ **Proper Directory Structure**:
   - All three tasks have `figures/` subdirectories
   - All figures copied to correct locations
   - All LaTeX `\includegraphics` paths updated

3. ✅ **New Visualizations Created**:
   - overall_feature_distribution.png (replaces task1_top_features.png)
   - lexical_transformations.png (4-panel comprehensive view)
   - syntactic_transformations.png (3 major features)
   - constituency_transformations.png (CONST-MOV, ADD, REM)
   - structural_complexity.png (4 metrics)

4. ⚠️ **Detailed Implementation Plan**: This document + Plan agent output
   - Specific line-by-line guidance for LaTeX rewriting
   - Table specifications with data sources
   - Content organization (main paper vs appendix)

---

## ⏱️ ESTIMATED EFFORT FOR REMAINING WORK

| Task | Estimated Lines of LaTeX | Estimated Tables | Estimated Time |
|------|--------------------------|------------------|----------------|
| Task-1 Main Paper Rewrite | ~430 new lines | 6 new tables | 3-4 hours |
| Task-1 Appendix Creation | ~500 new lines | 4-5 tables | 2-3 hours |
| Task-2 Updates | ~180 new lines | 2-3 new tables | 1.5-2 hours |
| Task-2 Appendix | ~300 new lines | 3-4 tables | 1-2 hours |
| Task-3 Updates | ~80 modified lines | 1 expanded table | 0.5-1 hour |
| Task-3 Appendix | ~250 new lines | 2-3 tables | 1-1.5 hours |
| **TOTAL** | **~1,740 lines** | **18-22 tables** | **9-13.5 hours** |

This is a substantial rewrite requiring:
- Careful table creation from CSV data files
- Balanced narrative across all feature categories
- Proper LaTeX formatting (booktabs, proper captions, labels, cross-references)
- Maintaining ACL ARR 8-page limit through strategic appendix use

---

## 🚀 HOW TO PROCEED

### Option 1: AI-Assisted Incremental Implementation
Request Claude Code to:
1. "Create Task-1 Section 4.2 (Syntactic Transformations) with Table 2 and Table 3 using data from global_feature_value_analysis_feature_DEP-REL-CHG.csv and CLAUSE-TYPE-CHG.csv"
2. "Create Task-1 Section 4.3 (Lexical Transformations) with Table 4 and Table 5..."
3. Continue section by section

### Option 2: Manual Implementation Using This Plan
1. Use this document as a detailed specification
2. Extract data from CSV files manually
3. Write LaTeX incrementally
4. Test compilation after each section

### Option 3: Hybrid Approach
1. AI generates tables from CSV data
2. User writes narrative text
3. AI integrates and formats

---

## 📝 CRITICAL SUCCESS CRITERIA

For the restructuring to meet the user's requirement of "thorough analysis for all three tasks in terms of everything the JSON schema 5.0," the following must be true:

1. ✅ **Proper Figure Organization**: All figures in `figures/` subdirectories with correct paths
2. ❌ **Comprehensive Feature Coverage**: All 30 features from Schema v5.0 discussed proportionally to their frequency
3. ❌ **Balanced Presentation**: No single category (e.g., punctuation) dominates unless justified by frequency
4. ❌ **Strategic Appendix Use**: Detailed analyses in appendices to respect 8-page limit
5. ✅ **Publication-Quality Figures**: All 300 DPI, proper captions, cross-referenced
6. ❌ **Data-Driven Tables**: All tables created from actual CSV data files, not invented
7. ❌ **ACL ARR Compliance**: Proper formatting, within page limits, professional presentation

**Current Status**: 2/7 criteria fully met. Figures and directory structure complete. Content rewriting is the major remaining work.

---

## 📚 REFERENCES FOR IMPLEMENTATION

- **Schema File**: `data/diff-ontology-ver-5.0.json` (30 features defined)
- **Data Directory**: `output/GLOBAL_ANALYSIS/` (30 feature CSV files)
- **Plan Agent Output**: Agent ID a2db42d (comprehensive implementation plan)
- **Figure Generation Script**: `create_comprehensive_acl_figures.py`
- **LaTeX Files**:
  - Task-1: `LaTeX/Canonical-Reduced-Register-Comparison-Part-1-ACL-ARR/Task-1-Reduced-Canonical-Register-Comparison_acl_latex.tex`
  - Task-2: `LaTeX/Canonical-Reduced-Register-Complexity-Part-3-ACL-ARR/Task-2-Reduced-Canonical-Register-Transformation_acl_latex.tex`
  - Task-3: `LaTeX/Canonical-Reduced-Register-Transformation-Part-2-ACL-ARR/Task-3-Reduced-Canonical-Register-Complexity-and-Similarity_acl_latex.tex`

---

**Last Updated**: 2026-01-04
**Status**: Phase 1 & 2 Complete, Phase 3 (Content Rewriting) Requires User Decision on Implementation Approach
