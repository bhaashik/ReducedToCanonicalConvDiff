"""
Surface Realizer: Converts modified CoNLL-U token lists back to surface text.

Builds an inflection table from the same corpus so that (lemma, UPOS, feats)
can be mapped to the most likely surface form.  Falls back to the lemma when
no inflected form is found.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass, field

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


@dataclass
class InflectionEntry:
    """One observed (lemma, UPOS, feats) → form mapping."""
    form: str
    frequency: int


class SurfaceRealizer:
    """
    Realizes surface text from a list of CoNLL-U-style token dicts.

    The inflection table is keyed by (lemma, upos, frozenset(feats.items()))
    and maps to the most-frequent surface form observed in the training corpus.
    """

    def __init__(self):
        # (lemma, upos, feats_key) → Counter[form]
        self._inflection_counts: Dict[Tuple, Counter] = defaultdict(Counter)
        # After build: (lemma, upos, feats_key) → best form
        self._inflection_table: Dict[Tuple, str] = {}
        # (lemma, upos) → Counter[form]  (fallback without feats)
        self._lemma_pos_counts: Dict[Tuple[str, str], Counter] = defaultdict(Counter)
        self._lemma_pos_table: Dict[Tuple[str, str], str] = {}
        self._built = False

    # ------------------------------------------------------------------
    # Building the inflection table from CoNLL-U files
    # ------------------------------------------------------------------

    def build_inflection_table(self, conllu_files: List[Path]):
        """
        Read all CoNLL-U files and build the inflection table.

        Each token contributes: (lemma, upos, feats) → form.
        """
        try:
            from conllu import parse_incr
        except ImportError:
            raise ImportError("Install conllu: pip install conllu")

        total_tokens = 0
        for conllu_path in conllu_files:
            if not conllu_path.exists():
                print(f"  Warning: {conllu_path} not found, skipping")
                continue
            with open(conllu_path, 'r', encoding='utf-8') as f:
                for token_list in parse_incr(f):
                    for token in token_list:
                        form = token.get('form', '')
                        lemma = token.get('lemma', '')
                        upos = token.get('upostag', '') or token.get('upos', '')
                        feats = token.get('feats') or {}

                        if not form or not lemma:
                            continue

                        feats_key = self._feats_to_key(feats)
                        self._inflection_counts[(lemma.lower(), upos, feats_key)][form] += 1
                        self._lemma_pos_counts[(lemma.lower(), upos)][form] += 1
                        total_tokens += 1

        # Build lookup tables from counts
        for key, counter in self._inflection_counts.items():
            self._inflection_table[key] = counter.most_common(1)[0][0]

        for key, counter in self._lemma_pos_counts.items():
            self._lemma_pos_table[key] = counter.most_common(1)[0][0]

        self._built = True
        print(f"  Inflection table built: {len(self._inflection_table)} entries "
              f"from {total_tokens} tokens, "
              f"{len(self._lemma_pos_table)} lemma-pos fallbacks")

    @staticmethod
    def _feats_to_key(feats: Dict) -> tuple:
        """Convert a feats dict to a hashable key."""
        if not feats:
            return ()
        return tuple(sorted(feats.items()))

    # ------------------------------------------------------------------
    # Inflection lookup
    # ------------------------------------------------------------------

    def inflect(self, lemma: str, upos: str,
                feats: Optional[Dict] = None) -> str:
        """
        Look up the surface form for (lemma, upos, feats).

        Falls back to (lemma, upos) without feats, then to the lemma itself.
        """
        if feats:
            feats_key = self._feats_to_key(feats)
            form = self._inflection_table.get((lemma.lower(), upos, feats_key))
            if form:
                return form

        # Fallback: lemma + pos only
        form = self._lemma_pos_table.get((lemma.lower(), upos))
        if form:
            return form

        # Last resort: return the lemma
        return lemma

    # ------------------------------------------------------------------
    # Surface realization from token list
    # ------------------------------------------------------------------

    def realize(self, tokens: List[Dict]) -> str:
        """
        Convert a list of CoNLL-U-style token dicts to surface text.

        Each token dict should have at least: 'form', 'lemma', 'upostag'.
        If 'form' is set and non-empty, it is used directly.
        Otherwise, we try to inflect from lemma + feats.

        Handles spacing around punctuation.
        """
        words = []
        for token in tokens:
            form = token.get('form', '')
            if not form:
                lemma = token.get('lemma', '')
                upos = token.get('upostag', '') or token.get('upos', '')
                feats = token.get('feats') or {}
                form = self.inflect(lemma, upos, feats)
            words.append(form)

        return self._join_words(words)

    @staticmethod
    def _join_words(words: List[str]) -> str:
        """Join words with proper spacing (no space before punctuation)."""
        if not words:
            return ''

        result = [words[0]]
        for w in words[1:]:
            if w in {'.', ',', '!', '?', ';', ':', "'s", "n't", "'re",
                     "'ve", "'ll", "'d", "'m", ")", "]", "}"}:
                result.append(w)
            elif result and result[-1] in {"(", "[", "{"}:
                result.append(w)
            else:
                result.append(' ')
                result.append(w)

        return ''.join(result)

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_statistics(self) -> Dict:
        return {
            'inflection_entries': len(self._inflection_table),
            'lemma_pos_entries': len(self._lemma_pos_table),
            'built': self._built,
        }

    def coverage_for_tokens(self, tokens: List[Dict]) -> Dict:
        """Compute how many tokens in a list have inflection table entries."""
        total = 0
        exact_hits = 0
        lemma_pos_hits = 0
        misses = 0

        for token in tokens:
            lemma = token.get('lemma', '')
            upos = token.get('upostag', '') or token.get('upos', '')
            feats = token.get('feats') or {}
            if not lemma:
                continue
            total += 1
            feats_key = self._feats_to_key(feats)
            if (lemma.lower(), upos, feats_key) in self._inflection_table:
                exact_hits += 1
            elif (lemma.lower(), upos) in self._lemma_pos_table:
                lemma_pos_hits += 1
            else:
                misses += 1

        return {
            'total': total,
            'exact_hits': exact_hits,
            'lemma_pos_hits': lemma_pos_hits,
            'misses': misses,
            'coverage_pct': (exact_hits + lemma_pos_hits) / total * 100 if total else 0,
        }
