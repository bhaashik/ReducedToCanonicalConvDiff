# Three-Level Data Analysis: CONFIRMED ✅

**Date**: 2026-01-03
**Total Events**: 123,042
**Schema Version**: v5.0 (30 features)
**Newspapers**: 3 (Times-of-India, Hindustan-Times, The-Hindu)

---

## Verification Results

✅ **LEVEL 1 (Features)**: 7 files confirmed
✅ **LEVEL 2 (Feature-Value Pairs)**: 120 files confirmed
✅ **LEVEL 3 (Value Statistics)**: 4 files confirmed

**Total CSV files**: 131+ files across all three levels

---

## LEVEL 1: FEATURES (Feature-Level Analysis)

### What it Shows
Aggregate counts for each of the 30 Schema v5.0 features without considering specific values.

### Key Files (7 total)

**GLOBAL**:
- `output/GLOBAL_ANALYSIS/global_statistical_summary_features.csv`
- `output/GLOBAL_ANALYSIS/global_comprehensive_analysis_global.csv`

**Per-Newspaper** (3 files):
- `output/Times-of-India/feature_freq_global.csv`
- `output/Hindustan-Times/feature_freq_global.csv`
- `output/The-Hindu/feature_freq_global.csv`

**Plus**: 2 more comprehensive analysis files

### Sample Data (Top 5 Features)
| Feature | Name | Count | % |
|---------|------|-------|---|
| CONST-MOV | Constituent Movement | 30,289 | 24.62% |
| DEP-REL-CHG | Dependency Relation Change | 26,935 | 21.89% |
| CLAUSE-TYPE-CHG | Clause Type Change | 7,636 | 6.21% |
| FW-DEL | Function Word Deletion | 7,112 | 5.78% |
| PUNCT-DEL | Punctuation Deletion | 4,042 | 3.29% |

---

## LEVEL 2: FEATURE-VALUE PAIRS (Transformation Analysis)

### What it Shows
Specific transformations from canonical_value → headline_value with counts and percentages.

### Key Files (120 total)

**GLOBAL Per-Feature Files** (30 files):
- `output/GLOBAL_ANALYSIS/global_feature_value_analysis_feature_FEAT-CHG.csv`
- `output/GLOBAL_ANALYSIS/global_feature_value_analysis_feature_FW-DEL.csv`
- `output/GLOBAL_ANALYSIS/global_feature_value_analysis_feature_DEP-REL-CHG.csv`
- ... (27 more files, one per feature)

**Per-Newspaper Files** (90 files = 3 newspapers × 30 features):
- `output/Times-of-India/feature_value_analysis_feature_FEAT-CHG.csv`
- `output/Times-of-India/feature_value_analysis_feature_FW-DEL.csv`
- ... (28 more per newspaper)
- Same structure for Hindustan-Times and The-Hindu

### Sample Data (FEAT-CHG - Morphological Transformations)
| Canonical Value | Headline Value | Count | % |
|----------------|----------------|-------|---|
| Tense=Past | Tense=Pres | 115 | 28.19% |
| Number=ABSENT | Number=Sing | 26 | 6.37% |
| Number=Plur | Number=Sing | 26 | 6.37% |
| Person=ABSENT | Person=3 | 22 | 5.39% |
| Mood=ABSENT | Mood=Ind | 22 | 5.39% |

**Total**: 408 FEAT-CHG events across 45 unique transformation types

### Sample Data (FW-DEL - Function Word Deletions)
| Canonical Value | Headline Value | Count | % |
|----------------|----------------|-------|---|
| AUX-DEL | ABSENT | 2,851 | 40.08% |
| ART-DEL | ABSENT | 2,098 | 29.50% |
| SCONJ-DEL | ABSENT | 1,138 | 16.00% |
| DET-DEL | ABSENT | 533 | 7.49% |
| PRON-DEL | ABSENT | 396 | 5.57% |

**Total**: 7,112 FW-DEL events across 6 unique transformation types

---

## LEVEL 3: FEATURE VALUES PER FEATURE (Statistical Properties)

### What it Shows
Distribution statistics for values within each feature: entropy, diversity, concentration metrics.

### Key Files (4 total)

**GLOBAL**:
- `output/GLOBAL_ANALYSIS/global_feature_value_analysis_value_statistics.csv`

**Per-Newspaper** (3 files):
- `output/Times-of-India/feature_value_analysis_value_statistics.csv`
- `output/Hindustan-Times/feature_value_analysis_value_statistics.csv`
- `output/The-Hindu/feature_value_analysis_value_statistics.csv`

### Sample Data (Selected Features)
| Feature | Total | Unique Types | Diversity | Entropy | Top Transform |
|---------|-------|--------------|-----------|---------|---------------|
| FEAT-CHG | 408 | 45 | 29 | 4.22 bits | Tense=Past→Pres |
| FW-DEL | 7,112 | 6 | 6 | 2.01 bits | AUX-DEL→ABSENT |
| DEP-REL-CHG | 26,935 | 1,023 | 46 | 8.35 bits | det→compound |
| CONST-MOV | 30,289 | 2 | 2 | 0.40 bits | CONST-FRONT→FRONT |

**Interpretation**:
- **High Entropy** (DEP-REL-CHG: 8.35 bits): Very unpredictable, 1,023 transformation types
- **Low Entropy** (CONST-MOV: 0.40 bits): Highly predictable, only 2 types (92% fronting)
- **Moderate Entropy** (FEAT-CHG: 4.22 bits): Some patterns, 45 transformation types

---

## Data Hierarchy Visualization

```
123,042 TOTAL EVENTS
    │
    ├─── LEVEL 1: 30 FEATURES (aggregate counts)
    │    │
    │    ├─ CONST-MOV: 30,289 events
    │    ├─ DEP-REL-CHG: 26,935 events
    │    ├─ FEAT-CHG: 408 events
    │    └─ ... (27 more)
    │
    ├─── LEVEL 2: 5,000+ FEATURE-VALUE PAIRS (transformations)
    │    │
    │    ├─ FEAT-CHG:
    │    │   ├─ Tense=Past→Tense=Pres: 115 events
    │    │   ├─ Number=ABSENT→Number=Sing: 26 events
    │    │   ├─ Number=Plur→Number=Sing: 26 events
    │    │   └─ ... (42 more types)
    │    │
    │    ├─ FW-DEL:
    │    │   ├─ AUX-DEL→ABSENT: 2,851 events
    │    │   ├─ ART-DEL→ABSENT: 2,098 events
    │    │   └─ ... (4 more types)
    │    │
    │    └─ ... (28 more features)
    │
    └─── LEVEL 3: 30 FEATURES (statistical properties)
         │
         ├─ FEAT-CHG: 45 types, 4.22 bits entropy
         ├─ FW-DEL: 6 types, 2.01 bits entropy
         └─ ... (28 more)
```

---

## Granularity Comparison

### Same Question, Three Levels of Detail:

**Q: Tell me about morphological feature changes**

**LEVEL 1 Answer**:
```
FEAT-CHG: 408 events (0.33% of all 123,042 events)
```

**LEVEL 2 Answer**:
```
FEAT-CHG: 408 events across 45 transformation types
Top transformations:
  1. Tense=Past→Tense=Pres: 115 (28.19%)
  2. Number=ABSENT→Number=Sing: 26 (6.37%)
  3. Number=Plur→Number=Sing: 26 (6.37%)
  ... (42 more)
```

**LEVEL 3 Answer**:
```
FEAT-CHG statistical properties:
  - 45 unique transformation types
  - 29 canonical values, 28 headline values
  - Entropy: 4.22 bits (moderate diversity)
  - Top 3 concentration: 40.93% (fairly distributed)
  - Most frequent: Tense=Past→Tense=Pres
```

---

## File Access Quick Reference

### LEVEL 1 (Feature Counts)
```bash
# GLOBAL
cat output/GLOBAL_ANALYSIS/global_statistical_summary_features.csv

# Per-Newspaper
cat output/Times-of-India/feature_freq_global.csv
cat output/Hindustan-Times/feature_freq_global.csv
cat output/The-Hindu/feature_freq_global.csv
```

### LEVEL 2 (Feature-Value Pairs)
```bash
# GLOBAL - All pairs combined
cat output/GLOBAL_ANALYSIS/global_feature_value_pair_analysis_global_pairs.csv

# GLOBAL - Specific feature (e.g., FEAT-CHG)
cat output/GLOBAL_ANALYSIS/global_feature_value_analysis_feature_FEAT-CHG.csv

# Per-Newspaper - Specific feature
cat output/Times-of-India/feature_value_analysis_feature_FEAT-CHG.csv
```

### LEVEL 3 (Value Statistics)
```bash
# GLOBAL
cat output/GLOBAL_ANALYSIS/global_feature_value_analysis_value_statistics.csv

# Per-Newspaper
cat output/Times-of-India/feature_value_analysis_value_statistics.csv
cat output/Hindustan-Times/feature_value_analysis_value_statistics.csv
cat output/The-Hindu/feature_value_analysis_value_statistics.csv
```

---

## Documentation Files Created

1. **`DATA_ORGANIZATION_THREE_LEVELS.md`** (16 KB)
   - Complete reference with all details
   - File structure, schema categories
   - Example queries, verification commands

2. **`DATA_QUICK_REFERENCE.md`** (2 KB)
   - One-page quick lookup
   - Direct file paths for all three levels

3. **`DATA_SAMPLES_ALL_LEVELS.md`** (9 KB)
   - Real data samples from each level
   - Side-by-side comparisons
   - Guidance on choosing the right level

4. **`THREE_LEVEL_DATA_CONFIRMED.md`** (This file)
   - Verification summary
   - File counts and samples

---

## Schema v5.0 Feature Breakdown

### 5 Categories, 30 Features

**LEXICAL** (5 features):
- FW-DEL (7,112), FW-ADD (485), C-DEL (2,572), C-ADD (1,430), FORM-CHG (308)

**MORPHOLOGICAL** (4 features):
- FEAT-CHG (408), POS-CHG (256), LEMMA-CHG (65), VERB-FORM-CHG (38)

**SYNTACTIC** (7 features):
- DEP-REL-CHG (26,935), HEAD-CHG (760), CLAUSE-TYPE-CHG (7,636), TOKEN-REORDER (21)
- CONST-MOV (30,289), CONST-ADD (329), CONST-REM (1,008)

**STRUCTURAL** (9 features):
- TREE-DEPTH-DIFF (3,689), BRANCH-DIFF (3,689), DEP-DIST-DIFF (3,689)
- LENGTH-CHG (3,276), CONST-COUNT-DIFF (3,689)
- TED-SIMPLE (3,234), TED-RTED (3,316), TED-ZHANG-SHASHA (2,713), TED-KLEIN (2,713)

**PUNCTUATION** (5 features):
- PUNCT-DEL (4,042), PUNCT-ADD (1,344), PUNCT-SUBST (618)
- H-STRUCT (3,689), H-TYPE (3,689)

---

## Verification Commands

```bash
# Verify LEVEL 1 files exist
find output -name "*statistical_summary_features.csv" -o -name "feature_freq_global.csv"
# Expected: 7 files

# Verify LEVEL 2 files exist
find output -name "*feature_value_analysis_feature_*.csv" | wc -l
# Expected: 120 files (30 features × 4 views)

# Verify LEVEL 3 files exist
find output -name "*feature_value_analysis_value_statistics.csv"
# Expected: 4 files (3 newspapers + GLOBAL)

# View sample LEVEL 1 data
head -10 output/GLOBAL_ANALYSIS/global_statistical_summary_features.csv

# View sample LEVEL 2 data (FEAT-CHG)
head -20 output/GLOBAL_ANALYSIS/global_feature_value_analysis_feature_FEAT-CHG.csv

# View sample LEVEL 3 data
head -10 output/GLOBAL_ANALYSIS/global_feature_value_analysis_value_statistics.csv
```

---

## Summary

✅ **ALL THREE LEVELS CONFIRMED AND DOCUMENTED**

**Data Coverage**:
- **131+ CSV files** organized across three hierarchical levels
- **123,042 events** with full context metadata
- **30 features** from Schema v5.0
- **3 newspapers** plus GLOBAL aggregation
- **5,000+ unique transformations** across all features

**Documentation**:
- 4 comprehensive markdown files
- Sample data at all levels
- Quick reference guides
- Verification commands

**Status**: Complete and ready for analysis at all three levels of granularity.
