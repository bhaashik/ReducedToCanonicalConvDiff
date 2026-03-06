#!/usr/bin/env python3
"""
generate_supplementary_visualizations.py
=========================================
Config-driven visualization generator for all three tasks.

Every figure type is implemented as a single function that accepts
(data, newspaper_label, out_path). The same function is called for
each newspaper and for the global (all-newspapers-combined) scope,
guaranteeing structural identity across newspapers.

After generating figures the script writes:
  output/figures_config.json
  output/tables_config.json

Usage:
  python generate_supplementary_visualizations.py
"""

import json
import warnings
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ── paths ─────────────────────────────────────────────────────────────────────
NEWSPAPERS = ["Times-of-India", "Hindustan-Times", "The-Hindu"]
OUT  = Path("output")
T1   = OUT / "task-1-comparative-study"
T2   = OUT / "task-2-transformation-study"
T3   = OUT / "task-3-complexity-similarity-study"

# Consistent colour palette
C3   = ["#1976D2", "#E53935", "#2E7D32"]   # blue / red / green — one per newspaper
NP_C = dict(zip(NEWSPAPERS, C3))

LEVEL_ORDER = ["character", "token", "morphological", "dependency", "constituency"]
LEVEL_LBL   = {"character":"L1 Char","token":"L2 Token",
                "morphological":"L3 Morph","dependency":"L4 Dep",
                "constituency":"L5 Const"}

# Category mapping for schema features
CAT = {
    "FW-DEL":"Lexical","FW-ADD":"Lexical","LEMMA-CHG":"Lexical",
    "FORM-CHG":"Morphological","FEAT-CHG":"Morphological",
    "POS-CHG":"Morphological","VERB-FORM-CHG":"Morphological",
    "DEP-REL-CHG":"Dependency","HEAD-CHG":"Dependency",
    "DEP-DIST-DIFF":"Dependency","TOKEN-REORDER":"Dependency",
    "CONST-MOV":"Structural","CONST-ADD":"Structural",
    "CONST-REM":"Structural","C-ADD":"Structural","C-DEL":"Structural",
    "CLAUSE-TYPE-CHG":"Structural","BRANCH-DIFF":"Structural",
    "CONST-COUNT-DIFF":"Structural","TREE-DEPTH-DIFF":"Structural",
    "H-TYPE":"Headline","H-STRUCT":"Headline",
    "PUNCT-ADD":"Punctuation","PUNCT-DEL":"Punctuation","PUNCT-SUBST":"Punctuation",
    "TED-SIMPLE":"TED","TED-RTED":"TED","TED-ZHANG-SHASHA":"TED","TED-KLEIN":"TED",
    "LENGTH-CHG":"Length",
}
CAT_COLORS = {
    "Lexical":"#1B5E20","Morphological":"#F57F17","Dependency":"#1A237E",
    "Structural":"#880E4F","Headline":"#4A148C","Punctuation":"#BF360C",
    "TED":"#006064","Length":"#37474F","Other":"#757575",
}

# ── catalogue registry (filled by make_entry) ─────────────────────────────────
_FIGURE_REGISTRY: list[dict] = []
_TABLE_REGISTRY:  list[dict] = []

def _reg_fig(id_, task, scope, np_name, filename, title,
             description, x_label, y_label, fig_type,
             data_sources, notes=""):
    _FIGURE_REGISTRY.append({
        "id": id_, "task": task, "scope": scope, "newspaper": np_name,
        "filename": filename,
        "path": str(filename),
        "title": title, "description": description,
        "x_label": x_label, "y_label": y_label,
        "figure_type": fig_type, "data_sources": data_sources,
        "notes": notes,
    })

def _reg_tbl(id_, task, scope, np_name, filename, title, description, notes=""):
    _TABLE_REGISTRY.append({
        "id": id_, "task": task, "scope": scope, "newspaper": np_name,
        "filename": filename,
        "path": str(filename),
        "title": title, "description": description, "notes": notes,
    })

# ── helpers ───────────────────────────────────────────────────────────────────
def _save(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  saved → {path.relative_to(OUT)}")

def _short(text, n=20):
    s = str(text)
    return s[:n] + "…" if len(s) > n else s

def _csv(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    try:
        df = pd.read_csv(path)
        return df if not df.empty else None
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════════════
# ── TASK 1 figure functions ───────────────────────────────────────────────────
# Each function has the same signature: (data_dir, label, out_dir) → saves PNG
# ══════════════════════════════════════════════════════════════════════════════

def t1_feature_frequency(data_dir: Path, label: str, out_dir: Path):
    """Horizontal bar — top-20 features by event count."""
    df = _csv(data_dir / "feature_freq_global.csv")
    if df is None: return
    df = df.sort_values("count", ascending=False).head(20)
    df["category"] = df["feature_id"].map(CAT).fillna("Other")
    colors = [CAT_COLORS.get(c, "#757575") for c in df["category"]]

    fig, ax = plt.subplots(figsize=(10, 8))
    bars = ax.barh(df["feature_id"][::-1], df["count"][::-1],
                   color=colors[::-1], alpha=0.87, edgecolor="white")
    for bar, v in zip(bars, df["count"][::-1]):
        ax.text(v + df["count"].max() * 0.01, bar.get_y() + bar.get_height()/2,
                f"{int(v):,}", va="center", fontsize=8)
    # legend for categories
    seen = {}
    for cat, col in CAT_COLORS.items():
        if cat in df["category"].values and cat not in seen:
            seen[cat] = plt.Rectangle((0,0), 1, 1, fc=col, alpha=0.87)
    ax.legend(seen.values(), seen.keys(), title="Category",
              fontsize=8, loc="lower right")
    ax.set_xlabel("Event count (total instances in corpus)")
    ax.set_ylabel("Feature ID (schema v5.0)")
    ax.set_title(f"{label} — Feature Event Frequency (Top 20)",
                 fontsize=12, fontweight="bold")
    _save(out_dir / "t1_feature_frequency.png")

def t1_feature_category_distribution(data_dir: Path, label: str, out_dir: Path):
    """Stacked/grouped bar of event counts per category."""
    df = _csv(data_dir / "feature_freq_global.csv")
    if df is None: return
    df["category"] = df["feature_id"].map(CAT).fillna("Other")
    cat_totals = df.groupby("category")["count"].sum().sort_values(ascending=False)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Left: bar by category
    ax = axes[0]
    colors = [CAT_COLORS.get(c, "#757575") for c in cat_totals.index]
    bars = ax.bar(range(len(cat_totals)), cat_totals.values, color=colors, alpha=0.87)
    for bar, v in zip(bars, cat_totals.values):
        ax.text(bar.get_x() + bar.get_width()/2, v + cat_totals.max()*0.01,
                f"{int(v):,}", ha="center", fontsize=8)
    ax.set_xticks(range(len(cat_totals)))
    ax.set_xticklabels(cat_totals.index, rotation=35, ha="right", fontsize=9)
    ax.set_xlabel("Feature category")
    ax.set_ylabel("Total event count")
    ax.set_title(f"{label}\nEvent Counts by Feature Category",
                 fontsize=11, fontweight="bold")

    # Right: donut chart
    ax = axes[1]
    wedge_colors = [CAT_COLORS.get(c, "#757575") for c in cat_totals.index]
    wedges, texts, autotexts = ax.pie(
        cat_totals.values, labels=cat_totals.index, colors=wedge_colors,
        autopct=lambda p: f"{p:.1f}%" if p > 3 else "",
        startangle=90, pctdistance=0.8,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5})
    for t in autotexts: t.set_fontsize(8)
    ax.set_title(f"{label}\nEvent Proportion by Category",
                 fontsize=11, fontweight="bold")

    _save(out_dir / "t1_feature_category_distribution.png")

def t1_top_transformations_grid(data_dir: Path, label: str, out_dir: Path):
    """2×3 grid: top-5 value-pair transformations for each of the top-6 features."""
    feat_df = _csv(data_dir / "feature_freq_global.csv")
    trans_df = _csv(data_dir / "feature_value_analysis_global_transformations.csv")
    if feat_df is None or trans_df is None: return

    top6_features = feat_df.sort_values("count", ascending=False).head(6)["feature_id"].tolist()
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.flatten()

    for idx, feat in enumerate(top6_features):
        ax = axes[idx]
        sub = trans_df[trans_df["feature_id"] == feat].nlargest(8, "count")
        if sub.empty:
            ax.set_visible(False)
            continue
        cat = CAT.get(feat, "Other")
        color = CAT_COLORS.get(cat, "#757575")
        labels = [_short(r["canonical_value"]) + "→" + _short(r["headline_value"], 12)
                  for _, r in sub.iterrows()]
        bars = ax.barh(labels[::-1], sub["count"].values[::-1],
                       color=color, alpha=0.87, edgecolor="white")
        for bar, v in zip(bars, sub["count"].values[::-1]):
            ax.text(v + sub["count"].max()*0.02, bar.get_y() + bar.get_height()/2,
                    f"{int(v):,}", va="center", fontsize=7.5)
        ax.set_xlabel("Event count")
        ax.set_title(f"{feat} ({cat})", fontsize=10, fontweight="bold",
                     color=color)
        ax.tick_params(axis="y", labelsize=8)

    for i in range(len(top6_features), 6):
        axes[i].set_visible(False)

    fig.suptitle(f"{label} — Top Transformations for Each of the 6 Most Frequent Features",
                 fontsize=13, fontweight="bold")
    _save(out_dir / "t1_top_transformations_grid.png")

def t1_transformation_diversity(data_dir: Path, label: str, out_dir: Path):
    """Two panels: transformation entropy and top-3 concentration per feature."""
    df = _csv(data_dir / "feature_value_analysis_value_statistics.csv")
    if df is None: return
    df = df[df["transformation_entropy"].notna()].sort_values("transformation_entropy", ascending=False)
    df["category"] = df["feature_id"].map(CAT).fillna("Other")
    colors = [CAT_COLORS.get(c, "#757575") for c in df["category"]]

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # Left: entropy
    ax = axes[0]
    bars = ax.barh(df["feature_id"][::-1], df["transformation_entropy"][::-1],
                   color=colors[::-1], alpha=0.87, edgecolor="white")
    ax.set_xlabel("Transformation entropy (bits) — higher = more diverse transformations")
    ax.set_ylabel("Feature ID (schema v5.0)")
    ax.set_title(f"{label}\nTransformation Diversity (Entropy)",
                 fontsize=11, fontweight="bold")

    # Right: top-3 concentration (1 = one dominant transformation)
    ax = axes[1]
    bars = ax.barh(df["feature_id"][::-1], df["top3_concentration_ratio"][::-1],
                   color=colors[::-1], alpha=0.87, edgecolor="white")
    ax.axvline(0.8, color="grey", lw=0.9, ls="--", alpha=0.6,
               label="0.8 concentration threshold")
    ax.set_xlabel("Top-3 pair concentration ratio (1 = single dominant transformation)")
    ax.set_ylabel("Feature ID (schema v5.0)")
    ax.set_title(f"{label}\nTransformation Concentration (Top-3 pairs)",
                 fontsize=11, fontweight="bold")
    ax.legend(fontsize=9)

    _save(out_dir / "t1_transformation_diversity.png")

def t1_parse_type_breakdown(data_dir: Path, label: str, out_dir: Path):
    """Stacked bar of feature event counts by parse type (dependency / constituency)."""
    df = _csv(data_dir / "comprehensive_analysis_by_parse_type.csv")
    if df is None: return

    pivot = df.pivot_table(index="feature_id", columns="parse_type",
                           values="count", aggfunc="sum", fill_value=0)
    pivot["total"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("total", ascending=False).head(20).drop(columns="total")

    fig, ax = plt.subplots(figsize=(11, 7))
    parse_colors = {"dependency":"#1565C0","constituency":"#558B2F",
                    "combined":"#F57F17","both":"#F57F17"}
    bottom = np.zeros(len(pivot))
    for pt in pivot.columns:
        col = parse_colors.get(pt, "#90A4AE")
        ax.barh(range(len(pivot)), pivot[pt].values,
                left=bottom, label=pt.capitalize(), color=col, alpha=0.87)
        bottom += pivot[pt].values

    ax.set_yticks(range(len(pivot)))
    ax.set_yticklabels(pivot.index, fontsize=9)
    ax.set_xlabel("Event count")
    ax.set_ylabel("Feature ID (schema v5.0)")
    ax.set_title(f"{label} — Feature Counts by Parse Type (Top 20 features)",
                 fontsize=11, fontweight="bold")
    ax.legend(title="Parse type", fontsize=9)
    _save(out_dir / "t1_parse_type_breakdown.png")

def t1_top_value_pairs(data_dir: Path, label: str, out_dir: Path):
    """Horizontal bar of top-25 feature-value pairs."""
    df = _csv(data_dir / "feature_value_pair_analysis_top_pairs.csv")
    if df is None: return
    df = df.head(25)
    df["feature"] = df["pair_unit"].str.split(":").str[0]
    df["category"] = df["feature"].map(CAT).fillna("Other")
    colors = [CAT_COLORS.get(c, "#757575") for c in df["category"]]

    fig, ax = plt.subplots(figsize=(11, 9))
    bars = ax.barh(df["pair_unit"][::-1], df["frequency"][::-1],
                   color=colors[::-1], alpha=0.87, edgecolor="white")
    for bar, v in zip(bars, df["frequency"][::-1]):
        ax.text(v + df["frequency"].max()*0.01, bar.get_y() + bar.get_height()/2,
                f"{int(v):,}", va="center", fontsize=7.5)
    ax.set_xlabel("Frequency (occurrence count in corpus)")
    ax.set_ylabel("Feature-value pair (feature_id:canonical→headline)")
    ax.set_title(f"{label} — Top-25 Feature-Value Pairs",
                 fontsize=11, fontweight="bold")
    ax.tick_params(axis="y", labelsize=7.5)
    # legend for categories
    seen = {}
    for cat, col in CAT_COLORS.items():
        if cat in df["category"].values and cat not in seen:
            seen[cat] = plt.Rectangle((0,0), 1, 1, fc=col, alpha=0.87)
    ax.legend(seen.values(), seen.keys(), title="Category",
              fontsize=8, loc="lower right")
    _save(out_dir / "t1_top_value_pairs.png")

def t1_per_feature_analysis(data_dir: Path, label: str, out_dir: Path):
    """One figure per schema feature: bar chart of canonical→headline transformations."""
    trans_dir = out_dir / "feature_analysis"
    trans_dir.mkdir(parents=True, exist_ok=True)
    feat_df = _csv(data_dir / "feature_freq_global.csv")
    if feat_df is None: return

    for _, row in feat_df.iterrows():
        fid = row["feature_id"]
        fname = data_dir / f"feature_value_analysis_feature_{fid}.csv"
        df = _csv(fname)
        if df is None: continue

        df = df.sort_values("count", ascending=False).head(15)
        df["label"] = df["canonical_value"].apply(_short) + "→" + df["headline_value"].apply(_short)
        cat = CAT.get(fid, "Other")
        color = CAT_COLORS.get(cat, "#757575")

        fig, ax = plt.subplots(figsize=(10, max(4, len(df)*0.45 + 1)))
        bars = ax.barh(df["label"][::-1], df["count"][::-1],
                       color=color, alpha=0.87, edgecolor="white")
        for bar, v in zip(bars, df["count"][::-1]):
            pct = f"  {df.loc[df['count']==v,'percentage'].values[0]:.1f}%"
            ax.text(v + df["count"].max()*0.01, bar.get_y() + bar.get_height()/2,
                    f"{int(v):,}{pct}", va="center", fontsize=8)
        ax.set_xlabel("Event count  (percentage of feature total annotated)")
        ax.set_ylabel("Transformation (canonical value → headline value)")
        ax.set_title(f"{label} — {fid}: {row.get('name', fid)}\nTransformation Distribution",
                     fontsize=11, fontweight="bold", color=color)
        _save(trans_dir / f"feature_{fid}.png")

def t1_statistical_overview(data_dir: Path, label: str, out_dir: Path):
    """Scatter: total occurrences vs. percentage, bubble = parse-type coverage."""
    df = _csv(data_dir / "statistical_summary_features.csv")
    if df is None: return
    df = df[df["total_occurrences"] > 0].copy()
    df["category"] = df["feature_id"].map(CAT).fillna("Other")
    colors = [CAT_COLORS.get(c, "#757575") for c in df["category"]]

    fig, ax = plt.subplots(figsize=(11, 7))
    sc = ax.scatter(df["total_occurrences"], df["percentage_of_total"],
                    c=colors, s=80, alpha=0.85, edgecolors="white", linewidth=0.8)
    for _, row in df.iterrows():
        ax.annotate(row["feature_id"],
                    (row["total_occurrences"], row["percentage_of_total"]),
                    textcoords="offset points", xytext=(4, 3), fontsize=7.5)
    ax.set_xlabel("Total event occurrences in corpus (log scale)")
    ax.set_ylabel("Percentage of total events (%)")
    ax.set_xscale("log")
    ax.set_title(f"{label} — Feature Occurrences vs. Percentage of Total Events",
                 fontsize=11, fontweight="bold")
    seen = {}
    for cat, col in CAT_COLORS.items():
        if cat in df["category"].values and cat not in seen:
            seen[cat] = plt.scatter([], [], c=col, alpha=0.87, label=cat)
    ax.legend(seen.values(), seen.keys(), title="Category", fontsize=8)
    _save(out_dir / "t1_statistical_overview.png")


# ── Task 1 global functions (cross-newspaper) ─────────────────────────────────

def t1g_feature_frequency(frames: dict, out_dir: Path):
    """Grouped bar — top-15 features by total count, all newspapers."""
    combined = pd.concat(list(frames.values()), ignore_index=True)
    top15 = (combined.groupby("feature_id")["count"].sum()
             .nlargest(15).index.tolist())

    fig, ax = plt.subplots(figsize=(14, 6))
    x = np.arange(len(top15)); w = 0.25
    for i, np_name in enumerate(NEWSPAPERS):
        if np_name not in frames: continue
        df_np = frames[np_name].set_index("feature_id")
        counts = [int(df_np.loc[f,"count"]) if f in df_np.index else 0 for f in top15]
        ax.bar(x + i*w, counts, w, label=np_name, color=C3[i], alpha=0.87)
    ax.set_xticks(x + w); ax.set_xticklabels(top15, rotation=40, ha="right", fontsize=9)
    ax.set_xlabel("Feature ID (schema v5.0 mnemonic)")
    ax.set_ylabel("Event count (total corpus instances)")
    ax.set_title("Top-15 Transformation Features — Cross-Newspaper Comparison",
                 fontsize=12, fontweight="bold")
    ax.legend(title="Newspaper", fontsize=9)
    _save(out_dir / "t1g_feature_frequency.png")

def t1g_feature_heatmap(frames: dict, out_dir: Path):
    """Normalised heatmap — features × newspapers."""
    combined = pd.concat(list(frames.values()), ignore_index=True)
    top15 = (combined.groupby("feature_id")["count"].sum()
             .nlargest(15).index.tolist())
    pivot = (combined[combined["feature_id"].isin(top15)]
             .pivot_table(index="feature_id", columns="newspaper",
                          values="count", aggfunc="sum", fill_value=0))
    pivot = pivot.reindex(top15)
    norm  = pivot.div(pivot.sum(axis=0))

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(norm.values, aspect="auto", cmap="YlOrRd")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, fontsize=9)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=9)
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Column-normalised frequency\n(share of each newspaper's total events)", fontsize=9)
    ax.set_xlabel("Newspaper")
    ax.set_ylabel("Feature ID (schema v5.0)")
    ax.set_title("Feature Frequency Heatmap — Cross-Newspaper (Column-Normalised)",
                 fontsize=12, fontweight="bold")
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            v = norm.values[i,j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    fontsize=7.5, color="white" if v > 0.45 else "black")
    _save(out_dir / "t1g_feature_heatmap.png")

def t1g_category_comparison(frames: dict, out_dir: Path):
    """Stacked bar of event counts per category, all newspapers."""
    combined = pd.concat(list(frames.values()), ignore_index=True)
    combined["category"] = combined["feature_id"].map(CAT).fillna("Other")
    pivot = (combined.groupby(["newspaper","category"])["count"]
             .sum().unstack(fill_value=0))
    cats = sorted(CAT_COLORS.keys(), key=lambda c: pivot[c].sum() if c in pivot.columns else 0, reverse=True)
    cats = [c for c in cats if c in pivot.columns]

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    ax = axes[0]
    bottom = np.zeros(len(pivot))
    for cat in cats:
        ax.bar(range(len(pivot)), pivot[cat].values, bottom=bottom,
               label=cat, color=CAT_COLORS[cat], alpha=0.87)
        bottom += pivot[cat].values
    ax.set_xticks(range(len(pivot)))
    ax.set_xticklabels(pivot.index, fontsize=10)
    ax.set_xlabel("Newspaper")
    ax.set_ylabel("Total event count")
    ax.set_title("Event Counts by Feature Category — All Newspapers",
                 fontsize=11, fontweight="bold")
    ax.legend(title="Category", fontsize=8, loc="upper right")

    ax = axes[1]
    norm = pivot[cats].div(pivot[cats].sum(axis=1), axis=0)
    bottom = np.zeros(len(norm))
    for cat in cats:
        ax.bar(range(len(norm)), norm[cat].values, bottom=bottom,
               label=cat, color=CAT_COLORS[cat], alpha=0.87)
        bottom += norm[cat].values
    ax.set_xticks(range(len(norm)))
    ax.set_xticklabels(norm.index, fontsize=10)
    ax.set_xlabel("Newspaper")
    ax.set_ylabel("Proportion of total events (0–1)")
    ax.set_title("Event Proportions by Feature Category — All Newspapers",
                 fontsize=11, fontweight="bold")
    ax.legend(title="Category", fontsize=8, loc="upper right")

    _save(out_dir / "t1g_category_comparison.png")

def t1g_transformation_diversity(data_dirs: dict, out_dir: Path):
    """Cross-newspaper transformation entropy comparison."""
    frames = {}
    for np_name, d in data_dirs.items():
        df = _csv(d / "feature_value_analysis_value_statistics.csv")
        if df is not None:
            df["newspaper"] = np_name
            frames[np_name] = df
    if not frames: return
    combined = pd.concat(list(frames.values()), ignore_index=True)
    top10 = (combined.groupby("feature_id")["transformation_entropy"]
             .mean().nlargest(10).index.tolist())
    pivot = combined[combined["feature_id"].isin(top10)].pivot_table(
        index="feature_id", columns="newspaper",
        values="transformation_entropy", aggfunc="mean", fill_value=0)
    pivot = pivot.reindex([f for f in top10 if f in pivot.index])

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(pivot)); w = 0.25
    for i, np_name in enumerate(NEWSPAPERS):
        if np_name not in pivot.columns: continue
        ax.bar(x + i*w, pivot[np_name].values, w,
               label=np_name, color=C3[i], alpha=0.87)
    ax.set_xticks(x + w)
    ax.set_xticklabels(pivot.index, rotation=35, ha="right", fontsize=9)
    ax.set_xlabel("Feature ID (schema v5.0)")
    ax.set_ylabel("Transformation entropy (bits) — higher = more varied transformations")
    ax.set_title("Transformation Diversity (Entropy) — Cross-Newspaper Comparison",
                 fontsize=12, fontweight="bold")
    ax.legend(title="Newspaper", fontsize=9)
    _save(out_dir / "t1g_transformation_diversity.png")

def t1g_parse_type_breakdown(data_dirs: dict, out_dir: Path):
    """Cross-newspaper parse-type feature breakdown."""
    frames = {}
    for np_name, d in data_dirs.items():
        df = _csv(d / "comprehensive_analysis_by_parse_type.csv")
        if df is not None:
            df["newspaper"] = np_name
            frames[np_name] = df
    if not frames: return
    combined = pd.concat(list(frames.values()), ignore_index=True)
    pt_totals = combined.groupby(["newspaper","parse_type"])["count"].sum().unstack(fill_value=0)

    parse_colors = {"dependency":"#1565C0","constituency":"#558B2F",
                    "combined":"#F57F17","both":"#F57F17"}

    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(pt_totals)); bottom = np.zeros(len(pt_totals))
    for pt in pt_totals.columns:
        col = parse_colors.get(pt, "#90A4AE")
        ax.bar(x, pt_totals[pt].values, bottom=bottom,
               label=pt.capitalize(), color=col, alpha=0.87)
        bottom += pt_totals[pt].values
    ax.set_xticks(x)
    ax.set_xticklabels(pt_totals.index, fontsize=10)
    ax.set_xlabel("Newspaper")
    ax.set_ylabel("Total event count (summed across all features)")
    ax.set_title("Event Counts by Parse Type — Cross-Newspaper",
                 fontsize=12, fontweight="bold")
    ax.legend(title="Parse type", fontsize=9)
    _save(out_dir / "t1g_parse_type_breakdown.png")

def t1g_morphological_features(morph_csv: Path, out_dir: Path):
    """Morphological feature cross-newspaper bubble chart + bar."""
    df = _csv(morph_csv)
    if df is None: return

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    df_s = df.sort_values("total_instances", ascending=False).head(12)
    axes[0].barh(df_s["feature"][::-1], df_s["total_instances"][::-1],
                 color="#7986CB", alpha=0.9, edgecolor="white")
    axes[0].set_xlabel("Total morphological feature instances across all newspapers")
    axes[0].set_ylabel("Morphological feature (CoNLL-U FEATS category)")
    axes[0].set_title("Morphological Feature Instances\n(all newspapers combined)",
                      fontsize=11, fontweight="bold")

    axes[1].scatter(df["newspaper_count"], df["total_rules"],
                    s=df["total_instances"]/df["total_instances"].max()*500+20,
                    alpha=0.75, color="#FF8A65", edgecolors="grey", linewidth=0.5)
    for _, row in df.iterrows():
        axes[1].annotate(row["feature"],
                         (row["newspaper_count"], row["total_rules"]),
                         textcoords="offset points", xytext=(5, 2), fontsize=8)
    axes[1].set_xlabel("Number of newspapers containing this feature (1–3)")
    axes[1].set_ylabel("Number of distinct transformation rules extracted")
    axes[1].set_title("Rule Generalisability vs. Newspaper Coverage\n"
                      "(bubble size ∝ total instances)",
                      fontsize=11, fontweight="bold")
    _save(out_dir / "t1g_morphological_features.png")


# ══════════════════════════════════════════════════════════════════════════════
# ── TASK 2 figure functions ───────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

def t2_morphological_rules(rules_dir: Path, label: str, out_dir: Path):
    """Four morphological-rule figures for one newspaper."""
    df = _csv(rules_dir / "morphological_rules.csv")
    if df is None: return
    df = df.sort_values("frequency", ascending=False)
    df["label"] = (df["feature"] + ": "
                   + df["transformation"].apply(lambda x: _short(x, 26)))

    # Figure A: confidence + coverage (top 20)
    top = df.head(20).copy()
    fig, ax = plt.subplots(figsize=(13, 7))
    x = np.arange(len(top)); w = 0.35
    ax.bar(x - w/2, top["confidence"], w,
           label="Confidence (0–1)", color="#42A5F5", alpha=0.9)
    ax.bar(x + w/2, top["coverage"] / 100, w,
           label="Coverage (normalised to 0–1)", color="#EF5350", alpha=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels(top["label"], rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Score (0 – 1)")
    ax.set_ylim(0, 1.2)
    ax.axhline(0.5, color="grey", lw=0.8, ls="--", alpha=0.5,
               label="0.5 reference line")
    ax.set_xlabel("Morphological transformation rule (feature: canonical→headline)")
    ax.set_title(f"{label} — Morphological Rule Confidence & Coverage (Top 20)",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=9)
    _save(out_dir / "t2_morphological_rule_confidence_coverage.png")

    # Figure B: frequency bar (top 20)
    fig, ax = plt.subplots(figsize=(13, 5))
    ax.barh(top["label"][::-1], top["frequency"][::-1],
            color="#66BB6A", alpha=0.9, edgecolor="white")
    ax.set_xlabel("Frequency (total corpus instances matching this rule)")
    ax.set_ylabel("Morphological transformation rule (feature: canonical→headline)")
    ax.set_title(f"{label} — Morphological Rule Frequencies (Top 20)",
                 fontsize=12, fontweight="bold")
    _save(out_dir / "t2_morphological_rule_frequencies.png")

    # Figure C: transformation matrices (canonical→headline) per morphological feature
    features = df["feature"].unique()
    ncols = min(3, len(features)); nrows = (len(features)+ncols-1)//ncols
    fig, axes = plt.subplots(nrows, ncols,
                              figsize=(5*ncols, 4*nrows), squeeze=False)
    for idx, feat in enumerate(features):
        ax = axes[idx//ncols][idx%ncols]
        sub = df[df["feature"]==feat]
        pivot = sub.pivot_table(index="canonical_value", columns="headline_value",
                                values="frequency", fill_value=0)
        if pivot.empty: ax.set_visible(False); continue
        im = ax.imshow(pivot.values, cmap="Blues", aspect="auto")
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels([_short(c,10) for c in pivot.columns], rotation=35, ha="right", fontsize=8)
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels([_short(r,10) for r in pivot.index], fontsize=8)
        ax.set_title(feat, fontsize=10, fontweight="bold")
        ax.set_xlabel("Headline value", fontsize=8)
        ax.set_ylabel("Canonical value", fontsize=8)
        vmax = pivot.values.max()
        for i in range(pivot.values.shape[0]):
            for j in range(pivot.values.shape[1]):
                v = pivot.values[i,j]
                if v > 0:
                    ax.text(j, i, str(int(v)), ha="center", va="center",
                            fontsize=8, color="white" if vmax>0 and v/vmax>0.55 else "black")
    for idx in range(len(features), nrows*ncols):
        axes[idx//ncols][idx%ncols].set_visible(False)
    fig.suptitle(f"{label} — Morphological Transformation Matrices\n"
                 "(rows = canonical value, columns = headline value, cells = frequency)",
                 fontsize=12, fontweight="bold")
    _save(out_dir / "t2_morphological_transformation_matrices.png")

    # Figure D: per-feature confidence summary
    feat_summary = (df.groupby("feature")
                    .agg(avg_conf=("confidence","mean"),
                         avg_cov=("coverage","mean"),
                         n_rules=("transformation","count"))
                    .reset_index().sort_values("avg_conf", ascending=False))
    colors = plt.cm.RdYlGn(feat_summary["avg_conf"].values)
    fig, ax = plt.subplots(figsize=(8, max(4, len(feat_summary)*0.6+1)))
    ax.barh(feat_summary["feature"][::-1], feat_summary["avg_conf"][::-1],
            color=colors[::-1], alpha=0.9, edgecolor="white")
    for _, row in feat_summary.iterrows():
        ax.text(row["avg_conf"]+0.01,
                list(feat_summary["feature"][::-1]).index(row["feature"]),
                f"n={int(row['n_rules'])}  cov={row['avg_cov']:.0f}%",
                va="center", fontsize=8)
    ax.set_xlim(0, 1.3)
    ax.axvline(0.5, color="grey", lw=0.8, ls="--", alpha=0.5,
               label="0.5 confidence threshold")
    ax.set_xlabel("Average rule confidence (0 = unreliable, 1 = perfectly reliable)")
    ax.set_ylabel("Morphological feature (CoNLL-U FEATS category)")
    ax.set_title(f"{label} — Per-Feature Rule Confidence Summary\n"
                 "(colour: green=high, red=low; annotated with rule count and avg coverage)",
                 fontsize=11, fontweight="bold")
    ax.legend(fontsize=9)
    _save(out_dir / "t2_morphological_feature_confidence_summary.png")


def t2g_morphological_rules_aggregate(data_dirs: dict, out_dir: Path):
    """Global: cross-newspaper rule inventory and confidence comparison."""
    all_frames = {}
    for np_name, rules_dir in data_dirs.items():
        df = _csv(rules_dir / "morphological_rules.csv")
        if df is not None:
            df["newspaper"] = np_name
            all_frames[np_name] = df
    if not all_frames: return
    combined = pd.concat(list(all_frames.values()), ignore_index=True)

    # Global inventory: aggregated confidence per feature
    feat_agg = (combined.groupby(["feature","newspaper"])
                .agg(avg_conf=("confidence","mean"),
                     n_rules=("transformation","count"),
                     total_freq=("frequency","sum"))
                .reset_index())

    features = (combined.groupby("feature")["frequency"].sum()
                .sort_values(ascending=False).index.tolist())
    pivot_conf = feat_agg.pivot_table(index="feature", columns="newspaper",
                                      values="avg_conf", fill_value=np.nan)
    pivot_conf = pivot_conf.reindex([f for f in features if f in pivot_conf.index])

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Grouped bar: avg confidence per feature per newspaper
    ax = axes[0]
    x = np.arange(len(pivot_conf)); w = 0.25
    for i, np_name in enumerate(NEWSPAPERS):
        if np_name not in pivot_conf.columns: continue
        vals = pivot_conf[np_name].values
        mask = ~np.isnan(vals)
        ax.bar(x[mask] + i*w, vals[mask], w,
               label=np_name, color=C3[i], alpha=0.87)
    ax.set_xticks(x + w)
    ax.set_xticklabels(pivot_conf.index, rotation=35, ha="right", fontsize=9)
    ax.axhline(0.5, color="grey", lw=0.8, ls="--", alpha=0.5)
    ax.set_xlabel("Morphological feature (CoNLL-U FEATS category)")
    ax.set_ylabel("Average rule confidence (0–1)")
    ax.set_title("Cross-Newspaper Rule Confidence\nby Morphological Feature",
                 fontsize=11, fontweight="bold")
    ax.legend(title="Newspaper", fontsize=9)

    # Rule count per newspaper
    ax = axes[1]
    rule_counts = feat_agg.groupby("newspaper")["n_rules"].sum()
    bars = ax.bar(range(len(rule_counts)), rule_counts.values,
                  color=[NP_C.get(n,"#90A4AE") for n in rule_counts.index], alpha=0.87)
    for bar, v in zip(bars, rule_counts.values):
        ax.text(bar.get_x()+bar.get_width()/2, v+0.5, str(int(v)),
                ha="center", fontsize=10)
    ax.set_xticks(range(len(rule_counts)))
    ax.set_xticklabels(rule_counts.index, fontsize=10)
    ax.set_xlabel("Newspaper")
    ax.set_ylabel("Total number of distinct morphological rules extracted")
    ax.set_title("Morphological Rule Inventory Size\nby Newspaper",
                 fontsize=11, fontweight="bold")

    _save(out_dir / "t2g_morphological_rules_aggregate.png")


def t2_bidirectional_rule_plots(tables_dir: Path, out_dir: Path):
    """Rule inventory + confidence figures for bidirectional transformation."""
    p = tables_dir / "rule_coverage_analysis.csv"
    df = _csv(p)
    if df is None: return

    rule_cols = ["feature_rules","deletion_rules","form_rules","structural_rules"]
    nice = {"feature_rules":"Feature","deletion_rules":"Deletion",
            "form_rules":"Form","structural_rules":"Structural"}
    rule_colors = ["#1976D2","#EF6C00","#2E7D32","#6A1B9A"]
    df["total_rules"] = df[rule_cols].sum(axis=1)

    for direction in ["C2R","R2C"]:
        sub = df[df["direction"]==direction].copy()
        if sub.empty: continue

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        x = np.arange(len(sub))

        # Stacked rule-type bar
        ax = axes[0]
        bottom = np.zeros(len(sub))
        for col, nice_name, col_color in zip(rule_cols, nice.values(), rule_colors):
            ax.bar(x, sub[col].values, bottom=bottom,
                   label=nice_name, color=col_color, alpha=0.87)
            bottom += sub[col].values
        ax.set_xticks(x); ax.set_xticklabels(sub["newspaper"].values, fontsize=10)
        ax.set_xlabel("Newspaper")
        ax.set_ylabel("Rule count (stacked by type)")
        ax.set_title(f"Rule Inventory by Type — {direction} Direction",
                     fontsize=11, fontweight="bold")
        ax.legend(title="Rule type", fontsize=9)

        # Confidence bar
        ax = axes[1]
        bar_c = [NP_C.get(n,"#90A4AE") for n in sub["newspaper"].values]
        bars = ax.bar(x, sub["avg_confidence"].values, color=bar_c, alpha=0.87)
        for bar, v in zip(bars, sub["avg_confidence"].values):
            ax.text(bar.get_x()+bar.get_width()/2, v+0.005, f"{v:.3f}",
                    ha="center", fontsize=9)
        ax.set_xticks(x); ax.set_xticklabels(sub["newspaper"].values, fontsize=10)
        ax.set_ylim(0, 0.8)
        ax.axhline(0.5, color="grey", lw=0.8, ls="--", alpha=0.5,
                   label="0.5 reference")
        ax.set_xlabel("Newspaper")
        ax.set_ylabel("Average rule confidence (0–1)")
        ax.set_title(f"Average Rule Confidence — {direction} Direction",
                     fontsize=11, fontweight="bold")
        ax.legend(fontsize=9)
        _save(out_dir / f"t2_bidirectional_rule_inventory_{direction}.png")

    # C2R vs R2C comparison
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    ax = axes[0]
    for direction, marker, ls, col in [("C2R","o","-","#1976D2"),("R2C","s","--","#E53935")]:
        sub = df[df["direction"]==direction]
        ax.plot(sub["newspaper"].values, sub["avg_confidence"].values,
                marker=marker, ls=ls, lw=2, markersize=9, label=direction, color=col)
        for _, row in sub.iterrows():
            ax.annotate(f"{row['avg_confidence']:.3f}",
                        (row["newspaper"], row["avg_confidence"]),
                        textcoords="offset points", xytext=(4,4), fontsize=8)
    ax.set_ylabel("Average rule confidence (0–1)")
    ax.set_xlabel("Newspaper")
    ax.set_ylim(0.4, 0.7)
    ax.axhline(0.5, color="grey", lw=0.8, ls="--", alpha=0.5)
    ax.set_title("Rule Confidence: C2R vs R2C\nAll Newspapers",
                 fontsize=11, fontweight="bold")
    ax.legend(title="Direction", fontsize=9)

    ax = axes[1]
    for direction, marker, ls, col in [("C2R","o","-","#1976D2"),("R2C","s","--","#E53935")]:
        sub = df[df["direction"]==direction]
        ax.plot(sub["newspaper"].values, sub["total_rules"].values,
                marker=marker, ls=ls, lw=2, markersize=9, label=direction, color=col)
    ax.set_ylabel("Total extracted rules (feature + deletion + form + structural)")
    ax.set_xlabel("Newspaper")
    ax.set_title("Total Extracted Rules: C2R vs R2C\nAll Newspapers",
                 fontsize=11, fontweight="bold")
    ax.legend(title="Direction", fontsize=9)
    _save(out_dir / "t2_bidirectional_rule_comparison.png")


# ══════════════════════════════════════════════════════════════════════════════
# ── TASK 3 figure functions ───────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

def t3_complexity_profile(np_dir: Path, label: str, out_dir: Path):
    df = _csv(np_dir / "accumulated" / "accumulated_complexity.csv")
    if df is None: return
    df = df[df["level_name"].isin(LEVEL_ORDER)].copy()
    df["lbl"] = df["level_name"].map(LEVEL_LBL)
    x = np.arange(len(df)); w = 0.35

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, col_c, col_h, ylabel, subtitle in [
        (axes[0], "level_entropy_canonical", "level_entropy_headline",
         "Entropy (bits) — Shannon entropy of the unit distribution",
         "Per-Level Entropy"),
        (axes[1], "level_diversity_canonical", "level_diversity_headline",
         "Diversity (normalised TTR / MATTR proxy)",
         "Per-Level Diversity"),
    ]:
        ax.bar(x-w/2, df[col_c], w, label="Canonical", color="#1976D2", alpha=0.88)
        ax.bar(x+w/2, df[col_h], w, label="Headline",  color="#F57C00", alpha=0.88)
        ax.set_xticks(x); ax.set_xticklabels(df["lbl"], fontsize=9)
        ax.set_xlabel("Analysis level (L1 = character, L5 = constituency)")
        ax.set_ylabel(ylabel)
        ax.set_title(f"{label}\n{subtitle}", fontsize=11, fontweight="bold")
        ax.legend(title="Register", fontsize=9)
    _save(out_dir / "t3_complexity_profile.png")

def t3_complexity_ratio(np_dir: Path, label: str, out_dir: Path):
    df = _csv(np_dir / "accumulated" / "accumulated_complexity.csv")
    if df is None or "entropy_ratio_CH" not in df.columns: return
    df = df[df["level_name"].isin(LEVEL_ORDER)].copy()
    df["lbl"] = df["level_name"].map(LEVEL_LBL)
    colors = ["#2E7D32" if v > 1 else "#C62828" for v in df["entropy_ratio_CH"]]
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(range(len(df)), df["entropy_ratio_CH"], color=colors, alpha=0.88)
    ax.axhline(1.0, color="black", lw=1.2, ls="--",
               label="1.0 = equal complexity")
    for xi, v in enumerate(df["entropy_ratio_CH"]):
        ax.text(xi, v + (0.003 if v>1 else -0.008),
                f"{v:.3f}", ha="center", fontsize=8.5)
    ax.set_xticks(range(len(df))); ax.set_xticklabels(df["lbl"], fontsize=9)
    ax.set_xlabel("Analysis level (L1 = character, L5 = constituency)")
    ax.set_ylabel("Entropy ratio (Canonical / Headline)\n>1 = canonical more complex")
    ax.set_title(f"{label} — Complexity Ratio per Level\n"
                 "(green = canonical more complex, red = headline more complex)",
                 fontsize=11, fontweight="bold")
    ax.legend(fontsize=9)
    _save(out_dir / "t3_complexity_ratio.png")

def t3_similarity_profile(np_dir: Path, label: str, out_dir: Path):
    df = _csv(np_dir / "similarity" / "bidirectional_metrics.csv")
    if df is None: return
    df_agg = (df.groupby("level")[["kl_divergence_C2H","kl_divergence_H2C",
                                    "js_similarity","wasserstein_distance"]]
              .mean().reset_index())
    order = [l for l in LEVEL_ORDER if l in df_agg["level"].values]
    df_agg = df_agg.set_index("level").loc[order].reset_index()
    df_agg["lbl"] = df_agg["level"].map(LEVEL_LBL)
    x = np.arange(len(df_agg)); w = 0.35

    fig, axes = plt.subplots(1, 3, figsize=(17, 5))

    ax = axes[0]
    ax.bar(x-w/2, df_agg["kl_divergence_C2H"], w,
           label="C→H (KL)", color="#E53935", alpha=0.88)
    ax.bar(x+w/2, df_agg["kl_divergence_H2C"], w,
           label="H→C (KL)", color="#8E24AA", alpha=0.88)
    ax.set_xticks(x); ax.set_xticklabels(df_agg["lbl"], fontsize=9)
    ax.set_xlabel("Analysis level")
    ax.set_ylabel("KL Divergence (bits) — larger = more distributional difference")
    ax.set_title(f"{label}\nDirectional KL Divergence", fontsize=11, fontweight="bold")
    ax.legend(title="Direction", fontsize=9)

    ax = axes[1]
    bars = ax.bar(x, df_agg["js_similarity"], color="#43A047", alpha=0.88)
    for bar, v in zip(bars, df_agg["js_similarity"]):
        ax.text(bar.get_x()+bar.get_width()/2, v+0.003, f"{v:.3f}",
                ha="center", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(df_agg["lbl"], fontsize=9)
    ax.set_ylim(0, 1.1)
    ax.axhline(1.0, color="grey", lw=0.8, ls="--", alpha=0.5, label="1.0 = identical")
    ax.set_xlabel("Analysis level")
    ax.set_ylabel("JS Similarity (0–1, higher = more similar)")
    ax.set_title(f"{label}\nJensen-Shannon Similarity", fontsize=11, fontweight="bold")
    ax.legend(fontsize=9)

    ax = axes[2]
    w_vals = df_agg["wasserstein_distance"].values
    wmax = w_vals.max()
    w_norm = w_vals/wmax if wmax > 0 else w_vals
    bars = ax.bar(x, w_norm, color="#039BE5", alpha=0.88)
    for xi, (vn, vr) in enumerate(zip(w_norm, w_vals)):
        ax.text(xi, vn+0.01, f"{vr:.2f}", ha="center", fontsize=7.5)
    ax.set_xticks(x); ax.set_xticklabels(df_agg["lbl"], fontsize=9)
    ax.set_ylim(0, 1.2)
    ax.set_xlabel("Analysis level")
    ax.set_ylabel("Wasserstein distance (panel-normalised; raw values annotated)")
    ax.set_title(f"{label}\nWasserstein Distance by Level", fontsize=11, fontweight="bold")

    _save(out_dir / "t3_similarity_profile.png")

def t3_accumulated_curves(np_dir: Path, label: str, out_dir: Path):
    comp = _csv(np_dir / "accumulated" / "accumulated_complexity.csv")
    sim  = _csv(np_dir / "accumulated" / "accumulated_similarity.csv")
    if comp is None or sim is None: return
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    ax = axes[0]
    xs = range(len(comp))
    ax.plot(xs, comp["accumulated_entropy_canonical"], "o-",
            lw=2.2, color="#1976D2", label="Canonical", markersize=7)
    ax.plot(xs, comp["accumulated_entropy_headline"], "s--",
            lw=2.2, color="#F57C00", label="Headline", markersize=7)
    ax.fill_between(xs, comp["accumulated_entropy_canonical"],
                    comp["accumulated_entropy_headline"],
                    alpha=0.12, color="grey",
                    label="Complexity gap")
    ax.set_xticks(xs); ax.set_xticklabels(comp["level_label"].values, fontsize=9)
    ax.set_xlabel("Analysis level (L1 = character, L5 = constituency)")
    ax.set_ylabel("Accumulated entropy (bits) — cumulative over levels L1…Lk")
    ax.set_title(f"{label}\nAccumulated Complexity Curve", fontsize=11, fontweight="bold")
    ax.legend(title="Register", fontsize=9)

    ax = axes[1]
    xs = range(len(sim))
    ax.plot(xs, sim["accumulated_jaccard"], "o-",
            lw=2.2, color="#43A047", label="Jaccard", markersize=7)
    ax.plot(xs, sim["accumulated_js_similarity"], "s--",
            lw=2.2, color="#7B1FA2", label="JS similarity", markersize=7)
    ax.set_xticks(xs); ax.set_xticklabels(sim["level_label"].values, fontsize=9)
    ax.set_ylim(0, 1.08)
    ax.axhline(1.0, color="grey", lw=0.8, ls="--", alpha=0.4)
    ax.set_xlabel("Analysis level (L1 = character, L5 = constituency)")
    ax.set_ylabel("Accumulated similarity (0–1) — averaged over levels L1…Lk")
    ax.set_title(f"{label}\nAccumulated Similarity Curve", fontsize=11, fontweight="bold")
    ax.legend(title="Metric", fontsize=9)

    _save(out_dir / "t3_accumulated_curves.png")

def t3_information_gain(np_dir: Path, label: str, out_dir: Path):
    df = _csv(np_dir / "accumulated" / "information_gain.csv")
    if df is None: return
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, col, reg in [(axes[0],"information_gain","Canonical"),
                          (axes[1],"information_gain_headline","Headline")]:
        vals = df[col].values
        colors = ["#2E7D32" if v >= 0 else "#C62828" for v in vals]
        bars = ax.bar(range(len(df)), vals, color=colors, alpha=0.88)
        ax.axhline(0, color="black", lw=0.8)
        for xi, v in enumerate(vals):
            ax.text(xi, v+(0.04 if v>=0 else -0.12), f"{v:.2f}",
                    ha="center", fontsize=8.5)
        ax.set_xticks(range(len(df)))
        ax.set_xticklabels(df["level_label"].values, fontsize=9, rotation=20)
        ax.set_xlabel("Analysis level")
        ax.set_ylabel("Information gain (entropy bits added by this level)\n"
                      "green = new information, red = redundancy")
        ax.set_title(f"{label}\nInformation Gain per Level ({reg})",
                     fontsize=11, fontweight="bold")
    _save(out_dir / "t3_information_gain.png")

def t3_directional_asymmetry(np_dir: Path, label: str, out_dir: Path):
    df = _csv(np_dir / "similarity" / "bidirectional_metrics.csv")
    if df is None: return
    df["asymmetry"] = (df["kl_divergence_C2H"] - df["kl_divergence_H2C"]).abs()
    df["direction_sign"] = df["kl_divergence_C2H"] > df["kl_divergence_H2C"]
    df["sublabel"] = df["level"] + "/" + df["sublevel"]
    df_s = df.sort_values("asymmetry", ascending=True)
    colors = ["#E53935" if s else "#1976D2" for s in df_s["direction_sign"]]
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.barh(df_s["sublabel"], df_s["asymmetry"], color=colors, alpha=0.88)
    ax.set_xlabel("|KL C→H − KL H→C| — directional asymmetry\n"
                  "red = C→H more divergent, blue = H→C more divergent")
    ax.set_ylabel("Level / sublevel")
    ax.set_title(f"{label} — Directional KL Asymmetry per Analysis Sublevel\n"
                 "(longer bar = more asymmetric information flow)",
                 fontsize=11, fontweight="bold")
    _save(out_dir / "t3_directional_kl_asymmetry.png")


# ── Task 3 global (cross-newspaper) figures ───────────────────────────────────

def t3g_complexity_profile(np_dirs: dict, out_dir: Path):
    """All newspapers overlaid: per-level entropy comparison."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for ax, col_c, col_h, ylabel, subtitle in [
        (axes[0], "level_entropy_canonical", "level_entropy_headline",
         "Entropy (bits)", "Per-Level Entropy"),
        (axes[1], "level_diversity_canonical", "level_diversity_headline",
         "Diversity (TTR / MATTR proxy)", "Per-Level Diversity"),
    ]:
        for i, (np_name, np_dir) in enumerate(np_dirs.items()):
            df = _csv(np_dir / "accumulated" / "accumulated_complexity.csv")
            if df is None: continue
            df = df[df["level_name"].isin(LEVEL_ORDER)].copy()
            df["lbl"] = df["level_name"].map(LEVEL_LBL)
            xs = range(len(df))
            ax.plot(xs, df[col_c], "o-", lw=2, color=C3[i],
                    label=f"{np_name} Canonical", markersize=6)
            ax.plot(xs, df[col_h], "s--", lw=1.5, color=C3[i],
                    alpha=0.6, label=f"{np_name} Headline", markersize=5)
            if i == 0:
                ax.set_xticks(range(len(df)))
                ax.set_xticklabels(df["lbl"], fontsize=9)
        ax.set_xlabel("Analysis level (L1 = character, L5 = constituency)")
        ax.set_ylabel(ylabel)
        ax.set_title(f"All Newspapers — {subtitle}\n(solid = canonical, dashed = headline)",
                     fontsize=11, fontweight="bold")
        ax.legend(fontsize=7, ncol=2)
    _save(out_dir / "t3g_complexity_profile.png")

def t3g_similarity_profile(np_dirs: dict, out_dir: Path):
    """All newspapers: KL C2H, JS similarity per level — grouped bars."""
    for col, ylabel, fname in [
        ("kl_divergence_C2H",
         "KL Divergence C→H (bits)",
         "t3g_kl_c2h_comparison.png"),
        ("js_similarity",
         "JS Similarity (0–1, higher = more similar)",
         "t3g_js_similarity_comparison.png"),
    ]:
        agg_frames = []
        for np_name, np_dir in np_dirs.items():
            df = _csv(np_dir / "similarity" / "bidirectional_metrics.csv")
            if df is None: continue
            agg = df.groupby("level")[col].mean().reset_index()
            agg["newspaper"] = np_name
            agg_frames.append(agg)
        if not agg_frames: continue
        combined = pd.concat(agg_frames, ignore_index=True)
        order = [l for l in LEVEL_ORDER if l in combined["level"].values]
        pivot = combined.pivot_table(index="level", columns="newspaper",
                                     values=col, aggfunc="mean")
        pivot = pivot.reindex(order)
        pivot.index = [LEVEL_LBL.get(l,l) for l in pivot.index]

        fig, ax = plt.subplots(figsize=(10, 5))
        x = np.arange(len(pivot)); w = 0.25
        for i, np_name in enumerate(NEWSPAPERS):
            if np_name not in pivot.columns: continue
            ax.bar(x+i*w, pivot[np_name].values, w,
                   label=np_name, color=C3[i], alpha=0.87)
        ax.set_xticks(x+w)
        ax.set_xticklabels(pivot.index, fontsize=9)
        ax.set_xlabel("Analysis level (L1 = character, L5 = constituency)")
        ax.set_ylabel(ylabel)
        ax.set_title(f"Cross-Newspaper Comparison — {ylabel.split('(')[0].strip()}",
                     fontsize=12, fontweight="bold")
        ax.legend(title="Newspaper", fontsize=9)
        _save(out_dir / fname)

def t3g_accumulated_curves(np_dirs: dict, out_dir: Path):
    """All newspapers overlaid on same accumulated complexity + similarity panels."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for i, (np_name, np_dir) in enumerate(np_dirs.items()):
        comp = _csv(np_dir / "accumulated" / "accumulated_complexity.csv")
        sim  = _csv(np_dir / "accumulated" / "accumulated_similarity.csv")
        if comp is not None:
            xs = range(len(comp))
            axes[0].plot(xs, comp["accumulated_entropy_canonical"], "o-",
                         lw=2, color=C3[i], label=f"{np_name} Canonical", markersize=6)
            axes[0].plot(xs, comp["accumulated_entropy_headline"], "s--",
                         lw=1.5, color=C3[i], alpha=0.6,
                         label=f"{np_name} Headline", markersize=5)
            if i == 0:
                axes[0].set_xticks(range(len(comp)))
                axes[0].set_xticklabels(comp["level_label"].values, fontsize=9)
        if sim is not None:
            xs = range(len(sim))
            axes[1].plot(xs, sim["accumulated_js_similarity"], "o-",
                         lw=2, color=C3[i], label=f"{np_name} JS sim.", markersize=6)
            if i == 0:
                axes[1].set_xticks(range(len(sim)))
                axes[1].set_xticklabels(sim["level_label"].values, fontsize=9)

    for ax, ylabel, title in [
        (axes[0],
         "Accumulated entropy (bits)",
         "Accumulated Complexity — All Newspapers\n(solid = canonical, dashed = headline)"),
        (axes[1],
         "Accumulated JS similarity (0–1)",
         "Accumulated Similarity (JS) — All Newspapers"),
    ]:
        ax.set_xlabel("Analysis level (L1 = character, L5 = constituency)")
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.legend(fontsize=7, ncol=2)
    _save(out_dir / "t3g_accumulated_curves.png")

def t3g_heatmaps(np_dirs: dict, out_dir: Path):
    """Cross-newspaper complexity and similarity heatmaps."""
    all_comp, all_sim, all_gain, all_bidi = [], [], [], []
    for np_name, np_dir in np_dirs.items():
        for lst, fname in [
            (all_comp, "accumulated/accumulated_complexity.csv"),
            (all_sim,  "accumulated/accumulated_similarity.csv"),
            (all_gain, "accumulated/information_gain.csv"),
            (all_bidi, "similarity/bidirectional_metrics.csv"),
        ]:
            df = _csv(np_dir / fname)
            if df is not None:
                df["newspaper"] = np_name
                lst.append(df)

    def _heatmap(ax, data, title, cbar_label, cmap, vmin=None, vmax=None):
        im = ax.imshow(data.values, cmap=cmap, aspect="auto",
                       vmin=vmin, vmax=vmax)
        ax.set_xticks(range(len(data.columns)))
        ax.set_xticklabels(data.columns, fontsize=9)
        ax.set_yticks(range(len(data.index)))
        ax.set_yticklabels(data.index, fontsize=9)
        cb = plt.colorbar(im, ax=ax, shrink=0.85)
        cb.set_label(cbar_label, fontsize=8)
        ax.set_title(title, fontsize=10, fontweight="bold")
        for i in range(data.values.shape[0]):
            for j in range(data.values.shape[1]):
                ax.text(j, i, f"{data.values[i,j]:.2f}",
                        ha="center", va="center", fontsize=8.5)

    if all_comp:
        comp_all = pd.concat(all_comp, ignore_index=True)
        p_e = comp_all.pivot_table(index="newspaper", columns="level_label",
                                    values="accumulated_entropy_canonical", aggfunc="mean")
        fig, ax = plt.subplots(figsize=(10, 4))
        _heatmap(ax, p_e, "Accumulated Complexity — Canonical Register",
                 "Accumulated entropy (bits)\ncanonical text", "Blues")
        ax.set_xlabel("Analysis level (L1 = character, L5 = constituency)")
        ax.set_ylabel("Newspaper")
        _save(out_dir / "t3g_complexity_heatmap.png")

        if "entropy_ratio_CH" in comp_all.columns:
            p_r = comp_all.pivot_table(index="newspaper", columns="level_label",
                                        values="entropy_ratio_CH", aggfunc="mean")
            fig, ax = plt.subplots(figsize=(10, 4))
            _heatmap(ax, p_r, "Complexity Ratio (Canonical / Headline)",
                     "Entropy ratio C/H\n>1 = canonical more complex\n<1 = headline more complex",
                     "RdYlGn", vmin=0.90, vmax=1.10)
            ax.set_xlabel("Analysis level (L1 = character, L5 = constituency)")
            ax.set_ylabel("Newspaper")
            _save(out_dir / "t3g_entropy_ratio_heatmap.png")

    if all_sim:
        sim_all = pd.concat(all_sim, ignore_index=True)
        p_js = sim_all.pivot_table(index="newspaper", columns="level_label",
                                    values="accumulated_js_similarity", aggfunc="mean")
        fig, ax = plt.subplots(figsize=(10, 4))
        _heatmap(ax, p_js, "Accumulated Similarity (Jensen-Shannon) — Cross-Newspaper",
                 "Accumulated JS similarity (0–1)\n1 = identical distributions",
                 "YlGn", vmin=0.7, vmax=1.0)
        ax.set_xlabel("Analysis level (L1 = character, L5 = constituency)")
        ax.set_ylabel("Newspaper")
        _save(out_dir / "t3g_similarity_heatmap.png")

    if all_bidi:
        bidi_all = pd.concat(all_bidi, ignore_index=True)
        bidi_avg = (bidi_all.groupby(["newspaper","level"])
                   [["kl_divergence_C2H","kl_divergence_H2C","js_similarity"]]
                   .mean().reset_index())
        bidi_avg["lbl"] = bidi_avg["level"].map(LEVEL_LBL)
        p_bidi = bidi_avg.pivot_table(index="newspaper", columns="lbl",
                                       values="js_similarity", aggfunc="mean")
        fig, ax = plt.subplots(figsize=(10, 4))
        _heatmap(ax, p_bidi, "JS Similarity by Level — Cross-Newspaper",
                 "JS similarity (0–1)\n1 = identical distributions",
                 "YlGn", vmin=0.85, vmax=1.0)
        ax.set_xlabel("Analysis level (L1 = character, L5 = constituency)")
        ax.set_ylabel("Newspaper")
        _save(out_dir / "t3g_js_similarity_heatmap.png")

    if all_gain:
        gain_all = pd.concat(all_gain, ignore_index=True)
        levels = gain_all["level_label"].unique().tolist()
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        for ax, col, reg in [(axes[0],"information_gain","Canonical"),
                              (axes[1],"information_gain_headline","Headline")]:
            x = np.arange(len(levels)); w = 0.25
            for i, np_name in enumerate(NEWSPAPERS):
                sub = (gain_all[gain_all["newspaper"]==np_name]
                       .set_index("level_label").reindex(levels))
                ax.bar(x+i*w, sub[col].values, w,
                       label=np_name, color=C3[i], alpha=0.85)
            ax.axhline(0, color="black", lw=0.8)
            ax.set_xticks(x+w); ax.set_xticklabels(levels, fontsize=9)
            ax.set_xlabel("Analysis level")
            ax.set_ylabel("Information gain (entropy bits)\ngreen = new information, negative = redundancy")
            ax.set_title(f"Information Gain per Level — {reg}\nCross-Newspaper Comparison",
                         fontsize=11, fontweight="bold")
            ax.legend(title="Newspaper", fontsize=9)
        _save(out_dir / "t3g_information_gain.png")


# ══════════════════════════════════════════════════════════════════════════════
# ── Config JSON export ────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

def _build_config(task_dirs: dict):
    """Build figures_config and tables_config dicts from the output tree."""
    today = str(date.today())
    figs  = {"version":"1.0","generated_at":today,
             "description":"Index of all figures produced for the ReducedToCanonical study",
             "global":{"task_1":[],"task_2":[],"task_3":[]},
             "per_newspaper":{np_name:{"task_1":[],"task_2":[],"task_3":[]}
                              for np_name in NEWSPAPERS}}
    tbls  = {"version":"1.0","generated_at":today,
             "description":"Index of all tables (CSV/JSON) produced for the ReducedToCanonical study",
             "global":{"task_1":[],"task_2":[],"task_3":[]},
             "per_newspaper":{np_name:{"task_1":[],"task_2":[],"task_3":[]}
                              for np_name in NEWSPAPERS}}

    def _entry_fig(path, title, description, x, y, fig_type, data_src="", notes=""):
        return {"path":str(path.relative_to(OUT)),
                "title":title,"description":description,
                "x_label":x,"y_label":y,"figure_type":fig_type,
                "data_source":data_src,"notes":notes}

    def _entry_tbl(path, title, description, notes=""):
        return {"path":str(path.relative_to(OUT)),
                "title":title,"description":description,"notes":notes}

    # ── Task 1 global ──────────────────────────────────────────────────────────
    g1 = T1 / "global"
    vis1g = g1 / "visualizations"
    for fname, title, desc, x, y, typ in [
        ("t1g_feature_frequency.png",
         "Top-15 Transformation Features — Cross-Newspaper Comparison",
         "Grouped bar: event counts for top-15 schema features, grouped by newspaper",
         "Feature ID (schema v5.0)","Event count","grouped_bar"),
        ("t1g_feature_heatmap.png",
         "Feature Frequency Heatmap — Cross-Newspaper (Column-Normalised)",
         "Heatmap: normalised feature frequency; rows=features, cols=newspapers",
         "Newspaper","Feature ID","heatmap"),
        ("t1g_category_comparison.png",
         "Event Counts by Feature Category — All Newspapers",
         "Stacked bar (count) and stacked bar (proportion) by category for each newspaper",
         "Newspaper","Event count / proportion","stacked_bar"),
        ("t1g_transformation_diversity.png",
         "Transformation Diversity (Entropy) — Cross-Newspaper Comparison",
         "Grouped bar: avg transformation entropy per feature across 3 newspapers",
         "Feature ID","Transformation entropy (bits)","grouped_bar"),
        ("t1g_parse_type_breakdown.png",
         "Event Counts by Parse Type — Cross-Newspaper",
         "Stacked bar: dependency vs constituency events per newspaper",
         "Newspaper","Total event count","stacked_bar"),
        ("t1g_morphological_features.png",
         "Morphological Feature Instances and Rule Generalisability",
         "Bar (instances) + bubble scatter (rule count vs newspaper coverage)",
         "Morphological feature","Instances / rule count","bar+scatter"),
    ]:
        p = vis1g / fname
        if p.exists():
            figs["global"]["task_1"].append(
                _entry_fig(p, title, desc, x, y, typ))

    morph_dir = g1 / "cross-newspaper-morphological"
    for fname, title, desc in [
        ("morphological_features_cross_newspaper.csv",
         "Morphological Features Cross-Newspaper Summary",
         "Aggregated morphological feature instances and rule counts across all newspapers"),
        ("morphological_rules_aggregated.json",
         "Aggregated Morphological Rules (JSON)",
         "All morphological transformation rules combined across newspapers"),
    ]:
        p = morph_dir / fname
        if p.exists():
            figs["global"]["task_1"].append(
                _entry_tbl(p, title, desc)) if fname.endswith(".json") else None
            tbls["global"]["task_1"].append(_entry_tbl(p, title, desc))

    # ── Task 1 per-newspaper ───────────────────────────────────────────────────
    for np_name in NEWSPAPERS:
        np_dir = T1 / "per-newspaper" / np_name
        vis1 = np_dir / "visualizations"
        feat_vis = vis1 / "feature_analysis"

        # supplementary figures
        for fname, title, desc, x, y, typ in [
            ("t1_feature_frequency.png",
             f"{np_name} — Feature Event Frequency (Top 20)",
             "Horizontal bar: top-20 schema features by event count, coloured by category",
             "Feature ID (schema v5.0)","Event count","horizontal_bar"),
            ("t1_feature_category_distribution.png",
             f"{np_name} — Event Counts by Feature Category",
             "Bar chart + donut chart of events grouped by linguistic category",
             "Category","Event count / proportion","bar+pie"),
            ("t1_top_transformations_grid.png",
             f"{np_name} — Top Transformations for 6 Most Frequent Features",
             "2×3 grid: top-8 value-pair transformations for each of the top-6 features",
             "Transformation (canonical→headline)","Event count","grid_bar"),
            ("t1_transformation_diversity.png",
             f"{np_name} — Transformation Diversity (Entropy & Concentration)",
             "Horizontal bars: Shannon entropy and top-3 concentration per feature",
             "Feature ID","Entropy (bits) / concentration ratio","horizontal_bar"),
            ("t1_parse_type_breakdown.png",
             f"{np_name} — Feature Counts by Parse Type",
             "Stacked horizontal bar: dependency vs constituency per feature",
             "Feature ID","Event count","stacked_bar"),
            ("t1_top_value_pairs.png",
             f"{np_name} — Top-25 Feature-Value Pairs",
             "Horizontal bar: most frequent feature-value pair combinations",
             "Feature-value pair","Frequency","horizontal_bar"),
            ("t1_statistical_overview.png",
             f"{np_name} — Feature Occurrences vs. Percentage",
             "Scatter plot: total occurrences (log) vs percentage of total events",
             "Total occurrences (log scale)","Percentage of total (%)","scatter"),
        ]:
            p = vis1 / fname
            if p.exists():
                figs["per_newspaper"][np_name]["task_1"].append(
                    _entry_fig(p, title, desc, x, y, typ))

        # per-feature analysis figures
        if feat_vis.exists():
            for p in sorted(feat_vis.glob("feature_*.png")):
                fid = p.stem.replace("feature_", "")
                figs["per_newspaper"][np_name]["task_1"].append(
                    _entry_fig(p, f"{np_name} — {fid}: Transformation Distribution",
                               "Horizontal bar: canonical→headline value pairs for this feature",
                               "Transformation (canonical→headline)","Event count","horizontal_bar"))

        # pipeline-generated figures (document if present)
        for p in sorted(np_dir.glob("*.png")):
            figs["per_newspaper"][np_name]["task_1"].append(
                _entry_fig(p, f"{np_name} — {p.stem} (pipeline)",
                           "Pipeline-generated figure",
                           "","","pipeline"))

        # tables
        for p in sorted(np_dir.glob("*.csv")):
            tbls["per_newspaper"][np_name]["task_1"].append(
                _entry_tbl(p, f"{np_name} — {p.stem}", "Pipeline-generated table"))
        for p in sorted(np_dir.glob("*.json")):
            tbls["per_newspaper"][np_name]["task_1"].append(
                _entry_tbl(p, f"{np_name} — {p.stem}", "Pipeline-generated JSON"))

    # ── Task 2 global ──────────────────────────────────────────────────────────
    for p in sorted((T2/"global").rglob("*.png")):
        figs["global"]["task_2"].append(
            _entry_fig(p, f"Global — {p.stem}", "Task 2 global figure","","",""))
    for p in sorted((T2/"global").rglob("*.csv")):
        tbls["global"]["task_2"].append(
            _entry_tbl(p, f"Global — {p.stem}", "Task 2 global table"))
    for p in sorted((T2/"bidirectional-transformation"/"figures").glob("*.png")):
        figs["global"]["task_2"].append(
            _entry_fig(p, f"Bidirectional — {p.stem}",
                       "Bidirectional transformation evaluation figure","","",""))
    for p in sorted((T2/"bidirectional-transformation"/"tables").glob("*.csv")):
        tbls["global"]["task_2"].append(
            _entry_tbl(p, f"Bidirectional — {p.stem}", "Bidirectional table"))

    # ── Task 2 per-newspaper ───────────────────────────────────────────────────
    for np_name in NEWSPAPERS:
        vis2 = T2 / "per-newspaper" / np_name / "visualizations"
        for p in sorted(vis2.glob("*.png")):
            figs["per_newspaper"][np_name]["task_2"].append(
                _entry_fig(p, f"{np_name} — {p.stem}",
                           "Task 2 morphological rule visualisation","","",""))
        rules_dir = T2 / "per-newspaper" / np_name / "morphological-rules"
        for p in sorted(rules_dir.glob("*.csv")):
            tbls["per_newspaper"][np_name]["task_2"].append(
                _entry_tbl(p, f"{np_name} — {p.stem}", "Morphological rule table"))
        for p in sorted(rules_dir.glob("*.json")):
            tbls["per_newspaper"][np_name]["task_2"].append(
                _entry_tbl(p, f"{np_name} — {p.stem}", "Morphological rule JSON"))

    # ── Task 3 global ──────────────────────────────────────────────────────────
    for p in sorted((T3/"figures").glob("*.png")):
        figs["global"]["task_3"].append(
            _entry_fig(p, f"Global — {p.stem}",
                       "Task 3 global complexity/similarity figure","","",""))
    for p in sorted((T3/"global").glob("*.csv")):
        tbls["global"]["task_3"].append(
            _entry_tbl(p, f"Global — {p.stem}", "Task 3 global CSV"))

    # ── Task 3 per-newspaper ───────────────────────────────────────────────────
    for np_name in NEWSPAPERS:
        np_dir = T3 / "per-newspaper" / np_name
        fig_dir = np_dir / "figures"
        for p in sorted(fig_dir.glob("*.png")):
            figs["per_newspaper"][np_name]["task_3"].append(
                _entry_fig(p, f"{np_name} — {p.stem}",
                           "Task 3 per-newspaper complexity/similarity figure","","",""))
        for subdir in ["complexity","similarity","accumulated","transformation"]:
            for p in sorted((np_dir/subdir).glob("*.csv")):
                tbls["per_newspaper"][np_name]["task_3"].append(
                    _entry_tbl(p, f"{np_name} — {subdir}/{p.stem}", f"Task 3 {subdir} CSV"))

    return figs, tbls


# ══════════════════════════════════════════════════════════════════════════════
# ── Main ─────────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # ── TASK 1 ────────────────────────────────────────────────────────────────
    print("\n[Task-1] Per-newspaper figures …")
    for np_name in NEWSPAPERS:
        data = T1 / "per-newspaper" / np_name
        vis  = data / "visualizations"
        vis.mkdir(parents=True, exist_ok=True)
        lbl  = np_name
        print(f"  {np_name}")
        t1_feature_frequency(data, lbl, vis)
        t1_feature_category_distribution(data, lbl, vis)
        t1_top_transformations_grid(data, lbl, vis)
        t1_transformation_diversity(data, lbl, vis)
        t1_parse_type_breakdown(data, lbl, vis)
        t1_top_value_pairs(data, lbl, vis)
        t1_per_feature_analysis(data, lbl, vis)
        t1_statistical_overview(data, lbl, vis)

    print("\n[Task-1] Global cross-newspaper figures …")
    feat_frames = {}
    data_dirs   = {}
    for np_name in NEWSPAPERS:
        data = T1 / "per-newspaper" / np_name
        df = _csv(data / "feature_freq_global.csv")
        if df is not None:
            df["newspaper"] = np_name
            feat_frames[np_name] = df
        data_dirs[np_name] = data

    vis1g = T1 / "global" / "visualizations"
    vis1g.mkdir(parents=True, exist_ok=True)
    t1g_feature_frequency(feat_frames, vis1g)
    t1g_feature_heatmap(feat_frames, vis1g)
    t1g_category_comparison(feat_frames, vis1g)
    t1g_transformation_diversity(data_dirs, vis1g)
    t1g_parse_type_breakdown(data_dirs, vis1g)
    t1g_morphological_features(
        T1/"global"/"cross-newspaper-morphological"/"morphological_features_cross_newspaper.csv",
        vis1g)

    # ── TASK 2 ────────────────────────────────────────────────────────────────
    print("\n[Task-2] Per-newspaper morphological rule figures …")
    for np_name in NEWSPAPERS:
        rules_dir = T2 / "per-newspaper" / np_name / "morphological-rules"
        vis2 = T2 / "per-newspaper" / np_name / "visualizations"
        vis2.mkdir(parents=True, exist_ok=True)
        print(f"  {np_name}")
        t2_morphological_rules(rules_dir, np_name, vis2)

    print("\n[Task-2] Global morphological aggregation …")
    t2g_morphological_rules_aggregate(
        {np_name: T2/"per-newspaper"/np_name/"morphological-rules"
         for np_name in NEWSPAPERS},
        T2 / "global" / "visualizations")

    print("\n[Task-2] Bidirectional transformation summary …")
    t2_bidirectional_rule_plots(
        T2 / "bidirectional-transformation" / "tables",
        T2 / "bidirectional-transformation" / "figures")

    # ── TASK 3 ────────────────────────────────────────────────────────────────
    print("\n[Task-3] Per-newspaper complexity/similarity figures …")
    for np_name in NEWSPAPERS:
        np_dir  = T3 / "per-newspaper" / np_name
        out_dir = np_dir / "figures"
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"  {np_name}")
        t3_complexity_profile(np_dir, np_name, out_dir)
        t3_complexity_ratio(np_dir, np_name, out_dir)
        t3_similarity_profile(np_dir, np_name, out_dir)
        t3_accumulated_curves(np_dir, np_name, out_dir)
        t3_information_gain(np_dir, np_name, out_dir)
        t3_directional_asymmetry(np_dir, np_name, out_dir)

    print("\n[Task-3] Global cross-newspaper figures …")
    np_dirs = {np_name: T3/"per-newspaper"/np_name for np_name in NEWSPAPERS}
    out3g   = T3 / "figures"
    out3g.mkdir(parents=True, exist_ok=True)
    t3g_complexity_profile(np_dirs, out3g)
    t3g_similarity_profile(np_dirs, out3g)
    t3g_accumulated_curves(np_dirs, out3g)
    t3g_heatmaps(np_dirs, out3g)

    # ── Config JSON ────────────────────────────────────────────────────────────
    print("\n[Config] Building figures_config.json and tables_config.json …")
    figs, tbls = _build_config({})

    for fname, obj in [("figures_config.json", figs),
                        ("tables_config.json",  tbls)]:
        p = OUT / fname
        p.write_text(json.dumps(obj, indent=2, ensure_ascii=False))
        print(f"  saved → {p.relative_to(OUT)}")

    # summary
    total_figs = (sum(len(v) for v in figs["global"].values())
                  + sum(len(v2) for v in figs["per_newspaper"].values()
                         for v2 in v.values()))
    total_tbls = (sum(len(v) for v in tbls["global"].values())
                  + sum(len(v2) for v in tbls["per_newspaper"].values()
                         for v2 in v.values()))
    print(f"\nConfig: {total_figs} figure entries, {total_tbls} table entries catalogued.")
    print("Done.")


if __name__ == "__main__":
    main()
