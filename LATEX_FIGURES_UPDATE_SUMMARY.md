# LaTeX Files and Figures Update Summary

**Date**: 2026-01-03
**Update Type**: Three-Level Data Organization Integration

---

## Overview

Updated LaTeX documents and created publication-quality figures to incorporate the three-level data hierarchy (Features, Feature-Value Pairs, Value Statistics).

---

## Files Updated

### 1. Task-1 LaTeX Document

**File**: `LaTeX/Task-1-Canonical_Reduced_Register_Comparison_ACL_ARR/task1_register_comparison_v5_context.tex`

**Updates**:
- ✅ Added new section "Three-Level Data Organization" (Section 4.2)
- ✅ Integrated 5 new figures with captions
- ✅ Added 3 new tables with real data
- ✅ Cross-referenced all levels with explanatory text

**New Content** (lines 307-452):
- Level 1: Feature-Level Analysis (Table 3, Figure 2)
- Level 2: Feature-Value Pair Analysis (Table 4, Figure 3)
- Level 3: Value Distribution Statistics (Table 5, Figure 4)
- Cross-Level Integration (Figures 1 and 5)

**Line Count**: ~145 new lines of LaTeX content

---

## Figures Created

### Location
- **Primary**: `LaTeX/figures/` (5 PNG files)
- **Task-1**: `LaTeX/Task-1-Canonical_Reduced_Register_Comparison_ACL_ARR/` (copied)
- **Source**: `output/three_level_visualizations/` (original output)

### Figure Details

#### Figure 1: `three_level_hierarchy.png`
- **Size**: 347 KB, 4200×3000 pixels (300 DPI)
- **Purpose**: Conceptual diagram of three-level hierarchy
- **Content**:
  - Level 1 boxes showing aggregate features
  - Level 2 boxes showing specific transformations
  - Level 3 boxes showing statistical properties
  - Connecting arrows with labels
  - Example data for each level
- **LaTeX Reference**: `\ref{fig:three-level-hierarchy}`

#### Figure 2: `level1_feature_frequency.png`
- **Size**: 304 KB, 3600×2400 pixels (300 DPI)
- **Purpose**: Feature frequency distribution (Level 1)
- **Content**:
  - Horizontal bar chart of top 15 features
  - Event counts with percentages
  - Color-coded bars
  - Value labels on bars
- **LaTeX Reference**: `\ref{fig:level1-frequency}`

#### Figure 3: `level2_featchange_transformations.png`
- **Size**: 405 KB, 4200×2400 pixels (300 DPI)
- **Purpose**: Feature-value pairs for FEAT-CHG (Level 2)
- **Content**:
  - Horizontal bar chart of top 15 morphological transformations
  - Transformation labels (canonical→headline)
  - Count and percentage labels
  - Color-coded bars (Paired colormap)
- **LaTeX Reference**: `\ref{fig:level2-featchange}`

#### Figure 4: `level3_entropy_diversity.png`
- **Size**: 302 KB, 4800×2100 pixels (300 DPI)
- **Purpose**: Entropy and diversity metrics (Level 3)
- **Content**:
  - Two-panel layout (entropy left, diversity right)
  - Top 15 features sorted by entropy
  - Horizontal bar charts with value labels
  - Gradient coloring (viridis and plasma)
- **LaTeX Reference**: `\ref{fig:level3-entropy-diversity}`

#### Figure 5: `cross_level_comparison.png`
- **Size**: 362 KB, 4200×3600 pixels (300 DPI)
- **Purpose**: Cross-level comparison for FEAT-CHG
- **Content**:
  - Three-panel vertical layout
  - Level 1: Single bar showing 408 events
  - Level 2: Horizontal bars showing top transformations
  - Level 3: Bar chart of statistical properties
  - Unified color scheme
- **LaTeX Reference**: `\ref{fig:cross-level-comparison}`

---

## Tables Added

### Table 3: Level 1 - Top Features
**LaTeX Label**: `\ref{tab:level1-top-features}`

| Feature ID | Feature Name | Count | % |
|-----------|--------------|-------|---|
| CONST-MOV | Constituent Movement | 30,289 | 24.62 |
| DEP-REL-CHG | Dependency Relation Change | 26,935 | 21.89 |
| ... | ... | ... | ... |

**Total Rows**: 10 top features + 1 remaining + 1 total = 12 rows

### Table 4: Level 2 - FEAT-CHG Transformations
**LaTeX Label**: `\ref{tab:level2-featchange}`

| Canonical Value | Headline Value | Count | % |
|----------------|----------------|-------|---|
| Tense=Past | Tense=Pres | 115 | 28.19 |
| Number=ABSENT | Number=Sing | 26 | 6.37 |
| ... | ... | ... | ... |

**Total Rows**: 10 top transformations + 1 remaining + 1 total = 12 rows

### Table 5: Level 3 - Value Statistics
**LaTeX Label**: `\ref{tab:level3-statistics}`

| Feature | Types | Diversity (Can\|Head) | Entropy (bits) | Top-3 Conc. |
|---------|-------|-----------------------|----------------|-------------|
| DEP-REL-CHG | 1,023 | 46 \| 46 | 8.35 | 0.07 |
| BRANCH-DIFF | 1,178 | 104 \| 90 | 9.06 | 0.10 |
| ... | ... | ... | ... | ... |

**Total Rows**: 5 high-entropy features + 4 low-entropy features = 9 rows

---

## Content Statistics

### Text Content
- **New Paragraphs**: ~12 paragraphs
- **Word Count**: ~800 words
- **Technical Terms Introduced**:
  - Shannon entropy
  - Transformation diversity
  - Top-3 concentration ratio
  - Feature-value mapping
  - Distributional properties

### Data Presented
- **Feature Counts**: 30 features (10 in table, all in figure)
- **Transformations**: 45 FEAT-CHG types (10 in table, 15 in figure)
- **Statistics**: 9 features with entropy/diversity metrics
- **Total Data Points**: ~80 numerical values across all tables

---

## File Structure

```
LaTeX/
├── figures/                                   # NEW - Shared figures directory
│   ├── three_level_hierarchy.png             # 347 KB
│   ├── level1_feature_frequency.png          # 304 KB
│   ├── level2_featchange_transformations.png # 405 KB
│   ├── level3_entropy_diversity.png          # 302 KB
│   └── cross_level_comparison.png            # 362 KB
│
├── Task-1-Canonical_Reduced_Register_Comparison_ACL_ARR/
│   ├── task1_register_comparison_v5_context.tex  # UPDATED
│   ├── references.bib                            # Existing
│   │
│   └── Copied figures (5 PNG files):
│       ├── three_level_hierarchy.png
│       ├── level1_feature_frequency.png
│       ├── level2_featchange_transformations.png
│       ├── level3_entropy_diversity.png
│       └── cross_level_comparison.png
│
├── Task-2-Canonical_Reduced_Register_Transformation_ACL_ARR/
│   ├── task2_transformation_study_v5_context.tex  # Can be updated later
│   └── references.bib
│
└── Task-3-Canonical_Reduced_Register_Complexity_ACL_ARR/
    ├── task3_complexity_similarity_v5_multilevel.tex  # Can be updated later
    └── references.bib
```

---

## LaTeX Compilation Notes

### Figure Paths
All figures use relative paths from Task-1 directory:
```latex
\includegraphics[width=\columnwidth]{../figures/level1_feature_frequency.png}
```

This works because:
- Figures are in `LaTeX/figures/`
- LaTeX file is in `LaTeX/Task-1-Canonical_Reduced_Register_Comparison_ACL_ARR/`
- Relative path: `../figures/` goes up one level then into figures

**Alternative**: If compilation fails, figures are also copied to Task-1 directory directly:
```latex
\includegraphics[width=\columnwidth]{level1_feature_frequency.png}
```

### Compilation Commands
```bash
cd LaTeX/Task-1-Canonical_Reduced_Register_Comparison_ACL_ARR

# First pass (may show undefined references - this is expected)
pdflatex task1_register_comparison_v5_context.tex

# Process bibliography
bibtex task1_register_comparison_v5_context

# Second pass (integrate citations)
pdflatex task1_register_comparison_v5_context.tex

# Third pass (resolve all references)
pdflatex task1_register_comparison_v5_context.tex
```

**Expected Output**: `task1_register_comparison_v5_context.pdf`

---

## Data Sources for Figures

All figures are generated from verified GLOBAL data:

1. **Level 1**: `output/GLOBAL_ANALYSIS/global_statistical_summary_features.csv`
2. **Level 2**: `output/GLOBAL_ANALYSIS/global_feature_value_analysis_feature_FEAT-CHG.csv`
3. **Level 3**: `output/GLOBAL_ANALYSIS/global_feature_value_analysis_value_statistics.csv`

**Data Integrity**: All numerical values in tables and figures match the source CSV files exactly.

---

## Python Script for Figure Generation

**File**: `create_three_level_visualizations.py`

**Functionality**:
- Creates all 5 publication-quality figures
- Saves to both `output/three_level_visualizations/` and `LaTeX/figures/`
- Uses matplotlib with seaborn styling
- 300 DPI resolution for publication
- Configurable color schemes

**Execution**:
```bash
python create_three_level_visualizations.py
```

**Output**:
```
[1/5] Creating hierarchy diagram... ✓
[2/5] Creating Level 1 visualization... ✓
[3/5] Creating Level 2 visualization... ✓
[4/5] Creating Level 3 visualization... ✓
[5/5] Creating cross-level comparison... ✓
```

---

## Integration with Existing Content

### Section Placement
The new "Three-Level Data Organization" section is inserted between:
- **Before**: "Overall Transformation Statistics" (Section 4.1)
- **After**: "Feature Category Distribution" (Section 4.3)

This placement makes sense because:
1. Overall stats introduced → Now explain data organization
2. Data organization explained → Then dive into specific categories

### Cross-References
The section creates these new labels:
- `\ref{fig:three-level-hierarchy}` - Conceptual diagram
- `\ref{fig:level1-frequency}` - Feature frequency
- `\ref{fig:level2-featchange}` - FEAT-CHG transformations
- `\ref{fig:level3-entropy-diversity}` - Entropy and diversity
- `\ref{fig:cross-level-comparison}` - Cross-level comparison
- `\ref{tab:level1-top-features}` - Top features table
- `\ref{tab:level2-featchange}` - FEAT-CHG transformations table
- `\ref{tab:level3-statistics}` - Value statistics table

These can be cited elsewhere in the document.

---

## Verification Steps

### 1. Check Figures Exist
```bash
ls -lh LaTeX/figures/*.png
```
**Expected**: 5 PNG files, 300-400 KB each

### 2. Check Task-1 Figures
```bash
ls LaTeX/Task-1-Canonical_Reduced_Register_Comparison_ACL_ARR/*.png | wc -l
```
**Expected**: 5

### 3. Verify LaTeX Update
```bash
grep -c "Three-Level Data Organization" LaTeX/Task-1-Canonical_Reduced_Register_Comparison_ACL_ARR/task1_register_comparison_v5_context.tex
```
**Expected**: 1 (section header)

### 4. Count New Tables
```bash
grep -c "\\\\label{tab:level" LaTeX/Task-1-Canonical_Reduced_Register_Comparison_ACL_ARR/task1_register_comparison_v5_context.tex
```
**Expected**: 3 (level1, level2, level3 tables)

### 5. Count New Figures
```bash
grep -c "\\\\label{fig:.*level" LaTeX/Task-1-Canonical_Reduced_Register_Comparison_ACL_ARR/task1_register_comparison_v5_context.tex
```
**Expected**: 4 (level1, level2, level3, cross-level) + 1 (hierarchy) = 5

---

## Next Steps (Optional)

### For Task-2 and Task-3
The same three-level organization can be integrated into:

1. **Task-2** (`task2_transformation_study_v5_context.tex`):
   - Add section on rule extraction at three levels
   - Show rules organized by feature (Level 1), transformation type (Level 2), and coverage statistics (Level 3)

2. **Task-3** (`task3_complexity_similarity_v5_multilevel.tex`):
   - Add section on complexity measured at three levels
   - Show perplexity organized by feature (Level 1), transformation (Level 2), and entropy (Level 3)

### For Publication
- ✅ Figures are publication-ready (300 DPI)
- ✅ Tables formatted with booktabs
- ✅ Citations integrated
- ⚠️ Consider adding figure to supplementary materials showing full 30-feature data
- ⚠️ Consider creating additional figure showing cross-newspaper comparison

---

## Summary

✅ **Task-1 LaTeX Document Updated**
- New section with 3 levels of data organization
- 3 new tables with real data
- 5 new figures (300 DPI, publication-quality)
- ~145 lines of new content
- ~800 words of explanatory text

✅ **Figures Created and Deployed**
- 5 PNG files in `LaTeX/figures/`
- 5 PNG files copied to Task-1 directory
- All figures referenced in LaTeX
- All captions written

✅ **Data Integrity Verified**
- All tables match source CSV files
- All figures generated from GLOBAL data
- Cross-references properly labeled

**Total File Size**: ~1.7 MB (5 figures)
**Total New Content**: ~145 lines LaTeX + ~800 words
**Ready for Compilation**: Yes (requires acl.sty package)
