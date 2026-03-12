"""
generate_fair_comparison_outputs.py
====================================
Creates per-task, per-stage tables and figures from pipeline outputs.

Output structure (inside each task's fair-comparison/ folder):
  task-{N}-{name}/
  ├── global/
  │   ├── 1-raw-counts/        single bar chart, mean across all 3 NPs; level-colored
  │   ├── 2-normalized/
  │   ├── 3-log/
  │   ├── 4-weighted/
  │   └── 5-information-theoretic/
  ├── cross-newspaper/
  │   ├── 1-raw-counts/        grouped bar chart, all 3 NPs in ONE figure (color by NP)
  │   ├── 2-normalized/
  │   ├── 3-log/
  │   ├── 4-weighted/
  │   └── 5-information-theoretic/
  └── per-newspaper/
      ├── Hindustan-Times/
      │   ├── 1-raw-counts/    single bar chart for this NP only; level-colored
      │   ├── 2-normalized/
      │   └── ...
      ├── The-Hindu/
      └── Times-of-India/

Stage subdirectories meaning:
  1-raw-counts/              original event / rule / metric counts
  2-normalized/              per-opportunity or per-baseline rates
  3-log/                     log₂ of normalized values
  4-weighted/                log₂ × structural / confidence weights
  5-information-theoretic/   log₂ × data-driven weights (JSD, PMI, entropy)

Tasks covered:
  Task 1 — Comparative Study          source: events_fair.csv
  Task 2 — Transformation Study       source: morphological_rules.csv
  Task 3 — Complexity & Similarity    source: complexity_summary.csv +
                                               bidirectional_metrics.csv

Usage:
    python generate_fair_comparison_outputs.py
    python generate_fair_comparison_outputs.py --no-plots
    python generate_fair_comparison_outputs.py --tasks 1 2
"""

import argparse
import sys
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from scipy.stats import entropy as scipy_entropy

sys.path.insert(0, os.path.dirname(__file__))
from config import BASE_DIR
from paths_config import NEWSPAPERS

# ── output roots ────────────────────────────────────────────────────────────
T1_DIR = BASE_DIR / "output" / "task-1-comparative-study"
T2_DIR = BASE_DIR / "output" / "task-2-transformation-study"
T3_DIR = BASE_DIR / "output" / "task-3-complexity-similarity-study"

STAGE_NAMES = {
    1: "1-raw-counts",
    2: "2-normalized",
    3: "3-log",
    4: "4-weighted",
    5: "5-information-theoretic",
}

# ── visual constants ─────────────────────────────────────────────────────────
LEVEL_COLORS = {
    "morphological": "#7B1FA2",
    "lexical":       "#1976D2",
    "punctuation":   "#0097A7",
    "dependency":    "#E65100",
    "syntactic":     "#E65100",
    "constituency":  "#E53935",
    "typological":   "#558B2F",
    "structural":    "#546E7A",
    "character":     "#00897B",
}
LEVEL_ORDER = [
    "morphological", "lexical", "punctuation",
    "dependency", "constituency", "typological", "structural",
]
NP_COLORS = {
    "Times-of-India":  "#1976D2",
    "Hindustan-Times": "#E53935",
    "The-Hindu":       "#2E7D32",
}
NP_SHORT = {
    "Times-of-India":  "ToI",
    "Hindustan-Times": "HT",
    "The-Hindu":       "TH",
}
REG_COLORS = {"canonical": "#1976D2", "headline": "#E65100"}

BAR_H    = 0.42
FS       = 7
FM       = 8.5
FT       = 9.5
DPI      = 150
EPSILON  = 1e-9
SPLIT_AT = 18     # features per figure before auto-splitting
VBAR_H   = 4.0    # fixed matplotlib height for vertical bar figures


# ═══════════════════════════════════════════════════════════════════════════
# ACL ARR figure-layout optimizer
# ═══════════════════════════════════════════════════════════════════════════

class ACLFigureOptimizer:
    """
    Recommends horizontal vs. vertical bar-chart orientation to minimise
    the space a figure occupies in an ACL ARR two-column A4 paper.

    ACL ARR A4 stylesheet geometry
    ───────────────────────────────
      \\columnwidth  = 3.33 in   (single-column figure)
      \\textwidth    = 6.97 in   (double-column / \\figure* figure)
      usable height ≈ 9.50 in per page

    Matplotlib figures are generated at "design" canvas widths (HBAR_W,
    CROSSH_W) and then \\includegraphics scales them to the paper column
    or text width.  The optimizer converts matplotlib figsize → displayed
    inches on the page to compare space in "column-inches"
    (height_in × col_span).
    """

    # Paper geometry (inches)
    COL_W  = 3.33
    TEXT_W = 6.97

    # Matplotlib "canvas" widths that match the generation functions
    HBAR_W   = 9.0    # _hbar figsize width
    CROSSH_W = 10.0   # _cross_np_grouped figsize width

    # Vertical-bar sizing (matplotlib units)
    VBAR_MPL_H  = VBAR_H      # fixed height for a vertical figure
    BAR_W_GRP   = 0.55        # matplotlib width per bar (per n_np group)
    VBAR_PAD_W  = 1.5         # left/right padding in a _vbar figure

    # Readability threshold: minimum displayed bar width (paper inches).
    # Computed as rendered_bar_mpl / canvas_mpl_w × display_w.
    MIN_BAR_W_IN  = 0.14      # ~10pt on paper — narrow but readable with colour

    @classmethod
    def _horiz_space(cls, n: int, n_np: int) -> float:
        """Estimated col-in for a horizontal figure (always single column)."""
        if n_np == 1:
            mpl_h = max(3.5, n * BAR_H + 1.5)
            mpl_w = cls.HBAR_W
        else:
            grp_h = BAR_H * n_np + 0.15
            mpl_h = max(4.0, n * grp_h + 1.5)
            mpl_w = cls.CROSSH_W
        return mpl_h / mpl_w * cls.COL_W   # single column → col_span=1

    @classmethod
    def _vert_space(cls, n: int, n_np: int) -> tuple:
        """
        Returns (col_in, col_span) for a vertical figure, or
        (inf, 2) if bars would be too narrow to read.

        Bar width is computed from the actual matplotlib canvas width that
        _vbar / _cross_np_vbar will produce (adapts to n and n_np).
        """
        mpl_w = max(
            cls.HBAR_W if n_np == 1 else cls.CROSSH_W,
            n * cls.BAR_W_GRP * n_np + cls.VBAR_PAD_W,
        )
        mpl_h = cls.VBAR_MPL_H

        # Actual bar width on paper = rendered_bar / canvas × display_width
        rendered_bar_mpl = cls.BAR_W_GRP * 0.85
        bar_w_single = rendered_bar_mpl / mpl_w * cls.COL_W
        bar_w_double = rendered_bar_mpl / mpl_w * cls.TEXT_W

        if bar_w_single >= cls.MIN_BAR_W_IN:
            disp_h = mpl_h / mpl_w * cls.COL_W
            return disp_h * 1, 1                    # single column
        elif bar_w_double >= cls.MIN_BAR_W_IN and n <= 20:
            disp_h = mpl_h / mpl_w * cls.TEXT_W
            return disp_h * 2, 2                    # double column
        else:
            return float("inf"), 2                  # unreadable

    @classmethod
    def analyze(cls, n: int, max_label_len: int, n_np: int = 1) -> dict:
        """
        Return a recommendation dict.

        Parameters
        ----------
        n             : number of bars / bar-groups
        max_label_len : longest label in characters
        n_np          : bars per group (1 = single NP, 3 = cross-NP)
        """
        horiz_col_in               = cls._horiz_space(n, n_np)
        vert_col_in, vert_span     = cls._vert_space(n, n_np)
        vert_readable              = vert_col_in < float("inf")

        if vert_readable and vert_col_in < horiz_col_in:
            rec     = "vertical"
            rec_span = vert_span
            saved   = (horiz_col_in - vert_col_in) / horiz_col_in * 100
        else:
            rec     = "horizontal"
            rec_span = 1
            saved   = 0.0

        return {
            "n_items":                 n,
            "n_np":                    n_np,
            "max_label_len":           max_label_len,
            "horiz_col_in":            round(horiz_col_in, 2),
            "vert_col_in":             round(vert_col_in, 2) if vert_readable else None,
            "vert_col_span":           vert_span,
            "vert_readable":           vert_readable,
            "recommended_orientation": rec,
            "recommended_col_span":    rec_span,
            "space_saved_pct":         round(saved, 1),
        }


# ═══════════════════════════════════════════════════════════════════════════
# Shared utilities
# ═══════════════════════════════════════════════════════════════════════════

def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"    fig  → {path.relative_to(BASE_DIR)}")


def _tbl(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"    tbl  → {path.relative_to(BASE_DIR)}")


def _tex(df: pd.DataFrame, path: Path, caption: str, label: str,
         id_col: str, extra_cols: list = None) -> None:
    """Write a booktabs LaTeX table."""
    extra_cols = extra_cols or []
    np_cols = [c for c in ["HT", "TH", "ToI"] if c in df.columns]
    NP_LABELS = {"HT": "Hindustan-Times", "TH": "The-Hindu", "ToI": "Times-of-India"}

    lines = [
        r"\begin{table}[htbp]",
        r"\small\centering",
        rf"\caption{{{caption}}}",
        rf"\label{{tab:{label}}}",
    ]
    all_cols = [id_col] + extra_cols + np_cols
    fmt_str = "l" * len([id_col] + extra_cols) + "r" * len(np_cols)
    lines.append(rf"\begin{{tabular}}{{{fmt_str}}}")
    lines.append(r"\toprule")

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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"    tex  → {path.relative_to(BASE_DIR)}")


def _level_legend(ax, keys=None):
    keys = keys or list(LEVEL_COLORS.keys())
    patches = [mpatches.Patch(color=LEVEL_COLORS[k], label=k.capitalize())
               for k in keys if k in LEVEL_COLORS]
    if patches:
        ax.legend(handles=patches, fontsize=FS, loc="lower right",
                  framealpha=0.7, ncol=2)


def _hbar(df: pd.DataFrame, col: str, title: str, xlabel: str,
          color_col: str = "level", use_abs: bool = False,
          newspaper: str = "") -> plt.Figure:
    """Generic level-coloured horizontal bar chart."""
    tmp = df.copy()
    tmp["_v"] = tmp[col].abs() if use_abs else tmp[col]
    tmp = tmp.dropna(subset=["_v"]).sort_values("_v", ascending=True)
    n = len(tmp)
    fig, ax = plt.subplots(figsize=(9, max(3.5, n * BAR_H + 1.5)))
    colors = [LEVEL_COLORS.get(str(r), "#999") for r in tmp[color_col]]
    bars   = ax.barh(tmp.iloc[:, 0], tmp["_v"], color=colors,
                     height=0.6, edgecolor="white", linewidth=0.4)
    for bar, v in zip(bars, tmp["_v"]):
        w = bar.get_width()
        ax.text(w + max(abs(w) * 0.02, 1e-9),
                bar.get_y() + bar.get_height() / 2,
                f"{v:.4g}", va="center", ha="left", fontsize=FS)
    suffix = f"  —  {newspaper}" if newspaper else ""
    ax.set_title(f"{title}{suffix}", fontsize=FT, pad=8)
    ax.set_xlabel(xlabel, fontsize=FM)
    ax.tick_params(axis="y", labelsize=FS)
    ax.tick_params(axis="x", labelsize=FS)
    ax.spines[["top", "right"]].set_visible(False)
    _level_legend(ax, tmp[color_col].unique().tolist())
    fig.tight_layout()
    return fig


def _cross_np_grouped(dfs: dict, col: str, label_col: str,
                      title: str, xlabel: str,
                      use_abs: bool = False) -> plt.Figure:
    """Grouped horizontal bar chart: one group per label, one bar per NP."""
    newspapers   = list(dfs.keys())
    all_labels   = sorted(set.union(*[set(df[label_col]) for df in dfs.values()]))
    mean_v = {}
    for lbl in all_labels:
        vals = []
        for df in dfs.values():
            row = df[df[label_col] == lbl]
            if not row.empty and col in row.columns:
                v = row[col].iloc[0]
                if pd.notna(v):
                    vals.append(abs(v) if use_abs else v)
        mean_v[lbl] = np.nanmean(vals) if vals else 0.0
    all_labels = sorted(all_labels, key=lambda l: mean_v[l])

    n_lbl  = len(all_labels)
    n_np   = len(newspapers)
    grp_h  = BAR_H * n_np + 0.15
    fig, ax = plt.subplots(figsize=(10, max(4.0, n_lbl * grp_h + 1.5)))
    y   = np.arange(n_lbl)
    off = np.linspace(-(n_np - 1) / 2, (n_np - 1) / 2, n_np) * BAR_H
    for i, (np_name, df) in enumerate(dfs.items()):
        vals = []
        for lbl in all_labels:
            row = df[df[label_col] == lbl]
            if not row.empty and col in row.columns and pd.notna(row[col].iloc[0]):
                v = row[col].iloc[0]
                vals.append(abs(v) if use_abs else v)
            else:
                vals.append(0.0)
        ax.barh(y + off[i], vals, height=BAR_H * 0.85,
                color=NP_COLORS.get(np_name, "#888"),
                label=np_name, edgecolor="white", linewidth=0.3)
    ax.set_yticks(y)
    ax.set_yticklabels(all_labels, fontsize=FS)
    ax.set_title(title, fontsize=FT, pad=8)
    ax.set_xlabel(xlabel, fontsize=FM)
    ax.tick_params(axis="x", labelsize=FS)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=FS, loc="lower right", framealpha=0.7)
    fig.tight_layout()
    return fig


def _vbar(df: pd.DataFrame, col: str, title: str, xlabel: str,
          color_col: str = "level", use_abs: bool = False,
          newspaper: str = "") -> plt.Figure:
    """
    Level-coloured vertical bar chart.
    Bars go upward; feature labels on X-axis (rotated 45°).
    Figure width adapts to n_items; height is fixed (VBAR_H).
    """
    tmp = df.copy()
    tmp["_v"] = tmp[col].abs() if use_abs else tmp[col]
    tmp = tmp.dropna(subset=["_v"]).sort_values("_v", ascending=False)
    labels = list(tmp.iloc[:, 0].astype(str))
    values = list(tmp["_v"])
    if color_col in tmp.columns:
        colors = [LEVEL_COLORS.get(str(r), "#999") for r in tmp[color_col]]
    else:
        colors = ["#546E7A"] * len(labels)

    n      = len(labels)
    fig_w  = max(ACLFigureOptimizer.HBAR_W, n * ACLFigureOptimizer.BAR_W_GRP + ACLFigureOptimizer.VBAR_PAD_W)
    fig, ax = plt.subplots(figsize=(fig_w, VBAR_H))
    x    = np.arange(n)
    bars = ax.bar(x, values, color=colors, width=0.6, edgecolor="white", linewidth=0.4)
    for bar, v in zip(bars, values):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2,
                h + max(abs(h) * 0.02, EPSILON),
                f"{v:.4g}", ha="center", va="bottom", fontsize=FS)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=FS)
    ax.set_ylabel(xlabel, fontsize=FM)
    suffix = f"  —  {newspaper}" if newspaper else ""
    ax.set_title(f"{title}{suffix}", fontsize=FT, pad=8)
    ax.tick_params(axis="y", labelsize=FS)
    ax.spines[["top", "right"]].set_visible(False)
    if color_col in tmp.columns:
        _level_legend(ax, tmp[color_col].unique().tolist())
    fig.tight_layout()
    return fig


def _cross_np_vbar(dfs: dict, col: str, label_col: str,
                   title: str, xlabel: str,
                   use_abs: bool = False) -> plt.Figure:
    """
    Grouped vertical bar chart: one group per label, one bar per NP.
    Wide and short — designed to minimise vertical space on the page.
    """
    newspapers = list(dfs.keys())
    all_labels = sorted(set.union(*[set(df[label_col]) for df in dfs.values()]))
    mean_v = {}
    for lbl in all_labels:
        vals = []
        for df in dfs.values():
            row = df[df[label_col] == lbl]
            if not row.empty and col in row.columns:
                v = row[col].iloc[0]
                if pd.notna(v):
                    vals.append(abs(v) if use_abs else v)
        mean_v[lbl] = np.nanmean(vals) if vals else 0.0
    all_labels = sorted(all_labels, key=lambda l: mean_v[l], reverse=True)

    n_lbl = len(all_labels)
    n_np  = len(newspapers)
    grp_w = ACLFigureOptimizer.BAR_W_GRP * n_np + 0.15
    fig_w = max(ACLFigureOptimizer.CROSSH_W,
                n_lbl * grp_w + ACLFigureOptimizer.VBAR_PAD_W)
    fig, ax = plt.subplots(figsize=(fig_w, VBAR_H))
    x   = np.arange(n_lbl)
    off = np.linspace(-(n_np - 1) / 2, (n_np - 1) / 2, n_np) * ACLFigureOptimizer.BAR_W_GRP

    for i, (np_name, df) in enumerate(dfs.items()):
        vals = []
        for lbl in all_labels:
            row = df[df[label_col] == lbl]
            if not row.empty and col in row.columns and pd.notna(row[col].iloc[0]):
                v = row[col].iloc[0]
                vals.append(abs(v) if use_abs else v)
            else:
                vals.append(0.0)
        ax.bar(x + off[i], vals, width=ACLFigureOptimizer.BAR_W_GRP * 0.85,
               color=NP_COLORS.get(np_name, "#888"),
               label=NP_SHORT.get(np_name, np_name),
               edgecolor="white", linewidth=0.3)

    ax.set_xticks(x)
    ax.set_xticklabels(all_labels, rotation=45, ha="right", fontsize=FS)
    ax.set_ylabel(xlabel, fontsize=FM)
    ax.set_title(title, fontsize=FT, pad=8)
    ax.tick_params(axis="y", labelsize=FS)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=FS, loc="upper right", framealpha=0.7)
    fig.tight_layout()
    return fig


def _wide_table(dfs: dict, col: str, label_col: str,
                extra_cols: list = None) -> pd.DataFrame:
    """Wide-format table: one row per label, one column per newspaper."""
    all_labels = sorted(set.union(*[set(df[label_col]) for df in dfs.values()]))
    extra_cols = extra_cols or []
    meta = {}
    for df in dfs.values():
        for _, row in df.iterrows():
            lbl = row[label_col]
            if lbl not in meta:
                meta[lbl] = {ec: row.get(ec, "") for ec in extra_cols}
    rows = []
    for lbl in all_labels:
        rec = {label_col: lbl}
        rec.update(meta.get(lbl, {}))
        for np_name, df in dfs.items():
            sub = df[df[label_col] == lbl]
            rec[NP_SHORT[np_name]] = (sub[col].iloc[0]
                                      if not sub.empty and col in sub.columns
                                      else np.nan)
        rows.append(rec)
    return pd.DataFrame(rows)


def _aggregate_mean(dfs: dict, col: str, label_col: str,
                    extra_cols: list = None) -> pd.DataFrame:
    """
    Return a single DataFrame with the mean value of `col` across all
    newspapers, one row per label.  Extra metadata columns (level, etc.)
    are taken from the first newspaper that has the label.
    """
    extra_cols = extra_cols or []
    all_labels = sorted(set.union(*[set(df[label_col]) for df in dfs.values()]))
    meta = {}
    for df in dfs.values():
        for _, row in df.iterrows():
            lbl = row[label_col]
            if lbl not in meta:
                meta[lbl] = {ec: row.get(ec, "") for ec in extra_cols}
    rows = []
    for lbl in all_labels:
        vals = []
        for df in dfs.values():
            sub = df[df[label_col] == lbl]
            if not sub.empty and col in sub.columns and pd.notna(sub[col].iloc[0]):
                vals.append(sub[col].iloc[0])
        if vals:
            rec = {label_col: lbl, col: float(np.nanmean(vals))}
            rec.update(meta.get(lbl, {}))
            rows.append(rec)
    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════════════════════
# Core emit helper — writes global/, cross-newspaper/, per-newspaper/{NP}/
# ═══════════════════════════════════════════════════════════════════════════

def _emit_stage(dfs: dict, label_col: str, col: str,
                title: str, xlabel: str,
                stage_dir: Path,
                use_abs: bool,
                plot: bool,
                extra_cols: list = None,
                with_latex: bool = False,
                color_col: str = "level",
                stem: str = None) -> None:
    """
    Write per-newspaper, cross-newspaper and global outputs for one metric.

    ``stage_dir`` is a specific stage directory, e.g.
    ``task-1-comparative-study/fair-comparison/1-raw-counts/``.

    ``stem`` overrides the filename stem (defaults to ``col``).

    Writes:
      stage_dir/per-newspaper/{NP}/{stem}.{png,csv}
      stage_dir/cross-newspaper/{stem}.{png,csv}  (+ .tex if with_latex)
      stage_dir/global/{stem}.{png,csv}           (+ .tex if with_latex)

    For cross-newspaper/: grouped bar chart (all NPs in one figure), wide CSV.
    For global/:          _hbar() with mean values, level-colored.
    For per-newspaper/:   _hbar() for that NP only.

    Long feature lists (> SPLIT_AT) are auto-split into _part1/_part2 figures.
    """
    extra_cols = extra_cols or []
    fstem = stem or col  # filename stem

    # Rename label_col → "feature_id" in all dfs once, up-front
    dfs_fid = {}
    for np_name, df in dfs.items():
        tmp = df.copy()
        if label_col != "feature_id":
            tmp = tmp.rename(columns={label_col: "feature_id"})
        dfs_fid[np_name] = tmp

    # ── per-newspaper ──────────────────────────────────────────────────────
    for np_name, df in dfs_fid.items():
        np_dir = stage_dir / "per-newspaper" / np_name
        np_dir.mkdir(parents=True, exist_ok=True)

        # CSV
        keep_cols = ["feature_id"] + [c for c in extra_cols if c in df.columns]
        if col in df.columns:
            keep_cols.append(col)
        tbl = df[list(dict.fromkeys(keep_cols))].copy()
        _tbl(tbl, np_dir / f"{fstem}.csv")

        # figure
        if plot and col in df.columns:
            tmp_lc = color_col if color_col in df.columns else "level"
            if tmp_lc not in df.columns:
                df = df.copy()
                df["level"] = "morphological"
                tmp_lc = "level"
            _save_split(df, col, title, xlabel, np_dir, fstem,
                        use_abs=use_abs, newspaper=np_name,
                        color_col=tmp_lc)

    # ── cross-newspaper ───────────────────────────────────────────────────
    if not dfs_fid:
        return
    cn_dir = stage_dir / "cross-newspaper"
    cn_dir.mkdir(parents=True, exist_ok=True)

    wide = _wide_table(dfs_fid, col, "feature_id", extra_cols)
    _tbl(wide, cn_dir / f"{fstem}.csv")
    if with_latex:
        _tex(wide, cn_dir / f"{fstem}.tex",
             caption=f"{title} — cross-newspaper comparison",
             label=f"cn_{fstem}",
             id_col="feature_id",
             extra_cols=[c for c in extra_cols if c in wide.columns])
    if plot and len(dfs_fid) > 1:
        _save_split_cross(dfs_fid, col, "feature_id",
                          title + " — All Newspapers", xlabel,
                          cn_dir, fstem, use_abs=use_abs)

    # ── global (mean across NPs) ──────────────────────────────────────────
    gl_dir = stage_dir / "global"
    gl_dir.mkdir(parents=True, exist_ok=True)

    agg = _aggregate_mean(dfs_fid, col, "feature_id", extra_cols)
    if agg.empty:
        return
    _tbl(agg, gl_dir / f"{fstem}.csv")
    if with_latex:
        _tex(agg, gl_dir / f"{fstem}.tex",
             caption=f"{title} — global mean",
             label=f"gl_{fstem}",
             id_col="feature_id",
             extra_cols=[c for c in extra_cols if c in agg.columns])
    if plot and color_col in agg.columns:
        _save_split(agg, col, title + " (mean · all newspapers)", xlabel,
                    gl_dir, fstem, use_abs=use_abs, newspaper="",
                    color_col=color_col)
    elif plot:
        # fallback: assign a synthetic level for colour coding
        tmp = agg.copy()
        tmp["level"] = "morphological"
        _save_split(tmp, col, title + " (mean · all newspapers)", xlabel,
                    gl_dir, fstem, use_abs=use_abs, newspaper="",
                    color_col="level")


def _emit_per_level_figures(dfs: dict, col: str, title_prefix: str,
                            xlabel: str, stage_dir: Path,
                            use_abs: bool, plot: bool,
                            with_latex: bool = False) -> None:
    """
    For each linguistic level, emit a focused figure/table containing only
    the features at that level.  Outputs are written into the same
    global/, cross-newspaper/, per-newspaper/ directories as the main
    figures but with file stems like ``{col}_{level}``.
    """
    for lv in LEVEL_ORDER:
        sub_dfs = {}
        for np_name, df in dfs.items():
            if "level" in df.columns:
                filt = df[df["level"] == lv].copy()
                if not filt.empty and col in filt.columns:
                    sub_dfs[np_name] = filt
        if not sub_dfs:
            continue
        _emit_stage(sub_dfs, "feature_id", col,
                    f"{title_prefix}\n{lv.capitalize()} Features",
                    xlabel, stage_dir, use_abs, plot,
                    extra_cols=["level"], with_latex=with_latex,
                    stem=f"{col}_{lv}")


def _pick_fig(df: pd.DataFrame, col: str, title: str, xlabel: str,
              color_col: str, use_abs: bool, newspaper: str) -> plt.Figure:
    """
    Choose horizontal or vertical orientation via ACLFigureOptimizer,
    then render and return the figure.
    """
    labels  = df.iloc[:, 0].astype(str).tolist()
    max_lbl = max(len(l) for l in labels) if labels else 5
    rec     = ACLFigureOptimizer.analyze(len(labels), max_lbl, n_np=1)
    if rec["recommended_orientation"] == "vertical":
        return _vbar(df, col, title, xlabel, color_col, use_abs, newspaper)
    return _hbar(df, col, title, xlabel, color_col, use_abs, newspaper)


def _pick_fig_cross(dfs_fid: dict, col: str, label_col: str,
                    title: str, xlabel: str, use_abs: bool) -> plt.Figure:
    """
    Choose horizontal or vertical orientation for a cross-NP figure via
    ACLFigureOptimizer, then render and return the figure.
    """
    all_labels = sorted(set.union(*[set(df[label_col]) for df in dfs_fid.values()]))
    max_lbl    = max(len(str(l)) for l in all_labels) if all_labels else 5
    n_np       = len(dfs_fid)
    rec        = ACLFigureOptimizer.analyze(len(all_labels), max_lbl, n_np=n_np)
    if rec["recommended_orientation"] == "vertical":
        return _cross_np_vbar(dfs_fid, col, label_col, title, xlabel, use_abs)
    return _cross_np_grouped(dfs_fid, col, label_col, title, xlabel, use_abs)


def _save_split(df: pd.DataFrame, col: str, title: str, xlabel: str,
                out_dir: Path, stem: str,
                use_abs: bool = False, newspaper: str = "",
                color_col: str = "level") -> None:
    """
    Save bar figure, auto-splitting if > SPLIT_AT features.
    Orientation (horizontal vs vertical) is chosen per-part by
    ACLFigureOptimizer to minimise paper space.
    """
    n = len(df)
    if n <= SPLIT_AT:
        parts_data, suffixes = [df], [""]
    else:
        mid = (n + 1) // 2
        parts_data = [df.iloc[:mid], df.iloc[mid:]]
        suffixes   = ["_part1", "_part2"]
    for part, suf in zip(parts_data, suffixes):
        fig = _pick_fig(part, col, title + suf.replace("_", " "), xlabel,
                        color_col, use_abs, newspaper)
        _save(fig, out_dir / f"{stem}{suf}.png")


def _save_split_cross(dfs_fid: dict, col: str, label_col: str,
                      title: str, xlabel: str,
                      out_dir: Path, stem: str,
                      use_abs: bool = False) -> None:
    """
    Save cross-NP bar figure, auto-splitting if > SPLIT_AT features.
    Orientation chosen per-part by ACLFigureOptimizer.
    """
    all_labels = sorted(set.union(*[set(df[label_col]) for df in dfs_fid.values()]))
    n = len(all_labels)
    if n <= SPLIT_AT:
        parts, suffixes = [all_labels], [""]
    else:
        mid = (n + 1) // 2
        parts    = [all_labels[:mid], all_labels[mid:]]
        suffixes = ["_part1", "_part2"]
    for lbls, suf in zip(parts, suffixes):
        sub_dfs = {k: df[df[label_col].isin(lbls)] for k, df in dfs_fid.items()}
        part_title = title + suf.replace("_", " ")
        fig = _pick_fig_cross(sub_dfs, col, label_col, part_title, xlabel, use_abs)
        _save(fig, out_dir / f"{stem}{suf}.png")


# ═══════════════════════════════════════════════════════════════════════════
# TASK 1 — Comparative Study
# ═══════════════════════════════════════════════════════════════════════════

# ── Value-level breakdown configuration ──────────────────────────────────
VB_CONFIG = {
    "FEAT-CHG":        {"label": "mnemonic",           "top_n": None, "color": "morphological"},
    "DEP-REL-CHG":     {"label": "cv→hv",               "top_n": 25,   "color": "dependency"},
    "POS-CHG":         {"label": "cv→hv",               "top_n": None, "color": "lexical"},
    "FW-DEL":          {"label": "canonical_value",     "top_n": None, "color": "lexical"},
    "FW-ADD":          {"label": "headline_value",      "top_n": None, "color": "lexical"},
    "CLAUSE-TYPE-CHG": {"label": "cv→hv",               "top_n": 15,   "color": "constituency"},
    "CONST-ADD":       {"label": "headline_value",      "top_n": None, "color": "constituency"},
    "CONST-REM":       {"label": "canonical_value",     "top_n": None, "color": "constituency"},
    "C-DEL":           {"label": "canonical_value",     "top_n": None, "color": "lexical"},
    "C-ADD":           {"label": "headline_value",      "top_n": None, "color": "lexical"},
    # Punctuation — canonical_value/headline_value carry the punct symbol
    "PUNCT-DEL":       {"label": "canonical_value",     "top_n": None, "color": "punctuation"},
    "PUNCT-ADD":       {"label": "headline_value",      "top_n": None, "color": "punctuation"},
    "PUNCT-SUBST":     {"label": "cv→hv",               "top_n": None, "color": "punctuation"},
}


def _vb_build(newspapers: list, feature_id: str, cfg: dict) -> dict:
    """
    Load events_global.csv + events_fair.csv for each newspaper, compute
    value-level counts and all 5-stage normalizations for one feature_id.

    Returns a dict {np_name: DataFrame} where each DataFrame has columns:
      feature_id (the value label), level, count_raw, eligible_site_count,
      rate_norm, log2_norm, weight_lvl, score_lvl, weight_idf, score_idf,
      weight_jsd, score_jsd, weight_pmi, score_pmi, dist_entropy, score_entropy
    """
    label_mode = cfg["label"]
    top_n      = cfg["top_n"]
    level_str  = cfg["color"]

    # First pass: collect per-NP counts to determine top_n filter
    np_counts = {}
    for np_name in newspapers:
        events_p = (T1_DIR / "per-newspaper" / np_name / "events_global.csv")
        fair_p   = (T1_DIR / "per-newspaper" / np_name / "events_fair.csv")
        if not events_p.exists() or not fair_p.exists():
            continue

        events = pd.read_csv(events_p)
        fair   = pd.read_csv(fair_p)

        sub = events[events["feature_id"] == feature_id].copy()
        if sub.empty:
            np_counts[np_name] = pd.Series(dtype=int)
            continue

        # Compute label column
        if label_mode == "mnemonic":
            sub["_label"] = sub["mnemonic"].astype(str)
        elif label_mode == "cv→hv":
            sub["_label"] = (sub["canonical_value"].astype(str) + "→"
                             + sub["headline_value"].astype(str))
        elif label_mode == "canonical_value":
            sub["_label"] = sub["canonical_value"].astype(str)
        elif label_mode == "headline_value":
            sub["_label"] = sub["headline_value"].astype(str)
        else:
            sub["_label"] = sub["canonical_value"].astype(str)

        counts = sub["_label"].value_counts()
        np_counts[np_name] = counts

    if not np_counts:
        return {}

    # Determine top_n labels using sum across newspapers
    all_labels = set()
    for counts in np_counts.values():
        all_labels.update(counts.index.tolist())

    if top_n is not None and len(all_labels) > top_n:
        sum_counts = {}
        for lbl in all_labels:
            total = sum(int(c.get(lbl, 0)) for c in np_counts.values())
            sum_counts[lbl] = total
        keep_labels = set(sorted(sum_counts, key=lambda l: sum_counts[l],
                                 reverse=True)[:top_n])
    else:
        keep_labels = all_labels

    # Second pass: build per-NP DataFrames with full normalizations
    result = {}
    for np_name in newspapers:
        events_p = (T1_DIR / "per-newspaper" / np_name / "events_global.csv")
        fair_p   = (T1_DIR / "per-newspaper" / np_name / "events_fair.csv")
        if not events_p.exists() or not fair_p.exists():
            continue

        events = pd.read_csv(events_p)
        fair   = pd.read_csv(fair_p)

        # Get parent feature row from events_fair.csv
        parent = fair[fair["feature_id"] == feature_id]
        if parent.empty:
            continue
        parent = parent.iloc[0]
        eligible_site_count = float(parent.get("eligible_site_count", 1) or 1)
        weight_lvl = float(parent.get("weight_lvl", 1.0) or 1.0)
        weight_idf = float(parent.get("weight_idf", 1.0) or 1.0)
        weight_jsd = float(parent.get("weight_jsd", 0.0) or 0.0)
        weight_pmi = float(parent.get("weight_pmi", 0.0) or 0.0)

        sub = events[events["feature_id"] == feature_id].copy()
        if sub.empty:
            continue

        # Compute label column
        if label_mode == "mnemonic":
            sub["_label"] = sub["mnemonic"].astype(str)
        elif label_mode == "cv→hv":
            sub["_label"] = (sub["canonical_value"].astype(str) + "→"
                             + sub["headline_value"].astype(str))
        elif label_mode == "canonical_value":
            sub["_label"] = sub["canonical_value"].astype(str)
        elif label_mode == "headline_value":
            sub["_label"] = sub["headline_value"].astype(str)
        else:
            sub["_label"] = sub["canonical_value"].astype(str)

        counts = sub["_label"].value_counts()
        # Filter to keep_labels
        counts = counts[counts.index.isin(keep_labels)]
        if counts.empty:
            continue

        # Distribution entropy across value pairs for this feature
        total_n = counts.sum()
        probs   = counts.values / total_n if total_n > 0 else counts.values
        dist_entropy = float(scipy_entropy(probs, base=2)) if total_n > 0 else 0.0

        rows = []
        for lbl, cnt in counts.items():
            count_raw = int(cnt)
            rate_norm = count_raw / eligible_site_count
            log2_norm = np.log2(max(rate_norm, EPSILON))
            score_lvl   = log2_norm * weight_lvl
            score_idf   = log2_norm * weight_idf
            score_jsd   = log2_norm * weight_jsd
            score_pmi   = log2_norm * weight_pmi
            score_entropy = log2_norm * dist_entropy
            rows.append({
                "feature_id":          lbl,
                "level":               level_str,
                "count_raw":           count_raw,
                "eligible_site_count": eligible_site_count,
                "rate_norm":           rate_norm,
                "log2_norm":           log2_norm,
                "weight_lvl":          weight_lvl,
                "score_lvl":           score_lvl,
                "weight_idf":          weight_idf,
                "score_idf":           score_idf,
                "weight_jsd":          weight_jsd,
                "score_jsd":           score_jsd,
                "weight_pmi":          weight_pmi,
                "score_pmi":           score_pmi,
                "dist_entropy":        dist_entropy,
                "score_entropy":       score_entropy,
            })

        if rows:
            result[np_name] = pd.DataFrame(rows)

    return result


def run_task1_value_level(newspapers: list, plot: bool,
                          base_dir: Path,
                          with_latex: bool = False) -> None:
    """Add value-level fine-grained breakdowns for each feature in VB_CONFIG."""
    print("  Value-level breakdowns ...")
    for feature_id, cfg in VB_CONFIG.items():
        dfs = _vb_build(newspapers, feature_id, cfg)
        if not dfs:
            print(f"    [skip] {feature_id}: no data")
            continue

        # Stage 1 — raw counts
        stage_vl_dir = base_dir / STAGE_NAMES[1] / "value-level" / feature_id
        _emit_stage(dfs, "feature_id", "count_raw",
                    f"{feature_id} · Value Breakdown — Raw Counts",
                    "count", stage_vl_dir, False, plot,
                    extra_cols=["level"], with_latex=with_latex,
                    color_col="level")

        # Stage 2 — normalized rates
        stage_vl_dir = base_dir / STAGE_NAMES[2] / "value-level" / feature_id
        _emit_stage(dfs, "feature_id", "rate_norm",
                    f"{feature_id} · Value Breakdown — Normalized Rates",
                    "rate", stage_vl_dir, False, plot,
                    extra_cols=["level"], with_latex=with_latex,
                    color_col="level")

        # Stage 3 — log₂
        stage_vl_dir = base_dir / STAGE_NAMES[3] / "value-level" / feature_id
        _emit_stage(dfs, "feature_id", "log2_norm",
                    f"{feature_id} · Value Breakdown — Log₂ Normalized",
                    "log₂(rate)", stage_vl_dir, True, plot,
                    extra_cols=["level"], with_latex=with_latex,
                    color_col="level")

        # Stage 4a — level-weighted
        stage_vl_dir = base_dir / STAGE_NAMES[4] / "value-level" / feature_id
        _emit_stage(dfs, "feature_id", "score_lvl",
                    f"{feature_id} · Value Breakdown — Level-Weighted Score",
                    "|score_lvl|", stage_vl_dir, True, plot,
                    extra_cols=["level"], with_latex=with_latex,
                    color_col="level")

        # Stage 4b — IDF-weighted
        _emit_stage(dfs, "feature_id", "score_idf",
                    f"{feature_id} · Value Breakdown — IDF-Weighted Score",
                    "|score_idf|", stage_vl_dir, True, plot,
                    extra_cols=["level"], with_latex=with_latex,
                    color_col="level")

        # Stage 5a — JSD-weighted
        stage_vl_dir = base_dir / STAGE_NAMES[5] / "value-level" / feature_id
        _emit_stage(dfs, "feature_id", "score_jsd",
                    f"{feature_id} · Value Breakdown — JSD-Weighted Score",
                    "|score_jsd|", stage_vl_dir, True, plot,
                    extra_cols=["level"], with_latex=with_latex,
                    color_col="level")

        # Stage 5b — PMI-weighted
        _emit_stage(dfs, "feature_id", "score_pmi",
                    f"{feature_id} · Value Breakdown — PMI-Weighted Score",
                    "|score_pmi|", stage_vl_dir, True, plot,
                    extra_cols=["level"], with_latex=with_latex,
                    color_col="level")

        # Stage 5c — entropy-weighted (use_abs=False, reflects direction)
        _emit_stage(dfs, "feature_id", "score_entropy",
                    f"{feature_id} · Value Breakdown — Entropy-Weighted Score",
                    "score_entropy", stage_vl_dir, False, plot,
                    extra_cols=["level"], with_latex=with_latex,
                    color_col="level")


def _t1_load(newspapers: list) -> dict:
    dfs = {}
    for np_name in newspapers:
        p = T1_DIR / "per-newspaper" / np_name / "events_fair.csv"
        if p.exists():
            dfs[np_name] = pd.read_csv(p)
        else:
            print(f"  [skip] events_fair.csv not found for {np_name}")
    return dfs


def run_task1(newspapers: list, plot: bool,
              base_dir: Path = None,
              with_latex: bool = False) -> None:
    print("\n" + "=" * 60)
    print("  Task 1 — Comparative Study")
    print("=" * 60)
    dfs = _t1_load(newspapers)
    if not dfs:
        print("  [skip] no data found"); return
    base = base_dir if base_dir is not None else T1_DIR / "fair-comparison"

    # Stage 1 — raw counts
    print("  Stage 1 — raw counts")
    d = base / STAGE_NAMES[1]
    _emit_stage(dfs, "feature_id", "count_raw",
                "Raw Event Counts  (uncorrected)", "count_raw  (events)",
                d, False, plot, extra_cols=["level"], with_latex=with_latex)
    _emit_per_level_figures(dfs, "count_raw", "Raw Event Counts",
                            "count_raw  (events)", d, False, plot, with_latex)

    # Stage 2 — normalized rates
    print("  Stage 2 — normalized rates")
    d = base / STAGE_NAMES[2]
    _emit_stage(dfs, "feature_id", "rate_norm",
                "Opportunity-Normalized Event Rates",
                "rate_norm  (events / eligible sites)",
                d, False, plot, extra_cols=["level"], with_latex=with_latex)
    _emit_per_level_figures(dfs, "rate_norm", "Opportunity-Normalized Event Rates",
                            "rate_norm", d, False, plot, with_latex)

    # Stage 3 — log₂
    print("  Stage 3 — log₂ normalized rates")
    d = base / STAGE_NAMES[3]
    _emit_stage(dfs, "feature_id", "log2_norm",
                "Log₂ Normalized Rates  (|log₂(rate)|)",
                "|log₂(rate_norm)|",
                d, True, plot, extra_cols=["level"], with_latex=with_latex)
    _emit_per_level_figures(dfs, "log2_norm", "Log₂ Normalized Rates",
                            "|log₂(rate_norm)|", d, True, plot, with_latex)
    if plot:
        _save(_t1_level_contribution(dfs),
              d / "cross-newspaper" / "level_contribution.png")
        _save(_t1_level_contribution(dfs),
              d / "global" / "level_contribution.png")

    # Stage 4 — weighted (level + IDF)
    print("  Stage 4 — weighted (level + IDF)")
    d = base / STAGE_NAMES[4]
    for score_col, short_title, xl in [
        ("score_lvl", "Level-Weighted Score",
         "|score_lvl|  (|log₂(rate)·w_level|)"),
        ("score_idf", "IDF-Weighted Score",
         "|score_idf|  (|log₂(rate)·w_IDF|)"),
    ]:
        if score_col not in next(iter(dfs.values())).columns:
            continue
        _emit_stage(dfs, "feature_id", score_col, short_title, xl,
                    d, True, plot, extra_cols=["level"], with_latex=with_latex)
        _emit_per_level_figures(dfs, score_col, short_title, xl,
                                d, True, plot, with_latex)
    if plot and len(dfs) > 1:
        _save(_t1_method_comparison(dfs, ["score_lvl", "score_idf"],
                                    ["Level", "IDF"]),
              d / "cross-newspaper" / "level_vs_idf.png")

    # Stage 5 — information-theoretic (JSD + PMI)
    print("  Stage 5 — information-theoretic (JSD + PMI)")
    d = base / STAGE_NAMES[5]
    first_df = next(iter(dfs.values()))
    for score_col, short_title, xl in [
        ("score_jsd", "JSD-Weighted Score",
         "|score_jsd|  (|log₂(rate)·JSD|)"),
        ("score_pmi", "PMI-Weighted Score",
         "|score_pmi|  (|log₂(rate)·PMI|)"),
    ]:
        if score_col not in first_df.columns:
            continue
        _emit_stage(dfs, "feature_id", score_col, short_title, xl,
                    d, True, plot, extra_cols=["level"], with_latex=with_latex)
        _emit_per_level_figures(dfs, score_col, short_title, xl,
                                d, True, plot, with_latex)
    if plot:
        for np_name, df in dfs.items():
            _save(_t1_all_methods_heatmap(df, np_name),
                  d / "per-newspaper" / np_name / "all_methods_heatmap.png")
        if len(dfs) > 1:
            _save(_t1_all_methods_panel(dfs),
                  d / "cross-newspaper" / "all_methods_panel.png")

    # Value-level fine-grained breakdowns
    print("  Value-level breakdowns")
    run_task1_value_level(newspapers, plot, base, with_latex=with_latex)


def _t1_level_contribution(dfs: dict) -> plt.Figure:
    records = []
    for np_name, df in dfs.items():
        for lv in LEVEL_ORDER:
            sub   = df[df["level"] == lv]
            total = sub["log2_norm"].abs().sum() if "log2_norm" in sub.columns else 0.0
            records.append({"newspaper": np_name, "level": lv, "abs_log2": total})
    rec_df = pd.DataFrame(records)
    newspapers = list(dfs.keys())
    fig, ax = plt.subplots(figsize=(9, 3.5))
    bottoms = np.zeros(len(newspapers))
    for lv in LEVEL_ORDER:
        vals = []
        for np_name in newspapers:
            row = rec_df[(rec_df["newspaper"] == np_name) & (rec_df["level"] == lv)]
            vals.append(row["abs_log2"].iloc[0] if not row.empty else 0.0)
        ax.barh(newspapers, vals, left=bottoms,
                color=LEVEL_COLORS.get(lv, "#999"),
                label=lv.capitalize(), edgecolor="white", linewidth=0.4)
        bottoms += np.array(vals)
    ax.set_title("Level Contribution to Total |log₂ Normalized Rate|",
                 fontsize=FT, pad=8)
    ax.set_xlabel("Sum of |log₂(rate_norm)| per level", fontsize=FM)
    ax.tick_params(labelsize=FS)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=FS, loc="lower right", framealpha=0.7, ncol=2)
    fig.tight_layout()
    return fig


def _t1_method_comparison(dfs: dict, cols: list, labels: list) -> plt.Figure:
    """Cross-NP comparison of multiple weighting methods in one panel."""
    n_methods = len(cols)
    newspapers = list(dfs.keys())
    all_feat   = sorted(set.union(*[set(df["feature_id"]) for df in dfs.values()]))
    sort_col   = cols[0]
    mean_v = {f: np.nanmean([abs(df[df["feature_id"] == f][sort_col].iloc[0])
                              for df in dfs.values()
                              if not df[df["feature_id"] == f].empty
                              and sort_col in df.columns])
              for f in all_feat}
    all_feat = sorted(all_feat, key=lambda f: mean_v.get(f, 0))
    method_colors = ["#7B1FA2", "#1976D2", "#E65100", "#2E7D32"]
    n_feat  = len(all_feat)
    n_np    = len(newspapers)
    n_bars  = n_methods * n_np
    grp_h   = BAR_H * n_bars + 0.2
    fig, ax = plt.subplots(figsize=(10, max(4.0, n_feat * grp_h + 1.5)))
    y       = np.arange(n_feat)
    width   = BAR_H * 0.85
    half    = (n_bars - 1) / 2
    slot    = 0
    for mi, (col, lbl) in enumerate(zip(cols, labels)):
        for ni, (np_name, df) in enumerate(dfs.items()):
            vals = []
            for f in all_feat:
                row = df[df["feature_id"] == f]
                v = row[col].iloc[0] if not row.empty and col in row.columns else 0.0
                vals.append(abs(v) if pd.notna(v) else 0.0)
            off   = (slot - half) * BAR_H
            color = method_colors[mi % len(method_colors)]
            alpha = 0.9 - ni * 0.25
            ax.barh(y + off, vals, height=width,
                    color=color, alpha=alpha,
                    label=f"{lbl} · {NP_SHORT[np_name]}",
                    edgecolor="white", linewidth=0.3)
            slot += 1
    ax.set_yticks(y)
    ax.set_yticklabels(all_feat, fontsize=FS)
    ax.set_title("Weighting Method Comparison — All Newspapers", fontsize=FT, pad=8)
    ax.set_xlabel("|score|", fontsize=FM)
    ax.tick_params(axis="x", labelsize=FS)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=FS, loc="lower right", framealpha=0.7, ncol=2)
    fig.tight_layout()
    return fig


def _t1_all_methods_heatmap(df: pd.DataFrame, newspaper: str) -> plt.Figure:
    """Heatmap: features × weighting methods, cell = |score| (column-normalised)."""
    method_cols = {c: c.replace("score_", "").upper()
                   for c in ["score_lvl", "score_idf", "score_jsd", "score_pmi"]
                   if c in df.columns}
    if not method_cols:
        return plt.figure()
    tmp = df[["feature_id", "level"] + list(method_cols.keys())].copy()
    tmp["_mean"] = tmp[list(method_cols.keys())].abs().mean(axis=1)
    tmp = tmp.sort_values("_mean", ascending=False)
    features  = tmp["feature_id"].tolist()
    n_feat    = len(features)
    n_meth    = len(method_cols)
    mat_raw   = tmp[list(method_cols.keys())].abs().fillna(0).values
    mat_norm  = mat_raw.copy().astype(float)
    for j in range(n_meth):
        mx = mat_norm[:, j].max()
        if mx > 0:
            mat_norm[:, j] /= mx
    fig, ax = plt.subplots(figsize=(5, max(4.0, n_feat * 0.32 + 1.5)))
    im = ax.imshow(mat_norm, aspect="auto", cmap="YlOrRd",
                   vmin=0, vmax=1, origin="upper")
    ax.set_xticks(range(n_meth))
    ax.set_xticklabels(list(method_cols.values()), fontsize=FM)
    ax.set_yticks(range(n_feat))
    ax.set_yticklabels(features, fontsize=FS)
    for i in range(n_feat):
        for j in range(n_meth):
            v = mat_raw[i, j]
            if v > 0:
                ax.text(j, i, f"{v:.3f}", ha="center", va="center",
                        fontsize=5.5,
                        color="white" if mat_norm[i, j] > 0.65 else "black")
    plt.colorbar(im, ax=ax, label="Normalised |score|", shrink=0.5, pad=0.01)
    ax.set_title(f"All Weighting Methods — {newspaper}", fontsize=FT, pad=8)
    fig.tight_layout()
    return fig


def _t1_all_methods_panel(dfs: dict) -> plt.Figure:
    """2×2 panel: one subplot per weighting method, grouped NP bars."""
    entries = [("score_lvl", "Level-Weighted",  "|score_lvl|"),
               ("score_idf", "IDF-Weighted",    "|score_idf|"),
               ("score_jsd", "JSD-Weighted",    "|score_jsd|"),
               ("score_pmi", "PMI-Weighted",    "|score_pmi|")]
    avail = [(c, l, xl) for c, l, xl in entries
             if any(c in df.columns for df in dfs.values())]
    n_m   = len(avail)
    ncols = 2
    nrows = (n_m + 1) // 2
    newspapers   = list(dfs.keys())
    all_feat     = sorted(set.union(*[set(df["feature_id"]) for df in dfs.values()]))
    sort_col     = avail[0][0] if avail else "score_lvl"
    mean_v = {f: np.nanmean([abs(df[df["feature_id"] == f][sort_col].iloc[0])
                              for df in dfs.values()
                              if not df[df["feature_id"] == f].empty
                              and sort_col in df.columns])
              for f in all_feat}
    all_feat = sorted(all_feat, key=lambda f: mean_v.get(f, 0))
    n_feat = len(all_feat)
    n_np   = len(newspapers)
    grp_h  = BAR_H * n_np + 0.12
    fig_h  = max(4.0, n_feat * grp_h + 1.5)
    fig, axes = plt.subplots(nrows, ncols,
                             figsize=(9 * ncols, fig_h), sharey=True)
    axes = axes.flatten()
    y   = np.arange(n_feat)
    off = np.linspace(-(n_np - 1) / 2, (n_np - 1) / 2, n_np) * BAR_H
    for idx, (col, lbl, xl) in enumerate(avail):
        ax = axes[idx]
        for i, (np_name, df) in enumerate(dfs.items()):
            vals = []
            for f in all_feat:
                row = df[df["feature_id"] == f]
                v = row[col].iloc[0] if not row.empty and col in row.columns else 0.0
                vals.append(abs(v) if pd.notna(v) else 0.0)
            ax.barh(y + off[i], vals, height=BAR_H * 0.85,
                    color=NP_COLORS.get(np_name, "#888"),
                    label=np_name, edgecolor="white", linewidth=0.3)
        ax.set_yticks(y)
        ax.set_yticklabels(all_feat, fontsize=FS)
        ax.set_title(f"{lbl}", fontsize=FM, pad=5)
        ax.set_xlabel(xl, fontsize=FS)
        ax.tick_params(axis="x", labelsize=FS)
        ax.spines[["top", "right"]].set_visible(False)
        if idx == 0:
            ax.legend(fontsize=FS, loc="lower right", framealpha=0.7)
    for j in range(len(avail), len(axes)):
        axes[j].set_visible(False)
    fig.suptitle("All Weighting Methods — Cross-Newspaper Comparison",
                 fontsize=FT, y=1.01)
    fig.tight_layout()
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# TASK 2 — Transformation Study
# ═══════════════════════════════════════════════════════════════════════════

def _t2_load(newspapers: list) -> dict:
    dfs = {}
    for np_name in newspapers:
        p = (T2_DIR / "per-newspaper" / np_name
             / "morphological-rules" / "morphological_rules.csv")
        if p.exists():
            dfs[np_name] = pd.read_csv(p)
        else:
            print(f"  [skip] morphological_rules.csv not found for {np_name}")
    return dfs


def _t2_aggregate(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate morphological rules by feature; add derived columns."""
    grp = df.groupby("feature").agg(
        total_freq=("frequency", "sum"),
        n_rules=("frequency", "count"),
        avg_confidence=("confidence", "mean"),
        avg_coverage=("coverage", "mean"),
    ).reset_index()
    total_all   = grp["total_freq"].sum()
    grp["rate_norm"]  = grp["total_freq"] / max(total_all, EPSILON)
    grp["log2_norm"]  = np.log2(grp["rate_norm"].clip(lower=EPSILON))
    grp["score_conf"] = grp["log2_norm"] * grp["avg_confidence"]
    grp["score_cov"]  = grp["log2_norm"] * grp["avg_coverage"] / 100.0
    # Rule distribution entropy per feature (info-theoretic)
    ent_map = {}
    for feat, sub in df.groupby("feature"):
        freqs = sub["frequency"].values.astype(float)
        if freqs.sum() > 0:
            p = freqs / freqs.sum()
            ent_map[feat] = float(scipy_entropy(p, base=2))
        else:
            ent_map[feat] = 0.0
    grp["rule_entropy"]  = grp["feature"].map(ent_map)
    grp["score_entropy"] = grp["log2_norm"] * grp["rule_entropy"]
    return grp


def run_task2(newspapers: list, plot: bool,
              base_dir: Path = None,
              with_latex: bool = False) -> None:
    print("\n" + "=" * 60)
    print("  Task 2 — Transformation Study")
    print("=" * 60)
    raw_dfs  = _t2_load(newspapers)
    if not raw_dfs:
        print("  [skip] no data found"); return
    agg_dfs  = {np_name: _t2_aggregate(df) for np_name, df in raw_dfs.items()}
    base     = base_dir if base_dir is not None else T2_DIR / "fair-comparison"

    # Rename "feature" → "feature_id" for consistency with _emit_stage
    fid_dfs = {k: v.rename(columns={"feature": "feature_id"}).assign(level="morphological")
               for k, v in agg_dfs.items()}

    print("  Stage 1 — raw rule frequencies")
    _emit_stage(fid_dfs, "feature_id", "total_freq",
                "Morphological Rule Frequencies", "total_freq  (occurrences)",
                base / STAGE_NAMES[1], False, plot,
                extra_cols=[], with_latex=with_latex,
                color_col="level")

    print("  Stage 2 — normalized rates")
    _emit_stage(fid_dfs, "feature_id", "rate_norm",
                "Normalised Rule Rates  (share of total morph events)",
                "rate_norm",
                base / STAGE_NAMES[2], False, plot,
                extra_cols=[], with_latex=with_latex,
                color_col="level")

    print("  Stage 3 — log₂ rates")
    _emit_stage(fid_dfs, "feature_id", "log2_norm",
                "Log₂ Normalised Rule Rates",
                "|log₂(rate_norm)|",
                base / STAGE_NAMES[3], True, plot,
                extra_cols=[], with_latex=with_latex,
                color_col="level")

    print("  Stage 4 — confidence-weighted")
    _emit_stage(fid_dfs, "feature_id", "score_conf",
                "Confidence-Weighted Log₂ Rate  (|log₂ × avg_confidence|)",
                "|score_conf|",
                base / STAGE_NAMES[4], True, plot,
                extra_cols=[], with_latex=with_latex,
                color_col="level")
    _emit_stage(fid_dfs, "feature_id", "score_cov",
                "Coverage-Weighted Log₂ Rate  (|log₂ × avg_coverage|)",
                "|score_cov|",
                base / STAGE_NAMES[4], True, plot,
                extra_cols=[], with_latex=with_latex,
                color_col="level")

    print("  Stage 5 — information-theoretic (rule entropy)")
    _emit_stage(fid_dfs, "feature_id", "rule_entropy",
                "Rule Distribution Entropy  (within-feature diversity)",
                "entropy  (bits)",
                base / STAGE_NAMES[5], False, plot,
                extra_cols=[], with_latex=with_latex,
                color_col="level")
    _emit_stage(fid_dfs, "feature_id", "score_entropy",
                "Entropy-Weighted Log₂ Rate  (|log₂ × rule_entropy|)",
                "|score_entropy|",
                base / STAGE_NAMES[5], True, plot,
                extra_cols=[], with_latex=with_latex,
                color_col="level")


# ═══════════════════════════════════════════════════════════════════════════
# TASK 3 — Complexity & Similarity Study
# ═══════════════════════════════════════════════════════════════════════════

# Representative metric per sublevel (complexity perspective)
T3_COMPLEXITY_METRICS = {
    ("character",     "chars"):                 ("char_entropy", "character entropy (bits)"),
    ("lexical",       "surface_forms"):          ("mattr",        "MATTR"),
    ("lexical",       "lemmas"):                 ("ttr",          "TTR"),
    ("morphological", "pos_tags"):               ("entropy",      "POS entropy (bits)"),
    ("morphological", "morph_features"):         ("entropy",      "morph-feat entropy (bits)"),
    ("syntactic",     "dependency_relations"):   ("avg_dependency_distance", "mean dep. distance"),
    ("syntactic",     "constituency_labels"):    ("entropy",      "const-label entropy (bits)"),
    ("structural",    "constituency"):           ("avg_depth",    "avg tree depth"),
    ("structural",    "dependency"):             ("mdd_normalized", "MDD (normalised)"),
}

T3_LEVEL_INDEX = {
    "character": 1, "lexical": 2, "morphological": 3,
    "syntactic": 4, "structural": 5,
}


def _t3_load(newspapers: list) -> dict:
    dfs = {}
    for np_name in newspapers:
        cpx_p = (T3_DIR / "per-newspaper" / np_name
                 / "complexity" / "complexity_summary.csv")
        sim_p = (T3_DIR / "per-newspaper" / np_name
                 / "similarity" / "bidirectional_metrics.csv")
        if not cpx_p.exists():
            print(f"  [skip] complexity_summary.csv not found for {np_name}")
            continue
        cpx = pd.read_csv(cpx_p)
        sim = pd.read_csv(sim_p) if sim_p.exists() else pd.DataFrame()
        dfs[np_name] = {"complexity": cpx, "similarity": sim}
    return dfs


def _t3_build_summary(raw: dict) -> dict:
    """Build one DataFrame per newspaper with canonical, headline, ratio, log2, weighted, jsd."""
    summaries = {}
    for np_name, data in raw.items():
        cpx = data["complexity"]
        sim = data["similarity"]
        rows = []
        for (level, sublevel), (metric, metric_label) in T3_COMPLEXITY_METRICS.items():
            sub = cpx[(cpx["level"] == level) & (cpx["sublevel"] == sublevel)]
            if sub.empty or metric not in sub.columns:
                continue
            vals = sub[metric].dropna().values
            if len(vals) < 2:
                continue
            canon_v = float(vals[0])   # even row = canonical
            head_v  = float(vals[1])   # odd row  = headline
            ratio   = canon_v / head_v if abs(head_v) > EPSILON else np.nan
            log2_r  = np.log2(ratio) if ratio > 0 else np.nan
            lvl_idx = T3_LEVEL_INDEX.get(level, 3)
            wt_lvl  = 1.0 / lvl_idx
            score_lvl = log2_r * wt_lvl if pd.notna(log2_r) else np.nan
            # JSD from bidirectional_metrics (if available)
            jsd = np.nan
            if not sim.empty:
                sim_row = sim[(sim["level"] == level) & (sim["sublevel"] == sublevel)]
                if not sim_row.empty and "js_divergence" in sim_row.columns:
                    jsd = float(sim_row["js_divergence"].iloc[0])
            score_jsd = log2_r * jsd if (pd.notna(log2_r) and pd.notna(jsd)) else np.nan
            rows.append({
                "sublevel_id": f"{level}/{sublevel}",
                "level":       level,
                "level_index": lvl_idx,
                "metric":      metric_label,
                "canonical":   canon_v,
                "headline":    head_v,
                "rate_norm":   ratio,
                "log2_norm":   log2_r,
                "weight_lvl":  wt_lvl,
                "score_lvl":   score_lvl,
                "jsd":         jsd,
                "score_jsd":   score_jsd,
            })
        summaries[np_name] = pd.DataFrame(rows)
    return summaries


def run_task3(newspapers: list, plot: bool,
              base_dir: Path = None,
              with_latex: bool = False) -> None:
    print("\n" + "=" * 60)
    print("  Task 3 — Complexity & Similarity Study")
    print("=" * 60)
    raw   = _t3_load(newspapers)
    if not raw:
        print("  [skip] no data found"); return
    sums  = _t3_build_summary(raw)
    base  = base_dir if base_dir is not None else T3_DIR / "fair-comparison"

    # Rename sublevel_id → feature_id for use with _emit_stage
    fid_sums = {k: v.rename(columns={"sublevel_id": "feature_id"})
                for k, v in sums.items()}

    # ── Stage 1: raw metrics (canonical + headline side by side) ──────────
    print("  Stage 1 — raw complexity metrics (canonical vs headline)")
    d = base / STAGE_NAMES[1]
    # per-NP canonical/headline grouped bar chart
    for np_name, df in sums.items():
        _tbl(df[["sublevel_id", "level", "metric", "canonical", "headline"]].copy(),
             d / "per-newspaper" / np_name / "raw_metrics.csv")
        if plot:
            _save(_t3_grouped_reg_chart(
                df, "canonical", "headline",
                "Raw Complexity Metrics  (canonical vs headline)",
                "metric value", np_name),
                d / "per-newspaper" / np_name / "raw_metrics.png")
    # cross-NP canonical values
    _emit_stage(fid_sums, "feature_id", "canonical",
                "Canonical Complexity Metrics", "canonical metric value",
                d, False, plot, extra_cols=["level", "metric"],
                with_latex=with_latex)
    # cross-NP headline values
    _emit_stage(fid_sums, "feature_id", "headline",
                "Headline Complexity Metrics", "headline metric value",
                d, False, plot, extra_cols=["level", "metric"],
                with_latex=with_latex)

    # ── Stage 2: normalized ratio ─────────────────────────────────────────
    print("  Stage 2 — canonical / headline ratio")
    d = base / STAGE_NAMES[2]
    _emit_stage(fid_sums, "feature_id", "rate_norm",
                "Complexity Ratio  (canonical / headline)",
                "ratio  (>1 means canonical more complex)",
                d, False, plot, extra_cols=["level", "metric"],
                with_latex=with_latex)

    # ── Stage 3: log₂ ratio ───────────────────────────────────────────────
    print("  Stage 3 — log₂(canonical / headline) ratio")
    d = base / STAGE_NAMES[3]
    _emit_stage(fid_sums, "feature_id", "log2_norm",
                "Log₂ Complexity Ratio  (bits advantage of canonical)",
                "log₂(canonical / headline)  (bits)",
                d, True, plot, extra_cols=["level", "metric"],
                with_latex=with_latex)

    # ── Stage 4: level-weighted ───────────────────────────────────────────
    print("  Stage 4 — level-weighted log₂ ratio")
    d = base / STAGE_NAMES[4]
    _emit_stage(fid_sums, "feature_id", "score_lvl",
                "Level-Weighted Complexity Score  (log₂ ratio × w_level)",
                "score_lvl",
                d, False, plot, extra_cols=["level", "metric"],
                with_latex=with_latex)

    # ── Stage 5: information-theoretic (JSD) ─────────────────────────────
    print("  Stage 5 — information-theoretic (JSD, KL from bidirectional metrics)")
    d = base / STAGE_NAMES[5]
    # Per-NP: JSD and KL tables from bidirectional_metrics.csv
    for np_name, data in raw.items():
        sim = data["similarity"]
        if sim.empty:
            continue
        _tbl(sim, d / "per-newspaper" / np_name / "bidirectional_metrics.csv")
        if plot:
            for col, title, xl in [
                ("js_divergence", "JSD between Registers  (per level)",
                 "JS divergence  (bits)"),
                ("kl_symmetrized", "Symmetrised KL Divergence  (per level)",
                 "KL sym. (bits)"),
                ("wasserstein_distance", "Wasserstein Distance  (per level)",
                 "Wasserstein dist."),
            ]:
                if col not in sim.columns:
                    continue
                sim2 = sim.copy()
                sim2.insert(0, "feature_id",
                            sim2["level"] + "/" + sim2["sublevel"])
                fig = _hbar(sim2, col, title, xl,
                            color_col="level", newspaper=np_name)
                _save(fig, d / "per-newspaper" / np_name / f"{col}.png")
    # JSD-weighted score from complexity summary
    _emit_stage(fid_sums, "feature_id", "score_jsd",
                "JSD-Weighted Complexity Score",
                "score_jsd  (|log₂(ratio) × JSD|)",
                d, True, plot, extra_cols=["level", "metric"],
                with_latex=with_latex)
    # Cross-NP raw JSD
    _emit_stage(fid_sums, "feature_id", "jsd",
                "JSD (canonical vs headline)",
                "Jensen-Shannon divergence",
                d, False, plot, extra_cols=["level"],
                with_latex=with_latex)
    # Cross-NP divergence metrics from similarity tables
    if plot and len(raw) > 1:
        sim_dfs = {}
        for np_name, data in raw.items():
            sim = data["similarity"]
            if not sim.empty:
                sim2 = sim.copy()
                sim2["feature_id"] = sim2["level"] + "/" + sim2["sublevel"]
                sim_dfs[np_name] = sim2
        if len(sim_dfs) > 1:
            for col, title, xl in [
                ("js_divergence", "JSD — All Newspapers", "JS divergence"),
                ("kl_symmetrized", "KL (sym.) — All Newspapers", "KL sym."),
                ("wasserstein_distance", "Wasserstein — All Newspapers", "Wasserstein"),
            ]:
                if all(col in df.columns for df in sim_dfs.values()):
                    fig = _cross_np_grouped(sim_dfs, col, "feature_id",
                                            title, xl)
                    _save(fig, d / "cross-newspaper" / f"{col}.png")


def _t3_grouped_reg_chart(df: pd.DataFrame,
                           col_c: str, col_h: str,
                           title: str, xlabel: str,
                           newspaper: str) -> plt.Figure:
    """Grouped bar chart: 2 bars (canonical, headline) per sublevel."""
    labels = df["sublevel_id"].tolist()
    n      = len(labels)
    fig, ax = plt.subplots(figsize=(9, max(3.5, n * BAR_H * 2 + 1.5)))
    y   = np.arange(n)
    off = BAR_H / 2
    ax.barh(y + off,  df[col_c].fillna(0), height=BAR_H * 0.85,
            color=REG_COLORS["canonical"], label="Canonical", edgecolor="white", lw=0.3)
    ax.barh(y - off, df[col_h].fillna(0), height=BAR_H * 0.85,
            color=REG_COLORS["headline"],  label="Headline",  edgecolor="white", lw=0.3)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=FS)
    ax.set_title(f"{title}  —  {newspaper}", fontsize=FT, pad=8)
    ax.set_xlabel(xlabel, fontsize=FM)
    ax.tick_params(axis="x", labelsize=FS)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=FS, loc="lower right", framealpha=0.7)
    fig.tight_layout()
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Generate per-stage fair-comparison tables and figures for all tasks"
    )
    parser.add_argument("--no-plots", action="store_true",
                        help="Skip figure generation; save tables only.")
    parser.add_argument("--newspapers", nargs="+", default=None,
                        metavar="NP",
                        help=f"Newspapers to process (default: all). Choices: {NEWSPAPERS}")
    parser.add_argument("--tasks", nargs="+", type=int, default=[1, 2, 3],
                        metavar="N",
                        help="Tasks to run (1, 2, 3; default: all)")
    args = parser.parse_args()

    newspapers = args.newspapers or NEWSPAPERS
    invalid    = [n for n in newspapers if n not in NEWSPAPERS]
    if invalid:
        print(f"[ERROR] Unknown newspaper(s): {invalid}")
        print(f"        Valid: {NEWSPAPERS}")
        sys.exit(1)

    plot = not args.no_plots

    if 1 in args.tasks:
        run_task1(newspapers, plot)
    if 2 in args.tasks:
        run_task2(newspapers, plot)
    if 3 in args.tasks:
        run_task3(newspapers, plot)

    print("\nDone.")


if __name__ == "__main__":
    main()
