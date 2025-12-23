# Directional Cross-Register Complexity Analysis

## Executive Summary

This analysis reveals a **critical asymmetry** in cross-register transformation complexity: **H→C (Headline to Canonical) expansion is significantly more complex than C→H (Canonical to Headline) reduction**.

**Key Finding**: **H→C is 1.6-2.2x MORE COMPLEX than C→H**

| Newspaper | C→H Perplexity | H→C Perplexity | Ratio (C→H/H→C) | H→C Complexity |
|-----------|----------------|----------------|-----------------|----------------|
| Times-of-India | 70.03 | 116.22 | 0.603 | **1.7x higher** |
| Hindustan-Times | 57.46 | 124.92 | 0.460 | **2.2x higher** |
| The-Hindu | 53.35 | 85.72 | 0.622 | **1.6x higher** |

**Implication**: **Expanding headlines to canonical form is inherently more difficult** than reducing canonical text to headlines.

---

## Detailed Results

### Cross-Newspaper Summary

| Newspaper | Direction | Label | Transformations | Patterns | Perplexity | PP_norm | Entropy (bits) |
|-----------|-----------|-------|-----------------|----------|------------|---------|----------------|
| **Times-of-India** |
|| C→H | Reduction | 8,161 | 421 | 70.03 | 1.010 | 6.13 |
|| H→C | Expansion | 6,075 | 416 | **116.22** | 1.011 | **6.86** |
|| Bidirectional | Change | 19,258 | 482 | 16.14 | 1.006 | 4.01 |
| **Hindustan-Times** |
|| C→H | Reduction | 10,861 | 418 | 57.46 | 1.010 | 5.84 |
|| H→C | Expansion | 7,237 | 415 | **124.92** | 1.012 | **6.96** |
|| Bidirectional | Change | 19,174 | 330 | 8.47 | 1.006 | 3.08 |
| **The-Hindu** |
|| C→H | Reduction | 5,406 | 311 | 53.35 | 1.013 | 5.74 |
|| H→C | Expansion | 3,195 | 305 | **85.72** | 1.015 | **6.42** |
|| Bidirectional | Change | 9,366 | 250 | 11.20 | 1.010 | 3.49 |

### Event-Level Directionality (Times-of-India Example)

| Event Type | C→H Count | C→H PP | H→C Count | H→C PP | Dominant Direction |
|------------|-----------|--------|-----------|--------|-------------------|
| **DEP-REL-CHG** | 3,671 | 133.75 | 4,497 | **136.76** | H→C (more complex!) |
| **FW-DEL** | 2,241 | 3.87 | 0 | 0.00 | C→H only |
| **FW-ADD** | 0 | 0.00 | 170 | 4.06 | H→C only |
| **C-DEL** | 720 | 2.90 | 0 | 0.00 | C→H only |
| **C-ADD** | 0 | 0.00 | 540 | 2.37 | H→C only |
| **LENGTH-CHG** | 190 | 14.82 | 2 | 2.00 | C→H dominant |
| **FORM-CHG** | 37 | 34.33 | 15 | 12.47 | C→H higher PP |
| **CLAUSE-TYPE-CHG** | 986 | 1.00 | 680 | 1.30 | Balanced |

---

## Analysis

### Finding 1: H→C Expansion is Consistently More Complex

**Across all newspapers**:
- H→C perplexity: 85.72 - 124.92
- C→H perplexity: 53.35 - 70.03
- **H→C is 1.6-2.2x higher**

**Interpretation**:
- Expanding headlines to canonical form requires resolving more ambiguity
- Many possible canonical expansions exist for same headline
- Reduction (C→H) follows more constrained patterns

### Finding 2: H→C Has Higher Entropy

**Entropy comparison**:
- H→C entropy: 6.42 - 6.96 bits
- C→H entropy: 5.74 - 6.13 bits
- **Difference: ~0.7-0.8 bits (~13-15% higher)**

**Interpretation**:
- H→C transformations carry ~0.7-0.8 bits more uncertainty
- This translates to ~1.6-1.8x more equivalent transformation types
- Headline-to-canonical mapping is fundamentally more ambiguous

### Finding 3: Similar Pattern Counts Despite Different Complexity

**Pattern counts**:
- C→H patterns: 311 - 421
- H→C patterns: 305 - 416
- **Similar sizes** (difference <5%)

**But perplexity differs greatly**:
- Despite similar vocabulary size, H→C perplexity is much higher
- This means the H→C distribution is **less uniform** (more peaked/skewed)
- Some H→C patterns are very common, others very rare → higher uncertainty

**Interpretation**: Normalized PP is also higher for H→C (1.012-1.015 vs 1.010-1.013), confirming genuine per-choice complexity difference.

### Finding 4: Bidirectional Changes Show Lowest Complexity

**Bidirectional (value↔value changes)**:
- Perplexity: 8.47 - 16.14
- Much lower than either C→H or H→C
- Pattern counts: 250-482

**Interpretation**:
- Direct value substitutions (not involving ABSENT) are simpler
- These are typically morphological or lexical changes
- Follow more regular patterns than addition/deletion

### Finding 5: DEP-REL-CHG Dominates H→C Complexity

**Dependency relation changes**:
- C→H: 3,671-4,231 events, PP = 80-133
- H→C: 4,497-5,453 events, PP = 94-147
- **H→C has more events AND higher perplexity**

**Interpretation**:
- Restoring dependency structure from headlines is the main challenge
- Headlines use reduced syntactic structure
- Multiple valid syntactic expansions possible

### Finding 6: Function Word Operations are Directional

**Purely directional events**:
- **FW-DEL** (Function Word Deletion): C→H only (0 H→C events)
- **FW-ADD** (Function Word Addition): H→C only (0 C→H events)
- **C-DEL** (Constituent Deletion): C→H only
- **C-ADD** (Constituent Addition): H→C only

**Interpretation**:
- Clear directionality in structural operations
- Headlines delete function words and constituents
- Canonical text adds them back
- These operations are unambiguous in direction

### Finding 7: Hindustan-Times Shows Highest Asymmetry

**Complexity ratios**:
- Times-of-India: 0.603 (H→C 1.7x more complex)
- **Hindustan-Times: 0.460 (H→C 2.2x more complex)** ← highest
- The-Hindu: 0.622 (H→C 1.6x more complex)

**Interpretation**:
- Hindustan-Times headlines are most compressed
- Require most expansion to restore canonical form
- Highest "reduction intensity" in headline writing

### Finding 8: The-Hindu Shows Least Asymmetry

**The-Hindu metrics**:
- Lowest H→C perplexity: 85.72 (vs 116-125 for others)
- Ratio: 0.622 (least asymmetric)

**Interpretation**:
- The-Hindu headlines maintain more canonical structure
- Less aggressive reduction strategy
- Easier to expand back to canonical form

---

## Implications

### For Linguistic Theory

**1. Register Asymmetry is Fundamental**:
- Reduction (canonical→headline) is structurally simpler
- Expansion (headline→canonical) involves ambiguity resolution
- This is **not** just reverse operations - different complexity profiles

**2. Headline Writing is Constrained**:
- C→H lower perplexity indicates formulaic reduction strategies
- Writers follow consistent compression patterns
- Enables headline "style" recognition

**3. Canonical Restoration is Creative**:
- H→C higher perplexity indicates multiple valid expansions
- Readers/systems must choose among alternatives
- Requires semantic/pragmatic knowledge

### For MT and NLG Systems

**1. C→H (Headline Generation) is Easier**:
- Lower perplexity (53-70) indicates more predictable task
- ~311-421 patterns to learn
- Rule-based systems more viable
- **Aligns with bidirectional evaluation**: C2H METEOR (0.73-0.77) > H2C (0.50-0.63)

**2. H→C (Canonical Expansion) is Harder**:
- Higher perplexity (86-125) indicates less predictable task
- Multiple valid outputs
- Statistical/neural methods essential
- Single-reference evaluation will underestimate quality

**3. Training Data Implications**:
- H→C systems need more diverse examples
- C→H systems can work with fewer, more concentrated patterns
- Multi-reference evaluation critical for H→C

### For Rule-Based Systems

**1. C→H Rules are More Effective**:
- Lower perplexity → higher determinism
- Function word deletion (PP=3-5) highly regular
- Constituent removal (PP=3-4) systematic
- **Explains bidirectional evaluation C2H success**

**2. H→C Rules Face Challenges**:
- Higher perplexity → lower determinism
- Article insertion ambiguous (which article? where?)
- Auxiliary restoration context-dependent
- **Explains bidirectional evaluation H2C lower scores**

**3. Hybrid Approach Recommended**:
```
C→H: Primarily rule-based (PP 53-70)
  - FW-DEL rules (PP ~4)
  - CONST-REM rules (PP ~3-4)
  - Statistical for DEP-REL-CHG (PP 80-133)

H→C: Primarily statistical (PP 86-125)
  - Statistical for most operations
  - Rules only for deterministic cases
  - Context-aware models for DEP-REL-CHG (PP 94-147)
```

### For Evaluation Methodologies

**1. Directional Bias in Metrics**:
- BLEU/METEOR penalize H→C more severely
- H→C should use multi-reference evaluation
- C→H can use single-reference

**2. Perplexity-Based Evaluation**:
- Could normalize by inherent task perplexity
- H→C scores should account for higher baseline complexity
- Fairer comparison across directions

**3. Human Evaluation Critical for H→C**:
- Multiple valid outputs make automatic metrics unreliable
- Need acceptability judgments, not just similarity

---

## Connection to Previous Findings

### Bidirectional Transformation Evaluation

**Previous Finding**:
- C2H METEOR: 0.729-0.765 (good)
- H2C METEOR: 0.499-0.628 (moderate)
- **C2H consistently outperforms H2C**

**Perplexity Explanation**:
- C→H PP: 53-70 (more predictable) → higher METEOR possible
- H→C PP: 86-125 (less predictable) → lower METEOR expected
- **Perplexity predicts evaluation performance**

**Correlation**:
- Complexity ratio (C→H/H→C): 0.46-0.62
- Performance ratio (H2C/C2H METEOR): 0.65-0.82
- **Directional complexity explains performance gap**

### Morphological Integration

**Previous Finding**:
- Morphological transformations contribute 30-66% coverage
- Morphological PP: 22-38 (moderate)

**Directional Insight**:
- Bidirectional changes (including morphological): PP 8-16
- Much lower than pure C→H or H→C
- **Morphological changes are among simplest transformations**

### Progressive Coverage

**Previous Finding**:
- Optimal rule counts: 115-142
- Event-based rules needed

**Directional Insight**:
- C→H needs ~311-421 patterns
- H→C needs ~305-416 patterns
- Total ~616-837 patterns
- But bidirectional overlap reduces effective count
- **Explains why 115-142 rules achieve good coverage**

---

## Visualizations

### 1. Directional Complexity Comparison

**File**: `directional_complexity_comparison.png`

**4-Panel Layout**:

**Panel 1 - Perplexity by Direction**:
- C→H: 53-70 (lower bars)
- H→C: 86-125 (higher bars)
- Clear visual asymmetry

**Panel 2 - Normalized Perplexity**:
- C→H: 1.010-1.013
- H→C: 1.012-1.015
- Smaller difference but H→C still higher

**Panel 3 - Entropy**:
- C→H: 5.7-6.1 bits
- H→C: 6.4-7.0 bits
- ~0.7-0.8 bits difference

**Panel 4 - Pattern Count**:
- Similar counts (305-421)
- Despite similar vocabulary, perplexity differs
- Shows distribution shape matters more than size

### 2. Complexity Ratios

**File**: `complexity_ratios.png`

**Left Panel - Perplexity Ratio**:
- All newspapers below 1.0 line (red dashed)
- Hindustan-Times lowest (0.460)
- The-Hindu highest (0.622)
- **All show H→C > C→H**

**Right Panel - Normalized PP Ratio**:
- Similar pattern but smaller differences
- Confirms genuine per-choice complexity difference

### 3. Pattern Diversity Comparison

**File**: `pattern_diversity_comparison.png`

**Scatter Plot**:
- X-axis: C→H patterns
- Y-axis: H→C patterns
- All points near diagonal (similar counts)
- But perplexity tells different story
- **Shows why counting patterns is insufficient**

---

## Detailed Results

### Times-of-India

**C→H (Reduction)**:
- 8,161 transformations (24% of events)
- 421 patterns
- PP = 70.03, H = 6.13 bits
- Dominant events: FW-DEL (2,241), DEP-REL-CHG (3,671), C-DEL (720)

**H→C (Expansion)**:
- 6,075 transformations (18% of events)
- 416 patterns
- PP = 116.22, H = 6.86 bits (+0.73 bits)
- Dominant events: DEP-REL-CHG (4,497), C-ADD (540), FW-ADD (170)

**Complexity Ratio**: 0.603 (H→C is **1.7x more complex**)

### Hindustan-Times

**C→H (Reduction)**:
- 10,861 transformations (29% of events)
- 418 patterns
- PP = 57.46, H = 5.84 bits
- Dominant events: FW-DEL (3,210), DEP-REL-CHG (4,231), C-DEL (1,405)

**H→C (Expansion)**:
- 7,237 transformations (19% of events)
- 415 patterns
- PP = 124.92, H = 6.96 bits (+1.12 bits)
- Dominant events: DEP-REL-CHG (5,453), C-ADD (690), FW-ADD (266)

**Complexity Ratio**: 0.460 (H→C is **2.2x more complex** - highest asymmetry)

### The-Hindu

**C→H (Reduction)**:
- 5,406 transformations (30% of events)
- 311 patterns
- PP = 53.35, H = 5.74 bits
- Dominant events: FW-DEL (1,661), DEP-REL-CHG (2,058), C-DEL (447)

**H→C (Expansion)**:
- 3,195 transformations (18% of events)
- 305 patterns
- PP = 85.72, H = 6.42 bits (+0.68 bits)
- Dominant events: DEP-REL-CHG (2,321), C-ADD (200), FW-ADD (49)

**Complexity Ratio**: 0.622 (H→C is **1.6x more complex** - lowest asymmetry)

---

## Conclusions

### Primary Conclusions

**1. H→C Expansion is Fundamentally More Complex**:
- **1.6-2.2x higher perplexity** across all newspapers
- **0.7-1.1 bits higher entropy**
- Consistent pattern universally observed

**2. Asymmetry Stems from Ambiguity**:
- Headlines deliberately reduce information
- Canonical expansion requires guessing removed content
- Multiple valid expansions possible

**3. C→H Reduction is More Deterministic**:
- Lower perplexity indicates formulaic patterns
- Compression strategies are consistent
- Rule-based approaches viable

**4. Direction Explains Evaluation Performance**:
- C2H better METEOR (0.73-0.77) aligns with lower PP (53-70)
- H2C worse METEOR (0.50-0.63) aligns with higher PP (86-125)
- **Perplexity predicts task difficulty**

**5. Newspaper Differences Exist**:
- Hindustan-Times: Highest asymmetry (2.2x)
- The-Hindu: Lowest asymmetry (1.6x)
- Reflects different headline writing styles

**6. Syntactic Restructuring Drives Complexity**:
- DEP-REL-CHG dominates both directions
- Higher complexity in H→C direction
- Main bottleneck for expansion systems

**7. Function Word Operations are Unambiguous**:
- FW-DEL and FW-ADD are purely directional
- No overlap between C→H and H→C
- These operations add little complexity

### Answers to Research Question

**Q: Which cross-register direction is more difficult?**

**A: H→C (Headline → Canonical) is significantly more difficult**:
- **Quantitatively**: 1.6-2.2x higher perplexity
- **Linguistically**: Requires ambiguity resolution
- **Computationally**: Lower MT evaluation scores
- **Cognitively**: Readers must infer deleted content

This asymmetry is fundamental to the headline-canonical register pair and has important implications for both linguistic theory and computational modeling.

---

**Analysis Date**: 2025-12-23
**Total Events**: 88,733
**Directional Events**: C→H: 24,428 | H→C: 16,507 | Bidirectional: 47,798
**Complexity Range**: C→H (53-70 PP) vs H→C (86-125 PP)
