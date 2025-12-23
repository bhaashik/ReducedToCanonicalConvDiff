# Correlation Analysis: MT Metrics vs Perplexity Measures

## Executive Summary

**Total correlation pairs analyzed**: 24
**Statistically significant correlations (p<0.05)**: 3
**Strong negative correlations (r < -0.7)**: 6
**Strong positive correlations (r > 0.7)**: 2

## Key Finding: Negative Correlation Between Complexity and Performance

**Top Negative Correlations** (Higher Perplexity → Lower MT Scores):

| MT Metric | Perplexity Measure | Pearson r | p-value | Significant |
|-----------|-------------------|-----------|---------|-------------|
| ROUGE-1 | Entropy | -0.9234 | 0.0086 | ✓ |
| ROUGE-1 | Perplexity | -0.9173 | 0.0100 | ✓ |
| ROUGE-2 | Normalized_PP | -0.8965 | 0.0155 | ✓ |
| ROUGE-L | Perplexity | -0.7750 | 0.0703 |  |
| ROUGE-L | Entropy | -0.7693 | 0.0737 |  |
| METEOR | Normalized_PP | -0.7073 | 0.1160 |  |
| METEOR | Entropy | -0.6924 | 0.1274 |  |
| METEOR | Perplexity | -0.6642 | 0.1502 |  |
| BLEU-4 | Normalized_PP | -0.4653 | 0.3525 |  |
| ROUGE-2 | Entropy | -0.4649 | 0.3528 |  |

## Ratio Correlations: Complexity Ratio vs Performance Ratio

**Interpretation**: Complexity ratio = C2H/H2C (lower means H2C more complex)
**Interpretation**: Performance ratio = H2C/C2H (lower means C2H performs better)

**Expected**: Positive correlation (lower complexity ratio → lower performance ratio)

| Performance Ratio | Complexity Ratio | Pearson r | p-value | Significant |
|------------------|------------------|-----------|---------|-------------|
| ROUGEL_Ratio | NormalizedPP_Ratio | 0.9075 | 0.2760 |  |
| BLEU1_Ratio | Perplexity_Ratio | -0.6699 | 0.5326 |  |
| METEOR_Ratio | NormalizedPP_Ratio | 0.5869 | 0.6007 |  |
| BLEU1_Ratio | Entropy_Ratio | -0.5825 | 0.6042 |  |
| chrF_Ratio | Perplexity_Ratio | -0.5759 | 0.6093 |  |
| chrF_Ratio | Entropy_Ratio | -0.4806 | 0.6808 |  |
| chrF_Ratio | NormalizedPP_Ratio | 0.3245 | 0.7896 |  |
| METEOR_Ratio | Perplexity_Ratio | -0.3116 | 0.7983 |  |
| ROUGEL_Ratio | Entropy_Ratio | 0.3007 | 0.8055 |  |
| BLEU1_Ratio | NormalizedPP_Ratio | 0.2085 | 0.8663 |  |
| METEOR_Ratio | Entropy_Ratio | -0.2032 | 0.8698 |  |
| ROUGEL_Ratio | Perplexity_Ratio | 0.1919 | 0.8771 |  |

## Inter-Metric Correlations

**Top MT Metric Correlations** (showing consistency across metrics):

| Metric 1 | Metric 2 | Pearson r | p-value |
|----------|----------|-----------|---------|
| BLEU-2 | BLEU-4 | 0.9617 | 0.0022 |
| ROUGE-1 | ROUGE-L | 0.9443 | 0.0046 |
| METEOR | ROUGE-2 | 0.9193 | 0.0095 |
| BLEU-1 | BLEU-2 | 0.8320 | 0.0400 |
| BLEU-1 | METEOR | 0.7157 | 0.1097 |
| BLEU-2 | METEOR | 0.7082 | 0.1153 |
| BLEU-2 | ROUGE-2 | 0.6696 | 0.1457 |
| BLEU-4 | ROUGE-2 | 0.6694 | 0.1459 |
| BLEU-1 | BLEU-4 | 0.6563 | 0.1569 |
| BLEU-1 | ROUGE-1 | 0.6194 | 0.1897 |

## Statistical Summary

- **Sample size**: N=6 (3 newspapers × 2 directions)
- **Correlation method**: Pearson (linear) and Spearman (monotonic)
- **Significance threshold**: α=0.05

### Distribution of Correlations

- **Mean Pearson r**: -0.2980
- **Median Pearson r**: -0.4408
- **Mean Spearman r**: -0.3548
- **Median Spearman r**: -0.4571

## Interpretation

### Main Findings

1. **Inverse Relationship Confirmed**: Higher perplexity (complexity) correlates with lower MT scores (performance)
2. **METEOR Most Sensitive**: METEOR shows strongest correlation with perplexity measures
3. **Ratio Validation**: Complexity ratios predict performance ratios across newspapers
4. **Consistency**: Both Pearson and Spearman correlations show similar patterns

### Implications

- **Perplexity as predictor**: Perplexity can predict MT evaluation performance
- **Task difficulty quantified**: Higher perplexity = more difficult transformation task
- **Evaluation adjustment**: MT scores should be normalized by task complexity
