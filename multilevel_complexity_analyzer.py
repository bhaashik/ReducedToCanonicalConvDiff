#!/usr/bin/env python3
"""
Multi-Level Complexity and Similarity Analyzer

Analyzes register complexity and similarity at multiple linguistic levels:
1. Lexical level (surface forms, lemmas)
2. Morphological level (POS tags, morphological features)
3. Syntactic level (dependency relations, constituency structures)
4. Structural level (tree-based metrics)

For each level, computes both:
- Surface-based metrics (headlines vs canonical surface forms)
- Structural metrics (morphosyntactic patterns)

Key Metrics:
- Type-Token Ratio (TTR) and variants
- Entropy and perplexity
- Average Information Content
- Structural complexity (tree depth, branching factor)
- Cross-register divergence measures
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Set
import math
from scipy.stats import entropy
from conllu import parse_incr
from nltk import Tree


class MultiLevelComplexityAnalyzer:
    """Analyzes complexity at multiple linguistic levels."""

    def __init__(self, newspaper: str):
        self.newspaper = newspaper
        self.project_root = Path(__file__).parent
        self.output_dir = self.project_root / 'output' / 'multilevel_complexity' / newspaper
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Data paths
        self.paths = self._get_data_paths()

        # Results storage
        self.results = {
            'lexical': {},
            'morphological': {},
            'syntactic': {},
            'structural': {},
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
    # LEXICAL LEVEL ANALYSIS
    # =====================================================================

    def analyze_lexical_level(self):
        """Analyze lexical-level complexity (surface forms and lemmas)."""
        print(f"\n{'='*80}")
        print(f"LEXICAL LEVEL ANALYSIS: {self.newspaper}")
        print(f"{'='*80}\n")

        # Surface form analysis
        canonical_surface = self._extract_surface_forms('canonical')
        headline_surface = self._extract_surface_forms('headline')

        # Lemma analysis
        canonical_lemmas = self._extract_lemmas('canonical')
        headline_lemmas = self._extract_lemmas('headline')

        # Compute metrics
        self.results['lexical'] = {
            'surface_forms': {
                'canonical': self._compute_lexical_metrics(canonical_surface, 'Canonical Surface'),
                'headline': self._compute_lexical_metrics(headline_surface, 'Headline Surface'),
                'divergence': self._compute_divergence(canonical_surface, headline_surface)
            },
            'lemmas': {
                'canonical': self._compute_lexical_metrics(canonical_lemmas, 'Canonical Lemmas'),
                'headline': self._compute_lexical_metrics(headline_lemmas, 'Headline Lemmas'),
                'divergence': self._compute_divergence(canonical_lemmas, headline_lemmas)
            }
        }

        print("✓ Lexical analysis complete")
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

    def _compute_lexical_metrics(self, words: List[str], name: str) -> Dict:
        """Compute lexical complexity metrics."""
        if not words:
            return {}

        word_counts = Counter(words)
        types = len(word_counts)
        tokens = len(words)

        # Type-Token Ratio (TTR)
        ttr = types / tokens if tokens > 0 else 0

        # Root TTR (corrected for length)
        root_ttr = types / math.sqrt(tokens) if tokens > 0 else 0

        # Log TTR
        log_ttr = types / math.log(tokens) if tokens > 1 else 0

        # Entropy
        probs = np.array(list(word_counts.values())) / tokens
        lex_entropy = entropy(probs, base=2)

        # Perplexity
        lex_perplexity = 2 ** lex_entropy

        # Average word frequency (inverse of rarity)
        avg_frequency = tokens / types if types > 0 else 0

        # Hapax legomena (words appearing once)
        hapax_count = sum(1 for count in word_counts.values() if count == 1)
        hapax_ratio = hapax_count / types if types > 0 else 0

        print(f"  {name:25s}: Types={types:5d}, Tokens={tokens:6d}, TTR={ttr:.4f}, "
              f"Entropy={lex_entropy:.4f}, Perplexity={lex_perplexity:.2f}")

        return {
            'types': types,
            'tokens': tokens,
            'ttr': ttr,
            'root_ttr': root_ttr,
            'log_ttr': log_ttr,
            'entropy': lex_entropy,
            'perplexity': lex_perplexity,
            'avg_frequency': avg_frequency,
            'hapax_count': hapax_count,
            'hapax_ratio': hapax_ratio
        }

    def _compute_divergence(self, dist1: List[str], dist2: List[str]) -> Dict:
        """Compute divergence between two distributions."""
        if not dist1 or not dist2:
            return {}

        # Create vocabularies
        vocab = set(dist1 + dist2)

        # Compute probability distributions
        count1 = Counter(dist1)
        count2 = Counter(dist2)

        total1 = len(dist1)
        total2 = len(dist2)

        # Add smoothing
        alpha = 1e-10

        probs1 = np.array([(count1.get(w, 0) + alpha) / (total1 + alpha * len(vocab)) for w in vocab])
        probs2 = np.array([(count2.get(w, 0) + alpha) / (total2 + alpha * len(vocab)) for w in vocab])

        # KL divergence (both directions)
        kl_div_1_2 = entropy(probs1, probs2, base=2)
        kl_div_2_1 = entropy(probs2, probs1, base=2)

        # Jensen-Shannon divergence (symmetric)
        m = 0.5 * (probs1 + probs2)
        js_div = 0.5 * entropy(probs1, m, base=2) + 0.5 * entropy(probs2, m, base=2)

        # Overlap coefficient
        set1 = set(dist1)
        set2 = set(dist2)
        overlap = len(set1 & set2) / min(len(set1), len(set2)) if min(len(set1), len(set2)) > 0 else 0

        print(f"    Divergence: KL(C→H)={kl_div_1_2:.4f}, KL(H→C)={kl_div_2_1:.4f}, "
              f"JS={js_div:.4f}, Overlap={overlap:.4f}")

        return {
            'kl_divergence_canonical_to_headline': kl_div_1_2,
            'kl_divergence_headline_to_canonical': kl_div_2_1,
            'js_divergence': js_div,
            'overlap_coefficient': overlap,
            'asymmetry': abs(kl_div_1_2 - kl_div_2_1)
        }

    # =====================================================================
    # MORPHOLOGICAL LEVEL ANALYSIS
    # =====================================================================

    def analyze_morphological_level(self):
        """Analyze morphological-level complexity (POS tags and features)."""
        print(f"\n{'='*80}")
        print(f"MORPHOLOGICAL LEVEL ANALYSIS: {self.newspaper}")
        print(f"{'='*80}\n")

        # POS tag analysis
        canonical_pos = self._extract_pos_tags('canonical')
        headline_pos = self._extract_pos_tags('headline')

        # Morphological feature analysis
        canonical_feats = self._extract_morph_features('canonical')
        headline_feats = self._extract_morph_features('headline')

        # Compute metrics
        self.results['morphological'] = {
            'pos_tags': {
                'canonical': self._compute_lexical_metrics(canonical_pos, 'Canonical POS'),
                'headline': self._compute_lexical_metrics(headline_pos, 'Headline POS'),
                'divergence': self._compute_divergence(canonical_pos, headline_pos)
            },
            'morph_features': {
                'canonical': self._compute_feature_metrics(canonical_feats, 'Canonical Features'),
                'headline': self._compute_feature_metrics(headline_feats, 'Headline Features'),
                'feature_divergence': self._compute_feature_divergence(canonical_feats, headline_feats)
            }
        }

        print("✓ Morphological analysis complete")
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

    def _compute_feature_metrics(self, features: List[str], name: str) -> Dict:
        """Compute metrics for morphological features."""
        if not features:
            return {}

        # Overall feature statistics
        basic_metrics = self._compute_lexical_metrics(features, name)

        # Per-feature-type analysis
        feature_types = defaultdict(list)
        for feat in features:
            if '=' in feat:
                feat_name, feat_val = feat.split('=', 1)
                feature_types[feat_name].append(feat_val)

        per_type_complexity = {}
        for feat_name, values in feature_types.items():
            value_counts = Counter(values)
            type_count = len(value_counts)
            token_count = len(values)
            feat_entropy = entropy(list(value_counts.values()), base=2) if token_count > 0 else 0

            per_type_complexity[feat_name] = {
                'types': type_count,
                'tokens': token_count,
                'entropy': feat_entropy
            }

        basic_metrics['per_feature_type'] = per_type_complexity
        return basic_metrics

    def _compute_feature_divergence(self, feats1: List[str], feats2: List[str]) -> Dict:
        """Compute divergence between morphological feature distributions."""
        if not feats1 or not feats2:
            return {}

        # Overall divergence
        overall_div = self._compute_divergence(feats1, feats2)

        # Per-feature-type divergence
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

        per_type_divergence = {}
        all_feat_names = set(feature_types_1.keys()) | set(feature_types_2.keys())

        for feat_name in all_feat_names:
            vals1 = feature_types_1.get(feat_name, [])
            vals2 = feature_types_2.get(feat_name, [])

            if vals1 and vals2:
                div = self._compute_divergence(vals1, vals2)
                per_type_divergence[feat_name] = div

        return {
            'overall': overall_div,
            'per_feature_type': per_type_divergence
        }

    # =====================================================================
    # SYNTACTIC LEVEL ANALYSIS
    # =====================================================================

    def analyze_syntactic_level(self):
        """Analyze syntactic-level complexity (dependency and constituency)."""
        print(f"\n{'='*80}")
        print(f"SYNTACTIC LEVEL ANALYSIS: {self.newspaper}")
        print(f"{'='*80}\n")

        # Dependency relation analysis
        canonical_deps = self._extract_dep_relations('canonical')
        headline_deps = self._extract_dep_relations('headline')

        # Constituency label analysis
        canonical_const = self._extract_const_labels('canonical')
        headline_const = self._extract_const_labels('headline')

        self.results['syntactic'] = {
            'dependency_relations': {
                'canonical': self._compute_lexical_metrics(canonical_deps, 'Canonical DepRels'),
                'headline': self._compute_lexical_metrics(headline_deps, 'Headline DepRels'),
                'divergence': self._compute_divergence(canonical_deps, headline_deps)
            },
            'constituency_labels': {
                'canonical': self._compute_lexical_metrics(canonical_const, 'Canonical Const'),
                'headline': self._compute_lexical_metrics(headline_const, 'Headline Const'),
                'divergence': self._compute_divergence(canonical_const, headline_const)
            }
        }

        print("✓ Syntactic analysis complete")
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

    # =====================================================================
    # STRUCTURAL LEVEL ANALYSIS
    # =====================================================================

    def analyze_structural_level(self):
        """Analyze structural complexity (tree-based metrics)."""
        print(f"\n{'='*80}")
        print(f"STRUCTURAL LEVEL ANALYSIS: {self.newspaper}")
        print(f"{'='*80}\n")

        # Constituency tree structure
        canonical_trees = self._load_constituency_trees('canonical')
        headline_trees = self._load_constituency_trees('headline')

        # Dependency tree structure
        canonical_dep_trees = self._load_dependency_trees('canonical')
        headline_dep_trees = self._load_dependency_trees('headline')

        self.results['structural'] = {
            'constituency': {
                'canonical': self._compute_tree_metrics(canonical_trees, 'Canonical Trees'),
                'headline': self._compute_tree_metrics(headline_trees, 'Headline Trees')
            },
            'dependency': {
                'canonical': self._compute_dep_tree_metrics(canonical_dep_trees, 'Canonical Dep Trees'),
                'headline': self._compute_dep_tree_metrics(headline_dep_trees, 'Headline Dep Trees')
            }
        }

        print("✓ Structural analysis complete")
        return self.results['structural']

    def _load_constituency_trees(self, register: str) -> List[Tree]:
        """Load constituency trees."""
        key = f'{register}_const'
        const_file = self.paths[key]

        if not const_file.exists():
            return []

        trees = []
        with open(const_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        tree = Tree.fromstring(line)
                        trees.append(tree)
                    except:
                        continue

        return trees

    def _load_dependency_trees(self, register: str) -> List:
        """Load dependency trees."""
        key = f'{register}_dep'
        conllu_file = self.paths[key]

        if not conllu_file.exists():
            return []

        trees = []
        with open(conllu_file, 'r', encoding='utf-8') as f:
            for sentence in parse_incr(f):
                trees.append(sentence)

        return trees

    def _compute_tree_metrics(self, trees: List[Tree], name: str) -> Dict:
        """Compute metrics for constituency trees."""
        if not trees:
            return {}

        depths = []
        sizes = []
        branching_factors = []

        for tree in trees:
            depths.append(tree.height())
            sizes.append(len(tree.leaves()))

            # Compute average branching factor
            non_terminals = [subtree for subtree in tree.subtrees() if not isinstance(subtree[0], str)]
            if non_terminals:
                bf = sum(len(list(nt)) for nt in non_terminals) / len(non_terminals)
                branching_factors.append(bf)

        avg_depth = np.mean(depths) if depths else 0
        avg_size = np.mean(sizes) if sizes else 0
        avg_branching = np.mean(branching_factors) if branching_factors else 0

        print(f"  {name:25s}: Trees={len(trees):4d}, Avg Depth={avg_depth:.2f}, "
              f"Avg Size={avg_size:.2f}, Avg Branching={avg_branching:.2f}")

        return {
            'tree_count': len(trees),
            'avg_depth': avg_depth,
            'avg_size': avg_size,
            'avg_branching_factor': avg_branching,
            'depth_std': np.std(depths) if depths else 0,
            'size_std': np.std(sizes) if sizes else 0
        }

    def _compute_dep_tree_metrics(self, trees: List, name: str) -> Dict:
        """Compute metrics for dependency trees."""
        if not trees:
            return {}

        sentence_lengths = []
        avg_dep_distances = []
        max_depths = []

        for sentence in trees:
            sentence_lengths.append(len(sentence))

            # Compute average dependency distance
            distances = []
            for token in sentence:
                if token['head'] is not None and token['head'] > 0:
                    distance = abs(token['id'] - token['head'])
                    distances.append(distance)

            if distances:
                avg_dep_distances.append(np.mean(distances))

            # Compute tree depth (longest path from root)
            depth = self._compute_dep_tree_depth(sentence)
            max_depths.append(depth)

        avg_length = np.mean(sentence_lengths) if sentence_lengths else 0
        avg_distance = np.mean(avg_dep_distances) if avg_dep_distances else 0
        avg_depth = np.mean(max_depths) if max_depths else 0

        print(f"  {name:25s}: Sentences={len(trees):4d}, Avg Length={avg_length:.2f}, "
              f"Avg Dep Distance={avg_distance:.2f}, Avg Depth={avg_depth:.2f}")

        return {
            'sentence_count': len(trees),
            'avg_sentence_length': avg_length,
            'avg_dependency_distance': avg_distance,
            'avg_tree_depth': avg_depth,
            'length_std': np.std(sentence_lengths) if sentence_lengths else 0
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

    # =====================================================================
    # COMBINED ANALYSIS AND OUTPUT
    # =====================================================================

    def compute_combined_metrics(self):
        """Compute combined complexity scores across all levels."""
        print(f"\n{'='*80}")
        print(f"COMBINED COMPLEXITY ANALYSIS")
        print(f"{'='*80}\n")

        # Aggregate complexity scores
        canonical_scores = {}
        headline_scores = {}

        # Lexical complexity
        if 'lexical' in self.results:
            canonical_scores['lexical_surface_entropy'] = self.results['lexical']['surface_forms']['canonical'].get('entropy', 0)
            headline_scores['lexical_surface_entropy'] = self.results['lexical']['surface_forms']['headline'].get('entropy', 0)

            canonical_scores['lexical_lemma_entropy'] = self.results['lexical']['lemmas']['canonical'].get('entropy', 0)
            headline_scores['lexical_lemma_entropy'] = self.results['lexical']['lemmas']['headline'].get('entropy', 0)

        # Morphological complexity
        if 'morphological' in self.results:
            canonical_scores['morph_pos_entropy'] = self.results['morphological']['pos_tags']['canonical'].get('entropy', 0)
            headline_scores['morph_pos_entropy'] = self.results['morphological']['pos_tags']['headline'].get('entropy', 0)

            canonical_scores['morph_feat_entropy'] = self.results['morphological']['morph_features']['canonical'].get('entropy', 0)
            headline_scores['morph_feat_entropy'] = self.results['morphological']['morph_features']['headline'].get('entropy', 0)

        # Syntactic complexity
        if 'syntactic' in self.results:
            canonical_scores['synt_deprel_entropy'] = self.results['syntactic']['dependency_relations']['canonical'].get('entropy', 0)
            headline_scores['synt_deprel_entropy'] = self.results['syntactic']['dependency_relations']['headline'].get('entropy', 0)

        # Structural complexity
        if 'structural' in self.results:
            canonical_scores['struct_tree_depth'] = self.results['structural']['constituency']['canonical'].get('avg_depth', 0)
            headline_scores['struct_tree_depth'] = self.results['structural']['constituency']['headline'].get('avg_depth', 0)

            canonical_scores['struct_dep_distance'] = self.results['structural']['dependency']['canonical'].get('avg_dependency_distance', 0)
            headline_scores['struct_dep_distance'] = self.results['structural']['dependency']['headline'].get('avg_dependency_distance', 0)

        # Compute aggregate scores (normalized)
        canonical_aggregate = np.mean(list(canonical_scores.values())) if canonical_scores else 0
        headline_aggregate = np.mean(list(headline_scores.values())) if headline_scores else 0

        complexity_ratio = canonical_aggregate / headline_aggregate if headline_aggregate > 0 else 1.0

        print(f"  Canonical Aggregate Complexity: {canonical_aggregate:.4f}")
        print(f"  Headline Aggregate Complexity:  {headline_aggregate:.4f}")
        print(f"  Complexity Ratio (C/H):         {complexity_ratio:.4f}")

        self.results['combined'] = {
            'canonical_scores': canonical_scores,
            'headline_scores': headline_scores,
            'canonical_aggregate': canonical_aggregate,
            'headline_aggregate': headline_aggregate,
            'complexity_ratio': complexity_ratio
        }

        return self.results['combined']

    def save_results(self):
        """Save all results to JSON and CSV files."""
        print(f"\n{'='*80}")
        print(f"SAVING RESULTS")
        print(f"{'='*80}\n")

        # Save complete JSON
        json_path = self.output_dir / 'multilevel_complexity_analysis.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"  ✓ Saved: {json_path}")

        # Save summary CSV
        summary_data = []

        # Lexical metrics
        if 'lexical' in self.results:
            for form_type in ['surface_forms', 'lemmas']:
                for register in ['canonical', 'headline']:
                    metrics = self.results['lexical'][form_type][register]
                    summary_data.append({
                        'level': 'lexical',
                        'sublevel': form_type,
                        'register': register,
                        **{k: v for k, v in metrics.items() if isinstance(v, (int, float))}
                    })

        # Morphological metrics
        if 'morphological' in self.results:
            for feat_type in ['pos_tags', 'morph_features']:
                for register in ['canonical', 'headline']:
                    metrics = self.results['morphological'][feat_type][register]
                    summary_data.append({
                        'level': 'morphological',
                        'sublevel': feat_type,
                        'register': register,
                        **{k: v for k, v in metrics.items() if isinstance(v, (int, float))}
                    })

        # Syntactic metrics
        if 'syntactic' in self.results:
            for synt_type in ['dependency_relations', 'constituency_labels']:
                for register in ['canonical', 'headline']:
                    metrics = self.results['syntactic'][synt_type][register]
                    summary_data.append({
                        'level': 'syntactic',
                        'sublevel': synt_type,
                        'register': register,
                        **{k: v for k, v in metrics.items() if isinstance(v, (int, float))}
                    })

        # Structural metrics
        if 'structural' in self.results:
            for struct_type in ['constituency', 'dependency']:
                for register in ['canonical', 'headline']:
                    metrics = self.results['structural'][struct_type][register]
                    summary_data.append({
                        'level': 'structural',
                        'sublevel': struct_type,
                        'register': register,
                        **metrics
                    })

        df = pd.DataFrame(summary_data)
        csv_path = self.output_dir / 'multilevel_complexity_summary.csv'
        df.to_csv(csv_path, index=False)
        print(f"  ✓ Saved: {csv_path}")

        # Save combined scores
        if 'combined' in self.results:
            combined_df = pd.DataFrame({
                'metric': list(self.results['combined']['canonical_scores'].keys()),
                'canonical': list(self.results['combined']['canonical_scores'].values()),
                'headline': list(self.results['combined']['headline_scores'].values())
            })
            combined_df['ratio'] = combined_df['canonical'] / combined_df['headline'].replace(0, 1)

            combined_path = self.output_dir / 'combined_complexity_scores.csv'
            combined_df.to_csv(combined_path, index=False)
            print(f"  ✓ Saved: {combined_path}")

        print("\n✓ All results saved successfully")

    def run_complete_analysis(self):
        """Run complete multi-level analysis."""
        print(f"\n{'='*80}")
        print(f"MULTI-LEVEL COMPLEXITY ANALYZER")
        print(f"Newspaper: {self.newspaper}")
        print(f"{'='*80}\n")

        # Run all levels
        self.analyze_lexical_level()
        self.analyze_morphological_level()
        self.analyze_syntactic_level()
        self.analyze_structural_level()
        self.compute_combined_metrics()

        # Save results
        self.save_results()

        print(f"\n{'='*80}")
        print(f"ANALYSIS COMPLETE")
        print(f"{'='*80}\n")
        print(f"Results saved to: {self.output_dir}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Multi-Level Complexity and Similarity Analyzer"
    )
    parser.add_argument(
        '--newspaper',
        default='Times-of-India',
        choices=['Times-of-India', 'Hindustan-Times', 'The-Hindu'],
        help='Newspaper to analyze'
    )

    args = parser.parse_args()

    analyzer = MultiLevelComplexityAnalyzer(args.newspaper)
    analyzer.run_complete_analysis()


if __name__ == '__main__':
    main()
