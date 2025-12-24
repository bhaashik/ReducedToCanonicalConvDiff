# Multi-Level Similarity Analysis - Implementation Summary

**Date**: December 25, 2024
**Status**: Fully Implemented
**Integration**: Task 3 Extended Features

## Overview

This document summarizes the comprehensive multi-level similarity analysis system implemented for Task 3. The system measures register similarity using rigorous information-theoretic and statistical metrics at multiple linguistic levels.

## Theoretical Foundation

Based on **SIMILARITY-METRICS.md**, which provides comprehensive guidance on:
- Conditional entropy vs. relative entropy
- Cross-entropy decomposition: H(P,Q) = H(P) + D_KL(P||Q)
- Symmetric vs. asymmetric divergence measures
- Normalized and bounded variants
- Practical estimators for language distributions

## Implemented Metrics

### 1. Entropy-Based Measures

#### Cross-Entropy (H(P,Q))
- **Both directions**: H(Canonical, Headline) and H(Headline, Canonical)
- **Interpretation**: Expected code length when using Q to encode P
- **Asymmetric**: H(P,Q) ≠ H(Q,P)
- **Normalized variants**: Per-token, vocabulary-normalized
- **Use case**: Measures how well one register's distribution predicts another

#### Relative Entropy / KL Divergence (D_KL(P||Q))
- **Both directions**: D_KL(C||H) and D_KL(H||C)
- **Interpretation**: Information lost when Q approximates P
- **Properties**: D_KL(P||Q) ≥ 0, with equality iff P = Q
- **Asymmetric**: D_KL(P||Q) ≠ D_KL(Q||P)
- **Symmetrized variant**: D_sym = D_KL(P||Q) + D_KL(Q||P)
- **Use case**: Quantifies how different two distributions are

#### Jensen-Shannon Divergence (JSD)
- **Formula**: JSD(P,Q) = 0.5 * D_KL(P||M) + 0.5 * D_KL(Q||M), where M = 0.5(P+Q)
- **Properties**:
  - Symmetric: JSD(P,Q) = JSD(Q,P)
  - Bounded: 0 ≤ JSD ≤ 1 (with base-2 logs)
  - Square root forms a metric (triangle inequality)
- **JS Similarity**: 1 - JSD, range [0,1]
- **JS Distance**: √JSD
- **Use case**: Safe, bounded divergence measure

### 2. Statistical Distribution Measures

#### Bhattacharyya Measures
- **Coefficient**: BC(P,Q) = Σ√(P(x) * Q(x))
  - Range: [0, 1], where 1 = identical distributions
- **Distance**: D_B = -ln(BC), range [0, ∞]
- **Use case**: Measures overlap via geometric mean

#### Hellinger Distance
- **Formula**: H(P,Q) = √(0.5 * Σ(√P(x) - √Q(x))²)
- **Properties**:
  - Bounded metric: [0, 1]
  - 0 = identical, 1 = completely different
- **Similarity**: 1 - Hellinger distance
- **Use case**: Bounded, symmetric distance metric

#### Perplexity Measures
- **Self-perplexity**: PPL = 2^H(P)
  - Interpretation: "Effective vocabulary size"
- **Cross-perplexity**: PPL = 2^H(P,Q)
  - Interpretation: Effective branching factor when using Q to model P
- **Normalized variants**: By vocabulary size
- **Use case**: Intuitive complexity measure

### 3. Set-Based Similarity

#### Jaccard Similarity
- **Formula**: |A ∩ B| / |A ∪ B|
- **Range**: [0, 1]
- **Use case**: Type overlap measure (ignores frequencies)

#### Dice Coefficient
- **Formula**: 2|A ∩ B| / (|A| + |B|)
- **Range**: [0, 1]
- **Use case**: Harmonic mean-based overlap

#### Overlap Coefficient
- **Formula**: |A ∩ B| / min(|A|, |B|)
- **Range**: [0, 1]
- **Use case**: Minimum-based overlap

### 4. Correlation Measures

#### Pearson Correlation
- **Interpretation**: Linear relationship between frequencies
- **Range**: [-1, 1]
- **Use case**: Frequency correlation for shared vocabulary

#### Spearman Correlation
- **Interpretation**: Rank-order relationship
- **Range**: [-1, 1]
- **Use case**: Monotonic relationship, robust to outliers

### 5. Sequence-Based Similarity

#### Edit Distance (Levenshtein)
- **Sentence-level**: Character-level edit distance
- **Normalized**: 1 - (distance / max_possible_distance)
- **Use case**: String similarity for parallel sentences

#### Token-Level Metrics
- **Average Jaccard**: Per-sentence token overlap
- **Token overlap ratio**: Proportion of shared tokens

## Analysis Levels

### Lexical Level
- **Surface forms**: All word tokens (case-normalized)
- **Lemmas**: Base forms from dependency parses
- **Sentence-level**: Parallel sentence comparison
- **Metrics**: All entropy, set-based, and sequence-based measures

### Morphological Level
- **POS tags**: Universal Dependencies POS tags
- **Morphological features**: 20 UD feature types
  - Person, Gender, Definiteness, Tense, Number, Aspect, Voice, Mood, Case, Degree
  - PronType, Possessive, NumType, NumForm, Polarity, Reflexive, VerbForm
  - Abbreviation, ExtPos, Foreign
- **Per-feature-type analysis**: Separate metrics for each feature type
- **Metrics**: All entropy and set-based measures, per-type divergence

### Syntactic Level
- **Dependency relations**: Universal dependency labels
- **Constituency labels**: Phrase-level categories (NP, VP, PP, etc.)
- **Dependency bigrams**: Head POS + relation + dependent POS patterns
- **Metrics**: All entropy and set-based measures

### Structural Level
- **Constituency trees**:
  - Height correlation
  - Size (node count) correlation
  - Label set similarity
- **Dependency trees**:
  - Sentence length correlation
  - Tree depth correlation
  - Average dependency distance correlation
- **Metrics**: Correlation-based similarity

## Directional Asymmetry Analysis

Key insight: Measures like cross-entropy and KL divergence are **asymmetric**.

### Asymmetry Components

1. **Entropy Difference**: H(C) vs H(H)
   - Canonical typically has higher entropy (more diverse)

2. **Cross-Entropy Asymmetry**: |H(C,H) - H(H,C)|
   - Reveals which direction is harder to predict

3. **KL Divergence Asymmetry**: |D_KL(C||H) - D_KL(H||C)|
   - Reveals which transformation loses more information

### Interpretation

- **Large asymmetry**: Fundamental distributional differences
- **Direction with higher cross-entropy**: Harder to model/predict
- **Direction with higher KL**: Loses more information in approximation

## Visualization Outputs

### 1. Jaccard Similarity Comparison (4 panels)
- Jaccard by linguistic level
- Jaccard by sublevel
- Distribution by newspaper
- Level × newspaper comparison

### 2. Cross-Entropy Comparison (4 panels)
- Canonical → Headline cross-entropy
- Headline → Canonical cross-entropy
- Bidirectional comparison by level
- Cross-entropy by newspaper

### 3. KL Divergence Comparison (4 panels)
- KL divergence by level (both directions)
- Symmetrized KL divergence
- KL asymmetry analysis
- KL by newspaper

### 4. Jensen-Shannon Similarity (2 panels)
- JS similarity by level
- JS similarity by newspaper

### 5. Similarity Heatmaps (4 metrics)
- Jaccard similarity heatmap
- JS similarity heatmap
- Hellinger similarity heatmap
- Bhattacharyya coefficient heatmap
- All: Level × Newspaper

### 6. Directional Asymmetry (2 panels)
- Cross-entropy asymmetry by level
- KL divergence asymmetry by level

### 7. Correlation Similarity (2 panels)
- Pearson correlation (structural)
- Spearman correlation (rank-based)

## File Structure

```
multilevel_similarity_analyzer.py          # Core analyzer (single newspaper)
run_multilevel_similarity_analysis.py      # Comprehensive runner (all newspapers)

output/multilevel_similarity/
├── [Newspaper]/
│   ├── multilevel_similarity_analysis.json    # Complete results
│   ├── multilevel_similarity_summary.csv      # Tabular summary
│   └── combined_similarity_scores.csv         # Aggregate scores
│
└── GLOBAL_ANALYSIS/
    ├── aggregated_similarity_metrics.csv      # All metrics, all newspapers
    ├── jaccard_similarity_comparison.png      # 4-panel Jaccard analysis
    ├── cross_entropy_comparison.png           # 4-panel cross-entropy
    ├── kl_divergence_comparison.png           # 4-panel KL analysis
    ├── js_similarity_comparison.png           # 2-panel JS analysis
    ├── similarity_heatmaps.png                # 4-metric heatmaps
    ├── directional_asymmetry.png              # 2-panel asymmetry
    ├── correlation_similarity.png             # 2-panel correlations
    └── MULTILEVEL_SIMILARITY_REPORT.md        # Comprehensive report
```

## Usage

### Single Newspaper Analysis
```bash
python multilevel_similarity_analyzer.py --newspaper "Times-of-India"
```

### All Newspapers with Comparative Analysis
```bash
python run_multilevel_similarity_analysis.py
```

Processes all three newspapers, aggregates results, creates visualizations, and generates comprehensive report.

## Research Applications

### 1. Register Similarity Quantification
- **Question**: How similar are canonical and headline registers?
- **Metrics**: Jaccard, JS similarity, Hellinger similarity
- **Interpretation**: Higher values = more similar

### 2. Information-Theoretic Differences
- **Question**: How much information is lost in reduction (C→H)?
- **Metrics**: Cross-entropy, KL divergence
- **Interpretation**: H(C,H) - H(C) = information loss

### 3. Transformation Asymmetry
- **Question**: Is C→H easier than H→C?
- **Metrics**: KL asymmetry, cross-entropy asymmetry
- **Interpretation**: Direction with lower cross-entropy is easier

### 4. Level-Specific Similarity
- **Question**: At which linguistic levels are registers most similar?
- **Metrics**: Per-level Jaccard, JS similarity
- **Interpretation**: Identify levels of greatest/least similarity

### 5. Cross-Newspaper Consistency
- **Question**: Are similarity patterns consistent across newspapers?
- **Metrics**: Heatmaps, newspaper × level comparisons
- **Interpretation**: Identify generalizable patterns

### 6. Correlation with Transformation Difficulty
- **Question**: Do similarity metrics predict transformation success?
- **Potential Analysis**: Correlate with Task 2 rule coverage
- **Hypothesis**: Lower similarity = harder transformation

## Integration with Existing System

### Complements Complexity Analysis
- **Complexity**: Measures each register individually
- **Similarity**: Measures register differences
- **Combined**: Complete picture of register relationships

### Synergy with Task 2
- **Task 2**: Rule-based transformation coverage
- **Similarity**: Quantifies transformation difficulty
- **Analysis**: Correlate coverage with similarity metrics

### Theoretical Validation
- **Empirical**: Measure actual distributions
- **Theoretical**: Compare with linguistic theory predictions
- **Publication**: Publication-ready metrics and visualizations

## Key Advantages

1. **Comprehensive**: 25+ distinct metrics across all levels
2. **Theoretically Grounded**: Based on established information theory
3. **Bidirectional**: Both C→H and H→C directions
4. **Normalized**: Multiple normalization schemes for comparability
5. **Bounded**: Includes bounded metrics (JS, Hellinger) for interpretation
6. **Asymmetry-Aware**: Explicitly analyzes directional differences
7. **Multi-Level**: Systematic coverage of all linguistic levels
8. **Visualized**: Publication-ready comparative visualizations
9. **Documented**: Comprehensive theoretical and practical documentation

## References

1. **SIMILARITY-METRICS.md**: Theoretical foundation and metric definitions
2. **Shannon (1948)**: Entropy and conditional entropy foundations
3. **Kullback & Leibler (1951)**: Relative entropy / KL divergence
4. **Cover & Thomas**: Elements of Information Theory
5. **Lin (1991)**: Jensen-Shannon divergence
6. **Chen & Goodman (1996)**: Cross-entropy evaluation in NLP

## Future Extensions

### Semantic Level
- Word embedding-based similarity (Word2Vec, BERT)
- Semantic role pattern similarity
- Argument structure alignment

### Pragmatic Level
- Discourse marker usage similarity
- Cohesion metric correlation
- Information structure patterns

### Cross-Linguistic
- Apply same framework to other language pairs
- Compare register differences across languages
- Universal vs. language-specific patterns

### Machine Learning Integration
- Use similarity metrics as features
- Predict transformation difficulty
- Automated register classification

---

**Implementation Date**: December 25, 2024
**Version**: 1.0
**Status**: Production-ready
**Integration**: Fully integrated with Task 3 pipeline
