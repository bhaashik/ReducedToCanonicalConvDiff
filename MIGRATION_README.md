# Comprehensive to Selected Migration - README

## Purpose

This directory contains a complete analysis and action plan for migrating summary-level tables and figures from comprehensive directories to selected directories for three 8-page ACL ARR long papers.

## Files in This Package

### 1. **MIGRATION_STATE.json** (SESSION STATE)
- **Purpose:** Machine-readable state file for resuming work across sessions
- **Contains:**
  - Current status of all three tasks
  - File counts and gaps
  - Priority actions
  - Completion tracking
  - Normalization requirements
- **Use:** Load this JSON to understand current state and resume work

### 2. **COMPREHENSIVE_TO_SELECTED_MIGRATION_PLAN.md** (DETAILED PLAN)
- **Purpose:** Human-readable comprehensive analysis with rationale
- **Contains:**
  - Executive summary with statistics
  - Task-by-task analysis (Task 1, 2, 3)
  - Priority 1, 2, 3 tables and figures with explanations
  - Why each file is important
  - Directory structure details
  - Normalization requirements (critical for Task 3)
  - Page budget allocation
  - Implementation phases with bash commands
  - Verification checklists
- **Length:** ~30+ pages with full details
- **Use:** Read this for understanding WHY each file should be copied

### 3. **MIGRATION_QUICK_START.sh** (EXECUTABLE SCRIPT)
- **Purpose:** Automated bash script to execute critical migrations
- **Contains:**
  - 8 phases of migration
  - Directory creation
  - File copying with error checking
  - Progress messages
  - Warnings for missing files
  - Summary report
- **Use:** Execute this to perform all critical migrations automatically
- **Execution:** `bash MIGRATION_QUICK_START.sh`

---

## Quick Start (3 Steps)

### Step 1: Read the Overview
```bash
# Understand what's missing and why
cat MIGRATION_STATE.json | jq .current_status
cat MIGRATION_STATE.json | jq .key_findings
```

### Step 2: Execute Critical Migrations
```bash
# Run the automated script
bash MIGRATION_QUICK_START.sh
```

### Step 3: Manual Verification (Task 3)
```bash
# Verify normalization in Task 3 figures
# Check these files in latex-selected/figures/global/:
# - entropy_comparison.png
# - cross_entropy_comparison.png
# - kl_divergence_comparison.png
# - complexity_ratios.png

# Open each and verify axis labels show "per-token" or "normalized"
```

---

## Current Status Summary

| Task | Paper | Tables | Figures | Critical Issue |
|------|-------|--------|---------|----------------|
| Task 1 | Comparative Study | 0/108 | 16/90 | Missing cross-newspaper comparisons |
| Task 2 | Transformation Study | 0/16 | 0/19 | **No global/ directory** |
| Task 3 | Complexity & Similarity | 0/44 | 12/12 | **Normalization verification needed** |

## Critical Files by Task

### Task 1: Comparative Study
- **Most Critical Table:** `global_comprehensive_analysis_global.tex`
  - Overall feature frequency (30 rows)
  - Core summary of all morphosyntactic differences
- **Most Critical Figure:** `cross_newspaper_normalized_comparison.png`
  - Fair comparison controlling for corpus size

### Task 2: Transformation Study
- **Most Critical Table:** `integrated_transformation_comparison.tex`
  - 3-row table summarizing entire Task 2
  - Shows events, morphological %, rules per newspaper
- **Most Critical Issue:** Directory structure broken
  - Need to create `latex-selected/figures/global/`
  - Move 8 root figures to global/

### Task 3: Complexity & Similarity
- **Most Critical Table:** `bidirectional_metrics.tex`
  - BLEU/ROUGE scores for H→C and C→H
  - 6 rows (3 newspapers × 2 directions)
- **Most Critical Issue:** Normalization verification
  - All complexity metrics MUST use normalized values
  - Per-token, per-char, or vocab-normalized
  - **WHY:** Fair comparison across newspapers with different sizes

---

## Normalization Requirements (CRITICAL FOR TASK 3)

### Why Normalization Matters

**Problem:** Raw values are meaningless for cross-newspaper comparison
- Times-of-India: 500 sentence pairs
- Hindustan-Times: 500 sentence pairs
- The-Hindu: 500 sentence pairs

BUT: Different sentence lengths, vocabulary sizes, feature distributions

**Solution:** Always use normalized metrics

### Required Normalizations

| Metric | Raw (WRONG) | Normalized (CORRECT) |
|--------|-------------|----------------------|
| Perplexity | Total bits | Bits per token |
| Cross-entropy | Total H(P,Q) | H(P,Q) / sequence length |
| KL divergence | Total D_KL | Bits per token |
| Feature freq | Raw count | Per 1000 tokens |
| TTR | N/A | Types / Tokens (inherently normalized) |
| Complexity ratio | Raw H→C / Raw C→H | Normalized H→C / Normalized C→H |

### Verification Checklist for Task 3

- [ ] `entropy_comparison.png` - y-axis should say "Bits per token"
- [ ] `cross_entropy_comparison.png` - y-axis should say "Bits per token"
- [ ] `kl_divergence_comparison.png` - y-axis should say "Bits per token"
- [ ] `complexity_ratios.png` - Should be ratio of normalized values
- [ ] `directional_perplexity_analysis.tex` - Table should show per-token values
- [ ] `cross_newspaper_comparison.tex` - Should use normalized metrics

**If any show raw values → CREATE normalized variants!**

---

## Directory Structure (Target)

```
latex-selected/
├── tables/                           # All summary tables
│   ├── [global_*.tex]               # Global cross-newspaper tables
│   ├── [cross_newspaper_*.tex]      # Cross-newspaper comparisons
│   └── [other summary tables]
│
├── figures/
│   ├── global/                      # Cross-newspaper figures
│   │   ├── cross_newspaper_*.png   # Cross-newspaper comparisons
│   │   ├── task*_*.png             # Task-level summaries
│   │   └── [other global figures]
│   │
│   ├── Hindustan-Times/            # Per-newspaper figures
│   │   └── [11-70 figures depending on task]
│   │
│   ├── The-Hindu/
│   │   └── [11-70 figures]
│   │
│   └── Times-of-India/
│       └── [11-70 figures]
│
└── main.tex                         # Main paper LaTeX file
```

### Current Issues

**Task 1:**
- ✗ No `tables/` directory
- ✗ Missing 74 global figures
- ✓ Has proper figure structure

**Task 2:**
- ✗ No `tables/` directory
- ✗ No `figures/global/` directory
- ✗ 8 figures in root that should be in global/

**Task 3:**
- ✗ No `tables/` directory
- ✓ Complete figure structure
- ⚠ Normalization verification needed

---

## Execution Phases

### Phase 1: Directory Setup (5 minutes)
- Create `tables/` in all three tasks
- Create `figures/global/` in Task 2

### Phase 2: Task 1 Critical (30 minutes)
- Copy 5 PRIORITY 1 tables
- Copy 3-5 missing global figures

### Phase 3: Task 2 Restructure (45 minutes)
- Move 8 root figures to global/
- Copy 3 PRIORITY 1 tables
- Copy 13 global figures

### Phase 4: Task 3 Critical (30 minutes)
- Copy 3 PRIORITY 1 tables
- Verify normalization in all 12 global figures

### Phase 5: High Priority Items (2-4 hours)
- Copy PRIORITY 2 tables (12 total across tasks)
- Copy additional global figures
- Create normalized variants if needed

### Phase 6: Appendix Materials (2-3 hours)
- Copy detailed per-feature tables
- Copy supporting figures
- Organize per-newspaper materials

**Total Time: 7-10 hours for complete migration**

---

## Post-Migration Tasks

### 1. Update LaTeX Files
- Modify main.tex to use `\input{tables/filename.tex}` instead of embedded tables
- Update figure references to match new paths
- Verify all cross-references work

### 2. Test Compilation
```bash
# Task 1
cd /path/to/Part_1/latex-selected/
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex

# Repeat for Task 2 and Task 3
```

### 3. Verify Page Counts
- Main content: Should fit in 8 pages
- References: Unlimited (separate section)
- Appendices: Unlimited (separate section)
- Check figure/table placement

### 4. Normalize Task 3 (If Needed)
```bash
# If any Task 3 figures/tables show raw values, regenerate with normalization
cd /path/to/analysis/scripts/
python regenerate_normalized_figures.py
python regenerate_normalized_tables.py
```

---

## Troubleshooting

### Problem: "File not found" errors during migration
**Solution:** Some files may not exist in comprehensive directory
- Check comprehensive directory manually
- May need to generate from analysis outputs
- See COMPREHENSIVE_TO_SELECTED_MIGRATION_PLAN.md for alternatives

### Problem: Task 2 figures in wrong location
**Solution:** Run Phase 4 of MIGRATION_QUICK_START.sh
- Creates global/ directory
- Moves root figures automatically

### Problem: Task 3 shows raw (un-normalized) values
**Solution:** Regenerate figures/tables with normalization
- Check original analysis scripts
- Add per-token / per-char normalization
- See normalization requirements section above

### Problem: LaTeX compilation fails after migration
**Solution:** Update file paths in main.tex
- Change embedded tables to `\input{tables/filename.tex}`
- Update figure paths: `figures/global/filename.png`
- Check for missing files

---

## Additional Resources

### For Detailed Rationale
- See **COMPREHENSIVE_TO_SELECTED_MIGRATION_PLAN.md**
- Sections:
  - Task 1: Lines 45-350
  - Task 2: Lines 351-600
  - Task 3: Lines 601-900
  - Implementation: Lines 901-1100

### For State Tracking
- See **MIGRATION_STATE.json**
- Fields:
  - `current_status`: What's done, what's missing
  - `priority_actions`: What to do next
  - `completion_tracking`: Progress counters
  - `normalization_requirements`: Task 3 requirements

### For Execution
- Run **MIGRATION_QUICK_START.sh**
- Automated migration of all CRITICAL items
- Includes error checking and progress messages

---

## Success Criteria

### Task 1: Comparative Study
- ✓ 5 global summary tables in latex-selected/tables/
- ✓ At least 20 global figures (current 16 + 4-10 additions)
- ✓ cross_newspaper_normalized_comparison.png present
- ✓ All key cross-newspaper comparisons included

### Task 2: Transformation Study
- ✓ latex-selected/figures/global/ directory exists
- ✓ All root figures moved to global/
- ✓ integrated_transformation_comparison.tex present
- ✓ At least 15 global figures (current 0 + 15 additions)
- ✓ Morphological analysis figures included

### Task 3: Complexity & Similarity
- ✓ 3 critical tables in latex-selected/tables/
- ✓ ALL figures verified to use normalized values
- ✓ Complexity ratios based on normalized metrics
- ✓ Perplexity tables show per-token values
- ✓ Cross-newspaper comparisons use fair metrics

---

## Contact / Questions

For issues or questions about this migration:
1. Check **MIGRATION_STATE.json** for current status
2. Refer to **COMPREHENSIVE_TO_SELECTED_MIGRATION_PLAN.md** for detailed rationale
3. Review **normalization_requirements** section for Task 3 requirements
4. Verify file existence in comprehensive directories before reporting missing files

---

## Changelog

**2026-01-07:** Initial creation
- Analyzed all three tasks
- Identified 108+16+44=168 comprehensive tables
- Found 74 missing Task 1 figures, 19 missing Task 2 figures
- Created automated migration script
- Documented normalization requirements for Task 3
