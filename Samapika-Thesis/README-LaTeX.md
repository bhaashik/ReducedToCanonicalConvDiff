# LaTeX Document for Samapika Thesis

## Overview

This directory contains a publication-ready LaTeX document (`thesis-latex-output.tex`) that includes:

- Complete feature ontology tables (from `diff-ontology.json`)
- All visualizations from the analysis (PNG files)
- Statistical tables from CSV data files
- Comprehensive linguistic analysis and interpretation

## Files in This Directory

- **thesis-latex-output.tex** - Main LaTeX document
- **diff-ontology.json** - Feature ontology schema
- **bibliography.bib** - Bibliography file
- **Global/** - Global analysis visualizations
- **TH/** - The Hindu newspaper analysis
- **HT/** - Hindustan Times analysis
- **ToI/** - Times of India analysis

## Compilation Instructions

### Prerequisites

Ensure you have a LaTeX distribution installed:
- **Linux**: TeX Live (`sudo apt-get install texlive-full`)
- **macOS**: MacTeX
- **Windows**: MiKTeX or TeX Live

### Required LaTeX Packages

The document uses the following packages (typically included in full distributions):
- graphicx
- booktabs
- longtable
- multirow
- array
- caption
- subcaption
- geometry
- hyperref
- xcolor
- float

### Compiling the Document

1. **Navigate to the Samapika-Thesis directory:**
   ```bash
   cd Samapika-Thesis
   ```

2. **Compile with pdflatex (run twice for cross-references):**
   ```bash
   pdflatex thesis-latex-output.tex
   pdflatex thesis-latex-output.tex
   ```

3. **If using bibliography (optional):**
   ```bash
   pdflatex thesis-latex-output.tex
   bibtex thesis-latex-output
   pdflatex thesis-latex-output.tex
   pdflatex thesis-latex-output.tex
   ```

4. **Output:** The compiled PDF will be `thesis-latex-output.pdf`

### Alternative: Using latexmk (Recommended)

For automatic compilation with proper handling of references:
```bash
latexmk -pdf thesis-latex-output.tex
```

## Document Structure

### 1. Introduction
Brief overview of the analysis scope and methodology.

### 2. Feature Ontology
- **Table 2.1**: Overview of ontology categories
- **Table 2.2**: Complete feature ontology schema (uses `longtable` for page breaks)
  - H-Struct: Headline Structure (sg-line, micro-disc)
  - H-Type: Headline Type (frag, non-frag)
  - F-Type: Fragment Type (complex-compound, phrase)

### 3. Global Analysis Across All Newspapers
- Figures showing global feature distributions
- **Table 3.1**: Global feature distribution statistics (uses `longtable`)
- Parse type comparisons
- Top features and diversity analyses

### 4-6. Individual Newspaper Analyses
Each newspaper section includes:
- Feature distribution visualizations
- Cross-dimensional analysis
- Feature coverage heatmaps
- Value diversity analysis
- Detailed statistics tables (uses `longtable` for The Hindu)

### 7. Comparative Analysis
Cross-newspaper comparison with key findings and patterns.

### 8. Feature-Value Transformations
Detailed linguistic descriptions of transformation patterns.

### 9. Methodology Notes
Documentation of data collection and analysis methods.

### 10. Conclusion
Summary of findings and implications.

### Appendix
- **Table A.1**: Complete feature abbreviations with descriptions (uses `longtable`)
- Data availability information

## Key Features

### Long Tables for Page Breaks
All major data tables use the `longtable` environment, which:
- Automatically breaks across pages
- Repeats headers on each page
- Shows "Continued from previous page" and "Continued on next page" messages
- Maintains professional formatting throughout

### Float Control
The document includes optimized float parameters to prevent figures from drifting too far from their text references.

### Cross-References
All tables and figures are properly labeled and referenced throughout the text.

## Customization

### Adjusting Table Appearance
- Column widths can be adjusted in the `L{width}` specifications
- Font sizes can be changed by modifying `\small` commands
- Colors and styling can be customized using the `xcolor` package

### Adding Content
The document is structured with clear section markers:
```latex
%==============================================================================
\section{Section Name}
%==============================================================================
```

### Modifying Float Behavior
Float parameters are set at the beginning of the document:
```latex
\setcounter{topnumber}{3}
\renewcommand{\topfraction}{0.85}
```
Adjust these to change how figures and tables float.

## Table Types Used

### Standard Tables (`table` + `tabular`)
Used for short tables that fit on one page:
- Feature ontology overview (Table 2.1)

### Long Tables (`longtable`)
Used for tables that may span multiple pages:
- Complete feature ontology schema (Table 2.2)
- Global feature distribution (Table 3.1)
- The Hindu cross-dimensional analysis (Table 4.1)
- Feature abbreviations (Table A.1)

### Fixed Position Tables (`table[H]`)
Used when a table must appear exactly where specified:
- Feature ontology overview (Table 2.1)

## Troubleshooting

### Images Not Found
If you get "File not found" errors for images:
1. Ensure you're compiling from the `Samapika-Thesis` directory
2. Check that all PNG files exist in their subdirectories (Global/, TH/, HT/, ToI/)
3. Verify image paths are relative (e.g., `Global/ALL-global_features.png`)

### Table Formatting Issues
If tables don't break properly across pages:
1. Ensure you've run pdflatex at least twice
2. Check that `longtable` package is loaded
3. Verify no conflicting `\begin{table}...\end{table}` wrappers around longtables

### Cross-Reference Issues
If you see "??" instead of numbers:
1. Run pdflatex at least twice
2. Delete auxiliary files (`.aux`, `.toc`, `.lot`, `.lof`) and recompile

### Float Issues
If figures appear far from their references:
1. Adjust float parameters in the preamble
2. Use `\clearpage` or `\FloatBarrier` to force placement
3. Consider using `[H]` placement specifier for critical figures

## Integration with Larger Documents

To integrate this document into a larger thesis or dissertation:

1. **Remove the preamble** (everything before `\begin{document}`)
2. **Include as chapters:**
   ```latex
   \input{Samapika-Thesis/thesis-latex-output-content.tex}
   ```
3. **Adjust section levels** if needed (e.g., `\section` → `\chapter`)
4. **Update cross-references** to match your main document structure

## Data Sources

All data in this document comes from:
- CSV files in `output/` directories
- JSON ontology in `diff-ontology.json`
- Visualizations generated from the analysis pipeline

## License and Attribution

All data, code, and visualizations are available in the project repository:
https://github.com/bhaashik/ReducedToCanonicalConvDiff.git

## Contact

For questions about the document structure or LaTeX compilation, refer to the main project documentation.
