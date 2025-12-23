#!/bin/bash
# Master compilation script for all LaTeX documents
# Compiles thesis and all supplementary documents

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Compiling All Thesis and Supplementary Documents      ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if pdflatex is available
if ! command -v pdflatex &> /dev/null; then
    echo -e "${RED}Error: pdflatex not found!${NC}"
    echo "Please install a LaTeX distribution (TeX Live, MacTeX, or MiKTeX)."
    exit 1
fi

# Function to compile a LaTeX document
compile_document() {
    local filename=$1
    local docname=$(basename "$filename" .tex)

    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Compiling: ${docname}.tex${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # First pass
    echo -e "${BLUE}  Pass 1/2...${NC}"
    pdflatex -interaction=nonstopmode "$filename" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo -e "${RED}  ✗ Error in first pass${NC}"
        echo -e "${RED}  Check ${docname}.log for details${NC}"
        return 1
    fi

    # Second pass for cross-references
    echo -e "${BLUE}  Pass 2/2...${NC}"
    pdflatex -interaction=nonstopmode "$filename" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo -e "${RED}  ✗ Error in second pass${NC}"
        echo -e "${RED}  Check ${docname}.log for details${NC}"
        return 1
    fi

    # Check if PDF was created
    if [ -f "${docname}.pdf" ]; then
        local size=$(du -h "${docname}.pdf" | cut -f1)
        local pages=$(pdfinfo "${docname}.pdf" 2>/dev/null | grep "Pages:" | awk '{print $2}')
        echo -e "${GREEN}  ✓ Success!${NC}"
        echo -e "    Output: ${GREEN}${docname}.pdf${NC}"
        echo -e "    Size: ${size}"
        if [ -n "$pages" ]; then
            echo -e "    Pages: ${pages}"
        fi
        return 0
    else
        echo -e "${RED}  ✗ PDF not created${NC}"
        return 1
    fi
}

# Document list with descriptions
declare -A documents
documents=(
    ["thesis-latex-output.tex"]="Main Thesis Document"
    ["supplementary-analysis.tex"]="Supplementary Analysis (7 chapters)"
    ["alignment-metrics.tex"]="Alignment & Evaluation Metrics"
    ["feature-deep-dives.tex"]="Feature-by-Feature Deep Dives"
)

# Track compilation results
declare -a success_docs
declare -a failed_docs
total=0
successful=0

echo ""
echo -e "${BLUE}Starting compilation of ${#documents[@]} documents...${NC}"
echo ""

# Compile each document
for doc in "${!documents[@]}"; do
    if [ -f "$doc" ]; then
        total=$((total + 1))
        description="${documents[$doc]}"
        echo -e "${BLUE}[$total/${#documents[@]}] ${description}${NC}"

        if compile_document "$doc"; then
            success_docs+=("$doc")
            successful=$((successful + 1))
        else
            failed_docs+=("$doc")
        fi
        echo ""
    else
        echo -e "${YELLOW}Skipping ${doc} (file not found)${NC}"
        echo ""
    fi
done

# Summary
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                  Compilation Summary                      ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ $successful -eq $total ]; then
    echo -e "${GREEN}✓ All $successful documents compiled successfully!${NC}"
else
    echo -e "${YELLOW}⚠ $successful of $total documents compiled successfully${NC}"
fi

echo ""

# List successful compilations
if [ ${#success_docs[@]} -gt 0 ]; then
    echo -e "${GREEN}Successful:${NC}"
    for doc in "${success_docs[@]}"; do
        pdf_file=$(basename "$doc" .tex).pdf
        size=$(du -h "$pdf_file" 2>/dev/null | cut -f1)
        echo -e "  ✓ $pdf_file (${size})"
    done
    echo ""
fi

# List failed compilations
if [ ${#failed_docs[@]} -gt 0 ]; then
    echo -e "${RED}Failed:${NC}"
    for doc in "${failed_docs[@]}"; do
        echo -e "  ✗ $doc"
    done
    echo ""
    echo -e "${YELLOW}Check .log files for error details${NC}"
    echo ""
fi

# Cleanup option
echo ""
read -p "$(echo -e ${YELLOW}Clean auxiliary files? [y/N]:${NC} )" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Cleaning auxiliary files...${NC}"
    rm -f *.aux *.log *.out *.toc *.lot *.lof *.bbl *.blg 2>/dev/null
    echo -e "${GREEN}✓ Cleaned${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Done!${NC}"
echo ""

# Exit with appropriate code
if [ $successful -eq $total ]; then
    exit 0
else
    exit 1
fi
