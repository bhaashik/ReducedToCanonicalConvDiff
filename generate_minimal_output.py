#!/usr/bin/env python3
"""
generate_minimal_output.py
===========================
Focused, publication-ready output: constituency, dependency, morphological,
POS, punctuation, function-word, TED-score, and overall schema-based figures.

Numeric count-change events (LENGTH-CHG, HEAD-CHG, DEP-DIST-DIFF, etc.) are
excluded from transformation bar charts — TED scores represent that dimension.

Directory structure (per task):
    output-minimal/task-N-*/
    ├── global/            ← aggregate (all 3 NPs) + cross-NP overview + tables
    ├── Times-of-India/    ← cross-NP grouped-bar figures sorted by ToI values
    ├── Hindustan-Times/   ← cross-NP grouped-bar figures sorted by HT values
    └── The-Hindu/         ← cross-NP grouped-bar figures sorted by TH values

Bar charts: grouped bars (3 per item, one colour per NP, legend).
Pie/donut:  1×3 row (one pie per NP) — exempt from grouped-bar rule.
Line/scatter: overlaid on shared axes.

Figure splitting: any category with more than MAX_FEATS_PER_FIG features is
split into _part1, _part2 … files so that each remains readable at A4/A3.

Reads from   output/
Writes to    output-minimal/
"""

import shutil
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

import generate_supplementary_visualizations as gsv

_csv    = gsv._csv
_short  = gsv._short
_absent = gsv._absent
CAT         = gsv.CAT
CAT_COLORS  = gsv.CAT_COLORS
C3          = gsv.C3
NP_C        = gsv.NP_C
LEVEL_ORDER = gsv.LEVEL_ORDER
LEVEL_LBL   = gsv.LEVEL_LBL
NEWSPAPERS  = gsv.NEWSPAPERS

# ── Paths ─────────────────────────────────────────────────────────────────────
SRC = Path("output")
OUT = Path("output-minimal")
gsv.OUT = OUT

S1 = SRC / "task-1-comparative-study"
S2 = SRC / "task-2-transformation-study"
S3 = SRC / "task-3-complexity-similarity-study"

O1 = OUT / "task-1-comparative-study"
O2 = OUT / "task-2-transformation-study"
O3 = OUT / "task-3-complexity-similarity-study"

# ── Feature classification ────────────────────────────────────────────────────
# Numeric count-change events: transformation bars are uninformative (22→24 etc.)
NUMERIC_SKIP = frozenset({
    "DEP-DIST-DIFF", "BRANCH-DIFF", "CONST-COUNT-DIFF",
    "TREE-DEPTH-DIFF", "LENGTH-CHG", "HEAD-CHG",
})
# TED score features: visualised as score distributions, not as transformation bars
TED_FEATURES = frozenset({"TED-SIMPLE", "TED-ZHANG-SHASHA", "TED-KLEIN", "TED-RTED"})
# Sparse / low-signal features: omitted from transformation figures
SPARSE_SKIP = frozenset({"FORM-CHG", "LEMMA-CHG", "TOKEN-REORDER", "H-STRUCT"})

# Feature groups for category analysis
CONSTITUENCY  = ["CONST-MOV", "H-TYPE", "CLAUSE-TYPE-CHG", "CONST-ADD", "CONST-REM"]
DEPENDENCY    = ["DEP-REL-CHG"]          # HEAD-CHG is numeric
MORPHOLOGICAL = ["FEAT-CHG"]             # special: grouped by morph feature name
POS           = ["POS-CHG"]
FUNC_WORD     = ["FW-DEL", "FW-ADD"]
PUNCTUATION   = ["PUNCT-DEL", "PUNCT-ADD", "PUNCT-SUBST"]
CONTENT_WORD  = ["C-DEL", "C-ADD", "VERB-FORM-CHG"]

# Layout parameters
_MAX_TRANS       = 15   # max transformation types shown per feature subplot
_MAX_FEATS_FIG   = 3    # max features per figure before splitting into parts
_BAR_H_PER_ITEM  = 0.42 # inches per bar item (for height estimation)
_SUBPLOT_H_MIN   = 5.0  # minimum subplot height (inches)
_SUBPLOT_H_PAD   = 2.0  # top/bottom padding per subplot (inches)
_COL_W_SINGLE    = 8.5  # column width for single-bar (aggregate) figures
_COL_W_GROUPED   = 10.0 # column width for 3-bar grouped figures


# ── Save / table helpers ───────────────────────────────────────────────────────
def _save(path: Path, dpi: int = 150):
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close()
    print(f"  saved → {path.relative_to(OUT)}")


def _copy_tables(src_dir: Path, dst_dir: Path, names=None) -> int:
    dst_dir.mkdir(parents=True, exist_ok=True)
    candidates = (
        [src_dir / n for n in names] if names
        else sorted(src_dir.glob("*.csv")) + sorted(src_dir.glob("*.tex"))
    )
    n = 0
    for src in candidates:
        if src.exists():
            shutil.copy2(src, dst_dir / src.name)
            print(f"  table  → {(dst_dir / src.name).relative_to(OUT)}")
            n += 1
    return n


def _np_legend(ax, loc="best", fontsize=9):
    handles = [mpatches.Patch(facecolor=C3[i], alpha=0.87, label=n)
               for i, n in enumerate(NEWSPAPERS)]
    ax.legend(handles=handles, title="Newspaper", fontsize=fontsize, loc=loc)


def _is_numeric(v):
    try:
        float(str(v)); return True
    except (ValueError, TypeError):
        return False


# ══════════════════════════════════════════════════════════════════════════════
# Core category figure engine
# ══════════════════════════════════════════════════════════════════════════════

def _read_transforms(data_dirs: dict, fid: str, max_rows: int = 60) -> dict:
    """Read per-feature transformation CSV for every newspaper.

    Returns {newspaper: [(label, count), ...]} sorted by count desc.
    """
    result = {}
    for n in NEWSPAPERS:
        df = _csv(data_dirs[n] / f"feature_value_analysis_feature_{fid}.csv")
        if df is None or df.empty:
            result[n] = []
            continue
        top = df.head(max_rows)
        items = []
        for _, r in top.iterrows():
            cval = str(r.get("canonical_value", "")) if pd.notna(r.get("canonical_value", "")) else ""
            hval = str(r.get("headline_value",  "")) if pd.notna(r.get("headline_value",  "")) else ""
            trans = r.get("transformation", "")
            if trans and pd.notna(trans):
                lbl = str(trans)
            else:
                lbl = _absent(cval) + "→" + _absent(hval)
            items.append((lbl, int(r.get("count", 0))))
        result[n] = sorted(items, key=lambda x: x[1], reverse=True)
    return result


def _transform_order(feat_data: dict, fid: str, focal_np=None, n: int = _MAX_TRANS) -> list:
    """Return ordered list of transformation labels for one feature."""
    if focal_np and feat_data[fid].get(focal_np):
        return [lbl for lbl, _ in feat_data[fid][focal_np][:n]]
    totals: dict = {}
    for items in feat_data[fid].values():
        for lbl, cnt in items:
            totals[lbl] = totals.get(lbl, 0) + cnt
    return sorted(totals, key=lambda k: totals[k], reverse=True)[:n]


def _cat_fig(data_dirs: dict, features: list, title_prefix: str,
             focal_np, out_dir: Path, fname_base: str,
             max_trans: int = _MAX_TRANS,
             max_feats_per_fig: int = _MAX_FEATS_FIG) -> None:
    """Create one or more figures showing top transformations for a feature list.

    focal_np=None  → aggregate: single horizontal bars coloured by feature category.
    focal_np=str   → cross-NP:  grouped horizontal bars (3 per item, coloured by NP).
    Figures are split into _part1 / _part2 … if len(features) > max_feats_per_fig.
    """
    # Load data
    feat_data = {fid: _read_transforms(data_dirs, fid, max_rows=max_trans * 3)
                 for fid in features}

    # Build transformation orders
    orders = {fid: _transform_order(feat_data, fid, focal_np, max_trans)
              for fid in features}

    # Split into parts
    parts = [features[i:i + max_feats_per_fig]
             for i in range(0, len(features), max_feats_per_fig)]

    for p_idx, part_feats in enumerate(parts):
        suffix = f"_part{p_idx + 1}" if len(parts) > 1 else ""
        n_feats = len(part_feats)
        n_cols  = min(2, n_feats)
        n_rows  = (n_feats + n_cols - 1) // n_cols

        max_items  = max((len(orders[fid]) for fid in part_feats), default=5)
        row_h = max(_SUBPLOT_H_MIN, max_items * _BAR_H_PER_ITEM + _SUBPLOT_H_PAD)
        col_w = _COL_W_GROUPED if focal_np else _COL_W_SINGLE

        fig, axs = plt.subplots(n_rows, n_cols,
                                figsize=(n_cols * col_w, n_rows * row_h),
                                squeeze=False)

        title = title_prefix
        if len(parts) > 1:
            title += f" (Part {p_idx + 1}/{len(parts)})"
        if focal_np:
            title += f"\nSorted by {focal_np}"
        fig.suptitle(title, fontsize=12, fontweight="bold")

        for f_idx, fid in enumerate(part_feats):
            ax = axs[f_idx // n_cols][f_idx % n_cols]
            cat   = CAT.get(fid, "Other")
            color = CAT_COLORS.get(cat, "#757575")
            ax.set_title(fid, fontsize=10, fontweight="bold", color=color)

            order = orders[fid]
            if not order:
                ax.text(0.5, 0.5, "No data", ha="center", va="center",
                        transform=ax.transAxes, color="#aaa"); continue

            x = np.arange(len(order))

            if focal_np:
                w = 0.25
                for i, n in enumerate(NEWSPAPERS):
                    lut = dict(feat_data[fid][n])
                    vals = [lut.get(lbl, 0) for lbl in order]
                    ax.barh(x + i * w, vals[::-1], w,
                            label=n, color=C3[i], alpha=0.85, edgecolor="white")
                ax.set_yticks(x + w)
                if f_idx == 0:
                    ax.legend(title="NP", fontsize=7, loc="lower right")
            else:
                totals = {}
                for items in feat_data[fid].values():
                    for lbl, cnt in items:
                        totals[lbl] = totals.get(lbl, 0) + cnt
                vals = [totals.get(lbl, 0) for lbl in order]
                ax.barh(x, vals[::-1], color=color, alpha=0.87, edgecolor="white")
                mx = max(vals) if vals else 1
                for bar, v in zip(ax.patches, vals[::-1]):
                    ax.text(v + mx * 0.01,
                            bar.get_y() + bar.get_height() / 2,
                            f"{int(v):,}", va="center", fontsize=7)
                ax.set_yticks(x)

            ax.set_yticklabels(order[::-1], fontsize=7.5)
            ax.set_xlabel("Event count")

        # Hide unused subplots
        for f_idx in range(n_feats, n_rows * n_cols):
            axs[f_idx // n_cols][f_idx % n_cols].set_visible(False)

        _save(out_dir / f"{fname_base}{suffix}.png")


# ══════════════════════════════════════════════════════════════════════════════
# Morphological feature breakdown (FEAT-CHG grouped by morph attribute)
# ══════════════════════════════════════════════════════════════════════════════

def _morph_fig(data_dirs: dict, focal_np, out_dir: Path,
               max_trans: int = 10, max_feats_per_fig: int = 4) -> None:
    """FEAT-CHG: group by morphological attribute (Tense, Number, …), show top transforms."""
    morph_data: dict = {}   # {attr: {newspaper: {label: count}}}

    for n in NEWSPAPERS:
        df = _csv(data_dirs[n] / "feature_value_analysis_feature_FEAT-CHG.csv")
        if df is None or df.empty:
            continue
        for _, r in df.iterrows():
            cval = str(r.get("canonical_value", "")) if pd.notna(r.get("canonical_value", "")) else ""
            hval = str(r.get("headline_value",  "")) if pd.notna(r.get("headline_value",  "")) else ""
            # Extract morph attribute name (e.g. "Tense" from "Tense=Past")
            attr = None
            for v in [cval, hval]:
                if "=" in v:
                    attr = v.split("=")[0].strip()
                    break
            if not attr:
                continue
            # Compact label: just the values (not the attribute names repeated)
            c_mval = cval.split("=")[1].strip() if "=" in cval else cval
            h_mval = hval.split("=")[1].strip() if "=" in hval else hval
            lbl = f"{c_mval}→{h_mval}"
            cnt = int(r.get("count", 0))
            morph_data.setdefault(attr, {}).setdefault(n, {})
            morph_data[attr][n][lbl] = morph_data[attr][n].get(lbl, 0) + cnt

    if not morph_data:
        return

    # Sort attributes by total count across all NPs
    attr_totals = {
        a: sum(sum(morph_data[a].get(n, {}).values()) for n in NEWSPAPERS)
        for a in morph_data
    }
    sorted_attrs = sorted(attr_totals, key=lambda k: attr_totals[k], reverse=True)

    parts = [sorted_attrs[i:i + max_feats_per_fig]
             for i in range(0, len(sorted_attrs), max_feats_per_fig)]
    morph_color = "#9C27B0"

    for p_idx, part_attrs in enumerate(parts):
        suffix = f"_part{p_idx + 1}" if len(parts) > 1 else ""
        n_feats = len(part_attrs)
        n_cols  = min(2, n_feats)
        n_rows  = (n_feats + n_cols - 1) // n_cols

        # Determine order per attribute
        orders: dict = {}
        for attr in part_attrs:
            if focal_np and morph_data[attr].get(focal_np):
                d = morph_data[attr][focal_np]
                orders[attr] = sorted(d, key=lambda k: d[k], reverse=True)[:max_trans]
            else:
                totals: dict = {}
                for n in NEWSPAPERS:
                    for lbl, cnt in morph_data[attr].get(n, {}).items():
                        totals[lbl] = totals.get(lbl, 0) + cnt
                orders[attr] = sorted(totals, key=lambda k: totals[k], reverse=True)[:max_trans]

        max_items = max((len(o) for o in orders.values()), default=5)
        row_h = max(_SUBPLOT_H_MIN, max_items * _BAR_H_PER_ITEM + _SUBPLOT_H_PAD)
        col_w = _COL_W_GROUPED if focal_np else _COL_W_SINGLE

        fig, axs = plt.subplots(n_rows, n_cols,
                                figsize=(n_cols * col_w, n_rows * row_h),
                                squeeze=False)

        title = "Morphological Feature Changes (FEAT-CHG)"
        if len(parts) > 1:
            title += f" — Part {p_idx + 1}/{len(parts)}"
        if focal_np:
            title += f"\nSorted by {focal_np}"
        fig.suptitle(title, fontsize=12, fontweight="bold")

        for f_idx, attr in enumerate(part_attrs):
            ax = axs[f_idx // n_cols][f_idx % n_cols]
            ax.set_title(f"Morphological: {attr}", fontsize=10,
                         fontweight="bold", color=morph_color)
            order = orders[attr]
            if not order:
                ax.text(0.5, 0.5, "No data", ha="center", va="center",
                        transform=ax.transAxes, color="#aaa"); continue

            x = np.arange(len(order))

            if focal_np:
                w = 0.25
                for i, n in enumerate(NEWSPAPERS):
                    vals = [morph_data[attr].get(n, {}).get(lbl, 0) for lbl in order]
                    ax.barh(x + i * w, vals[::-1], w,
                            label=n, color=C3[i], alpha=0.85, edgecolor="white")
                ax.set_yticks(x + w)
                if f_idx == 0:
                    ax.legend(title="NP", fontsize=7, loc="lower right")
            else:
                totals = {lbl: sum(morph_data[attr].get(n, {}).get(lbl, 0) for n in NEWSPAPERS)
                          for lbl in order}
                vals = [totals[lbl] for lbl in order]
                ax.barh(x, vals[::-1], color=morph_color, alpha=0.87, edgecolor="white")
                mx = max(vals) if vals else 1
                for bar, v in zip(ax.patches, vals[::-1]):
                    ax.text(v + mx * 0.01,
                            bar.get_y() + bar.get_height() / 2,
                            f"{int(v):,}", va="center", fontsize=7)
                ax.set_yticks(x)

            ax.set_yticklabels(order[::-1], fontsize=8)
            ax.set_xlabel("Event count")

        for f_idx in range(n_feats, n_rows * n_cols):
            axs[f_idx // n_cols][f_idx % n_cols].set_visible(False)

        fname = ("t1c_morphological" if focal_np else "t1a_morphological") + suffix
        _save(out_dir / f"{fname}.png")


# ══════════════════════════════════════════════════════════════════════════════
# TED score distributions
# ══════════════════════════════════════════════════════════════════════════════

def _ted_fig(data_dirs: dict, focal_np, out_dir: Path) -> None:
    """TED score distributions: frequency of each tree-edit-distance value per NP."""
    available = [f for f in sorted(TED_FEATURES)
                 if _csv(data_dirs[NEWSPAPERS[0]] / f"feature_value_analysis_feature_{f}.csv")
                 is not None]
    if not available:
        return

    n_cols = min(2, len(available))
    n_rows = (len(available) + n_cols - 1) // n_cols
    fig, axs = plt.subplots(n_rows, n_cols,
                            figsize=(n_cols * 8.5, n_rows * 5.5),
                            squeeze=False)

    title = "Tree Edit Distance (TED) Score Distributions"
    if focal_np:
        title += f"\nGrouped by {focal_np} (all NPs shown)"
    fig.suptitle(title, fontsize=12, fontweight="bold")

    for f_idx, fid in enumerate(available):
        ax = axs[f_idx // n_cols][f_idx % n_cols]
        ax.set_title(fid, fontsize=10, fontweight="bold", color="#FF6F00")

        # Collect score→count per NP
        np_counts: dict = {n: {} for n in NEWSPAPERS}
        for n in NEWSPAPERS:
            df = _csv(data_dirs[n] / f"feature_value_analysis_feature_{fid}.csv")
            if df is None or df.empty:
                continue
            for _, r in df.iterrows():
                try:
                    score = int(float(str(r.get("canonical_value", 0))))
                    cnt   = int(r.get("count", 0))
                    np_counts[n][score] = np_counts[n].get(score, 0) + cnt
                except (ValueError, TypeError):
                    pass

        # All scores present (up to 15, then ">15")
        all_scores = sorted({s for counts in np_counts.values() for s in counts})
        if not all_scores:
            ax.text(0.5, 0.5, "No data", ha="center", va="center",
                    transform=ax.transAxes, color="#aaa"); continue

        high = [s for s in all_scores if s > 15]
        bin_keys = [s for s in all_scores if s <= 15]
        labels = [str(s) for s in bin_keys]
        if high:
            bin_keys.append(">15")
            labels.append(">15")
            for n in NEWSPAPERS:
                extra = sum(np_counts[n].get(s, 0) for s in high)
                np_counts[n][">15"] = extra

        x = np.arange(len(labels)); w = 0.25
        for i, n in enumerate(NEWSPAPERS):
            vals = [np_counts[n].get(k, 0) for k in bin_keys]
            ax.bar(x + i * w, vals, w, label=n, color=C3[i], alpha=0.85)
        ax.set_xticks(x + w)
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_xlabel("TED score")
        ax.set_ylabel("Pair count")
        if f_idx == 0:
            ax.legend(title="Newspaper", fontsize=8)

    for f_idx in range(len(available), n_rows * n_cols):
        axs[f_idx // n_cols][f_idx % n_cols].set_visible(False)

    fname = "t1c_ted_scores" if focal_np else "t1a_ted_scores"
    _save(out_dir / f"{fname}.png")


# ══════════════════════════════════════════════════════════════════════════════
# TASK 1 — Aggregate overview figures (all 3 NPs summed)
# ══════════════════════════════════════════════════════════════════════════════

def t1a_feature_frequency(data_dirs: dict, out_dir: Path) -> None:
    """Single horizontal bar — top-20 features by total count."""
    frames = [_csv(data_dirs[n] / "feature_freq_global.csv") for n in NEWSPAPERS]
    frames = [f for f in frames if f is not None]
    if not frames:
        return
    agg = pd.concat(frames).groupby("feature_id")["count"].sum().reset_index()
    agg = agg.sort_values("count", ascending=False).head(20)
    agg["cat"] = agg["feature_id"].map(CAT).fillna("Other")
    colors = [CAT_COLORS.get(c, "#757575") for c in agg["cat"]]

    fig, ax = plt.subplots(figsize=(10, 8))
    bars = ax.barh(agg["feature_id"][::-1], agg["count"][::-1],
                   color=colors[::-1], alpha=0.87, edgecolor="white")
    mx = agg["count"].max()
    for bar, v in zip(bars, agg["count"][::-1]):
        ax.text(v + mx * 0.01, bar.get_y() + bar.get_height() / 2,
                f"{int(v):,}", va="center", fontsize=8)
    ax.set_xlabel("Total event count (all newspapers)")
    ax.set_ylabel("Feature ID")
    ax.set_title("Feature Event Frequency — All Newspapers Aggregate",
                 fontsize=13, fontweight="bold")
    _save(out_dir / "t1a_feature_frequency.png")


def t1a_category_distribution(data_dirs: dict, out_dir: Path) -> None:
    """Category bar + 1×3 pies — all NPs summed."""
    frames = [_csv(data_dirs[n] / "feature_freq_global.csv") for n in NEWSPAPERS]
    frames = [f for f in frames if f is not None]
    if not frames:
        return
    agg = pd.concat(frames)
    agg["cat"] = agg["feature_id"].map(CAT).fillna("Other")
    cat_totals = agg.groupby("cat")["count"].sum().sort_values(ascending=False)
    colors = [CAT_COLORS.get(c, "#757575") for c in cat_totals.index]

    fig = plt.figure(figsize=(16, 10))
    gs  = gridspec.GridSpec(2, 3, figure=fig, hspace=0.55, wspace=0.35,
                            height_ratios=[1.4, 1])
    ax_bar = fig.add_subplot(gs[0, :])
    bars = ax_bar.bar(range(len(cat_totals)), cat_totals.values, color=colors, alpha=0.87)
    for bar, v in zip(bars, cat_totals.values):
        ax_bar.text(bar.get_x() + bar.get_width() / 2, v + cat_totals.max() * 0.01,
                    f"{int(v):,}", ha="center", fontsize=9)
    ax_bar.set_xticks(range(len(cat_totals)))
    ax_bar.set_xticklabels(cat_totals.index, rotation=30, ha="right", fontsize=9)
    ax_bar.set_ylabel("Total event count")
    ax_bar.set_title("Category Totals — All Newspapers Aggregate", fontweight="bold")

    for col, n in enumerate(NEWSPAPERS):
        df = _csv(data_dirs[n] / "feature_freq_global.csv")
        ax_pie = fig.add_subplot(gs[1, col])
        ax_pie.set_title(n, fontsize=10, fontweight="bold")
        if df is None:
            ax_pie.text(0.5, 0.5, "No data", ha="center", va="center",
                        transform=ax_pie.transAxes, color="#aaa"); continue
        df["cat"] = df["feature_id"].map(CAT).fillna("Other")
        s = df.groupby("cat")["count"].sum().sort_values(ascending=False)
        ax_pie.pie(s.values, labels=s.index,
                   colors=[CAT_COLORS.get(c, "#757575") for c in s.index],
                   autopct=lambda p: f"{p:.0f}%" if p > 4 else "",
                   startangle=90, pctdistance=0.78,
                   wedgeprops={"edgecolor": "white", "linewidth": 1.2})

    fig.suptitle("Feature Category Distribution", fontsize=13, fontweight="bold")
    _save(out_dir / "t1a_category_distribution.png")


def t1a_transformation_diversity(data_dirs: dict, out_dir: Path) -> None:
    """Mean entropy + concentration per feature (informative features only)."""
    EXCLUDED = NUMERIC_SKIP | TED_FEATURES | SPARSE_SKIP
    frames = [_csv(data_dirs[n] / "feature_value_analysis_value_statistics.csv")
              for n in NEWSPAPERS]
    frames = [f for f in frames if f is not None]
    if not frames:
        return
    agg = (pd.concat(frames).groupby("feature_id")
           [["transformation_entropy", "top3_concentration_ratio"]]
           .mean().reset_index())
    agg = agg[~agg["feature_id"].isin(EXCLUDED)]
    agg = agg.sort_values("transformation_entropy", ascending=False)
    agg["cat"] = agg["feature_id"].map(CAT).fillna("Other")
    colors = [CAT_COLORS.get(c, "#757575") for c in agg["cat"]]

    fig, axes = plt.subplots(1, 2, figsize=(16, max(6, len(agg) * 0.4 + 2)))
    axes[0].barh(agg["feature_id"][::-1], agg["transformation_entropy"][::-1],
                 color=colors[::-1], alpha=0.87, edgecolor="white")
    axes[0].set_xlabel("Mean entropy (bits)")
    axes[0].set_ylabel("Feature ID")
    axes[0].set_title("Transformation Entropy", fontweight="bold")

    axes[1].barh(agg["feature_id"][::-1], agg["top3_concentration_ratio"][::-1],
                 color=colors[::-1], alpha=0.87, edgecolor="white")
    axes[1].axvline(0.8, color="grey", lw=0.9, ls="--", alpha=0.6)
    axes[1].set_xlabel("Top-3 concentration ratio")
    axes[1].set_title("Transformation Concentration", fontweight="bold")

    fig.suptitle("Transformation Diversity (informative features only) — Aggregate",
                 fontsize=13, fontweight="bold")
    _save(out_dir / "t1a_transformation_diversity.png")


def t1a_top_value_pairs(data_dirs: dict, out_dir: Path) -> None:
    """Top-25 feature-value pairs, excluding purely numeric pairs."""
    EXCLUDED = NUMERIC_SKIP | TED_FEATURES | SPARSE_SKIP
    frames = [_csv(data_dirs[n] / "feature_value_pair_analysis_top_pairs.csv")
              for n in NEWSPAPERS]
    frames = [f for f in frames if f is not None]
    if not frames:
        return
    agg = pd.concat(frames).groupby("pair_unit", as_index=False)["frequency"].sum()
    agg["feature"] = agg["pair_unit"].str.split(":").str[0]
    agg = agg[~agg["feature"].isin(EXCLUDED)]
    agg = agg.sort_values("frequency", ascending=False).head(25)
    agg["cat"] = agg["feature"].map(CAT).fillna("Other")
    colors = [CAT_COLORS.get(c, "#757575") for c in agg["cat"]]

    fig, ax = plt.subplots(figsize=(10, 10))
    bars = ax.barh(agg["pair_unit"][::-1], agg["frequency"][::-1],
                   color=colors[::-1], alpha=0.87, edgecolor="white")
    mx = agg["frequency"].max()
    for bar, v in zip(bars, agg["frequency"][::-1]):
        ax.text(v + mx * 0.01, bar.get_y() + bar.get_height() / 2,
                f"{int(v):,}", va="center", fontsize=7)
    ax.set_xlabel("Total frequency (all newspapers)")
    ax.tick_params(axis="y", labelsize=7.5)
    ax.set_title("Top-25 Feature-Value Pairs (numeric pairs excluded) — Aggregate",
                 fontsize=12, fontweight="bold")
    _save(out_dir / "t1a_top_value_pairs.png")


# ── Cross-NP scatter (no focal_np) ────────────────────────────────────────────

def t1c_statistical_overview(data_dirs: dict, out_dir: Path) -> None:
    """Overlaid scatter — all 3 newspapers on shared axes."""
    markers = ["o", "s", "^"]
    fig, ax = plt.subplots(figsize=(12, 7))
    for i, n in enumerate(NEWSPAPERS):
        df = _csv(data_dirs[n] / "statistical_summary_features.csv")
        if df is None:
            continue
        df = df[df["total_occurrences"] > 0].copy()
        df["cat"] = df["feature_id"].map(CAT).fillna("Other")
        colors = [CAT_COLORS.get(c, "#757575") for c in df["cat"]]
        ax.scatter(df["total_occurrences"], df["percentage_of_total"],
                   c=colors, s=70, alpha=0.80, marker=markers[i],
                   edgecolors=C3[i], linewidth=1.2, label=n)
        for _, row in df.iterrows():
            ax.annotate(row["feature_id"],
                        (row["total_occurrences"], row["percentage_of_total"]),
                        textcoords="offset points", xytext=(4, 2),
                        fontsize=6.5, color=C3[i], alpha=0.85)
    ax.set_xlabel("Total event occurrences (log scale)")
    ax.set_ylabel("Percentage of total events (%)")
    ax.set_xscale("log")
    ax.legend(title="Newspaper", fontsize=9)
    ax.set_title("Feature Occurrences vs. Percentage — Cross-Newspaper",
                 fontsize=12, fontweight="bold")
    _save(out_dir / "t1c_statistical_overview.png")


# ── Cross-NP feature frequency (sorted by focal_np) ──────────────────────────

def t1c_feature_frequency(data_dirs: dict, focal_np: str, out_dir: Path) -> None:
    """Grouped horizontal bar — top-20 features sorted by focal_np."""
    dfs = {n: _csv(data_dirs[n] / "feature_freq_global.csv") for n in NEWSPAPERS}
    focal = dfs.get(focal_np)
    if focal is None:
        return
    top20 = focal.sort_values("count", ascending=False).head(20)["feature_id"].tolist()
    count_lut = {n: dict(zip(dfs[n]["feature_id"], dfs[n]["count"]))
                 if dfs[n] is not None else {} for n in NEWSPAPERS}

    x = np.arange(len(top20)); w = 0.25
    fig, ax = plt.subplots(figsize=(12, max(7, len(top20) * 0.52 + 2)))
    for i, n in enumerate(NEWSPAPERS):
        vals = [count_lut[n].get(f, 0) for f in top20]
        ax.barh(x + i * w, vals[::-1], w, label=n, color=C3[i], alpha=0.85, edgecolor="white")
    ax.set_yticks(x + w)
    ax.set_yticklabels(top20[::-1], fontsize=8.5)
    ax.set_xlabel("Event count")
    _np_legend(ax, loc="lower right")
    ax.set_title(f"Feature Event Frequency (Top 20) — sorted by {focal_np}",
                 fontsize=12, fontweight="bold")
    _save(out_dir / "t1c_feature_frequency.png")


# ══════════════════════════════════════════════════════════════════════════════
# TASK 2 — Aggregate + cross-NP
# ══════════════════════════════════════════════════════════════════════════════

def t2a_rule_summary(data_dirs: dict, out_dir: Path) -> None:
    """Two bars — total rule frequency + avg confidence per feature, all NPs."""
    frames = []
    for n in NEWSPAPERS:
        df = _csv(data_dirs[n] / "morphological_rules.csv")
        if df is not None:
            df["newspaper"] = n; frames.append(df)
    if not frames:
        return
    combined = pd.concat(frames, ignore_index=True)
    agg = (combined.groupby("feature")
           .agg(total_freq=("frequency", "sum"), avg_conf=("confidence", "mean"))
           .reset_index().sort_values("total_freq", ascending=False))

    x = np.arange(len(agg))
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].bar(x, agg["total_freq"].values, color="#66BB6A", alpha=0.9, edgecolor="white")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(agg["feature"], rotation=35, ha="right", fontsize=9)
    axes[0].set_ylabel("Total frequency (all newspapers)")
    axes[0].set_title("Rule Frequency per Feature", fontweight="bold")

    axes[1].bar(x, agg["avg_conf"].values, color="#42A5F5", alpha=0.9, edgecolor="white")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(agg["feature"], rotation=35, ha="right", fontsize=9)
    axes[1].axhline(0.5, color="grey", lw=0.8, ls="--", alpha=0.5)
    axes[1].set_ylim(0, 1.2)
    axes[1].set_ylabel("Average confidence (0–1)")
    axes[1].set_title("Avg Rule Confidence per Feature", fontweight="bold")

    fig.suptitle("Morphological Rule Summary — All Newspapers Aggregate",
                 fontsize=13, fontweight="bold")
    _save(out_dir / "t2a_rule_summary.png")


def t2c_morphological_rule_frequencies(data_dirs: dict, focal_np: str, out_dir: Path) -> None:
    """Grouped horizontal bar — top-15 rules sorted by focal_np."""
    dfs = {n: _csv(data_dirs[n] / "morphological_rules.csv") for n in NEWSPAPERS}
    focal = dfs.get(focal_np)
    if focal is None:
        return
    focal2 = focal.copy()
    focal2["label"] = (focal2["feature"] + ": "
                       + focal2["transformation"].apply(lambda x: _short(x, 22)))
    top15 = focal2.sort_values("frequency", ascending=False).head(15)["label"].tolist()
    freq_lut = {}
    for n in NEWSPAPERS:
        df = dfs[n]
        if df is not None:
            df2 = df.copy()
            df2["label"] = (df2["feature"] + ": "
                            + df2["transformation"].apply(lambda x: _short(x, 22)))
            freq_lut[n] = dict(zip(df2["label"], df2["frequency"]))
        else:
            freq_lut[n] = {}

    x = np.arange(len(top15)); w = 0.25
    fig, ax = plt.subplots(figsize=(11, max(7, len(top15) * 0.57 + 2)))
    for i, n in enumerate(NEWSPAPERS):
        vals = [freq_lut[n].get(lbl, 0) for lbl in top15]
        ax.barh(x + i * w, vals[::-1], w, label=n, color=C3[i], alpha=0.85)
    ax.set_yticks(x + w)
    ax.set_yticklabels(top15[::-1], fontsize=8)
    ax.set_xlabel("Rule frequency")
    _np_legend(ax)
    ax.set_title(f"Morphological Rule Frequencies (Top 15) — sorted by {focal_np}",
                 fontsize=12, fontweight="bold")
    _save(out_dir / "t2c_morphological_rule_frequencies.png")


def t2c_morphological_feature_confidence(data_dirs: dict, focal_np: str, out_dir: Path) -> None:
    """Grouped bar — per-feature avg confidence sorted by focal_np frequency."""
    frames = []
    for n in NEWSPAPERS:
        df = _csv(data_dirs[n] / "morphological_rules.csv")
        if df is not None:
            df["newspaper"] = n; frames.append(df)
    if not frames:
        return
    combined = pd.concat(frames, ignore_index=True)
    feat_agg = (combined.groupby(["feature", "newspaper"])
                .agg(avg_conf=("confidence", "mean"), total_freq=("frequency", "sum"))
                .reset_index())
    focal_order = (feat_agg[feat_agg["newspaper"] == focal_np]
                   .sort_values("total_freq", ascending=False)["feature"].tolist())
    seen, all_feats = set(), []
    for f in focal_order + feat_agg["feature"].unique().tolist():
        if f not in seen:
            all_feats.append(f); seen.add(f)
    pivot = (feat_agg.pivot_table(index="feature", columns="newspaper",
                                   values="avg_conf", fill_value=0)
             .reindex([f for f in all_feats if f in
                       feat_agg.pivot_table(index="feature", columns="newspaper",
                                            values="avg_conf").index]))

    x = np.arange(len(pivot)); w = 0.25
    fig, ax = plt.subplots(figsize=(max(8, len(pivot) * 0.9 + 2), 5))
    for i, n in enumerate(NEWSPAPERS):
        if n in pivot.columns:
            ax.bar(x + i * w, pivot[n].values, w, label=n, color=C3[i], alpha=0.87)
    ax.set_xticks(x + w)
    ax.set_xticklabels(pivot.index, rotation=35, ha="right", fontsize=9)
    ax.set_ylim(0, 1.2)
    ax.axhline(0.5, color="grey", lw=0.8, ls="--", alpha=0.5)
    ax.set_ylabel("Average rule confidence (0–1)")
    _np_legend(ax)
    ax.set_title(f"Per-Feature Morphological Rule Confidence — sorted by {focal_np}",
                 fontsize=12, fontweight="bold")
    _save(out_dir / "t2c_morphological_feature_confidence.png")


# ══════════════════════════════════════════════════════════════════════════════
# TASK 3 — Aggregate + cross-NP
# ══════════════════════════════════════════════════════════════════════════════

def t3a_complexity_summary(np_dirs: dict, out_dir: Path) -> None:
    frames = []
    for n in NEWSPAPERS:
        df = _csv(np_dirs[n] / "accumulated" / "accumulated_complexity.csv")
        if df is not None:
            df["newspaper"] = n; frames.append(df)
    if not frames:
        return
    combined = pd.concat(frames)
    combined = combined[combined["level_name"].isin(LEVEL_ORDER)]
    agg = (combined.groupby("level_name")
           [["level_entropy_canonical", "level_entropy_headline"]]
           .mean().reset_index())
    agg["lbl"] = agg["level_name"].map(LEVEL_LBL)
    agg = agg.set_index("level_name").reindex(
        [l for l in LEVEL_ORDER if l in agg["level_name"].values]).reset_index()

    x = np.arange(len(agg)); w = 0.35
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - w/2, agg["level_entropy_canonical"], w, label="Canonical",
           color="#1976D2", alpha=0.88)
    ax.bar(x + w/2, agg["level_entropy_headline"],  w, label="Headline",
           color="#F57C00", alpha=0.88)
    ax.set_xticks(x); ax.set_xticklabels(agg["lbl"].values, fontsize=9)
    ax.set_ylabel("Mean entropy (bits)"); ax.legend(fontsize=9)
    ax.set_title("Complexity per Level — All Newspapers Aggregate\n"
                 "(averaged across ToI + HT + TH)", fontsize=12, fontweight="bold")
    _save(out_dir / "t3a_complexity_summary.png")


def t3a_similarity_summary(np_dirs: dict, out_dir: Path) -> None:
    frames = []
    for n in NEWSPAPERS:
        df = _csv(np_dirs[n] / "similarity" / "bidirectional_metrics.csv")
        if df is not None:
            df["newspaper"] = n; frames.append(df)
    if not frames:
        return
    combined = pd.concat(frames)
    combined = combined[combined["level"].isin(LEVEL_ORDER)]
    agg = (combined.groupby("level")
           [["js_similarity", "kl_divergence_C2H", "kl_divergence_H2C"]]
           .mean().reset_index())
    agg["lbl"] = agg["level"].map(LEVEL_LBL)
    agg = agg.set_index("level").reindex(
        [l for l in LEVEL_ORDER if l in agg["level"].values]).reset_index()

    x = np.arange(len(agg)); w = 0.25
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - w,    agg["js_similarity"],     w, label="JS Similarity", color="#43A047", alpha=0.88)
    ax.bar(x,        agg["kl_divergence_C2H"], w, label="KL C→H",        color="#E53935", alpha=0.88)
    ax.bar(x + w,    agg["kl_divergence_H2C"], w, label="KL H→C",        color="#8E24AA", alpha=0.88)
    ax.set_xticks(x); ax.set_xticklabels(agg["lbl"].values, fontsize=9)
    ax.set_ylabel("Mean value"); ax.legend(fontsize=9)
    ax.set_title("Similarity per Level — All Newspapers Aggregate\n"
                 "(averaged across ToI + HT + TH)", fontsize=12, fontweight="bold")
    _save(out_dir / "t3a_similarity_summary.png")


def t3a_accumulated_curves(np_dirs: dict, out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for i, n in enumerate(NEWSPAPERS):
        comp = _csv(np_dirs[n] / "accumulated" / "accumulated_complexity.csv")
        sim  = _csv(np_dirs[n] / "accumulated" / "accumulated_similarity.csv")
        if comp is not None:
            xs = range(len(comp))
            axes[0].plot(xs, comp["accumulated_entropy_canonical"], "o-", lw=2,
                         color=C3[i], label=f"{n} Canonical", markersize=5)
            axes[0].plot(xs, comp["accumulated_entropy_headline"], "s--", lw=1.5,
                         color=C3[i], alpha=0.6, label=f"{n} Headline", markersize=5)
            if i == 0:
                axes[0].set_xticks(xs)
                axes[0].set_xticklabels(comp["level_label"].values, fontsize=8.5)
        if sim is not None:
            xs = range(len(sim))
            axes[1].plot(xs, sim["accumulated_jaccard"], "o-", lw=2,
                         color=C3[i], label=f"{n} Jaccard", markersize=5)
            axes[1].plot(xs, sim["accumulated_js_similarity"], "s--", lw=1.5,
                         color=C3[i], alpha=0.6, label=f"{n} JS", markersize=5)
            if i == 0:
                axes[1].set_xticks(xs)
                axes[1].set_xticklabels(sim["level_label"].values, fontsize=8.5)
    axes[0].set_ylabel("Accumulated entropy (bits)"); axes[0].set_xlabel("Level")
    axes[0].legend(fontsize=7, ncol=2); axes[0].set_title("Accumulated Complexity", fontweight="bold")
    axes[1].set_ylabel("Accumulated similarity (0–1)"); axes[1].set_xlabel("Level")
    axes[1].set_ylim(0, 1.1); axes[1].legend(fontsize=7, ncol=2)
    axes[1].set_title("Accumulated Similarity", fontweight="bold")
    fig.suptitle("Accumulated Curves — All Newspapers Aggregate", fontsize=13, fontweight="bold")
    _save(out_dir / "t3a_accumulated_curves.png")


def t3c_complexity_ratio(np_dirs: dict, out_dir: Path) -> None:
    frames = []
    for n in NEWSPAPERS:
        df = _csv(np_dirs[n] / "accumulated" / "accumulated_complexity.csv")
        if df is None or "entropy_ratio_CH" not in df.columns:
            continue
        df = df[df["level_name"].isin(LEVEL_ORDER)].copy()
        df["lbl"] = df["level_name"].map(LEVEL_LBL); df["newspaper"] = n
        frames.append(df)
    if not frames:
        return
    combined = pd.concat(frames)
    levels = [LEVEL_LBL[l] for l in LEVEL_ORDER if l in combined["level_name"].values]
    pivot = (combined.pivot_table(index="lbl", columns="newspaper",
                                   values="entropy_ratio_CH", aggfunc="mean")
             .reindex([l for l in levels if l in
                       combined.pivot_table(index="lbl", columns="newspaper",
                                            values="entropy_ratio_CH").index]))

    x = np.arange(len(pivot)); w = 0.25
    fig, ax = plt.subplots(figsize=(11, 5))
    for i, n in enumerate(NEWSPAPERS):
        if n in pivot.columns:
            ax.bar(x + i * w, pivot[n].values, w, label=n, color=C3[i], alpha=0.87)
    ax.axhline(1.0, color="black", lw=1.2, ls="--", label="1.0 = equal")
    ax.set_xticks(x + w); ax.set_xticklabels(pivot.index, fontsize=9)
    ax.set_ylabel("Entropy ratio (Canonical / Headline)")
    ax.legend(title="Newspaper", fontsize=9)
    ax.set_title("Complexity Ratio per Level — Cross-Newspaper", fontsize=12, fontweight="bold")
    _save(out_dir / "t3c_complexity_ratio.png")


def t3c_similarity_profile(np_dirs: dict, out_dir: Path) -> None:
    frames = []
    for n in NEWSPAPERS:
        df = _csv(np_dirs[n] / "similarity" / "bidirectional_metrics.csv")
        if df is None:
            continue
        df_agg = (df.groupby("level")
                  [["js_similarity", "kl_divergence_C2H", "kl_divergence_H2C"]]
                  .mean().reset_index())
        df_agg["newspaper"] = n; frames.append(df_agg)
    if not frames:
        return
    combined = pd.concat(frames)
    levels = [LEVEL_LBL[l] for l in LEVEL_ORDER if l in combined["level"].values]
    combined["lbl"] = combined["level"].map(LEVEL_LBL)
    pivot_js = (combined.pivot_table(index="lbl", columns="newspaper",
                                      values="js_similarity", aggfunc="mean")
                .reindex([l for l in levels if l in combined["lbl"].values]))
    pivot_kl = (combined.pivot_table(index="lbl", columns="newspaper",
                                      values="kl_divergence_C2H", aggfunc="mean")
                .reindex(pivot_js.index))

    x = np.arange(len(pivot_js)); w = 0.25
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for i, n in enumerate(NEWSPAPERS):
        if n in pivot_js.columns:
            axes[0].bar(x + i * w, pivot_js[n].values, w, label=n, color=C3[i], alpha=0.87)
        if n in pivot_kl.columns:
            axes[1].bar(x + i * w, pivot_kl[n].values, w, label=n, color=C3[i], alpha=0.87)
    axes[0].set_ylim(0, 1.1)
    for ax, title, ylabel in [
        (axes[0], "JS Similarity",     "JS Similarity (0–1)"),
        (axes[1], "KL Divergence C→H", "KL Divergence (bits)"),
    ]:
        ax.set_xticks(x + w); ax.set_xticklabels(pivot_js.index, fontsize=9)
        ax.set_xlabel("Level"); ax.set_ylabel(ylabel)
        ax.legend(title="Newspaper", fontsize=8); ax.set_title(title, fontweight="bold")
    fig.suptitle("Similarity Profile — Cross-Newspaper", fontsize=13, fontweight="bold")
    _save(out_dir / "t3c_similarity_profile.png")


# ══════════════════════════════════════════════════════════════════════════════
# Task runners
# ══════════════════════════════════════════════════════════════════════════════

def run_task1():
    data_dirs = {n: S1 / "per-newspaper" / n for n in NEWSPAPERS}
    global_dir = O1 / "global"
    global_dir.mkdir(parents=True, exist_ok=True)

    # ── Aggregate overview ─────────────────────────────────────────────────────
    print("\n[Task-1] Aggregate overview → global/ …")
    t1a_feature_frequency(data_dirs, global_dir)
    t1a_category_distribution(data_dirs, global_dir)
    t1a_transformation_diversity(data_dirs, global_dir)
    t1a_top_value_pairs(data_dirs, global_dir)

    # Cross-NP overview (existing global functions)
    feat_frames = {}
    for n in NEWSPAPERS:
        df = _csv(data_dirs[n] / "feature_freq_global.csv")
        if df is not None:
            df["newspaper"] = n; feat_frames[n] = df
    gsv.t1g_feature_heatmap(feat_frames, global_dir)
    gsv.t1g_category_comparison(feat_frames, global_dir)
    gsv.t1g_morphological_features(
        S1 / "global" / "cross-newspaper-morphological"
           / "morphological_features_cross_newspaper.csv",
        global_dir)
    t1c_statistical_overview(data_dirs, global_dir)

    # ── Aggregate category-specific figures ────────────────────────────────────
    print("\n[Task-1] Aggregate category analysis → global/ …")
    _cat_fig(data_dirs, CONSTITUENCY, "Constituency Features",
             None, global_dir, "t1a_constituency", max_feats_per_fig=3)
    _cat_fig(data_dirs, DEPENDENCY, "Dependency Relations (DEP-REL-CHG)",
             None, global_dir, "t1a_dependency", max_trans=20, max_feats_per_fig=1)
    _morph_fig(data_dirs, None, global_dir)
    _cat_fig(data_dirs, POS, "POS Changes",
             None, global_dir, "t1a_pos", max_trans=20, max_feats_per_fig=1)
    _cat_fig(data_dirs, FUNC_WORD, "Function Word Changes",
             None, global_dir, "t1a_function_word", max_feats_per_fig=2)
    _cat_fig(data_dirs, PUNCTUATION, "Punctuation Changes",
             None, global_dir, "t1a_punctuation", max_feats_per_fig=3)
    _cat_fig(data_dirs, CONTENT_WORD, "Content Word Changes",
             None, global_dir, "t1a_content_word", max_feats_per_fig=3)
    _ted_fig(data_dirs, None, global_dir)

    # ── Per-newspaper cross-NP grouped-bar figures ─────────────────────────────
    for np_name in NEWSPAPERS:
        print(f"\n[Task-1] Cross-NP sorted by {np_name} …")
        np_dir = O1 / np_name
        np_dir.mkdir(parents=True, exist_ok=True)
        t1c_feature_frequency(data_dirs, np_name, np_dir)
        _cat_fig(data_dirs, CONSTITUENCY, "Constituency",
                 np_name, np_dir, "t1c_constituency", max_feats_per_fig=3)
        _cat_fig(data_dirs, DEPENDENCY, "Dependency Relations (DEP-REL-CHG)",
                 np_name, np_dir, "t1c_dependency", max_trans=15, max_feats_per_fig=1)
        _morph_fig(data_dirs, np_name, np_dir)
        _cat_fig(data_dirs, POS, "POS Changes",
                 np_name, np_dir, "t1c_pos", max_trans=15, max_feats_per_fig=1)
        _cat_fig(data_dirs, FUNC_WORD, "Function Word Changes",
                 np_name, np_dir, "t1c_function_word", max_feats_per_fig=2)
        _cat_fig(data_dirs, PUNCTUATION, "Punctuation Changes",
                 np_name, np_dir, "t1c_punctuation", max_feats_per_fig=3)
        _cat_fig(data_dirs, CONTENT_WORD, "Content Word Changes",
                 np_name, np_dir, "t1c_content_word", max_feats_per_fig=3)
        _ted_fig(data_dirs, np_name, np_dir)

    # ── Tables ────────────────────────────────────────────────────────────────
    print("\n[Task-1] Tables → global/tables/ …")
    n = _copy_tables(S1 / "morph-deprel-analysis" / "tables", global_dir / "tables")
    print(f"  {n} files.")


def run_task2():
    rules_dirs = {n: S2 / "per-newspaper" / n / "morphological-rules"
                  for n in NEWSPAPERS}
    global_dir = O2 / "global"
    global_dir.mkdir(parents=True, exist_ok=True)

    print("\n[Task-2] Aggregate figures → global/ …")
    t2a_rule_summary(rules_dirs, global_dir)

    print("\n[Task-2] Cross-newspaper comparison figures → global/ …")
    gsv.t2g_morphological_rules_aggregate(rules_dirs, global_dir)
    gsv.t2_bidirectional_rule_plots(
        S2 / "bidirectional-transformation" / "tables", global_dir)

    for np_name in NEWSPAPERS:
        print(f"\n[Task-2] Cross-NP sorted by {np_name} …")
        np_dir = O2 / np_name
        np_dir.mkdir(parents=True, exist_ok=True)
        t2c_morphological_rule_frequencies(rules_dirs, np_name, np_dir)
        t2c_morphological_feature_confidence(rules_dirs, np_name, np_dir)

    print("\n[Task-2] Tables → global/tables/ …")
    n = _copy_tables(S2 / "morph-deprel-analysis" / "tables", global_dir / "tables")
    n += _copy_tables(
        S2 / "bidirectional-transformation" / "tables",
        global_dir / "tables",
        names=["rule_coverage_analysis.csv", "rule_coverage_analysis.tex",
               "transformation_accuracy_by_newspaper.csv",
               "transformation_accuracy_by_newspaper.tex",
               "hypothesis_selection_stats.csv", "hypothesis_selection_stats.tex"])
    print(f"  {n} files.")


def run_task3():
    np_dirs = {n: S3 / "per-newspaper" / n for n in NEWSPAPERS}
    global_dir = O3 / "global"
    global_dir.mkdir(parents=True, exist_ok=True)

    print("\n[Task-3] Aggregate figures → global/ …")
    t3a_complexity_summary(np_dirs, global_dir)
    t3a_similarity_summary(np_dirs, global_dir)
    t3a_accumulated_curves(np_dirs, global_dir)

    print("\n[Task-3] Cross-newspaper comparison figures → global/ …")
    gsv.t3g_complexity_profile(np_dirs, global_dir)
    gsv.t3g_similarity_profile(np_dirs, global_dir)
    gsv.t3g_accumulated_curves(np_dirs, global_dir)
    gsv.t3g_heatmaps(np_dirs, global_dir)
    t3c_complexity_ratio(np_dirs, global_dir)
    t3c_similarity_profile(np_dirs, global_dir)

    for np_name in NEWSPAPERS:
        print(f"\n[Task-3] Cross-NP figures → {np_name}/ …")
        np_dir = O3 / np_name
        np_dir.mkdir(parents=True, exist_ok=True)
        # Task 3 figures are inherently cross-NP (no focal ordering needed)
        # Copy the global cross-NP figures into each NP dir as reference
        # (Task-3 has no NP-specific ordering dimension)

    print("\n[Task-3] Tables → global/tables/ …")
    n = _copy_tables(S3 / "morph-deprel-analysis" / "tables", global_dir / "tables")
    n += _copy_tables(
        S3 / "global", global_dir / "tables",
        names=["cross_newspaper_complexity.csv", "cross_newspaper_similarity.csv",
               "accumulated_levels_comparison.csv"])
    print(f"  {n} files.")


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("Minimal Output Generator  (focused, category-structured)")
    print("  global/       — aggregate + cross-NP overview")
    print("  <Newspaper>/  — cross-NP grouped-bar figures sorted by that NP")
    print(f"Source : {SRC.resolve()}")
    print(f"Output : {OUT.resolve()}")
    print("=" * 70)

    OUT.mkdir(parents=True, exist_ok=True)
    run_task1()
    run_task2()
    run_task3()

    figs = sorted(OUT.rglob("*.png"))
    tbls = sorted(OUT.rglob("*.csv"))
    tex  = sorted(OUT.rglob("*.tex"))
    print("\n" + "=" * 70)
    print("Done.")
    print(f"  {len(figs):3d} figures (.png)")
    print(f"  {len(tbls):3d} tables  (.csv)")
    print(f"  {len(tex):3d} tables  (.tex)")
    print(f"  Output : {OUT}/")
    print("=" * 70)


if __name__ == "__main__":
    main()
