# Data Samples: All Three Levels

## LEVEL 1: FEATURES (Aggregate Counts)

**File**: `output/GLOBAL_ANALYSIS/global_statistical_summary_features.csv`

```csv
feature_id,feature_name,total_occurrences,percentage_of_total
CONST-MOV,Constituent Movement,30289,24.62%
DEP-REL-CHG,Dependency Relation Change,26935,21.89%
CLAUSE-TYPE-CHG,Clause Type Change,7636,6.21%
FW-DEL,Function Word Deletion,7112,5.78%
PUNCT-DEL,Punctuation Deletion,4042,3.29%
FEAT-CHG,Morphological Feature Change,408,0.33%
POS-CHG,Part of Speech Change,256,0.21%
...
```

**Insight**: Shows which features occur most frequently (CONST-MOV and DEP-REL-CHG dominate with ~46% of all events).

---

## LEVEL 2: FEATURE-VALUE PAIRS (Specific Transformations)

### Example 1: Morphological Features (FEAT-CHG)
**File**: `output/GLOBAL_ANALYSIS/global_feature_value_analysis_feature_FEAT-CHG.csv`

```csv
canonical_value,headline_value,transformation,count,percentage
Tense=Past,Tense=Pres,Tense=Past→Tense=Pres,115,28.19%
Number=ABSENT,Number=Sing,Number=ABSENT→Number=Sing,26,6.37%
Number=Plur,Number=Sing,Number=Plur→Number=Sing,26,6.37%
Person=ABSENT,Person=3,Person=ABSENT→Person=3,22,5.39%
Mood=ABSENT,Mood=Ind,Mood=ABSENT→Mood=Ind,22,5.39%
VerbForm=Part,VerbForm=Fin,VerbForm=Part→VerbForm=Fin,15,3.68%
...
```

**Insight**: Past tense → Present tense is the dominant morphological transformation (28% of all FEAT-CHG events).

### Example 2: Function Word Deletion (FW-DEL)
**File**: `output/GLOBAL_ANALYSIS/global_feature_value_analysis_feature_FW-DEL.csv`

```csv
canonical_value,headline_value,transformation,count,percentage
AUX-DEL,ABSENT,AUX-DEL→ABSENT,2851,40.08%
ART-DEL,ABSENT,ART-DEL→ABSENT,2098,29.50%
SCONJ-DEL,ABSENT,SCONJ-DEL→ABSENT,1138,16.00%
DET-DEL,ABSENT,DET-DEL→ABSENT,533,7.49%
PRON-DEL,ABSENT,PRON-DEL→ABSENT,396,5.57%
ADP-DEL,ABSENT,ADP-DEL→ABSENT,96,1.35%
```

**Insight**: Auxiliary verbs (40%), articles (29.5%), and subordinating conjunctions (16%) account for 85% of function word deletions.

### Example 3: Dependency Relations (DEP-REL-CHG)
**File**: `output/GLOBAL_ANALYSIS/global_feature_value_analysis_feature_DEP-REL-CHG.csv` (top 10)

```csv
canonical_value,headline_value,transformation,count,percentage
det,compound,det→compound,700,2.60%
mark,xcomp,mark→xcomp,410,1.52%
nsubj,obj,nsubj→obj,385,1.43%
case,compound,case→compound,330,1.23%
cc,compound,cc→compound,295,1.10%
...
```

**Insight**: 1,023 unique dependency relation changes show high variability (no single transformation dominates).

---

## LEVEL 3: FEATURE VALUES PER FEATURE (Statistical Properties)

**File**: `output/GLOBAL_ANALYSIS/global_feature_value_analysis_value_statistics.csv`

```csv
feature_id,total_transformations,unique_types,can_diversity,head_diversity,entropy,top3_conc,most_frequent
FEAT-CHG,408,45,29,28,4.22,0.41,Tense=Past→Tense=Pres
FW-DEL,7112,6,6,1,2.01,0.83,AUX-DEL→ABSENT
DEP-REL-CHG,26935,1023,46,46,8.35,0.07,det→compound
CONST-MOV,30289,2,2,2,0.40,1.00,CONST-FRONT→CONST-FRONT
PUNCT-DEL,4042,8,8,1,1.10,0.94,period→
CLAUSE-TYPE-CHG,7636,7,5,5,2.31,0.78,Part→Fin
C-DEL,2572,4,4,1,1.51,0.99,VERB-DEL→ABSENT
```

**Columns Explained**:
- `total_transformations`: Total events for this feature
- `unique_types`: Number of distinct canonical→headline transformations
- `can_diversity`: Unique values in canonical register
- `head_diversity`: Unique values in headline register
- `entropy`: Shannon entropy (bits) - higher = more unpredictable
- `top3_conc`: Top 3 concentration ratio - higher = more concentrated
- `most_frequent`: Most common transformation

**Insights**:
1. **High Entropy Features** (diverse, unpredictable):
   - DEP-REL-CHG: 8.35 bits, 1,023 types → Very variable
   - BRANCH-DIFF: 9.06 bits, 1,178 types → Very variable

2. **Low Entropy Features** (concentrated, predictable):
   - CONST-MOV: 0.40 bits, 2 types → Highly predictable (92% fronting)
   - PUNCT-DEL: 1.10 bits, 8 types → Fairly predictable (80% period deletion)

3. **Moderate Entropy Features** (some patterns):
   - FEAT-CHG: 4.22 bits, 45 types → Moderate variability
   - FW-DEL: 2.01 bits, 6 types → Some concentration (83% in top 3)

---

## Comparison Across Levels

### Same Information, Different Granularity:

**Q: How many morphological feature changes are there?**

**Level 1 Answer** (Feature-level):
```
FEAT-CHG: 408 events total (0.33% of all events)
```

**Level 2 Answer** (Value-pair-level):
```
408 events distributed across 45 transformation types:
- Tense=Past→Tense=Pres: 115 (28.19%)
- Number=ABSENT→Number=Sing: 26 (6.37%)
- Number=Plur→Number=Sing: 26 (6.37%)
- ... (42 more types)
```

**Level 3 Answer** (Statistical properties):
```
FEAT-CHG statistics:
- 45 unique transformation types
- 29 canonical values, 28 headline values
- Entropy: 4.22 bits (moderate diversity)
- Top 3 concentration: 40.93% (fairly distributed)
```

---

## How to Choose the Right Level

### Use LEVEL 1 when you need:
- Overall feature frequency comparison
- "Which features are most common?"
- "What percentage of events are morphological?"
- Cross-newspaper feature comparison

### Use LEVEL 2 when you need:
- Specific transformation patterns
- "Which tense transformations occur?"
- "What function words are deleted?"
- Training data for transformation models

### Use LEVEL 3 when you need:
- Statistical properties of transformations
- "How predictable are transformations?"
- "Which features show the most diversity?"
- Entropy/perplexity estimates for modeling

---

## File Locations Summary

```
LEVEL 1 (Features):
  GLOBAL: output/GLOBAL_ANALYSIS/global_statistical_summary_features.csv
  Per-NP: output/{Newspaper}/feature_freq_global.csv

LEVEL 2 (Feature-Value Pairs):
  GLOBAL: output/GLOBAL_ANALYSIS/global_feature_value_pair_analysis_global_pairs.csv
  GLOBAL (per-feature): output/GLOBAL_ANALYSIS/global_feature_value_analysis_feature_{FEATURE}.csv
  Per-NP: output/{Newspaper}/feature_value_pair_analysis_global_pairs.csv
  Per-NP (per-feature): output/{Newspaper}/feature_value_analysis_feature_{FEATURE}.csv

LEVEL 3 (Value Statistics):
  GLOBAL: output/GLOBAL_ANALYSIS/global_feature_value_analysis_value_statistics.csv
  Per-NP: output/{Newspaper}/feature_value_analysis_value_statistics.csv

RAW EVENTS:
  output/{Newspaper}/events_global.csv (123,042 total events)
```

---

## Total Data Available

- **Features**: 30
- **Newspapers**: 3 (Times-of-India, Hindustan-Times, The-Hindu)
- **Total Events**: 123,042
- **Unique Transformation Types**: 5,000+ (across all features)
- **CSV Files**: 150+
- **Visualizations**: 335 PNG files
