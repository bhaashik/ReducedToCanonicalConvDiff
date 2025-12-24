# Difference Ontology Schema: Version 4.0 Changelog

## Overview

Version 4.0 enriches the morphological feature change taxonomy to include **ALL** granular morphological features extracted from Stanza Universal Dependencies parses. This ensures complete morphosyntactic coverage for the comparative analysis.

## Major Changes from v3.0 to v4.0

### Morphological Feature Change (FEAT-CHG) - SIGNIFICANTLY ENRICHED

**v3.0 had only 7 feature types**:
1. Tense change
2. Number change
3. Aspect change
4. Voice change
5. Mood change
6. Case change
7. Degree change

**v4.0 now has 20 comprehensive feature types** (13 NEW):

#### Retained from v3.0 (7):
1. ✓ Tense change (`TENSE-CHG`)
2. ✓ Number change (`NUM-CHG`)
3. ✓ Aspect change (`ASP-CHG`)
4. ✓ Voice change (`VOICE-CHG`)
5. ✓ Mood change (`MOOD-CHG`)
6. ✓ Case change (`CASE-CHG`)
7. ✓ Degree change (`DEG-CHG`)

#### NEW in v4.0 (13):
8. **Person change** (`PERSON-CHG`) - 1st, 2nd, 3rd person
   - Example: "I go" (1st) vs "he goes" (3rd)

9. **Gender change** (`GENDER-CHG`) - Masculine, Feminine, Neuter
   - Example: "his" (Masc) vs "her" (Fem)

10. **Definiteness change** (`DEF-CHG`) - Definite vs Indefinite
    - Example: "the" (Def) vs "a" (Ind)

11. **Pronoun Type change** (`PRONTYPE-CHG`) - Art, Dem, Ind, Int, Prs, Rel
    - Example: "the" (Art) vs "this" (Dem) vs "he" (Prs)

12. **Possessive change** (`POSS-CHG`) - Possessive marking
    - Example: "his" (Poss=Yes) vs "he" (Poss=No)

13. **Number Type change** (`NUMTYPE-CHG`) - Cardinal, Ordinal, Fraction, Multiplicative
    - Example: "one" (Card) vs "first" (Ord)

14. **Number Form change** (`NUMFORM-CHG`) - Word, Digit, Roman
    - Example: "one" (Word) vs "1" (Digit)

15. **Polarity change** (`POL-CHG`) - Positive vs Negative
    - Example: "is" (Pos) vs "isn't" (Neg)

16. **Reflexive change** (`REFLEX-CHG`) - Reflexive pronouns
    - Example: "him" vs "himself" (Reflex=Yes)

17. **VerbForm change** (`VFORM-CHG`) - Finite, Infinitive, Participle, Gerund
    - Example: "goes" (Fin) vs "going" (Part) vs "to go" (Inf)
    - Note: Also captured separately in VERB-FORM-CHG event

18. **Abbreviation change** (`ABBR-CHG`) - Abbreviation marking
    - Example: "Doctor" vs "Dr." (Abbr=Yes)

19. **External POS change** (`EXTPOS-CHG`) - When word functions as different POS
    - Example: Noun functioning as adjective

20. **Foreign change** (`FOREIGN-CHG`) - Foreign word marking
    - Example: "raison d'être" (Foreign=Yes)

## Technical Changes

### 1. Enhanced FEAT-CHG Structure

**v3.0 structure**:
```json
{
  "values": ["tense change", "number change", "aspect change", "voice change",
             "mood change", "case change", "degree change"],
  "extra": ["source_feats", "target_feats"]
}
```

**v4.0 structure**:
```json
{
  "values": [
    "tense change", "number change", "aspect change", "voice change",
    "mood change", "case change", "degree change",
    "person change", "gender change", "definiteness change",
    "pronoun type change", "possessive change", "number type change",
    "number form change", "polarity change", "reflexive change",
    "verbform change", "abbreviation change", "external pos change",
    "foreign change"
  ],
  "extra": ["source_feats", "target_feats", "feature_name", "source_value", "target_value"],
  "feature_definitions": { /* Detailed documentation of each feature */ }
}
```

### 2. Added Feature Definitions

v4.0 includes comprehensive documentation for each morphological feature with:
- **Feature name**: Official Universal Dependencies feature name
- **Description**: What the feature represents
- **Possible values**: Valid values from UD specification

Example:
```json
"Person": "Grammatical person: 1, 2, 3",
"Gender": "Grammatical gender: Masc, Fem, Neut",
"Definite": "Definiteness: Def, Ind"
```

### 3. Enhanced Extra Fields

**v3.0**: `["source_feats", "target_feats"]`
**v4.0**: `["source_feats", "target_feats", "feature_name", "source_value", "target_value"]`

This allows tracking:
- `feature_name`: Which specific feature changed (e.g., "Person")
- `source_value`: Original value (e.g., "1")
- `target_value`: New value (e.g., "3")

## Data Source

All features extracted from **Stanza Universal Dependencies CoNLL-U parses**:
- File format: CoNLL-U (column 6: FEATS)
- Parse type: dependency
- Files location: `data/input/dependecy-parsed/*.conllu`

## Impact on Analysis

### Task 1: Comparative Study
- **Complete morphosyntactic coverage**: All morphological differences now captured
- **Granular analysis**: Can analyze each feature type separately
- **Linguistic validity**: Matches UD standard for morphological annotation

### Task 2: Transformation Study
- **Richer transformation rules**: Rules can target specific morphological features
- **Better coverage estimation**: Morphological rules now comprehensive
- **Feature-based transformations**: Can model person/gender/definiteness changes

### Task 3: Complexity & Similarity
- **Enhanced perplexity analysis**: More granular feature distributions
- **Complete morphological complexity**: All morphological dimensions measured
- **Better correlation analysis**: More features to correlate with MT metrics

## Compatibility

### Backward Compatibility
- ✓ v3.0 events still valid in v4.0
- ✓ All v3.0 feature types retained
- ✓ Same event structure and mnemonics
- ✓ Only FEAT-CHG enriched, others unchanged

### Migration Required
- Update comparison code to extract all 20 feature types
- Regenerate all events_global.csv files
- Rerun all analyses with enriched schema

## Validation Checklist

Before using v4.0, verify:
- [ ] All 20 FEAT-CHG values defined
- [ ] Feature definitions match UD specification
- [ ] Stanza CoNLL-U files contain these features
- [ ] Comparison code extracts all features
- [ ] Events_global.csv includes all feature changes
- [ ] No features from data are missing from schema

## Next Steps

1. **Update comparison code** to:
   - Load v4.0 schema
   - Extract all 20 morphological feature types from CoNLL-U
   - Generate separate event for each feature change
   - Store feature_name, source_value, target_value

2. **Regenerate Task 1 outputs**:
   - Run `register_comparison/compare_registers.py` with v4.0 schema
   - Verify events_global.csv includes all new feature types
   - Check statistics for each feature type

3. **Manual verification**:
   - User reviews events_global.csv
   - Confirms all morphological changes captured
   - Approves schema before proceeding to Tasks 2 & 3

## Schema File Locations

- **Current (v4.0)**: `data/diff-ontology-ver-4.0.json`
- **Previous (v3.0)**: `data/diff-ontology-ver-3.0.json` (archived)

---

**Version**: 4.0.0
**Date**: 2025-12-23
**Changes**: +13 morphological feature types (from 7 to 20)
**Impact**: Complete morphosyntactic coverage for comparative analysis
**Status**: Ready for implementation and testing
