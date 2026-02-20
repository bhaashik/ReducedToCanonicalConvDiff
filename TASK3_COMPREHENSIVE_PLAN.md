# Plan: Comprehensive Task 3 — Multi-Level Complexity & Similarity Analysis

## Context

Task 2 (bidirectional transformation) is complete with v2 improvements (BLEU ~0.23–0.34, WER ~0.34–0.71). The user now wants to complete **Task 3**: a comprehensive complexity and similarity study between canonical (full sentence) and reduced (headline) registers, going well beyond what the existing code does.

### What Exists

- `multilevel_complexity_analyzer.py` (802 lines): Per-register entropy, TTR, perplexity, structural metrics at lexical/morphological/syntactic/structural levels
- `multilevel_similarity_analyzer.py` (1108 lines): Cross-register Jaccard, Dice, Overlap, KL, JS, Bhattacharyya, Hellinger, cross-entropy, correlations
- `run_multilevel_complexity_analysis.py` (568 lines): Runner that aggregates across newspapers
- `run_multilevel_similarity_analysis.py` (717 lines): Runner that aggregates across newspapers
- Task 1 `events_global.csv`: Per-sentence transformation events (FW-DEL, FEAT-CHG, DEP-REL-CHG, etc.)
- Task 2 `c2r_results_*.csv` / `r2c_results_*.csv`: Bidirectional transformation results with per-sentence metrics
- Task 2 `rule_coverage_analysis.csv`: Rule inventory counts and confidence per newspaper/direction

### What's Missing

1. **Character-level analysis** (linguistic level i)
2. **Enhanced lexical diversity metrics** (MATTR, MTLD, HD-D, Yule's K, Brunet's W, Honore's H)
3. **Transformation-based metrics** (complexity/similarity through the lens of Task 2 rules)
4. **Accumulated levels** (running aggregation char→token→morph→dep→const)
5. **Explicit both-directions** for all asymmetric metrics (C→H and H→C)
6. **Symmetrized versions** for every asymmetric metric
7. **More NLP metrics** from ACL papers (chrF, compression ratio, MDD normalization, lexical density, Wasserstein distance)

## Implementation Plan

### Architecture: 3 New Files + 2 Extended Files + 1 New Runner

| File | Action | Purpose |
|------|--------|---------|
| `multilevel_complexity_analyzer.py` | **Extend** | Add character level, enhanced lexical diversity, better dep/const metrics |
| `multilevel_similarity_analyzer.py` | **Extend** | Add character-level similarity, Wasserstein, explicit bidirectional + symmetrized |
| `transformation_based_analyzer.py` | **New** (~400 lines) | Complexity/similarity through transformation rules |
| `accumulated_level_analyzer.py` | **New** (~300 lines) | Accumulated metrics from char→constituency levels |
| `comprehensive_task3_runner.py` | **New** (~500 lines) | Unified runner for all Task 3 analysis |

---

### Step 1: Extend `multilevel_complexity_analyzer.py`

Add new methods to `MultiLevelComplexityAnalyzer`:

**a) Character-Level Analysis** — new `analyze_character_level()` method:
- Character entropy: `H(chars)` — entropy of character unigram distribution
- Character bigram/trigram entropy
- Average word length: `total_chars / total_words`
- MATTR (Moving Average TTR) at character n-gram level (window=50 chars): `MATTR = avg(TTR_window)` — Covington & McFall 2010
- Character type-token ratio

**b) Enhanced Lexical Diversity** — extend `_compute_lexical_metrics()`:
- **MATTR** (window=50 tokens): Sliding window TTR averaged — Covington & McFall 2010
- **MTLD** (Measure of Textual Lexical Diversity): Sequential TTR with threshold reset — McCarthy & Jarvis 2010
- **HD-D** (Hypergeometric Distribution D): Non-stochastic vocd-D — McCarthy & Jarvis 2010
- **Yule's K**: `K = 10^4 * (SUM(i^2 * V(i)) - N) / N^2` — Yule 1944
- **Brunet's W**: `W = N^(V^-0.172)` — Brunet 1978
- **Honore's H**: `H = 100 * log(N) / (1 - V1/V)` — Honore 1979
- **Lexical density**: `content_words / total_words` (NOUN, VERB, ADJ, ADV = content)
- **Compression ratio**: `len(headline) / len(canonical)` (per sentence pair, averaged)

**c) Better Dependency Metrics** — extend `_compute_dep_tree_metrics()`:
- **MDD normalized**: `MDD_ratio = MDD_observed / MDD_random_baseline` — Futrell et al. 2015
  - Random baseline: expected MDD for random permutation of same-length sentence
- **Dependency distance distribution entropy**: `H(distance_distribution)`
- **Proportion of long dependencies** (distance > 5)

**d) Better Constituency Metrics** — extend `_compute_tree_metrics()`:
- **Subordination index approximation**: Count SBAR nodes / count S nodes
- **Clause density**: SBAR + S nodes per sentence
- **Production rule entropy**: Entropy of the distribution of CFG production rules
- **Right-branching ratio**: Fraction of non-terminals where rightmost child is also non-terminal

### Step 2: Extend `multilevel_similarity_analyzer.py`

**a) Character-Level Similarity** — new `analyze_character_similarity()` method:
- **chrF** (character n-gram F-score, n=6): Popovic 2015 — per sentence pair, averaged
- **Character n-gram Jaccard** (for n=2,3,4): Set overlap of character n-grams
- **Normalized Compression Distance (NCD)**: `NCD(x,y) = (C(xy) - min(C(x),C(y))) / max(C(x),C(y))` using zlib — Cilibrasi & Vitanyi 2005

**b) Wasserstein Distance** — add to `_distributional_similarity()`:
- **Wasserstein distance**: `scipy.stats.wasserstein_distance` on frequency vectors — symmetric metric
- Advantage over KL/JS: defined even when supports differ

**c) Explicit Both-Directions Reporting**:
- Every asymmetric metric already computed in both directions internally
- Add clear labeling: `metric_C2H` (canonical→headline) and `metric_H2C` (headline→canonical)
- Separate CSV columns for each direction

**d) Symmetrized Versions** — new `_symmetrize()` method:
- For KL divergence: `D_sym = 0.5*(D_KL(P||Q) + D_KL(Q||P))`
- For cross-entropy: `H_sym = 0.5*(H(P,Q) + H(Q,P))`
- For Wasserstein: already symmetric
- JSD: already symmetric
- Add `*_symmetrized` columns to output CSV

### Step 3: New `transformation_based_analyzer.py`

Compute complexity and similarity **through the lens of transformations** using Task 1 events and Task 2 bidirectional results.

```python
class TransformationBasedAnalyzer:
    def __init__(self, newspaper: str):
        ...

    def analyze(self) -> Dict:
        """Run all transformation-based analyses."""

    # === Complexity Metrics (per register/direction) ===

    def _transformation_density(self) -> Dict:
        """Average number of transformation events per sentence pair."""
        # Load events_global.csv, group by sentence_id, count events

    def _rule_entropy(self) -> Dict:
        """Entropy of the distribution of rule types applied."""
        # From events CSV: H(distribution of feature_id values)

    def _transformation_type_distribution(self) -> Dict:
        """Proportion breakdown: lexical vs morphological vs syntactic vs structural."""
        # FW-DEL, C-DEL = lexical; FEAT-CHG, FORM-CHG = morphological;
        # DEP-REL-CHG = syntactic; TED-* = structural

    def _transformation_difficulty(self) -> Dict:
        """From Task 2: average actions per sentence, avg confidence of applied rules."""
        # Load c2r_results_*.csv / r2c_results_*.csv

    def _hypothesis_diversity(self) -> Dict:
        """From Task 2: hypothesis selection distribution as complexity indicator."""
        # Load hypothesis_selection_stats.csv

    # === Similarity Metrics (cross-register via transformations) ===

    def _transformation_coverage(self) -> Dict:
        """What fraction of token differences are explained by extracted rules?"""
        # From rule_coverage_analysis.csv

    def _directional_asymmetry(self) -> Dict:
        """Compare C2R vs R2C transformation characteristics."""
        # Rule counts, confidence, event density in each direction

    def _transformation_based_similarity(self) -> Dict:
        """1 - (normalized transformation density): fewer changes = more similar."""
        # Normalized by sentence length
```

**Data sources**:
- `output/{newspaper}/events_global.csv` — Task 1 events
- `output/transformation-study/bidirectional-transformation/generated/*_results_*.csv` — Task 2 per-sentence results
- `output/transformation-study/bidirectional-transformation/tables/rule_coverage_analysis.csv`
- `output/transformation-study/bidirectional-transformation/tables/hypothesis_selection_stats.csv`

### Step 4: New `accumulated_level_analyzer.py`

Compute **accumulated** complexity and similarity by progressively combining levels.

```python
class AccumulatedLevelAnalyzer:
    def __init__(self, newspaper: str,
                 complexity_results: Dict,
                 similarity_results: Dict):
        ...

    def compute_accumulated_complexity(self) -> pd.DataFrame:
        """
        Levels (in order):
          L1: character only
          L2: character + token
          L3: character + token + morphological
          L4: character + token + morphological + dependency
          L5: character + token + morphological + dependency + constituency
          L6: character + token + morphological + dependency + constituency + TED

        For each accumulated level, compute:
        - Combined entropy (average of constituent level entropies)
        - Combined TTR/diversity (average)
        - Information gain: how much does adding this level increase the signal?
        """

    def compute_accumulated_similarity(self) -> pd.DataFrame:
        """Same levels, for cross-register similarity metrics."""
        # Average Jaccard, JSD, cross-entropy across included levels

    def compute_information_gain(self) -> pd.DataFrame:
        """Delta between consecutive accumulated levels."""
        # gain_i = accumulated_i - accumulated_{i-1}
```

### Step 5: New `comprehensive_task3_runner.py`

Unified runner that orchestrates everything:

```python
class ComprehensiveTask3Runner:
    def __init__(self):
        self.newspapers = ['Times-of-India', 'Hindustan-Times', 'The-Hindu']
        self.output_dir = Path('output/complexity-similarity-study/')

    def run(self):
        for newspaper in self.newspapers:
            # 1. Complexity analysis (extended)
            complexity = MultiLevelComplexityAnalyzer(newspaper)
            complexity.run_complete_analysis()

            # 2. Similarity analysis (extended)
            similarity = MultiLevelSimilarityAnalyzer(newspaper)
            similarity.run_complete_analysis()

            # 3. Transformation-based analysis
            transform = TransformationBasedAnalyzer(newspaper)
            transform.analyze()

            # 4. Accumulated level analysis
            accumulated = AccumulatedLevelAnalyzer(
                newspaper,
                complexity.results,
                similarity.results
            )
            accumulated.compute_all()

        # 5. Cross-newspaper aggregation + visualization
        self.aggregate_and_visualize()

    def aggregate_and_visualize(self):
        """Generate cross-newspaper comparative tables and figures."""
```

**Output structure**:
```
output/complexity-similarity-study/
├── per-newspaper/
│   ├── {Newspaper}/
│   │   ├── complexity/
│   │   │   ├── character_level.csv
│   │   │   ├── token_level.csv
│   │   │   ├── morphological_level.csv
│   │   │   ├── dependency_level.csv
│   │   │   ├── constituency_level.csv
│   │   │   └── combined_complexity.csv
│   │   ├── similarity/
│   │   │   ├── character_similarity.csv
│   │   │   ├── token_similarity.csv
│   │   │   ├── morphological_similarity.csv
│   │   │   ├── dependency_similarity.csv
│   │   │   ├── constituency_similarity.csv
│   │   │   ├── bidirectional_metrics.csv      # C2H + H2C columns
│   │   │   └── symmetrized_metrics.csv
│   │   ├── transformation/
│   │   │   ├── transformation_complexity.csv
│   │   │   ├── transformation_similarity.csv
│   │   │   └── rule_based_metrics.csv
│   │   └── accumulated/
│   │       ├── accumulated_complexity.csv
│   │       ├── accumulated_similarity.csv
│   │       └── information_gain.csv
├── global/
│   ├── cross_newspaper_complexity.csv
│   ├── cross_newspaper_similarity.csv
│   ├── accumulated_levels_comparison.csv
│   └── comprehensive_summary.csv
├── figures/
│   ├── complexity_by_level_and_newspaper.png
│   ├── similarity_by_level_and_newspaper.png
│   ├── accumulated_complexity_curve.png
│   ├── accumulated_similarity_curve.png
│   ├── directional_asymmetry_heatmap.png
│   ├── transformation_density_by_type.png
│   ├── information_gain_by_level.png
│   └── character_to_constituency_ladder.png
└── tables/
    ├── comprehensive_metrics_all_levels.csv   # Master table
    ├── bidirectional_comparison.csv
    └── symmetrized_comparison.csv
```

### Step 6: Figures

New visualizations:

1. **Accumulated complexity curve**: X=level (char→const), Y=accumulated complexity score, lines=newspaper×register
2. **Accumulated similarity curve**: X=level, Y=accumulated similarity, lines=newspaper
3. **Information gain bar chart**: How much each level adds beyond the previous
4. **Directional asymmetry heatmap**: |metric_C2H - metric_H2C| across levels and newspapers
5. **Transformation density by type**: Stacked bar chart showing proportion of lexical/morph/syntactic/structural transformations
6. **Character-to-constituency ladder**: Multi-panel showing metrics at each level side-by-side
7. **Lexical diversity comparison**: MATTR, MTLD, HD-D, Yule's K across newspapers×registers

---

## Metrics Reference (with ACL citations)

### Character Level (i)
| Metric | Type | Symmetric | Citation |
|--------|------|-----------|----------|
| Character entropy | Complexity | N/A | Standard info theory |
| Character n-gram entropy | Complexity | N/A | Standard |
| Avg word length | Complexity | N/A | Coleman & Liau 1975 |
| MATTR (char n-grams) | Complexity | N/A | Covington & McFall 2010 |
| chrF (n=6) | Similarity | Yes | Popovic, WMT 2015 |
| Char n-gram Jaccard | Similarity | Yes | Standard |
| NCD (zlib) | Similarity | Yes | Cilibrasi & Vitanyi 2005 |

### Token Level (ii)
| Metric | Type | Symmetric | Citation |
|--------|------|-----------|----------|
| TTR, Root-TTR, Log-TTR | Complexity | N/A | Johnson 1944 |
| MATTR (window=50) | Complexity | N/A | Covington & McFall 2010 |
| MTLD | Complexity | N/A | McCarthy & Jarvis 2010 |
| HD-D | Complexity | N/A | McCarthy & Jarvis 2010 |
| Yule's K | Complexity | N/A | Yule 1944 |
| Brunet's W | Complexity | N/A | Brunet 1978 |
| Honore's H | Complexity | N/A | Honore 1979 |
| Hapax ratio | Complexity | N/A | Standard |
| Lexical density | Complexity | N/A | Ure 1971 |
| Compression ratio | Similarity | No | Clarke & Lapata 2008 |
| Perplexity | Complexity | N/A | Jelinek 1977 |

### Morphological Level (iii)
| Metric | Type | Symmetric | Citation |
|--------|------|-----------|----------|
| Feature entropy (per feat type) | Complexity | N/A | Cotterell et al. TACL 2019 |
| Feature-value TTR | Complexity | N/A | Standard |
| Morphological richness index | Complexity | N/A | Blevins 2013 |
| Feature distribution KL/JSD | Similarity | JSD=yes | Standard info theory |
| Feature distribution Wasserstein | Similarity | Yes | Kantorovich 1942 |

### Dependency Level (iv)
| Metric | Type | Symmetric | Citation |
|--------|------|-----------|----------|
| MDD (mean dependency distance) | Complexity | N/A | Liu 2008 |
| MDD normalized (vs random) | Complexity | N/A | Futrell et al. 2015 |
| Dep distance distribution entropy | Complexity | N/A | Liu 2008 |
| Proportion long deps (>5) | Complexity | N/A | Standard |
| Deprel distribution KL/JSD | Similarity | JSD=yes | Plank & van Noord 2011 |
| Deprel Wasserstein | Similarity | Yes | Standard |
| Dep bigram overlap (Jaccard) | Similarity | Yes | Standard |

### Constituency Level (v)
| Metric | Type | Symmetric | Citation |
|--------|------|-----------|----------|
| Tree depth (avg, std) | Complexity | N/A | Yngve 1960 |
| Branching factor | Complexity | N/A | Standard |
| Subordination index (SBAR/S) | Complexity | N/A | Lu 2010 |
| Clause density | Complexity | N/A | Lu 2010 |
| Production rule entropy | Complexity | N/A | Standard |
| Right-branching ratio | Complexity | N/A | Standard |
| Constituency label KL/JSD | Similarity | JSD=yes | Standard |
| Label set Jaccard | Similarity | Yes | Standard |
| Height/size correlation | Similarity | Yes | Standard |

### TED / Structural Level (vi)
| Metric | Type | Symmetric | Citation |
|--------|------|-----------|----------|
| TED simple | Similarity | Yes | Standard |
| TED Zhang-Shasha | Similarity | Yes | Zhang & Shasha 1989 |
| TED Klein | Similarity | Yes | Klein 1998 |
| TED RTED | Similarity | Yes | Pawlik & Augsten 2011 |
| Normalized TED | Similarity | Yes | Bille 2005 |
| TED distribution entropy | Complexity | N/A | Derived |

### Transformation-Based (cross-cutting)
| Metric | Type | Symmetric | Citation |
|--------|------|-----------|----------|
| Transformation density | Complexity | N/A | Project-specific |
| Rule entropy | Complexity | N/A | Project-specific |
| Rule type distribution | Complexity | N/A | Project-specific |
| Rule coverage | Similarity | No | Project-specific |
| Directional asymmetry | Similarity | N/A | Project-specific |

---

## Execution Order

1. **Step 1**: Extend `multilevel_complexity_analyzer.py` (character level + enhanced lexical diversity + better dep/const metrics)
2. **Step 2**: Extend `multilevel_similarity_analyzer.py` (character similarity + Wasserstein + explicit bidirectional + symmetrized)
3. **Step 3**: Create `transformation_based_analyzer.py` (new file)
4. **Step 4**: Create `accumulated_level_analyzer.py` (new file)
5. **Step 5**: Create `comprehensive_task3_runner.py` (new runner)
6. **Step 6**: Run for all newspapers and verify
7. **Step 7**: Generate figures

## Dependencies

All metrics use existing dependencies (numpy, scipy, pandas, matplotlib, seaborn, nltk, conllu). No new packages needed.
- `scipy.stats.wasserstein_distance` for Wasserstein metric
- `zlib` (stdlib) for NCD compression
- `scipy.special.comb` for HD-D hypergeometric calculation

## Verification

1. Run `python comprehensive_task3_runner.py` for all 3 newspapers
2. Check that all CSV files are generated in `output/complexity-similarity-study/`
3. Verify accumulated curves show monotonic information gain
4. Confirm bidirectional metrics: `metric_C2H != metric_H2C` for asymmetric measures
5. Confirm symmetrized: `metric_sym = 0.5*(metric_C2H + metric_H2C)`
6. Spot-check: character-level metrics should differ from token-level (not redundant)
