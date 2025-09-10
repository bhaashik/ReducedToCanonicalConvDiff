
# Version 1

from typing import List, Tuple, Dict
from pathlib import Path
from conllu import TokenList
from nltk.tree import Tree

class AlignedSentencePair:
    def __init__(self, newspaper: str, sent_id: int,
                 canonical_text: str,
                 headline_text: str,
                 canonical_dep: TokenList,
                 headline_dep: TokenList,
                 canonical_const: Tree,
                 headline_const: Tree):
        self.newspaper = newspaper
        self.sent_id = sent_id
        self.canonical_text = canonical_text
        self.headline_text = headline_text
        self.canonical_dep = canonical_dep
        self.headline_dep = headline_dep
        self.canonical_const = canonical_const
        self.headline_const = headline_const

    def __repr__(self):
        return f"<AlignedSentencePair newspaper={self.newspaper} sent_id={self.sent_id}>"

class Aligner:
    def __init__(self,
                 texts_canonical: List[str],
                 texts_headlines: List[str],
                 deps_canonical: List[TokenList],
                 deps_headlines: List[TokenList],
                 consts_canonical: List[Tree],
                 consts_headlines: List[Tree],
                 newspaper_name: str):
        self.texts_canonical = texts_canonical
        self.texts_headlines = texts_headlines
        self.deps_canonical = deps_canonical
        self.deps_headlines = deps_headlines
        self.consts_canonical = consts_canonical
        self.consts_headlines = consts_headlines
        self.newspaper_name = newspaper_name

    def align(self) -> List[AlignedSentencePair]:
        """
        Assumes all lists are aligned by sentence order and length.
        Returns a list of AlignedSentencePair.
        """
        n = min(len(self.texts_canonical), len(self.texts_headlines),
                len(self.deps_canonical), len(self.deps_headlines),
                len(self.consts_canonical), len(self.consts_headlines))
        pairs = []
        for i in range(n):
            pair = AlignedSentencePair(
                newspaper=self.newspaper_name,
                sent_id=i + 1,  # 1-based sentence numbering
                canonical_text=self.texts_canonical[i],
                headline_text=self.texts_headlines[i],
                canonical_dep=self.deps_canonical[i],
                headline_dep=self.deps_headlines[i],
                canonical_const=self.consts_canonical[i],
                headline_const=self.consts_headlines[i]
            )
            pairs.append(pair)
        return pairs
