#!/usr/bin/env python3
"""
Multi-Level Similarity Analyzer

Measures register similarity at multiple linguistic levels:
1. Lexical level (surface forms, lemmas)
2. Morphological level (POS tags, morphological features)
3. Syntactic level (dependency relations, constituency structures)
4. Structural level (tree-based alignment and similarity)
5. Semantic level (word embeddings, if available)

Key Similarity Metrics:
- Jaccard similarity (set overlap)
- Cosine similarity (vector similarity)
- Edit distance (Levenshtein, sequence alignment)
- Tree edit distance (structural similarity)
- Distributional similarity (KL, JS divergence as dissimilarity)
- Correlation measures (rank correlation, Pearson)
- Alignment metrics (precision, recall, F1)
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Set
import math
from scipy.stats import entropy, spearmanr, pearsonr
from scipy.spatial.distance import cosine, euclidean
from conllu import parse_incr
from nltk import Tree
from nltk.metrics.distance import edit_distance
import itertools


class MultiLevelSimilarityAnalyzer:
    """Analyzes similarity between registers at multiple linguistic levels."""

    def __init__(self, newspaper: str):
        self.newspaper = newspaper
        self.project_root = Path(__file__).parent
        self.output_dir = self.project_root / 'output' / 'multilevel_similarity' / newspaper
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Data paths
        self.paths = self._get_data_paths()

        # Results storage
        self.results = {
            'lexical': {},
            'morphological': {},
            'syntactic': {},
            'structural': {},
            'semantic': {},
            'combined': {}
        }

    def _get_data_paths(self) -> Dict:
        """Get paths to data files."""
        data_root = self.project_root / 'data' / 'input'

        return {
            'canonical_text': data_root / 'input-single-line-break' / f'{self.newspaper}-canonical.txt',
            'headline_text': data_root / 'input-single-line-break' / f'{self.newspaper}-headlines.txt',
            'canonical_dep': data_root / 'dependecy-parsed' / f'{self.newspaper}-canonical-parsed.conllu',
            'headline_dep': data_root / 'dependecy-parsed' / f'{self.newspaper}-headlines-parsed.conllu',
            'canonical_const': data_root / 'constituency-parsed' / f'{self.newspaper}-canonical-parsed.txt',
            'headline_const': data_root / 'constituency-parsed' / f'{self.newspaper}-headlines-parsed.txt'
        }

    # =====================================================================
    # UTILITY FUNCTIONS
    # =====================================================================

    def _jaccard_similarity(self, set1: Set, set2: Set) -> float:
        """Compute Jaccard similarity between two sets."""
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) == 0 or len(vec2) == 0:
            return 0.0

        # Normalize
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return np.dot(vec1, vec2) / (norm1 * norm2)

    def _dice_coefficient(self, set1: Set, set2: Set) -> float:
        """Compute Dice coefficient (Sørensen–Dice)."""
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        return 2 * intersection / (len(set1) + len(set2))

    def _overlap_coefficient(self, set1: Set, set2: Set) -> float:
        """Compute overlap coefficient (Szymkiewicz–Simpson)."""
        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        return intersection / min(len(set1), len(set2))

    def _distributional_similarity(self, dist1: Counter, dist2: Counter) -> Dict:
        """
        Compute comprehensive distributional similarity/divergence metrics.

        Based on SIMILARITY-METRICS.md:
        - Cross-entropy (both directions)
        - Relative entropy / KL divergence (both directions)
        - Conditional entropy
        - Jensen-Shannon divergence (symmetric, bounded)
        - Symmetrized KL
        - Bhattacharyya coefficient
        - Hellinger distance
        - Normalized variants
        """
        # Get all keys
        all_keys = set(dist1.keys()) | set(dist2.keys())

        if not all_keys:
            return {}

        # Convert to probability distributions
        total1 = sum(dist1.values())
        total2 = sum(dist2.values())

        # Add smoothing (Laplace smoothing with small alpha)
        alpha = 1e-10

        probs1 = np.array([(dist1.get(k, 0) + alpha) / (total1 + alpha * len(all_keys)) for k in all_keys])
        probs2 = np.array([(dist2.get(k, 0) + alpha) / (total2 + alpha * len(all_keys)) for k in all_keys])

        # === ENTROPY MEASURES ===

        # Shannon entropy (self-information)
        entropy1 = entropy(probs1, base=2)  # H(P)
        entropy2 = entropy(probs2, base=2)  # H(Q)

        # === CROSS-ENTROPY MEASURES (H(P,Q) and H(Q,P)) ===
        # Cross-entropy: H(P,Q) = -sum_x P(x) log Q(x)
        # Decomposition: H(P,Q) = H(P) + D_KL(P||Q)

        cross_entropy_1_2 = -np.sum(probs1 * np.log2(probs2 + 1e-15))  # H(P,Q): canonical wrt headline
        cross_entropy_2_1 = -np.sum(probs2 * np.log2(probs1 + 1e-15))  # H(Q,P): headline wrt canonical

        # Per-token cross-entropy (normalized by distribution size)
        per_token_cross_entropy_1_2 = cross_entropy_1_2 / len(all_keys) if len(all_keys) > 0 else 0
        per_token_cross_entropy_2_1 = cross_entropy_2_1 / len(all_keys) if len(all_keys) > 0 else 0

        # === RELATIVE ENTROPY / KL DIVERGENCE (D_KL(P||Q)) ===
        # KL divergence: D_KL(P||Q) = sum_x P(x) log(P(x)/Q(x))
        # Asymmetric (not a distance metric)

        kl_divergence_1_2 = entropy(probs1, probs2, base=2)  # D_KL(P||Q): canonical to headline
        kl_divergence_2_1 = entropy(probs2, probs1, base=2)  # D_KL(Q||P): headline to canonical

        # Verify: H(P,Q) = H(P) + D_KL(P||Q)
        # cross_entropy_1_2 should ≈ entropy1 + kl_divergence_1_2

        # === SYMMETRIZED KL DIVERGENCE ===
        # D_sym(P,Q) = D_KL(P||Q) + D_KL(Q||P)
        symmetrized_kl = kl_divergence_1_2 + kl_divergence_2_1

        # === JENSEN-SHANNON DIVERGENCE (bounded, symmetric) ===
        # JSD(P,Q) = 0.5 * D_KL(P||M) + 0.5 * D_KL(Q||M), where M = 0.5(P+Q)
        # Bounded: 0 ≤ JSD ≤ 1 (with base-2 logs)

        m = 0.5 * (probs1 + probs2)
        js_divergence = 0.5 * entropy(probs1, m, base=2) + 0.5 * entropy(probs2, m, base=2)

        # JS similarity (1 - JS divergence, range [0,1])
        js_similarity = 1 - js_divergence if js_divergence <= 1 else 0

        # JS distance (sqrt of JS divergence, forms a metric)
        js_distance = np.sqrt(js_divergence)

        # === BHATTACHARYYA COEFFICIENT (similarity measure) ===
        # BC(P,Q) = sum_x sqrt(P(x) * Q(x))
        # Range: [0, 1], where 1 = identical distributions

        bhattacharyya_coefficient = np.sum(np.sqrt(probs1 * probs2))

        # Bhattacharyya distance (derived from coefficient)
        # D_B = -ln(BC), range [0, ∞]
        bhattacharyya_distance = -np.log(bhattacharyya_coefficient + 1e-15)

        # === HELLINGER DISTANCE ===
        # H(P,Q) = sqrt(1/2 * sum_x (sqrt(P(x)) - sqrt(Q(x)))^2)
        # Bounded metric: range [0, 1]

        hellinger_distance = np.sqrt(0.5 * np.sum((np.sqrt(probs1) - np.sqrt(probs2)) ** 2))
        hellinger_similarity = 1 - hellinger_distance

        # === NORMALIZED METRICS ===

        # Maximum entropy for uniform distribution
        max_entropy = np.log2(len(all_keys)) if len(all_keys) > 0 else 1

        # Normalized entropies (range [0,1])
        normalized_entropy1 = entropy1 / max_entropy if max_entropy > 0 else 0
        normalized_entropy2 = entropy2 / max_entropy if max_entropy > 0 else 0

        # Normalized cross-entropies
        normalized_cross_entropy_1_2 = cross_entropy_1_2 / max_entropy if max_entropy > 0 else 0
        normalized_cross_entropy_2_1 = cross_entropy_2_1 / max_entropy if max_entropy > 0 else 0

        # Normalized KL divergence
        normalized_kl_1_2 = kl_divergence_1_2 / max_entropy if max_entropy > 0 else 0
        normalized_kl_2_1 = kl_divergence_2_1 / max_entropy if max_entropy > 0 else 0

        # === PERPLEXITY (exponentiated cross-entropy) ===
        # PPL = 2^H, measures "effective vocabulary size"

        perplexity_1 = 2 ** entropy1
        perplexity_2 = 2 ** entropy2
        cross_perplexity_1_2 = 2 ** cross_entropy_1_2
        cross_perplexity_2_1 = 2 ** cross_entropy_2_1

        # Normalized perplexity (by vocabulary size)
        vocab_size = len(all_keys)
        normalized_perplexity_1 = perplexity_1 / vocab_size if vocab_size > 0 else 0
        normalized_perplexity_2 = perplexity_2 / vocab_size if vocab_size > 0 else 0

        return {
            # === Basic Entropies ===
            'entropy_1': float(entropy1),
            'entropy_2': float(entropy2),
            'normalized_entropy_1': float(normalized_entropy1),
            'normalized_entropy_2': float(normalized_entropy2),

            # === Cross-Entropies (both directions) ===
            'cross_entropy_1_to_2': float(cross_entropy_1_2),
            'cross_entropy_2_to_1': float(cross_entropy_2_1),
            'normalized_cross_entropy_1_to_2': float(normalized_cross_entropy_1_2),
            'normalized_cross_entropy_2_to_1': float(normalized_cross_entropy_2_1),
            'per_token_cross_entropy_1_to_2': float(per_token_cross_entropy_1_2),
            'per_token_cross_entropy_2_to_1': float(per_token_cross_entropy_2_1),

            # === Relative Entropy / KL Divergence (both directions) ===
            'kl_divergence_1_to_2': float(kl_divergence_1_2),
            'kl_divergence_2_to_1': float(kl_divergence_2_1),
            'normalized_kl_1_to_2': float(normalized_kl_1_2),
            'normalized_kl_2_to_1': float(normalized_kl_2_1),
            'symmetrized_kl': float(symmetrized_kl),

            # === Jensen-Shannon (symmetric, bounded) ===
            'js_divergence': float(js_divergence),
            'js_similarity': float(js_similarity),
            'js_distance': float(js_distance),

            # === Bhattacharyya ===
            'bhattacharyya_coefficient': float(bhattacharyya_coefficient),
            'bhattacharyya_distance': float(bhattacharyya_distance),

            # === Hellinger ===
            'hellinger_distance': float(hellinger_distance),
            'hellinger_similarity': float(hellinger_similarity),

            # === Perplexity ===
            'perplexity_1': float(perplexity_1),
            'perplexity_2': float(perplexity_2),
            'cross_perplexity_1_to_2': float(cross_perplexity_1_2),
            'cross_perplexity_2_to_1': float(cross_perplexity_2_1),
            'normalized_perplexity_1': float(normalized_perplexity_1),
            'normalized_perplexity_2': float(normalized_perplexity_2),

            # === Metadata ===
            'vocabulary_size': vocab_size,
            'max_entropy': float(max_entropy)
        }

    # =====================================================================
    # LEXICAL LEVEL SIMILARITY
    # =====================================================================

    def analyze_lexical_similarity(self):
        """Analyze lexical-level similarity (surface forms and lemmas)."""
        print(f"\n{'='*80}")
        print(f"LEXICAL LEVEL SIMILARITY: {self.newspaper}")
        print(f"{'='*80}\n")

        # Extract data
        canonical_surface = self._extract_surface_forms('canonical')
        headline_surface = self._extract_surface_forms('headline')

        canonical_lemmas = self._extract_lemmas('canonical')
        headline_lemmas = self._extract_lemmas('headline')

        # Compute similarity metrics
        self.results['lexical'] = {
            'surface_forms': self._compute_lexical_similarity(
                canonical_surface, headline_surface, 'Surface Forms'
            ),
            'lemmas': self._compute_lexical_similarity(
                canonical_lemmas, headline_lemmas, 'Lemmas'
            ),
            'sentence_level': self._compute_sentence_level_similarity()
        }

        print("✓ Lexical similarity analysis complete")
        return self.results['lexical']

    def _extract_surface_forms(self, register: str) -> List[str]:
        """Extract surface word forms from text."""
        key = f'{register}_text'
        text_file = self.paths[key]

        if not text_file.exists():
            return []

        words = []
        with open(text_file, 'r', encoding='utf-8') as f:
            for line in f:
                words.extend(line.strip().lower().split())

        return words

    def _extract_lemmas(self, register: str) -> List[str]:
        """Extract lemmas from dependency parses."""
        key = f'{register}_dep'
        conllu_file = self.paths[key]

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
        """Compute lexical similarity metrics."""
        if not words1 or not words2:
            return {}

        # Convert to sets and counters
        set1 = set(words1)
        set2 = set(words2)
        count1 = Counter(words1)
        count2 = Counter(words2)

        # Set-based similarity
        jaccard = self._jaccard_similarity(set1, set2)
        dice = self._dice_coefficient(set1, set2)
        overlap = self._overlap_coefficient(set1, set2)

        # Distributional similarity
        dist_sim = self._distributional_similarity(count1, count2)

        # Vocabulary overlap statistics
        shared_vocab = len(set1 & set2)
        unique_to_1 = len(set1 - set2)
        unique_to_2 = len(set2 - set1)
        total_vocab = len(set1 | set2)

        # Frequency correlation (for shared vocabulary)
        shared_words = list(set1 & set2)
        if len(shared_words) > 1:
            freqs1 = [count1[w] for w in shared_words]
            freqs2 = [count2[w] for w in shared_words]

            # Spearman rank correlation
            spearman_corr, spearman_p = spearmanr(freqs1, freqs2)

            # Pearson correlation
            pearson_corr, pearson_p = pearsonr(freqs1, freqs2)
        else:
            spearman_corr, spearman_p = 0.0, 1.0
            pearson_corr, pearson_p = 0.0, 1.0

        print(f"  {name:20s}: Jaccard={jaccard:.4f}, JS-Sim={dist_sim.get('js_similarity', 0):.4f}, "
              f"CrossEnt(C→H)={dist_sim.get('cross_entropy_1_to_2', 0):.3f}, "
              f"KL(C→H)={dist_sim.get('kl_divergence_1_to_2', 0):.3f}")

        return {
            'jaccard_similarity': jaccard,
            'dice_coefficient': dice,
            'overlap_coefficient': overlap,
            'shared_vocabulary': shared_vocab,
            'unique_to_canonical': unique_to_1,
            'unique_to_headline': unique_to_2,
            'total_vocabulary': total_vocab,
            'vocabulary_overlap_ratio': shared_vocab / total_vocab if total_vocab > 0 else 0,
            'spearman_correlation': float(spearman_corr),
            'spearman_p_value': float(spearman_p),
            'pearson_correlation': float(pearson_corr),
            'pearson_p_value': float(pearson_p),
            **dist_sim
        }

    def _compute_sentence_level_similarity(self) -> Dict:
        """Compute sentence-level similarity (parallel sentences)."""
        canonical_file = self.paths['canonical_text']
        headline_file = self.paths['headline_text']

        if not canonical_file.exists() or not headline_file.exists():
            return {}

        # Read parallel sentences
        with open(canonical_file, 'r', encoding='utf-8') as f:
            canonical_sents = [line.strip().lower() for line in f]

        with open(headline_file, 'r', encoding='utf-8') as f:
            headline_sents = [line.strip().lower() for line in f]

        if len(canonical_sents) != len(headline_sents):
            print(f"  Warning: Mismatched sentence counts ({len(canonical_sents)} vs {len(headline_sents)})")
            return {}

        # Compute per-sentence similarities
        edit_distances = []
        jaccard_scores = []
        token_overlap_ratios = []

        for can_sent, head_sent in zip(canonical_sents, headline_sents):
            # Character-level edit distance
            char_edit_dist = edit_distance(can_sent, head_sent)
            edit_distances.append(char_edit_dist)

            # Token-level Jaccard
            can_tokens = set(can_sent.split())
            head_tokens = set(head_sent.split())
            jaccard = self._jaccard_similarity(can_tokens, head_tokens)
            jaccard_scores.append(jaccard)

            # Token overlap ratio
            if can_tokens:
                overlap_ratio = len(can_tokens & head_tokens) / len(can_tokens)
                token_overlap_ratios.append(overlap_ratio)

        # Compute statistics
        avg_edit_distance = np.mean(edit_distances) if edit_distances else 0
        avg_jaccard = np.mean(jaccard_scores) if jaccard_scores else 0
        avg_token_overlap = np.mean(token_overlap_ratios) if token_overlap_ratios else 0

        # Normalized edit distance (0-1 range, lower = more similar)
        max_possible_edit = max(len(c) + len(h) for c, h in zip(canonical_sents, headline_sents))
        normalized_edit_similarity = 1 - (avg_edit_distance / max_possible_edit) if max_possible_edit > 0 else 0

        print(f"  Sentence-Level:      Avg Jaccard={avg_jaccard:.4f}, "
              f"Avg Edit Sim={normalized_edit_similarity:.4f}, "
              f"Avg Token Overlap={avg_token_overlap:.4f}")

        return {
            'avg_edit_distance': avg_edit_distance,
            'normalized_edit_similarity': normalized_edit_similarity,
            'avg_jaccard_similarity': avg_jaccard,
            'avg_token_overlap_ratio': avg_token_overlap,
            'sentence_count': len(canonical_sents)
        }

    # =====================================================================
    # MORPHOLOGICAL LEVEL SIMILARITY
    # =====================================================================

    def analyze_morphological_similarity(self):
        """Analyze morphological-level similarity (POS tags and features)."""
        print(f"\n{'='*80}")
        print(f"MORPHOLOGICAL LEVEL SIMILARITY: {self.newspaper}")
        print(f"{'='*80}\n")

        # Extract POS tags
        canonical_pos = self._extract_pos_tags('canonical')
        headline_pos = self._extract_pos_tags('headline')

        # Extract morphological features
        canonical_feats = self._extract_morph_features('canonical')
        headline_feats = self._extract_morph_features('headline')

        # Compute similarity
        self.results['morphological'] = {
            'pos_tags': self._compute_morphological_similarity(
                canonical_pos, headline_pos, 'POS Tags'
            ),
            'morph_features': self._compute_morphological_similarity(
                canonical_feats, headline_feats, 'Morphological Features'
            ),
            'feature_type_similarity': self._compute_feature_type_similarity(
                canonical_feats, headline_feats
            )
        }

        print("✓ Morphological similarity analysis complete")
        return self.results['morphological']

    def _extract_pos_tags(self, register: str) -> List[str]:
        """Extract POS tags from dependency parses."""
        key = f'{register}_dep'
        conllu_file = self.paths[key]

        if not conllu_file.exists():
            return []

        pos_tags = []
        with open(conllu_file, 'r', encoding='utf-8') as f:
            for sentence in parse_incr(f):
                for token in sentence:
                    if token['upos']:
                        pos_tags.append(token['upos'])

        return pos_tags

    def _extract_morph_features(self, register: str) -> List[str]:
        """Extract morphological features from dependency parses."""
        key = f'{register}_dep'
        conllu_file = self.paths[key]

        if not conllu_file.exists():
            return []

        features = []
        with open(conllu_file, 'r', encoding='utf-8') as f:
            for sentence in parse_incr(f):
                for token in sentence:
                    if token['feats']:
                        for feat_name, feat_val in token['feats'].items():
                            features.append(f"{feat_name}={feat_val}")

        return features

    def _compute_morphological_similarity(self, items1: List[str], items2: List[str], name: str) -> Dict:
        """Compute morphological similarity metrics."""
        if not items1 or not items2:
            return {}

        # Set-based similarity
        set1 = set(items1)
        set2 = set(items2)
        count1 = Counter(items1)
        count2 = Counter(items2)

        jaccard = self._jaccard_similarity(set1, set2)
        dice = self._dice_coefficient(set1, set2)
        overlap = self._overlap_coefficient(set1, set2)

        # Distributional similarity
        dist_sim = self._distributional_similarity(count1, count2)

        print(f"  {name:25s}: Jaccard={jaccard:.4f}, JS-Sim={dist_sim.get('js_similarity', 0):.4f}, "
              f"CrossEnt(C→H)={dist_sim.get('cross_entropy_1_to_2', 0):.3f}")

        return {
            'jaccard_similarity': jaccard,
            'dice_coefficient': dice,
            'overlap_coefficient': overlap,
            'shared_types': len(set1 & set2),
            'unique_to_canonical': len(set1 - set2),
            'unique_to_headline': len(set2 - set1),
            **dist_sim
        }

    def _compute_feature_type_similarity(self, feats1: List[str], feats2: List[str]) -> Dict:
        """Compute per-feature-type similarity."""
        if not feats1 or not feats2:
            return {}

        # Group by feature type
        feature_types_1 = defaultdict(list)
        feature_types_2 = defaultdict(list)

        for feat in feats1:
            if '=' in feat:
                feat_name, feat_val = feat.split('=', 1)
                feature_types_1[feat_name].append(feat_val)

        for feat in feats2:
            if '=' in feat:
                feat_name, feat_val = feat.split('=', 1)
                feature_types_2[feat_name].append(feat_val)

        # Compute similarity for each feature type
        per_type_similarity = {}
        all_feat_names = set(feature_types_1.keys()) | set(feature_types_2.keys())

        for feat_name in all_feat_names:
            vals1 = feature_types_1.get(feat_name, [])
            vals2 = feature_types_2.get(feat_name, [])

            if vals1 and vals2:
                set1 = set(vals1)
                set2 = set(vals2)
                count1 = Counter(vals1)
                count2 = Counter(vals2)

                jaccard = self._jaccard_similarity(set1, set2)
                dist_sim = self._distributional_similarity(count1, count2)

                per_type_similarity[feat_name] = {
                    'jaccard_similarity': jaccard,
                    'js_similarity': dist_sim.get('js_similarity', 0),
                    'bhattacharyya_coefficient': dist_sim.get('bhattacharyya_coefficient', 0)
                }

        return per_type_similarity

    # =====================================================================
    # SYNTACTIC LEVEL SIMILARITY
    # =====================================================================

    def analyze_syntactic_similarity(self):
        """Analyze syntactic-level similarity (dependency and constituency)."""
        print(f"\n{'='*80}")
        print(f"SYNTACTIC LEVEL SIMILARITY: {self.newspaper}")
        print(f"{'='*80}\n")

        # Dependency relations
        canonical_deps = self._extract_dep_relations('canonical')
        headline_deps = self._extract_dep_relations('headline')

        # Constituency labels
        canonical_const = self._extract_const_labels('canonical')
        headline_const = self._extract_const_labels('headline')

        # Dependency bigrams (head-dependent relation patterns)
        canonical_dep_bigrams = self._extract_dep_bigrams('canonical')
        headline_dep_bigrams = self._extract_dep_bigrams('headline')

        self.results['syntactic'] = {
            'dependency_relations': self._compute_morphological_similarity(
                canonical_deps, headline_deps, 'Dependency Relations'
            ),
            'constituency_labels': self._compute_morphological_similarity(
                canonical_const, headline_const, 'Constituency Labels'
            ),
            'dependency_bigrams': self._compute_morphological_similarity(
                canonical_dep_bigrams, headline_dep_bigrams, 'Dependency Bigrams'
            )
        }

        print("✓ Syntactic similarity analysis complete")
        return self.results['syntactic']

    def _extract_dep_relations(self, register: str) -> List[str]:
        """Extract dependency relation labels."""
        key = f'{register}_dep'
        conllu_file = self.paths[key]

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
        """Extract constituency labels from parse trees."""
        key = f'{register}_const'
        const_file = self.paths[key]

        if not const_file.exists():
            return []

        labels = []
        with open(const_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        tree = Tree.fromstring(line)
                        for subtree in tree.subtrees():
                            if not isinstance(subtree[0], str):  # Non-terminal
                                labels.append(subtree.label())
                    except:
                        continue

        return labels

    def _extract_dep_bigrams(self, register: str) -> List[str]:
        """Extract dependency bigrams (head POS + relation + dependent POS)."""
        key = f'{register}_dep'
        conllu_file = self.paths[key]

        if not conllu_file.exists():
            return []

        bigrams = []
        with open(conllu_file, 'r', encoding='utf-8') as f:
            for sentence in parse_incr(f):
                # Build head-dependent pairs
                for token in sentence:
                    if token['head'] is not None and token['head'] > 0:
                        head_idx = token['head'] - 1  # Convert to 0-indexed
                        if 0 <= head_idx < len(sentence):
                            head_token = sentence[head_idx]
                            head_pos = head_token['upos']
                            dep_pos = token['upos']
                            rel = token['deprel']

                            if head_pos and dep_pos and rel:
                                bigram = f"{head_pos}-{rel}-{dep_pos}"
                                bigrams.append(bigram)

        return bigrams

    # =====================================================================
    # STRUCTURAL LEVEL SIMILARITY
    # =====================================================================

    def analyze_structural_similarity(self):
        """Analyze structural similarity (tree-based metrics)."""
        print(f"\n{'='*80}")
        print(f"STRUCTURAL LEVEL SIMILARITY: {self.newspaper}")
        print(f"{'='*80}\n")

        # Tree structure similarity
        constituency_sim = self._compute_tree_structure_similarity()

        # Dependency structure similarity
        dependency_sim = self._compute_dependency_structure_similarity()

        self.results['structural'] = {
            'constituency_trees': constituency_sim,
            'dependency_trees': dependency_sim
        }

        print("✓ Structural similarity analysis complete")
        return self.results['structural']

    def _compute_tree_structure_similarity(self) -> Dict:
        """Compute constituency tree structure similarity."""
        canonical_file = self.paths['canonical_const']
        headline_file = self.paths['headline_const']

        if not canonical_file.exists() or not headline_file.exists():
            return {}

        # Read parallel trees
        canonical_trees = []
        headline_trees = []

        with open(canonical_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        tree = Tree.fromstring(line)
                        canonical_trees.append(tree)
                    except:
                        canonical_trees.append(None)

        with open(headline_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        tree = Tree.fromstring(line)
                        headline_trees.append(tree)
                    except:
                        headline_trees.append(None)

        if len(canonical_trees) != len(headline_trees):
            print(f"  Warning: Mismatched tree counts ({len(canonical_trees)} vs {len(headline_trees)})")
            return {}

        # Compute structural similarity metrics
        height_correlations = []
        size_correlations = []
        label_similarities = []

        for can_tree, head_tree in zip(canonical_trees, headline_trees):
            if can_tree is None or head_tree is None:
                continue

            # Height correlation (shallow trees vs deep trees)
            height_correlations.append((can_tree.height(), head_tree.height()))

            # Size correlation (number of nodes)
            can_size = len(list(can_tree.subtrees()))
            head_size = len(list(head_tree.subtrees()))
            size_correlations.append((can_size, head_size))

            # Label set similarity
            can_labels = set(st.label() for st in can_tree.subtrees() if not isinstance(st[0], str))
            head_labels = set(st.label() for st in head_tree.subtrees() if not isinstance(st[0], str))
            label_sim = self._jaccard_similarity(can_labels, head_labels)
            label_similarities.append(label_sim)

        if height_correlations:
            heights_can, heights_head = zip(*height_correlations)
            height_corr, height_p = pearsonr(heights_can, heights_head)
        else:
            height_corr, height_p = 0.0, 1.0

        if size_correlations:
            sizes_can, sizes_head = zip(*size_correlations)
            size_corr, size_p = pearsonr(sizes_can, sizes_head)
        else:
            size_corr, size_p = 0.0, 1.0

        avg_label_similarity = np.mean(label_similarities) if label_similarities else 0

        print(f"  Constituency Trees:  Height Corr={height_corr:.4f}, "
              f"Size Corr={size_corr:.4f}, Avg Label Sim={avg_label_similarity:.4f}")

        return {
            'height_correlation': float(height_corr),
            'height_p_value': float(height_p),
            'size_correlation': float(size_corr),
            'size_p_value': float(size_p),
            'avg_label_similarity': avg_label_similarity,
            'tree_pair_count': len(label_similarities)
        }

    def _compute_dependency_structure_similarity(self) -> Dict:
        """Compute dependency tree structure similarity."""
        canonical_file = self.paths['canonical_dep']
        headline_file = self.paths['headline_dep']

        if not canonical_file.exists() or not headline_file.exists():
            return {}

        # Read parallel dependency trees
        canonical_sents = []
        headline_sents = []

        with open(canonical_file, 'r', encoding='utf-8') as f:
            for sentence in parse_incr(f):
                canonical_sents.append(sentence)

        with open(headline_file, 'r', encoding='utf-8') as f:
            for sentence in parse_incr(f):
                headline_sents.append(sentence)

        if len(canonical_sents) != len(headline_sents):
            print(f"  Warning: Mismatched sentence counts ({len(canonical_sents)} vs {len(headline_sents)})")
            return {}

        # Compute metrics
        length_correlations = []
        depth_correlations = []
        distance_correlations = []

        for can_sent, head_sent in zip(canonical_sents, headline_sents):
            # Length correlation
            length_correlations.append((len(can_sent), len(head_sent)))

            # Depth correlation
            can_depth = self._compute_dep_tree_depth(can_sent)
            head_depth = self._compute_dep_tree_depth(head_sent)
            depth_correlations.append((can_depth, head_depth))

            # Average dependency distance
            can_dist = self._compute_avg_dep_distance(can_sent)
            head_dist = self._compute_avg_dep_distance(head_sent)
            distance_correlations.append((can_dist, head_dist))

        if length_correlations:
            lengths_can, lengths_head = zip(*length_correlations)
            length_corr, length_p = pearsonr(lengths_can, lengths_head)
        else:
            length_corr, length_p = 0.0, 1.0

        if depth_correlations:
            depths_can, depths_head = zip(*depth_correlations)
            depth_corr, depth_p = pearsonr(depths_can, depths_head)
        else:
            depth_corr, depth_p = 0.0, 1.0

        if distance_correlations:
            dists_can, dists_head = zip(*distance_correlations)
            distance_corr, distance_p = pearsonr(dists_can, dists_head)
        else:
            distance_corr, distance_p = 0.0, 1.0

        print(f"  Dependency Trees:    Length Corr={length_corr:.4f}, "
              f"Depth Corr={depth_corr:.4f}, Distance Corr={distance_corr:.4f}")

        return {
            'length_correlation': float(length_corr),
            'length_p_value': float(length_p),
            'depth_correlation': float(depth_corr),
            'depth_p_value': float(depth_p),
            'distance_correlation': float(distance_corr),
            'distance_p_value': float(distance_p),
            'sentence_pair_count': len(length_correlations)
        }

    def _compute_dep_tree_depth(self, sentence) -> int:
        """Compute maximum depth of dependency tree."""
        if not sentence:
            return 0

        # Build parent-child mapping
        children = defaultdict(list)
        root_id = None

        for token in sentence:
            if token['head'] is None or token['head'] == 0:
                root_id = token['id']
            else:
                children[token['head']].append(token['id'])

        if root_id is None:
            return 0

        # BFS to find maximum depth
        def get_depth(node_id):
            if node_id not in children:
                return 1
            return 1 + max(get_depth(child) for child in children[node_id])

        return get_depth(root_id)

    def _compute_avg_dep_distance(self, sentence) -> float:
        """Compute average dependency distance."""
        if not sentence:
            return 0.0

        distances = []
        for token in sentence:
            if token['head'] is not None and token['head'] > 0:
                distance = abs(token['id'] - token['head'])
                distances.append(distance)

        return np.mean(distances) if distances else 0.0

    # =====================================================================
    # COMBINED ANALYSIS AND OUTPUT
    # =====================================================================

    def compute_combined_similarity(self):
        """Compute combined similarity scores across all levels."""
        print(f"\n{'='*80}")
        print(f"COMBINED SIMILARITY ANALYSIS")
        print(f"{'='*80}\n")

        # Aggregate similarity scores
        similarity_scores = {}

        # Lexical similarity
        if 'lexical' in self.results:
            if 'surface_forms' in self.results['lexical']:
                similarity_scores['lexical_surface_jaccard'] = self.results['lexical']['surface_forms'].get('jaccard_similarity', 0)
                similarity_scores['lexical_surface_js'] = self.results['lexical']['surface_forms'].get('js_similarity', 0)

            if 'lemmas' in self.results['lexical']:
                similarity_scores['lexical_lemma_jaccard'] = self.results['lexical']['lemmas'].get('jaccard_similarity', 0)
                similarity_scores['lexical_lemma_js'] = self.results['lexical']['lemmas'].get('js_similarity', 0)

        # Morphological similarity
        if 'morphological' in self.results:
            if 'pos_tags' in self.results['morphological']:
                similarity_scores['morph_pos_jaccard'] = self.results['morphological']['pos_tags'].get('jaccard_similarity', 0)
                similarity_scores['morph_pos_js'] = self.results['morphological']['pos_tags'].get('js_similarity', 0)

        # Syntactic similarity
        if 'syntactic' in self.results:
            if 'dependency_relations' in self.results['syntactic']:
                similarity_scores['synt_deprel_jaccard'] = self.results['syntactic']['dependency_relations'].get('jaccard_similarity', 0)
                similarity_scores['synt_deprel_js'] = self.results['syntactic']['dependency_relations'].get('js_similarity', 0)

        # Structural similarity
        if 'structural' in self.results:
            if 'constituency_trees' in self.results['structural']:
                similarity_scores['struct_height_corr'] = self.results['structural']['constituency_trees'].get('height_correlation', 0)
                similarity_scores['struct_label_sim'] = self.results['structural']['constituency_trees'].get('avg_label_similarity', 0)

        # Compute aggregate similarity (average of normalized scores)
        aggregate_similarity = np.mean(list(similarity_scores.values())) if similarity_scores else 0

        print(f"  Aggregate Similarity Score: {aggregate_similarity:.4f}")
        print(f"  (Range: 0=completely different, 1=identical)")

        self.results['combined'] = {
            'individual_scores': similarity_scores,
            'aggregate_similarity': aggregate_similarity
        }

        return self.results['combined']

    def save_results(self):
        """Save all results to JSON and CSV files."""
        print(f"\n{'='*80}")
        print(f"SAVING RESULTS")
        print(f"{'='*80}\n")

        # Save complete JSON
        json_path = self.output_dir / 'multilevel_similarity_analysis.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"  ✓ Saved: {json_path}")

        # Save summary CSV
        summary_data = []

        # Helper function to extract metrics
        def add_metrics(level, sublevel, metrics_dict):
            if metrics_dict and isinstance(metrics_dict, dict):
                row = {
                    'level': level,
                    'sublevel': sublevel,
                    **{k: v for k, v in metrics_dict.items() if isinstance(v, (int, float))}
                }
                summary_data.append(row)

        # Lexical metrics
        if 'lexical' in self.results:
            for sublevel in ['surface_forms', 'lemmas', 'sentence_level']:
                if sublevel in self.results['lexical']:
                    add_metrics('lexical', sublevel, self.results['lexical'][sublevel])

        # Morphological metrics
        if 'morphological' in self.results:
            for sublevel in ['pos_tags', 'morph_features']:
                if sublevel in self.results['morphological']:
                    add_metrics('morphological', sublevel, self.results['morphological'][sublevel])

        # Syntactic metrics
        if 'syntactic' in self.results:
            for sublevel in ['dependency_relations', 'constituency_labels', 'dependency_bigrams']:
                if sublevel in self.results['syntactic']:
                    add_metrics('syntactic', sublevel, self.results['syntactic'][sublevel])

        # Structural metrics
        if 'structural' in self.results:
            for sublevel in ['constituency_trees', 'dependency_trees']:
                if sublevel in self.results['structural']:
                    add_metrics('structural', sublevel, self.results['structural'][sublevel])

        df = pd.DataFrame(summary_data)
        csv_path = self.output_dir / 'multilevel_similarity_summary.csv'
        df.to_csv(csv_path, index=False)
        print(f"  ✓ Saved: {csv_path}")

        # Save combined scores
        if 'combined' in self.results:
            combined_df = pd.DataFrame({
                'metric': list(self.results['combined']['individual_scores'].keys()),
                'similarity': list(self.results['combined']['individual_scores'].values())
            })

            combined_path = self.output_dir / 'combined_similarity_scores.csv'
            combined_df.to_csv(combined_path, index=False)
            print(f"  ✓ Saved: {combined_path}")

        print("\n✓ All results saved successfully")

    def run_complete_analysis(self):
        """Run complete multi-level similarity analysis."""
        print(f"\n{'='*80}")
        print(f"MULTI-LEVEL SIMILARITY ANALYZER")
        print(f"Newspaper: {self.newspaper}")
        print(f"{'='*80}\n")

        # Run all levels
        self.analyze_lexical_similarity()
        self.analyze_morphological_similarity()
        self.analyze_syntactic_similarity()
        self.analyze_structural_similarity()
        self.compute_combined_similarity()

        # Save results
        self.save_results()

        print(f"\n{'='*80}")
        print(f"ANALYSIS COMPLETE")
        print(f"{'='*80}\n")
        print(f"Results saved to: {self.output_dir}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Multi-Level Similarity Analyzer - Measures register similarity at multiple linguistic levels"
    )
    parser.add_argument(
        '--newspaper',
        default='Times-of-India',
        choices=['Times-of-India', 'Hindustan-Times', 'The-Hindu'],
        help='Newspaper to analyze'
    )

    args = parser.parse_args()

    analyzer = MultiLevelSimilarityAnalyzer(args.newspaper)
    analyzer.run_complete_analysis()


if __name__ == '__main__':
    main()
