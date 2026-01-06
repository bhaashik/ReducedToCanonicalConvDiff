#!/usr/bin/env python3
"""
Generate per-task Markdown and HTML review files with side-by-side table/figure pairs.
Outputs:
  TABLES-FIGURES-ALL-MD/Task-1-COMPREHENSIVE.{md,html}
  TABLES-FIGURES-ALL-MD/Task-2-COMPREHENSIVE.{md,html}
  TABLES-FIGURES-ALL-MD/Task-3-COMPREHENSIVE.{md,html}

Rules:
- Pair tables and figures by mnemonic precedence (shared stem tokens), otherwise by best stem overlap.
- No repeats; if a table matches multiple figures, only the best match is kept.
- Skip the two largest CSVs per task and any CSV > max_csv_mb; include a top-15 summary (by first numeric column desc or head) for skipped tables.
- Skip figures over max_fig_mb.
- Sections: Task -> Global -> Feature family buckets (lexical, punctuation, morphological, syntactic, other),
  then Task -> Per-newspaper -> Feature family buckets. Unpaired summaries allowed.
"""

import argparse
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Set

import pandas as pd
from pandas.errors import EmptyDataError

BASE = Path(".")
OUT_DIR = BASE / "TABLES-FIGURES-ALL-MD"
NEWSPAPERS = ["Times-of-India", "Hindustan-Times", "The-Hindu"]
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".svg", ".pdf"}
FAMILIES = ["punctuation", "morphological", "lexical", "syntactic"]

TASKS = {
    "Task 1": {
        "tables_root": BASE / "output" / "comparative-study",
        "fig_dirs": [
            BASE / "LaTeX" / "Canonical-Reduced-Register-Comparison-Part-1-ACL-ARR" / "figures",
            BASE / "LaTeX" / "Canonical-Reduced-Register-Comparison-Part-1-ACL-ARR",
        ],
    },
    "Task 2": {
        "tables_root": BASE / "output" / "transformation-study",
        "fig_dirs": [
            BASE / "LaTeX" / "Canonical-Reduced-Register-Transformation-Part-2-ACL-ARR" / "figures",
        ],
    },
    "Task 3": {
        "tables_root": BASE / "output" / "complexity-similarity-study",
        "fig_dirs": [
            BASE / "LaTeX" / "Canonical-Reduced-Register-Complexity-Part-3-ACL-ARR" / "figures",
        ],
    },
}


def size_mb(p: Path) -> float:
    return p.stat().st_size / (1024 * 1024)


def collect_csvs(root: Path) -> List[Path]:
    return [p for p in root.rglob("*.csv") if p.is_file()]


def collect_figs(dirs: List[Path]) -> List[Path]:
    figs = []
    for d in dirs:
        if d.exists():
            for p in d.rglob("*"):
                if p.suffix.lower() in IMAGE_EXTS and p.is_file():
                    figs.append(p)
    return figs


def tokenize(stem: str) -> Set[str]:
    tokens = []
    for part in stem.replace("-", "_").split("_"):
        part = part.lower()
        if not part or part in {"combined", "global"}:
            continue
        tokens.append(part)
    return set(tokens)


def family_for(path: Path) -> str:
    stem = path.stem.lower()
    for fam in FAMILIES:
        if fam in stem:
            return fam
    return "other"


def summarize_csv(path: Path, max_cols: int = 20, top_n: int = 15) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
    except EmptyDataError:
        return pd.DataFrame()
    df = df.dropna(axis=1, how="all")
    numeric_cols = df.select_dtypes(include=["number"]).columns
    for col in numeric_cols:
        if (df[col].fillna(0).abs() == 0).all():
            df = df.drop(columns=[col])
    if df.empty:
        return df
    if df.shape[1] > max_cols:
        df = df.iloc[:, :max_cols]
    sort_col = None
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            sort_col = col
            break
    if sort_col:
        df = df.sort_values(by=sort_col, ascending=False)
    return df.head(top_n)


def best_pair(table_tokens: Set[str], figures: List[Path], used: Set[Path]) -> Path | None:
    best = None
    best_score = 0
    for fig in figures:
        if fig in used:
            continue
        ftok = tokenize(fig.stem)
        score = len(table_tokens & ftok)
        if score > best_score:
            best_score = score
            best = fig
    return best if best_score > 0 else None


def render_md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    try:
        return df.to_markdown(index=False, tablefmt="github")
    except Exception:
        # Fallback simple pipe table
        headers = list(df.columns)
        rows = df.values.tolist()
        header_line = "| " + " | ".join(str(h) for h in headers) + " |"
        sep_line = "| " + " | ".join(["---"] * len(headers)) + " |"
        body = []
        for row in rows:
            body.append("| " + " | ".join("" if pd.isna(v) else str(v) for v in row) + " |")
        return "\n".join([header_line, sep_line] + body)


def render_html_table(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    return df.to_html(index=False, escape=True)


def safe_read_csv(path: Path) -> pd.DataFrame | None:
    try:
        return pd.read_csv(path)
    except EmptyDataError:
        return None


def build_task(task_name: str, cfg: Dict, max_csv_mb: float, max_fig_mb: float):
    out_md = OUT_DIR / f"{task_name.replace(' ', '-')}-COMPREHENSIVE.md"
    out_html = OUT_DIR / f"{task_name.replace(' ', '-')}-COMPREHENSIVE.html"

    tables = collect_csvs(cfg["tables_root"])
    figures = collect_figs(cfg["fig_dirs"])

    # Skip top 2 largest CSVs per task
    skip_top = {p for p, _ in sorted([(p, size_mb(p)) for p in tables], key=lambda x: x[1], reverse=True)[:2]}

    # Prepare structures: global vs per-paper
    def area(p: Path) -> Tuple[str, str]:
        # returns (scope, paper or 'global')
        for paper in NEWSPAPERS:
            if paper in p.parts:
                return ("per-paper", paper)
        return ("global", "global")

    grouped_tables = defaultdict(list)
    for t in tables:
        grouped_tables[area(t)].append(t)
    grouped_figs = defaultdict(list)
    for f in figures:
        grouped_figs[area(f)].append(f)

    md_lines = [f"# {task_name} Comprehensive Tables and Figures", "", f"CSV limit: {max_csv_mb} MB (skips top 2 largest); Figure limit: {max_fig_mb} MB.", ""]
    html_lines = [
        "<html><head><meta charset='utf-8'><style>table {border-collapse: collapse;} th, td {border: 1px solid #999; padding: 4px;} img {max-width: 100%; height: auto;} .skipped {color: #888; font-style: italic;} .pair {display: flex; gap: 16px;} .pair div {flex: 1;} </style></head><body>",
        f"<h1>{task_name} Comprehensive Tables and Figures</h1><p>CSV limit: {max_csv_mb} MB (skips top 2 largest); Figure limit: {max_fig_mb} MB.</p>",
    ]

    for scope in ["global", "per-paper"]:
        md_lines.append(f"## {scope.title()}")
        html_lines.append(f"<h2>{scope.title()}</h2>")
        subareas = grouped_tables.keys() | grouped_figs.keys()
        for area_key in sorted({a for a in subareas if a[0] == scope}, key=lambda x: x[1]):
            scope_name, paper = area_key
            md_lines.append(f"### {paper}")
            html_lines.append(f"<h3>{paper}</h3>")

            # bucket by family
            fam_buckets = {fam: {"tables": [], "figs": []} for fam in FAMILIES + ["other"]}
            for t in grouped_tables.get(area_key, []):
                fam_buckets[family_for(t)]["tables"].append(t)
            for f in grouped_figs.get(area_key, []):
                fam_buckets[family_for(f)]["figs"].append(f)

            for fam in FAMILIES + ["other"]:
                tables_list = fam_buckets[fam]["tables"]
                figs_list = fam_buckets[fam]["figs"]
                if not tables_list and not figs_list:
                    continue
                md_lines.append(f"#### {fam.title()}")
                html_lines.append(f"<h4>{fam.title()}</h4>")

                used_figs = set()
                for t in sorted(tables_list):
                    if t in skip_top:
                        summary_df = summarize_csv(t)
                        md_lines.append(f"- Skipped large table: {t} (top summary below)")
                        md_lines.append(render_md_table(summary_df))
                        html_lines.append(f"<p class='skipped'>Skipped large table: {t} (summary below)</p>")
                        html_lines.append(render_html_table(summary_df))
                        continue
                    if size_mb(t) > max_csv_mb:
                        summary_df = summarize_csv(t)
                        md_lines.append(f"- Skipped >{max_csv_mb}MB: {t} (summary below)")
                        md_lines.append(render_md_table(summary_df))
                        html_lines.append(f"<p class='skipped'>Skipped >{max_csv_mb}MB: {t} (summary below)</p>")
                        html_lines.append(render_html_table(summary_df))
                        continue
                    table_tokens = tokenize(t.stem)
                    paired_fig = best_pair(table_tokens, figs_list, used_figs)
                    df_table = safe_read_csv(t)
                    if df_table is None:
                        md_lines.append(f"- Skipped empty table: {t}")
                        html_lines.append(f"<p class='skipped'>Skipped empty table: {t}</p>")
                        continue
                    md_table = render_md_table(df_table)
                    if paired_fig and size_mb(paired_fig) <= max_fig_mb:
                        used_figs.add(paired_fig)
                        md_lines.append(f"**{t}** (paired with {paired_fig})")
                        md_lines.append(f"<table><tr><td>{md_table}</td><td>![{paired_fig.stem}]({paired_fig.relative_to(BASE).as_posix()})</td></tr></table>")
                        html_lines.append("<div class='pair'><div>")
                        html_lines.append(f"<p><b>{t}</b></p>")
                        html_lines.append(render_html_table(df_table))
                        html_lines.append("</div><div>")
                        html_lines.append(f"<p>{paired_fig}</p><img src='{paired_fig.relative_to(BASE).as_posix()}' alt='{paired_fig.stem}'/>")
                        html_lines.append("</div></div>")
                    else:
                        md_lines.append(f"**{t}**")
                        md_lines.append(md_table)
                        html_lines.append(f"<p><b>{t}</b></p>")
                        html_lines.append(render_html_table(df_table))

                # Any remaining figures not used
                for f in sorted(figs_list):
                    if f in used_figs:
                        continue
                    if size_mb(f) > max_fig_mb:
                        html_lines.append(f"<p class='skipped'>Skipped figure >{max_fig_mb}MB: {f}</p>")
                        md_lines.append(f"- Skipped figure >{max_fig_mb}MB: {f}")
                        continue
                    md_lines.append(f"![{f.stem}]({f.relative_to(BASE).as_posix()})")
                    html_lines.append(f"<div><p>{f}</p><img src='{f.relative_to(BASE).as_posix()}' alt='{f.stem}'/></div>")

    html_lines.append("</body></html>")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(md_lines), encoding="utf-8")
    out_html.write_text("\n".join(html_lines), encoding="utf-8")
    print(f"Wrote {out_md} and {out_html}")


def main():
    parser = argparse.ArgumentParser(description="Build per-task MD/HTML with paired tables and figures.")
    parser.add_argument("--max-csv-size-mb", type=float, default=1.0, help="Skip CSVs larger than this size.")
    parser.add_argument("--max-figure-size-mb", type=float, default=5.0, help="Skip figures larger than this size.")
    args = parser.parse_args()

    for task_name, cfg in TASKS.items():
        build_task(task_name, cfg, args.max_csv_size_mb, args.max_figure_size_mb)


if __name__ == "__main__":
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
    os.environ.setdefault("KMP_AFFINITY", "disabled")
    os.environ.setdefault("KMP_INIT_AT_FORK", "FALSE")
    main()
