#!/usr/bin/env python3
"""
Build comprehensive figure includes for each task and insert \\includegraphics
blocks into the comprehensive documents (not the main submission).

Usage:
  python build_comprehensive_figures.py --task task1
  python build_comprehensive_figures.py --task all

Tasks:
  task1 -> figures under LaTeX/Canonical-Reduced-Register-Comparison-Part-1-ACL-ARR/figures
  task2 -> figures under LaTeX/Canonical-Reduced-Register-Transformation-Part-2-ACL-ARR/figures
  task3 -> figures under LaTeX/Canonical-Reduced-Register-Complexity-Part-3-ACL-ARR/figures

Notes:
- Generates \\section*{Auto-generated Figures} with one figure environment per image.
- Captions/labels are derived from filenames (friendly, but still placeholders).
- LaTeX files remain ignored unless you choose to track them.
"""

import argparse
import os
from pathlib import Path
from typing import List, Dict

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".svg", ".pdf"}


def friendly_caption(path: Path) -> str:
    stem = path.stem.replace("_", " ").replace("-", " ")
    return stem.title()


def friendly_label(task: str, path: Path) -> str:
    return f"fig:{task}-{path.stem.replace('_','-')}"


def collect_figures(task: str) -> Dict[str, List[Path]]:
    if task == "task1":
        root = Path("LaTeX/Canonical-Reduced-Register-Comparison-Part-1-ACL-ARR/figures")
        doc = Path("LaTeX/Canonical-Reduced-Register-Comparison-Part-1-ACL-ARR/Task-1-Comprehensive-Figures.tex")
    elif task == "task2":
        root = Path("LaTeX/Canonical-Reduced-Register-Transformation-Part-2-ACL-ARR/figures")
        doc = Path("LaTeX/Canonical-Reduced-Register-Transformation-Part-2-ACL-ARR/Task-2-Comprehensive-Figures.tex")
    elif task == "task3":
        root = Path("LaTeX/Canonical-Reduced-Register-Complexity-Part-3-ACL-ARR/figures")
        doc = Path("LaTeX/Canonical-Reduced-Register-Complexity-Part-3-ACL-ARR/Task-3-Comprehensive-Figures.tex")
    else:
        raise ValueError(f"Unknown task: {task}")

    figures = []
    if root.exists():
        for path in sorted(root.rglob("*")):
            if path.suffix.lower() in IMAGE_EXTS and path.is_file():
                figures.append(path)

    return {"doc": doc, "figures": figures}


def build_block(doc: Path, figures: List[Path], task: str) -> str:
    if not figures:
        return ""
    lines = []
    lines.append("% ===== Auto-generated Figures (do not edit by hand) =====")
    lines.append("\\section*{Auto-generated Figures}")
    for fig in figures:
        rel = fig.relative_to(doc.parent)
        caption = friendly_caption(fig)
        label = friendly_label(task, fig)
        lines.append("\\begin{figure}[htbp]")
        lines.append("\\centering")
        lines.append("\\includegraphics[width=0.9\\columnwidth]{" + rel.as_posix() + "}")
        lines.append(f"\\caption{{{caption}}}")
        lines.append(f"\\label{{{label}}}")
        lines.append("\\end{figure}")
        lines.append("")
    lines.append("% ===== End auto-generated figures =====")
    return "\n".join(lines)


def append_block(doc: Path, block: str):
    if not block.strip():
        return
    with open(doc, "a", encoding="utf-8") as f:
        f.write("\n\n" + block + "\n")


def main():
    parser = argparse.ArgumentParser(description="Insert all figures into comprehensive documents for review.")
    parser.add_argument(
        "--task",
        choices=["task1", "task2", "task3", "all"],
        default="all",
        help="Which task(s) to process.",
    )
    args = parser.parse_args()

    tasks = ["task1", "task2", "task3"] if args.task == "all" else [args.task]

    for task in tasks:
        cfg = collect_figures(task)
        doc = cfg["doc"]
        figures = cfg["figures"]
        block = build_block(doc, figures, task)
        append_block(doc, block)
        print(f"[{task}] Inserted {len(figures)} figures into {doc}")


if __name__ == "__main__":
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
    os.environ.setdefault("KMP_AFFINITY", "disabled")
    os.environ.setdefault("KMP_INIT_AT_FORK", "FALSE")
    main()
