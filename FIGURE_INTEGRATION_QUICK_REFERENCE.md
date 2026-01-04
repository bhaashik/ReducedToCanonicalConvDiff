# Figure Integration - Quick Reference Guide

**Status**: ✅ COMPLETE | **Date**: 2026-01-04 | **Figures**: 16/17 integrated

---

## At a Glance

```
Task-1: Comparison Study
├── 5 figures ✅ (all referenced)
├── Focus: Punctuation as compensatory mechanism
└── Location: LaTeX/Canonical-Reduced-Register-Comparison-Part-1-ACL-ARR/

Task-2: Transformation Study
├── 5 figures ⚠️ (4 referenced, 1 unreferenced)
├── Focus: Context-based rules, power-law coverage
└── Location: LaTeX/Canonical-Reduced-Register-Complexity-Part-3-ACL-ARR/

Task-3: Complexity Study
├── 7 figures ✅ (all referenced)
├── Focus: Multi-level complexity, directional asymmetry
└── Location: LaTeX/Canonical-Reduced-Register-Transformation-Part-2-ACL-ARR/
```

---

## Figure Mapping

### Task-1 (Lines 281-481 in .tex file)

| Line | Figure | Key Finding |
|------|--------|-------------|
| 322 | `task1_top_features.png` | Top 15 features, punctuation highlighted in red |
| 334 | `punctuation_overview.png` | 67.32% deletion, 22.39% addition, 10.30% substitution |
| 368 | `punctuation_deletion.png` | 80.13% periods (sentence boundary marking) |
| 401 | `punctuation_addition.png` | 54.54% colons (conjunction replacement) |
| 433 | `punctuation_substitution.png` | 86.73% concentrated in top 3 pairs |

### Task-2 (Lines 169-344 in .tex file)

| Line | Figure | Key Finding |
|------|--------|-------------|
| 204 | `task2_coverage_curve.png` | Power-law: 15-20 rules = 80% coverage |
| 247 | `task2_morphological_rules.png` | Morphological pattern distribution |
| 253 | `task2_newspaper_comparison.png` | ToI 74.4%, HT 59.5%, TH 49.3% verb morphology |
| 293 | `task2_punctuation_rules.png` | 38 distinct punctuation rule types |
| N/A | `morphological_impact_comparison.png` | ⚠️ **UNREFERENCED** - needs decision |

### Task-3 (Lines 225-452 in .tex file)

| Line | Figure | Key Finding |
|------|--------|-------------|
| 258 | `ttr_comparison.png` | Headlines 33% higher lexical diversity |
| 296 | `entropy_comparison.png` | Lexical-structural trade-off |
| 335 | `cross_entropy_comparison.png` | 1.10× directional asymmetry |
| 341 | `kl_divergence_comparison.png` | H→C 10% more information cost |
| 347 | `directional_asymmetry.png` | Multi-metric comparison (10-59% range) |
| 388 | `similarity_heatmaps.png` | 4 metrics × 4 levels matrix |
| 494 | `task3_feature_complexity.png` | 20.9× entropy range (8.35 to 0.40 bits) |

---

## What Was Done

### Phase 1: Figure Creation ✅
- Created `create_publication_figures.py` script
- Generated 3 new publication-quality figures (300 DPI):
  - `task1_top_features.png` - Top 15 features bar chart
  - `task2_newspaper_comparison.png` - Cross-newspaper morphological comparison
  - `task3_feature_complexity.png` - Feature-level entropy ranking

### Phase 2: Figure Organization ✅
- Copied 5 figures to Task-1 directory
- Copied 5 figures to Task-2 directory
- Copied 7 figures to Task-3 directory
- Total: 17 PNG files (300 DPI)

### Phase 3: LaTeX Integration ✅
- Added figure references to Task-1 document (5 figures)
- Added figure references to Task-2 document (4 figures)
- Added figure references to Task-3 document (7 figures)
- Total: 16 integrated, 1 unreferenced

---

## ACL ARR Compliance ✅

All figures follow ACL ARR guidelines:

**Resolution**: 300 DPI (publication quality)
**Format**: PNG (widely compatible)
**LaTeX Structure**:
```latex
\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\columnwidth]{filename.png}
\caption{Clear description with quantitative findings.}
\label{fig:unique-identifier}
\end{figure}
```

**Caption Style**: Descriptive with key quantitative findings
**Width**: 0.85 or 0.95 columnwidth (ACL standard)
**Placement**: `[htbp]` - here, top, bottom, or separate page
**Labels**: Consistent naming scheme for cross-referencing

---

## Next Steps

### Required Before Compilation:
1. **Install ACL style files**
   - Download: https://github.com/acl-org/acl-style-files
   - Files needed: `acl.sty`, `acl.bst`
   - Place in each task directory

2. **Resolve Task-2 unreferenced figure**
   - Option A: Add reference to `morphological_impact_comparison.png`
   - Option B: Remove file from directory

### Compilation:
```bash
# Each task requires:
pdflatex [filename].tex
bibtex [filename]
pdflatex [filename].tex
pdflatex [filename].tex
```

### Verification:
- Check all figures appear in PDFs
- Verify figure numbering is sequential
- Confirm cross-references resolve
- Review caption accuracy

---

## Key Research Findings (Visualized)

### Task-1: Punctuation Compensates for Information Loss
- 6,004 punctuation events (4.88% of total 123,042)
- Colon addition (54.54%) replaces conjunctions
- Period deletion (80.13%) at sentence boundaries
- 3 critical functions: boundary marking, relationship signaling, information preservation

### Task-2: Power-Law Rule Distribution
- 1 rule covers 32.09% of events
- 50 rules cover 89.80% of events
- 91 rules cover 94.55% of events
- Cross-newspaper variation: 74.4% vs 59.5% vs 49.3% verb morphology

### Task-3: Directional Asymmetry in Complexity
- H→C transformation 10-59% more complex than C→H
- 1.10× cross-entropy asymmetry
- 10% higher KL divergence for headline expansion
- 33% higher lexical diversity in headlines
- 20.9× entropy range across features

---

## Files Reference

### Documentation:
- `FIGURE_INTEGRATION_COMPLETE.md` - Comprehensive verification report
- `FIGURE_INTEGRATION_QUICK_REFERENCE.md` - This file (quick reference)
- `LATEX_RESULTS_INSERTION_COMPLETE.md` - Previous Results sections work

### Scripts:
- `create_publication_figures.py` - Figure generation script

### LaTeX Documents:
- Task-1: `LaTeX/Canonical-Reduced-Register-Comparison-Part-1-ACL-ARR/Task-1-Reduced-Canonical-Register-Comparison_acl_latex.tex`
- Task-2: `LaTeX/Canonical-Reduced-Register-Complexity-Part-3-ACL-ARR/Task-2-Reduced-Canonical-Register-Transformation_acl_latex.tex`
- Task-3: `LaTeX/Canonical-Reduced-Register-Transformation-Part-2-ACL-ARR/Task-3-Reduced-Canonical-Register-Complexity-and-Similarity_acl_latex.tex`

### Figure Directories:
- Source: `output/publication_figures/`, `output/punctuation_visualizations/`, `output/multilevel_complexity/GLOBAL_ANALYSIS/`, `output/multilevel_similarity/GLOBAL_ANALYSIS/`, `output/task2_visualizations/`
- Task-1: `LaTeX/Canonical-Reduced-Register-Comparison-Part-1-ACL-ARR/` (5 PNG files)
- Task-2: `LaTeX/Canonical-Reduced-Register-Complexity-Part-3-ACL-ARR/` (5 PNG files)
- Task-3: `LaTeX/Canonical-Reduced-Register-Transformation-Part-2-ACL-ARR/` (7 PNG files)

---

**Summary**: All figure integration tasks complete. 16/17 figures successfully integrated into ACL ARR LaTeX documents. Ready for compilation after installing ACL style files and resolving one unreferenced figure in Task-2.
