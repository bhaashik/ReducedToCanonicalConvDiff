# Extractive Headline Generation Based on Learning to Rank for Community Question Answering

**Authors:** Tatsuru Higurashi, Hayato Kobayashi, Takeshi Masuyama, Kazuma Murao
**Year:** 2018
**Venue:** COLING 2018
**URL:** https://aclanthology.org/C18-1148/

## Summary

This paper addresses the challenge of automatically generating headlines for user-generated content on community question answering (CQA) platforms, where questions often lack appropriate titles or headlines.

## Problem Statement

User-generated content on CQA forums (like Stack Overflow, Quora, etc.) doesn't always come with appropriate headlines. Questions may have:
- Missing headlines
- Low-quality or uninformative titles
- Verbose descriptions without clear topic identification

## Proposed Method

**Extractive Approach**: The method extracts the most informative substring from each question to serve as its headline, rather than generating headlines from scratch.

**Learning to Rank Framework**: Uses a learning-to-rank approach to:
1. Identify candidate substrings from the question
2. Rank these candidates based on informativeness
3. Select the top-ranked substring as the headline

## Key Insights

1. **Extractive vs. Abstractive**: For CQA domains, extractive methods can be effective because questions often contain suitable headline text that just needs to be identified and extracted.

2. **Informativeness Metrics**: The paper develops metrics for assessing which portions of text would make effective headlines based on content coverage and conciseness.

3. **Domain Adaptation**: The approach is designed to work with community-generated content, which differs from professionally-written news where traditional headline generation methods are typically evaluated.

## Relevance to Headline Analysis

This work connects to headline research by:
- Demonstrating that headline generation is a cross-domain problem (news vs. CQA)
- Showing that extraction and selection are viable alternatives to generation
- Highlighting the importance of informativeness metrics in headline quality
- Providing insights into what makes text suitable for headline use

## Differences from News Headlines

Unlike news headlines:
- CQA headlines are extracted rather than professionally written
- Source material is conversational rather than journalistic
- Headlines must work for interactive Q&A contexts
- Less adherence to headlinese grammatical conventions

## Methodology

The system uses:
- Feature engineering for candidate substring ranking
- Machine learning models trained on CQA data with headlines
- Evaluation metrics including ROUGE and human judgments
- Comparison with baseline extractive methods
