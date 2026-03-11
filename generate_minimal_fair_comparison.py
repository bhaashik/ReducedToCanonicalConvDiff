"""
generate_minimal_fair_comparison.py
====================================
Produces cross-newspaper combined figures and tables for all 5 fair-comparison
analysis stages across all 3 tasks, placed in output-minimal/fair-comparison/.

Each figure shows all 3 newspapers in a single grouped horizontal bar chart.
Each table is a wide-format CSV + LaTeX booktabs file (feature × newspaper).

Output layout
-------------
output-minimal/fair-comparison/
├── task-1-comparative-study/
│   ├── 1-raw-counts/     count_raw.{png,csv,tex}
│   ├── 2-normalized/     rate_norm.{png,csv,tex}
│   ├── 3-log/            log2_norm.{png,csv,tex}
│   ├── 4-weighted/       score_lvl.{…}  score_idf.{…}
│   └── 5-information-theoretic/  score_jsd.{…}  score_pmi.{…}
├── task-2-transformation-study/
│   └── (same 5 stages with morph-feature data)
└── task-3-complexity-similarity-study/
    └── (same 5 stages with complexity / similarity metrics)

Usage
-----
    python generate_minimal_fair_comparison.py
    python generate_minimal_fair_comparison.py --no-plots
"""

import argparse
import os
import sys
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from config import BASE_DIR

# ── Paths ─────────────────────────────────────────────────────────────────────
OUTPUT_DIR = BASE_DIR / "output"
MINIMAL_DIR = BASE_DIR / "output-minimal" / "fair-comparison"

TASK_DIRS = {
    "task1": "task-1-comparative-study",
    "task2": "task-2-transformation-study",
    "task3": "task-3-complexity-similarity-study",
}

NP_COLS   = ["HT", "TH", "ToI"]
NP_LABELS = {"HT": "Hindustan-Times", "TH": "The-Hindu", "ToI": "Times-of-India"}
NP_COLORS = {"HT": "#E15759", "TH": "#4E79A7", "ToI": "#59A14F"}
SPLIT_AT  = 18   # features per figure before auto-splitting


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

def _src(task_key: str, stage: str, filename: str) -> Path:
    return OUTPUT_DIR / TASK_DIRS[task_key] / "fair-comparison" / stage / "tables" / filename


def _dst(task_key: str, stage: str) -> Path:
    p = MINIMAL_DIR / TASK_DIRS[task_key] / stage
    p.mkdir(parents=True, exist_ok=True)
    return p


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {path.relative_to(BASE_DIR)}")


def _to_latex(df: pd.DataFrame, path: Path, caption: str, label: str,
              id_col: str, extra_cols: list = None) -> None:
    """Write a booktabs LaTeX table."""
    extra_cols = extra_cols or []
    round_cols = [c for c in NP_COLS if c in df.columns]

    lines = [
        r"\begin{table}[htbp]",
        r"\small\centering",
        rf"\caption{{{caption}}}",
        rf"\label{{tab:{label}}}",
    ]
    all_cols = [id_col] + extra_cols + round_cols
    n = len(all_cols)
    fmt_str = "l" * (len([id_col] + extra_cols)) + "r" * len(round_cols)
    lines.append(rf"\begin{{tabular}}{{{fmt_str}}}")
    lines.append(r"\toprule")

    # Header
    header = " & ".join(
        NP_LABELS.get(c, c.replace("_", " ").title()) for c in all_cols
    )
    lines.append(header + r" \\")
    lines.append(r"\midrule")

    for _, row in df.iterrows():
        cells = []
        for c in all_cols:
            v = row.get(c, "")
            if pd.isna(v):
                cells.append("---")
            elif isinstance(v, float):
                cells.append(f"{v:.4f}")
            else:
                cells.append(str(v))
        lines.append(" & ".join(cells) + r" \\")

    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


# ── Figure core ───────────────────────────────────────────────────────────────

def _grouped_hbar(df: pd.DataFrame, id_col: str, title: str, xlabel: str,
                  use_abs: bool = False, color_col: str = None) -> plt.Figure:
    """Grouped horizontal bar chart: one group per feature, one bar per NP."""
    val_cols = [c for c in NP_COLS if c in df.columns]
    labels   = df[id_col].tolist()
    n_feat   = len(labels)
    n_np     = len(val_cols)

    # Sort by mean absolute value descending
    means = df[val_cols].apply(pd.to_numeric, errors="coerce").abs().mean(axis=1)
    order = means.argsort()[::-1]
    df    = df.iloc[order].reset_index(drop=True)
    labels = df[id_col].tolist()

    bar_h    = 0.22
    group_h  = bar_h * n_np + 0.08   # gap between groups
    fig_h    = max(4, n_feat * group_h + 1.5)
    fig, ax  = plt.subplots(figsize=(10, fig_h))

    y_centers = np.arange(n_feat) * group_h
    offsets   = np.linspace(-(n_np - 1) / 2, (n_np - 1) / 2, n_np) * bar_h

    for i, col in enumerate(val_cols):
        vals = pd.to_numeric(df[col], errors="coerce").fillna(0).values
        if use_abs:
            vals = np.abs(vals)
        color = NP_COLORS[col]
        ax.barh(
            y_centers + offsets[i], vals,
            height=bar_h, color=color, alpha=0.85,
            label=NP_LABELS[col], edgecolor="white", linewidth=0.4,
        )

    ax.set_yticks(y_centers)
    ax.set_yticklabels(labels, fontsize=8)
    ax.invert_yaxis()
    ax.axvline(0, color="black", linewidth=0.6, linestyle="--", alpha=0.4)
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_title(title, fontsize=10, fontweight="bold", pad=8)
    ax.legend(loc="lower right", fontsize=8, framealpha=0.7)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="y", labelsize=8)
    ax.tick_params(axis="x", labelsize=8)
    fig.tight_layout()
    return fig


def _emit(df: pd.DataFrame, id_col: str, title: str, xlabel: str,
          out_dir: Path, stem: str, caption: str, label: str,
          extra_cols: list = None, use_abs: bool = False, plot: bool = True) -> None:
    """Produce PNG + CSV + LaTeX for one metric, auto-splitting if too long."""
    extra_cols = extra_cols or []

    # Save CSV (always)
    df.to_csv(out_dir / f"{stem}.csv", index=False)

    # Save LaTeX
    _to_latex(df, out_dir / f"{stem}.tex", caption, label, id_col, extra_cols)

    if not plot:
        return

    # Auto-split figures
    n = len(df)
    if n <= SPLIT_AT:
        parts = [df]
        suffixes = [""]
    else:
        mid = (n + 1) // 2
        parts = [df.iloc[:mid], df.iloc[mid:]]
        suffixes = ["_part1", "_part2"]

    for part, suf in zip(parts, suffixes):
        fig = _grouped_hbar(part, id_col, title + suf.replace("_", " "), xlabel,
                            use_abs=use_abs)
        _save(fig, out_dir / f"{stem}{suf}.png")


# ══════════════════════════════════════════════════════════════════════════════
# Task 1 — Comparative Study
# ══════════════════════════════════════════════════════════════════════════════

def _t1(plot: bool) -> None:
    print("\n── Task 1: Comparative Study ──")
    task = "task1"
    base = OUTPUT_DIR / TASK_DIRS[task] / "fair-comparison"

    # Stage 1 — raw counts
    dst = _dst(task, "1-raw-counts")
    df = pd.read_csv(base / "1-raw-counts" / "tables" / "count_raw_cross_newspaper.csv")
    _emit(df, "feature_id", "Task 1 · Raw Event Counts", "count", dst, "count_raw",
          "Task 1: Raw event counts across newspapers",
          "t1_raw_counts", extra_cols=["level"], plot=plot)

    # Stage 2 — normalized
    dst = _dst(task, "2-normalized")
    df = pd.read_csv(base / "2-normalized" / "tables" / "rate_norm_cross_newspaper.csv")
    _emit(df, "feature_id", "Task 1 · Opportunity-Normalized Rate", "events / eligible site",
          dst, "rate_norm",
          "Task 1: Opportunity-normalized event rates",
          "t1_rate_norm", extra_cols=["level"], plot=plot)

    # Stage 3 — log
    dst = _dst(task, "3-log")
    df = pd.read_csv(base / "3-log" / "tables" / "log2_norm_cross_newspaper.csv")
    _emit(df, "feature_id", "Task 1 · Log₂-Normalized Rate", "log₂(rate)", dst, "log2_norm",
          r"Task 1: Log$_2$-normalized event rates",
          "t1_log2_norm", extra_cols=["level"], plot=plot)

    # Stage 4 — weighted (level + IDF)
    dst = _dst(task, "4-weighted")
    for col_stem, col_label, cap_suffix in [
        ("score_lvl", "level-weighted score", "level-weighted scores"),
        ("score_idf", "IDF-weighted score",   "IDF-weighted scores"),
    ]:
        f = base / "4-weighted" / "tables" / f"{col_stem}_cross_newspaper.csv"
        if not f.exists():
            continue
        df = pd.read_csv(f)
        _emit(df, "feature_id", f"Task 1 · {col_label.title()}", col_label,
              dst, col_stem,
              f"Task 1: {cap_suffix.capitalize()}",
              f"t1_{col_stem}", extra_cols=["level"], plot=plot)

    # Stage 5 — information-theoretic (JSD + PMI)
    dst = _dst(task, "5-information-theoretic")
    for col_stem, col_label, cap_suffix in [
        ("score_jsd", "JSD-weighted score",  "JSD-weighted scores"),
        ("score_pmi", "PMI-weighted score",  "PMI-weighted scores"),
    ]:
        f = base / "5-information-theoretic" / "tables" / f"{col_stem}_cross_newspaper.csv"
        if not f.exists():
            continue
        df = pd.read_csv(f)
        _emit(df, "feature_id", f"Task 1 · {col_label.title()}", col_label,
              dst, col_stem,
              f"Task 1: {cap_suffix.capitalize()}",
              f"t1_{col_stem}", extra_cols=["level"], plot=plot)


# ══════════════════════════════════════════════════════════════════════════════
# Task 2 — Transformation Study
# ══════════════════════════════════════════════════════════════════════════════

def _t2(plot: bool) -> None:
    print("\n── Task 2: Transformation Study ──")
    task = "task2"
    base = OUTPUT_DIR / TASK_DIRS[task] / "fair-comparison"

    # Stage 1 — raw rule frequencies
    dst = _dst(task, "1-raw-counts")
    df = pd.read_csv(base / "1-raw-counts" / "tables" / "total_freq_cross_newspaper.csv")
    _emit(df, "feature_id", "Task 2 · Raw Rule Frequencies", "total occurrences", dst, "total_freq",
          "Task 2: Raw morphological rule frequencies across newspapers",
          "t2_raw_freq", plot=plot)

    # Stage 2 — normalized
    dst = _dst(task, "2-normalized")
    f = base / "2-normalized" / "tables" / "rate_norm_cross_newspaper.csv"
    if f.exists():
        df = pd.read_csv(f)
        _emit(df, "feature_id", "Task 2 · Normalized Rule Rate", "rate (per eligible site)",
              dst, "rate_norm",
              "Task 2: Normalized morphological rule rates",
              "t2_rate_norm", plot=plot)

    # Stage 3 — log
    dst = _dst(task, "3-log")
    f = base / "3-log" / "tables" / "log2_norm_cross_newspaper.csv"
    if f.exists():
        df = pd.read_csv(f)
        _emit(df, "feature_id", "Task 2 · Log₂ Rule Rate", "log₂(rate)",
              dst, "log2_norm",
              r"Task 2: Log$_2$-normalized rule rates",
              "t2_log2_norm", plot=plot)

    # Stage 4 — confidence + coverage weighted
    dst = _dst(task, "4-weighted")
    for col_stem, col_label, cap_suffix in [
        ("score_conf", "confidence-weighted score", "confidence-weighted scores"),
        ("score_cov",  "coverage-weighted score",   "coverage-weighted scores"),
    ]:
        f = base / "4-weighted" / "tables" / f"{col_stem}_cross_newspaper.csv"
        if not f.exists():
            continue
        df = pd.read_csv(f)
        _emit(df, "feature_id", f"Task 2 · {col_label.title()}", col_label,
              dst, col_stem,
              f"Task 2: {cap_suffix.capitalize()}",
              f"t2_{col_stem}", plot=plot)

    # Stage 5 — rule entropy + entropy score
    dst = _dst(task, "5-information-theoretic")
    for col_stem, col_label, cap_suffix in [
        ("rule_entropy",  "rule entropy (bits)",  "rule entropy (bits per feature type)"),
        ("score_entropy", "entropy-weighted score", "entropy-weighted scores"),
    ]:
        f = base / "5-information-theoretic" / "tables" / f"{col_stem}_cross_newspaper.csv"
        if not f.exists():
            continue
        df = pd.read_csv(f)
        _emit(df, "feature_id", f"Task 2 · {col_label.title()}", col_label,
              dst, col_stem,
              f"Task 2: {cap_suffix.capitalize()}",
              f"t2_{col_stem}", plot=plot)


# ══════════════════════════════════════════════════════════════════════════════
# Task 3 — Complexity & Similarity Study
# ══════════════════════════════════════════════════════════════════════════════

def _t3_label(df: pd.DataFrame) -> pd.DataFrame:
    """Add a human-readable feature_id column for Task 3 data."""
    if "metric" in df.columns:
        df = df.copy()
        df["feature_id"] = df["sublevel_id"].str.split("/").str[-1] + " (" + df["metric"] + ")"
    elif "sublevel_id" in df.columns:
        df = df.copy()
        df["feature_id"] = df["sublevel_id"].str.split("/").str[-1]
    return df


def _t3(plot: bool) -> None:
    print("\n── Task 3: Complexity & Similarity Study ──")
    task = "task3"
    base = OUTPUT_DIR / TASK_DIRS[task] / "fair-comparison"

    # Stage 1 — raw complexity metrics (canonical + headline)
    dst = _dst(task, "1-raw-counts")
    for stem, register, cap in [
        ("raw_canonical_cross_newspaper", "Canonical", "canonical register"),
        ("raw_headline_cross_newspaper",  "Headline",  "headline register"),
    ]:
        f = base / "1-raw-counts" / "tables" / f"{stem}.csv"
        if not f.exists():
            continue
        df = _t3_label(pd.read_csv(f))
        id_col = "feature_id"
        extra = ["level"] if "level" in df.columns else []
        out_stem = stem.replace("_cross_newspaper", "")
        _emit(df, id_col, f"Task 3 · Raw Complexity Metrics ({register})",
              "metric value", dst, out_stem,
              f"Task 3: Raw complexity metrics — {register.lower()} register",
              f"t3_raw_{register.lower()}", extra_cols=extra, plot=plot)

    # Stage 2 — canonical/headline ratio
    dst = _dst(task, "2-normalized")
    f = base / "2-normalized" / "tables" / "ratio_cross_newspaper.csv"
    if f.exists():
        df = _t3_label(pd.read_csv(f))
        extra = ["level"] if "level" in df.columns else []
        _emit(df, "feature_id", "Task 3 · Canonical / Headline Ratio", "ratio",
              dst, "ratio",
              "Task 3: Canonical-to-headline complexity ratio",
              "t3_ratio", extra_cols=extra, plot=plot)

    # Stage 3 — log₂ ratio
    dst = _dst(task, "3-log")
    f = base / "3-log" / "tables" / "log2_ratio_cross_newspaper.csv"
    if f.exists():
        df = _t3_label(pd.read_csv(f))
        extra = ["level"] if "level" in df.columns else []
        _emit(df, "feature_id", "Task 3 · Log₂ Complexity Ratio", "log₂(ratio) (bits advantage)",
              dst, "log2_ratio",
              r"Task 3: Log$_2$ complexity ratio (bits advantage of canonical over headline)",
              "t3_log2_ratio", extra_cols=extra, plot=plot)

    # Stage 4 — level-weighted
    dst = _dst(task, "4-weighted")
    f = base / "4-weighted" / "tables" / "level_weighted_cross_newspaper.csv"
    if f.exists():
        df = _t3_label(pd.read_csv(f))
        extra = ["level"] if "level" in df.columns else []
        _emit(df, "feature_id", "Task 3 · Level-Weighted Complexity Ratio",
              "level-weighted log₂(ratio)", dst, "level_weighted",
              "Task 3: Level-weighted log$_2$ complexity ratio",
              "t3_level_weighted", extra_cols=extra, plot=plot)

    # Stage 5 — JSD
    dst = _dst(task, "5-information-theoretic")
    f = base / "5-information-theoretic" / "tables" / "jsd_cross_newspaper.csv"
    if f.exists():
        df = _t3_label(pd.read_csv(f))
        # Drop rows that are all-NaN across NP cols
        np_present = [c for c in NP_COLS if c in df.columns]
        df = df.dropna(subset=np_present, how="all").reset_index(drop=True)
        extra = ["level"] if "level" in df.columns else []
        _emit(df, "feature_id", "Task 3 · JSD (canonical vs headline)",
              "Jensen-Shannon divergence", dst, "jsd",
              "Task 3: Jensen-Shannon divergence between canonical and headline distributions",
              "t3_jsd", extra_cols=extra, plot=plot)

    # Stage 5 — bidirectional metrics (per-NP only, need to pivot)
    _t3_bidirectional(base, dst, plot)


def _t3_bidirectional(base: Path, dst: Path, plot: bool) -> None:
    """Load per-NP bidirectional metrics CSVs and produce a cross-NP combined view."""
    nps = {"HT": "Hindustan-Times", "TH": "The-Hindu", "ToI": "Times-of-India"}
    np_files = {
        "HT":  base / "5-information-theoretic" / "tables" / "bidirectional_metrics_Hindustan-Times.csv",
        "TH":  base / "5-information-theoretic" / "tables" / "bidirectional_metrics_The-Hindu.csv",
        "ToI": base / "5-information-theoretic" / "tables" / "bidirectional_metrics_Times-of-India.csv",
    }
    dfs = {}
    for short, f in np_files.items():
        if f.exists():
            dfs[short] = pd.read_csv(f)

    if not dfs:
        return

    # Pivot: for each metric, show HT/TH/ToI values side by side
    # Expected columns: metric (or similar label), value
    sample = next(iter(dfs.values()))
    id_col = "metric" if "metric" in sample.columns else sample.columns[0]

    all_ids = []
    for df in dfs.values():
        all_ids.extend(df[id_col].dropna().tolist())
    all_ids = list(dict.fromkeys(all_ids))  # unique, preserve order

    val_col = [c for c in sample.columns if c not in [id_col, "level"]]
    val_col = val_col[0] if val_col else None
    if val_col is None:
        return

    rows = []
    for mid in all_ids:
        row = {id_col: mid}
        for short, df in dfs.items():
            match = df[df[id_col] == mid]
            row[short] = match[val_col].iloc[0] if not match.empty else float("nan")
        rows.append(row)
    combined = pd.DataFrame(rows)
    combined.rename(columns={id_col: "feature_id"}, inplace=True)

    _emit(combined, "feature_id", "Task 3 · Bidirectional Similarity Metrics",
          "metric value", dst, "bidirectional_metrics",
          "Task 3: Cross-newspaper bidirectional similarity metrics",
          "t3_bidirectional", plot=plot)


# ══════════════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Generate cross-newspaper minimal fair-comparison output"
    )
    parser.add_argument("--no-plots", action="store_true",
                        help="Skip figure generation; CSV/LaTeX only.")
    args = parser.parse_args()
    plot = not args.no_plots

    print(f"Output → {MINIMAL_DIR.relative_to(BASE_DIR)}/")
    _t1(plot)
    _t2(plot)
    _t3(plot)

    total_files = sum(1 for _ in MINIMAL_DIR.rglob("*") if _.is_file())
    print(f"\nDone. {total_files} files written under output-minimal/fair-comparison/")


if __name__ == "__main__":
    main()
