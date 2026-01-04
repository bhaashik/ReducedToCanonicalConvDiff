# Quick Reference: Where to Find Data

## LEVEL 1: FEATURES (Feature Counts)

**GLOBAL**: `output/GLOBAL_ANALYSIS/global_statistical_summary_features.csv`
**Per-Newspaper**:
- `output/Times-of-India/feature_freq_global.csv`
- `output/Hindustan-Times/feature_freq_global.csv`
- `output/The-Hindu/feature_freq_global.csv`

**Shows**: 30 features with total counts, percentages

---

## LEVEL 2: FEATURE-VALUE PAIRS (Transformations)

### All Pairs Combined
**GLOBAL**: `output/GLOBAL_ANALYSIS/global_feature_value_pair_analysis_global_pairs.csv`
**Per-Newspaper**:
- `output/Times-of-India/feature_value_pair_analysis_global_pairs.csv`
- `output/Hindustan-Times/feature_value_pair_analysis_global_pairs.csv`
- `output/The-Hindu/feature_value_pair_analysis_global_pairs.csv`

### Per-Feature Files (30 files each)
**GLOBAL**: `output/GLOBAL_ANALYSIS/global_feature_value_analysis_feature_[FEATURE_ID].csv`
**Example**: `output/GLOBAL_ANALYSIS/global_feature_value_analysis_feature_FEAT-CHG.csv`

**Shows**: canonical_value → headline_value transformations with counts, percentages

---

## LEVEL 3: FEATURE VALUES PER FEATURE (Value Statistics)

**GLOBAL**: `output/GLOBAL_ANALYSIS/global_feature_value_analysis_value_statistics.csv`
**Per-Newspaper**:
- `output/Times-of-India/feature_value_analysis_value_statistics.csv`
- `output/Hindustan-Times/feature_value_analysis_value_statistics.csv`
- `output/The-Hindu/feature_value_analysis_value_statistics.csv`

**Shows**: Entropy, diversity, concentration metrics per feature

---

## RAW EVENT DATA

**Per-Newspaper** (all individual events):
- `output/Times-of-India/events_global.csv` (41,616 events)
- `output/Hindustan-Times/events_global.csv` (40,715 events)
- `output/The-Hindu/events_global.csv` (40,711 events)

**Total**: 123,042 events with full context metadata

---

## TOP TRANSFORMATIONS

**File**: `output/GLOBAL_ANALYSIS/global_feature_value_pair_analysis_top_pairs.csv`

Most frequent transformations ranked by count across all features.
