# Sentence Compression as Tree Transduction

**Authors:** Trevor Anthony Cohn, Mirella Lapata
**Year:** 2009
**Journal:** Journal of Artificial Intelligence Research
**Volume:** 34, pages 637-674
**arXiv:** 1401.5693
**DOI:** 10.48550/arXiv.1401.5693

## Summary

This paper presents a foundational tree-to-tree transduction method for sentence compression, addressing structural transformations through synchronous tree substitution grammar. The approach enables systematic handling of syntactic changes during compression.

## Key Contributions

1. **Tree Transduction Framework**: Introduces a formal framework for modeling sentence compression as tree-to-tree transformations rather than string-to-string operations, capturing structural changes more accurately.

2. **Handling Structural Mismatches**: The method addresses "structural mismatches" by enabling "local distortion of the tree topology" - crucial for handling cases where compression requires syntactic restructuring, not just deletion.

3. **Synchronous Tree Substitution Grammar**: Uses STSG to model correspondences between source and compressed trees, allowing for principled handling of:
   - Node deletion
   - Subtree movement
   - Local restructuring

4. **Discriminative Training**: Describes a discriminative training method within a large margin framework, moving beyond purely generative approaches.

5. **Decoding Algorithm**: Provides an efficient decoding algorithm for finding optimal compressions under the model.

## Performance

The paper demonstrates "significant improvements over a state-of-the-art model" at the time of publication, establishing tree transduction as a viable approach for compression tasks.

## Relevance to Headline Analysis

This work is highly relevant because:
- Headlines involve systematic tree transformations (constituent movement, deletion, restructuring)
- The tree transduction framework can model morphosyntactic changes beyond simple deletion
- The approach handles structural mismatches that occur when headlines reorganize information
- The formalism provides a theoretical foundation for understanding headline transformations

## Methodology

The approach combines:
- Synchronous grammars for modeling tree-to-tree correspondences
- Large margin training for discriminative learning
- Dynamic programming for efficient decoding
- Evaluation on standard sentence compression datasets

## Connection to Tree Edit Distance

While this work focuses on learned transductions, it relates to tree edit distance (TED) approaches by explicitly modeling tree transformations. The synchronous grammar provides a more structured alternative to pure edit distance metrics.
