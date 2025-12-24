# Related Work: Register Variation, Headlines, and Morphosyntactic Transformations

**Generated:** 2025-12-24
**Purpose:** Comprehensive literature review for research on morphosyntactic transformations between news headlines (reduced register) and canonical sentences

---

## Directory Structure

```
related-work/
├── README.md                           # This file
├── related-work.bib                    # ACL-style BibTeX bibliography (14 entries)
├── related-work.tex                    # LaTeX section with citations
├── papers/                             # Directory for full-text PDFs (when accessible)
└── summaries/                          # Individual and synthetic summaries
    ├── Individual Papers:
    │   ├── yin-vanschijndel-2023-summary.md
    │   ├── moncomble-2018-summary.md
    │   ├── cohn-lapata-2009-summary.md
    │   ├── higurashi-etal-2018-summary.md
    │   ├── nivre-etal-2020-summary.md
    │   ├── van-etal-2021-summary.md
    │   ├── omelianchuk-etal-2021-summary.md
    │   ├── mardh-1980-summary.md
    │   └── biber-register-variation-summary.md
    ├── TOPIC-WISE-SUMMARY.md           # Organized by research themes
    └── OVERALL-SUMMARY.md              # Comprehensive synthesis
```

---

## Contents Overview

### 1. BibTeX Bibliography (`related-work.bib`)

**Format:** ACL style with URLs and DOIs
**Entries:** 14 publications spanning 1980-2023

**Categories:**
- Morphosyntactic Analysis and Linguistic Compression (1 entry)
- Headlinese and News Discourse (2 entries)
- Sentence Compression and Tree Transduction (1 entry)
- Headline Generation (1 entry)
- Universal Dependencies and Morphological Annotation (2 entries)
- Text Simplification (2 entries)
- Register Theory and Multi-Dimensional Analysis (3 entries)
- Additional Relevant Work (2 entries)

**Features:**
- All entries include URLs where available
- DOIs provided for papers with digital identifiers
- ACL Anthology URLs for computational linguistics papers
- Abstracts included for key papers

### 2. LaTeX Related Work Section (`related-work.tex`)

**Purpose:** Ready-to-use LaTeX section for inclusion in research papers or thesis
**Length:** ~4 pages (estimated)
**Structure:**
```latex
\section{Related Work}
  \subsection{Linguistic Register Theory and Headlinese}
    \paragraph{Foundational Work on Headlinese}
    \paragraph{Register Theory and Multi-Dimensional Analysis}
  \subsection{Morphosyntactic Annotation and Universal Dependencies}
    \paragraph{Universal Dependencies Framework}
    \paragraph{Stanza Parser}
  \subsection{Text Compression, Simplification, and Transformation}
    \paragraph{Tree-Based Compression}
    \paragraph{Edit-Based Simplification}
    \paragraph{Linguistic Compression Patterns}
  \subsection{Headline Generation}
  \subsection{Integration and Contributions}
    \paragraph{Novel Contributions}
```

**Citations:** Uses `\cite{key}` and `\citet{key}` with BibTeX keys from `related-work.bib`

**Usage:**
```latex
% In your main document preamble:
\bibliographystyle{acl_natbib}

% In your document body:
\input{related-work/related-work}  % Includes the section

% At end of document:
\bibliography{related-work/related-work}  % References
```

### 3. Individual Paper Summaries (`summaries/`)

**9 detailed summaries** covering foundational and recent works:

1. **yin-vanschijndel-2023-summary.md**
   Linguistic compression in summaries; morphological expansion finding

2. **moncomble-2018-summary.md**
   Pragmatic analysis of headlinese syntax; systematic deviations

3. **cohn-lapata-2009-summary.md**
   Tree transduction for sentence compression; STSG framework

4. **higurashi-etal-2018-summary.md**
   Extractive headline generation for Q&A; learning-to-rank approach

5. **nivre-etal-2020-summary.md**
   Universal Dependencies v2; 20 morphological features, 200+ treebanks

6. **van-etal-2021-summary.md**
   Neural simplification for downstream NLP; data augmentation

7. **omelianchuk-etal-2021-summary.md**
   Text simplification by tagging; edit operations (KEEP/DELETE/REPLACE)

8. **mardh-1980-summary.md**
   Foundational headlinese grammar study; coining the term

9. **biber-register-variation-summary.md**
   Multi-dimensional analysis framework; register theory synthesis

**Each summary includes:**
- Full bibliographic information
- Abstract/overview
- Key findings and contributions
- Relevance to current headline research
- Methodological approaches
- Connections to other work

### 4. Topic-Wise Summary (`TOPIC-WISE-SUMMARY.md`)

**Organizes related work into 5 thematic areas:**

**Topic 1: Foundational Work on Headlines and Register**
- Headlinese as a linguistic variety (Mårdh, Moncomble)
- Register theory framework (Biber, Halliday)

**Topic 2: Morphosyntactic Annotation and Universal Dependencies**
- UD framework and standardized features (Nivre et al.)
- Stanza parser for CoNLL-U annotation

**Topic 3: Text Compression and Sentence Simplification**
- Tree-based approaches (Cohn & Lapata)
- Edit-based approaches (Omelianchuk et al.)
- Neural approaches (Van et al.)

**Topic 4: Linguistic Compression and Summarization**
- Human compression strategies (Yin & van Schijndel)
- Automatic headline generation (Higurashi et al.)

**Topic 5: Methodological Connections**
- Cross-topic integration themes
- Gaps in prior work
- Novel contributions of current research

**Length:** ~12 pages
**Features:** Synthesis showing how different research streams converge

### 5. Overall Summary (`OVERALL-SUMMARY.md`)

**Comprehensive synthesis integrating all related work**

**Sections:**
1. Research Landscape
   - Three research traditions (linguistic, computational, compression)

2. Convergent Themes
   - Systematicity of variation
   - Multi-dimensional nature of transformation
   - Bidirectionality and asymmetry
   - Importance of morphology

3. Methodological Synthesis
   - Corpus-based empiricism
   - Statistical rigor
   - Computational reproducibility

4. Theoretical Contributions to Current Research
   - From Biber: Multi-feature analysis
   - From Mårdh/Moncomble: Systematic grammar
   - From UD: Morphological inventory
   - From Cohn & Lapata: Tree transduction
   - From Yin & van Schijndel: Bidirectional complexity

5. Knowledge Gaps Addressed
   - Morphological transformations
   - Quantitative complexity metrics
   - Systematic rule extraction
   - Cross-newspaper validation
   - Bidirectional analysis

6. Integrated Framework
   - Synthesis of all traditions
   - Applications and extensions

**Length:** ~16 pages
**Features:** Complete intellectual history and positioning of current work

---

## Key Publications by Category

### Foundational Linguistic Works

1. **Mårdh (1980)**: First systematic study of headlinese grammar
2. **Biber (1995)**: Multi-dimensional analysis of register variation
3. **Halliday & Hasan (1989)**: Systemic functional linguistics, register theory

### Modern Linguistic Analysis

4. **Moncomble (2018)**: Pragmatic analysis of headlinese syntax
5. **Biber & Egbert (2016)**: Register variation on the web

### Computational Infrastructure

6. **Nivre et al. (2020)**: Universal Dependencies v2 (200+ treebanks)
7. **Qi et al. (2020)**: Stanza parser for UD annotation

### Transformation Modeling

8. **Cohn & Lapata (2009)**: Tree transduction for compression
9. **Omelianchuk et al. (2021)**: Edit-based simplification
10. **Van et al. (2021)**: Neural simplification for NLP tasks

### Compression & Generation

11. **Yin & van Schijndel (2023)**: Linguistic compression patterns
12. **Higurashi et al. (2018)**: Extractive headline generation

---

## How to Use This Collection

### For Writing Papers

1. **Cite relevant work:**
   - Copy entries from `related-work.bib` to your bibliography
   - Use BibTeX keys in citations: `\cite{biber-1995-dimensions}`

2. **Include related work section:**
   - Copy `related-work.tex` content or adapt subsections
   - Modify to fit your narrative and space constraints

3. **Reference summaries:**
   - Use individual summaries to understand papers in depth
   - Check TOPIC-WISE-SUMMARY for thematic organization

### For Thesis Writing

1. **Chapter/section structure:**
   - Use TOPIC-WISE-SUMMARY as chapter outline
   - Expand individual paper summaries into detailed discussions

2. **Comprehensive coverage:**
   - OVERALL-SUMMARY provides full intellectual context
   - Shows evolution of ideas across 45 years (1980-2025)

3. **Gap identification:**
   - "Knowledge Gaps Addressed" section positions contributions
   - "Novel Contributions" lists specific advances

### For Understanding the Field

1. **Start with OVERALL-SUMMARY** for big picture
2. **Read TOPIC-WISE-SUMMARY** for thematic organization
3. **Dive into individual summaries** for specific papers
4. **Use BibTeX file** to find full papers (URLs/DOIs provided)

---

## Coverage Statistics

**Total Publications:** 14
**Date Range:** 1980-2023 (45 years)
**Venues:**
- ACL/EMNLP/COLING: 5 papers
- LREC: 1 paper
- Journals (JAIR, e-Rea, Journal of English Linguistics, Corpora): 4 papers
- Books: 3 monographs
- Web/Online: 1 resource

**Geographic Scope:**
- International (ACL, LREC)
- UK (Mårdh - Sweden, Moncomble - France)
- US (Biber, Stanford NLP)

**Languages Covered:**
- English (primary focus)
- Cross-linguistic (UD: 150+ languages)

**Research Methods:**
- Corpus analysis: 6 papers
- Computational modeling: 5 papers
- Theoretical frameworks: 3 papers

---

## Citation Format

All entries follow ACL BibTeX style:

```bibtex
@inproceedings{key,
    title = "Paper Title",
    author = "Author, First and Author, Second",
    booktitle = "Proceedings of Conference",
    year = "2023",
    url = "https://aclanthology.org/...",
    doi = "10.xxxxx/xxxxx",
    pages = "XX--YY"
}
```

**Required fields:** title, author, booktitle/journal, year
**Recommended fields:** url, doi, pages, publisher
**Optional fields:** abstract, note

---

## Updates and Maintenance

**Last Updated:** 2025-12-24

**To add new papers:**
1. Create summary in `summaries/[key]-summary.md`
2. Add BibTeX entry to `related-work.bib`
3. Integrate into appropriate section of `related-work.tex`
4. Update TOPIC-WISE-SUMMARY with new categorization
5. Revise OVERALL-SUMMARY if significant theoretical contribution

**To extend:**
- Add full PDFs to `papers/` directory when accessible
- Create specialized topic summaries (e.g., neural methods, cross-linguistic)
- Develop citation network analysis
- Track forward citations of our work

---

## Sources and Search Strategy

**Primary Sources:**
- ACL Anthology (https://aclanthology.org/)
- Google Scholar
- Semantic Scholar
- OpenEdition Journals
- University press websites

**Search Queries Used:**
- "headline" + "register variation" + "news"
- "headlinese" + "grammar" + "syntax"
- "sentence compression" + "tree transduction"
- "text simplification" + "morphological"
- "Universal Dependencies" + "morphological features"
- "register theory" + "Biber" + "multi-dimensional"
- "linguistic compression" + "summarization"

**Inclusion Criteria:**
- Directly relevant to headlines, register variation, or morphosyntactic transformation
- Foundational theoretical work (Biber, Halliday, Mårdh)
- Computational methods (UD, parsers, transformation models)
- Published in peer-reviewed venues or established monographs
- Available with full bibliographic information including URLs/DOIs

---

## Contact and Attribution

**Generated for:** PhD research on morphosyntactic transformations in news headlines
**Date:** December 24, 2025
**Assistant:** Claude Code (Anthropic)

**For questions or suggestions about this collection:**
- Review individual summaries for detailed paper information
- Check URLs in .bib file for full paper access
- Consult OVERALL-SUMMARY for theoretical integration

---

**End of README**
