"""
Candidate Ranker: Scores and ranks multiple hypothesis transformations
using a combination of fluency (n-gram LM) and adequacy (token overlap,
length ratio, position preservation) scores.

Includes sanity filters that reject degenerate hypotheses before scoring.
"""

import math
from typing import Dict, List, Optional, Tuple

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from register_comparison.generation.sentence_transformer import TransformedSentence
from register_comparison.generation.ngram_scorer import NgramScorer


class CandidateRanker:
    """
    Score each hypothesis on fluency and adequacy, then select the best.

    Combined score = alpha * fluency_norm + (1 - alpha) * adequacy

    Args:
        ngram_scorer: Trained NgramScorer for fluency evaluation.
        alpha: Weight for fluency vs adequacy. 0.6 = 60% fluency.
        expected_length_ratio: Expected ratio of target/source lengths
            (from training data). Used for length adequacy score.
    """

    def __init__(self, ngram_scorer: NgramScorer,
                 alpha: float = 0.6,
                 expected_length_ratio: float = 1.0):
        self.ngram_scorer = ngram_scorer
        self.alpha = alpha
        self.expected_length_ratio = expected_length_ratio

    def rank(self, hypotheses: List[TransformedSentence],
             source_text: str) -> List[Tuple[TransformedSentence, float]]:
        """
        Rank hypotheses by combined score (descending).

        Returns list of (hypothesis, combined_score) tuples, sorted best-first.
        """
        if not hypotheses:
            return []

        source_words = source_text.lower().split()

        # Filter out degenerate hypotheses
        valid = []
        for h in hypotheses:
            if self._passes_sanity(h, source_words):
                valid.append(h)

        if not valid:
            # All hypotheses failed sanity — fall back to the one
            # closest to source length
            best = min(hypotheses,
                       key=lambda h: abs(len(h.generated_text.split()) - len(source_words)))
            return [(best, 0.0)]

        # Score each valid hypothesis
        scored = []
        fluency_scores = []
        adequacy_scores = []

        for h in valid:
            fluency = self._fluency_score(h.generated_text)
            adequacy = self._adequacy_score(h.generated_text, source_words)
            fluency_scores.append(fluency)
            adequacy_scores.append(adequacy)

        # Normalize fluency scores to [0, 1] range
        fluency_norm = self._normalize_scores(fluency_scores)

        for i, h in enumerate(valid):
            combined = (self.alpha * fluency_norm[i] +
                        (1 - self.alpha) * adequacy_scores[i])
            scored.append((h, combined))

        scored.sort(key=lambda x: -x[1])
        return scored

    def select_best(self, hypotheses: List[TransformedSentence],
                    source_text: str) -> TransformedSentence:
        """Select the single best hypothesis."""
        ranked = self.rank(hypotheses, source_text)
        return ranked[0][0]

    # ------------------------------------------------------------------
    # Sanity filters
    # ------------------------------------------------------------------

    def _passes_sanity(self, hypothesis: TransformedSentence,
                       source_words: List[str]) -> bool:
        """
        Reject degenerate hypotheses before scoring.

        Filters:
        - Empty or very short output (< 3 tokens)
        - > 50% punctuation tokens
        - Length too short (< 20% of source) or too long (> 200%)
        - Starts with lowercase when source doesn't
        """
        gen_words = hypothesis.generated_text.split()

        # Reject empty or very short
        if len(gen_words) < 3:
            return False

        # Reject if > 50% punctuation
        punct_count = sum(1 for w in gen_words if all(c in '.,!?;:"\'-()[]{}' for c in w))
        if punct_count > len(gen_words) * 0.5:
            return False

        # Length ratio check
        if source_words:
            ratio = len(gen_words) / len(source_words)
            if ratio < 0.2 or ratio > 2.0:
                return False

        # Capitalization check: reject if starts lowercase when source doesn't
        if (source_words and gen_words
                and source_words[0][0:1].isupper()
                and gen_words[0][0:1].islower()):
            return False

        return True

    # ------------------------------------------------------------------
    # Fluency score (from n-gram LM)
    # ------------------------------------------------------------------

    def _fluency_score(self, text: str) -> float:
        """
        Return log-probability per token from the n-gram LM.

        Higher = more fluent.
        """
        return self.ngram_scorer.score(text)

    # ------------------------------------------------------------------
    # Adequacy score
    # ------------------------------------------------------------------

    def _adequacy_score(self, gen_text: str, source_words: List[str]) -> float:
        """
        Combined adequacy score measuring how well the hypothesis
        preserves source content.

        Components:
        - Content word overlap (Jaccard of non-stopword tokens)
        - Length ratio match (how close to expected length)
        - Position preservation (Kendall tau of shared tokens)
        """
        gen_words = gen_text.lower().split()

        if not gen_words or not source_words:
            return 0.0

        # Content word overlap
        overlap = self._content_overlap(gen_words, source_words)

        # Length ratio
        expected_len = len(source_words) * self.expected_length_ratio
        length_score = min(len(gen_words), expected_len) / max(len(gen_words), expected_len) if expected_len > 0 else 0.0

        # Position preservation
        position_score = self._position_preservation(gen_words, source_words)

        # Weighted combination
        return 0.5 * overlap + 0.25 * length_score + 0.25 * position_score

    @staticmethod
    def _content_overlap(gen_words: List[str], source_words: List[str]) -> float:
        """Jaccard similarity of content words (excluding common stopwords)."""
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be',
                     'been', 'being', 'have', 'has', 'had', 'do', 'does',
                     'did', 'will', 'would', 'could', 'should', 'may',
                     'might', 'shall', 'can', 'to', 'of', 'in', 'for',
                     'on', 'with', 'at', 'by', 'from', 'as', 'into',
                     'that', 'which', 'who', 'whom', 'this', 'these',
                     'those', 'it', 'its', 'and', 'but', 'or', 'not',
                     '.', ',', '!', '?', ';', ':', '"', "'"}

        gen_content = set(w for w in gen_words if w not in stopwords)
        src_content = set(w for w in source_words if w not in stopwords)

        if not gen_content and not src_content:
            return 1.0
        if not gen_content or not src_content:
            return 0.0

        intersection = gen_content & src_content
        union = gen_content | src_content
        return len(intersection) / len(union)

    @staticmethod
    def _position_preservation(gen_words: List[str],
                               source_words: List[str]) -> float:
        """
        Kendall tau correlation of shared tokens between generated and source.

        Measures whether shared tokens appear in a similar order.
        """
        shared = set(gen_words) & set(source_words)
        if len(shared) < 2:
            return 1.0

        # Build position maps (first occurrence)
        gen_pos = {}
        for i, w in enumerate(gen_words):
            if w in shared and w not in gen_pos:
                gen_pos[w] = i
        src_pos = {}
        for i, w in enumerate(source_words):
            if w in shared and w not in src_pos:
                src_pos[w] = i

        common = sorted(shared)
        if len(common) < 2:
            return 1.0

        concordant = 0
        discordant = 0
        for i in range(len(common)):
            for j in range(i + 1, len(common)):
                a, b = common[i], common[j]
                if a not in gen_pos or b not in gen_pos or a not in src_pos or b not in src_pos:
                    continue
                gen_order = gen_pos[a] < gen_pos[b]
                src_order = src_pos[a] < src_pos[b]
                if gen_order == src_order:
                    concordant += 1
                else:
                    discordant += 1

        total = concordant + discordant
        if total == 0:
            return 1.0

        # Normalize to [0, 1]
        tau = (concordant - discordant) / total
        return (tau + 1) / 2  # Map [-1, 1] to [0, 1]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_scores(scores: List[float]) -> List[float]:
        """Normalize scores to [0, 1] using min-max normalization."""
        if not scores:
            return []
        if len(scores) == 1:
            return [1.0]

        min_s = min(scores)
        max_s = max(scores)
        rng = max_s - min_s

        if rng < 1e-10:
            return [0.5] * len(scores)

        return [(s - min_s) / rng for s in scores]
