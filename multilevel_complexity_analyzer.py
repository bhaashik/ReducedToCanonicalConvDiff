#!/usr/bin/env python3
"""
Multi-Level Complexity Analyzer (Extended v2)

Analyzes register complexity at multiple linguistic levels:
  i.   Character level (char entropy, avg word length, MATTR on chars)
  ii.  Lexical / Token level (TTR variants, MATTR, MTLD, HD-D, Yule's K,
                              Brunet's W, Honore's H, hapax ratio, lexical density)
  iii. Morphological level (POS tags, morphological features, feature entropy)
  iv.  Dependency level (deprel entropy, MDD, MDD normalized, dep distance entropy,
                         prop long deps)
  v.   Constituency level (tree depth, branching, subordination index, clause density,
                           production rule entropy, right-branching ratio)

v2 additions (2026-02-19):
  - Character level (i) with char n-gram entropy
  - Enhanced lexical diversity: MATTR, MTLD, HD-D, Yule's K, Brunet's W, Honore's H
  - Lexical density (content-word ratio from POS tags)
  - MDD normalized vs random baseline; dep distance distribution entropy;
    proportion long dependencies (>5 positions)
  - Subordination index, clause density, production rule entropy, right-branching ratio

References:
  Covington & McFall 2010 (MATTR), McCarthy & Jarvis 2010 (MTLD, HD-D),
  Yule 1944, Brunet 1978, Honore 1979, Liu 2008 (MDD), Futrell et al. 2015 (MDD norm),
  Lu 2010 (subordination index, clause density).
"""

import json
import math
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional

from scipy.stats import entropy
from scipy.special import comb as spcomb
from conllu import parse_incr
from nltk import Tree


# ---------------------------------------------------------------------------
# Content POS tags for lexical density (Ure 1971)
# ---------------------------------------------------------------------------
CONTENT_POS = {'NOUN', 'VERB', 'ADJ', 'ADV'}


class MultiLevelComplexityAnalyzer:
    """Analyzes complexity at multiple linguistic levels (v2 extended)."""

    def __init__(self, newspaper: str):
        self.newspaper = newspaper
        self.project_root = Path(__file__).parent
        self.output_dir = self.project_root / 'output' / 'multilevel_complexity' / newspaper
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.paths = self._get_data_paths()

        self.results = {
            'character': {},
            'lexical': {},
            'morphological': {},
            'syntactic': {},
            'structural': {},
            'combined': {}
        }

    # =========================================================================
    # DATA PATHS
    # =========================================================================

    def _get_data_paths(self) -> Dict:
        data_root = self.project_root / 'data' / 'input'
        # The-Hindu and Times-of-India use "corrected-" prefix in plain-text files
        corrected = {'The-Hindu', 'Times-of-India'}
        if self.newspaper in corrected:
            can_txt = f'{self.newspaper}-corrected-canonical.txt'
            hl_txt  = f'{self.newspaper}-corrected-headlines.txt'
        else:
            can_txt = f'{self.newspaper}-canonical.txt'
            hl_txt  = f'{self.newspaper}-headlines.txt'

        return {
            'canonical_text': data_root / 'input-single-line-break' / can_txt,
            'headline_text':  data_root / 'input-single-line-break' / hl_txt,
            'canonical_dep':  data_root / 'dependecy-parsed' / f'{self.newspaper}-canonical-stanza-parsed-deps.conllu',
            'headline_dep':   data_root / 'dependecy-parsed' / f'{self.newspaper}-headlines-stanza-parsed-deps.conllu',
            'canonical_const': data_root / 'constituency-parsed' / f'{self.newspaper}-canonical-stanza-parsed-constituency.txt',
            'headline_const':  data_root / 'constituency-parsed' / f'{self.newspaper}-headlines-stanza-parsed-constituency.txt',
        }

    def _resolve_text_path(self, key: str) -> Optional[Path]:
        """Return path, falling back to non-corrected name if file absent."""
        p = self.paths[key]
        if p.exists():
            return p
        alt = Path(str(p).replace('-corrected-', '-'))
        if alt.exists():
            return alt
        return None

    # =========================================================================
    # LEXICAL DIVERSITY HELPERS
    # =========================================================================

    def _compute_mattr(self, words: List[str], window: int = 50) -> float:
        """Moving Average Type-Token Ratio (Covington & McFall 2010)."""
        if not words:
            return 0.0
        if len(words) <= window:
            return len(set(words)) / len(words)
        ttrs = [
            len(set(words[i:i + window])) / window
            for i in range(len(words) - window + 1)
        ]
        return float(np.mean(ttrs))

    def _compute_mtld(self, words: List[str], threshold: float = 0.720) -> float:
        """Measure of Textual Lexical Diversity (McCarthy & Jarvis 2010)."""
        if not words:
            return 0.0

        def _pass(seq):
            factors = 0.0
            start = 0
            for end in range(1, len(seq) + 1):
                window = seq[start:end]
                ttr = len(set(window)) / len(window)
                if ttr <= threshold:
                    factors += 1.0
                    start = end
            remaining = seq[start:]
            if remaining:
                r_ttr = len(set(remaining)) / len(remaining)
                denom = 1.0 - threshold
                if denom > 0:
                    factors += (1.0 - r_ttr) / denom
            return len(seq) / factors if factors > 0 else float(len(seq))

        return float((_pass(words) + _pass(list(reversed(words)))) / 2)

    def _compute_hdd(self, words: List[str], sample_size: int = 42) -> float:
        """Hypergeometric Distribution D / vocd-D (McCarthy & Jarvis 2010)."""
        n = len(words)
        if n == 0:
            return 0.0
        s = min(sample_size, n)
        counts = Counter(words)
        cn_s = spcomb(n, s, exact=False)
        if cn_s == 0:
            return 0.0
        hdd_sum = 0.0
        for freq in counts.values():
            if freq > n - s:
                prob = 1.0
            else:
                prob = 1.0 - spcomb(n - freq, s, exact=False) / cn_s
            hdd_sum += prob
        return float(hdd_sum / s)

    # =========================================================================
    # CHARACTER LEVEL ANALYSIS (level i)
    # =========================================================================

    def analyze_character_level(self):
        """Analyze character-level complexity."""
        print(f"\n{'='*80}")
        print(f"CHARACTER LEVEL ANALYSIS: {self.newspaper}")
        print(f"{'='*80}\n")

        canonical_chars, canonical_words = self._extract_chars('canonical')
        headline_chars,  headline_words  = self._extract_chars('headline')

        self.results['character'] = {
            'canonical': self._compute_char_metrics(canonical_chars, canonical_words, 'Canonical'),
            'headline':  self._compute_char_metrics(headline_chars,  headline_words,  'Headline'),
            'divergence': self._compute_char_divergence(canonical_chars, headline_chars),
        }
        print("✓ Character analysis complete")
        return self.results['character']

    def _extract_chars(self, register: str) -> Tuple[List[str], List[str]]:
        """Return (list_of_chars, list_of_words) from text file."""
        path = self._resolve_text_path(f'{register}_text')
        if path is None:
            return [], []

        chars, words = [], []
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                toks = line.lower().split()
                words.extend(toks)
                for tok in toks:
                    chars.extend(list(tok))
        return chars, words

    def _compute_char_metrics(self, chars: List[str], words: List[str], name: str) -> Dict:
        if not chars:
            return {}

        char_counts = Counter(chars)
        n_chars = len(chars)
        n_words = len(words)

        # Unigram entropy
        probs = np.array(list(char_counts.values())) / n_chars
        char_entropy = float(entropy(probs, base=2))

        # Bigram entropy
        bigrams = [''.join(chars[i:i+2]) for i in range(len(chars)-1)]
        if bigrams:
            bg_probs = np.array(list(Counter(bigrams).values()), dtype=float)
            bg_probs /= bg_probs.sum()
            bigram_entropy = float(entropy(bg_probs, base=2))
        else:
            bigram_entropy = 0.0

        # Trigram entropy
        trigrams = [''.join(chars[i:i+3]) for i in range(len(chars)-2)]
        if trigrams:
            tg_probs = np.array(list(Counter(trigrams).values()), dtype=float)
            tg_probs /= tg_probs.sum()
            trigram_entropy = float(entropy(tg_probs, base=2))
        else:
            trigram_entropy = 0.0

        avg_word_length = n_chars / n_words if n_words > 0 else 0.0
        char_ttr  = len(char_counts) / n_chars if n_chars > 0 else 0.0
        char_mattr = self._compute_mattr(chars, window=50)

        print(f"  {name:25s}: Chars={n_chars:6d}, UnigramH={char_entropy:.3f}b, "
              f"BigramH={bigram_entropy:.3f}b, AvgWLen={avg_word_length:.2f}")

        return {
            'n_chars':             n_chars,
            'n_words':             n_words,
            'n_char_types':        len(char_counts),
            'char_entropy':        char_entropy,
            'char_bigram_entropy': bigram_entropy,
            'char_trigram_entropy': trigram_entropy,
            'avg_word_length':     avg_word_length,
            'char_ttr':            char_ttr,
            'char_mattr':          char_mattr,
        }

    def _compute_char_divergence(self, chars1: List[str], chars2: List[str]) -> Dict:
        if not chars1 or not chars2:
            return {}
        return self._compute_divergence(chars1, chars2)

    # =========================================================================
    # LEXICAL LEVEL ANALYSIS (level ii)
    # =========================================================================

    def analyze_lexical_level(self):
        """Analyze lexical-level complexity."""
        print(f"\n{'='*80}")
        print(f"LEXICAL LEVEL ANALYSIS: {self.newspaper}")
        print(f"{'='*80}\n")

        canonical_surface = self._extract_surface_forms('canonical')
        headline_surface  = self._extract_surface_forms('headline')

        canonical_lemmas  = self._extract_lemmas('canonical')
        headline_lemmas   = self._extract_lemmas('headline')

        can_pos = self._extract_pos_tags('canonical')
        hl_pos  = self._extract_pos_tags('headline')

        compression = self._compute_compression_ratio()

        self.results['lexical'] = {
            'surface_forms': {
                'canonical':  self._compute_lexical_metrics(canonical_surface, 'Canonical Surface'),
                'headline':   self._compute_lexical_metrics(headline_surface,  'Headline Surface'),
                'divergence': self._compute_divergence(canonical_surface, headline_surface),
            },
            'lemmas': {
                'canonical':  self._compute_lexical_metrics(canonical_lemmas, 'Canonical Lemmas'),
                'headline':   self._compute_lexical_metrics(headline_lemmas,  'Headline Lemmas'),
                'divergence': self._compute_divergence(canonical_lemmas, headline_lemmas),
            },
            'lexical_density': {
                'canonical': self._compute_lexical_density(canonical_surface, can_pos, 'Canonical'),
                'headline':  self._compute_lexical_density(headline_surface,  hl_pos,  'Headline'),
            },
            'compression_ratio': compression,
        }
        print("✓ Lexical analysis complete")
        return self.results['lexical']

    def _extract_surface_forms(self, register: str) -> List[str]:
        path = self._resolve_text_path(f'{register}_text')
        if path is None:
            return []
        words = []
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                words.extend(line.strip().lower().split())
        return words

    def _extract_lemmas(self, register: str) -> List[str]:
        conllu_file = self.paths[f'{register}_dep']
        if not conllu_file.exists():
            return []
        lemmas = []
        with open(conllu_file, 'r', encoding='utf-8') as f:
            for sentence in parse_incr(f):
                for token in sentence:
                    if token['lemma']:
                        lemmas.append(token['lemma'].lower())
        return lemmas

    def _compute_lexical_metrics(self, words: List[str], name: str) -> Dict:
        """Compute lexical complexity metrics (v2 extended)."""
        if not words:
            return {}

        word_counts = Counter(words)
        types  = len(word_counts)
        tokens = len(words)

        ttr      = types / tokens if tokens > 0 else 0.0
        root_ttr = types / math.sqrt(tokens) if tokens > 0 else 0.0
        log_ttr  = types / math.log(tokens) if tokens > 1 else 0.0

        probs = np.array(list(word_counts.values())) / tokens
        lex_entropy   = float(entropy(probs, base=2))
        lex_perplexity = 2 ** lex_entropy

        hapax_count = sum(1 for c in word_counts.values() if c == 1)
        hapax_ratio = hapax_count / types if types > 0 else 0.0

        # v2 enhanced diversity
        mattr = self._compute_mattr(words, window=50)
        mtld  = self._compute_mtld(words, threshold=0.720)
        hdd   = self._compute_hdd(words, sample_size=42)

        # Yule's K = 1e4 * (sum(i^2 * V(i)) - N) / N^2
        freq_spectrum = Counter(word_counts.values())
        yules_k_num = sum(i * i * vi for i, vi in freq_spectrum.items()) - tokens
        yules_k = 1e4 * yules_k_num / (tokens * tokens) if tokens > 0 else 0.0

        # Brunet's W = N ^ (V ^ -0.172)
        brunets_w = tokens ** (types ** -0.172) if types > 0 and tokens > 0 else 0.0

        # Honore's H = 100 * log(N) / (1 - V1/V)
        if types > 0 and hapax_count < types and tokens > 1:
            honores_h = 100.0 * math.log(tokens) / (1.0 - hapax_count / types)
        else:
            honores_h = 0.0

        avg_frequency = tokens / types if types > 0 else 0.0

        print(f"  {name:25s}: Types={types:5d}, Tokens={tokens:6d}, TTR={ttr:.4f}, "
              f"MATTR={mattr:.4f}, MTLD={mtld:.2f}, H={lex_entropy:.4f}")

        return {
            'types':         types,
            'tokens':        tokens,
            'ttr':           ttr,
            'root_ttr':      root_ttr,
            'log_ttr':       log_ttr,
            'entropy':       lex_entropy,
            'perplexity':    lex_perplexity,
            'avg_frequency': avg_frequency,
            'hapax_count':   hapax_count,
            'hapax_ratio':   hapax_ratio,
            'mattr':         mattr,
            'mtld':          mtld,
            'hdd':           hdd,
            'yules_k':       yules_k,
            'brunets_w':     brunets_w,
            'honores_h':     honores_h,
        }

    def _compute_lexical_density(
        self, words: List[str], pos_tags: List[str], name: str
    ) -> Dict:
        """Lexical density = content words / total words (Ure 1971)."""
        if not words or not pos_tags:
            return {}
        n = min(len(words), len(pos_tags))
        content = sum(1 for p in pos_tags[:n] if p in CONTENT_POS)
        density = content / n if n > 0 else 0.0
        print(f"  Lex density {name}: {density:.4f}  (content={content}/{n})")
        return {'lexical_density': density, 'content_words': content, 'total_words': n}

    def _compute_compression_ratio(self) -> Dict:
        """Avg headline/canonical length ratio per sentence pair."""
        can_path = self._resolve_text_path('canonical_text')
        hl_path  = self._resolve_text_path('headline_text')
        if can_path is None or hl_path is None:
            return {}
        with open(can_path, 'r', encoding='utf-8') as f:
            can_sents = [l.strip() for l in f if l.strip()]
        with open(hl_path, 'r', encoding='utf-8') as f:
            hl_sents = [l.strip() for l in f if l.strip()]
        if not can_sents or not hl_sents:
            return {}
        char_ratios, tok_ratios = [], []
        for can, hl in zip(can_sents, hl_sents):
            if len(can) > 0:
                char_ratios.append(len(hl) / len(can))
            c_toks = len(can.split())
            if c_toks > 0:
                tok_ratios.append(len(hl.split()) / c_toks)
        return {
            'avg_char_compression':  float(np.mean(char_ratios))  if char_ratios  else 0.0,
            'avg_token_compression': float(np.mean(tok_ratios))   if tok_ratios   else 0.0,
            'sentence_pairs':        len(char_ratios),
        }

    def _compute_divergence(self, dist1: List[str], dist2: List[str]) -> Dict:
        """KL/JS divergence and overlap between two token distributions."""
        if not dist1 or not dist2:
            return {}
        vocab = set(dist1 + dist2)
        count1 = Counter(dist1)
        count2 = Counter(dist2)
        total1, total2 = len(dist1), len(dist2)
        alpha = 1e-10
        probs1 = np.array([(count1.get(w, 0) + alpha) / (total1 + alpha * len(vocab)) for w in vocab])
        probs2 = np.array([(count2.get(w, 0) + alpha) / (total2 + alpha * len(vocab)) for w in vocab])
        kl_1_2 = float(entropy(probs1, probs2, base=2))
        kl_2_1 = float(entropy(probs2, probs1, base=2))
        m = 0.5 * (probs1 + probs2)
        js_div = float(0.5 * entropy(probs1, m, base=2) + 0.5 * entropy(probs2, m, base=2))
        set1, set2 = set(dist1), set(dist2)
        overlap = len(set1 & set2) / min(len(set1), len(set2)) if min(len(set1), len(set2)) > 0 else 0.0
        print(f"    Divergence: KL(C→H)={kl_1_2:.4f}, KL(H→C)={kl_2_1:.4f}, JS={js_div:.4f}")
        return {
            'kl_divergence_canonical_to_headline': kl_1_2,
            'kl_divergence_headline_to_canonical': kl_2_1,
            'js_divergence':     js_div,
            'overlap_coefficient': overlap,
            'asymmetry':         abs(kl_1_2 - kl_2_1),
        }

    # =========================================================================
    # MORPHOLOGICAL LEVEL ANALYSIS (level iii)
    # =========================================================================

    def analyze_morphological_level(self):
        """Analyze morphological-level complexity."""
        print(f"\n{'='*80}")
        print(f"MORPHOLOGICAL LEVEL ANALYSIS: {self.newspaper}")
        print(f"{'='*80}\n")

        canonical_pos   = self._extract_pos_tags('canonical')
        headline_pos    = self._extract_pos_tags('headline')
        canonical_feats = self._extract_morph_features('canonical')
        headline_feats  = self._extract_morph_features('headline')

        self.results['morphological'] = {
            'pos_tags': {
                'canonical':  self._compute_lexical_metrics(canonical_pos, 'Canonical POS'),
                'headline':   self._compute_lexical_metrics(headline_pos,  'Headline POS'),
                'divergence': self._compute_divergence(canonical_pos, headline_pos),
            },
            'morph_features': {
                'canonical':  self._compute_feature_metrics(canonical_feats, 'Canonical Features'),
                'headline':   self._compute_feature_metrics(headline_feats,  'Headline Features'),
                'feature_divergence': self._compute_feature_divergence(canonical_feats, headline_feats),
            },
        }
        print("✓ Morphological analysis complete")
        return self.results['morphological']

    def _extract_pos_tags(self, register: str) -> List[str]:
        conllu_file = self.paths[f'{register}_dep']
        if not conllu_file.exists():
            return []
        tags = []
        with open(conllu_file, 'r', encoding='utf-8') as f:
            for sentence in parse_incr(f):
                for token in sentence:
                    if token['upos']:
                        tags.append(token['upos'])
        return tags

    def _extract_morph_features(self, register: str) -> List[str]:
        conllu_file = self.paths[f'{register}_dep']
        if not conllu_file.exists():
            return []
        features = []
        with open(conllu_file, 'r', encoding='utf-8') as f:
            for sentence in parse_incr(f):
                for token in sentence:
                    if token['feats']:
                        for fn, fv in token['feats'].items():
                            features.append(f"{fn}={fv}")
        return features

    def _compute_feature_metrics(self, features: List[str], name: str) -> Dict:
        if not features:
            return {}
        basic = self._compute_lexical_metrics(features, name)
        feature_types: Dict[str, List[str]] = defaultdict(list)
        for feat in features:
            if '=' in feat:
                fn, fv = feat.split('=', 1)
                feature_types[fn].append(fv)
        per_type = {}
        for fn, vals in feature_types.items():
            vc = Counter(vals)
            per_type[fn] = {
                'types':   len(vc),
                'tokens':  len(vals),
                'entropy': float(entropy(list(vc.values()), base=2)) if vals else 0.0,
            }
        basic['per_feature_type'] = per_type
        return basic

    def _compute_feature_divergence(self, feats1: List[str], feats2: List[str]) -> Dict:
        if not feats1 or not feats2:
            return {}
        overall = self._compute_divergence(feats1, feats2)
        ft1: Dict[str, List] = defaultdict(list)
        ft2: Dict[str, List] = defaultdict(list)
        for f in feats1:
            if '=' in f:
                fn, fv = f.split('=', 1); ft1[fn].append(fv)
        for f in feats2:
            if '=' in f:
                fn, fv = f.split('=', 1); ft2[fn].append(fv)
        per_type = {}
        for fn in set(ft1) | set(ft2):
            v1, v2 = ft1.get(fn, []), ft2.get(fn, [])
            if v1 and v2:
                per_type[fn] = self._compute_divergence(v1, v2)
        return {'overall': overall, 'per_feature_type': per_type}

    # =========================================================================
    # SYNTACTIC LEVEL ANALYSIS (level iv — deprel label distribution)
    # =========================================================================

    def analyze_syntactic_level(self):
        """Analyze syntactic-level complexity."""
        print(f"\n{'='*80}")
        print(f"SYNTACTIC LEVEL ANALYSIS: {self.newspaper}")
        print(f"{'='*80}\n")

        canonical_deps  = self._extract_dep_relations('canonical')
        headline_deps   = self._extract_dep_relations('headline')
        canonical_const = self._extract_const_labels('canonical')
        headline_const  = self._extract_const_labels('headline')

        self.results['syntactic'] = {
            'dependency_relations': {
                'canonical':  self._compute_lexical_metrics(canonical_deps,  'Canonical DepRels'),
                'headline':   self._compute_lexical_metrics(headline_deps,   'Headline DepRels'),
                'divergence': self._compute_divergence(canonical_deps, headline_deps),
            },
            'constituency_labels': {
                'canonical':  self._compute_lexical_metrics(canonical_const, 'Canonical Const'),
                'headline':   self._compute_lexical_metrics(headline_const,  'Headline Const'),
                'divergence': self._compute_divergence(canonical_const, headline_const),
            },
        }
        print("✓ Syntactic analysis complete")
        return self.results['syntactic']

    def _extract_dep_relations(self, register: str) -> List[str]:
        conllu_file = self.paths[f'{register}_dep']
        if not conllu_file.exists():
            return []
        dep_rels = []
        with open(conllu_file, 'r', encoding='utf-8') as f:
            for sentence in parse_incr(f):
                for token in sentence:
                    if token['deprel']:
                        dep_rels.append(token['deprel'])
        return dep_rels

    def _extract_const_labels(self, register: str) -> List[str]:
        const_file = self.paths[f'{register}_const']
        if not const_file.exists():
            return []
        labels = []
        with open(const_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    tree = Tree.fromstring(line)
                    for st in tree.subtrees():
                        if not isinstance(st[0], str):
                            labels.append(st.label())
                except Exception:
                    continue
        return labels

    # =========================================================================
    # STRUCTURAL LEVEL ANALYSIS (level v — trees)
    # =========================================================================

    def analyze_structural_level(self):
        """Analyze structural complexity (extended v2)."""
        print(f"\n{'='*80}")
        print(f"STRUCTURAL LEVEL ANALYSIS: {self.newspaper}")
        print(f"{'='*80}\n")

        canonical_trees     = self._load_constituency_trees('canonical')
        headline_trees      = self._load_constituency_trees('headline')
        canonical_dep_trees = self._load_dependency_trees('canonical')
        headline_dep_trees  = self._load_dependency_trees('headline')

        self.results['structural'] = {
            'constituency': {
                'canonical': self._compute_tree_metrics(canonical_trees,     'Canonical Trees'),
                'headline':  self._compute_tree_metrics(headline_trees,      'Headline Trees'),
            },
            'dependency': {
                'canonical': self._compute_dep_tree_metrics(canonical_dep_trees, 'Canonical Dep Trees'),
                'headline':  self._compute_dep_tree_metrics(headline_dep_trees,  'Headline Dep Trees'),
            },
        }
        print("✓ Structural analysis complete")
        return self.results['structural']

    def _load_constituency_trees(self, register: str) -> List[Tree]:
        const_file = self.paths[f'{register}_const']
        if not const_file.exists():
            return []
        trees = []
        with open(const_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    trees.append(Tree.fromstring(line))
                except Exception:
                    continue
        return trees

    def _load_dependency_trees(self, register: str) -> List:
        conllu_file = self.paths[f'{register}_dep']
        if not conllu_file.exists():
            return []
        trees = []
        with open(conllu_file, 'r', encoding='utf-8') as f:
            for sentence in parse_incr(f):
                trees.append(sentence)
        return trees

    def _compute_tree_metrics(self, trees: List[Tree], name: str) -> Dict:
        """Constituency tree metrics (extended: subordination index, clause density,
        production rule entropy, right-branching ratio)."""
        if not trees:
            return {}

        depths, sizes, branching_factors = [], [], []
        sbar_counts, s_counts, clause_densities = [], [], []
        production_rules: List[str] = []
        right_branch_fracs: List[float] = []

        for tree in trees:
            depths.append(tree.height())
            sizes.append(len(tree.leaves()))

            nts = [st for st in tree.subtrees() if not isinstance(st[0], str)]
            if nts:
                branching_factors.append(float(np.mean([len(list(nt)) for nt in nts])))

            labels = [st.label() for st in tree.subtrees()]
            n_sbar = labels.count('SBAR')
            n_s    = labels.count('S')
            sbar_counts.append(n_sbar)
            s_counts.append(n_s)
            clause_densities.append(n_sbar + n_s)

            for st in tree.subtrees():
                if isinstance(st[0], str):
                    continue
                ch_labels = tuple(
                    ch.label() if not isinstance(ch, str) else ch
                    for ch in st
                )
                production_rules.append(f"{st.label()} -> {' '.join(ch_labels)}")

            rb, nt_count = 0, 0
            for st in tree.subtrees():
                if isinstance(st[0], str):
                    continue
                nt_count += 1
                rightmost = st[-1]
                if not isinstance(rightmost, str) and hasattr(rightmost, '__iter__'):
                    rb += 1
            if nt_count > 0:
                right_branch_fracs.append(rb / nt_count)

        sub_indices = [
            sbar / s for sbar, s in zip(sbar_counts, s_counts) if s > 0
        ]
        rule_counts = Counter(production_rules)
        if rule_counts:
            prod_probs = np.array(list(rule_counts.values()), dtype=float)
            prod_probs /= prod_probs.sum()
            prod_rule_entropy = float(entropy(prod_probs, base=2))
        else:
            prod_rule_entropy = 0.0

        avg_depth    = float(np.mean(depths))    if depths    else 0.0
        avg_size     = float(np.mean(sizes))     if sizes     else 0.0
        avg_branching = float(np.mean(branching_factors)) if branching_factors else 0.0
        subordination_index = float(np.mean(sub_indices))     if sub_indices     else 0.0
        avg_clause_density  = float(np.mean(clause_densities)) if clause_densities else 0.0
        avg_right_branching = float(np.mean(right_branch_fracs)) if right_branch_fracs else 0.0

        print(f"  {name:25s}: Trees={len(trees):4d}, Depth={avg_depth:.2f}, "
              f"SubIdx={subordination_index:.3f}, ClauseDens={avg_clause_density:.2f}, "
              f"ProdRuleH={prod_rule_entropy:.3f}")

        return {
            'tree_count':                   len(trees),
            'avg_depth':                    avg_depth,
            'avg_size':                     avg_size,
            'avg_branching_factor':         avg_branching,
            'depth_std':                    float(np.std(depths)) if depths else 0.0,
            'size_std':                     float(np.std(sizes))  if sizes  else 0.0,
            'subordination_index':          subordination_index,
            'avg_clause_density':           avg_clause_density,
            'production_rule_entropy':      prod_rule_entropy,
            'avg_right_branching_ratio':    avg_right_branching,
        }

    def _compute_dep_tree_metrics(self, trees: List, name: str) -> Dict:
        """Dependency tree metrics (extended: MDD normalized, dep dist entropy,
        proportion of long dependencies > 5 positions)."""
        if not trees:
            return {}

        sent_lengths, avg_dep_dists, max_depths = [], [], []
        all_distances: List[int] = []
        long_dep_fracs: List[float] = []

        for sentence in trees:
            n = len(sentence)
            sent_lengths.append(n)

            distances = [
                abs(tok['id'] - tok['head'])
                for tok in sentence
                if tok['head'] is not None and tok['head'] > 0
            ]
            if distances:
                avg_dep_dists.append(float(np.mean(distances)))
                all_distances.extend(distances)
                long_dep_fracs.append(sum(1 for d in distances if d > 5) / len(distances))

            max_depths.append(self._compute_dep_tree_depth(sentence))

        mdd           = float(np.mean(avg_dep_dists))  if avg_dep_dists else 0.0
        avg_length    = float(np.mean(sent_lengths))   if sent_lengths  else 0.0
        avg_depth     = float(np.mean(max_depths))     if max_depths    else 0.0

        # MDD normalized vs random baseline ≈ (n+1)/3  (Futrell et al. 2015)
        baselines = [(n + 1) / 3.0 for n in sent_lengths if n > 0]
        mdd_normalized = mdd / float(np.mean(baselines)) \
            if baselines and np.mean(baselines) > 0 else 0.0

        # Dependency distance distribution entropy
        if all_distances:
            dist_probs = np.array(list(Counter(all_distances).values()), dtype=float)
            dist_probs /= dist_probs.sum()
            dep_dist_entropy = float(entropy(dist_probs, base=2))
        else:
            dep_dist_entropy = 0.0

        prop_long_deps = float(np.mean(long_dep_fracs)) if long_dep_fracs else 0.0

        print(f"  {name:25s}: Sents={len(trees):4d}, AvgLen={avg_length:.2f}, "
              f"MDD={mdd:.2f}, MDD_norm={mdd_normalized:.3f}, "
              f"DepDistH={dep_dist_entropy:.3f}, LongDep%={prop_long_deps*100:.1f}")

        return {
            'sentence_count':           len(trees),
            'avg_sentence_length':      avg_length,
            'avg_dependency_distance':  mdd,
            'mdd_normalized':           mdd_normalized,
            'dep_distance_entropy':     dep_dist_entropy,
            'prop_long_deps':           prop_long_deps,
            'avg_tree_depth':           avg_depth,
            'length_std':               float(np.std(sent_lengths)) if sent_lengths else 0.0,
        }

    def _compute_dep_tree_depth(self, sentence) -> int:
        if not sentence:
            return 0
        children: Dict[int, List[int]] = defaultdict(list)
        root_id = None
        for token in sentence:
            if token['head'] is None or token['head'] == 0:
                root_id = token['id']
            else:
                children[token['head']].append(token['id'])
        if root_id is None:
            return 0

        def get_depth(node_id):
            if node_id not in children:
                return 1
            return 1 + max(get_depth(c) for c in children[node_id])

        return get_depth(root_id)

    # =========================================================================
    # COMBINED ANALYSIS AND OUTPUT
    # =========================================================================

    def compute_combined_metrics(self):
        """Compute combined complexity scores across all levels."""
        print(f"\n{'='*80}")
        print(f"COMBINED COMPLEXITY ANALYSIS")
        print(f"{'='*80}\n")

        canonical_scores: Dict[str, float] = {}
        headline_scores:  Dict[str, float] = {}

        # Character
        if self.results.get('character'):
            canonical_scores['char_entropy'] = self.results['character'].get('canonical', {}).get('char_entropy', 0)
            headline_scores['char_entropy']  = self.results['character'].get('headline', {}).get('char_entropy', 0)

        # Lexical
        if self.results.get('lexical'):
            for k, v_key in [('lexical_surface_entropy', ('surface_forms', 'entropy')),
                              ('lexical_mattr',           ('surface_forms', 'mattr')),
                              ('lexical_mtld',            ('surface_forms', 'mtld'))]:
                sub, field = v_key
                canonical_scores[k] = self.results['lexical'][sub]['canonical'].get(field, 0)
                headline_scores[k]  = self.results['lexical'][sub]['headline'].get(field, 0)

        # Morphological
        if self.results.get('morphological'):
            canonical_scores['morph_pos_entropy']  = self.results['morphological']['pos_tags']['canonical'].get('entropy', 0)
            headline_scores['morph_pos_entropy']   = self.results['morphological']['pos_tags']['headline'].get('entropy', 0)
            canonical_scores['morph_feat_entropy'] = self.results['morphological']['morph_features']['canonical'].get('entropy', 0)
            headline_scores['morph_feat_entropy']  = self.results['morphological']['morph_features']['headline'].get('entropy', 0)

        # Syntactic
        if self.results.get('syntactic'):
            canonical_scores['synt_deprel_entropy'] = self.results['syntactic']['dependency_relations']['canonical'].get('entropy', 0)
            headline_scores['synt_deprel_entropy']  = self.results['syntactic']['dependency_relations']['headline'].get('entropy', 0)

        # Structural
        if self.results.get('structural'):
            canonical_scores['struct_tree_depth']   = self.results['structural']['constituency']['canonical'].get('avg_depth', 0)
            headline_scores['struct_tree_depth']    = self.results['structural']['constituency']['headline'].get('avg_depth', 0)
            canonical_scores['struct_dep_distance'] = self.results['structural']['dependency']['canonical'].get('avg_dependency_distance', 0)
            headline_scores['struct_dep_distance']  = self.results['structural']['dependency']['headline'].get('avg_dependency_distance', 0)
            canonical_scores['struct_prod_entropy'] = self.results['structural']['constituency']['canonical'].get('production_rule_entropy', 0)
            headline_scores['struct_prod_entropy']  = self.results['structural']['constituency']['headline'].get('production_rule_entropy', 0)

        canonical_aggregate = float(np.mean(list(canonical_scores.values()))) if canonical_scores else 0.0
        headline_aggregate  = float(np.mean(list(headline_scores.values()))) if headline_scores else 0.0
        complexity_ratio = canonical_aggregate / headline_aggregate if headline_aggregate > 0 else 1.0

        print(f"  Canonical Aggregate Complexity: {canonical_aggregate:.4f}")
        print(f"  Headline Aggregate Complexity:  {headline_aggregate:.4f}")
        print(f"  Complexity Ratio (C/H):         {complexity_ratio:.4f}")

        self.results['combined'] = {
            'canonical_scores':    canonical_scores,
            'headline_scores':     headline_scores,
            'canonical_aggregate': canonical_aggregate,
            'headline_aggregate':  headline_aggregate,
            'complexity_ratio':    complexity_ratio,
        }
        return self.results['combined']

    def save_results(self):
        """Save all results to JSON and CSV."""
        print(f"\n{'='*80}")
        print(f"SAVING RESULTS")
        print(f"{'='*80}\n")

        json_path = self.output_dir / 'multilevel_complexity_analysis.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"  ✓ Saved: {json_path}")

        summary_data = []

        def _add_rows(level, sublevel, metrics):
            if metrics and isinstance(metrics, dict):
                row = {'level': level, 'sublevel': sublevel}
                row.update({k: v for k, v in metrics.items() if isinstance(v, (int, float))})
                summary_data.append(row)

        # Character
        if self.results.get('character'):
            for reg in ['canonical', 'headline']:
                m = self.results['character'].get(reg, {})
                _add_rows('character', 'chars', {**m, 'register': reg})

        # Lexical
        if self.results.get('lexical'):
            for form_type in ['surface_forms', 'lemmas']:
                for reg in ['canonical', 'headline']:
                    m = self.results['lexical'][form_type][reg]
                    _add_rows('lexical', form_type, {**{k: v for k, v in m.items() if isinstance(v, (int, float))}, 'register': reg})

        # Morphological
        if self.results.get('morphological'):
            for ft in ['pos_tags', 'morph_features']:
                for reg in ['canonical', 'headline']:
                    m = self.results['morphological'][ft][reg]
                    _add_rows('morphological', ft, {**{k: v for k, v in m.items() if isinstance(v, (int, float))}, 'register': reg})

        # Syntactic
        if self.results.get('syntactic'):
            for st in ['dependency_relations', 'constituency_labels']:
                for reg in ['canonical', 'headline']:
                    m = self.results['syntactic'][st][reg]
                    _add_rows('syntactic', st, {**{k: v for k, v in m.items() if isinstance(v, (int, float))}, 'register': reg})

        # Structural
        if self.results.get('structural'):
            for st in ['constituency', 'dependency']:
                for reg in ['canonical', 'headline']:
                    m = self.results['structural'][st][reg]
                    _add_rows('structural', st, {**{k: v for k, v in m.items() if isinstance(v, (int, float))}, 'register': reg})

        df = pd.DataFrame(summary_data)
        csv_path = self.output_dir / 'multilevel_complexity_summary.csv'
        df.to_csv(csv_path, index=False)
        print(f"  ✓ Saved: {csv_path}")

        if self.results.get('combined'):
            c = self.results['combined']
            combined_df = pd.DataFrame({
                'metric':    list(c['canonical_scores'].keys()),
                'canonical': list(c['canonical_scores'].values()),
                'headline':  list(c['headline_scores'].values()),
            })
            combined_df['ratio'] = combined_df['canonical'] / combined_df['headline'].replace(0, 1)
            combined_path = self.output_dir / 'combined_complexity_scores.csv'
            combined_df.to_csv(combined_path, index=False)
            print(f"  ✓ Saved: {combined_path}")

        print("\n✓ All results saved")

    def run_complete_analysis(self):
        """Run complete multi-level analysis (v2 extended)."""
        print(f"\n{'='*80}")
        print(f"MULTI-LEVEL COMPLEXITY ANALYZER v2")
        print(f"Newspaper: {self.newspaper}")
        print(f"{'='*80}\n")

        self.analyze_character_level()
        self.analyze_lexical_level()
        self.analyze_morphological_level()
        self.analyze_syntactic_level()
        self.analyze_structural_level()
        self.compute_combined_metrics()
        self.save_results()

        print(f"\n{'='*80}")
        print(f"ANALYSIS COMPLETE — Results: {self.output_dir}")
        print(f"{'='*80}\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Multi-Level Complexity Analyzer v2")
    parser.add_argument(
        '--newspaper', default='Times-of-India',
        choices=['Times-of-India', 'Hindustan-Times', 'The-Hindu'],
    )
    args = parser.parse_args()
    MultiLevelComplexityAnalyzer(args.newspaper).run_complete_analysis()


if __name__ == '__main__':
    main()
