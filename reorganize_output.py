#!/usr/bin/env python3
"""
Reorganize output/ into a clean, task-oriented directory structure.

Target layout
─────────────
output/
├── task-1-comparative-study/
│   ├── per-newspaper/{NP}/          ← all Task-1 per-NP files
│   └── global/
│       └── cross-newspaper-morphological/
├── task-2-transformation-study/
│   ├── per-newspaper/{NP}/
│   │   └── morphological-rules/     ← {NP}/morphological_analysis/
│   ├── bidirectional-transformation/
│   └── global/
│       ├── morphological-rules/
│       ├── visualizations/
│       └── morphological-comparative-analysis/
├── task-3-complexity-similarity-study/
│   ├── per-newspaper/
│   ├── global/
│   ├── figures/
│   ├── tables/
│   └── correlation/
├── common/                           ← kept (empty placeholder for now)
└── perhaps-useful/
    ├── multilevel-complexity-legacy/
    └── multilevel-similarity-legacy/

Run from the project root:
    python reorganize_output.py [--dry-run]
"""

import argparse
import shutil
from pathlib import Path

BASE = Path(__file__).parent / "output"
NEWSPAPERS = ["Times-of-India", "Hindustan-Times", "The-Hindu"]


def log(msg: str):
    print(msg)


def move(src: Path, dst: Path, dry: bool):
    if not src.exists():
        return
    if dry:
        log(f"  [DRY] mv  {src.relative_to(BASE)}  →  {dst.relative_to(BASE)}")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        if dst.exists():
            # Merge: move files one by one
            for item in src.iterdir():
                move(item, dst / item.name, dry)
            try:
                src.rmdir()
            except OSError:
                pass
        else:
            shutil.move(str(src), str(dst))
    else:
        shutil.move(str(src), str(dst))
    log(f"  mv  {src.relative_to(BASE)}  →  {dst.relative_to(BASE)}")


def rmdir_if_empty(path: Path, dry: bool):
    if not path.exists():
        return
    # Remove all empty subdirectories recursively, then the dir itself if empty
    for child in sorted(path.rglob("*"), reverse=True):
        if child.is_dir():
            try:
                if not dry:
                    child.rmdir()
                log(f"  rmdir (empty) {child.relative_to(BASE)}")
            except OSError:
                pass
    try:
        if not dry:
            path.rmdir()
        log(f"  rmdir (empty) {path.relative_to(BASE)}")
    except OSError:
        pass


def reorganize(dry: bool = False):
    t1 = BASE / "task-1-comparative-study"
    t2 = BASE / "task-2-transformation-study"
    t3 = BASE / "task-3-complexity-similarity-study"
    pu = BASE / "perhaps-useful"

    # ── Task 1: per-newspaper flat dirs ──────────────────────────────────────
    log("\n[Task 1] Per-newspaper files")
    for np in NEWSPAPERS:
        src_np = BASE / np
        if not src_np.exists():
            continue
        dst_np = t1 / "per-newspaper" / np
        dst_np.mkdir(parents=True, exist_ok=True)

        # Move morphological_analysis first (belongs to Task 2)
        morph_src = src_np / "morphological_analysis"
        if morph_src.exists():
            move(morph_src, t2 / "per-newspaper" / np / "morphological-rules", dry)

        # Move all remaining files/dirs into Task 1 per-newspaper
        if not dry:
            dst_np.mkdir(parents=True, exist_ok=True)
        for item in list(src_np.iterdir()):
            move(item, dst_np / item.name, dry)

        # Remove now-empty source dir
        if not dry:
            try:
                src_np.rmdir()
                log(f"  rmdir {np}/")
            except OSError:
                pass

    # ── Task 1: global aggregated cross-newspaper morphological ──────────────
    log("\n[Task 1] Global aggregated outputs")
    move(BASE / "AGGREGATED_CROSS_NEWSPAPER",
         t1 / "global" / "cross-newspaper-morphological", dry)

    # ── Task 2: transformation-study subtree ─────────────────────────────────
    log("\n[Task 2] Transformation study content")
    ts = BASE / "transformation-study"
    if ts.exists():
        # Bidirectional transformation → task-2/bidirectional-transformation/
        move(ts / "bidirectional-transformation",
             t2 / "bidirectional-transformation", dry)

        # Morphological rules global summary
        move(ts / "morphological-rules",
             t2 / "global" / "morphological-rules", dry)

        # Visualizations
        move(ts / "visualizations",
             t2 / "global" / "visualizations", dry)

        # Top-level summary report
        summary = ts / "TASK2_SUMMARY_REPORT.md"
        if summary.exists():
            move(summary, t2 / "TASK2_SUMMARY_REPORT.md", dry)

        # Remove remaining empty subdirs
        rmdir_if_empty(ts, dry)

    # Task 2: cross-newspaper morphological visualizations
    log("\n[Task 2] Cross-newspaper morphological visualizations")
    move(BASE / "comprehensive_morphological_visualizations",
         t2 / "global" / "visualizations", dry)   # merge into same viz dir

    # Task 2: morphological comparative analysis
    move(BASE / "morphological_comparative_analysis",
         t2 / "global" / "morphological-comparative-analysis", dry)

    # ── Task 3: complexity-similarity-study subtree ───────────────────────────
    log("\n[Task 3] Complexity-similarity-study content")
    cs = BASE / "complexity-similarity-study"
    if cs.exists():
        for item in list(cs.iterdir()):
            move(item, t3 / item.name, dry)
        try:
            if not dry:
                cs.rmdir()
                log("  rmdir complexity-similarity-study/")
        except OSError:
            pass

    # ── perhaps-useful: legacy multilevel runners ─────────────────────────────
    log("\n[perhaps-useful] Legacy multilevel outputs")
    move(BASE / "multilevel_complexity",
         pu / "multilevel-complexity-legacy", dry)
    move(BASE / "multilevel_similarity",
         pu / "multilevel-similarity-legacy", dry)

    # ── Clean up empty dirs from pipeline setup ───────────────────────────────
    log("\n[Cleanup] Removing empty directories")
    for empty_name in [
        "comparative-study",
        "progressive_coverage_with_morphology",
    ]:
        rmdir_if_empty(BASE / empty_name, dry)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reorganize output/ directory")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print actions without executing")
    args = parser.parse_args()

    if args.dry_run:
        print("=== DRY RUN — no files will be moved ===\n")

    reorganize(dry=args.dry_run)
    print("\nDone.")
