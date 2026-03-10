"""
eligible_site_counter.py
========================
Computes per-newspaper eligible site (opportunity) denominators for
opportunity normalization.  All counts are taken from the *canonical*
register; the headline register token count is used only to approximate
aligned-token-pair counts.

Eligible sites are the structural "slots" where a given feature *could*
have differed between canonical and reduced registers.  Dividing a raw
event count by the corresponding eligible-site count gives a per-opportunity
rate that is independent of both corpus size and linguistic-level granularity.
"""

import re
import sys
import os
from pathlib import Path

import conllu
from nltk import Tree

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from paths_config import CONLLU_FILES, CONST_FILES


# ---------------------------------------------------------------------------
# UPOS category sets
# ---------------------------------------------------------------------------
FUNCTION_WORD_UPOS = {"DET", "ADP", "AUX", "PART", "CCONJ", "SCONJ", "PRON"}
CONTENT_WORD_UPOS  = {"NOUN", "VERB", "ADJ", "ADV", "PROPN"}
VERB_UPOS          = {"VERB", "AUX"}
CLAUSE_LABELS      = {"S", "SBAR", "SINV", "SQ"}

# Sentence marker pattern in constituency files
_SENT_MARKER = re.compile(r"\(sentence\s+[\d.]+\)[^\n]*\n")


class EligibleSiteCounter:
    """
    Compute all eligible-site counts for a given newspaper.

    Usage
    -----
    counter = EligibleSiteCounter("The-Hindu")
    sites   = counter.get_all_site_counts()
    # sites is a dict: {site_name: int_count}
    """

    def __init__(self, newspaper: str):
        self.newspaper = newspaper
        self._sites: dict | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_all_site_counts(self) -> dict:
        """Return all eligible-site counts (cached after first call)."""
        if self._sites is None:
            sites = {}
            sites.update(self._count_from_conllu())
            sites.update(self._count_from_constituency())
            self._sites = sites
        return self._sites

    # ------------------------------------------------------------------
    # CoNLL-U counts
    # ------------------------------------------------------------------

    def _count_from_conllu(self) -> dict:
        np = self.newspaper
        canon_path    = CONLLU_FILES[np]["canonical"]
        headline_path = CONLLU_FILES[np]["headlines"]

        canon_sents    = self._load_conllu(canon_path)
        headline_sents = self._load_conllu(headline_path)

        counts = {
            "sentence_pairs":                    len(canon_sents),
            "tokens_canonical":                  0,
            "function_word_tokens_canonical":    0,
            "content_word_tokens_canonical":     0,
            "verb_tokens_canonical":             0,
            "morph_feature_slots_canonical":     0,
            "punct_tokens_canonical":            0,
            "aligned_token_pairs":               0,
        }

        # Per-sentence canonical token counts (for aligned-pair approximation)
        canon_len_per_sent = []

        for sent in canon_sents:
            sent_tok = 0
            for token in sent:
                if not isinstance(token["id"], int):   # skip multi-word spans
                    continue
                upos  = token.get("upos") or ""
                feats = token.get("feats") or {}
                counts["tokens_canonical"]              += 1
                counts["morph_feature_slots_canonical"] += len(feats)
                sent_tok += 1
                if upos in FUNCTION_WORD_UPOS:
                    counts["function_word_tokens_canonical"] += 1
                if upos in CONTENT_WORD_UPOS:
                    counts["content_word_tokens_canonical"]  += 1
                if upos in VERB_UPOS:
                    counts["verb_tokens_canonical"]          += 1
                if upos == "PUNCT":
                    counts["punct_tokens_canonical"]         += 1
            canon_len_per_sent.append(sent_tok)

        # aligned_token_pairs ≈ sum of min(len_canonical, len_headline) per sentence
        # This is an approximation; the actual aligner output is not stored separately.
        headline_len_per_sent = []
        for sent in headline_sents:
            n = sum(1 for t in sent if isinstance(t["id"], int))
            headline_len_per_sent.append(n)

        n_pairs = min(len(canon_len_per_sent), len(headline_len_per_sent))
        counts["aligned_token_pairs"] = sum(
            min(canon_len_per_sent[i], headline_len_per_sent[i])
            for i in range(n_pairs)
        )

        return counts

    @staticmethod
    def _load_conllu(path):
        with open(path, encoding="utf-8") as f:
            return conllu.parse(f.read())

    # ------------------------------------------------------------------
    # Constituency parse counts
    # ------------------------------------------------------------------

    def _count_from_constituency(self) -> dict:
        path = CONST_FILES[self.newspaper]["canonical"]
        with open(path, encoding="utf-8") as f:
            content = f.read()

        # Split file into per-tree blocks on sentence markers
        blocks = _SENT_MARKER.split(content)

        constituency_nodes = 0
        clause_nodes       = 0

        for block in blocks:
            block = block.strip()
            if not block:
                continue
            try:
                tree = Tree.fromstring(block)
                for subtree in tree.subtrees():
                    # Skip preterminal nodes (POS tag directly over a word string)
                    if len(subtree) == 1 and isinstance(subtree[0], str):
                        continue
                    constituency_nodes += 1
                    if subtree.label() in CLAUSE_LABELS:
                        clause_nodes += 1
            except Exception:
                continue

        return {
            "constituency_nodes_canonical": constituency_nodes,
            "clause_nodes_canonical":       clause_nodes,
        }
