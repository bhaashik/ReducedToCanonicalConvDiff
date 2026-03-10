"""
generate_fair_comparison_outputs.py
====================================
Creates per-task, per-stage tables and figures from pipeline outputs.

Stage subdirectories (inside each task's fair-comparison/ folder):
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

BAR_H = 0.42
FS    = 7
FM    = 8.5
FT    = 9.5
DPI   = 150
EPSILON = 1e-9


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


# ═══════════════════════════════════════════════════════════════════════════
# TASK 1 — Comparative Study
# ═══════════════════════════════════════════════════════════════════════════

def _t1_load(newspapers: list) -> dict:
    dfs = {}
    for np_name in newspapers:
        p = T1_DIR / "per-newspaper" / np_name / "events_fair.csv"
        if p.exists():
            dfs[np_name] = pd.read_csv(p)
        else:
            print(f"  [skip] events_fair.csv not found for {np_name}")
    return dfs


def _t1_stage(dfs, stage, cols_per_np, wide_col, title, xlabel,
              base_dir, use_abs, plot):
    for np_name, df in dfs.items():
        tbl = df[["feature_id", "level", "level_index"] + cols_per_np].copy()
        _tbl(tbl.sort_values("level_index"),
             base_dir / "tables" / f"{wide_col}_{np_name}.csv")
        if plot:
            fig = _hbar(df.rename(columns={"feature_id": "feature_id"}),
                        wide_col, title, xlabel,
                        use_abs=use_abs, newspaper=np_name)
            _save(fig, base_dir / "figures" / f"{wide_col}_{np_name}.png")
    wide = _wide_table(dfs, wide_col, "feature_id", ["level"])
    _tbl(wide, base_dir / "tables" / f"{wide_col}_cross_newspaper.csv")
    if plot and len(dfs) > 1:
        fig = _cross_np_grouped(
            {k: v.rename(columns={"feature_id": "feature_id"}) for k, v in dfs.items()},
            wide_col, "feature_id", title + " — All Newspapers", xlabel, use_abs=use_abs)
        _save(fig, base_dir / "figures" / f"{wide_col}_cross_newspaper.png")


def run_task1(newspapers: list, plot: bool) -> None:
    print("\n" + "=" * 60)
    print("  Task 1 — Comparative Study")
    print("=" * 60)
    dfs = _t1_load(newspapers)
    if not dfs:
        print("  [skip] no data found"); return
    base = T1_DIR / "fair-comparison"

    # Stage 1 — raw counts
    print("  Stage 1 — raw counts")
    d = base / STAGE_NAMES[1]
    _t1_stage(dfs, 1, ["eligible_site_name", "eligible_site_count", "count_raw"],
              "count_raw", "Raw Event Counts  (uncorrected)", "count_raw  (events)",
              d, False, plot)

    # Stage 2 — normalized rates
    print("  Stage 2 — normalized rates")
    d = base / STAGE_NAMES[2]
    _t1_stage(dfs, 2, ["eligible_site_name", "eligible_site_count", "rate_norm"],
              "rate_norm", "Opportunity-Normalized Event Rates",
              "rate_norm  (events / eligible sites)", d, False, plot)

    # Stage 3 — log₂
    print("  Stage 3 — log₂ normalized rates")
    d = base / STAGE_NAMES[3]
    _t1_stage(dfs, 3, ["rate_norm", "log2_norm"],
              "log2_norm", "Log₂ Normalized Rates  (|log₂(rate)|)",
              "|log₂(rate_norm)|", d, True, plot)
    if plot:
        # Level contribution stacked bar
        _save(_t1_level_contribution(dfs),
              d / "figures" / "level_contribution.png")

    # Stage 4 — weighted (level + IDF)
    print("  Stage 4 — weighted (level + IDF)")
    d = base / STAGE_NAMES[4]
    for score_col, wt_col, short_title, xl in [
        ("score_lvl", "weight_lvl", "Level-Weighted Score",
         "|score_lvl|  (|log₂(rate)·w_level|)"),
        ("score_idf", "weight_idf", "IDF-Weighted Score",
         "|score_idf|  (|log₂(rate)·w_IDF|)"),
    ]:
        cols = ["rate_norm", "log2_norm", wt_col, score_col]
        _t1_stage(dfs, 4, cols, score_col, short_title, xl, d, True, plot)
    if plot and len(dfs) > 1:
        _save(_t1_method_comparison(dfs, ["score_lvl", "score_idf"],
                                    ["Level", "IDF"]),
              d / "figures" / "level_vs_idf_cross_newspaper.png")

    # Stage 5 — information-theoretic (JSD + PMI)
    print("  Stage 5 — information-theoretic (JSD + PMI)")
    d = base / STAGE_NAMES[5]
    for score_col, wt_col, short_title, xl in [
        ("score_jsd", "weight_jsd", "JSD-Weighted Score",
         "|score_jsd|  (|log₂(rate)·JSD|)"),
        ("score_pmi", "weight_pmi", "PMI-Weighted Score",
         "|score_pmi|  (|log₂(rate)·PMI|)"),
    ]:
        if score_col not in next(iter(dfs.values())).columns:
            continue
        cols = ["log2_norm", wt_col, score_col]
        _t1_stage(dfs, 5, cols, score_col, short_title, xl, d, True, plot)
    if plot:
        for np_name, df in dfs.items():
            _save(_t1_all_methods_heatmap(df, np_name),
                  d / "figures" / f"all_methods_heatmap_{np_name}.png")
        if len(dfs) > 1:
            _save(_t1_all_methods_panel(dfs),
                  d / "figures" / "all_methods_panel_cross_newspaper.png")


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


def run_task2(newspapers: list, plot: bool) -> None:
    print("\n" + "=" * 60)
    print("  Task 2 — Transformation Study")
    print("=" * 60)
    raw_dfs  = _t2_load(newspapers)
    if not raw_dfs:
        print("  [skip] no data found"); return
    agg_dfs  = {np_name: _t2_aggregate(df) for np_name, df in raw_dfs.items()}
    base     = T2_DIR / "fair-comparison"

    def _stage(col, title, xl, stage_n, extra_cols, use_abs):
        d = base / STAGE_NAMES[stage_n]
        for np_name, df in agg_dfs.items():
            tbl = df[["feature"] + extra_cols].copy()
            _tbl(tbl.sort_values(col, ascending=False),
                 d / "tables" / f"{col}_{np_name}.csv")
            if plot:
                tmp = df.copy().rename(columns={"feature": "feature"})
                tmp["_lv"] = "morphological"
                fig = _hbar(tmp.rename(columns={"feature": "feature_id",
                                                "_lv": "level"}),
                            col, title, xl,
                            color_col="level", use_abs=use_abs,
                            newspaper=np_name)
                _save(fig, d / "figures" / f"{col}_{np_name}.png")
        wide = _wide_table(
            {k: v.rename(columns={"feature": "feature_id"}) for k, v in agg_dfs.items()},
            col, "feature_id", [])
        _tbl(wide, d / "tables" / f"{col}_cross_newspaper.csv")
        if plot and len(agg_dfs) > 1:
            tmp_dfs = {k: v.rename(columns={"feature": "feature_id"})
                       for k, v in agg_dfs.items()}
            fig = _cross_np_grouped(tmp_dfs, col, "feature_id",
                                    title + " — All Newspapers", xl, use_abs=use_abs)
            _save(fig, d / "figures" / f"{col}_cross_newspaper.png")

    print("  Stage 1 — raw rule frequencies")
    _stage("total_freq", "Morphological Rule Frequencies",
           "total_freq  (occurrences)", 1,
           ["total_freq", "n_rules", "avg_confidence", "avg_coverage"], False)

    print("  Stage 2 — normalized rates")
    _stage("rate_norm", "Normalised Rule Rates  (share of total morph events)",
           "rate_norm", 2,
           ["total_freq", "rate_norm"], False)

    print("  Stage 3 — log₂ rates")
    _stage("log2_norm", "Log₂ Normalised Rule Rates",
           "|log₂(rate_norm)|", 3,
           ["rate_norm", "log2_norm"], True)

    print("  Stage 4 — confidence-weighted")
    _stage("score_conf",
           "Confidence-Weighted Log₂ Rate  (|log₂ × avg_confidence|)",
           "|score_conf|", 4,
           ["log2_norm", "avg_confidence", "score_conf"], True)
    # Also produce coverage-weighted in stage 4
    _stage("score_cov",
           "Coverage-Weighted Log₂ Rate  (|log₂ × avg_coverage|)",
           "|score_cov|", 4,
           ["log2_norm", "avg_coverage", "score_cov"], True)

    print("  Stage 5 — information-theoretic (rule entropy)")
    _stage("rule_entropy",
           "Rule Distribution Entropy  (within-feature diversity)",
           "entropy  (bits)", 5,
           ["rule_entropy"], False)
    _stage("score_entropy",
           "Entropy-Weighted Log₂ Rate  (|log₂ × rule_entropy|)",
           "|score_entropy|", 5,
           ["log2_norm", "rule_entropy", "score_entropy"], True)


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


def run_task3(newspapers: list, plot: bool) -> None:
    print("\n" + "=" * 60)
    print("  Task 3 — Complexity & Similarity Study")
    print("=" * 60)
    raw   = _t3_load(newspapers)
    if not raw:
        print("  [skip] no data found"); return
    sums  = _t3_build_summary(raw)
    base  = T3_DIR / "fair-comparison"

    # ── Stage 1: raw metrics (canonical + headline side by side) ──────────
    print("  Stage 1 — raw complexity metrics (canonical vs headline)")
    d = base / STAGE_NAMES[1]
    for np_name, df in sums.items():
        tbl = df[["sublevel_id", "level", "metric", "canonical", "headline"]].copy()
        _tbl(tbl, d / "tables" / f"raw_metrics_{np_name}.csv")
        if plot:
            _save(_t3_grouped_reg_chart(
                df, "canonical", "headline",
                "Raw Complexity Metrics  (canonical vs headline)",
                "metric value", np_name),
                d / "figures" / f"raw_metrics_{np_name}.png")
    # cross-NP: canonical values only
    wide_c = _wide_table(sums, "canonical", "sublevel_id", ["level", "metric"])
    wide_h = _wide_table(sums, "headline",  "sublevel_id", ["level", "metric"])
    _tbl(wide_c, d / "tables" / "raw_canonical_cross_newspaper.csv")
    _tbl(wide_h, d / "tables" / "raw_headline_cross_newspaper.csv")
    if plot and len(sums) > 1:
        _save(_cross_np_grouped(
            {k: v.rename(columns={"sublevel_id": "feature_id"}) for k, v in sums.items()},
            "canonical", "feature_id",
            "Canonical Complexity — All Newspapers", "canonical metric value"),
            d / "figures" / "raw_canonical_cross_newspaper.png")
        _save(_cross_np_grouped(
            {k: v.rename(columns={"sublevel_id": "feature_id"}) for k, v in sums.items()},
            "headline", "feature_id",
            "Headline Complexity — All Newspapers", "headline metric value"),
            d / "figures" / "raw_headline_cross_newspaper.png")

    # ── Stage 2: normalized ratio ─────────────────────────────────────────
    print("  Stage 2 — canonical / headline ratio")
    d = base / STAGE_NAMES[2]
    for np_name, df in sums.items():
        tbl = df[["sublevel_id", "level", "metric", "canonical", "headline", "rate_norm"]]
        _tbl(tbl, d / "tables" / f"ratio_{np_name}.csv")
        if plot:
            tmp = df.copy().rename(columns={"sublevel_id": "feature_id"})
            fig = _hbar(tmp, "rate_norm",
                        "Complexity Ratio  (canonical / headline)",
                        "ratio  (>1 means canonical more complex)",
                        color_col="level", newspaper=np_name)
            _save(fig, d / "figures" / f"ratio_{np_name}.png")
    wide = _wide_table(sums, "rate_norm", "sublevel_id", ["level", "metric"])
    _tbl(wide, d / "tables" / "ratio_cross_newspaper.csv")
    if plot and len(sums) > 1:
        _save(_cross_np_grouped(
            {k: v.rename(columns={"sublevel_id": "feature_id"}) for k, v in sums.items()},
            "rate_norm", "feature_id",
            "Complexity Ratio — All Newspapers", "canonical / headline"),
            d / "figures" / "ratio_cross_newspaper.png")

    # ── Stage 3: log₂ ratio ───────────────────────────────────────────────
    print("  Stage 3 — log₂(canonical / headline) ratio")
    d = base / STAGE_NAMES[3]
    for np_name, df in sums.items():
        tbl = df[["sublevel_id", "level", "metric", "rate_norm", "log2_norm"]]
        _tbl(tbl, d / "tables" / f"log2_ratio_{np_name}.csv")
        if plot:
            tmp = df.copy().rename(columns={"sublevel_id": "feature_id"})
            fig = _hbar(tmp, "log2_norm",
                        "Log₂ Complexity Ratio  (bits advantage of canonical)",
                        "log₂(canonical / headline)  (bits)",
                        color_col="level", newspaper=np_name)
            _save(fig, d / "figures" / f"log2_ratio_{np_name}.png")
    wide = _wide_table(sums, "log2_norm", "sublevel_id", ["level", "metric"])
    _tbl(wide, d / "tables" / "log2_ratio_cross_newspaper.csv")
    if plot and len(sums) > 1:
        _save(_cross_np_grouped(
            {k: v.rename(columns={"sublevel_id": "feature_id"}) for k, v in sums.items()},
            "log2_norm", "feature_id",
            "Log₂ Complexity Ratio — All Newspapers",
            "log₂(canonical / headline)"),
            d / "figures" / "log2_ratio_cross_newspaper.png")

    # ── Stage 4: level-weighted ───────────────────────────────────────────
    print("  Stage 4 — level-weighted log₂ ratio")
    d = base / STAGE_NAMES[4]
    for np_name, df in sums.items():
        tbl = df[["sublevel_id", "level", "metric", "log2_norm",
                  "weight_lvl", "score_lvl"]]
        _tbl(tbl, d / "tables" / f"level_weighted_{np_name}.csv")
        if plot:
            tmp = df.copy().rename(columns={"sublevel_id": "feature_id"})
            fig = _hbar(tmp, "score_lvl",
                        "Level-Weighted Complexity Score  (log₂ ratio × w_level)",
                        "score_lvl", color_col="level", newspaper=np_name)
            _save(fig, d / "figures" / f"level_weighted_{np_name}.png")
    wide = _wide_table(sums, "score_lvl", "sublevel_id", ["level", "metric"])
    _tbl(wide, d / "tables" / "level_weighted_cross_newspaper.csv")
    if plot and len(sums) > 1:
        _save(_cross_np_grouped(
            {k: v.rename(columns={"sublevel_id": "feature_id"}) for k, v in sums.items()},
            "score_lvl", "feature_id",
            "Level-Weighted Complexity Score — All Newspapers", "score_lvl"),
            d / "figures" / "level_weighted_cross_newspaper.png")

    # ── Stage 5: information-theoretic (JSD) ─────────────────────────────
    print("  Stage 5 — information-theoretic (JSD, KL from bidirectional metrics)")
    d = base / STAGE_NAMES[5]
    # Per-NP: JSD and KL tables from bidirectional_metrics.csv
    for np_name, data in raw.items():
        sim = data["similarity"]
        if sim.empty:
            continue
        _tbl(sim, d / "tables" / f"bidirectional_metrics_{np_name}.csv")
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
                _save(fig, d / "figures" / f"{col}_{np_name}.png")
    # JSD-weighted score from complexity summary
    for np_name, df in sums.items():
        if df["jsd"].notna().any():
            tbl = df[["sublevel_id", "level", "metric",
                      "log2_norm", "jsd", "score_jsd"]]
            _tbl(tbl, d / "tables" / f"jsd_weighted_{np_name}.csv")
            if plot:
                tmp = df.copy().rename(columns={"sublevel_id": "feature_id"})
                fig = _hbar(tmp, "score_jsd",
                            "JSD-Weighted Complexity Score",
                            "score_jsd  (|log₂(ratio) × JSD|)",
                            color_col="level", use_abs=True, newspaper=np_name)
                _save(fig, d / "figures" / f"jsd_weighted_{np_name}.png")
    # Cross-NP JSD
    wide = _wide_table(sums, "jsd", "sublevel_id", ["level"])
    _tbl(wide, d / "tables" / "jsd_cross_newspaper.csv")
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
                    _save(fig, d / "figures" / f"{col}_cross_newspaper.png")


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
