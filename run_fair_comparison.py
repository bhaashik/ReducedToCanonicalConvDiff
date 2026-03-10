"""
run_fair_comparison.py
======================
Top-level CLI runner for the fair-comparison analysis layer.

Produces opportunity-normalized, log2-transformed, and optionally weighted
feature profiles for all three newspapers.  The original events_global.csv
and all existing pipeline outputs are untouched.

Usage
-----
    python run_fair_comparison.py                            # all newspapers, all methods, with plots
    python run_fair_comparison.py --no-plots                 # CSV only, no figures
    python run_fair_comparison.py --newspapers "The-Hindu"   # single newspaper

Output
------
Per newspaper:
    output/task-1-comparative-study/per-newspaper/{NP}/events_fair.csv
    output/task-1-comparative-study/per-newspaper/{NP}/visualizations/fair_comparison/

Global:
    output/task-1-comparative-study/global/events_fair_global.csv
    output/task-1-comparative-study/global/visualizations/fair_comparison/
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from paths_config import NEWSPAPERS
from register_comparison.analysis.fair_comparison_pipeline import FairComparisonPipeline


def main():
    parser = argparse.ArgumentParser(
        description="Fair comparison analysis: opportunity normalization + log2 + weighting"
    )
    parser.add_argument(
        "--newspapers", nargs="+", default=None,
        metavar="NP",
        help=(
            f"Newspapers to process (default: all three). "
            f"Choices: {NEWSPAPERS}"
        ),
    )
    parser.add_argument(
        "--no-plots", action="store_true",
        help="Skip figure generation; save CSV only.",
    )
    args = parser.parse_args()

    newspapers = args.newspapers or NEWSPAPERS
    # Validate
    invalid = [n for n in newspapers if n not in NEWSPAPERS]
    if invalid:
        print(f"[ERROR] Unknown newspaper(s): {invalid}")
        print(f"        Valid choices: {NEWSPAPERS}")
        sys.exit(1)

    plot = not args.no_plots
    pipe = FairComparisonPipeline(plot=plot)

    if len(newspapers) == len(NEWSPAPERS):
        # All three → also produce global cross-newspaper figures
        pipe.run_all_newspapers()
    else:
        for np_name in newspapers:
            pipe.run(np_name)


if __name__ == "__main__":
    main()
