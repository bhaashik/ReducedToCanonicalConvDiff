# Topic-Wise Summary of Related Work

This document organizes the related work into thematic areas, showing how different research streams contribute to understanding register variation, headlines, and morphosyntactic transformations.

---

## Topic 1: Foundational Work on Headlines and Register

### Headlinese as a Linguistic Variety

**Mårdh (1980)**: "Headlinese: On the Grammar of English Front Page Headlines"
- First systematic linguistic study of headline grammar
- Coined and legitimized the term "headlinese"
- Documented core syntactic features: determiner deletion, tense patterns, ellipsis
- Established headlines as a coherent grammatical variety, not mere abbreviation

**Moncomble (2018)**: "The deviant syntax of headlinese and its role in the pragmatics of headlines"
- Modern pragmatic analysis building on Mårdh
- Argues headlinese serves pragmatic functions beyond space-saving
- Shows syntactic deviations optimize relevance and reader engagement
- Documents persistence of headlinese features in web-era journalism

**Synthesis**: These works establish that headlines constitute a systematic linguistic register with grammatical conventions that serve communicative and pragmatic functions. The patterns are not arbitrary compression but principled linguistic variation.

### Register Theory Framework

**Biber (1995, 2016)**: Multi-Dimensional Analysis of Register Variation
- Empirical, corpus-based approach to register identification
- Multi-dimensional framework: registers defined by co-occurring linguistic features
- Statistical methodology: factor analysis of 60+ grammatical features
- Dimension 1 (Involved vs. Informational) particularly relevant to news
- Extension to web registers (CORE corpus)

**Connection to Headlines**: Biber's framework provides the theoretical foundation for treating headlines as a register characterized by systematic patterns of linguistic features rather than situational context alone. His quantitative methodology validates frequency-based and statistical approaches to register comparison.

---

## Topic 2: Morphosyntactic Annotation and Universal Dependencies

### Universal Dependencies Framework

**Nivre et al. (2020)**: "Universal Dependencies v2: An Evergrowing Multilingual Treebank Collection"
- Cross-linguistically consistent annotation framework
- Three layers: word segmentation, morphology, syntax
- Standardized morphological features (20+ categories)
- CoNLL-U format with FEATS column for morphology
- 200+ treebanks in 150+ languages

**Stanza Parser** (Qi et al., 2020): Python NLP toolkit
- Neural pipeline for UD annotation
- Outputs CoNLL-U format with morphological features
- State-of-the-art accuracy for POS, morphology, dependencies
- Used for parsing both headlines and canonical sentences

**Relevance**: UD provides the standardized morphological feature inventory (Tense, Number, Mood, Person, etc.) that forms the foundation of morphosyntactic analysis. The framework ensures that features are consistently annotated across registers, enabling systematic comparison of headlines vs. canonical sentences.

---

## Topic 3: Text Compression and Sentence Simplification

### Tree-Based Approaches

**Cohn & Lapata (2009)**: "Sentence Compression as Tree Transduction"
- Tree-to-tree transduction using synchronous tree substitution grammar
- Handles structural mismatches through local tree topology distortion
- Discriminative training with large margin framework
- Models compression as systematic syntactic transformation

**Relevance to Headlines**: Headlines involve similar tree transformations (constituent deletion, movement, restructuring). The synchronous grammar framework provides formal tools for modeling bidirectional transformations between canonical and headline syntax.

### Edit-Based Approaches

**Omelianchuk et al. (2021)**: "Text Simplification by Tagging"
- Frames simplification as sequence tagging (KEEP, DELETE, REPLACE, INSERT)
- 11× faster than sequence-to-sequence approaches
- Pre-trained Transformers for contextualized representations
- Explicit edit operations enable interpretability

**Relevance**: Edit operations (DELETE, INSERT, REPLACE) map directly to difference event types in headline transformation:
- DELETE → FW-DEL, C-DEL, CONST-REM
- INSERT → H-ADD, CONST-ADD
- REPLACE → LEMMA-CHG, FORM-CHG, FEAT-CHG

The tagging framework could model both H→C (expansion) and C→H (compression) transformations.

### Neural Approaches

**Van et al. (2021)**: "Using Neural Text Simplification to Improve Downstream NLP Tasks"
- Text simplification for improving machine (not human) comprehension
- Two strategies: prediction-time simplification, training-time augmentation
- Gains on relation extraction (1.82-1.98%) and text classification (0.65%)
- Shows register transformations have practical NLP applications

**Synthesis**: These works demonstrate that text transformations can be modeled computationally through tree transduction, edit operations, or neural seq2seq. Each approach offers insights:
- **Tree transduction**: Captures structural transformations
- **Edit tagging**: Makes operations explicit and efficient
- **Neural methods**: Learn transformations from data

---

## Topic 4: Linguistic Compression and Summarization

### Human Compression Strategies

**Yin & van Schijndel (2023)**: "Linguistic Compression in Single-Sentence Human-Written Summaries"
- Corpus study of how humans compress information
- **Counter-intuitive finding**: Summaries show morphological expansion, not reduction
- Increased lexical diversity in summaries vs. sources
- Misalignment between writer strategies and reader preferences

**Implications for Headlines**:
- Challenges simplistic view of headlines as "reduced" language
- Suggests headlines may involve morphological transformations (not just deletion)
- Our finding that H→C is more complex than C→H aligns with expansion/complexity observations
- Highlights importance of studying bidirectional transformations

### Automatic Headline Generation

**Higurashi et al. (2018)**: "Extractive Headline Generation for Community Q&A"
- Learning-to-rank approach for extractive headline generation
- Identifies most informative substrings as headlines
- Domain: User-generated Q&A (different from professional journalism)
- Informativeness metrics for headline quality

**Relevance**: Shows headline generation is a cross-domain problem. While journalistic headlines follow headlinese conventions, extractive approaches reveal which text segments have headline-worthy properties. Complements our work by showing what makes text suitable for headline use.

---

## Topic 5: Methodological Connections

### Cross-Topic Integration

The related work integrates around several methodological themes:

**1. Multi-Feature Analysis**
- Biber: 60+ co-varying grammatical features define registers
- UD: 20+ morphological features systematically annotated
- Our work: 22 feature types (morphological, syntactic, lexical, structural)

**2. Transformation-Based Modeling**
- Cohn & Lapata: Tree transduction with edit operations
- Omelianchuk et al.: Explicit tagging of edits (DELETE, KEEP, INSERT)
- Our work: Difference events (DEL, ADD, CHG, MOV, REM)

**3. Bidirectionality**
- Yin & van Schijndel: Compression involves expansion in some dimensions
- Van et al.: Simplification improves both comprehension and computation
- Our work: H→C more complex than C→H (perplexity 1.6-2.2× higher)

**4. Corpus-Based Empiricism**
- Mårdh: Systematic description from newspaper corpora
- Biber: Statistical analysis of large multi-register corpora
- UD: Massive multilingual treebank collection
- Our work: 94,907 difference events from aligned parallel corpus

**5. Register as Systematic Variation**
- Halliday/Biber: Registers defined by situational and/or linguistic patterns
- Moncomble: Headlinese grammar serves pragmatic functions
- Our work: Headlines show systematic morphosyntactic transformations (60% rule-based)

---

## Gaps and Novel Contributions

### What Prior Work Lacks

1. **Morphological Detail**: Previous headline studies focus on syntax/lexicon; less attention to morphological features (Tense, Mood, Person, etc.)

2. **Bidirectional Analysis**: Most work studies compression (C→H) or simplification; less on expansion (H→C) and comparative complexity

3. **Transformation Rules**: Descriptive work (Mårdh, Moncomble) identifies patterns but doesn't extract systematic transformation rules at scale

4. **Quantitative Complexity**: Register studies describe differences but don't quantify directional complexity (perplexity, entropy)

### Our Contributions

1. **Complete Morphosyntactic Coverage**: 20 UD morphological features + syntactic + lexical transformations

2. **Bidirectional Complexity**: Perplexity analysis showing H→C is 1.6-2.2× more complex than C→H

3. **Rule Extraction**: 23 morphological + numerous syntactic/lexical transformation rules at 70-95% accuracy

4. **Multi-Newspaper Validation**: Cross-newspaper patterns show universal vs. publication-specific transformations

5. **Information-Theoretic Metrics**: Entropy, perplexity, cross-entropy for quantifying transformation difficulty

---

## Theoretical Integration

### Unified View of Headlines

Combining insights from all topics:

**Headlines are:**
1. A systematic linguistic register (Mårdh, Biber, Moncomble)
2. Characterized by co-occurring morphosyntactic features (Biber's dimensions)
3. Producible via systematic transformations (Cohn & Lapata, Omelianchuk et al.)
4. Not merely reduced but transformed across multiple dimensions (Yin & van Schijndel)
5. Requiring explicit morphological modeling (UD framework)
6. Computationally analyzable through tree/edit/feature-based methods

**Our work synthesizes**:
- Linguistic register theory (Biber, Halliday)
- Headline grammar (Mårdh, Moncomble)
- Morphosyntactic annotation (UD)
- Transformation modeling (Cohn & Lapata, Omelianchuk et al.)
- Information theory (complexity metrics)

to provide a comprehensive quantitative account of morphosyntactic transformations between canonical and reduced registers in English news.
