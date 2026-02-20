#!/usr/bin/env python3
"""
Multi-Level Similarity Analyzer (Extended v2)

Measures register similarity at multiple linguistic levels:
  i.   Character level (chrF, char n-gram Jaccard, NCD)
  ii.  Lexical / Token level (Jaccard, Dice, Overlap, distributional)
  iii. Morphological level (POS tags, morphological features)
  iv.  Dependency level (deprels, dep bigrams)
  v.   Constituency level (tree label sets, structural correlations)

Key metrics:
  - Jaccard, Dice, Overlap set-based coefficients
  - Cross-entropy (both directions C→H and H→C)
  - KL divergence (both directions) + symmetrized KL
  - Jensen-Shannon divergence (symmetric, bounded)
  - Bhattacharyya coefficient, Hellinger distance
  - Wasserstein distance (scipy.stats.wasserstein_distance)
  - Pearson / Spearman correlations
  - chrF character n-gram F-score (Popovic 2015)
  - Character n-gram Jaccard (n=2,3,4)
  - Normalized Compression Distance / NCD (Cilibrasi & Vitanyi 2005)

v2 additions (2026-02-19):
  - Character-level similarity section (i)
  - Wasserstein distance in every distributional comparison
  - Explicit C2H / H2C column labeling (asymmetric measures)
  - Symmetrized versions: kl_symmetrized, cross_entropy_symmetrized

References:
  Popovic, WMT 2015 (chrF); Cilibrasi & Vitanyi 2005 (NCD);
  scipy.stats.wasserstein_distance; Kantorovich 1942 (Wasserstein).
"""

import json
import zlib
import math
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional, Set

from scipy.stats import entropy, spearmanr, pearsonr, wasserstein_distance
from scipy.spatial.distance import cosine
from conllu import parse_incr
from nltk import Tree
from nltk.metrics.distance import edit_distance


class MultiLevelSimilarityAnalyzer:
    """Analyzes similarity between registers at multiple linguistic levels (v2)."""

    def __init__(self, newspaper: str):
        self.newspaper = newspaper
        self.project_root = Path(__file__).parent
        self.output_dir = self.project_root / 'output' / 'multilevel_similarity' / newspaper
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.paths = self._get_data_paths()

        self.results = {
            'character':     {},
            'lexical':       {},
            'morphological': {},
            'syntactic':     {},
            'structural':    {},
            'combined':      {}
        }

    # =========================================================================
    # DATA PATHS
    # =========================================================================

    def _get_data_paths(self) -> Dict:
        data_root = self.project_root / 'data' / 'input'
        corrected = {'The-Hindu', 'Times-of-India'}
        if self.newspaper in corrected:
            can_txt = f'{self.newspaper}-corrected-canonical.txt'
            hl_txt  = f'{self.newspaper}-corrected-headlines.txt'
        else:
            can_txt = f'{self.newspaper}-canonical.txt'
            hl_txt  = f'{self.newspaper}-headlines.txt'

        return {
            'canonical_text':  data_root / 'input-single-line-break' / can_txt,
            'headline_text':   data_root / 'input-single-line-break' / hl_txt,
            'canonical_dep':   data_root / 'dependecy-parsed' / f'{self.newspaper}-canonical-stanza-parsed-deps.conllu',
            'headline_dep':    data_root / 'dependecy-parsed' / f'{self.newspaper}-headlines-stanza-parsed-deps.conllu',
            'canonical_const': data_root / 'constituency-parsed' / f'{self.newspaper}-canonical-stanza-parsed-constituency.txt',
            'headline_const':  data_root / 'constituency-parsed' / f'{self.newspaper}-headlines-stanza-parsed-constituency.txt',
        }

    def _resolve_text_path(self, key: str) -> Optional[Path]:
        p = self.paths[key]
        if p.exists():
            return p
        alt = Path(str(p).replace('-corrected-', '-'))
        if alt.exists():
            return alt
        return None

    # =========================================================================
    # CORE SIMILARITY UTILITIES
    # =========================================================================

    def _jaccard_similarity(self, set1: Set, set2: Set) -> float:
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0

    def _dice_coefficient(self, set1: Set, set2: Set) -> float:
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0
        return 2 * len(set1 & set2) / (len(set1) + len(set2))

    def _overlap_coefficient(self, set1: Set, set2: Set) -> float:
        if not set1 or not set2:
            return 0.0
        return len(set1 & set2) / min(len(set1), len(set2))

    def _distributional_similarity(self, dist1: Counter, dist2: Counter) -> Dict:
        """
        Comprehensive distributional similarity metrics (v2 + Wasserstein).

        Metrics: cross-entropy, KL divergence, symmetrized KL, JSD,
                 Bhattacharyya, Hellinger, perplexity, and (v2) Wasserstein distance.
        """
        all_keys = list(set(dist1.keys()) | set(dist2.keys()))
        if not all_keys:
            return {}

        total1 = sum(dist1.values())
        total2 = sum(dist2.values())
        alpha = 1e-10

        probs1 = np.array([(dist1.get(k, 0) + alpha) / (total1 + alpha * len(all_keys)) for k in all_keys])
        probs2 = np.array([(dist2.get(k, 0) + alpha) / (total2 + alpha * len(all_keys)) for k in all_keys])

        # Entropies
        entropy1 = float(entropy(probs1, base=2))
        entropy2 = float(entropy(probs2, base=2))

        # Cross-entropy H(P,Q) = -sum P log Q
        cross_entropy_1_2 = float(-np.sum(probs1 * np.log2(probs2 + 1e-15)))
        cross_entropy_2_1 = float(-np.sum(probs2 * np.log2(probs1 + 1e-15)))

        # Symmetrized cross-entropy
        cross_entropy_sym = 0.5 * (cross_entropy_1_2 + cross_entropy_2_1)

        # Per-token cross-entropy
        n_keys = len(all_keys)
        per_token_ce_1_2 = cross_entropy_1_2 / n_keys if n_keys > 0 else 0.0
        per_token_ce_2_1 = cross_entropy_2_1 / n_keys if n_keys > 0 else 0.0

        # KL divergence
        kl_1_2 = float(entropy(probs1, probs2, base=2))
        kl_2_1 = float(entropy(probs2, probs1, base=2))
        kl_sym  = kl_1_2 + kl_2_1                     # symmetrized KL

        max_entropy = float(np.log2(n_keys)) if n_keys > 0 else 1.0
        norm_kl_1_2 = kl_1_2 / max_entropy if max_entropy > 0 else 0.0
        norm_kl_2_1 = kl_2_1 / max_entropy if max_entropy > 0 else 0.0
        norm_ce_1_2 = cross_entropy_1_2 / max_entropy if max_entropy > 0 else 0.0
        norm_ce_2_1 = cross_entropy_2_1 / max_entropy if max_entropy > 0 else 0.0

        # Jensen-Shannon divergence (symmetric, bounded [0,1])
        m = 0.5 * (probs1 + probs2)
        js_div = float(0.5 * entropy(probs1, m, base=2) + 0.5 * entropy(probs2, m, base=2))
        js_sim = max(0.0, 1.0 - js_div)
        js_dist = math.sqrt(js_div)

        # Bhattacharyya coefficient
        bhatt_coeff = float(np.sum(np.sqrt(probs1 * probs2)))
        bhatt_dist  = float(-math.log(bhatt_coeff + 1e-15))

        # Hellinger distance
        hellinger_dist = float(math.sqrt(0.5 * float(np.sum((np.sqrt(probs1) - np.sqrt(probs2)) ** 2))))
        hellinger_sim  = 1.0 - hellinger_dist

        # Perplexity
        perp1 = 2 ** entropy1
        perp2 = 2 ** entropy2
        cross_perp_1_2 = 2 ** cross_entropy_1_2
        cross_perp_2_1 = 2 ** cross_entropy_2_1

        # v2: Wasserstein distance (Earth Mover's Distance)
        # Use numeric codes for each key so wasserstein can be computed
        positions = np.arange(len(all_keys), dtype=float)
        raw1 = np.array([dist1.get(k, 0) for k in all_keys], dtype=float)
        raw2 = np.array([dist2.get(k, 0) for k in all_keys], dtype=float)
        if raw1.sum() > 0 and raw2.sum() > 0:
            w1 = raw1 / raw1.sum()
            w2 = raw2 / raw2.sum()
            wasserstein_dist = float(wasserstein_distance(positions, positions, w1, w2))
        else:
            wasserstein_dist = 0.0
        # Normalize by vocab size so it's comparable across scales
        wasserstein_dist_norm = wasserstein_dist / n_keys if n_keys > 0 else 0.0

        return {
            # Self-entropies
            'entropy_C': entropy1,
            'entropy_H': entropy2,
            'normalized_entropy_C': entropy1 / max_entropy if max_entropy > 0 else 0.0,
            'normalized_entropy_H': entropy2 / max_entropy if max_entropy > 0 else 0.0,
            # Cross-entropy (both directions)
            'cross_entropy_C2H': cross_entropy_1_2,
            'cross_entropy_H2C': cross_entropy_2_1,
            'cross_entropy_symmetrized': cross_entropy_sym,
            'normalized_cross_entropy_C2H': norm_ce_1_2,
            'normalized_cross_entropy_H2C': norm_ce_2_1,
            'per_token_cross_entropy_C2H': per_token_ce_1_2,
            'per_token_cross_entropy_H2C': per_token_ce_2_1,
            # KL divergence
            'kl_divergence_C2H': kl_1_2,
            'kl_divergence_H2C': kl_2_1,
            'kl_symmetrized': kl_sym,
            'normalized_kl_C2H': norm_kl_1_2,
            'normalized_kl_H2C': norm_kl_2_1,
            # Jensen-Shannon
            'js_divergence': js_div,
            'js_similarity': js_sim,
            'js_distance':   js_dist,
            # Bhattacharyya
            'bhattacharyya_coefficient': bhatt_coeff,
            'bhattacharyya_distance':    bhatt_dist,
            # Hellinger
            'hellinger_distance':   hellinger_dist,
            'hellinger_similarity': hellinger_sim,
            # Perplexity
            'perplexity_C':       perp1,
            'perplexity_H':       perp2,
            'cross_perplexity_C2H': cross_perp_1_2,
            'cross_perplexity_H2C': cross_perp_2_1,
            # v2: Wasserstein
            'wasserstein_distance': wasserstein_dist,
            'wasserstein_distance_normalized': wasserstein_dist_norm,
            # Metadata
            'vocabulary_size': n_keys,
            'max_entropy':     max_entropy,
        }

    # =========================================================================
    # CHARACTER LEVEL SIMILARITY (level i — v2 new)
    # =========================================================================

    def analyze_character_similarity(self):
        """Analyze character-level similarity (v2 new)."""
        print(f"\n{'='*80}")
        print(f"CHARACTER LEVEL SIMILARITY: {self.newspaper}")
        print(f"{'='*80}\n")

        self.results['character'] = self._compute_char_similarity()
        print("✓ Character similarity complete")
        return self.results['character']

    def _compute_char_similarity(self) -> Dict:
        can_path = self._resolve_text_path('canonical_text')
        hl_path  = self._resolve_text_path('headline_text')
        if can_path is None or hl_path is None:
            return {}

        with open(can_path, 'r', encoding='utf-8') as f:
            can_sents = [l.strip() for l in f if l.strip()]
        with open(hl_path, 'r', encoding='utf-8') as f:
            hl_sents  = [l.strip() for l in f if l.strip()]

        if not can_sents or not hl_sents:
            return {}

        pairs = list(zip(can_sents, hl_sents))

        # chrF (character n-gram F-score, Popovic 2015)
        chrf_6_scores = [self._compute_chrf(c, h, n=6) for c, h in pairs]

        # Character n-gram Jaccard (average of n=2,3,4)
        char_jac_2 = [self._compute_char_ngram_jaccard(c, h, n=2) for c, h in pairs]
        char_jac_3 = [self._compute_char_ngram_jaccard(c, h, n=3) for c, h in pairs]
        char_jac_4 = [self._compute_char_ngram_jaccard(c, h, n=4) for c, h in pairs]
        char_jac_avg = [(j2 + j3 + j4) / 3 for j2, j3, j4 in zip(char_jac_2, char_jac_3, char_jac_4)]

        # Normalized Compression Distance (Cilibrasi & Vitanyi 2005)
        ncd_scores = [self._compute_ncd(c, h) for c, h in pairs]

        # Global character unigram distributional similarity
        can_all_chars = list(''.join(c.lower().replace(' ', '') for c in can_sents))
        hl_all_chars  = list(''.join(h.lower().replace(' ', '') for h in hl_sents))
        dist_sim = self._distributional_similarity(Counter(can_all_chars), Counter(hl_all_chars))

        avg_chrf      = float(np.mean(chrf_6_scores)) if chrf_6_scores else 0.0
        avg_char_jac  = float(np.mean(char_jac_avg))  if char_jac_avg  else 0.0
        avg_ncd       = float(np.mean(ncd_scores))    if ncd_scores    else 0.0
        avg_ncd_sim   = 1.0 - avg_ncd                 # NCD=0 → identical

        print(f"  chrF(6):  {avg_chrf:.4f}   CharNgramJac: {avg_char_jac:.4f}   NCD: {avg_ncd:.4f}")

        return {
            'chrf_n6':              avg_chrf,
            'char_ngram_jaccard_n2': float(np.mean(char_jac_2)),
            'char_ngram_jaccard_n3': float(np.mean(char_jac_3)),
            'char_ngram_jaccard_n4': float(np.mean(char_jac_4)),
            'char_ngram_jaccard_avg': avg_char_jac,
            'ncd':                  avg_ncd,
            'ncd_similarity':       avg_ncd_sim,
            'sentence_pairs':       len(pairs),
            **dist_sim,
        }

    def _compute_chrf(self, ref: str, hyp: str, n: int = 6, beta: float = 1.0) -> float:
        """Character n-gram F-score (Popovic 2015)."""
        def get_ngrams(s, k):
            return Counter(s[i:i+k] for i in range(len(s) - k + 1))

        ref_ng = get_ngrams(ref, n)
        hyp_ng = get_ngrams(hyp, n)

        n_ref = sum(ref_ng.values())
        n_hyp = sum(hyp_ng.values())
        if n_ref == 0 or n_hyp == 0:
            return 0.0

        tp = sum(min(ref_ng[k], hyp_ng[k]) for k in ref_ng)
        precision = tp / n_hyp
        recall    = tp / n_ref

        if precision + recall == 0:
            return 0.0
        return (1 + beta ** 2) * precision * recall / (beta ** 2 * precision + recall)

    def _compute_char_ngram_jaccard(self, s1: str, s2: str, n: int = 2) -> float:
        """Character n-gram Jaccard similarity."""
        def get_ngrams(s, k):
            return set(s[i:i+k] for i in range(len(s) - k + 1))
        ng1 = get_ngrams(s1.lower(), n)
        ng2 = get_ngrams(s2.lower(), n)
        if not ng1 and not ng2:
            return 1.0
        if not ng1 or not ng2:
            return 0.0
        return len(ng1 & ng2) / len(ng1 | ng2)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (Cilibrasi & Vitanyi 2005) via zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        c1 = len(zlib.compress(b1, level=9))
        c2 = len(zlib.compress(b2, level=9))
        c12 = len(zlib.compress(b1 + b2, level=9))
        denom = max(c1, c2)
        if denom == 0:
            return 0.0
        return max(0.0, min(1.0, (c12 - min(c1, c2)) / denom))

    # =========================================================================
    # LEXICAL LEVEL SIMILARITY (level ii)
    # =========================================================================

    def analyze_lexical_similarity(self):
        """Analyze lexical-level similarity."""
        print(f"\n{'='*80}")
        print(f"LEXICAL LEVEL SIMILARITY: {self.newspaper}")
        print(f"{'='*80}\n")

        canonical_surface = self._extract_surface_forms('canonical')
        headline_surface  = self._extract_surface_forms('headline')
        canonical_lemmas  = self._extract_lemmas('canonical')
        headline_lemmas   = self._extract_lemmas('headline')

        self.results['lexical'] = {
            'surface_forms': self._compute_lexical_similarity(canonical_surface, headline_surface, 'Surface Forms'),
            'lemmas':        self._compute_lexical_similarity(canonical_lemmas,  headline_lemmas,  'Lemmas'),
            'sentence_level': self._compute_sentence_level_similarity(),
        }
        print("✓ Lexical similarity complete")
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

    def _compute_lexical_similarity(self, words1: List[str], words2: List[str], name: str) -> Dict:
        if not words1 or not words2:
            return {}

        set1 = set(words1)
        set2 = set(words2)
        count1 = Counter(words1)
        count2 = Counter(words2)

        jaccard = self._jaccard_similarity(set1, set2)
        dice    = self._dice_coefficient(set1, set2)
        overlap = self._overlap_coefficient(set1, set2)

        dist_sim = self._distributional_similarity(count1, count2)

        shared_vocab   = len(set1 & set2)
        total_vocab    = len(set1 | set2)
        shared_words   = list(set1 & set2)

        if len(shared_words) > 1:
            f1 = [count1[w] for w in shared_words]
            f2 = [count2[w] for w in shared_words]
            spearman_corr, spearman_p = spearmanr(f1, f2)
            pearson_corr,  pearson_p  = pearsonr(f1, f2)
        else:
            spearman_corr = spearman_p = pearson_corr = pearson_p = 0.0

        print(f"  {name:20s}: Jaccard={jaccard:.4f}, JS-Sim={dist_sim.get('js_similarity', 0):.4f}, "
              f"Wasserstein={dist_sim.get('wasserstein_distance_normalized', 0):.4f}")

        return {
            'jaccard_similarity':      jaccard,
            'dice_coefficient':        dice,
            'overlap_coefficient':     overlap,
            'shared_vocabulary':       shared_vocab,
            'unique_to_canonical':     len(set1 - set2),
            'unique_to_headline':      len(set2 - set1),
            'total_vocabulary':        total_vocab,
            'vocabulary_overlap_ratio': shared_vocab / total_vocab if total_vocab > 0 else 0.0,
            'spearman_correlation':    float(spearman_corr),
            'spearman_p_value':        float(spearman_p),
            'pearson_correlation':     float(pearson_corr),
            'pearson_p_value':         float(pearson_p),
            **dist_sim,
        }

    def _compute_sentence_level_similarity(self) -> Dict:
        """Per-sentence similarity metrics (Jaccard, edit distance)."""
        can_path = self._resolve_text_path('canonical_text')
        hl_path  = self._resolve_text_path('headline_text')
        if can_path is None or hl_path is None:
            return {}

        with open(can_path, 'r', encoding='utf-8') as f:
            can_sents = [l.strip().lower() for l in f if l.strip()]
        with open(hl_path, 'r', encoding='utf-8') as f:
            hl_sents  = [l.strip().lower() for l in f if l.strip()]

        if len(can_sents) != len(hl_sents):
            print(f"  Warning: Sentence count mismatch ({len(can_sents)} vs {len(hl_sents)})")
            return {}

        edit_dists, jac_scores, overlap_ratios = [], [], []
        for can, hl in zip(can_sents, hl_sents):
            edit_dists.append(edit_distance(can, hl))
            can_tok = set(can.split())
            hl_tok  = set(hl.split())
            jac_scores.append(self._jaccard_similarity(can_tok, hl_tok))
            if can_tok:
                overlap_ratios.append(len(can_tok & hl_tok) / len(can_tok))

        max_ed = max(len(c) + len(h) for c, h in zip(can_sents, hl_sents))
        avg_ed = float(np.mean(edit_dists)) if edit_dists else 0.0
        norm_edit_sim = 1.0 - avg_ed / max_ed if max_ed > 0 else 0.0

        print(f"  Sentence-Level: Avg Jaccard={np.mean(jac_scores):.4f}, "
              f"Avg Edit Sim={norm_edit_sim:.4f}")

        return {
            'avg_edit_distance':        avg_ed,
            'normalized_edit_similarity': norm_edit_sim,
            'avg_jaccard_similarity':   float(np.mean(jac_scores)) if jac_scores else 0.0,
            'avg_token_overlap_ratio':  float(np.mean(overlap_ratios)) if overlap_ratios else 0.0,
            'sentence_count':           len(can_sents),
        }

    # =========================================================================
    # MORPHOLOGICAL LEVEL SIMILARITY (level iii)
    # =========================================================================

    def analyze_morphological_similarity(self):
        """Analyze morphological-level similarity."""
        print(f"\n{'='*80}")
        print(f"MORPHOLOGICAL LEVEL SIMILARITY: {self.newspaper}")
        print(f"{'='*80}\n")

        canonical_pos   = self._extract_pos_tags('canonical')
        headline_pos    = self._extract_pos_tags('headline')
        canonical_feats = self._extract_morph_features('canonical')
        headline_feats  = self._extract_morph_features('headline')

        self.results['morphological'] = {
            'pos_tags':     self._compute_morphological_similarity(canonical_pos,   headline_pos,   'POS Tags'),
            'morph_features': self._compute_morphological_similarity(canonical_feats, headline_feats, 'Morphological Features'),
            'feature_type_similarity': self._compute_feature_type_similarity(canonical_feats, headline_feats),
        }
        print("✓ Morphological similarity complete")
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

    def _compute_morphological_similarity(self, items1: List[str], items2: List[str], name: str) -> Dict:
        if not items1 or not items2:
            return {}
        set1 = set(items1)
        set2 = set(items2)
        jaccard = self._jaccard_similarity(set1, set2)
        dice    = self._dice_coefficient(set1, set2)
        overlap = self._overlap_coefficient(set1, set2)
        dist_sim = self._distributional_similarity(Counter(items1), Counter(items2))

        print(f"  {name:25s}: Jaccard={jaccard:.4f}, JS-Sim={dist_sim.get('js_similarity', 0):.4f}, "
              f"Wasserstein={dist_sim.get('wasserstein_distance_normalized', 0):.4f}")

        return {
            'jaccard_similarity':  jaccard,
            'dice_coefficient':    dice,
            'overlap_coefficient': overlap,
            'shared_types':        len(set1 & set2),
            'unique_to_canonical': len(set1 - set2),
            'unique_to_headline':  len(set2 - set1),
            **dist_sim,
        }

    def _compute_feature_type_similarity(self, feats1: List[str], feats2: List[str]) -> Dict:
        if not feats1 or not feats2:
            return {}
        ft1: Dict[str, List] = defaultdict(list)
        ft2: Dict[str, List] = defaultdict(list)
        for feat in feats1:
            if '=' in feat:
                fn, fv = feat.split('=', 1); ft1[fn].append(fv)
        for feat in feats2:
            if '=' in feat:
                fn, fv = feat.split('=', 1); ft2[fn].append(fv)
        per_type = {}
        for fn in set(ft1) | set(ft2):
            v1, v2 = ft1.get(fn, []), ft2.get(fn, [])
            if v1 and v2:
                ds = self._distributional_similarity(Counter(v1), Counter(v2))
                per_type[fn] = {
                    'jaccard_similarity':       self._jaccard_similarity(set(v1), set(v2)),
                    'js_similarity':            ds.get('js_similarity', 0),
                    'bhattacharyya_coefficient': ds.get('bhattacharyya_coefficient', 0),
                    'wasserstein_distance':     ds.get('wasserstein_distance', 0),
                }
        return per_type

    # =========================================================================
    # SYNTACTIC LEVEL SIMILARITY (level iv)
    # =========================================================================

    def analyze_syntactic_similarity(self):
        """Analyze syntactic-level similarity."""
        print(f"\n{'='*80}")
        print(f"SYNTACTIC LEVEL SIMILARITY: {self.newspaper}")
        print(f"{'='*80}\n")

        canonical_deps  = self._extract_dep_relations('canonical')
        headline_deps   = self._extract_dep_relations('headline')
        canonical_const = self._extract_const_labels('canonical')
        headline_const  = self._extract_const_labels('headline')
        canonical_bigrams = self._extract_dep_bigrams('canonical')
        headline_bigrams  = self._extract_dep_bigrams('headline')

        self.results['syntactic'] = {
            'dependency_relations': self._compute_morphological_similarity(canonical_deps,    headline_deps,    'Dependency Relations'),
            'constituency_labels':  self._compute_morphological_similarity(canonical_const,   headline_const,   'Constituency Labels'),
            'dependency_bigrams':   self._compute_morphological_similarity(canonical_bigrams, headline_bigrams, 'Dependency Bigrams'),
        }
        print("✓ Syntactic similarity complete")
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

    def _extract_dep_bigrams(self, register: str) -> List[str]:
        conllu_file = self.paths[f'{register}_dep']
        if not conllu_file.exists():
            return []
        bigrams = []
        with open(conllu_file, 'r', encoding='utf-8') as f:
            for sentence in parse_incr(f):
                for token in sentence:
                    if token['head'] is not None and token['head'] > 0:
                        head_idx = token['head'] - 1
                        if 0 <= head_idx < len(sentence):
                            head_pos = sentence[head_idx]['upos']
                            dep_pos  = token['upos']
                            rel      = token['deprel']
                            if head_pos and dep_pos and rel:
                                bigrams.append(f"{head_pos}-{rel}-{dep_pos}")
        return bigrams

    # =========================================================================
    # STRUCTURAL LEVEL SIMILARITY (level v)
    # =========================================================================

    def analyze_structural_similarity(self):
        """Analyze structural similarity (tree-based metrics)."""
        print(f"\n{'='*80}")
        print(f"STRUCTURAL LEVEL SIMILARITY: {self.newspaper}")
        print(f"{'='*80}\n")

        self.results['structural'] = {
            'constituency_trees': self._compute_tree_structure_similarity(),
            'dependency_trees':   self._compute_dependency_structure_similarity(),
        }
        print("✓ Structural similarity complete")
        return self.results['structural']

    def _compute_tree_structure_similarity(self) -> Dict:
        can_file = self.paths['canonical_const']
        hl_file  = self.paths['headline_const']
        if not can_file.exists() or not hl_file.exists():
            return {}

        def load_trees(path):
            trees = []
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            trees.append(Tree.fromstring(line))
                        except Exception:
                            trees.append(None)
            return trees

        can_trees = load_trees(can_file)
        hl_trees  = load_trees(hl_file)

        if len(can_trees) != len(hl_trees):
            print(f"  Warning: Tree count mismatch ({len(can_trees)} vs {len(hl_trees)})")
            return {}

        hcorrs, scorrs, label_sims = [], [], []
        for ct, ht in zip(can_trees, hl_trees):
            if ct is None or ht is None:
                continue
            hcorrs.append((ct.height(), ht.height()))
            scorrs.append((len(list(ct.subtrees())), len(list(ht.subtrees()))))
            cl = set(st.label() for st in ct.subtrees() if not isinstance(st[0], str))
            hl = set(st.label() for st in ht.subtrees() if not isinstance(st[0], str))
            label_sims.append(self._jaccard_similarity(cl, hl))

        def corr(pairs):
            if len(pairs) < 2:
                return 0.0, 1.0
            a, b = zip(*pairs)
            c, p = pearsonr(a, b)
            return float(c), float(p)

        h_corr, h_p = corr(hcorrs)
        s_corr, s_p = corr(scorrs)
        avg_label_sim = float(np.mean(label_sims)) if label_sims else 0.0

        print(f"  Constituency Trees: HeightCorr={h_corr:.4f}, SizeCorr={s_corr:.4f}, "
              f"AvgLabelSim={avg_label_sim:.4f}")

        return {
            'height_correlation':  h_corr,
            'height_p_value':      h_p,
            'size_correlation':    s_corr,
            'size_p_value':        s_p,
            'avg_label_similarity': avg_label_sim,
            'tree_pair_count':     len(label_sims),
        }

    def _compute_dependency_structure_similarity(self) -> Dict:
        can_file = self.paths['canonical_dep']
        hl_file  = self.paths['headline_dep']
        if not can_file.exists() or not hl_file.exists():
            return {}

        def load_dep(path):
            sents = []
            with open(path, 'r', encoding='utf-8') as f:
                for sentence in parse_incr(f):
                    sents.append(sentence)
            return sents

        can_sents = load_dep(can_file)
        hl_sents  = load_dep(hl_file)

        if len(can_sents) != len(hl_sents):
            print(f"  Warning: Sentence count mismatch ({len(can_sents)} vs {len(hl_sents)})")
            return {}

        len_pairs, dep_pairs, dist_pairs = [], [], []
        for cs, hs in zip(can_sents, hl_sents):
            len_pairs.append((len(cs), len(hs)))
            dep_pairs.append((self._tree_depth(cs), self._tree_depth(hs)))
            dist_pairs.append((self._avg_dep_dist(cs), self._avg_dep_dist(hs)))

        def corr(pairs):
            if len(pairs) < 2:
                return 0.0, 1.0
            a, b = zip(*pairs)
            c, p = pearsonr(a, b)
            return float(c), float(p)

        lc, lp = corr(len_pairs)
        dc, dp = corr(dep_pairs)
        rc, rp = corr(dist_pairs)

        print(f"  Dependency Trees:   LengthCorr={lc:.4f}, DepthCorr={dc:.4f}, DistCorr={rc:.4f}")

        return {
            'length_correlation':   lc,
            'length_p_value':       lp,
            'depth_correlation':    dc,
            'depth_p_value':        dp,
            'distance_correlation': rc,
            'distance_p_value':     rp,
            'sentence_pair_count':  len(len_pairs),
        }

    def _tree_depth(self, sentence) -> int:
        children: Dict[int, List[int]] = defaultdict(list)
        root_id = None
        for token in sentence:
            if token['head'] is None or token['head'] == 0:
                root_id = token['id']
            else:
                children[token['head']].append(token['id'])
        if root_id is None:
            return 0
        def _d(nid):
            if nid not in children:
                return 1
            return 1 + max(_d(c) for c in children[nid])
        return _d(root_id)

    def _avg_dep_dist(self, sentence) -> float:
        ds = [abs(t['id'] - t['head']) for t in sentence if t['head'] is not None and t['head'] > 0]
        return float(np.mean(ds)) if ds else 0.0

    # =========================================================================
    # COMBINED ANALYSIS AND OUTPUT
    # =========================================================================

    def compute_combined_similarity(self):
        """Compute combined similarity scores across all levels."""
        print(f"\n{'='*80}")
        print(f"COMBINED SIMILARITY ANALYSIS")
        print(f"{'='*80}\n")

        scores = {}

        # Character (new)
        if self.results.get('character'):
            scores['char_chrf']     = self.results['character'].get('chrf_n6', 0)
            scores['char_ncd_sim']  = self.results['character'].get('ncd_similarity', 0)
            scores['char_ngram_jac'] = self.results['character'].get('char_ngram_jaccard_avg', 0)

        # Lexical
        if self.results.get('lexical'):
            for sub, key in [('surface_forms', 'jaccard_similarity'), ('surface_forms', 'js_similarity')]:
                scores[f'lex_{key}'] = self.results['lexical'].get(sub, {}).get(key, 0)

        # Morphological
        if self.results.get('morphological'):
            scores['morph_pos_jaccard'] = self.results['morphological']['pos_tags'].get('jaccard_similarity', 0)
            scores['morph_pos_js']      = self.results['morphological']['pos_tags'].get('js_similarity', 0)

        # Syntactic
        if self.results.get('syntactic'):
            scores['synt_deprel_jaccard'] = self.results['syntactic']['dependency_relations'].get('jaccard_similarity', 0)
            scores['synt_deprel_js']      = self.results['syntactic']['dependency_relations'].get('js_similarity', 0)

        # Structural
        if self.results.get('structural'):
            scores['struct_height_corr'] = self.results['structural']['constituency_trees'].get('height_correlation', 0)
            scores['struct_label_sim']   = self.results['structural']['constituency_trees'].get('avg_label_similarity', 0)

        aggregate = float(np.mean(list(scores.values()))) if scores else 0.0
        print(f"  Aggregate Similarity Score: {aggregate:.4f}")

        self.results['combined'] = {'individual_scores': scores, 'aggregate_similarity': aggregate}
        return self.results['combined']

    def save_results(self):
        """Save all results to JSON and CSV."""
        print(f"\n{'='*80}")
        print(f"SAVING RESULTS")
        print(f"{'='*80}\n")

        json_path = self.output_dir / 'multilevel_similarity_analysis.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"  ✓ Saved: {json_path}")

        summary_data = []

        def add_metrics(level, sublevel, metrics_dict):
            if metrics_dict and isinstance(metrics_dict, dict):
                row = {'level': level, 'sublevel': sublevel,
                       **{k: v for k, v in metrics_dict.items() if isinstance(v, (int, float))}}
                summary_data.append(row)

        if self.results.get('character'):
            add_metrics('character', 'char_similarity', self.results['character'])

        if self.results.get('lexical'):
            for sub in ['surface_forms', 'lemmas', 'sentence_level']:
                add_metrics('lexical', sub, self.results['lexical'].get(sub, {}))

        if self.results.get('morphological'):
            for sub in ['pos_tags', 'morph_features']:
                add_metrics('morphological', sub, self.results['morphological'].get(sub, {}))

        if self.results.get('syntactic'):
            for sub in ['dependency_relations', 'constituency_labels', 'dependency_bigrams']:
                add_metrics('syntactic', sub, self.results['syntactic'].get(sub, {}))

        if self.results.get('structural'):
            for sub in ['constituency_trees', 'dependency_trees']:
                add_metrics('structural', sub, self.results['structural'].get(sub, {}))

        df = pd.DataFrame(summary_data)
        csv_path = self.output_dir / 'multilevel_similarity_summary.csv'
        df.to_csv(csv_path, index=False)
        print(f"  ✓ Saved: {csv_path}")

        if self.results.get('combined'):
            combined_df = pd.DataFrame({
                'metric':     list(self.results['combined']['individual_scores'].keys()),
                'similarity': list(self.results['combined']['individual_scores'].values()),
            })
            combined_path = self.output_dir / 'combined_similarity_scores.csv'
            combined_df.to_csv(combined_path, index=False)
            print(f"  ✓ Saved: {combined_path}")

        # v2: bidirectional metrics table
        bd_data = []
        for level, level_results in self.results.items():
            if not isinstance(level_results, dict):
                continue
            for sublevel, metrics in level_results.items():
                if not isinstance(metrics, dict):
                    continue
                row = {'level': level, 'sublevel': sublevel}
                for key in ['kl_divergence_C2H', 'kl_divergence_H2C', 'kl_symmetrized',
                            'cross_entropy_C2H', 'cross_entropy_H2C', 'cross_entropy_symmetrized',
                            'wasserstein_distance', 'js_divergence', 'js_similarity']:
                    if key in metrics:
                        row[key] = metrics[key]
                if len(row) > 2:
                    bd_data.append(row)

        if bd_data:
            bd_df = pd.DataFrame(bd_data)
            bd_path = self.output_dir / 'bidirectional_metrics.csv'
            bd_df.to_csv(bd_path, index=False)
            print(f"  ✓ Saved: {bd_path}")

        print("\n✓ All results saved")

    def run_complete_analysis(self):
        """Run complete multi-level similarity analysis (v2 extended)."""
        print(f"\n{'='*80}")
        print(f"MULTI-LEVEL SIMILARITY ANALYZER v2")
        print(f"Newspaper: {self.newspaper}")
        print(f"{'='*80}\n")

        self.analyze_character_similarity()
        self.analyze_lexical_similarity()
        self.analyze_morphological_similarity()
        self.analyze_syntactic_similarity()
        self.analyze_structural_similarity()
        self.compute_combined_similarity()
        self.save_results()

        print(f"\n{'='*80}")
        print(f"ANALYSIS COMPLETE — Results: {self.output_dir}")
        print(f"{'='*80}\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Multi-Level Similarity Analyzer v2")
    parser.add_argument(
        '--newspaper', default='Times-of-India',
        choices=['Times-of-India', 'Hindustan-Times', 'The-Hindu'],
    )
    args = parser.parse_args()
    MultiLevelSimilarityAnalyzer(args.newspaper).run_complete_analysis()


if __name__ == '__main__':
    main()
