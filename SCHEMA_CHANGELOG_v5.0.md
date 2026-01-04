# Schema Changelog: v5.0

**Date**: January 2, 2026
**Previous Version**: 4.0.0
**Current Version**: 5.0.0
**Total Features**: 18 → 30 (+12 features)

---

## Executive Summary

Schema v5.0 addresses **critical gaps** identified in v4.0 through comprehensive gap analysis. The most serious omission was the complete absence of punctuation features, which are essential for capturing how headlines use punctuation to compensate for deleted function words.

This update adds 12 new features in two priority categories:
- **Priority 1** (10 features): Critical for transformation analysis
- **Priority 2** (2 features): Simple length metrics calculated anyway

---

## Critical Gap Addressed

### The Punctuation Problem

Headlines extensively use **punctuation as function word substitutes**:

- **Colon (:)** replaces conjunctions ("and", "or", "that")
  - Example: "Modi in US: Discusses trade" ← "Modi is in the US and discusses trade"
- **Comma (,)** replaces "and" in lists
  - Example: "Modi, Trump discuss trade" ← "Modi and Trump discuss trade"
- **Dash (—)** replaces relative clauses
  - Example: "Modi — PM of India — visits US" ← "Modi, who is the PM of India, visits the US"
- **Quotes (" ")** replace reported speech markers
  - Example: "'Will win' says Modi" ← "Modi says that he will win"

**v4.0 had ZERO features to capture this phenomenon.**

---

## New Features Added

### Priority 1: Critical Features (10)

#### 1. Punctuation Features (3)

**PUNCT-DEL** - Punctuation Deletion (Position 8)
- **Category**: lexical/punctuation
- **Values** (12): comma deletion, colon deletion, semicolon deletion, dash deletion, hyphen deletion, period deletion, exclamation mark deletion, question mark deletion, quote deletion, parenthesis deletion, slash deletion, apostrophe deletion
- **Parse Types**: dependency, constituency
- **Extra Fields**: deleted_punctuation, position, context

**PUNCT-ADD** - Punctuation Addition (Position 9)
- **Category**: lexical/punctuation
- **Values** (12): Same as PUNCT-DEL but "addition"
- **Parse Types**: dependency, constituency
- **Extra Fields**: added_punctuation, position, context

**PUNCT-SUBST** - Punctuation Substitution (Position 10) ⭐ **MOST CRITICAL**
- **Category**: lexical/punctuation
- **Description**: Substitution between punctuation marks and function words
- **Values** (19):
  - Bidirectional transformations:
    - colon ↔ conjunction
    - comma ↔ conjunction
    - dash ↔ relative clause
    - dash ↔ conjunction
    - semicolon ↔ conjunction
    - quote ↔ reported speech
    - comma ↔ preposition
    - slash ↔ conjunction
    - slash ↔ disjunction
  - other punctuation substitution
- **Parse Types**: dependency, constituency
- **Extra Fields**: source_element, target_element, transformation_type, context

#### 2. Headline Typology Features (3)

These features were present in the original schema (Samapika-Thesis/diff-ontology.json) but missing from v4.0.

**H-STRUCT** - Headline Structure (Position 19)
- **Category**: register/headline-typology
- **Values** (2):
  - `single-line`: Single sentence or clause headline (most common)
  - `micro-discourse`: Multi-sentence/multi-clause with discourse structure
- **Example micro-disc**: "Looking to retire in a warm place? Want live music too? Here's where to go"
- **Parse Types**: dependency, constituency
- **Extra Fields**: num_sentences, num_clauses, length_difference, tree_depth_diff

**H-TYPE** - Headline Type (Position 20)
- **Category**: register/headline-typology
- **Values** (2):
  - `fragment`: Incomplete sentence, no full predication (e.g., "Answers for Chakravyuh")
  - `non-fragment`: Complete SVO structure (e.g., "Hospital issues special cards")
- **Parse Types**: dependency, constituency
- **Extra Fields**: length_difference, tree_depth_diff, has_predicate

**F-TYPE** - Fragment Type (Position 21)
- **Category**: register/headline-typology
- **Applies When**: H-TYPE = fragment
- **Values** (2):
  - `complex-compound`: Noun-noun compounds (e.g., "Dark charm")
  - `phrase`: Phrasal fragments - NP, PP, VP, etc. (e.g., "A burning issue", "At his best")
- **Parse Types**: dependency, constituency
- **Extra Fields**: phrase_type, length_difference, tree_depth_diff

#### 3. Structural Complexity Features (4)

**TREE-DEPTH-DIFF** - Tree Depth Difference (Position 22)
- **Category**: structural/complexity
- **Values**: numeric
- **Description**: Difference in parse tree depth (both constituency and dependency)
- **Parse Types**: dependency, constituency
- **Extra Fields**: headline_depth, canonical_depth, depth_ratio, parse_type

**CONST-COUNT-DIFF** - Constituent Count Difference (Position 23)
- **Category**: structural/complexity
- **Values**: numeric
- **Description**: Difference in number of syntactic constituents
- **Parse Types**: constituency
- **Extra Fields**: headline_constituent_count, canonical_constituent_count, reduction_ratio

**DEP-DIST-DIFF** - Dependency Distance Difference (Position 24)
- **Category**: structural/complexity
- **Values**: numeric
- **Description**: Difference in average dependency distance
- **Parse Types**: dependency
- **Extra Fields**: headline_avg_dep_distance, canonical_avg_dep_distance, distance_ratio

**BRANCH-DIFF** - Branching Factor Difference (Position 25)
- **Category**: structural/complexity
- **Values**: numeric
- **Description**: Difference in average branching factor
- **Parse Types**: constituency, dependency
- **Extra Fields**: headline_avg_branching, canonical_avg_branching, branching_ratio, parse_type

### Priority 2: Simple Length Features (2)

**TOKEN-COUNT-DIFF** - Token Count Difference (Position 29)
- **Category**: statistical/length
- **Values**: numeric
- **Description**: Difference in number of tokens
- **Parse Types**: dependency, constituency
- **Extra Fields**: headline_token_count, canonical_token_count, reduction_ratio

**CHAR-COUNT-DIFF** - Character Count Difference (Position 30)
- **Category**: statistical/length
- **Values**: numeric
- **Description**: Difference in character count
- **Parse Types**: dependency, constituency
- **Extra Fields**: headline_char_count, canonical_char_count, reduction_ratio

---

## Feature Organization in v5.0

```
Positions 1-7:   Lexical features (existing from v4.0)
Positions 8-10:  Punctuation features (NEW)
Positions 11-17: Morphological & syntactic features (existing from v4.0)
Position 18:     Clause type change (existing from v4.0)
Positions 19-21: Headline typology features (NEW)
Positions 22-25: Structural complexity features (NEW)
Position 26:     Verb form change (existing from v4.0)
Position 27:     Tree Edit Distance (existing from v4.0)
Position 28:     Sentence Length Change (existing from v4.0)
Positions 29-30: Token & character count differences (NEW)
```

---

## Feature Count by Category

| Category | v4.0 Count | v5.0 Count | Change |
|----------|------------|------------|--------|
| Lexical | 7 | 10 | +3 (punctuation) |
| Morphological | 2 | 2 | - |
| Syntactic | 5 | 5 | - |
| Word-order | 2 | 2 | - |
| Register | 0 | 3 | +3 (headline typology) |
| Structural | 2 | 6 | +4 (complexity metrics) |
| Statistical | 0 | 2 | +2 (length metrics) |
| **TOTAL** | **18** | **30** | **+12** |

---

## Parse Type Coverage

### Dependency-only features (3):
- FEAT-CHG (Morphological Feature Change)
- DEP-DIST-DIFF (Dependency Distance Difference)
- DEP-REL-CHG (Dependency Relation Change)

### Constituency-only features (2):
- CONST-COUNT-DIFF (Constituent Count Difference)
- TED (Tree Edit Distance)

### Both parse types (25):
- All other features

---

## Backward Compatibility

### Breaking Changes: **NONE**

All existing v4.0 features are **unchanged**. New features are purely additive.

### Migration Path

1. **Extract new features** from existing data:
   - Punctuation features can be extracted from plain text and parses
   - Headline typology can be computed from parse structures
   - Complexity metrics can be computed from existing parses

2. **Re-run extraction pipeline**:
   ```bash
   python run_task1_all_newspapers.py
   ```

3. **Validate results**:
   - Check that punctuation events are now captured
   - Verify headline classification (fragment vs. non-fragment)
   - Compare complexity metrics across registers

---

## Validation Requirements

After updating to v5.0, the following validation is required:

### 1. Schema Validation ✅
- [x] JSON schema loads without errors
- [x] All 30 features have required fields
- [x] Value mnemonics are unique within features
- [x] Parse types are valid

### 2. Data Validation ⏳
- [ ] Test with sample dependency parses
- [ ] Test with sample constituency parses
- [ ] Manual inspection of 100 headline pairs
- [ ] Verify punctuation events are captured
- [ ] Verify headline typology classification

### 3. Pipeline Validation ⏳
- [ ] Re-run extraction pipeline
- [ ] Check output CSV for new features
- [ ] Validate feature frequencies
- [ ] Check cross-newspaper consistency

---

## Example Events with New Features

### Punctuation Substitution Example

**Headline**: `Modi in US: Discusses trade`
**Canonical**: `Modi is in the US and discusses trade`

**Events**:
- `PUNCT-SUBST`: colon to conjunction (COLON2CONJ)
- `FW-ADD`: article addition ("the")
- `FW-ADD`: auxiliary addition ("is")

### Headline Typology Example

**Fragment Headline**: `Answers for Chakravyuh`

**Events**:
- `H-STRUCT`: single-line
- `H-TYPE`: fragment (no full predication)
- `F-TYPE`: phrase (NP fragment)

**Non-fragment Headline**: `Hospital issues special cards`

**Events**:
- `H-STRUCT`: single-line
- `H-TYPE`: non-fragment (complete SVO)

---

## Impact on Research Tasks

### Task 1: Comparative Study ⭐⭐⭐
**High Impact** - Punctuation and headline typology features will significantly enrich the feature distribution analysis.

### Task 2: Transformation Study ⭐⭐⭐
**High Impact** - Punctuation substitution rules will add a new dimension to transformation analysis. Headline typology will enable fragment-specific rule extraction.

### Task 3: Complexity & Similarity Study ⭐⭐
**Moderate Impact** - Structural complexity metrics will enhance multi-level complexity analysis already performed.

---

## Known Limitations

1. **Punctuation detection relies on parses**: Some punctuation may not be in parse trees
2. **Headline typology classification**: May need manual validation for edge cases
3. **Complexity metrics**: Require complete parse trees (may fail for malformed sentences)

---

## Future Enhancements (v6.0+)

### Considered but deferred:
1. **CASE-CHG** - Capitalization changes (can be integrated into FORM-CHG)
2. **ELLIPSIS** - Explicit ellipsis marking (redundant with FW-DEL/C-DEL)
3. **MWE-CHG** - Multiword expression changes (can be inferred from other features)

### Potential additions:
1. Enhanced metadata fields (tree depth, branching factor) for ALL features
2. Cross-feature co-occurrence patterns
3. Discourse-level features for micro-discourse headlines

---

## Changelog Summary

```json
"changelog": {
  "5.0.0": "Added critical missing features: Priority 1 - (1) Punctuation features (PUNCT-DEL, PUNCT-ADD, PUNCT-SUBST) to capture punctuation-function word transformations; (2) Headline typology (H-STRUCT, H-TYPE, F-TYPE) for register classification; (3) Structural complexity features (TREE-DEPTH-DIFF, CONST-COUNT-DIFF, DEP-DIST-DIFF, BRANCH-DIFF). Priority 2 - Simple length features (TOKEN-COUNT-DIFF, CHAR-COUNT-DIFF) for statistical analysis.",
  "4.0.0": "Enriched FEAT-CHG with all morphological features from Stanza: Person, Gender, Definite, PronType, Poss, NumType, NumForm, Polarity, Reflex, Abbr, ExtPos, Foreign. Complete morphosyntactic coverage."
}
```

---

## Contributors

- **Gap Analysis**: Based on SCHEMA_GAP_ANALYSIS.md (December 29, 2024)
- **Original Schema**: Samapika Thesis (diff-ontology.json)
- **Implementation**: Schema v5.0 (January 2, 2026)

---

**Status**: ✅ Schema v5.0 created and validated
**Next Steps**: Re-run extraction pipeline with new schema
