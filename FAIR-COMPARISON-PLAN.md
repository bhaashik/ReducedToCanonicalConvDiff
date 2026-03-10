# Fair Comparison Plan — Opportunity Normalization + Log₂ + Weighting

## Problem

All features in `events_global.csv` are currently treated with equal weight in all figures and statistics. This is unfair because:

1. **Granularity bias**: CONST-MOV has 5705 events in The-Hindu; VERB-FORM-CHG has 11. Not because constituency changes are linguistically dominant — but because there are far more constituency nodes per sentence than verb tokens.
2. **Corpus size bias**: The-Hindu has 1500 sentence pairs, Times-of-India has 1041. Raw counts are not comparable across newspapers.

Raw counts do not measure *how often the feature changes* — they measure *how many times the event was observed*, which conflates linguistic frequency with structural granularity and corpus size.

## Solution: Three-Stage Pipeline (added on top of existing)

```
Stage 1: Raw counts          ← existing pipeline, untouched
Stage 2: Opportunity norm.   ← divide by eligible sites (structural granularity + corpus size)
Stage 3: Log₂ of rate        ← compress Zipfian distribution; 1 bit = 2× frequency ratio
Stage 4: Weighting [optional] ← re-emphasis by linguistic significance
```

Key principle from the conversation: **normalize for correctness, log₂ for scale, weight only for emphasis.**

Config file: `data/fair-comparison-config.json`

---

## Stage 2: Opportunity Normalization

**Formula**: `rate = count / eligible_sites`

Each feature has a natural denominator — the number of sites where that feature *could have* differed. Dividing by this gives a per-opportunity rate that is independent of both corpus size and level granularity.

| Feature(s) | Eligible Site | Rationale |
|---|---|---|
| FEAT-CHG | Total morph-feature slots in canonical (sum of FEATS entries) | Each (token, attribute) pair is one possible morph change |
| VERB-FORM-CHG | Verb tokens in canonical | One possible verb form change per verb |
| FW-DEL, FW-ADD | Function word tokens in canonical | One deletion/addition possible per function word |
| C-DEL, C-ADD | Content word tokens in canonical | One deletion/addition possible per content word |
| POS-CHG, FORM-CHG, LEMMA-CHG, TOKEN-REORDER | Aligned token pairs | One possible change per aligned pair |
| PUNCT-DEL, PUNCT-ADD, PUNCT-SUBST | Punctuation tokens in canonical | One possible change per punctuation mark |
| DEP-REL-CHG, HEAD-CHG | Aligned token pairs | Each aligned token has exactly one deprel |
| CONST-MOV, CONST-REM, CONST-ADD | Constituency nodes in canonical | One possible operation per constituent |
| CLAUSE-TYPE-CHG | Clause nodes (S/SBAR) in canonical | One possible clause change per clause |
| H-TYPE, H-STRUCT, F-TYPE | Sentence pairs | One typological label per sentence |
| TED-SIMPLE, TED-ZS, TED-KLEIN, TED-RTED | Sentence pairs | Mean TED score = sum(scores) / n_sentences |

**Excluded** (continuous numeric, not event counts): LENGTH-CHG, BRANCH-DIFF, CONST-COUNT-DIFF, TREE-DEPTH-DIFF, DEP-DIST-DIFF, TOKEN-COUNT-DIFF, CHAR-COUNT-DIFF.

---

## Stage 3: Log₂ Transformation

**Formula**: `log2_norm = log2(rate + ε)` where `ε = 1e-9`

- Applied to `rate_norm` (NOT to raw counts)
- Values will be negative (since `rate < 1`); differences are in bits
- 1 bit difference = one feature occurs twice as often as another
- Compresses 4–5 orders of magnitude down to ~15 bits range
- Makes all features visible in the same figure

---

## Stage 4: Weighting Methods (Optional, Comparative)

All four methods run independently and produce separate output columns. Results compared before any combination.

### A. Level-Based Weight
`weight_lvl = 1 / level_index ^ α`  (α = 1.0 default)

| Level | Index | Weight (α=1) |
|---|---|---|
| Morphological | 1 | 1.000 |
| Lexical/Token | 2 | 0.500 |
| Punctuation | 3 | 0.333 |
| Dependency | 4 | 0.250 |
| Constituency | 5 | 0.200 |
| Typological | 6 | 0.167 |
| Structural/TED | 7 | 0.143 |

Interpretable, theory-grounded. Requires pre-assigning levels (done in config).

### B. IDF-Analog Weight
`weight_idf = -log(rate_norm)` = log(1/rate)

Data-driven. High-frequency features get lower weight automatically. No tuning needed.

### C. JSD Weight
`weight_jsd = JSD(P_canonical(f) || P_reduced(f))`

Measures how much the feature's value distribution shifts between registers. Data-driven, symmetric, theoretically motivated for register comparison and similarity analysis. Range: [0, 1] (log₂ base).

### D. PMI Weight (per feature-value pair)
`pmi(f,v) = log2(P(v|canonical) / P(v))`
`weight_pmi = Σ_v max(0, pmi(f,v))`

Identifies register-discriminating feature-value pairs. Most granular.

---

## New Modules

All new code goes under `register_comparison/analysis/` (new subdirectory). **Existing pipeline untouched.**

```
register_comparison/
  analysis/
    __init__.py
    eligible_site_counter.py      ← computes denominators from corpus
    opportunity_normalizer.py     ← Stages 2 + 3
    feature_weighter.py           ← Stage 4 (all 4 methods)
    fair_comparison_pipeline.py   ← orchestrator
    fair_comparison_visualizer.py ← new figures

run_fair_comparison.py            ← top-level CLI runner
```

### `eligible_site_counter.py`

```python
class EligibleSiteCounter:
    def count_from_conllu(self, newspaper: str) -> dict
    # Returns: tokens_canonical, function_word_tokens_canonical,
    #          content_word_tokens_canonical, verb_tokens_canonical,
    #          morph_feature_slots_canonical, punct_tokens_canonical,
    #          aligned_token_pairs (approximated)

    def count_from_constituency(self, newspaper: str) -> dict
    # Returns: constituency_nodes_canonical, clause_nodes_canonical

    def get_all_site_counts(self, newspaper: str) -> dict
    # Returns: merged dict of all eligible site counts + sentence_pairs
```

### `opportunity_normalizer.py`

```python
class OpportunityNormalizer:
    def normalize(self, events_df, site_counts) -> DataFrame
    # Adds: eligible_site_name, eligible_site_count, rate_norm

    def apply_log2(self, df) -> DataFrame
    # Adds: log2_norm

    def run(self, events_df, site_counts) -> DataFrame
    # Both stages combined
```

### `feature_weighter.py`

```python
class FeatureWeighter:
    def apply_level_weights(self, df, alpha=1.0) -> DataFrame
    # Adds: weight_lvl, score_lvl

    def apply_idf_weights(self, df) -> DataFrame
    # Adds: weight_idf, score_idf

    def apply_jsd_weights(self, df) -> DataFrame
    # Adds: weight_jsd, score_jsd (requires value distribution)

    def apply_pmi_weights(self, df) -> DataFrame
    # Adds: weight_pmi, score_pmi (per feature-value pair)

    def run_all(self, df, alpha=1.0) -> DataFrame
    # All four methods
```

### `fair_comparison_pipeline.py`

```python
class FairComparisonPipeline:
    def run(self, newspaper: str) -> DataFrame
    # Full pipeline: load → site_counts → normalize → log2 → weight → save

    def run_all_newspapers(self) -> dict
    # Runs for all 3 newspapers, returns {np: df}
```

### `fair_comparison_visualizer.py`

```python
class FairComparisonVisualizer:
    def plot_normalized_frequency(self, df, out_dir)
    # Horizontal bar chart: rate_norm per feature (all levels comparable)

    def plot_log2_profile(self, df, out_dir)
    # Horizontal bar chart: log2_norm per feature

    def plot_weighted_ranking(self, df, method, out_dir)
    # One figure per weighting method; features ranked by score

    def plot_cross_newspaper_normalized(self, dfs, out_dir)
    # Grouped bars: 3 newspapers, normalized rates (corpus-size fair)

    def plot_register_profiles(self, dfs, out_dir)
    # For Task 3: log2-normalized feature vectors as register profiles
    # (heatmap or radar chart)

    def plot_level_contribution(self, dfs, out_dir)
    # Stacked bar: proportion of total normalized score per linguistic level
```

---

## Output Files

Per newspaper (`output/task-1-comparative-study/per-newspaper/{NP}/`):
- `events_fair.csv` — enriched events with all new columns

Global (`output/task-1-comparative-study/global/`):
- `events_fair_global.csv` — aggregated across all newspapers

Figures (per newspaper and global, in existing `visualizations/` dirs):
- `normalized_feature_frequency.png`
- `log2_feature_profile.png`
- `weighted_ranking_level.png`
- `weighted_ranking_idf.png`
- `weighted_ranking_jsd.png`
- `cross_newspaper_normalized.png`
- `level_contribution.png`

---

## Execution Order

```bash
# Full fair comparison pipeline (all 3 newspapers)
python run_fair_comparison.py

# With options
python run_fair_comparison.py --newspapers "Times-of-India" --methods level idf --no-plots
```

---

## Verification

After running:
1. Confirm `FEAT-CHG` normalized rate > `CONST-MOV` normalized rate (or comparable) — this validates the normalization is working
2. Confirm cross-newspaper rates for the same feature are similar in magnitude (corpus-size independence)
3. Check log₂ values: all negative; VERB-FORM-CHG should be closer to CONST-MOV on log scale than on raw scale
4. Spot-check JSD weight: features with very different value distributions between registers should have higher JSD than those with nearly identical distributions
5. Compare level-weighted vs IDF-weighted rankings — correlation should be moderate but not perfect (they're measuring different things)

---

## Task 3 Integration

The log₂-normalized feature vectors (one per register per newspaper) become input to Task 3 complexity and similarity analyses:
- **Complexity**: Entropy of the log₂-normalized rate distribution per level
- **Similarity**: Cosine or JSD distance between canonical and reduced feature vectors
- **Biber-style**: PCA/factor analysis over the feature matrix to find co-varying clusters

This connects the new fair-comparison layer directly to the downstream research goals of measuring linguistic complexity and register similarity.
