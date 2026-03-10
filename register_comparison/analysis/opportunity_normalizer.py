"""
opportunity_normalizer.py
=========================
Stage 2 + 3 of the fair-comparison pipeline.

Stage 2 — Opportunity normalization
    rate_norm = count_raw / eligible_site_count

Stage 3 — Log₂ transformation
    log2_norm = log2(rate_norm + ε)

The result is a *feature-level* summary DataFrame (one row per feature),
NOT an event-level frame.  The original events_global.csv is unchanged.

Output columns added
--------------------
    eligible_site_name   : name of the denominator used
    eligible_site_count  : numeric denominator value
    count_raw            : raw event count (or sum of scores for TED features)
    rate_norm            : count_raw / eligible_site_count
    log2_norm            : log2(rate_norm + ε)
"""

import json
import sys
import os
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

CONFIG_PATH = Path(__file__).parents[2] / "data" / "fair-comparison-config.json"
EPSILON     = 1e-9   # added inside log2 to avoid log(0)

# Features whose canonical_value IS a numeric score (TED algorithms)
TED_FEATURES = {"TED-SIMPLE", "TED-ZHANG-SHASHA", "TED-KLEIN", "TED-RTED"}


class OpportunityNormalizer:
    """
    Normalise raw event counts by eligible sites and apply log2.

    Usage
    -----
    norm = OpportunityNormalizer()
    summary_df = norm.run(events_df, site_counts)
    """

    def __init__(self):
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
        self._taxonomy  = cfg["feature_taxonomy"]["features"]
        self._excluded  = set(cfg["excluded_features"].keys())

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, events_df: pd.DataFrame, site_counts: dict) -> pd.DataFrame:
        """
        Full pipeline: aggregate counts → normalize → log2.

        Parameters
        ----------
        events_df   : raw events_global.csv loaded as a DataFrame
        site_counts : dict returned by EligibleSiteCounter.get_all_site_counts()

        Returns
        -------
        DataFrame with one row per known feature, sorted by level_index.
        """
        df = self._aggregate_raw(events_df)
        df = self._attach_site_counts(df, site_counts)
        df = self._compute_rate(df)
        df = self._apply_log2(df)
        return df.sort_values("level_index").reset_index(drop=True)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _aggregate_raw(self, events_df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate events_global.csv to feature level.

        For TED features the canonical_value column holds the numeric score;
        we sum those scores and use the sum as count_raw (mean = sum / n_sentences).
        For all other features count_raw = number of event rows.
        """
        rows = []
        df_work = events_df[~events_df["feature_id"].isin(self._excluded)].copy()

        for fid, grp in df_work.groupby("feature_id"):
            if fid not in self._taxonomy:
                continue
            meta = self._taxonomy[fid]

            if fid in TED_FEATURES:
                scores = pd.to_numeric(grp["canonical_value"], errors="coerce")
                raw_val = float(scores.dropna().sum())
            else:
                raw_val = float(len(grp))

            rows.append({
                "feature_id":   fid,
                "level":        meta["level"],
                "level_index":  meta["level_index"],
                "event_type":   meta.get("event_type", "count"),
                "eligible_site_name": meta["eligible_site"],
                "count_raw":    raw_val,
            })

        return pd.DataFrame(rows)

    def _attach_site_counts(self, df: pd.DataFrame, site_counts: dict) -> pd.DataFrame:
        df = df.copy()
        df["eligible_site_count"] = df["eligible_site_name"].map(site_counts)
        return df

    def _compute_rate(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["rate_norm"] = df["count_raw"] / df["eligible_site_count"]
        return df

    def _apply_log2(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["log2_norm"] = np.log2(df["rate_norm"].clip(lower=EPSILON))
        return df
