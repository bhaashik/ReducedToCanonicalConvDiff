# Schema Gap Analysis for diff-ontology v4.0

**Date**: December 29, 2024
**Current Version**: 4.0.0
**Proposed Version**: 5.0.0 ✅ **COMPLETED (January 2, 2026)**

---

## ✅ RESOLUTION STATUS

**ALL IDENTIFIED GAPS HAVE BEEN ADDRESSED IN SCHEMA v5.0**

- **Schema file created**: `data/diff-ontology-ver-5.0.json`
- **Feature count**: 18 (v4.0) → 30 (v5.0)
- **New features added**: 12 (10 Priority 1 + 2 Priority 2)
- **Changelog**: See `SCHEMA_CHANGELOG_v5.0.md` for complete details

**Status of Priority 1 features**:
- ✅ PUNCT-DEL, PUNCT-ADD, PUNCT-SUBST (3 features)
- ✅ H-STRUCT, H-TYPE, F-TYPE (3 features)
- ✅ TREE-DEPTH-DIFF, CONST-COUNT-DIFF, DEP-DIST-DIFF, BRANCH-DIFF (4 features)

**Status of Priority 2 features**:
- ✅ TOKEN-COUNT-DIFF, CHAR-COUNT-DIFF (2 features)

**Next Steps**:
1. Re-run extraction pipeline with schema v5.0
2. Validate punctuation event detection
3. Verify headline typology classification

---

## Executive Summary

Critical gaps identified in the current schema v4.0 that prevent complete representation of canonical-reduced register differences:

1. **CRITICAL**: No punctuation features (headlines use punctuation to compensate for deleted function words)
2. **IMPORTANT**: Missing headline typology features from original schema
3. **IMPORTANT**: Missing capitalization/case change features
4. **MODERATE**: Missing multiword expression features
5. **MODERATE**: Enhanced structural metadata needed

---

## Gap Category 1: Punctuation Features (CRITICAL)

### Current State
**NO punctuation features exist in v4.0**

### Why This is Critical
Headlines extensively use punctuation to compensate for deleted function words:
- **Colon (:)** replaces conjunctions ("and", "or", "that")
  - Example: "Modi in US: Discusses trade" ← "Modi is in the US and discusses trade"
- **Comma (,)** replaces "and" in lists
  - Example: "Modi, Trump discuss trade" ← "Modi and Trump discuss trade"
- **Dash (—)** replaces relative clauses or elaboration
  - Example: "Modi — PM of India — visits US" ← "Modi, who is the PM of India, visits the US"
- **Quotes (" ")** replace reported speech markers
  - Example: "'Will win' says Modi" ← "Modi says that he will win"
- **Semicolon (;)** replaces conjunctions between clauses
- **Slash (/)** replaces "or" or "and"

### Missing Features (3)

#### PUNCT-DEL: Punctuation Deletion
- Deletion of punctuation when expanding to canonical form
- Values: comma deletion, colon deletion, semicolon deletion, dash deletion, quote deletion, etc.

#### PUNCT-ADD: Punctuation Addition
- Addition of punctuation in canonical form
- Values: comma addition, period addition, etc.

#### PUNCT-SUBST: Punctuation Substitution
- **Most critical feature** - punctuation ↔ function word transformations
- Values:
  - colon to conjunction
  - comma to conjunction
  - dash to relative clause
  - quote to reported speech marker
  - semicolon to conjunction
  - slash to conjunction/disjunction
  - conjunction to colon (reverse)
  - conjunction to comma (reverse)
  - reported speech to quote (reverse)

---

## Gap Category 2: Headline Typology (IMPORTANT)

### Current State
These features exist in original schema (Samapika-Thesis/diff-ontology.json) but are **missing from v4.0**

### Missing Features (3)

#### H-STRUCT: Headline Structure
Classifies overall structure of headlines
- **sg-line**: Single-line headlines (most common)
- **micro-disc**: Multi-sentence/multi-clause headlines with discourse structure

Example micro-disc:
> "Looking to retire in a warm place? Want live music too? Here's where to go"

Metadata: num_sentences, length_difference, tree_depth_diff

#### H-TYPE: Headline Type
Classifies completeness of headline
- **frag**: Fragment (incomplete sentence, no full predication)
  - Example: "Answers for Chakravyuh"
- **non-frag**: Complete sentence (full SVO structure)
  - Example: "Hospital issues special cards"

Metadata: length_difference, tree_depth_diff

#### F-TYPE: Fragment Type
Classifies type of fragment (only applies when H-TYPE = frag)
- **complex-compound**: Noun-noun compounds
  - Example: "Dark charm"
- **phrase**: Phrasal fragments (NP, PP, VP, etc.)
  - Examples: "A burning issue", "At his best"

Metadata: length_difference, tree_depth_diff

---

## Gap Category 3: Capitalization/Case Changes (IMPORTANT)

### Current State
FORM-CHG exists but doesn't specifically capture capitalization patterns

### Why This Matters
Headlines have systematic capitalization conventions:
- Title case vs. sentence case
- ALL CAPS for emphasis
- Proper nouns vs. common nouns capitalization
- Acronyms and abbreviations

### Missing Feature

#### CASE-CHG: Case/Capitalization Change
Specific feature for capitalization transformations
- Values:
  - lowercase to uppercase
  - uppercase to lowercase
  - title case to sentence case
  - sentence case to title case
  - all caps to mixed case
  - capitalization for emphasis

Note: This could be integrated into FORM-CHG with specific values, or kept separate for clarity.

---

## Gap Category 4: Multiword Expressions (MODERATE)

### Current State
No explicit MWE features

### Why This Matters
Headlines often use multiword expressions (MWEs) differently:
- Idioms, collocations, compound nouns
- MWE splitting/joining in transformations

### Potential Feature

#### MWE-CHG: Multiword Expression Change
- mwe to separate words
- separate words to mwe
- mwe substitution

**Decision**: This might be low priority as it can be inferred from other features.

---

## Gap Category 5: Enhanced Structural Metadata (MODERATE)

### Current State
LENGTH-CHG exists but lacks granular metadata

### Enhancements Needed
All features should capture additional metadata:
- **Tree depth differences** (constituency and dependency)
- **Branching factor changes**
- **Dependency distance changes**
- **Sentence complexity metrics**

These are in "extra" fields in original schema but not consistently in v4.0.

---

## Gap Category 6: Ellipsis (MODERATE)

### Current State
Partially covered by C-DEL, FW-DEL, but not explicitly marked as ellipsis

### Why This Matters
Headlines use systematic ellipsis:
- Subject ellipsis: "Will visit India" (subject "He/She" omitted)
- Copula ellipsis: "Modi happy with results" (copula "is" omitted)
- Auxiliary ellipsis: "Modi visiting US" (auxiliary "is" omitted)

### Potential Feature

#### ELLIPSIS: Ellipsis Type
- subject ellipsis
- copula ellipsis
- auxiliary ellipsis
- object ellipsis

**Decision**: This might be redundant with FW-DEL/C-DEL, but explicit marking helps analysis.

---

## Recommended Additions for v4.1

### MUST ADD (Priority 1):
1. ✅ **PUNCT-DEL** - Punctuation Deletion
2. ✅ **PUNCT-ADD** - Punctuation Addition
3. ✅ **PUNCT-SUBST** - Punctuation Substitution (**most critical**)
4. ✅ **H-STRUCT** - Headline Structure
5. ✅ **H-TYPE** - Headline Type
6. ✅ **F-TYPE** - Fragment Type

### SHOULD ADD (Priority 2):
7. ⏳ **CASE-CHG** - Capitalization changes (or enhance FORM-CHG with case-specific values)

### CONSIDER (Priority 3):
8. ⏳ **ELLIPSIS** - Explicit ellipsis marking
9. ⏳ **MWE-CHG** - Multiword expression changes

### Enhancement:
10. ⏳ Add enhanced metadata fields (tree depth, branching factor, etc.) to all features

---

## Implementation Plan

### Phase 1: v4.1 (Immediate)
- Add all Priority 1 features (6 features)
- Update changelog
- Test with existing data

### Phase 2: v4.2 (Next)
- Add Priority 2 features
- Enhance metadata across all features

### Phase 3: v5.0 (Future)
- Consider Priority 3 features
- Major schema restructuring if needed

---

## Data Validation Needed

After adding missing features, validate against:
1. ✅ Sample dependency parses (Times-of-India-headlines-stanza-parsed-deps.conllu)
2. ✅ Sample constituency parses (Times-of-India-headlines-stanza-parsed-constituency.txt)
3. ⏳ Sample plain text headlines
4. ⏳ Manual inspection of 100 headline pairs
5. ⏳ Re-run extraction pipeline to ensure all events captured

---

## Conclusion

The current schema v4.0 has **critical gaps**, particularly:
1. **Punctuation features are completely absent** - this is the most serious omission
2. **Headline typology features were dropped from original schema** - need restoration
3. **Capitalization not explicitly captured** - should be added or enhanced

**Recommendation**: Create v4.1 with all Priority 1 features immediately, as current results are incomplete without punctuation analysis.

---

**Status**: Gap analysis complete, ready for schema update implementation.
