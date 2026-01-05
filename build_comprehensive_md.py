#!/usr/bin/env python3
"""
Generate a single Markdown reference file with tables (as Markdown) and figure links
for all three tasks, to be browsed easily (e.g., in PyCharm). Skips the two largest
table CSVs and any CSVs over 1 MB. Figures are listed with relative paths and
skipping those over 1 MB.

Output: TABLES-FIGURES-ALL-MD/comprehensive.md (created alongside the LaTeX dir).

Usage:
  python build_comprehensive_md.py
"""

import os
from pathlib import Path
from typing import List, Tuple

import pandas as pd
from pandas.errors import EmptyDataError

BASE = Path('.')
OUT_DIR = BASE / 'TABLES-FIGURES-ALL-MD'
OUT_FILE = OUT_DIR / 'comprehensive.md'

CSV_MAX_MB = 1.0
FIG_MAX_MB = 1.0
IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.svg', '.pdf'}

TASKS = {
    'Task 1': {
        'tables_root': BASE / 'output' / 'comparative-study',
        'fig_dirs': [BASE / 'LaTeX' / 'Canonical-Reduced-Register-Comparison-Part-1-ACL-ARR' / 'figures',
                     BASE / 'LaTeX' / 'Canonical-Reduced-Register-Comparison-Part-1-ACL-ARR'],
    },
    'Task 2': {
        'tables_root': BASE / 'output' / 'transformation-study',
        'fig_dirs': [BASE / 'LaTeX' / 'Canonical-Reduced-Register-Transformation-Part-2-ACL-ARR' / 'figures'],
    },
    'Task 3': {
        'tables_root': BASE / 'output' / 'complexity-similarity-study',
        'fig_dirs': [BASE / 'LaTeX' / 'Canonical-Reduced-Register-Complexity-Part-3-ACL-ARR' / 'figures'],
    },
}


def size_mb(path: Path) -> float:
    return path.stat().st_size / (1024 * 1024)


def collect_csvs(root: Path) -> List[Path]:
    return [p for p in root.rglob('*.csv') if p.is_file()]


def collect_figs(dirs: List[Path]) -> List[Path]:
    figs = []
    for d in dirs:
        if d.exists():
            for p in d.rglob('*'):
                if p.suffix.lower() in IMAGE_EXTS and p.is_file():
                    figs.append(p)
    return figs


def csv_to_md_table(path: Path) -> str:
    try:
        df = pd.read_csv(path)
    except EmptyDataError:
        return ''
    # Drop all-empty columns
    df = df.dropna(axis=1, how='all')
    # Drop numeric columns that are all zero/NaN
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        col_data = df[col].fillna(0)
        if (col_data.abs() == 0).all():
            df = df.drop(columns=[col])
    # Drop rows that are all empty/zero
    def row_all_empty(row):
        num_zero = True
        for col in row.index:
            val = row[col]
            if pd.api.types.is_numeric_dtype(df[col]):
                if pd.notna(val) and abs(val) > 0:
                    num_zero = False
            else:
                if isinstance(val, str) and val.strip():
                    return False
                if pd.notna(val) and not isinstance(val, str):
                    return False
        return num_zero
    df = df[~df.apply(row_all_empty, axis=1)]
    if df.empty:
        return ''
    return df.to_markdown(index=False)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []
    lines.append('# Comprehensive Tables and Figures (Markdown)')
    lines.append('')
    lines.append(f'*CSV size limit*: {CSV_MAX_MB} MB (skips larger files)')
    lines.append(f'*Figure size limit*: {FIG_MAX_MB} MB (skips larger files)')
    lines.append('')

    # Collect all CSVs across tasks to find top two largest
    all_csvs: List[Tuple[Path, float]] = []
    for info in TASKS.values():
        for csv in collect_csvs(info['tables_root']):
            all_csvs.append((csv, size_mb(csv)))
    all_csvs_sorted = sorted(all_csvs, key=lambda x: x[1], reverse=True)
    skip_top = {p for p, _ in all_csvs_sorted[:2]}

    for task_name, info in TASKS.items():
        lines.append(f'## {task_name}')
        lines.append('')

        # Tables
        lines.append('### Tables')
        task_csvs = collect_csvs(info['tables_root'])
        kept = 0
        for csv in sorted(task_csvs):
            if csv in skip_top:
                lines.append(f'- Skipped (top size): {csv}')
                continue
            mb = size_mb(csv)
            if mb > CSV_MAX_MB:
                lines.append(f'- Skipped (>{CSV_MAX_MB}MB): {csv}')
                continue
            md_table = csv_to_md_table(csv)
            if not md_table.strip():
                continue
            rel = csv.relative_to(BASE)
            lines.append(f'#### {rel}')
            lines.append(md_table)
            lines.append('')
            kept += 1
        if kept == 0:
            lines.append('*(No tables included)*')
        lines.append('')

        # Figures
        lines.append('### Figures')
        figs = collect_figs(info['fig_dirs'])
        kept_figs = 0
        for fig in sorted(figs):
            mb = size_mb(fig)
            if mb > FIG_MAX_MB:
                lines.append(f'- Skipped (>{FIG_MAX_MB}MB): {fig}')
                continue
            rel = fig.relative_to(BASE)
            caption = friendly_caption(fig)
            lines.append(f'![{caption}]({rel.as_posix()})')
            kept_figs += 1
        if kept_figs == 0:
            lines.append('*(No figures included)*')
        lines.append('')

    OUT_FILE.write_text('\n'.join(lines), encoding='utf-8')
    print(f"Wrote {OUT_FILE} (tables/figures with size filters; skipped top 2 largest CSVs)")


if __name__ == '__main__':
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
    os.environ.setdefault("KMP_AFFINITY", "disabled")
    os.environ.setdefault("KMP_INIT_AT_FORK", "FALSE")
    main()
