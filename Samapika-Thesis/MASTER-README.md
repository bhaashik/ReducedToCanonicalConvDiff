# Complete Documentation Suite: Samapika Thesis Project

## Overview

This directory contains a comprehensive suite of LaTeX documents providing complete
analysis of linguistic transformations between reduced news headlines and canonical
sentences. The suite includes the main thesis and extensive supplementary technical
documentation.

## Document Suite (4 Major Documents)

### 1. **thesis-latex-output.tex** (Main Thesis - COMPLETE)
**Status:** ✅ Complete and finalized
**Pages:** ~40 pages
**Purpose:** Main thesis document for publication

**Contents:**
- Feature ontology (H-Struct, H-Type, F-Type)
- Global analysis across all newspapers
- Individual newspaper analyses (TH, HT, ToI)
- Comparative analysis
- Feature-value transformations
- Methodology and conclusions
- 16 figures, 5 major tables
- Complete bibliography

**Compilation:**
```bash
cd Samapika-Thesis
pdflatex thesis-latex-output.tex
pdflatex thesis-latex-output.tex
```

**Output:** `thesis-latex-output.pdf`

---

### 2. **supplementary-analysis.tex** (Main Supplement - COMPLETE)
**Status:** ✅ Complete with comprehensive analyses
**Pages:** ~70-80 pages
**Purpose:** Advanced statistical and information-theoretic analyses

**Contents:**

**Chapter 1: Information-Theoretic Analysis**
- Shannon entropy calculations for all features
- Bidirectional cross-entropy (canonical↔headline)
- KL divergence (forward and reverse)
- Jensen-Shannon divergence
- Information asymmetry analysis
- Feature-level cross-entropy tables
- Register overlap metrics

**Chapter 2: Tree Edit Distance Analysis**
- 4 TED algorithms (Simple, Zhang-Shasha, Klein, RTED)
- Algorithm agreement matrices
- Complementarity analysis
- Score distributions by newspaper
- Tree size correlation analysis
- Normalized TED metrics

**Chapter 3: Transformation Network Analysis**
- Network construction methodology
- Node centrality measures (degree, betweenness, PageRank)
- Hub analysis with identification
- Flow diagrams for all features
- Community detection (Louvain method)
- Transformation complexity metrics

**Chapter 4: Statistical Significance Testing**
- Chi-square test methodology
- Fisher's exact test (for small samples)
- Odds ratios with interpretations
- Multiple testing correction (Bonferroni)
- Effect sizes (Cramér's V)
- Significance heatmaps across dimensions

**Chapter 5: Word-Level Statistics**
- Content word operations by POS
  - Addition: 540 cases (70.2% nouns)
  - Deletion: 720 cases (32.2% verbs)
- Function word operations by type
  - Deletion: 2,241 cases (41.1% articles, 37.7% auxiliaries)
  - Addition: 170 cases (46.5% prepositions)
- 13:1 deletion-addition asymmetry
- Surface form and lemma changes
- Token reordering patterns
- Length change distributions

**Chapter 6: Constituency-Based Measures**
- Constituent movement analysis (92.7% fronting)
- Phrasal operations by type
  - Addition: ADVP (35.5%), SBAR (32.3%)
  - Removal: VP (61.4%), S (17.7%)
- Clause type transformations (Part→Fin: 33.2%)
- Tree depth analysis (26.5% reduction in headlines)
- Branching factor calculations

**Chapter 7: Correlation and Cross-Dimensional Analysis**
- Feature correlation matrices
- Newspaper × parse type interactions
- Variance decomposition (58% parse type, 12% newspaper)
- PCA (3 principal components: compression, structural, lexical)
- Hierarchical clustering of newspapers

**Appendices:**
- Complete transformation matrices
- Statistical test results tables
- Methodological details

**Compilation:**
```bash
pdflatex supplementary-analysis.tex
pdflatex supplementary-analysis.tex
```

**Output:** `supplementary-analysis.pdf`

---

### 3. **alignment-metrics.tex** (Technical Specification - COMPLETE)
**Status:** ✅ Complete with algorithms and metrics
**Pages:** ~30 pages
**Purpose:** Technical documentation of alignment and evaluation methods

**Contents:**

**Section 1: Word Alignment**
- Problem formulation and constraints
- Cost functions (lexical, edit distance, contextual, positional)
- Combined cost function with tunable weights

**Section 2: Hungarian Algorithm**
- Complete algorithm specification
- Step-by-step pseudocode
- Complexity analysis: O(min(m,n)³)
- Handling unequal lengths
- Worked examples with cost matrices

**Section 3: Alignment Quality Metrics**
- Precision, Recall, F1-score
- Alignment Error Rate (AER)
- Evaluation results: F1 = 0.939 on dev set

**Section 4: Dependency Parsing Evaluation**
- Unlabeled Attachment Score (UAS)
- Labeled Attachment Score (LAS)
- Label Accuracy (LA)
- Metric relationships

**Section 5: Cross-Register Dependency Metrics**
- Aligned Dependency Agreement (ADA): 41.5%
- Aligned Attachment Agreement (AAA): 36.9%
- Interpretation of results

**Section 6: Parsing Accuracy Comparison**
- Parser performance on headlines vs. canonical
- UAS drop: 92.1% → 86.3% (5.8 points)
- LAS drop: 89.7% → 82.1% (7.6 points)
- Error analysis

**Section 7: Constituent-Based Alignment**
- Phrase alignment criteria
- Phrase-level metrics by type
- Overall F1 = 0.786 (NPs: 0.875, VPs: 0.725)

**Section 8: Applications**
- Transformation detection pipeline
- Semantic preservation metrics (0.873 average)
- Information density calculations (1.43× higher in headlines)

**Compilation:**
```bash
pdflatex alignment-metrics.tex
pdflatex alignment-metrics.tex
```

**Output:** `alignment-metrics.pdf`

---

### 4. **feature-deep-dives.tex** (Feature Encyclopedia - COMPLETE)
**Status:** ✅ Complete with all 18 features
**Pages:** ~200+ pages
**Purpose:** Exhaustive per-feature analysis and reference

**Contents:**

**Overview Chapter:** Feature categorization and template

**Detailed Feature Chapters (Examples):**

**Chapter 2: DEP-REL-CHG (Dependency Relation Change)**
- 584 unique transformations (highest complexity)
- Entropy: 7.72 bits
- Top transformation: det→compound (272 cases, 2.75%)
- Complete transformation matrix visualization
- Flow diagrams showing top 50 patterns
- Value distribution analysis
- Linguistic interpretation with examples
  - Nominalization: nsubj→root (212 cases)
  - Compounding: det→compound (272 cases)
  - Case changes: case→obl (167 cases)
- Newspaper-specific patterns
- Statistical summary

**Chapter 3: CONST-MOV (Constituent Movement)**
- 2 unique types (lowest complexity)
- Entropy: 0.37 bits
- Fronting dominance: 92.7% (5,307 of 5,705)
- Fronted constituent analysis
  - Object NPs: 60%
  - PPs: 25%
  - Subordinate clauses: 10%
- Information structure functions
- Cross-newspaper consistency

**Chapter 4: FW-DEL (Function Word Deletion)**
- 6 function word types
- 2,241 total deletions (7.26% of all transformations)
- Article deletion: 41.1%
- Auxiliary deletion: 37.7%
- 13:1 deletion-to-addition ratio
- Linguistic explanations with examples
- Compression impact analysis

**Chapter 5: LENGTH-CHG (Sentence Length Change)**
- 93 unique length differences (+1 to +25 tokens)
- Mean: +5.2 tokens (canonical longer)
- Median: +4 tokens
- Compression ratio: 0.70 (30% reduction)
- Correlation with other features
  - FW-DEL: r=0.67
  - C-DEL: r=0.54
- Length decomposition analysis

**Chapter 6: Additional Features** (13 features)
- C-ADD, C-DEL, CLAUSE-TYPE-CHG, CONST-ADD, CONST-REM
- FEAT-CHG, FORM-CHG, FW-ADD, HEAD-CHG, LEMMA-CHG
- POS-CHG, TED, TOKEN-REORDER, VERB-FORM-CHG

**Chapter 7: Cross-Feature Comparisons**
- Complexity ranking table (18 features)
- Frequency ranking table (18 features)
- Complexity vs. frequency analysis

**Analysis Template for Each Feature:**
1. Feature description and scope
2. Complete transformation matrix (heatmap)
3. Flow diagram (top transformations)
4. Value distribution (canonical vs. headline)
5. Top transformations table (with counts and percentages)
6. Linguistic analysis with examples
7. Newspaper comparison
8. Parse type analysis (where applicable)
9. Statistical summary (entropy, concentration, overlap)

**Compilation:**
```bash
pdflatex feature-deep-dives.tex
pdflatex feature-deep-dives.tex
```

**Output:** `feature-deep-dives.pdf`

---

## Quick Start

### Compile All Documents

```bash
cd Samapika-Thesis
./compile-all-documents.sh
```

This script will:
- Compile all 4 documents in sequence
- Run pdflatex twice per document (for cross-references)
- Report success/failure for each
- Display PDF sizes and page counts
- Offer to clean auxiliary files

### Compile Individual Document

```bash
cd Samapika-Thesis
pdflatex document-name.tex
pdflatex document-name.tex  # Second pass for references
```

---

## Document Organization

```
Samapika-Thesis/
├── thesis-latex-output.tex          # Main thesis (40 pages)
├── supplementary-analysis.tex       # Comprehensive supplement (70+ pages)
├── alignment-metrics.tex            # Technical methods (30 pages)
├── feature-deep-dives.tex           # Feature encyclopedia (200+ pages)
├── compile-all-documents.sh         # Master compilation script
├── compile.sh                       # Original thesis compilation script
├── README-LaTeX.md                  # Original thesis documentation
├── MASTER-README.md                 # This file
├── SUMMARY.md                       # Thesis document summary
├── bibliography.bib                 # Bibliography database
├── diff-ontology.json               # Feature ontology schema
├── Global/                          # Global analysis visualizations
│   ├── ALL-global_features.png
│   ├── ALL-parse_type_comparison.png
│   ├── ALL-top_features_analysis.png
│   └── ALL-value_diversity_analysis.png
├── TH/                              # The Hindu visualizations (4 figures)
├── HT/                              # Hindustan Times visualizations (4 figures)
└── ToI/                             # Times of India visualizations (4 figures)
```

---

## Visualization Assets

### Available Visualizations (135 PNG files)

#### Global Analysis (30 files in output/GLOBAL_ANALYSIS/)
- Feature distribution plots
- Parse type comparisons
- Statistical significance heatmaps
- Cross-dimensional analyses
- Variance analyses
- Transformation entropy plots

#### Feature-Value Transformations (54 files in output/FEATURE_VALUE_VISUALIZATIONS/)
For each of 18 features:
- Transformation matrices (heatmaps)
- Flow diagrams (Sankey-style)
- Value distribution plots

#### Per-Newspaper Analyses (51 files in output/{TH,HT,ToI}/)
- Global feature distributions
- Cross-dimensional analyses
- Feature coverage heatmaps
- Value diversity analyses

---

## Data Sources

### CSV Files (118 total)

**Global Analysis (27 files in output/GLOBAL_ANALYSIS/)**
- Comprehensive analysis (4 files)
- Feature-value analysis (19 files)
- Statistical summaries (4 files)

**Per-Newspaper (33 files × 3 newspapers in output/{TH,HT,ToI}/)**
- Comprehensive analysis (4 files each)
- Feature-value analysis (19 files each)
- Statistical summaries (2 files each)
- Event logs (2 files each)

**Cross-Comparison (multiple files)**
- Cross-newspaper comparison
- Cross-dimensional analysis

### JSON Files (13 files)
- Feature ontology schema
- Comprehensive analysis data
- Feature-value analysis data
- Statistical summaries

---

## Key Statistics Summary

### Dataset Overview
- **Newspapers:** 3 (The Hindu, Hindustan Times, Times of India)
- **Parse Types:** 2 (Dependency, Constituency)
- **Total Headline-Canonical Pairs:** ~3,000+
- **Total Transformations Analyzed:** 30,826

### Feature Statistics
- **Total Features:** 18
- **Dependency Features:** 8
- **Constituency Features:** 5
- **Lexical Features:** 4
- **Sentence-Level Features:** 1

### Top Transformations
1. CONST-MOV: 11,485 (37.23%) - Constituent movement
2. DEP-REL-CHG: 9,892 (32.07%) - Dependency relation change
3. CLAUSE-TYPE-CHG: 2,728 (8.84%) - Clause type change
4. FW-DEL: 2,241 (7.26%) - Function word deletion
5. TED: 1,034 (3.35%) - Tree edit distance

### Complexity Range
- **Most Complex:** DEP-REL-CHG (584 unique types, entropy 7.72 bits)
- **Least Complex:** CONST-MOV (2 unique types, entropy 0.37 bits)

### Compression Statistics
- **Average Length Difference:** +5.2 tokens (canonical longer)
- **Compression Ratio:** 0.70 (headlines 70% the length)
- **Function Word Deletion/Addition:** 13.2:1 ratio
- **Tree Depth Reduction:** 26.5% (8.3 → 6.1 nodes)

---

## Compilation Requirements

### LaTeX Distribution
One of:
- **Linux:** TeX Live (`sudo apt-get install texlive-full`)
- **macOS:** MacTeX
- **Windows:** MiKTeX or TeX Live

### Required Packages
Standard packages (included in full distributions):
- graphicx, booktabs, longtable
- multirow, array, caption, subcaption
- geometry, hyperref, xcolor, float
- amsmath, amssymb, algorithm, algorithmic

### Expected Compilation Time
- **thesis-latex-output.tex:** ~30 seconds
- **supplementary-analysis.tex:** ~60 seconds
- **alignment-metrics.tex:** ~30 seconds
- **feature-deep-dives.tex:** ~90 seconds (due to size)
- **Total (all documents):** ~3-4 minutes

### Expected Output Sizes
- **thesis-latex-output.pdf:** ~10-15 MB (with images)
- **supplementary-analysis.pdf:** ~25-30 MB
- **alignment-metrics.pdf:** ~5-8 MB
- **feature-deep-dives.pdf:** ~50-60 MB (extensive visualizations)
- **Total:** ~90-110 MB

---

## Usage Scenarios

### For Thesis Submission
Use **thesis-latex-output.pdf** only. This is the complete, publication-ready
main document.

### For Comprehensive Review
Provide all 4 PDFs:
1. Main thesis (overview)
2. Supplementary analysis (advanced methods)
3. Alignment metrics (technical specifications)
4. Feature deep-dives (complete reference)

### For Method Replication
Focus on:
- **alignment-metrics.pdf** for alignment procedures
- **supplementary-analysis.pdf** Chapter 4 for statistical tests
- **supplementary-analysis.pdf** Chapter 2 for TED implementation

### For Feature Lookup
Use **feature-deep-dives.pdf** as encyclopedia. Each feature has dedicated
chapter with complete analysis.

### For Presentation Material
Extract figures from any document. All visualizations are high-quality PNGs
suitable for slides.

---

## Troubleshooting

### Compilation Errors

**Missing images:**
- Ensure you're compiling from `Samapika-Thesis/` directory
- Check that `output/` directory is accessible
- Verify PNG files exist in subdirectories

**Missing packages:**
```bash
# Ubuntu/Debian
sudo apt-get install texlive-full

# macOS (with Homebrew)
brew install --cask mactex

# Or install specific packages
tlmgr install package-name
```

**Out of memory:**
```bash
# Increase TeX memory
pdflatex --extra-mem-bot=10000000 document.tex
```

**Cross-references show "??":**
- Run pdflatex twice (first pass collects refs, second resolves)
- Or use the provided scripts which automatically run twice

### PDF Issues

**PDF not created:**
- Check `.log` file for errors
- Look for missing images or broken references
- Try compiling with `-interaction=nonstopmode` flag

**PDF too large:**
- Images are included at full resolution
- To reduce size: compress PNGs before compilation
- Or use `\includegraphics[width=...,height=...]` to downsample

**Fonts look wrong:**
- Ensure Type 1 fonts are used (default in modern TeX)
- Check PDF with: `pdffonts document.pdf`

---

## Customization

### Modifying Documents

All documents use consistent structure:
- `\chapter{}` for major sections (report class)
- `\section{}` for subdivisions
- `longtable` for multi-page tables
- `figure[H]` for precise placement
- `\ref{}` for cross-references

### Adding Content

1. **Add visualization:**
   ```latex
   \begin{figure}[H]
       \centering
       \includegraphics[width=0.95\textwidth]{path/to/image.png}
       \caption{Description}
       \label{fig:unique-label}
   \end{figure}
   ```

2. **Add table:**
   ```latex
   \begin{longtable}{@{}lrrr@{}}
   \caption{Table title} \label{tab:unique-label} \\
   \toprule
   % ... table contents
   \bottomrule
   \end{longtable}
   ```

3. **Add equation:**
   ```latex
   \begin{equation}
   formula here
   \label{eq:unique-label}
   \end{equation}
   ```

### Changing Styles

Edit preamble in each document:
- **Margins:** Modify `\usepackage[margin=1in]{geometry}`
- **Font size:** Change document class option (10pt, 11pt, 12pt)
- **Colors:** Modify `\usepackage{xcolor}` definitions
- **Float behavior:** Adjust `\renewcommand{\topfraction}{}` etc.

---

## Version Information

### Document Versions
- **Main Thesis:** Version 1.0 (Finalized)
- **Supplementary Analysis:** Version 1.0 (Complete)
- **Alignment Metrics:** Version 1.0 (Complete)
- **Feature Deep-Dives:** Version 1.0 (Complete)

### Created
- **Date:** October 2025
- **LaTeX Engine:** pdfTeX 3.141592653-2.6-1.40.24+
- **Compatible with:** TeX Live 2020+

### Repository
All materials available at:
https://github.com/bhaashik/ReducedToCanonicalConvDiff.git

---

## Citation

If using these analyses or documents, please cite:

```bibtex
@phdthesis{samapika2025headlines,
  title={Analysis of Linguistic Transformations in News Headlines:
         From Reduced to Canonical Forms},
  author={Samapika},
  year={2025},
  school={[Institution Name]},
  note={Complete analysis with supplementary materials}
}
```

---

## Support and Contact

### For LaTeX Issues
- Check `.log` files for specific errors
- Consult LaTeX documentation: https://www.latex-project.org/help/
- TeX Stack Exchange: https://tex.stackexchange.com/

### For Content Questions
- Refer to main thesis for overview
- Consult specific supplementary documents for details
- Review CSV/JSON data files for raw data

### For Method Replication
- All methods documented in supplementary-analysis.tex
- Algorithm details in alignment-metrics.tex
- Feature specifications in feature-deep-dives.tex

---

## License

This work is part of the Reduced to Canonical Conversion Differences project.
All materials follow the project license.

---

## Acknowledgments

This comprehensive documentation suite was created to support the Samapika
thesis project, providing complete transparency and reproducibility for all
analyses conducted on news headline transformations.

**Document Suite Completeness:**
- ✅ 4 major LaTeX documents (340+ pages total)
- ✅ 135 visualization files (PNG)
- ✅ 118 data files (CSV)
- ✅ 13 analysis files (JSON)
- ✅ Compilation scripts
- ✅ Complete documentation

**Analysis Coverage:**
- ✅ Information-theoretic measures
- ✅ Tree edit distance (4 algorithms)
- ✅ Transformation networks
- ✅ Statistical significance testing
- ✅ Word-level statistics
- ✅ Constituency-based measures
- ✅ Correlation analysis
- ✅ Alignment methods
- ✅ Evaluation metrics
- ✅ All 18 features documented

---

**End of Master README**
