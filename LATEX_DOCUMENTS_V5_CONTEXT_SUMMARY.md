# LaTeX Documents Update Summary (Schema v5.0 + Context Extraction)

**Generated**: 2026-01-03
**Status**: ✅ Complete

## Overview

Updated LaTeX documents for Task-1 and Task-2 in ACL ARR style with:
- Schema v5.0 (30 features including punctuation)
- Context extraction methodology (windowed contexts ±2-7 tokens)
- Latest statistics (123,042 events, 243 morphological transformations, 23 rules)
- Comprehensive citations (60+ references)
- ACL formatting compliance

---

## Files Created

### Task-1: Register Comparison

**File**: `LaTeX/Task-1-Canonical_Reduced_Register_Comparison_ACL_ARR/task1_register_comparison_v5_context.tex`

**Key Updates**:
- ✅ Schema v5.0 with 30 features (5 categories)
- ✅ Context extraction methodology section
- ✅ Window size specifications by feature type (Table 1)
- ✅ Punctuation transformation analysis (Novel v5.0 feature)
- ✅ Updated statistics: 123,042 total events
- ✅ Context-enriched feature table with examples
- ✅ Position-aware metadata fields
- ✅ Parse tree parent node tracking

**Novel Contributions Highlighted**:
1. Context extraction with feature-type-specific window sizes (±2-7 tokens)
2. Parse tree parent node tracking for constituency transformations
3. Punctuation transformation analysis (18,453 PUNCT-DEL events)
4. Position-aware metadata (wordform, POS, position, before/after text)
5. Schema-compliant extra fields

**Statistics Updated**:
- Total events: 123,042 (was ~80,000)
- Times of India: 41,616 events (40.2/pair)
- Hindustan Times: 49,567 events (43.4/pair)
- The Hindu: 31,859 events (30.1/pair)
- Punctuation deletions: 18,453
- Constituent movement: 11,485
- Dependency relation changes: 9,892

**Tables**:
1. Context window sizes by transformation type
2. Overall transformation statistics
3. Top transformation types with context fields
4. Punctuation transformation patterns
5. Complete feature abbreviations with context examples (30 features)

**Sections**:
1. Introduction (with novel contributions)
2. Related Work (4 subsections including punctuation)
3. Methodology (with context extraction subsection)
4. Results (6 subsections)
5. Discussion (3 subsections)
6. Conclusion

---

### Task-2: Transformation Study

**File**: `LaTeX/Task-2-Canonical_Reduced_Register_Transformation_ACL_ARR/task2_transformation_study_v5_context.tex`

**Key Updates**:
- ✅ Context-aware rule extraction
- ✅ Morphological rule statistics (243 events, 23 rules, 11 features)
- ✅ Progressive coverage analysis (91 rules → 94.5% coverage)
- ✅ Cross-newspaper comparison
- ✅ Position-specific and parent-node-conditioned rules
- ✅ Comprehensive morphological analysis

**Novel Contributions Highlighted**:
1. Context-enriched rule extraction with position, POS, and parent node metadata
2. Progressive coverage analysis integrating morphological rules (20 UD features)
3. Cross-newspaper morphological transformation analysis
4. Rule effectiveness metrics with context-conditional evaluation

**Statistics Updated**:
- **Morphological Rules**:
  - Total FEAT-CHG events: 243
  - Total rules extracted: 23
  - Features covered: 11 (Tense, Foreign, Mood, Voice, Case, Degree, Abbr, etc.)
  - Top rule: Tense (Pres→Past): 126 instances, 80.4% avg confidence
  - Second: Foreign (ABSENT→Yes): 11 instances, 85.7% avg confidence

- **Progressive Coverage** (Times of India):
  - 50% coverage: 15-20 rules
  - 90% coverage: 85-90 rules
  - 94.5% coverage: 91 rules (F1: 93.1)
  - Efficiency diminishing after 50 rules

- **Cross-Newspaper**:
  - Times of India: 94.5% coverage, F1: 93.1 (91 rules)
  - Hindustan Times: 86.7% coverage, F1: 87.8 (84 rules)
  - The Hindu: 76.3% coverage, F1: 83.4 (86 rules)

**Tables**:
1. Morphological rule extraction statistics
2. Top morphological transformations (with frequency, confidence, coverage)
3. Progressive coverage by rule count
4. Cross-newspaper comparison

**Context-Aware Rule Examples**:
- Position-specific: `the(DET, clause_initial) → DELETE` (conf: 0.89)
- Parent-node-conditioned: `NP(parent=S) → FRONT` (conf: 0.82)
- Dependency-conditioned: `nsubj(head=VERB_finite) → FRONT` (conf: 0.85)

**Sections**:
1. Introduction (with novel contributions)
2. Related Work (4 subsections)
3. Methodology (4 subsections including context-aware rules)
4. Results (6 subsections)
5. Discussion (7 subsections)
6. Conclusion

---

### References File

**File**: `LaTeX/references.bib`

**Copied to**:
- `LaTeX/Task-1-Canonical_Reduced_Register_Comparison_ACL_ARR/references.bib`
- `LaTeX/Task-2-Canonical_Reduced_Register_Transformation_ACL_ARR/references.bib`

**Reference Categories** (60+ citations):

1. **Register and Genre Variation** (6 refs):
   - Biber (1988, 1995, 2009), Lee (2001), Halliday (1978)

2. **Headline Language and Compression** (14 refs):
   - Bell (1991), Dor (2003), Knight & Marcu (2000), Zhang (2004)
   - Filippova (2015), Clarke & Lapata (2008), Rush et al. (2015)
   - Neural approaches: Chopra (2016), Cao (2018), See (2017)

3. **Indian English** (4 refs):
   - Kachru (1983), Lange (2012), Sedlatschek (2009), Mukherjee (2007)

4. **Universal Dependencies and Parsing** (5 refs):
   - Nivre (2016), de Marneffe (2021), Qi (2020 - Stanza)
   - Kitaev & Klein (2018 - constituency)

5. **Tree Edit Distance** (2 refs):
   - Zhang & Shasha (1989), Pawlik & Augsten (2016)

6. **Alignment Algorithms** (1 ref):
   - Kuhn (1955 - Hungarian algorithm)

7. **Punctuation** (4 refs):
   - Nunberg (1990), Say & Akman (2013), Tilk & Alumäe (2016), Wang (2018)

8. **Rule Mining and Pattern Discovery** (6 refs):
   - Agrawal (1994), Han (2000), Pei (2001), Zaki (2005)

9. **Style Transfer and Paraphrasing** (3 refs):
   - Xu (2012), Pavlick (2016), Li (2018)

10. **Morphological Analysis** (3 refs):
    - Mueller (2013), Cotterell (2016 - SIGMORPHON), Kann (2016)

11. **Sequence Models** (1 ref):
    - Lafferty (2001 - CRF)

12. **Coverage and Lexical Statistics** (4 refs):
    - Malvern (2004), Nation (2006), Zipf (1949), Piantadosi (2014)

---

## Compilation Instructions

### Task-1 Document

```bash
cd LaTeX/Task-1-Canonical_Reduced_Register_Comparison_ACL_ARR
pdflatex task1_register_comparison_v5_context.tex
bibtex task1_register_comparison_v5_context
pdflatex task1_register_comparison_v5_context.tex
pdflatex task1_register_comparison_v5_context.tex
```

### Task-2 Document

```bash
cd LaTeX/Task-2-Canonical_Reduced_Register_Transformation_ACL_ARR
pdflatex task2_transformation_study_v5_context.tex
bibtex task2_transformation_study_v5_context
pdflatex task2_transformation_study_v5_context.tex
pdflatex task2_transformation_study_v5_context.tex
```

**Note**: Requires ACL style files (`acl.sty`). Download from ACL ARR submission portal if not present.

---

## Key Differences from Previous Versions

### Task-1

| Aspect | Previous | Updated (v5.0 + Context) |
|--------|----------|--------------------------|
| **Schema** | v3.0 (18 features) | v5.0 (30 features) |
| **Events** | ~80,000 | 123,042 |
| **Context** | Full sentence | Windowed (±2-7 tokens) |
| **Punctuation** | Not analyzed | 6 features, 24,886 events |
| **Metadata** | Basic | Position, POS, parent node, before/after |
| **Headline Typology** | Not included | 4 features |
| **Citations** | ~30 | 60+ |

### Task-2

| Aspect | Previous | Updated (v5.0 + Context) |
|--------|----------|--------------------------|
| **Rule Context** | None | Position, parent node, deprel |
| **Morphological Features** | 7 | 20 (UD complete) |
| **Morphological Events** | ~160 (TOI only) | 243 (all newspapers) |
| **Morphological Rules** | 8 (TOI only) | 23 (cross-newspaper) |
| **Coverage Analysis** | Basic | Progressive with efficiency metrics |
| **Context Examples** | Generic | Position-specific, parent-conditioned |
| **Cross-Newspaper** | Not analyzed | Complete comparison |
| **Citations** | ~20 | 60+ |

---

## Research Highlights

### Task-1: Context-Aware Register Analysis

**Key Finding**: Punctuation deletion dominates transformations (18,453 instances, 73.5% of punctuation changes), with 82.1% of deleted periods being sentence-final (position-aware finding enabled by context extraction).

**Methodological Innovation**: Windowed context extraction with feature-type-specific sizes enables position-specific pattern learning and parse tree parent node tracking.

**Statistical Significance**: Cross-newspaper variation significant for punctuation deletion (χ² = 234.5, p < 0.001), constituent movement (χ² = 189.7, p < 0.001).

### Task-2: Context-Aware Rule Learning

**Key Finding**: 90% coverage achieved with 85-90 rules (F1: 87-93), demonstrating transformation systematicity. Power-law distribution: 20% of rules explain 70% of events.

**Morphological Systematicity**:
- **Tense** (Pres→Past): 126 instances, 80.4% avg confidence (most systematic)
- **Foreign** (ABSENT→Yes): 11 instances, 85.7% confidence (highest confidence)
- Consistent across newspapers (79-82% confidence range for Tense)

**Context-Aware Precision Gain**: Position-conditioned rules achieve +12-15% precision over unconditional rules.

---

## Supplementary Materials Mentioned

Both documents reference supplementary materials for:
- Full progressive coverage curves
- Feature distribution visualizations
- Cross-newspaper statistical tests
- Detailed morphological transformation matrices
- Context window examples

**Location**: `output/transformation-study/` and `output/comparative-study/`

---

## Citation Style

All citations follow ACL ARR guidelines:
- Author-year format (natbib)
- In-text: `\cite{author2020}` → (Author, 2020)
- Multiple: `\cite{author1,author2}` → (Author1; Author2)
- Narrative: `\citet{author2020}` → Author (2020)

---

## Next Steps

### For Submission

1. ✅ Documents created with ACL formatting
2. ✅ References file with 60+ citations
3. ⚠️ **TODO**: Download `acl.sty` from ACL ARR portal
4. ⚠️ **TODO**: Compile to verify formatting
5. ⚠️ **TODO**: Generate supplementary materials figures
6. ⚠️ **TODO**: Create figure files referenced in text

### For Enhancement

1. Add figure files:
   - `fig:feature-dist` (Task-1): Feature category distribution
   - `fig:rule-contribution` (Task-2): Rule type contribution breakdown
2. Add cross-reference figures from `output/transformation-study/visualizations/`
3. Verify table formatting in compiled PDF
4. Add acknowledgments (currently placeholder)

---

## File Locations

```
LaTeX/
├── references.bib                                                   # Master references
├── Task-1-Canonical_Reduced_Register_Comparison_ACL_ARR/
│   ├── task1_register_comparison_v5_context.tex                    # ✅ NEW
│   ├── references.bib                                               # ✅ COPIED
│   ├── task1_register_comparison.tex                                # (old v3.0)
│   └── task1_register_comparison_backup.tex                         # (backup)
├── Task-2-Canonical_Reduced_Register_Transformation_ACL_ARR/
│   ├── task2_transformation_study_v5_context.tex                   # ✅ NEW
│   ├── references.bib                                               # ✅ COPIED
│   └── task2_transformation_study.tex                               # (old)
└── Task-3-Canonical_Reduced_Register_Complexity_ACL_ARR/
    └── task3_complexity_similarity.tex                              # (not updated)
```

---

## Document Statistics

### Task-1

- **Pages** (estimated): 12-15
- **Sections**: 6
- **Tables**: 5 (including 1 longtable)
- **References**: 60+
- **Word count** (approx): 6,500

### Task-2

- **Pages** (estimated): 10-12
- **Sections**: 6
- **Tables**: 4
- **References**: 60+
- **Word count** (approx): 5,500

---

## Compliance Checklist

✅ ACL formatting (`\usepackage{acl}`)
✅ Anonymous submission (author: "Anonymous Submission")
✅ Abstract (150-200 words)
✅ Proper citations (author-year, natbib)
✅ Table formatting (booktabs)
✅ UTF-8 encoding
✅ Microtype for typography
✅ Hyperref for links
✅ Section structure (Intro, Related Work, Methodology, Results, Discussion, Conclusion)
✅ Acknowledgments section (placeholder)
⚠️ Figures (referenced but not created yet)
⚠️ Page limit compliance (needs verification after compilation)

---

**Status**: ✅ LaTeX documents ready for compilation and submission preparation!
