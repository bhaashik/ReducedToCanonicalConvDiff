#!/bin/bash

# Quick Start Migration Script
# Task: Copy summary-level tables and figures from comprehensive to selected directories
# For: ACL ARR 8-page long papers (3 tasks)
# Date: 2026-01-07

# Set error handling
set -e

# Base directories
BASE="/mnt/d/Dropbox/backup-and-keep/D-Drive-HP-x360-14-cd/projects/Bhaashik/ReducedToCanonicalConvDiff/LaTeX"
TASK1_BASE="$BASE/Canonical_Reduced_Register_Complexity_Part_1_ACL_ARR_short_submitted"
TASK2_BASE="$BASE/Canonical_Reduced_Register_Complexity_Part_2_ACL_ARR_short_not_submitted/latex"
TASK3_BASE="$BASE/Canonical_Reduced_Register_Complexity_Part_3_ACL_ARR_short_submiited"

echo "========================================="
echo "COMPREHENSIVE TO SELECTED MIGRATION"
echo "========================================="
echo ""

# =============================================================================
# PHASE 1: Create Required Directories
# =============================================================================

echo "PHASE 1: Creating directory structure..."

mkdir -p "$TASK1_BASE/latex-selected/tables/"
echo "  ✓ Created Task 1 tables/ directory"

mkdir -p "$TASK2_BASE/latex-selected/tables/"
echo "  ✓ Created Task 2 tables/ directory"

mkdir -p "$TASK2_BASE/latex-selected/figures/global/"
echo "  ✓ Created Task 2 figures/global/ directory"

mkdir -p "$TASK3_BASE/latex-selected/tables/"
echo "  ✓ Created Task 3 tables/ directory"

echo ""
echo "PHASE 1 COMPLETE"
echo ""

# =============================================================================
# PHASE 2: TASK 1 - Copy Critical Tables
# =============================================================================

echo "PHASE 2: Task 1 - Copying 5 CRITICAL tables..."

cd "$TASK1_BASE"

cp latex-comprehensive/tables/global_comprehensive_analysis_global.tex \
   latex-selected/tables/
echo "  ✓ Copied global_comprehensive_analysis_global.tex"

cp latex-comprehensive/tables/cross_newspaper_comparison.tex \
   latex-selected/tables/
echo "  ✓ Copied cross_newspaper_comparison.tex"

cp latex-comprehensive/tables/global_statistical_summary_features.tex \
   latex-selected/tables/
echo "  ✓ Copied global_statistical_summary_features.tex"

cp latex-comprehensive/tables/global_bidirectional_cross_entropy_analysis_global_metrics.tex \
   latex-selected/tables/
echo "  ✓ Copied global_bidirectional_cross_entropy_analysis_global_metrics.tex"

cp latex-comprehensive/tables/global_feature_value_pair_analysis_top_pairs.tex \
   latex-selected/tables/
echo "  ✓ Copied global_feature_value_pair_analysis_top_pairs.tex"

echo ""
echo "PHASE 2 COMPLETE: Task 1 tables copied"
echo ""

# =============================================================================
# PHASE 3: TASK 1 - Copy Critical Figures
# =============================================================================

echo "PHASE 3: Task 1 - Copying missing global figures..."

# Check if files exist before copying
if [ -f latex-comprehensive/figures/global/cross_newspaper_event_counts.png ]; then
  cp latex-comprehensive/figures/global/cross_newspaper_event_counts.png \
     latex-selected/global/
  echo "  ✓ Copied cross_newspaper_event_counts.png"
else
  echo "  ⚠ WARNING: cross_newspaper_event_counts.png not found"
fi

if [ -f latex-comprehensive/figures/global/cross_newspaper_top_features_comparison.png ]; then
  cp latex-comprehensive/figures/global/cross_newspaper_top_features_comparison.png \
     latex-selected/global/
  echo "  ✓ Copied cross_newspaper_top_features_comparison.png"
else
  echo "  ⚠ WARNING: cross_newspaper_top_features_comparison.png not found"
fi

if [ -f latex-comprehensive/figures/global/cross_newspaper_parse_types.png ]; then
  cp latex-comprehensive/figures/global/cross_newspaper_parse_types.png \
     latex-selected/global/
  echo "  ✓ Copied cross_newspaper_parse_types.png"
else
  echo "  ⚠ WARNING: cross_newspaper_parse_types.png not found"
fi

echo ""
echo "PHASE 3 COMPLETE: Task 1 figures copied"
echo ""

# =============================================================================
# PHASE 4: TASK 2 - Restructure Figures (Move root to global/)
# =============================================================================

echo "PHASE 4: Task 2 - Restructuring figures directory..."

cd "$TASK2_BASE"

# Count existing root figures
ROOT_FIGS=$(ls latex-selected/figures/*.png 2>/dev/null | wc -l)

if [ "$ROOT_FIGS" -gt 0 ]; then
  echo "  Found $ROOT_FIGS figures in root, moving to global/..."

  # Move all PNG files from root to global/
  mv latex-selected/figures/*.png latex-selected/figures/global/ 2>/dev/null || true

  echo "  ✓ Moved root figures to global/"
else
  echo "  ℹ No root figures found (may have been moved already)"
fi

echo ""
echo "PHASE 4 COMPLETE: Task 2 directory restructured"
echo ""

# =============================================================================
# PHASE 5: TASK 2 - Copy Critical Tables
# =============================================================================

echo "PHASE 5: Task 2 - Copying 3 CRITICAL tables..."

cp latex-comprehensive/tables/integrated_transformation_comparison.tex \
   latex-selected/tables/
echo "  ✓ Copied integrated_transformation_comparison.tex (MOST CRITICAL)"

cp latex-comprehensive/tables/overall_morphological_statistics.tex \
   latex-selected/tables/
echo "  ✓ Copied overall_morphological_statistics.tex"

cp latex-comprehensive/tables/morphological_systematicity.tex \
   latex-selected/tables/
echo "  ✓ Copied morphological_systematicity.tex"

echo ""
echo "PHASE 5 COMPLETE: Task 2 tables copied"
echo ""

# =============================================================================
# PHASE 6: TASK 2 - Copy Critical Figures
# =============================================================================

echo "PHASE 6: Task 2 - Copying missing global figures..."

# Copy task2_*.png figures
for fig in task2_coverage_curve.png \
           task2_newspaper_comparison.png \
           task2_morphological_rules.png \
           task2_punctuation_rules.png \
           task2_rule_hierarchy.png; do
  if [ -f "latex-comprehensive/figures/global/$fig" ]; then
    cp "latex-comprehensive/figures/global/$fig" \
       latex-selected/figures/global/
    echo "  ✓ Copied $fig"
  else
    echo "  ⚠ WARNING: $fig not found"
  fi
done

# Copy other critical figures
for fig in integrated_comparison.png \
           morphological_features_heatmap.png \
           morphological_impact_comparison.png \
           noun_morphology_comparison.png \
           verb_morphology_comparison.png \
           overall_morphological_statistics.png \
           transformation_directionality.png \
           cross_newspaper_feature_comparison.png; do
  if [ -f "latex-comprehensive/figures/global/$fig" ]; then
    cp "latex-comprehensive/figures/global/$fig" \
       latex-selected/figures/global/
    echo "  ✓ Copied $fig"
  else
    echo "  ⚠ WARNING: $fig not found"
  fi
done

echo ""
echo "PHASE 6 COMPLETE: Task 2 figures copied"
echo ""

# =============================================================================
# PHASE 7: TASK 3 - Copy Critical Tables
# =============================================================================

echo "PHASE 7: Task 3 - Copying 3 CRITICAL tables..."

cd "$TASK3_BASE"

cp latex-comprehensive/tables/bidirectional_metrics.tex \
   latex-selected/tables/
echo "  ✓ Copied bidirectional_metrics.tex (MOST CRITICAL)"

cp latex-comprehensive/tables/directional_perplexity_analysis.tex \
   latex-selected/tables/
echo "  ✓ Copied directional_perplexity_analysis.tex"

cp latex-comprehensive/tables/cross_newspaper_comparison.tex \
   latex-selected/tables/
echo "  ✓ Copied cross_newspaper_comparison.tex"

echo ""
echo "PHASE 7 COMPLETE: Task 3 tables copied"
echo ""

# =============================================================================
# PHASE 8: TASK 3 - Normalization Verification
# =============================================================================

echo "PHASE 8: Task 3 - Normalization verification..."
echo ""
echo "  ⚠ MANUAL VERIFICATION REQUIRED:"
echo "  Please check the following figures for normalized values:"
echo "    - entropy_comparison.png (should be per-token)"
echo "    - cross_entropy_comparison.png (should be bits per token)"
echo "    - kl_divergence_comparison.png (should be bits per token)"
echo "    - complexity_ratios.png (should be based on normalized values)"
echo ""
echo "  If any show RAW values, create normalized variants!"
echo ""

# =============================================================================
# Summary
# =============================================================================

echo "========================================="
echo "MIGRATION SUMMARY"
echo "========================================="
echo ""
echo "COMPLETED:"
echo "  ✓ Task 1: Copied 5 tables + 3 figures"
echo "  ✓ Task 2: Restructured directory + copied 3 tables + 13 figures"
echo "  ✓ Task 3: Copied 3 tables"
echo ""
echo "NEXT STEPS:"
echo "  1. Task 3: Verify normalization in all figures"
echo "  2. Update main .tex files to reference new table files"
echo "  3. Test LaTeX compilation"
echo ""
echo "FOR HIGH PRIORITY ITEMS:"
echo "  See COMPREHENSIVE_TO_SELECTED_MIGRATION_PLAN.md"
echo "  Sections: Priority 2 tables and figures"
echo ""
echo "STATE SAVED TO:"
echo "  MIGRATION_STATE.json"
echo ""
echo "========================================="
echo "MIGRATION COMPLETE"
echo "========================================="
