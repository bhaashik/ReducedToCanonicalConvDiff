# Data Organization: Three-Level Analysis Structure

**Generated**: 2026-01-03
**Total Events**: 123,042 (across 3 newspapers)

---

## Overview

This document organizes all analytical data into three distinct levels:

1. **Level 1: FEATURES** - Feature-level counts and statistics (30 features)
2. **Level 2: FEATURE-VALUE PAIRS** - Transformations between specific values
3. **Level 3: FEATURE VALUES PER FEATURE** - Value distributions within each feature

All data exists in both **per-newspaper** and **GLOBAL** (cross-newspaper) formats.

---

## LEVEL 1: FEATURES (Feature-Level Analysis)

### Description
Aggregate counts and statistics for each of the 30 Schema v5.0 linguistic features, without considering specific values.

### Key Data Files

#### GLOBAL (All Newspapers Combined)
**File**: `output/GLOBAL_ANALYSIS/global_statistical_summary_features.csv`

**Columns**:
- `feature_id`: Feature mnemonic (e.g., "FEAT-CHG", "FW-DEL")
- `feature_name`: Full feature name (e.g., "Morphological Feature Change")
- `total_occurrences`: Count across all newspapers
- `percentage_of_total`: Percentage of 123,042 total events
- `newspapers_found_in`: Number of newspapers (1-3)
- `parse_types_found_in`: Number of parse types (dependency/constituency)

**Sample Data** (Top 10 Features):
| Feature ID | Feature Name | Count | Percentage |
|-----------|--------------|-------|------------|
| CONST-MOV | Constituent Movement | 30,289 | 24.62% |
| DEP-REL-CHG | Dependency Relation Change | 26,935 | 21.89% |
| CLAUSE-TYPE-CHG | Clause Type Change | 7,636 | 6.21% |
| FW-DEL | Function Word Deletion | 7,112 | 5.78% |
| PUNCT-DEL | Punctuation Deletion | 4,042 | 3.29% |
| H-STRUCT | Headline Structure | 3,689 | 3.00% |
| CONST-COUNT-DIFF | Constituent Count Difference | 3,689 | 3.00% |
| TREE-DEPTH-DIFF | Tree Depth Difference | 3,689 | 3.00% |
| DEP-DIST-DIFF | Dependency Distance Difference | 3,689 | 3.00% |
| BRANCH-DIFF | Branching Factor Difference | 3,689 | 3.00% |

**Total**: 30 features analyzed

#### Per-Newspaper
**Files**:
- `output/Times-of-India/feature_freq_global.csv` (41,616 events)
- `output/Hindustan-Times/feature_freq_global.csv` (40,715 events)
- `output/The-Hindu/feature_freq_global.csv` (40,711 events)

**Same structure** as GLOBAL file, but newspaper-specific counts.

### Visualizations
- Feature frequency bar charts (per newspaper + GLOBAL)
- Feature category pie charts (Lexical, Morphological, Syntactic, etc.)
- Cross-newspaper feature comparison heatmaps

**Location**: `output/[Newspaper]/visualizations/feature_frequency_*.png`

---

## LEVEL 2: FEATURE-VALUE PAIRS (Transformation Analysis)

### Description
Specific transformations from one feature value to another (canonical → headline), showing the directional nature of register transformations.

### Key Data Files

#### GLOBAL (All Newspapers Combined)

**Per-Feature Files**: `output/GLOBAL_ANALYSIS/global_feature_value_analysis_feature_[FEATURE_ID].csv`

**Example**: `global_feature_value_analysis_feature_FEAT-CHG.csv`

**Columns**:
- `feature_id`: Feature mnemonic
- `canonical_value`: Value in canonical (full sentence)
- `headline_value`: Value in headline (reduced)
- `transformation`: Combined representation (canonical→headline)
- `count`: Number of occurrences
- `percentage`: Percentage of all transformations for this feature

**Sample Data** (FEAT-CHG - Morphological Feature Changes):
| Canonical Value | Headline Value | Transformation | Count | % |
|----------------|----------------|----------------|-------|-----|
| Tense=Past | Tense=Pres | Tense=Past→Tense=Pres | 115 | 28.19% |
| Number=ABSENT | Number=Sing | Number=ABSENT→Number=Sing | 26 | 6.37% |
| Number=Plur | Number=Sing | Number=Plur→Number=Sing | 26 | 6.37% |
| Person=ABSENT | Person=3 | Person=ABSENT→Person=3 | 22 | 5.39% |
| Mood=ABSENT | Mood=Ind | Mood=ABSENT→Mood=Ind | 22 | 5.39% |
| Person=3 | Person=ABSENT | Person=3→Person=ABSENT | 19 | 4.66% |
| Mood=Ind | Mood=ABSENT | Mood=Ind→Mood=ABSENT | 18 | 4.41% |
| Number=Sing | Number=Plur | Number=Sing→Number=Plur | 16 | 3.92% |
| ... | ... | ... | ... | ... |

**Total Transformations for FEAT-CHG**: 408 events across 45 unique transformation types

**All Features Available** (30 files):
- `global_feature_value_analysis_feature_FEAT-CHG.csv` (408 events, 45 types)
- `global_feature_value_analysis_feature_FW-DEL.csv` (7,112 events, 6 types)
- `global_feature_value_analysis_feature_DEP-REL-CHG.csv` (26,935 events, 1,023 types)
- `global_feature_value_analysis_feature_CONST-MOV.csv` (30,289 events, 2 types)
- ... (26 more files)

#### Aggregated Pair Analysis

**File**: `output/GLOBAL_ANALYSIS/global_feature_value_pair_analysis_global_pairs.csv`

Comprehensive analysis of all feature-value pairs across all features.

**Columns**:
- `feature_id`
- `canonical_value`
- `headline_value`
- `transformation`
- `count`
- `percentage_within_feature`
- `percentage_of_total`
- `newspaper_diversity` (how many newspapers show this transformation)

#### Top Pairs

**File**: `output/GLOBAL_ANALYSIS/global_feature_value_pair_analysis_top_pairs.csv`

Most frequent transformations across all features (ranked by count).

**Sample Data** (Top 10 Transformations):
| Rank | Feature | Transformation | Count |
|------|---------|----------------|-------|
| 1 | CONST-MOV | CONST-FRONT→CONST-FRONT | 27,855 |
| 2 | PUNCT-DEL | period→ | 3,239 |
| 3 | FW-DEL | AUX-DEL→ABSENT | 2,851 |
| 4 | CLAUSE-TYPE-CHG | Part→Fin | 2,825 |
| 5 | TED-SIMPLE | 10→10 | 2,896 |
| 6 | H-STRUCT | →single-line | 3,634 |
| 7 | C-DEL | VERB-DEL→ABSENT | 1,105 |
| 8 | C-ADD | ABSENT→NOUN-ADD | 1,048 |
| 9 | PUNCT-ADD | →colon | 733 |
| 10 | DEP-REL-CHG | det→compound | 700 |

#### Per-Newspaper

**Files**:
- `output/Times-of-India/feature_value_pair_analysis_global_pairs.csv`
- `output/Hindustan-Times/feature_value_pair_analysis_global_pairs.csv`
- `output/The-Hindu/feature_value_pair_analysis_global_pairs.csv`

### Visualizations
- Transformation matrices (heatmaps showing value-to-value flows)
- Sankey/flow diagrams (top transformations)
- Network graphs (value transformation networks)

**Location**: `output/[Newspaper]/visualizations/transformation_*.png`

---

## LEVEL 3: FEATURE VALUES PER FEATURE (Value Distribution Analysis)

### Description
Distribution and statistics of values **within** each feature, analyzing value diversity, entropy, and concentration.

### Key Data Files

#### GLOBAL (All Newspapers Combined)

**File**: `output/GLOBAL_ANALYSIS/global_feature_value_analysis_value_statistics.csv`

**Columns**:
- `feature_id`: Feature mnemonic
- `total_transformations`: Total events for this feature
- `unique_transformation_types`: Number of distinct value-to-value transformations
- `canonical_value_diversity`: Number of unique values in canonical register
- `headline_value_diversity`: Number of unique values in headline register
- `top3_concentration_ratio`: Proportion of events in top 3 transformations
- `transformation_entropy`: Shannon entropy of transformation distribution (bits)
- `most_frequent_transformation`: Most common transformation
- `most_frequent_count`: Count of most frequent transformation

**Sample Data** (Selected Features):

| Feature ID | Total | Unique Types | Can Diversity | Head Diversity | Entropy | Top Transform | Top Count |
|-----------|-------|--------------|---------------|----------------|---------|---------------|-----------|
| FEAT-CHG | 408 | 45 | 29 | 28 | 4.22 bits | Tense=Past→Tense=Pres | 115 |
| FW-DEL | 7,112 | 6 | 6 | 1 | 2.01 bits | AUX-DEL→ABSENT | 2,851 |
| DEP-REL-CHG | 26,935 | 1,023 | 46 | 46 | 8.35 bits | det→compound | 700 |
| CONST-MOV | 30,289 | 2 | 2 | 2 | 0.40 bits | CONST-FRONT→CONST-FRONT | 27,855 |
| PUNCT-DEL | 4,042 | 8 | 8 | 1 | 1.10 bits | period→ | 3,239 |
| CLAUSE-TYPE-CHG | 7,636 | 7 | 5 | 5 | 2.31 bits | Part→Fin | 2,825 |

**Interpretation**:
- **High Entropy** (e.g., DEP-REL-CHG: 8.35 bits): Many diverse transformations, low predictability
- **Low Entropy** (e.g., CONST-MOV: 0.40 bits): Few transformations, highly concentrated
- **High Diversity** (e.g., DEP-REL-CHG: 46 values): Rich value space
- **Low Diversity** (e.g., CONST-MOV: 2 values): Limited value space

#### Transformation Patterns

**File**: `output/GLOBAL_ANALYSIS/global_feature_value_analysis_transformation_patterns.csv`

Detailed analysis of transformation patterns including:
- Bidirectional transformations (A→B and B→A)
- Self-transformations (A→A)
- Asymmetric transformations (only A→B exists)

#### Concentration Metrics

**File**: `output/GLOBAL_ANALYSIS/global_feature_value_pair_analysis_concentration_metrics.csv`

Statistical concentration measures:
- Gini coefficient (inequality in transformation distribution)
- Herfindahl index (market concentration analogue)
- Top-K concentration ratios (K=1,3,5,10)

#### Per-Newspaper

**Files**:
- `output/Times-of-India/feature_value_analysis_value_statistics.csv`
- `output/Hindustan-Times/feature_value_analysis_value_statistics.csv`
- `output/The-Hindu/feature_value_analysis_value_statistics.csv`

### Visualizations
- Value distribution bar charts per feature
- Entropy comparison across features
- Diversity scatter plots (canonical vs. headline diversity)
- Concentration ratio heatmaps

**Location**: `output/[Newspaper]/visualizations/value_distribution_*.png`

---

## Complete File Structure

```
output/
│
├── GLOBAL_ANALYSIS/                           # Cross-newspaper aggregated data
│   │
│   ├── LEVEL 1: FEATURES
│   │   ├── global_statistical_summary_features.csv
│   │   ├── global_comprehensive_analysis_global.csv
│   │   └── global_comprehensive_analysis_by_newspaper.csv
│   │
│   ├── LEVEL 2: FEATURE-VALUE PAIRS
│   │   ├── global_feature_value_pair_analysis_global_pairs.csv
│   │   ├── global_feature_value_pair_analysis_top_pairs.csv
│   │   ├── global_feature_value_pair_analysis_transformation_complexity.csv
│   │   ├── global_feature_value_pair_analysis_concentration_metrics.csv
│   │   ├── global_feature_value_pair_analysis_newspaper_diversity.csv
│   │   │
│   │   └── PER-FEATURE FILES (30 files):
│   │       ├── global_feature_value_analysis_feature_FEAT-CHG.csv
│   │       ├── global_feature_value_analysis_feature_FW-DEL.csv
│   │       ├── global_feature_value_analysis_feature_DEP-REL-CHG.csv
│   │       └── ... (27 more)
│   │
│   └── LEVEL 3: FEATURE VALUES PER FEATURE
│       ├── global_feature_value_analysis_value_statistics.csv
│       ├── global_feature_value_analysis_transformation_patterns.csv
│       └── global_feature_value_analysis_global_transformations.csv
│
├── Times-of-India/                            # Newspaper-specific data
│   ├── events_global.csv                      # RAW EVENT DATA (all events)
│   │
│   ├── LEVEL 1: FEATURES
│   │   ├── feature_freq_global.csv
│   │   ├── comprehensive_analysis_global.csv
│   │   └── statistical_summary_features.csv
│   │
│   ├── LEVEL 2: FEATURE-VALUE PAIRS
│   │   ├── feature_value_pair_analysis_global_pairs.csv
│   │   ├── feature_value_pair_analysis_top_pairs.csv
│   │   ├── feature_value_pair_analysis_transformation_complexity.csv
│   │   ├── feature_value_pair_analysis_concentration_metrics.csv
│   │   │
│   │   └── PER-FEATURE FILES (30 files):
│   │       ├── feature_value_analysis_feature_FEAT-CHG.csv
│   │       ├── feature_value_analysis_feature_FW-DEL.csv
│   │       └── ... (28 more)
│   │
│   ├── LEVEL 3: FEATURE VALUES PER FEATURE
│   │   ├── feature_value_analysis_value_statistics.csv
│   │   ├── feature_value_analysis_transformation_patterns.csv
│   │   └── feature_value_analysis_global_transformations.csv
│   │
│   └── visualizations/                        # 100+ PNG files
│       ├── feature_frequency_*.png
│       ├── transformation_*.png
│       ├── value_distribution_*.png
│       └── ...
│
├── Hindustan-Times/                           # Same structure as Times-of-India
│   └── ... (identical file structure)
│
└── The-Hindu/                                 # Same structure as Times-of-India
    └── ... (identical file structure)
```

---

## Data Hierarchy Summary

### Granularity Levels

1. **FEATURES** (30 rows)
   - One row per feature
   - Aggregate counts without value detail
   - Example: "FEAT-CHG has 408 total occurrences"

2. **FEATURE-VALUE PAIRS** (1,000+ rows)
   - One row per unique transformation (canonical_value → headline_value)
   - Directional transformation counts
   - Example: "Tense=Past → Tense=Pres occurs 115 times in FEAT-CHG"

3. **FEATURE VALUES PER FEATURE** (30 rows with detailed statistics)
   - One row per feature with value distribution statistics
   - Entropy, diversity, concentration metrics
   - Example: "FEAT-CHG has 45 unique transformation types with 4.22 bits entropy"

### Newspaper Dimensions

For each level, data is available in:
- **Per-newspaper format** (3 files: ToI, HT, TH)
- **GLOBAL format** (1 file: all newspapers combined)

**Total data files**: ~150+ CSV files organized across 3 levels × 4 views (3 newspapers + GLOBAL)

---

## Schema v5.0 Feature Categories

All 30 features are organized into 5 categories:

### 1. LEXICAL (5 features)
- FW-DEL (Function Word Deletion) - 7,112 events
- FW-ADD (Function Word Addition) - 485 events
- C-DEL (Content Word Deletion) - 2,572 events
- C-ADD (Content Word Addition) - 1,430 events
- FORM-CHG (Surface Form Change) - 308 events

### 2. MORPHOLOGICAL (4 features)
- FEAT-CHG (Morphological Feature Change) - 408 events
- POS-CHG (Part of Speech Change) - 256 events
- LEMMA-CHG (Lemma Change) - 65 events
- VERB-FORM-CHG (Verb Form Change) - 38 events

### 3. SYNTACTIC (7 features)
- DEP-REL-CHG (Dependency Relation Change) - 26,935 events
- HEAD-CHG (Dependency Head Change) - 760 events
- CLAUSE-TYPE-CHG (Clause Type Change) - 7,636 events
- TOKEN-REORDER (Token Reordering) - 21 events
- CONST-MOV (Constituent Movement) - 30,289 events
- CONST-ADD (Constituent Addition) - 329 events
- CONST-REM (Constituent Removal) - 1,008 events

### 4. STRUCTURAL (9 features)
- TREE-DEPTH-DIFF (Tree Depth Difference) - 3,689 events
- BRANCH-DIFF (Branching Factor Difference) - 3,689 events
- DEP-DIST-DIFF (Dependency Distance Difference) - 3,689 events
- LENGTH-CHG (Sentence Length Change) - 3,276 events
- CONST-COUNT-DIFF (Constituent Count Difference) - 3,689 events
- TED-SIMPLE (Simple Tree Edit Distance) - 3,234 events
- TED-RTED (RTED Algorithm) - 3,316 events
- TED-ZHANG-SHASHA (Zhang-Shasha Algorithm) - 2,713 events
- TED-KLEIN (Klein Algorithm) - 2,713 events

### 5. PUNCTUATION (5 features)
- PUNCT-DEL (Punctuation Deletion) - 4,042 events
- PUNCT-ADD (Punctuation Addition) - 1,344 events
- PUNCT-SUBST (Punctuation Substitution) - 618 events
- H-STRUCT (Headline Structure) - 3,689 events
- H-TYPE (Headline Type) - 3,689 events

---

## Example Queries by Level

### Level 1: Feature-Level Questions

**Q**: Which feature is most frequent?
**A**: CONST-MOV (Constituent Movement) with 30,289 occurrences (24.62%)

**Q**: How many punctuation-related events are there?
**A**: 13,682 events (PUNCT-DEL: 4,042 + PUNCT-ADD: 1,344 + PUNCT-SUBST: 618 + H-STRUCT: 3,689 + H-TYPE: 3,689)

**Data Source**: `global_statistical_summary_features.csv` (Level 1)

### Level 2: Feature-Value Pair Questions

**Q**: What is the most common morphological feature transformation?
**A**: Tense=Past → Tense=Pres (115 occurrences, 28.19% of FEAT-CHG events)

**Q**: What function words are deleted most often?
**A**: AUX-DEL→ABSENT (2,851 times, 40.08% of FW-DEL events)

**Data Source**: `global_feature_value_analysis_feature_FEAT-CHG.csv` (Level 2)

### Level 3: Value Distribution Questions

**Q**: Which feature has the most diverse transformations?
**A**: DEP-REL-CHG with 1,023 unique transformation types and 8.35 bits entropy

**Q**: Which feature is most concentrated?
**A**: CONST-MOV with only 2 transformation types and 0.40 bits entropy (92% are CONST-FRONT→CONST-FRONT)

**Data Source**: `global_feature_value_analysis_value_statistics.csv` (Level 3)

---

## Usage Recommendations

### For Quantitative Analysis
1. Start with **Level 1** for overall feature frequency
2. Drill down to **Level 2** for specific transformation patterns
3. Use **Level 3** for statistical properties (entropy, diversity)

### For Linguistic Research
1. Use **Level 2** to identify systematic transformations
2. Compare **Level 3** entropy across features to find regular vs. variable patterns
3. Use **Level 1** for cross-newspaper feature comparison

### For Computational Modeling
1. **Level 3** provides perplexity estimates (via entropy)
2. **Level 2** provides training data for transformation rules
3. **Level 1** provides feature weights for models

---

## Verification Commands

```bash
# Count Level 1 files (feature-level)
find output -name "*statistical_summary_features.csv" | wc -l
# Expected: 4 (3 newspapers + GLOBAL)

# Count Level 2 files (per-feature value pairs)
find output -name "*feature_value_analysis_feature_*.csv" | wc -l
# Expected: 120 (30 features × 4 views)

# Count Level 3 files (value statistics)
find output -name "*feature_value_analysis_value_statistics.csv" | wc -l
# Expected: 4 (3 newspapers + GLOBAL)

# Verify GLOBAL data exists
ls output/GLOBAL_ANALYSIS/global_*.csv | wc -l
# Expected: 40+ files

# Check all newspapers have same structure
for np in Times-of-India Hindustan-Times The-Hindu; do
  echo "$np:"
  ls output/$np/*.csv | wc -l
done
```

---

## Summary

✅ **All three levels of data are COMPLETE and available**

- **Level 1 (Features)**: 4 files (30 features each)
- **Level 2 (Feature-Value Pairs)**: 120+ files (30 features × 4 views)
- **Level 3 (Value Statistics)**: 4 files (statistics for all features)

**Total CSV files**: ~150 files organized hierarchically
**Total events analyzed**: 123,042 events with context enrichment
**Schema version**: v5.0 (30 features across 5 categories)

All data is available in both per-newspaper and GLOBAL (cross-newspaper) formats.
