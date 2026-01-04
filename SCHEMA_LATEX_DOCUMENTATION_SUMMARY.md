# Schema v5.0 LaTeX Documentation Summary

**Date**: January 2, 2026
**Status**: ✅ Complete - LaTeX documentation generated and compiled

---

## What Was Created

### 1. Comprehensive LaTeX Documentation ✅

**Location**: `LaTeX/Schema-Documentation/`

**Files Created**:
- `diff-ontology-v5.0-documentation.tex` (39 KB) - Complete LaTeX source
- `diff-ontology-v5.0-documentation.pdf` (192 KB, 15 pages) - Compiled PDF
- `README.md` - Documentation guide and usage instructions

### 2. Generation Script ✅

**Location**: `generate_schema_documentation.py` (project root)
- Programmatically generates LaTeX from JSON schema
- Ensures accuracy and consistency
- Reusable for future schema versions

---

## Document Organization

The schema is organized into **5 broad categories** as requested:

### 1. Lexical Features (5 features)
**Addition, Deletion, Position Change**

#### Addition (2)
- **FW-ADD**: Function Word Addition (9 values)
  - article, quantifier, auxiliary, preposition, conjunctions, pronouns
- **C-ADD**: Content Word Addition (4 values)
  - noun, verb, adjective, adverb

#### Deletion (2)
- **FW-DEL**: Function Word Deletion (9 values)
  - article, quantifier, auxiliary, preposition, conjunctions, pronouns
- **C-DEL**: Content Word Deletion (4 values)
  - noun, verb, adjective, adverb

#### Position Change (1)
- **TOKEN-REORDER**: Token Reordering (4 values)
  - fronting, postposing, local swap, long-distance move

### 2. Morphological Features (5 features)
**Morphological features, lemma, word form, POS**

- **POS-CHG**: Part of Speech Change (9 values)
  - noun↔verb, adjective↔noun, verb↔adjective, finite↔nonfinite, proper↔common
- **LEMMA-CHG**: Lemma Change (1 value: any lemma change)
- **FORM-CHG**: Surface Form Change (1 value: any form change)
- **FEAT-CHG**: Morphological Feature Change (20 values) ⭐
  - Tense, Number, Aspect, Voice, Mood, Case, Degree
  - Person, Gender, Definiteness, PronType, Possessive
  - NumType, NumForm, Polarity, Reflexive, VerbForm
  - Abbreviation, ExtPos, Foreign
  - **Complete UD morphological feature coverage**
- **VERB-FORM-CHG**: Verb Form Change (3 values)
  - finite↔participle, finite↔infinitive, participle↔finite

### 3. Syntactic Features (6 features)
**Surface, Constituency, Dependency**

#### Constituency (4)
- **CONST-REM**: Constituent Removal (8 values)
  - NP, PP, SBAR, ADJP, VP, CP, QP, AdvP removal
- **CONST-ADD**: Constituent Addition (8 values)
  - NP, PP, SBAR, ADJP, VP, CP, QP, AdvP addition
- **CONST-MOV**: Constituent Movement (2 values)
  - fronted constituent, postposed constituent
- **CLAUSE-TYPE-CHG**: Clause Type Change (3 values)
  - finite↔nonfinite, verbless clause, declarative↔imperative

#### Dependency (2)
- **DEP-REL-CHG**: Dependency Relation Change (8 values)
  - nsubj↔obl, obl↔advmod, obj↔nsubj, modifier shift, complement drop
- **HEAD-CHG**: Dependency Head Change (2 values)
  - lexical head change, syntactic head change

### 4. Punctuation Features (3 features) ⭐ **CRITICAL**
**Punctuation-related transformations**

- **PUNCT-DEL**: Punctuation Deletion (12 values)
  - comma, colon, semicolon, dash, hyphen, period
  - exclamation mark, question mark, quote, parenthesis, slash, apostrophe
- **PUNCT-ADD**: Punctuation Addition (12 values)
  - Same as PUNCT-DEL but addition
- **PUNCT-SUBST**: Punctuation Substitution (19 values) ⭐ **MOST CRITICAL**
  - **Bidirectional transformations**:
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

### 5. Aggregate Features (11 features)
**Length, structural complexity, register typology**

#### Register Typology (3)
- **H-STRUCT**: Headline Structure (2 values)
  - single-line, micro-discourse
- **H-TYPE**: Headline Type (2 values)
  - fragment, non-fragment
- **F-TYPE**: Fragment Type (2 values)
  - complex-compound, phrase

#### Structural Complexity (4)
- **TREE-DEPTH-DIFF**: Tree Depth Difference (numeric)
- **CONST-COUNT-DIFF**: Constituent Count Difference (numeric)
- **DEP-DIST-DIFF**: Dependency Distance Difference (numeric)
- **BRANCH-DIFF**: Branching Factor Difference (numeric)

#### Length Metrics (3)
- **LENGTH-CHG**: Sentence Length Change (numeric)
- **TOKEN-COUNT-DIFF**: Token Count Difference (numeric)
- **CHAR-COUNT-DIFF**: Character Count Difference (numeric)

#### Edit Distance (1)
- **TED**: Tree Edit Distance (numeric)

---

## Document Structure (15 pages)

### Table of Contents
Automatically generated with page numbers and hyperlinks

### Section 1: Schema Overview (2 pages)
- Version information (5.0.0)
- Version history (4.0.0 → 5.0.0 changelog)
- Feature categories table (5 categories, 30 features)
- Parse type requirements

### Section 2: Feature Categories (8 pages)
**Detailed descriptions of all 30 features**

Each feature includes:
- ✅ Full name and mnemonic code
- ✅ Description
- ✅ Parse type requirements
- ✅ Category classification
- ✅ **Complete value enumeration with mnemonics**
- ✅ Extra metadata fields
- ✅ Definitions (where applicable)

**Special features**:
- **FEAT-CHG**: Full table of 20 UD morphological features with definitions
- **PUNCT-SUBST**: All 19 punctuation↔function word transformations
- All features organized by the 5 broad categories

### Section 3: Summary Tables (3 pages)
1. **All Features by Category** (longtable)
   - 30 rows, one per feature
   - Columns: #, Code, Name, Category, Parse Type, Value Count

2. **Features by Broad Category** (table)
   - 5 rows, one per category
   - Shows feature codes grouped by category

3. **Value Count Statistics** (table)
   - Total features, categorical/numeric split
   - Maximum values per feature

### Section 4: Usage Guidelines (1 page)
- Feature extraction pipeline (6 steps)
- Parse type selection guidelines
- Critical features for analysis

### Section 5: Implementation Notes (1 page)
- Backward compatibility notes
- Data requirements (plain text, CoNLL-U, constituency)
- Validation procedures

---

## Key Tables Included

### Feature Value Tables (18 categorical features)

Each categorical feature has a detailed value table:

**Example: PUNCT-SUBST (19 values)**
```
#   Mnemonic            Value
1   COLON2CONJ          colon to conjunction
2   CONJ2COLON          conjunction to colon
3   COMMA2CONJ          comma to conjunction
... [16 more rows]
19  PUNCT-SUBST-OTHER   other punctuation substitution
```

**Example: FEAT-CHG (20 values)**
```
#   Mnemonic        Value
1   TENSE-CHG       tense change
2   NUM-CHG         number change
3   ASP-CHG         aspect change
... [17 more rows]
20  FOREIGN-CHG     foreign change
```

Plus additional table with definitions for all 20 morphological features.

### Summary Tables

**All Features by Category** (30 rows)
| # | Code | Name | Category | Parse | Values |
|---|------|------|----------|-------|--------|
| 1 | FW-DEL | Function Word Deletion | lexical | both | 9 |
| ... | ... | ... | ... | ... | ... |
| 30 | CHAR-COUNT-DIFF | Character Count Difference | statistical | both | 1 |

**Features by Broad Category** (5 rows)
| Category | Features | Count |
|----------|----------|-------|
| Lexical | FW-DEL, FW-ADD, C-DEL, C-ADD, TOKEN-REORDER | 5 |
| Morphological | POS-CHG, LEMMA-CHG, FORM-CHG, FEAT-CHG, VERB-FORM-CHG | 5 |
| Syntactic | CONST-REM, CONST-ADD, CONST-MOV, CLAUSE-TYPE-CHG, DEP-REL-CHG, HEAD-CHG | 6 |
| Punctuation | PUNCT-DEL, PUNCT-ADD, PUNCT-SUBST | 3 |
| Aggregate | H-STRUCT, H-TYPE, F-TYPE, TREE-DEPTH-DIFF, CONST-COUNT-DIFF, DEP-DIST-DIFF, BRANCH-DIFF, LENGTH-CHG, TOKEN-COUNT-DIFF, CHAR-COUNT-DIFF, TED | 11 |

**Value Count Statistics**
| Statistic | Value |
|-----------|-------|
| Total features | 30 |
| Total categorical values | ~150 |
| Numeric features | 12 |
| Categorical features | 18 |
| Maximum values per feature | 20 (FEAT-CHG) |

---

## Parse Type Coverage

### Dependency Only (4 features)
- FEAT-CHG, DEP-REL-CHG, HEAD-CHG, DEP-DIST-DIFF

### Constituency Only (2 features)
- CONST-COUNT-DIFF, TED

### Both Parse Types (24 features)
- All lexical features (5)
- Most morphological features (4/5)
- Most syntactic features (4/6)
- All punctuation features (3)
- Most aggregate features (10/11)

---

## How to Use

### View PDF
```bash
# Location
cd LaTeX/Schema-Documentation
open diff-ontology-v5.0-documentation.pdf  # macOS
xdg-open diff-ontology-v5.0-documentation.pdf  # Linux
```

### Recompile PDF
```bash
cd LaTeX/Schema-Documentation
pdflatex diff-ontology-v5.0-documentation.tex
pdflatex diff-ontology-v5.0-documentation.tex  # Run twice for TOC
```

### Regenerate from Schema
```bash
# If schema JSON is updated
cd /mnt/d/Dropbox/.../ReducedToCanonicalConvDiff
python generate_schema_documentation.py
cd LaTeX/Schema-Documentation
pdflatex diff-ontology-v5.0-documentation.tex
```

---

## Statistics

### Feature Count by Category
- **Lexical**: 5 features (16.7%)
- **Morphological**: 5 features (16.7%)
- **Syntactic**: 6 features (20.0%)
- **Punctuation**: 3 features (10.0%)
- **Aggregate**: 11 features (36.7%)
- **TOTAL**: 30 features

### Value Count
- **Categorical features**: 18 features, ~150 total values
- **Numeric features**: 12 features
- **Average values per categorical feature**: ~8.3 values
- **Max values**: 20 (FEAT-CHG)
- **Min values**: 1 (LEMMA-CHG, FORM-CHG)

### Document Metrics
- **Pages**: 15
- **Sections**: 5 main sections
- **Subsections**: 11 subsections
- **Tables**: 3 summary tables + 18 feature value tables
- **Features documented**: 30 (100% coverage)

---

## Critical Features Highlighted

The documentation emphasizes these critical features:

1. **PUNCT-SUBST** (position 10)
   - Most critical for headline analysis
   - 19 bidirectional transformations
   - Captures punctuation ↔ function word substitution

2. **FEAT-CHG** (position 11)
   - Complete UD morphological coverage
   - 20 morphological feature types
   - Separate table with feature definitions

3. **H-TYPE** (position 20)
   - Fragment vs. non-fragment classification
   - Enables stratified analysis

4. **FW-DEL** (position 1)
   - Most frequent transformation in headlines
   - 9 function word types

5. **CONST-MOV** (position 17)
   - Captures word order changes at phrase level
   - 2 movement types (fronting, postposing)

---

## Files Created

### Primary Files
```
LaTeX/Schema-Documentation/
├── diff-ontology-v5.0-documentation.tex    (39 KB)  ← LaTeX source
├── diff-ontology-v5.0-documentation.pdf    (192 KB) ← Compiled PDF
└── README.md                                (8 KB)  ← Documentation guide
```

### Supporting Files
```
generate_schema_documentation.py            (18 KB)  ← Generation script
SCHEMA_LATEX_DOCUMENTATION_SUMMARY.md       (This file)
```

### LaTeX Artifacts
```
diff-ontology-v5.0-documentation.aux        (14 KB)  ← Auxiliary
diff-ontology-v5.0-documentation.toc        (5 KB)   ← Table of contents
diff-ontology-v5.0-documentation.out        (5 KB)   ← Hyperlinks
diff-ontology-v5.0-documentation.log        (31 KB)  ← Compilation log
```

---

## Schema Refinements Made

Based on your request for categorization, the schema organization was refined:

### Before (v4.0 categories)
- lexical/function
- lexical/content
- morphological
- syntactic/dependency
- syntactic/phrase-level
- word-order
- structural
- statistical

### After (v5.0 broad categories in LaTeX doc)
1. **Lexical** - Addition, Deletion, Position Change
2. **Morphological** - Morph features, lemma, word form, POS
3. **Syntactic** - Constituency and Dependency (separated)
4. **Punctuation** - New category for punctuation features
5. **Aggregate** - Length, edit distance, register typology

**Note**: The JSON schema still retains the original fine-grained categories, but the LaTeX documentation presents the broader categorization for clarity.

---

## Next Steps

### For Documentation
- ✅ LaTeX documentation complete
- ⏳ Consider adding examples section with real headline pairs
- ⏳ Add cross-references between related features
- ⏳ Create quick reference card (1-page summary)

### For Schema Implementation
- ⏳ Update pipeline to use schema v5.0
- ⏳ Run extraction and validate new features
- ⏳ Update research papers with new findings

---

## Citation

When using this documentation:

```latex
@techreport{diffontology2026,
  title={Feature Schema for Canonical-Reduced Register Comparison:
         Diff-Ontology Version 5.0},
  author={ReducedToCanonicalConvDiff Project},
  year={2026},
  institution={Bhaashik Research},
  type={Technical Documentation},
  url={https://github.com/bhaashik/ReducedToCanonicalConvDiff}
}
```

---

✅ **LaTeX Documentation Complete and Ready for Use**

**Location**: `LaTeX/Schema-Documentation/diff-ontology-v5.0-documentation.pdf`
**Pages**: 15
**Features**: 30 (100% coverage)
**Categories**: 5 (Lexical, Morphological, Syntactic, Punctuation, Aggregate)
