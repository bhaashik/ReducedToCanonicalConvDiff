#!/usr/bin/env python3
"""
Generate a single HTML reference with tables (rendered via pandas) and figures for all tasks.
Skips the two largest CSVs and any CSV over a size threshold to keep the page responsive.

Output: TABLES-FIGURES-ALL-MD/comprehensive.html

Usage:
  python build_comprehensive_html.py [--max-csv-size-mb 2] [--max-figure-size-mb 10]
"""

import argparse
import os
from pathlib import Path
from typing import List, Tuple

import pandas as pd
from pandas.errors import EmptyDataError

BASE = Path('.')
OUT_DIR = BASE / 'TABLES-FIGURES-ALL-MD'
OUT_FILE = OUT_DIR / 'comprehensive.html'

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


def friendly_caption(path: Path) -> str:
    stem = path.stem.replace('_', ' ').replace('-', ' ')
    return stem.title()


def csv_to_html_table(path: Path, max_cols: int = 30) -> str:
    try:
        df = pd.read_csv(path)
    except EmptyDataError:
        return ''

    # Drop fully empty columns
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
    if df.shape[1] > max_cols:
        df = df.iloc[:, :max_cols]
    return df.to_html(index=False, escape=True)


def main():
    parser = argparse.ArgumentParser(description="Build HTML with tables and figures for review.")
    parser.add_argument('--max-csv-size-mb', type=float, default=2.0, help='Skip CSVs larger than this size.')
    parser.add_argument('--max-figure-size-mb', type=float, default=10.0, help='Skip figures larger than this size.')
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # gather largest CSVs to skip top 2
    all_csvs: List[Tuple[Path, float]] = []
    for info in TASKS.values():
        for csv in collect_csvs(info['tables_root']):
            all_csvs.append((csv, size_mb(csv)))
    skip_top = {p for p, _ in sorted(all_csvs, key=lambda x: x[1], reverse=True)[:2]}

    html_lines: List[str] = []
    html_lines.append("<html><head><meta charset='utf-8'><style>table {border-collapse: collapse;} th, td {border: 1px solid #999; padding: 4px;} img {max-width: 100%; height: auto;} .skipped {color: #888; font-style: italic;} </style></head><body>")
    html_lines.append(f"<h1>Comprehensive Tables and Figures</h1><p>CSV limit: {args.max_csv_size_mb} MB (skip top 2 largest); Figure limit: {args.max_figure_size_mb} MB.</p>")

    for task_name, info in TASKS.items():
        html_lines.append(f"<h2>{task_name}</h2>")

        # Tables
        html_lines.append("<h3>Tables</h3>")
        task_csvs = collect_csvs(info['tables_root'])
        kept = 0
        for csv in sorted(task_csvs):
            if csv in skip_top:
                html_lines.append(f"<p class='skipped'>Skipped (top size): {csv}</p>")
                continue
            mb = size_mb(csv)
            if mb > args.max_csv_size_mb:
                html_lines.append(f"<p class='skipped'>Skipped ({mb:.2f} MB > {args.max_csv_size_mb} MB): {csv}</p>")
                continue
            table_html = csv_to_html_table(csv)
            if not table_html.strip():
                continue
            rel = csv.relative_to(BASE)
            html_lines.append(f"<h4>{rel}</h4>")
            html_lines.append(table_html)
            kept += 1
        if kept == 0:
            html_lines.append("<p class='skipped'>(No tables included)</p>")

        # Figures
        html_lines.append("<h3>Figures</h3>")
        figs = collect_figs(info['fig_dirs'])
        kept_figs = 0
        for fig in sorted(figs):
            mb = size_mb(fig)
            if mb > args.max_figure_size_mb:
                html_lines.append(f"<p class='skipped'>Skipped ({mb:.2f} MB > {args.max_figure_size_mb} MB): {fig}</p>")
                continue
            rel = fig.relative_to(BASE)
            caption = friendly_caption(fig)
            html_lines.append(f"<div><p>{caption}</p><img src='{rel.as_posix()}' alt='{caption}'/></div>")
            kept_figs += 1
        if kept_figs == 0:
            html_lines.append("<p class='skipped'>(No figures included)</p>")

    html_lines.append("</body></html>")
    OUT_FILE.write_text("\n".join(html_lines), encoding='utf-8')
    print(f"Wrote {OUT_FILE} (HTML with size filters; skipped top 2 largest CSVs)")


if __name__ == '__main__':
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
    os.environ.setdefault("KMP_AFFINITY", "disabled")
    os.environ.setdefault("KMP_INIT_AT_FORK", "FALSE")
    main()
