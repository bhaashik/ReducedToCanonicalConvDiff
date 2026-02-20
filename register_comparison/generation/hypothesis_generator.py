"""
Hypothesis Generator: Generates multiple candidate transformations for
each source sentence by varying which rules fire.

Each hypothesis uses a different rule subset/configuration, producing
diverse outputs that can be scored and ranked by CandidateRanker.

Hypothesis strategies:
  0: High-confidence only (conf >= 0.8), no structural rules
  1: All rules above threshold, with constituency filtering (status quo+)
  2: Feature changes + form rules only (no deletions, no structural)
  3: Deletions + form rules only (no feature changes, no structural)
  4: Deletions only (aggressive reduction for C2R)
  5: Random 50% subsample of rules (seed=1)
  6: Random 50% subsample of rules (seed=2)
  7: Identity (no transformation — baseline)
"""

from typing import Dict, List, Optional, Tuple

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from register_comparison.generation.bidirectional_rules import RuleSet
from register_comparison.generation.surface_realizer import SurfaceRealizer
from register_comparison.generation.sentence_transformer import (
    SentenceTransformer, TransformedSentence, MIN_APPLY_CONFIDENCE,
)


N_HYPOTHESES = 8


class HypothesisGenerator:
    """
    Generate multiple candidate transformations for a single sentence.

    Each hypothesis varies which rules fire, producing diverse outputs
    for downstream ranking.
    """

    def __init__(self, ruleset: RuleSet, realizer: SurfaceRealizer,
                 n_hypotheses: int = N_HYPOTHESES):
        self.ruleset = ruleset
        self.realizer = realizer
        self.n_hypotheses = n_hypotheses
        self.transformer = SentenceTransformer(ruleset, realizer)

    def generate(self, tokens: List[Dict],
                 const_tree_str: Optional[str] = None
                 ) -> List[TransformedSentence]:
        """
        Generate multiple candidate transformations for one sentence.

        Returns a list of TransformedSentence objects, one per hypothesis.
        """
        hypotheses = []

        for h_id in range(self.n_hypotheses):
            result = self._generate_hypothesis(h_id, tokens, const_tree_str)
            hypotheses.append(result)

        return hypotheses

    def _generate_hypothesis(self, h_id: int, tokens: List[Dict],
                             const_tree_str: Optional[str]
                             ) -> TransformedSentence:
        """Generate a single hypothesis by ID."""

        if h_id == 0:
            # High-confidence only, no structural
            return self.transformer.transform(
                tokens, const_tree_str=const_tree_str,
                hypothesis_id=0,
                min_confidence=0.8,
                allow_structural=False,
            )

        elif h_id == 1:
            # All rules above threshold (status quo + constituency fixes)
            return self.transformer.transform(
                tokens, const_tree_str=const_tree_str,
                hypothesis_id=1,
                min_confidence=MIN_APPLY_CONFIDENCE,
            )

        elif h_id == 2:
            # Feature changes + form rules only (no deletions, no structural)
            return self.transformer.transform(
                tokens, const_tree_str=const_tree_str,
                hypothesis_id=2,
                allow_deletions=False,
                allow_structural=False,
            )

        elif h_id == 3:
            # Deletions + form rules only (no feature changes, no structural)
            return self.transformer.transform(
                tokens, const_tree_str=const_tree_str,
                hypothesis_id=3,
                allow_feature_changes=False,
                allow_form_changes=True,
                allow_structural=False,
            )

        elif h_id == 4:
            # Deletions only (no feature changes, no form changes, no structural)
            return self.transformer.transform(
                tokens, const_tree_str=const_tree_str,
                hypothesis_id=4,
                allow_feature_changes=False,
                allow_form_changes=False,
                allow_structural=False,
            )

        elif h_id == 5:
            # Random 50% subsample (seed=1)
            return self.transformer.transform(
                tokens, const_tree_str=const_tree_str,
                hypothesis_id=5,
                rule_sample_seed=1,
                rule_sample_frac=0.5,
            )

        elif h_id == 6:
            # Random 50% subsample (seed=2)
            return self.transformer.transform(
                tokens, const_tree_str=const_tree_str,
                hypothesis_id=6,
                rule_sample_seed=2,
                rule_sample_frac=0.5,
            )

        elif h_id == 7:
            # Identity — no transformation
            source_text = self.realizer.realize(tokens)
            return TransformedSentence(
                source_tokens=tokens,
                transformed_tokens=tokens,
                generated_text=source_text,
                applied_actions=[],
                skipped_actions=[],
                conflict_count=0,
                hypothesis_id=7,
            )

        else:
            # Fallback: default transformation
            return self.transformer.transform(
                tokens, const_tree_str=const_tree_str,
                hypothesis_id=h_id,
            )

    def generate_batch(self, token_lists: List[List[Dict]],
                       const_trees: Optional[List[str]] = None
                       ) -> List[List[TransformedSentence]]:
        """Generate hypotheses for a batch of sentences."""
        results = []
        for i, tokens in enumerate(token_lists):
            tree = const_trees[i] if const_trees and i < len(const_trees) else None
            hypotheses = self.generate(tokens, tree)
            results.append(hypotheses)

            if (i + 1) % 50 == 0:
                print(f"    Generated hypotheses for {i + 1}/{len(token_lists)} sentences")

        return results
