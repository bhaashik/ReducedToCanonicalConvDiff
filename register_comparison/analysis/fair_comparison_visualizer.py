"""
fair_comparison_visualizer.py
=============================
Visualizations for the fair-comparison analysis.

Figures produced per newspaper
-------------------------------
1. log2_raw_counts          — log2 of raw event counts (reference baseline)
2. normalized_rates         — opportunity-normalized rates (linear scale)
3. log2_normalized_rates    — log2 of normalized rates (main comparable view)
4. level_weighted           — log2_norm × level weight  (absolute value)
5. idf_weighted             — log2_norm × IDF weight    (absolute value)
6. jsd_weighted             — log2_norm × JSD weight    (if JSD computed)
7. pmi_weighted             — log2_norm × PMI weight    (if PMI computed)

Cross-newspaper figures (global)
---------------------------------
8. cross_np_normalized_rates  — grouped bars: rate_norm per feature × newspaper
9. cross_np_log2_normalized   — grouped bars: log2_norm per feature × newspaper
10. level_contribution         — stacked bar: share of abs(log2_norm) per level

Design
------
- Horizontal bar charts; features ordered by score (descending absolute value)
- Features colour-coded by linguistic level
- Consistent with project colour palette and matplotlib style
"""

import sys
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LEVEL_COLORS = {
    "morphological": "#7B1FA2",   # purple
    "lexical":       "#1976D2",   # blue
    "punctuation":   "#0097A7",   # teal
    "dependency":    "#E65100",   # deep orange
    "constituency":  "#E53935",   # red
    "typological":   "#558B2F",   # green
    "structural":    "#546E7A",   # blue-grey
}

LEVEL_ORDER = [
    "morphological", "lexical", "punctuation",
    "dependency", "constituency", "typological", "structural",
]

NEWSPAPER_COLORS = {
    "Times-of-India":   "#1976D2",
    "Hindustan-Times":  "#E53935",
    "The-Hindu":        "#2E7D32",
}

BAR_HEIGHT   = 0.45
FONT_SMALL   = 7
FONT_MEDIUM  = 8.5
FONT_TITLE   = 9.5


def _level_legend(ax):
    patches = [
        mpatches.Patch(color=LEVEL_COLORS[l], label=l.capitalize())
        for l in LEVEL_ORDER if l in LEVEL_COLORS
    ]
    ax.legend(handles=patches, fontsize=FONT_SMALL, loc="lower right",
              framealpha=0.7, ncol=2)


def _save(fig, path: Path, dpi: int = 150):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {path.name}")


# ---------------------------------------------------------------------------
# Single-newspaper horizontal bar charts
# ---------------------------------------------------------------------------

def _hbar_figure(
    df: pd.DataFrame,
    value_col: str,
    title: str,
    xlabel: str,
    use_abs: bool = False,
    newspaper: str = "",
) -> plt.Figure:
    """
    Generic horizontal bar chart sorted by |value| descending.
    Features colour-coded by linguistic level.
    """
    plot_df = df.copy()
    plot_df["_val"] = plot_df[value_col].abs() if use_abs else plot_df[value_col]
    plot_df = plot_df.dropna(subset=["_val"]).sort_values("_val", ascending=True)

    n = len(plot_df)
    fig_h = max(3.5, n * BAR_HEIGHT + 1.5)
    fig, ax = plt.subplots(figsize=(9, fig_h))

    colors = [LEVEL_COLORS.get(lv, "#999999") for lv in plot_df["level"]]
    bars = ax.barh(plot_df["feature_id"], plot_df["_val"], color=colors,
                   height=0.6, edgecolor="white", linewidth=0.4)

    # Value labels at bar ends
    for bar, val in zip(bars, plot_df["_val"]):
        w = bar.get_width()
        ax.text(w + abs(w) * 0.02, bar.get_y() + bar.get_height() / 2,
                f"{val:.4f}", va="center", ha="left", fontsize=FONT_SMALL)

    np_label = f" — {newspaper}" if newspaper else ""
    ax.set_title(f"{title}{np_label}", fontsize=FONT_TITLE, pad=8)
    ax.set_xlabel(xlabel, fontsize=FONT_MEDIUM)
    ax.tick_params(axis="y", labelsize=FONT_SMALL)
    ax.tick_params(axis="x", labelsize=FONT_SMALL)
    ax.spines[["top", "right"]].set_visible(False)
    _level_legend(ax)
    fig.tight_layout()
    return fig


def plot_log2_raw_counts(df: pd.DataFrame, out_dir: Path, newspaper: str = ""):
    """Log2 of raw event counts (reference baseline; no normalization)."""
    tmp = df.copy()
    tmp["log2_raw"] = np.log2(tmp["count_raw"].clip(lower=1e-9))
    fig = _hbar_figure(tmp, "log2_raw",
                       "Log₂ of Raw Event Counts (reference)",
                       "log₂(count_raw)", newspaper=newspaper)
    _save(fig, out_dir / "log2_raw_counts.png")


def plot_normalized_rates(df: pd.DataFrame, out_dir: Path, newspaper: str = ""):
    """Opportunity-normalized rates (linear scale)."""
    fig = _hbar_figure(df, "rate_norm",
                       "Opportunity-Normalized Event Rates",
                       "rate_norm  (events / eligible sites)",
                       newspaper=newspaper)
    _save(fig, out_dir / "normalized_rates.png")


def plot_log2_normalized(df: pd.DataFrame, out_dir: Path, newspaper: str = ""):
    """Log₂ of normalized rates — main comparable view; displayed as |value|."""
    fig = _hbar_figure(df, "log2_norm",
                       "Log₂ Normalized Rates  (|log₂(rate)|)",
                       "|log₂(rate_norm)|",
                       use_abs=True, newspaper=newspaper)
    _save(fig, out_dir / "log2_normalized_rates.png")


def plot_level_weighted(df: pd.DataFrame, out_dir: Path, newspaper: str = ""):
    if "score_lvl" not in df.columns:
        return
    fig = _hbar_figure(df, "score_lvl",
                       "Level-Weighted Score  (|log₂(rate) × w_level|)",
                       "|score_lvl|", use_abs=True, newspaper=newspaper)
    _save(fig, out_dir / "level_weighted.png")


def plot_idf_weighted(df: pd.DataFrame, out_dir: Path, newspaper: str = ""):
    if "score_idf" not in df.columns:
        return
    fig = _hbar_figure(df, "score_idf",
                       "IDF-Weighted Score  (|log₂(rate) × w_IDF|)",
                       "|score_idf|", use_abs=True, newspaper=newspaper)
    _save(fig, out_dir / "idf_weighted.png")


def plot_jsd_weighted(df: pd.DataFrame, out_dir: Path, newspaper: str = ""):
    if "score_jsd" not in df.columns:
        return
    fig = _hbar_figure(df, "score_jsd",
                       "JSD-Weighted Score  (|log₂(rate) × JSD|)",
                       "|score_jsd|", use_abs=True, newspaper=newspaper)
    _save(fig, out_dir / "jsd_weighted.png")


def plot_pmi_weighted(df: pd.DataFrame, out_dir: Path, newspaper: str = ""):
    if "score_pmi" not in df.columns:
        return
    fig = _hbar_figure(df, "score_pmi",
                       "PMI-Weighted Score  (|log₂(rate) × PMI|)",
                       "|score_pmi|", use_abs=True, newspaper=newspaper)
    _save(fig, out_dir / "pmi_weighted.png")


def plot_all_single_np(df: pd.DataFrame, out_dir: Path, newspaper: str = ""):
    """Produce all single-newspaper figures."""
    plot_log2_raw_counts(df, out_dir, newspaper)
    plot_normalized_rates(df, out_dir, newspaper)
    plot_log2_normalized(df, out_dir, newspaper)
    plot_level_weighted(df, out_dir, newspaper)
    plot_idf_weighted(df, out_dir, newspaper)
    plot_jsd_weighted(df, out_dir, newspaper)
    plot_pmi_weighted(df, out_dir, newspaper)


# ---------------------------------------------------------------------------
# Cross-newspaper figures (global)
# ---------------------------------------------------------------------------

def plot_cross_np_grouped(
    dfs: dict,           # {newspaper_name: summary_df}
    value_col: str,
    title: str,
    xlabel: str,
    out_path: Path,
    use_abs: bool = False,
):
    """
    Grouped horizontal bar chart: one group of bars per feature,
    one bar per newspaper, coloured by newspaper.
    Features sorted by mean |value| across newspapers.
    """
    newspapers = list(dfs.keys())
    all_features = sorted(
        set.union(*[set(df["feature_id"]) for df in dfs.values()])
    )
    # Sort by mean absolute value across newspapers
    mean_vals = {}
    for fid in all_features:
        vals = []
        for df in dfs.values():
            row = df[df["feature_id"] == fid]
            if not row.empty:
                v = abs(row[value_col].iloc[0]) if use_abs else row[value_col].iloc[0]
                vals.append(v)
        mean_vals[fid] = np.mean(vals) if vals else 0.0
    all_features = sorted(all_features, key=lambda f: mean_vals[f])

    n_feat = len(all_features)
    n_np   = len(newspapers)
    group_h = BAR_HEIGHT * n_np + 0.15
    fig_h   = max(4.0, n_feat * group_h + 1.5)
    fig, ax = plt.subplots(figsize=(10, fig_h))

    y_base = np.arange(n_feat)
    offsets = np.linspace(-(n_np - 1) / 2, (n_np - 1) / 2, n_np) * BAR_HEIGHT

    for i, (np_name, df) in enumerate(dfs.items()):
        vals = []
        for fid in all_features:
            row = df[df["feature_id"] == fid]
            v = row[value_col].iloc[0] if not row.empty else 0.0
            vals.append(abs(v) if use_abs else v)
        color = NEWSPAPER_COLORS.get(np_name, "#888888")
        ax.barh(y_base + offsets[i], vals, height=BAR_HEIGHT * 0.85,
                color=color, label=np_name, edgecolor="white", linewidth=0.3)

    ax.set_yticks(y_base)
    ax.set_yticklabels(all_features, fontsize=FONT_SMALL)
    ax.set_title(title, fontsize=FONT_TITLE, pad=8)
    ax.set_xlabel(xlabel, fontsize=FONT_MEDIUM)
    ax.tick_params(axis="x", labelsize=FONT_SMALL)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=FONT_SMALL, loc="lower right", framealpha=0.7)
    fig.tight_layout()
    _save(fig, out_path)


def plot_level_contribution(dfs: dict, out_path: Path):
    """
    Stacked horizontal bar chart showing what fraction of total |log2_norm|
    comes from each linguistic level, per newspaper.
    """
    newspapers = list(dfs.keys())
    # Compute per-level absolute sum of log2_norm for each newspaper
    records = []
    for np_name, df in dfs.items():
        for lv in LEVEL_ORDER:
            sub = df[df["level"] == lv]
            total = sub["log2_norm"].abs().sum()
            records.append({"newspaper": np_name, "level": lv, "abs_log2": total})
    rec_df = pd.DataFrame(records)

    fig, ax = plt.subplots(figsize=(9, 3.5))
    bottoms = np.zeros(len(newspapers))
    np_idx  = {n: i for i, n in enumerate(newspapers)}

    for lv in LEVEL_ORDER:
        vals = []
        for np_name in newspapers:
            row = rec_df[(rec_df["newspaper"] == np_name) & (rec_df["level"] == lv)]
            vals.append(row["abs_log2"].iloc[0] if not row.empty else 0.0)
        ax.barh(newspapers, vals, left=bottoms,
                color=LEVEL_COLORS.get(lv, "#999999"),
                label=lv.capitalize(), edgecolor="white", linewidth=0.4)
        bottoms += np.array(vals)

    ax.set_title("Level Contribution to Total |log₂ Normalized Rate|",
                 fontsize=FONT_TITLE, pad=8)
    ax.set_xlabel("Sum of |log₂(rate_norm)| per level", fontsize=FONT_MEDIUM)
    ax.tick_params(labelsize=FONT_SMALL)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=FONT_SMALL, loc="lower right", framealpha=0.7, ncol=2)
    fig.tight_layout()
    _save(fig, out_path)
