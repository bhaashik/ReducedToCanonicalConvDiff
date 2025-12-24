# Universal Dependencies v2: An Evergrowing Multilingual Treebank Collection

**Authors:** Joakim Nivre, Marie-Catherine de Marneffe, Filip Ginter, Jan Hajič, Christopher D. Manning, Sampo Pyysalo, Sebastian Schuster, Francis Tyers, Daniel Zeman
**Year:** 2020
**Venue:** LREC 2020
**URL:** https://aclanthology.org/2020.lrec-1.497/

## Summary

This paper describes version 2 of the Universal Dependencies (UD) project, an open community effort to create cross-linguistically consistent treebank annotation for over 90 languages. UD has become the de facto standard for dependency parsing and morphological annotation in NLP.

## Universal Dependencies Framework

### Three Annotation Layers

1. **Word Segmentation**: Linguistically motivated tokenization and sentence splitting

2. **Morphological Layer**:
   - Lemmas (base forms)
   - Universal POS tags (UPOS) - 17 categories
   - Language-specific POS tags (XPOS)
   - **Morphological features (FEATS)** - standardized across languages

3. **Syntactic Layer**:
   - Dependency relations between words
   - Focus on predicate-argument structures
   - Universal relation taxonomy

## Key Features

**Cross-Linguistic Consistency**: The framework enables consistent annotation across typologically diverse languages while accommodating language-specific phenomena.

**Morphological Features**: UD defines a comprehensive set of morphological features including:
- Tense, Aspect, Mood, Voice (verbal categories)
- Number, Gender, Case (nominal categories)
- Person, Degree, Definiteness, and others
- Total of 20+ standardized features

**Open Community**: Over 600 contributors working on 200+ treebanks in 150+ languages, making it one of the largest collaborative linguistic annotation projects.

## Version 2 Enhancements

The paper discusses major changes from UD v1 to v2:
- Refined annotation guidelines
- Improved consistency across languages
- Enhanced morphological feature inventory
- Better handling of multi-word tokens
- Expanded language coverage

## Applications

**NLP Applications**:
- Syntactic parsing
- Semantic parsing
- Machine translation
- Morphological analysis
- Cross-lingual transfer learning

**Linguistic Research**:
- Typological studies
- Psycholinguistics
- Word order variation
- Morphosyntactic phenomena

## Relevance to Current Research

UD is foundational for morphosyntactic analysis because:
- Provides standardized morphological features used in register comparison
- Enables cross-linguistic comparison of grammatical phenomena
- CoNLL-U format is the standard output for parsers like Stanza
- Morphological features in Column 6 are exactly what we analyze in FEAT-CHG events

## Data Format: CoNLL-U

The CoNLL-U format includes 10 columns:
1. ID
2. FORM (word)
3. LEMMA
4. UPOS (universal POS)
5. XPOS (language-specific POS)
6. **FEATS (morphological features)** ← critical for our analysis
7. HEAD (dependency head)
8. DEPREL (dependency relation)
9. DEPS (enhanced dependencies)
10. MISC (miscellaneous annotations)

## Impact

With 200+ treebanks and widespread adoption, UD has become the standard framework for morphosyntactic annotation in computational linguistics, enabling consistent cross-linguistic analysis and serving as training data for state-of-the-art parsers.
