"""
feature_weighter.py
===================
Stage 4 of the fair-comparison pipeline — weighting.

Each method is computed independently and adds its own columns to the
summary DataFrame produced by OpportunityNormalizer.  Methods implemented:

    Level-based (simplest)
        weight_lvl  = 1 / level_index ^ alpha
        score_lvl   = log2_norm * weight_lvl

    IDF-analog
        weight_idf  = -log2(rate_norm)   i.e. log2(1 / rate_norm)
        score_idf   = log2_norm * weight_idf

    JSD (Jensen-Shannon Divergence)  — more sophisticated; data-driven
        weight_jsd  = JSD(P_canonical(f) || P_headline(f))
        score_jsd   = log2_norm * weight_jsd
        Requires the original events_df (for value distributions).

    PMI-based discriminativity        — most sophisticated; per-value
        weight_pmi  = Σ_v max(0, PMI(feature_value v ; register=canonical))
        score_pmi   = log2_norm * weight_pmi
        Requires the original events_df.

All scores are applied to log2_norm.  Because log2_norm is negative
(rates < 1), multiplying by a positive weight produces a more-negative
score for features with low normalised rates — so ranking by *absolute
value* (or by negated score) shows which features are relatively more
prominent after weighting.

Convention used in visualizations: display abs(score) so that larger
bars = more prominent feature after weighting.
"""

import json
import sys
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

CONFIG_PATH = Path(__file__).parents[2] / "data" / "fair-comparison-config.json"
EPSILON     = 1e-9


class FeatureWeighter:
    """
    Apply weighting methods to a normalised summary DataFrame.

    Usage
    -----
    weighter = FeatureWeighter()

    # Simplest: level-based only
    df = weighter.apply_level_weights(summary_df)

    # IDF
    df = weighter.apply_idf_weights(df)

    # JSD and PMI require the original events_df
    df = weighter.apply_jsd_weights(df, events_df)
    df = weighter.apply_pmi_weights(df, events_df)

    # All at once
    df = weighter.run_all(summary_df, events_df)
    """

    def __init__(self):
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
        self._default_alpha = cfg["weighting_methods"]["level"]["alpha"]

    # ------------------------------------------------------------------
    # Level-based (simplest — no events_df needed)
    # ------------------------------------------------------------------

    def apply_level_weights(self, df: pd.DataFrame, alpha: float | None = None) -> pd.DataFrame:
        """
        weight_lvl = 1 / level_index ^ alpha

        Penalises coarser-grained features (higher level_index).
        Morphological (level 1) → weight 1.0;
        Constituency  (level 5) → weight 0.2  (for alpha=1).
        """
        if alpha is None:
            alpha = self._default_alpha
        out = df.copy()
        out["weight_lvl"] = 1.0 / (out["level_index"].astype(float) ** alpha)
        out["score_lvl"]  = out["log2_norm"] * out["weight_lvl"]
        return out

    # ------------------------------------------------------------------
    # IDF-analog (no events_df needed; uses rate_norm)
    # ------------------------------------------------------------------

    def apply_idf_weights(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        weight_idf = -log2(rate_norm)  =  log2(1 / rate_norm)

        Rare features (low rate_norm) get high weight; frequent features
        get low weight.  Entirely data-driven, no tuning needed.
        """
        out = df.copy()
        safe_rate = out["rate_norm"].clip(lower=EPSILON)
        out["weight_idf"] = -np.log2(safe_rate)
        out["score_idf"]  = out["log2_norm"] * out["weight_idf"]
        return out

    # ------------------------------------------------------------------
    # JSD — requires events_df
    # ------------------------------------------------------------------

    def apply_jsd_weights(self, df: pd.DataFrame, events_df: pd.DataFrame) -> pd.DataFrame:
        """
        weight_jsd = JSD(P_canonical(f) || P_headline(f))

        Measures how much the feature's *value distribution* shifts between
        the two registers.  A feature where values are nearly identically
        distributed gets low JSD (both forms use the same values equally);
        a feature with a dramatic distributional shift gets high JSD.

        JSD ∈ [0, 1] when using log base 2 and scipy's jensenshannon
        (which returns the square root, so we square it).
        """
        out = df.copy()
        jsd_map = {}

        for fid in out["feature_id"]:
            grp = events_df[events_df["feature_id"] == fid]
            canon_counts = grp["canonical_value"].value_counts()
            head_counts  = grp["headline_value"].value_counts()
            all_vals     = list(set(canon_counts.index) | set(head_counts.index))

            if len(all_vals) < 2:
                jsd_map[fid] = 0.0
                continue

            p = np.array([canon_counts.get(v, 0) for v in all_vals], dtype=float)
            q = np.array([head_counts.get(v,  0) for v in all_vals], dtype=float)
            p = p / p.sum() if p.sum() > 0 else np.ones(len(p)) / len(p)
            q = q / q.sum() if q.sum() > 0 else np.ones(len(q)) / len(q)

            # scipy jensenshannon returns sqrt(JSD); square to get JSD ∈ [0,1]
            jsd_map[fid] = float(jensenshannon(p, q, base=2) ** 2)

        out["weight_jsd"] = out["feature_id"].map(jsd_map).fillna(0.0)
        out["score_jsd"]  = out["log2_norm"] * out["weight_jsd"]
        return out

    # ------------------------------------------------------------------
    # PMI — requires events_df
    # ------------------------------------------------------------------

    def apply_pmi_weights(self, df: pd.DataFrame, events_df: pd.DataFrame) -> pd.DataFrame:
        """
        For each feature, compute per-value PMI with the canonical register
        and sum positive PMI values:

            pmi(f, v) = log2( P(v | canonical) / P(v) )
            weight_pmi = Σ_v max(0, pmi(f, v))

        Where P(v) = average of P(v|canonical) and P(v|headline),
        and P(v|register) = fraction of events for feature f with value v
        in the given register column.

        Features with values that strongly skew toward one register get
        high weight; features whose values appear equally in both get low weight.
        """
        out = df.copy()
        pmi_map = {}

        for fid in out["feature_id"]:
            grp = events_df[events_df["feature_id"] == fid]
            n = len(grp)
            if n == 0:
                pmi_map[fid] = 0.0
                continue

            all_vals = set(grp["canonical_value"].unique()) | set(grp["headline_value"].unique())
            all_vals.discard("ABSENT")

            pmi_sum = 0.0
            for v in all_vals:
                p_v_canon = (grp["canonical_value"] == v).sum() / n
                p_v_head  = (grp["headline_value"]  == v).sum() / n
                p_v       = (p_v_canon + p_v_head) / 2.0
                if p_v > EPSILON and p_v_canon > EPSILON:
                    pmi_val = np.log2(p_v_canon / p_v)
                    pmi_sum += max(0.0, pmi_val)

            pmi_map[fid] = pmi_sum

        out["weight_pmi"] = out["feature_id"].map(pmi_map).fillna(0.0)
        out["score_pmi"]  = out["log2_norm"] * out["weight_pmi"]
        return out

    # ------------------------------------------------------------------
    # Convenience: run all methods
    # ------------------------------------------------------------------

    def run_all(
        self,
        df: pd.DataFrame,
        events_df: pd.DataFrame | None = None,
        alpha: float | None = None,
    ) -> pd.DataFrame:
        """
        Apply all weighting methods in order (simplest first).
        JSD and PMI are skipped if events_df is None.
        """
        out = self.apply_level_weights(df, alpha)
        out = self.apply_idf_weights(out)
        if events_df is not None:
            out = self.apply_jsd_weights(out, events_df)
            out = self.apply_pmi_weights(out, events_df)
        return out
