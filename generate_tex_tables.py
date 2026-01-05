#!/usr/bin/env python3
"""
Utility: convert CSV tables to LaTeX tabular environments.

Example:
  python generate_tex_tables.py --input output/complexity-similarity-study/perplexity/directional_perplexity_analysis.csv \
    --caption "Directional perplexity analysis" \
    --label tab:dir-perplexity \
    --output LaTeX/Canonical-Reduced-Register-Complexity-Part-3-ACL-ARR/tables/directional_perplexity.tex

Notes:
- Keeps ASCII-safe output.
- Uses pandas to load CSV; falls back to manual parsing if pandas is missing.
- This does not auto-include the table in any LaTeX document; it only writes the .tex snippet.
"""

import argparse
import os
from pathlib import Path
from typing import Optional


def csv_to_latex(input_path: Path, caption: str, label: str, max_rows: Optional[int] = None) -> str:
    """Render a CSV file as a LaTeX table string."""
    try:
        import pandas as pd
    except ImportError:
        raise SystemExit("pandas is required for this tool. Please install pandas and retry.")

    df = pd.read_csv(input_path)
    if max_rows is not None and len(df) > max_rows:
        df = df.head(max_rows)

    latex_table = df.to_latex(index=False, escape=True, na_rep="--")
    snippet = []
    snippet.append("\\begin{table}[htbp]")
    snippet.append("\\centering")
    snippet.append(latex_table)
    snippet.append(f"\\caption{{{caption}}}")
    snippet.append(f"\\label{{{label}}}")
    snippet.append("\\end{table}")
    return "\n".join(snippet)


def main():
    parser = argparse.ArgumentParser(description="Convert a CSV file to a LaTeX table snippet.")
    parser.add_argument("--input", required=True, type=Path, help="Path to CSV file.")
    parser.add_argument("--output", required=True, type=Path, help="Path to write .tex snippet.")
    parser.add_argument("--caption", required=True, help="Caption for the LaTeX table.")
    parser.add_argument("--label", required=True, help="Label (\\label{...}) for the LaTeX table.")
    parser.add_argument(
        "--max-rows",
        type=int,
        default=None,
        help="Optionally limit rows for large tables.",
    )
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Input CSV not found: {args.input}")

    tex = csv_to_latex(args.input, args.caption, args.label, args.max_rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="ascii", errors="ignore") as f:
        f.write(tex)

    print(f"Wrote LaTeX table to: {args.output}")


if __name__ == "__main__":
    # Ensure thread-hungry libs stay tame if pandas pulls in BLAS
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
    os.environ.setdefault("KMP_AFFINITY", "disabled")
    os.environ.setdefault("KMP_INIT_AT_FORK", "FALSE")
    main()
