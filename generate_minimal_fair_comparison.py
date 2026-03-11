"""
generate_minimal_fair_comparison.py
====================================
Thin wrapper around generate_fair_comparison_outputs that writes all
fair-comparison outputs to output-minimal/, with LaTeX tables included.

Output layout mirrors the main fair-comparison structure exactly:

output-minimal/
├── task-1-comparative-study/
│   ├── global/
│   │   ├── 1-raw-counts/       count_raw.{png,csv,tex}
│   │   ├── 2-normalized/       rate_norm.{png,csv,tex}
│   │   ├── 3-log/              log2_norm.{png,csv,tex}
│   │   ├── 4-weighted/         score_lvl.{…}  score_idf.{…}
│   │   └── 5-information-theoretic/  score_jsd.{…}  score_pmi.{…}
│   ├── cross-newspaper/
│   │   └── (same 5 stage subdirs, grouped NP figures + .tex tables)
│   └── per-newspaper/
│       ├── Hindustan-Times/
│       │   └── (same 5 stage subdirs, per-NP figures + CSVs)
│       ├── The-Hindu/
│       └── Times-of-India/
├── task-2-transformation-study/
│   └── (same structure with morphological-rule data)
└── task-3-complexity-similarity-study/
    └── (same structure with complexity / similarity metrics)

Usage
-----
    python generate_minimal_fair_comparison.py
    python generate_minimal_fair_comparison.py --no-plots
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from config import BASE_DIR
from paths_config import NEWSPAPERS

# Import task runners from the main script
from generate_fair_comparison_outputs import (
    run_task1,
    run_task2,
    run_task3,
)

# ── paths ─────────────────────────────────────────────────────────────────────
MINIMAL_DIR = BASE_DIR / "output-minimal"

TASK_DIRS = {
    "task1": "task-1-comparative-study",
    "task2": "task-2-transformation-study",
    "task3": "task-3-complexity-similarity-study",
}


# ═══════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Generate compact fair-comparison outputs in output-minimal/, "
            "with LaTeX tables for cross-newspaper and global views."
        )
    )
    parser.add_argument("--no-plots", action="store_true",
                        help="Skip figure generation; CSV and LaTeX only.")
    parser.add_argument("--newspapers", nargs="+", default=None,
                        metavar="NP",
                        help=f"Newspapers to process (default: all). "
                             f"Choices: {NEWSPAPERS}")
    parser.add_argument("--tasks", nargs="+", type=int, default=[1, 2, 3],
                        metavar="N",
                        help="Tasks to run (1, 2, 3; default: all)")
    args = parser.parse_args()

    newspapers = args.newspapers or NEWSPAPERS
    invalid = [n for n in newspapers if n not in NEWSPAPERS]
    if invalid:
        print(f"[ERROR] Unknown newspaper(s): {invalid}")
        print(f"        Valid: {NEWSPAPERS}")
        sys.exit(1)

    plot = not args.no_plots

    print(f"Output → {MINIMAL_DIR.relative_to(BASE_DIR)}/")
    print(f"LaTeX tables: enabled for cross-newspaper and global views")

    if 1 in args.tasks:
        run_task1(
            newspapers, plot,
            base_dir=MINIMAL_DIR / TASK_DIRS["task1"],
            with_latex=True,
        )

    if 2 in args.tasks:
        run_task2(
            newspapers, plot,
            base_dir=MINIMAL_DIR / TASK_DIRS["task2"],
            with_latex=True,
        )

    if 3 in args.tasks:
        run_task3(
            newspapers, plot,
            base_dir=MINIMAL_DIR / TASK_DIRS["task3"],
            with_latex=True,
        )

    total_files = sum(1 for _ in MINIMAL_DIR.rglob("*") if _.is_file())
    print(f"\nDone. {total_files} files written under output-minimal/")


if __name__ == "__main__":
    main()
