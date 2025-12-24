# Complete Morphological Feature Analysis
## Schema v4.0: All 20 Morphological Features

**Generated**: 2025-12-23
**Total FEAT-CHG Events**: 408 across all newspapers

---

## 1. Features DETECTED in Data (13 out of 20)

### High-Frequency Features (with extracted rules)

| Feature | Total Events | Newspapers | Top Transformation | Confidence | Status |
|---------|-------------|------------|-------------------|------------|---------|
| **Tense** | 148 | 3 | Pres → Past | 82% | ✅ 3 rules extracted |
| **Number** | 91 | 3 | ABSENT → Sing | 37% | ⚠️ No systematic rule (too varied) |
| **VerbForm** | 55 | 3 | Part → Fin | 35% | ⚠️ No systematic rule (too varied) |
| **Mood** | 42 | 3 | ABSENT ↔ Ind | 50% | ✅ 4 rules extracted |
| **Person** | 26 | 2 | 3 → ABSENT | 65% | ✅ 2 rules extracted |

### Medium-Frequency Features

| Feature | Total Events | Newspapers | Top Transformation | Confidence | Status |
|---------|-------------|------------|-------------------|------------|---------|
| **Degree** | 8 | 3 | Pos → ABSENT | 67% | ✅ 4 rules extracted |
| **Foreign** | 7 | 1 | ABSENT → Yes | 86% | ✅ 1 rule extracted |
| **Abbr** | 4 | 2 | Yes → ABSENT | 100% | ✅ 2 rules extracted |
| **Case** | 3 | 2 | Nom → Acc | 33% | ✅ 3 rules extracted |
| **Voice** | 3 | 2 | Pass → ABSENT | 100% | ✅ 2 rules extracted |

### Low-Frequency Features

| Feature | Total Events | Newspapers | Top Transformation | Confidence | Status |
|---------|-------------|------------|-------------------|------------|---------|
| **Gender** | 1 | 1 | Masc → Neut | 100% | ✅ 1 rule extracted |
| **PronType** | 1 | 1 | Prs → Art | 100% | ✅ 1 rule extracted |

---

## 2. Features PRESENT but NO CHANGES (2 out of 20)

These features exist in the data but don't change as morphological features:

| Feature | Total in Data | Why No FEAT-CHG Events |
|---------|--------------|------------------------|
| **Poss** | 111 canonical, 66 headline | **Present but never changes in aligned tokens**. When possessive pronouns disappear (57 deletions), entire NP is deleted (C-DEL/CONST-REM), not a feature change. Linguistically: headlines don't change "his"→"her", they keep or delete the whole NP. |
| **Definite** | ~hundreds | Article changes handled by FW-DEL/FW-ADD (article deletion), not as morphological feature changes. Definiteness is lexical (the/a) not inflectional in English. |

## 3. Features NOT IN DATA (5 out of 20)

These features don't exist in Stanza's English annotations:

| Feature | UD Definition | Reason |
|---------|--------------|--------|
| **Aspect** | Viewpoint aspect (Imp, Perf, Prog) | **Verified: 0 instances**. English marks aspect lexically (auxiliary+participle) not morphologically. Stanza doesn't annotate Aspect for English. |
| **NumType** | Numeral type (Card, Ord) | Low frequency in news headlines |
| **NumForm** | Numeral form (Word, Digit) | Handled as FORM-CHG not FEAT-CHG |
| **Polarity** | Negation (Pos, Neg) | Lexical (not/n't) not morphological in English |
| **Reflex** | Reflexive pronouns | Low frequency in news text |
| **ExtPos** | External POS function | Complex feature, rarely annotated by Stanza |

---

## 4. Detailed Breakdown by Newspaper

### Times-of-India (160 FEAT-CHG events)

| Rank | Feature | Count | Top Pattern |
|------|---------|-------|-------------|
| 1 | Tense | 56 | Pres → Past (82%) |
| 2 | Number | 35 | ABSENT → Sing (37%) |
| 3 | VerbForm | 20 | Part → Fin (35%) |
| 4 | Person | 19 | 3 → ABSENT (53%) |
| 5 | Mood | 16 | ABSENT ↔ Ind (50/50) |
| 6 | Foreign | 7 | ABSENT → Yes (86%) |
| 7 | Degree | 3 | Pos → ABSENT (67%) |
| 8 | Voice | 2 | Pass → ABSENT (100%) |
| 9 | Case | 1 | Nom → Acc (100%) |
| 10 | Abbr | 1 | Yes → ABSENT (100%) |

### Hindustan-Times (126 FEAT-CHG events)

| Rank | Feature | Count | Top Pattern |
|------|---------|-------|-------------|
| 1 | Tense | 51 | Pres → Past (82%) |
| 2 | Number | 27 | Various patterns |
| 3 | VerbForm | 15 | Part → Fin (40%) |
| 4 | Person | 15 | 3 → ABSENT (73%) |
| 5 | Mood | 12 | Ind → ABSENT (58%) |
| 6 | Case | 2 | Various patterns |
| 7 | Voice | 1 | Pass → ABSENT (100%) |
| 8 | PronType | 1 | Prs → Art (100%) |
| 9 | Gender | 1 | Masc → Neut (100%) |
| 10 | Degree | 1 | Pos → ABSENT (100%) |

### The-Hindu (122 FEAT-CHG events)

| Rank | Feature | Count | Top Pattern |
|------|---------|-------|-------------|
| 1 | Tense | 41 | Pres → Past (76%) |
| 2 | Number | 29 | ABSENT → Sing (45%) |
| 3 | VerbForm | 20 | Part → Fin (35%) |
| 4 | Mood | 14 | ABSENT → Ind (50%) |
| 5 | Person | 11 | 3 → ABSENT (55%) |
| 6 | Degree | 4 | Various patterns |
| 7 | Abbr | 3 | Yes → ABSENT (100%) |

---

## 5. Key Patterns and Insights

### Most Systematic Transformations (>70% confidence)

1. **Tense: Pres → Past** (82% confidence, 148 instances)
   - Headlines use present tense, canonical uses past tense
   - Universal across all newspapers

2. **Foreign: ABSENT → Yes** (86% confidence, 7 instances)
   - Canonical marks foreign words, headlines don't
   - Times-of-India only (Hindi phrases)

3. **Person: 3 → ABSENT** (65% average confidence, 26 instances)
   - Canonical has explicit person marking, headlines drop it
   - Pattern varies by newspaper

### Least Systematic Transformations (<40% confidence)

1. **Number** (37% best confidence)
   - Multiple competing patterns: ABSENT→Sing, Plur→Sing, Sing→Plur
   - Context-dependent, no clear rule

2. **VerbForm** (35% best confidence)
   - Varied patterns: Part→Fin, Fin→ABSENT, Inf→ABSENT
   - Closely tied to tense and aux deletion

---

## 6. Coverage Analysis

### By Rule Extraction

- **Features with systematic rules** (>50% conf): 8 features (61.5%)
- **Features with varied patterns**: 2 features (15.4%)
- **Features with sparse data**: 3 features (23.1%)

### By Instance Count

- **Total FEAT-CHG instances**: 408
- **Covered by extracted rules**: 243 (59.6%)
- **Not systematic enough**: 165 (40.4%)

---

## 7. Implications for Tasks 2 & 3

### Task 2: Transformation Rules

**Morphological transformation rules extracted**:
- ✅ 23 total rules across 10 features
- ✅ Covers 60% of morphological transformations
- ⚠️ Number & VerbForm need contextual rules (not feature-level)

**Integration needed**:
- Combine morphological rules with lexical/syntactic rules
- Create composite rules for Number+VerbForm (tied to auxiliary deletion)

### Task 3: Complexity & Similarity

**Morphological complexity metrics**:
- Feature diversity: 13 features detected
- Transformation entropy: High for Number/VerbForm, Low for Tense/Foreign
- Systematicity: 60% of transformations are rule-based

**Bidirectional transformation**:
- H→C: Add morphological features (Tense, Person, Mood)
- C→H: Remove morphological features (simplify forms)

---

## Summary

✅ **Successfully detected and analyzed 13 out of 20 morphological features**

✅ **Extracted 23 systematic transformation rules** for 10 features

⚠️ **2 high-frequency features (Number, VerbForm) have non-systematic patterns** - require contextual rules

❌ **7 features not present in data** - English morphology limitations

**Next Steps**:
1. Integrate morphological rules into transformation engine
2. Create contextual rules for Number/VerbForm
3. Use morphological complexity in Task 3 analyses
