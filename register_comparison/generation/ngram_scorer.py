"""
N-gram Language Model for Fluency Scoring.

Builds a trigram LM from the training corpus (target register) with
Laplace smoothing.  Used by CandidateRanker to score how fluent a
generated sentence sounds in the target register.
"""

import math
from collections import Counter, defaultdict
from typing import Dict, List, Tuple

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


# Sentinel tokens for n-gram boundaries
_BOS = "<s>"
_EOS = "</s>"


class NgramScorer:
    """
    Trigram language model with add-k (Laplace) smoothing.

    Usage::

        scorer = NgramScorer(n=3, smoothing=1.0)
        scorer.train(["The cat sat on the mat .", "Dogs run fast ."])
        score = scorer.score("The dog sat on the mat .")
    """

    def __init__(self, n: int = 3, smoothing: float = 1.0):
        self.n = n
        self.smoothing = smoothing

        # Counts: context_tuple -> Counter[next_word]
        self._counts: Dict[Tuple[str, ...], Counter] = defaultdict(Counter)
        # Total count per context
        self._context_totals: Dict[Tuple[str, ...], int] = defaultdict(int)
        # Vocabulary (for smoothing denominator)
        self._vocab: set = set()
        self._trained = False

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train(self, sentences: List[str]):
        """Build n-gram model from a list of space-separated sentences."""
        self._counts.clear()
        self._context_totals.clear()
        self._vocab = set()

        for sentence in sentences:
            tokens = self._tokenize(sentence)
            self._vocab.update(tokens)

            # Pad with BOS/EOS markers
            padded = [_BOS] * (self.n - 1) + tokens + [_EOS]

            for i in range(self.n - 1, len(padded)):
                context = tuple(padded[i - self.n + 1 : i])
                word = padded[i]
                self._counts[context][word] += 1
                self._context_totals[context] += 1

        # Add boundary tokens to vocab for smoothing
        self._vocab.add(_BOS)
        self._vocab.add(_EOS)
        self._trained = True

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def score(self, sentence: str) -> float:
        """
        Return average log-probability per token (higher = more fluent).

        Uses Laplace-smoothed probability:
            P(w | context) = (count(context, w) + k) / (count(context) + k*V)
        """
        if not self._trained:
            return 0.0

        tokens = self._tokenize(sentence)
        if not tokens:
            return -10.0  # heavily penalize empty output

        padded = [_BOS] * (self.n - 1) + tokens + [_EOS]
        V = len(self._vocab)
        k = self.smoothing
        total_log_prob = 0.0

        for i in range(self.n - 1, len(padded)):
            context = tuple(padded[i - self.n + 1 : i])
            word = padded[i]
            count_w = self._counts[context][word]
            count_ctx = self._context_totals[context]
            prob = (count_w + k) / (count_ctx + k * V)
            total_log_prob += math.log(prob)

        # Normalize by number of predicted tokens (including EOS)
        n_predicted = len(tokens) + 1  # +1 for EOS
        return total_log_prob / n_predicted

    def perplexity(self, sentence: str) -> float:
        """
        Return perplexity of the sentence (lower = more fluent).

        perplexity = exp(-avg_log_prob)
        """
        avg_log_prob = self.score(sentence)
        return math.exp(-avg_log_prob)

    # ------------------------------------------------------------------
    # Batch scoring
    # ------------------------------------------------------------------

    def score_batch(self, sentences: List[str]) -> List[float]:
        """Score multiple sentences."""
        return [self.score(s) for s in sentences]

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _tokenize(sentence: str) -> List[str]:
        """Simple whitespace tokenizer with lowercasing."""
        return sentence.lower().split()

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_statistics(self) -> Dict:
        """Return model statistics."""
        return {
            'n': self.n,
            'smoothing': self.smoothing,
            'vocab_size': len(self._vocab),
            'n_contexts': len(self._counts),
            'trained': self._trained,
        }
