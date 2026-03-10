"""
fair_comparison_pipeline.py
============================
Orchestrates the full fair-comparison pipeline for one or all newspapers.

Pipeline
--------
1. Load events_global.csv  (existing output, unchanged)
2. Count eligible sites    (EligibleSiteCounter)
3. Normalize + log2        (OpportunityNormalizer)
4. Apply all weightings    (FeatureWeighter)
5. Save events_fair.csv
6. Produce visualizations  (FairComparisonVisualizer)

Outputs
-------
Per newspaper:
    output/task-1-comparative-study/per-newspaper/{NP}/events_fair.csv
    output/task-1-comparative-study/per-newspaper/{NP}/visualizations/fair_comparison/*.png

Global (aggregated across newspapers):
    output/task-1-comparative-study/global/events_fair_global.csv
    output/task-1-comparative-study/global/visualizations/fair_comparison/*.png
"""

import sys
import os
from pathlib import Path

import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import BASE_DIR
from paths_config import NEWSPAPERS
from register_comparison.analysis.eligible_site_counter   import EligibleSiteCounter
from register_comparison.analysis.opportunity_normalizer  import OpportunityNormalizer
from register_comparison.analysis.feature_weighter        import FeatureWeighter
from register_comparison.analysis.fair_comparison_visualizer import (
    plot_all_single_np,
    plot_cross_np_grouped,
    plot_level_contribution,
)

TASK1_DIR = BASE_DIR / "output" / "task-1-comparative-study"


class FairComparisonPipeline:
    """
    Runs the fair-comparison pipeline for one or all newspapers.

    Usage
    -----
    pipe = FairComparisonPipeline()
    pipe.run("The-Hindu")          # single newspaper
    pipe.run_all_newspapers()      # all 3 + global aggregate figures
    """

    def __init__(self, plot: bool = True):
        self.plot       = plot
        self._normalizer = OpportunityNormalizer()
        self._weighter   = FeatureWeighter()

    # ------------------------------------------------------------------
    # Single newspaper
    # ------------------------------------------------------------------

    def run(self, newspaper: str) -> pd.DataFrame:
        """
        Full pipeline for one newspaper.  Returns the summary DataFrame.
        """
        print(f"\n{'='*60}")
        print(f"  Fair comparison — {newspaper}")
        print(f"{'='*60}")

        # ── 1. Load events ──────────────────────────────────────────────
        events_path = (TASK1_DIR / "per-newspaper" / newspaper
                       / "events_global.csv")
        if not events_path.exists():
            print(f"  [SKIP] events_global.csv not found: {events_path}")
            return pd.DataFrame()

        events_df = pd.read_csv(events_path)
        print(f"  Loaded {len(events_df):,} events from events_global.csv")

        # ── 2. Eligible site counts ─────────────────────────────────────
        print("  Counting eligible sites …")
        counter    = EligibleSiteCounter(newspaper)
        site_counts = counter.get_all_site_counts()
        print(f"    sentence_pairs              = {site_counts['sentence_pairs']:,}")
        print(f"    tokens_canonical            = {site_counts['tokens_canonical']:,}")
        print(f"    morph_feature_slots         = {site_counts['morph_feature_slots_canonical']:,}")
        print(f"    aligned_token_pairs (approx)= {site_counts['aligned_token_pairs']:,}")
        print(f"    constituency_nodes          = {site_counts['constituency_nodes_canonical']:,}")
        print(f"    clause_nodes                = {site_counts['clause_nodes_canonical']:,}")

        # ── 3. Normalize + log2 ─────────────────────────────────────────
        print("  Normalizing …")
        summary_df = self._normalizer.run(events_df, site_counts)

        # ── 4. Weighting (all methods) ──────────────────────────────────
        print("  Weighting …")
        summary_df = self._weighter.run_all(summary_df, events_df)

        # ── 5. Save CSV ─────────────────────────────────────────────────
        out_dir  = TASK1_DIR / "per-newspaper" / newspaper
        csv_path = out_dir / "events_fair.csv"
        summary_df.to_csv(csv_path, index=False)
        print(f"  Saved → events_fair.csv  ({len(summary_df)} features)")

        # ── 6. Visualizations ───────────────────────────────────────────
        if self.plot:
            fig_dir = out_dir / "visualizations" / "fair_comparison"
            fig_dir.mkdir(parents=True, exist_ok=True)
            print(f"  Generating figures → {fig_dir.relative_to(BASE_DIR)}/")
            plot_all_single_np(summary_df, fig_dir, newspaper=newspaper)

        return summary_df

    # ------------------------------------------------------------------
    # All newspapers + global aggregate figures
    # ------------------------------------------------------------------

    def run_all_newspapers(self) -> dict:
        """
        Run for all 3 newspapers, then produce cross-newspaper figures
        in the global output directory.

        Returns dict {newspaper: summary_df}.
        """
        all_dfs = {}
        for np_name in NEWSPAPERS:
            df = self.run(np_name)
            if not df.empty:
                df["newspaper"] = np_name
                all_dfs[np_name] = df

        if len(all_dfs) < 2:
            print("\n[WARN] Fewer than 2 newspapers succeeded; skipping global figures.")
            return all_dfs

        # ── Global CSV ─────────────────────────────────────────────────
        global_dir = TASK1_DIR / "global"
        global_dir.mkdir(parents=True, exist_ok=True)
        global_df = pd.concat(all_dfs.values(), ignore_index=True)
        global_csv = global_dir / "events_fair_global.csv"
        global_df.to_csv(global_csv, index=False)
        print(f"\n  Saved global CSV → {global_csv.relative_to(BASE_DIR)}")

        # ── Cross-newspaper figures ─────────────────────────────────────
        if self.plot:
            fig_dir = global_dir / "visualizations" / "fair_comparison"
            fig_dir.mkdir(parents=True, exist_ok=True)
            print(f"  Generating cross-newspaper figures → "
                  f"{fig_dir.relative_to(BASE_DIR)}/")

            plot_cross_np_grouped(
                all_dfs, "rate_norm",
                "Opportunity-Normalized Rates — All Newspapers",
                "rate_norm  (events / eligible sites)",
                fig_dir / "cross_np_normalized_rates.png",
            )
            plot_cross_np_grouped(
                all_dfs, "log2_norm",
                "Log₂ Normalized Rates — All Newspapers",
                "|log₂(rate_norm)|",
                fig_dir / "cross_np_log2_normalized.png",
                use_abs=True,
            )
            plot_cross_np_grouped(
                all_dfs, "score_lvl",
                "Level-Weighted Scores — All Newspapers",
                "|score_lvl|",
                fig_dir / "cross_np_level_weighted.png",
                use_abs=True,
            )
            plot_cross_np_grouped(
                all_dfs, "score_idf",
                "IDF-Weighted Scores — All Newspapers",
                "|score_idf|",
                fig_dir / "cross_np_idf_weighted.png",
                use_abs=True,
            )
            if "score_jsd" in next(iter(all_dfs.values())).columns:
                plot_cross_np_grouped(
                    all_dfs, "score_jsd",
                    "JSD-Weighted Scores — All Newspapers",
                    "|score_jsd|",
                    fig_dir / "cross_np_jsd_weighted.png",
                    use_abs=True,
                )
            plot_level_contribution(all_dfs, fig_dir / "level_contribution.png")

        print("\nDone.")
        return all_dfs
