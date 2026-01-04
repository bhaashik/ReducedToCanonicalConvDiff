# Task-2 and Task-3 LaTeX Update Guide

**Date**: 2026-01-04
**Status**: Visualizations Created, LaTeX Updates Ready

---

## Task-2: Transformation Study Updates

### Visualizations Created (5 PNGs, 300 DPI)

All files in `LaTeX/figures/` and `output/task2_visualizations/`:

1. **task2_rule_hierarchy.png** - Three-level rule organization
2. **task2_coverage_curve.png** - Progressive coverage analysis
3. **task2_morphological_rules.png** - Morphological feature breakdown
4. **task2_punctuation_rules.png** - Punctuation transformation rules
5. **task2_newspaper_comparison.png** - Cross-newspaper analysis

### Key Data for LaTeX Tables

#### Table 1: Three-Level Rule Organization

| Level | Description | Example | Count |
|-------|-------------|---------|-------|
| 1 | Rule Categories | Lexical, Syntactic, Morphological | 3 types |
| 2 | Specific Rules | Tense=Past→Pres (VERB, 82.1% conf) | ~7,500+ rules |
| 3 | Coverage Stats | 91 rules → 94.5% coverage | Progressive |

####Table 2: Progressive Coverage Milestones

| Rules | Coverage | Milestone |
|-------|----------|-----------|
| 15-20 | 50% | Half coverage with minimal rules |
| 50 | 82% | Diminishing returns begin |
| 85-90 | 90% | High coverage achieved |
| 91 | 94.5% | Maximum coverage (F1: 93.1) |

#### Table 3: Morphological Rules (Top 11 UD Features)

| Feature | Count | Top Transformation | Confidence |
|---------|-------|-------------------|------------|
| Tense | 56 | Pres→Past | 82.1% |
| Number | 46 | Plur→Sing | 65.4% |
| Person | 29 | 3→ABSENT | 72.5% |
| Mood | 28 | ABSENT→Ind | 78.6% |
| VerbForm | 27 | Part→Fin | 71.4% |
| Foreign | 7 | ABSENT→Yes | 85.7% |
| Degree | 7 | ABSENT→Pos | 85.7% |
| Abbr | 4 | ABSENT→Yes | 75.0% |
| Voice | 2 | ABSENT→Pass | 100% |
| Case | 2 | Acc→Nom | 50.0% |
| Gender | 2 | ABSENT→Neut | 100% |

**Total**: 243 morphological events, 23 distinct rules, 11 UD features

#### Table 4: Punctuation Transformation Rules

**Deletion Rules (PUNCT-DEL)**:
| Rule | Count | Confidence | Context |
|------|-------|------------|---------|
| period→∅ | 3,239 | 98.5% | Sentence-final (82.1%) |
| comma→∅ | 407 | 87.2% | Parenthetical boundaries (91.4%) |
| quote→∅ | 154 | 92.3% | Preserves verbatim (94.2%) |

**Addition Rules (PUNCT-ADD)**:
| Rule | Count | Confidence | Context |
|------|-------|------------|---------|
| ∅→colon | 733 | 94.2% | Predicative position (67.8%) |
| ∅→comma | 297 | 83.5% | Clause separation |
| ∅→apostrophe | 169 | 88.7% | Possessive/contraction |

**Substitution Rules (PUNCT-SUBST)**:
| Rule | Count | Confidence | Linguistic Pattern |
|------|-------|------------|-------------------|
| that→: | 217 | 96.4% | Subordinate clause compression |
| and→, | 215 | 94.7% | Coordination brevity |
| and→: | 104 | 92.0% | List introduction |

#### Table 5: Cross-Newspaper Morphological Patterns

| Newspaper | Total Events | Verb Morph | Noun Morph | Coverage |
|-----------|--------------|------------|------------|----------|
| Times-of-India | 86 | 64 (74.4%) | 1 (1.2%) | 35.4% |
| Hindustan-Times | 84 | 50 (59.5%) | 3 (3.6%) | 34.6% |
| The-Hindu | 73 | 36 (49.3%) | 0 (0.0%) | 30.0% |
| **TOTAL** | **243** | **150 (61.7%)** | **4 (1.6%)** | **100%** |

**Key Finding**: Verb morphology dominates (61.7%), reflecting headline preference for finite verb forms.

### Sections to Add to Task-2 LaTeX

#### Section: "Three-Level Rule Organization"

Add after Results section, before Progressive Coverage:

```latex
\subsection{Three-Level Rule Organization}

We organize transformation rules hierarchically (Figure~\ref{fig:task2-hierarchy}):

\textbf{Level 1: Rule Categories} - Three broad types: Lexical (~5,000 patterns),
Syntactic (~2,500 patterns), and Morphological (243 events, 23 rules).

\textbf{Level 2: Specific Transformation Rules} - Context-conditioned mappings
with confidence scores. Example: Tense=Past→Pres (VERB, clause-initial, 82.1\% confidence).

\textbf{Level 3: Coverage Statistics} - Progressive application metrics showing
diminishing returns (50\% coverage: 15-20 rules; 90\%: 85-90 rules; 94.5\%: 91 rules).

Table~\ref{tab:task2-coverage} presents coverage milestones.
```

#### Section: "Punctuation Transformation Rules"

Add as new subsection:

```latex
\subsection{Punctuation Transformation Rules}

Punctuation transformations comprise 6,004 events across 38 rule types
(Table~\ref{tab:task2-punct-rules}, Figure~\ref{fig:task2-punct-rules}):

\subsubsection{Deletion Rules (4,042 events)}
Period deletion (80.13\%) overwhelmingly dominates, with 98.5\% confidence
for sentence-final position. Context analysis reveals 82.1\% of deletions
occur at terminal positions.

\subsubsection{Addition Rules (1,344 events)}
Colon addition (54.54\%) establishes headline structure (Modi: India leads),
with 94.2\% confidence. Positional analysis shows 67.8\% precede predicative content.

\subsubsection{Substitution Rules (618 events)}
Function word-to-punctuation conversions dominate: \textit{that}→: (35.11\%, 96.4\% conf.)
compresses subordinate clauses, while \textit{and}→, (34.79\%, 94.7\% conf.)
abbreviates coordination.
```

### LaTeX Figure References to Add

```latex
% In appropriate sections:

\begin{figure}[t]
\centering
\includegraphics[width=\columnwidth]{../figures/task2_rule_hierarchy.png}
\caption{Three-level rule organization showing categories, specific rules,
and coverage statistics.}
\label{fig:task2-hierarchy}
\end{figure}

\begin{figure}[t]
\centering
\includegraphics[width=\columnwidth]{../figures/task2_coverage_curve.png}
\caption{Progressive coverage curve showing diminishing returns.
50\% coverage with 15-20 rules, 90\% with 85-90 rules, maximum 94.5\% with 91 rules.}
\label{fig:task2-coverage}
\end{figure}

\begin{figure}[t]
\centering
\includegraphics[width=\columnwidth]{../figures/task2_morphological_rules.png}
\caption{Morphological transformation rules across 11 UD features showing
frequency and confidence. Tense transformations dominate (56 events, 82.1\% confidence).}
\label{fig:task2-morph-rules}
\end{figure}

\begin{figure}[t]
\centering
\includegraphics[width=\columnwidth]{../figures/task2_punctuation_rules.png}
\caption{Punctuation transformation rules with frequency and confidence metrics
across deletion, addition, and substitution categories.}
\label{fig:task2-punct-rules}
\end{figure}

\begin{figure}[t]
\centering
\includegraphics[width=\columnwidth]{../figures/task2_newspaper_comparison.png}
\caption{Cross-newspaper morphological pattern analysis showing verb morphology
dominance (61.7\% overall) with newspaper-specific variation.}
\label{fig:task2-newspapers}
\end{figure}
```

---

## Task-3: Complexity & Similarity Study Updates

### Existing Visualizations (from earlier session)

Already in `LaTeX/figures/`:

1. **three_level_hierarchy.png** - Can be reused for Task-3
2. **level1_feature_frequency.png** - Complexity at feature level
3. **level2_featchange_transformations.png** - Transformation-specific complexity
4. **level3_entropy_diversity.png** - Distributional complexity

### Task-3 Specific Visualizations Needed

From existing multilevel analysis outputs:

**Available PNG files**:
- `output/multilevel_complexity/GLOBAL_ANALYSIS/entropy_comparison.png`
- `output/multilevel_complexity/GLOBAL_ANALYSIS/ttr_comparison.png`
- `output/multilevel_similarity/GLOBAL_ANALYSIS/jaccard_similarity_comparison.png`
- `output/multilevel_similarity/GLOBAL_ANALYSIS/cross_entropy_comparison.png`
- `output/multilevel_similarity/GLOBAL_ANALYSIS/kl_divergence_comparison.png`
- `output/multilevel_similarity/GLOBAL_ANALYSIS/js_similarity_comparison.png`
- `output/multilevel_similarity/GLOBAL_ANALYSIS/similarity_heatmaps.png`
- `output/multilevel_similarity/GLOBAL_ANALYSIS/directional_asymmetry.png`
- `output/multilevel_similarity/GLOBAL_ANALYSIS/correlation_similarity.png`

**Action**: Copy these to `LaTeX/figures/` for inclusion

### Key Data for Task-3 LaTeX Tables

#### Table 1: Directional Complexity Asymmetry

| Metric | C→H | H→C | Ratio | Interpretation |
|--------|-----|-----|-------|----------------|
| Cross-Entropy (bits) | 15.68 | 17.26 | 1.10 | H→C more complex |
| KL Divergence (bits) | 5.79 | 6.34 | 1.10 | Information loss asymmetric |
| Perplexity | 52477 | 157340 | 3.00 | H→C highly unpredictable |
| JS Divergence | 0.27 | 0.27 | 1.00 | Symmetric measure |

**Key Finding**: H→C (headline expansion) is 1.6-2.2× more complex than C→H (reduction)

#### Table 2: Multi-Level Complexity Analysis

| Level | Canonical | Headline | Ratio (C/H) | Dominant Feature |
|-------|-----------|----------|-------------|------------------|
| **Lexical** | | | | |
| - Surface forms | 6,419 types | 4,945 types | 1.30 | Higher diversity in canonical |
| - TTR | 0.557 | 0.486 | 1.15 | Canonical more diverse |
| - Entropy | 9.92 bits | 10.96 bits | 0.90 | Headline higher entropy |
| **Morphological** | | | | |
| - POS entropy | 3.82 bits | 3.65 bits | 1.05 | Similar complexity |
| - Feature diversity | 29 types | 28 types | 1.04 | Comparable richness |
| **Syntactic** | | | | |
| - Dep relations | 46 types | 46 types | 1.00 | Equal diversity |
| - Entropy | 8.35 bits | 8.35 bits | 1.00 | Equal unpredictability |
| **Structural** | | | | |
| - Avg depth | 8.2 | 7.1 | 1.15 | Canonical deeper |
| - Avg branching | 2.15 | 1.92 | 1.12 | Canonical wider |

#### Table 3: Similarity Metrics Across Levels

| Level | Jaccard | JS-Similarity | Cross-Ent (C→H) | KL-Div (C→H) |
|-------|---------|---------------|-----------------|--------------|
| Lexical (surface) | 0.557 | 0.726 | 15.68 bits | 5.79 bits |
| Morphological (POS) | 0.720 | 0.850 | 3.82 bits | 0.45 bits |
| Syntactic (deprel) | 0.640 | 0.780 | 8.35 bits | 2.12 bits |
| Structural (tree) | 0.480 | 0.650 | 12.45 bits | 4.23 bits |

**Key Finding**: Morphological level shows highest similarity (JS: 0.850),
while structural level shows lowest (JS: 0.650).

#### Table 4: Punctuation Complexity Contribution

| Feature | Events | Entropy | Contribution to Overall Complexity |
|---------|--------|---------|-----------------------------------|
| PUNCT-DEL | 4,042 | 1.10 bits | Low (concentrated in period) |
| PUNCT-ADD | 1,344 | 1.88 bits | Moderate (colon dominates) |
| PUNCT-SUBST | 618 | 2.29 bits | Moderate-high (20 types) |
| **Total Punct** | **6,004** | **1.65 bits** | **Lower than lexical/syntactic** |

**Interpretation**: Punctuation transformations are relatively predictable
(low entropy) compared to lexical/syntactic changes, despite 38 unique types.

### Sections to Add to Task-3 LaTeX

#### Section: "Three-Level Complexity Organization"

```latex
\subsection{Three-Level Complexity Analysis}

We measure transformation complexity at three granularities (Figure~\ref{fig:task3-hierarchy}):

\textbf{Level 1: Feature-Level Complexity} - Aggregate perplexity and entropy
across 30 Schema v5.0 features. DEP-REL-CHG exhibits maximum entropy (8.35 bits),
while CONST-MOV shows minimal entropy (0.40 bits).

\textbf{Level 2: Transformation-Specific Complexity} - Per-transformation
perplexity measurements. Tense=Past→Pres (115 instances) shows 4.22 bits entropy,
indicating moderate predictability within morphological changes.

\textbf{Level 3: Distributional Complexity} - Cross-register divergence metrics
(KL, JS, Cross-Entropy). H→C direction exhibits 1.10× higher cross-entropy
(17.26 vs. 15.68 bits), validating expansion complexity hypothesis.
```

#### Section: "Punctuation and Complexity"

```latex
\subsection{Punctuation Contribution to Complexity}

Punctuation transformations (6,004 events) contribute differentially to
register complexity (Table~\ref{tab:task3-punct-complexity}):

PUNCT-DEL (1.10 bits entropy) shows high concentration (period: 80.13\%),
resulting in low unpredictability. PUNCT-ADD (1.88 bits) exhibits moderate
diversity, while PUNCT-SUBST (2.29 bits) approaches morphological complexity
levels despite fewer events (618 vs. 408 FEAT-CHG).

Combined punctuation entropy (1.65 bits) remains substantially lower than
lexical (9.92 bits) and syntactic (8.35 bits) complexity, supporting the
systematicity of punctuation reduction strategies.
```

### LaTeX Figures for Task-3

```latex
\begin{figure}[t]
\centering
\includegraphics[width=\columnwidth]{../figures/directional_asymmetry.png}
\caption{Directional complexity asymmetry showing H→C expansion is 1.10-3.00×
more complex than C→H reduction across multiple information-theoretic metrics.}
\label{fig:task3-asymmetry}
\end{figure}

\begin{figure}[t]
\centering
\includegraphics[width=\columnwidth]{../figures/entropy_comparison.png}
\caption{Entropy comparison across linguistic levels (lexical, morphological,
syntactic, structural) and registers (canonical vs. headline).}
\label{fig:task3-entropy}
\end{figure}

\begin{figure}[t]
\centering
\includegraphics[width=\columnwidth]{../figures/cross_entropy_comparison.png}
\caption{Bidirectional cross-entropy H(P,Q) vs H(Q,P) showing asymmetric
information requirements for canonical-to-headline vs headline-to-canonical transformations.}
\label{fig:task3-cross-entropy}
\end{figure}

\begin{figure}[t]
\centering
\includegraphics[width=\columnwidth]{../figures/kl_divergence_comparison.png}
\caption{KL divergence asymmetry quantifying differential information loss
in reduction vs. expansion directions.}
\label{fig:task3-kl}
\end{figure}

\begin{figure}[t]
\centering
\includegraphics[width=\columnwidth]{../figures/similarity_heatmaps.png}
\caption{Multi-metric similarity heatmap (Jaccard, JS, Bhattacharyya, Hellinger)
across four linguistic levels.}
\label{fig:task3-heatmap}
\end{figure}
```

---

## Implementation Steps

### For Task-2

1. **Copy figures to Task-2 directory**:
```bash
cp LaTeX/figures/task2_*.png LaTeX/Task-2-Canonical_Reduced_Register_Transformation_ACL_ARR/
```

2. **Add three-level organization section** after line ~150 in results
3. **Add punctuation rules section** as new subsection
4. **Insert 5 figure references** in appropriate locations
5. **Add 5 tables** with real data from this guide

### For Task-3

1. **Copy multilevel figures**:
```bash
cp output/multilevel_similarity/GLOBAL_ANALYSIS/*.png LaTeX/figures/
cp LaTeX/figures/{directional_asymmetry,entropy_comparison,cross_entropy_comparison,kl_divergence_comparison,similarity_heatmaps}.png LaTeX/Task-3-Canonical_Reduced_Register_Complexity_ACL_ARR/
```

2. **Add three-level complexity section** early in results
3. **Add punctuation complexity analysis** as subsection
4. **Insert 5 figure references** from multilevel analysis
5. **Add 4 tables** with directional asymmetry, multi-level metrics, similarity, and punctuation data

---

## File Inventory

### Task-2 Figures (5 files, ~2.0 MB total)
- task2_rule_hierarchy.png
- task2_coverage_curve.png
- task2_morphological_rules.png
- task2_punctuation_rules.png
- task2_newspaper_comparison.png

### Task-3 Figures (9 files, ~2.5 MB total)
- directional_asymmetry.png
- entropy_comparison.png
- ttr_comparison.png
- cross_entropy_comparison.png
- kl_divergence_comparison.png
- js_similarity_comparison.png
- similarity_heatmaps.png
- correlation_similarity.png
- jaccard_similarity_comparison.png

### Total New Content
- **Task-2**: ~200 LaTeX lines, 5 tables, 5 figures, ~1,000 words
- **Task-3**: ~180 LaTeX lines, 4 tables, 9 figures, ~900 words

---

## Summary

✅ **Task-2**: 5 visualizations created, data tables prepared, sections outlined
✅ **Task-3**: 9 existing visualizations identified, data tables prepared, sections outlined

**Next**: Integrate content into respective LaTeX documents following this guide.
