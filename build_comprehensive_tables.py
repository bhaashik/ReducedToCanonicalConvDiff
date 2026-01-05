#!/usr/bin/env python3
"""
Build comprehensive LaTeX tables for each task and insert \\input statements
into the comprehensive documents (not the main submission). Designed for quick
review of all tables before selecting for the main papers.

Usage:
  python build_comprehensive_tables.py --task task1
  python build_comprehensive_tables.py --task all

Tasks:
  task1 -> comparative-study tables (excludes raw events)
  task2 -> transformation-study tables (coverage, morphology, lexical, etc.)
  task3 -> complexity-similarity-study tables (perplexity, correlation, mt-eval)

Notes:
- Generates .tex tables using pandas (longtable=True for multi-page tables).
- Appends an "Auto-generated Tables" section with \\input{...} at end of each
  comprehensive document. Paths are relative to the task LaTeX directory.
- LaTeX files remain ignored unless you choose to track them.
"""

import argparse
import os
from pathlib import Path
from typing import List, Dict


def csv_to_latex_longtable(csv_path: Path, caption: str, label: str) -> str:
    import pandas as pd
    from pandas.errors import EmptyDataError

    try:
        df = pd.read_csv(csv_path)
    except EmptyDataError:
        return ""
    latex_body = df.to_latex(
        index=False,
        escape=True,
        na_rep="--",
        longtable=True,
    )
    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        latex_body,
        f"\\caption{{{caption}}}",
        f"\\label{{{label}}}",
        "\\end{table}",
    ]
    return "\n".join(lines)


def friendly_caption(path: Path) -> str:
    stem = path.stem.replace("_", " ").replace("-", " ")
    return stem.title()


def friendly_label(task: str, path: Path) -> str:
    return f"tab:{task}-{path.stem.replace('_','-')}"


def write_tables(task: str, csv_files: List[Path], tex_dir: Path) -> List[Path]:
    tex_dir.mkdir(parents=True, exist_ok=True)
    created = []
    for csv in csv_files:
        if csv.stat().st_size == 0:
            continue
        caption = friendly_caption(csv)
        label = friendly_label(task, csv)
        tex_content = csv_to_latex_longtable(csv, caption, label)
        if not tex_content.strip():
            continue
        tex_path = tex_dir / f"{csv.stem}.tex"
        with open(tex_path, "w", encoding="ascii", errors="ignore") as f:
            f.write(tex_content)
        created.append(tex_path)
    return created


def append_inputs_to_doc(doc_path: Path, tex_paths: List[Path]):
    if not tex_paths:
        return
    tex_paths = sorted(tex_paths)
    rel_inputs = [p.relative_to(doc_path.parent) for p in tex_paths]
    block = ["% ===== Auto-generated Tables (do not edit by hand) =====", "\\section*{Auto-generated Tables}"]
    for p in rel_inputs:
        block.append(f"\\input{{{p.as_posix()}}}")
    block.append("% ===== End auto-generated tables =====")
    with open(doc_path, "a", encoding="utf-8") as f:
        f.write("\n\n" + "\n".join(block) + "\n")


def collect_csvs(task: str) -> Dict[str, List[Path]]:
    base = Path("output")
    if task == "task1":
        root = base / "comparative-study"
        csvs = [p for p in root.rglob("*.csv") if "events" not in p.parts]
        doc = Path("LaTeX/Canonical-Reduced-Register-Comparison-Part-1-ACL-ARR/Task-1-Comprehensive-Figures.tex")
        tex_dir = doc.parent / "tables"
        return {"doc": doc, "tex_dir": tex_dir, "csvs": csvs}
    if task == "task2":
        root = base / "transformation-study"
        csvs = [p for p in root.rglob("*.csv")]
        doc = Path("LaTeX/Canonical-Reduced-Register-Transformation-Part-2-ACL-ARR/Task-2-Comprehensive-Figures.tex")
        tex_dir = doc.parent / "tables"
        return {"doc": doc, "tex_dir": tex_dir, "csvs": csvs}
    if task == "task3":
        root = base / "complexity-similarity-study"
        csvs = [p for p in root.rglob("*.csv")]
        doc = Path("LaTeX/Canonical-Reduced-Register-Complexity-Part-3-ACL-ARR/Task-3-Comprehensive-Figures.tex")
        tex_dir = doc.parent / "tables"
        return {"doc": doc, "tex_dir": tex_dir, "csvs": csvs}
    raise ValueError(f"Unknown task: {task}")


def main():
    parser = argparse.ArgumentParser(description="Generate LaTeX tables from CSVs and insert into comprehensive docs.")
    parser.add_argument(
        "--task",
        choices=["task1", "task2", "task3", "all"],
        default="all",
        help="Which task(s) to process.",
    )
    args = parser.parse_args()

    tasks = ["task1", "task2", "task3"] if args.task == "all" else [args.task]

    for task in tasks:
        cfg = collect_csvs(task)
        doc = cfg["doc"]
        tex_dir = cfg["tex_dir"]
        csvs = cfg["csvs"]
        created = write_tables(task, csvs, tex_dir)
        append_inputs_to_doc(doc, created)
        print(f"[{task}] Generated {len(created)} tables and updated {doc}")


if __name__ == "__main__":
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
    os.environ.setdefault("KMP_AFFINITY", "disabled")
    os.environ.setdefault("KMP_INIT_AT_FORK", "FALSE")
    main()
