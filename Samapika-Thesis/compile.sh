#!/bin/bash
# Compilation script for thesis-latex-output.tex
# This script compiles the LaTeX document and handles all necessary passes

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting LaTeX compilation for Samapika Thesis...${NC}"

# Check if we're in the right directory
if [ ! -f "thesis-latex-output.tex" ]; then
    echo -e "${RED}Error: thesis-latex-output.tex not found!${NC}"
    echo "Please run this script from the Samapika-Thesis directory."
    exit 1
fi

# Check if pdflatex is available
if ! command -v pdflatex &> /dev/null; then
    echo -e "${RED}Error: pdflatex not found!${NC}"
    echo "Please install a LaTeX distribution (TeX Live, MacTeX, or MiKTeX)."
    exit 1
fi

# Function to run pdflatex
run_pdflatex() {
    echo -e "${YELLOW}Running pdflatex (pass $1)...${NC}"
    pdflatex -interaction=nonstopmode thesis-latex-output.tex > /dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Pass $1 completed successfully${NC}"
    else
        echo -e "${RED}✗ Error in pass $1${NC}"
        echo "Check the .log file for details"
        return 1
    fi
}

# Clean previous build files (optional)
echo -e "${YELLOW}Cleaning previous build files...${NC}"
rm -f thesis-latex-output.aux thesis-latex-output.log thesis-latex-output.out \
      thesis-latex-output.toc thesis-latex-output.lot thesis-latex-output.lof

# First pass
run_pdflatex 1

# Second pass (for cross-references)
run_pdflatex 2

# Check if PDF was created
if [ -f "thesis-latex-output.pdf" ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✓ Compilation successful!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "Output: ${GREEN}thesis-latex-output.pdf${NC}"

    # Get PDF size
    SIZE=$(du -h thesis-latex-output.pdf | cut -f1)
    echo -e "Size: ${SIZE}"

    # Count pages if pdfinfo is available
    if command -v pdfinfo &> /dev/null; then
        PAGES=$(pdfinfo thesis-latex-output.pdf 2>/dev/null | grep "Pages:" | awk '{print $2}')
        echo -e "Pages: ${PAGES}"
    fi

    echo ""
    echo "You can open the PDF with:"
    echo "  - Linux: xdg-open thesis-latex-output.pdf"
    echo "  - macOS: open thesis-latex-output.pdf"
    echo "  - Windows: start thesis-latex-output.pdf"
else
    echo -e "${RED}✗ PDF was not created. Check the log file for errors.${NC}"
    exit 1
fi

# Optional: Clean auxiliary files
read -p "$(echo -e ${YELLOW}Clean auxiliary files? [y/N]:${NC} )" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Cleaning auxiliary files...${NC}"
    rm -f thesis-latex-output.aux thesis-latex-output.log thesis-latex-output.out \
          thesis-latex-output.toc thesis-latex-output.lot thesis-latex-output.lof
    echo -e "${GREEN}✓ Cleaned${NC}"
fi

echo -e "${GREEN}Done!${NC}"
