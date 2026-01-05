#!/usr/bin/env python3
"""
Insert all figures for a task into the comprehensive document (not the main submission).

Usage:
  python build_comprehensive_figures.py --task task1
  python build_comprehensive_figures.py --task all

Notes:
- Figures are collected from the task's `figures/` directory (and any PNG/JPG/SVG/PDF in the task root).
- Captions/labels are derived from filenames (placeholders for review).
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
        root = Path("LaTeX/Canonical-Reduced-Register-Comparison-Part-1-ACL-ARR")
        fig_dirs = [root / "figures", root]
        doc = root / "Task-1-Comprehensive-Figures.tex"
    elif task == "task2":
        root = Path("LaTeX/Canonical-Reduced-Register-Transformation-Part-2-ACL-ARR")
        fig_dirs = [root / "figures"]
        doc = root / "Task-2-Comprehensive-Figures.tex"
    elif task == "task3":
        root = Path("LaTeX/Canonical-Reduced-Register-Complexity-Part-3-ACL-ARR")
        fig_dirs = [root / "figures"]
        doc = root / "Task-3-Comprehensive-Figures.tex"
    else:
        raise ValueError(f"Unknown task: {task}")

    figures = []
    for d in fig_dirs:
        if d.exists():
            for path in sorted(d.rglob("*")):
                if path.suffix.lower() in IMAGE_EXTS and path.is_file():
                    figures.append(path)

    return {"doc": doc, "figures": figures}


def build_block(doc: Path, figures: List[Path], task: str, max_size_mb: float) -> str:
    if not figures:
        return ""
    lines = []
    lines.append("% ===== Auto-generated Figures (do not edit by hand) =====")
    lines.append("\\section*{Auto-generated Figures}")
    for fig in figures:
        size_mb = fig.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            lines.append(f"% Skipped {fig} (size {size_mb:.2f} MB > {max_size_mb} MB)")
            continue
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
    parser.add_argument(
        "--max-figure-size-mb",
        type=float,
        default=1.0,
        help="Skip figures larger than this size (MB).",
    )
    args = parser.parse_args()

    tasks = ["task1", "task2", "task3"] if args.task == "all" else [args.task]

    for task in tasks:
        cfg = collect_figures(task)
        doc = cfg["doc"]
        figures = cfg["figures"]
        block = build_block(doc, figures, task, args.max_figure_size_mb)
        append_block(doc, block)
        print(f"[{task}] Processed {len(figures)} figures into {doc}")


if __name__ == "__main__":
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
    os.environ.setdefault("KMP_AFFINITY", "disabled")
    os.environ.setdefault("KMP_INIT_AT_FORK", "FALSE")
    main()
