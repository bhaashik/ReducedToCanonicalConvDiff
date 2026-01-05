"""
Feature detection methods for schema v5.0 new features.

This module adds detection for:
1. Punctuation features (PUNCT-DEL, PUNCT-ADD, PUNCT-SUBST)
2. Headline typology (H-STRUCT, H-TYPE, F-TYPE)
3. Structural complexity (TREE-DEPTH-DIFF, CONST-COUNT-DIFF, DEP-DIST-DIFF, BRANCH-DIFF)

Enhanced with:
- Windowed context extraction (±2-7 tokens depending on feature type)
- Schema-defined extra metadata fields
- Position, POS, wordform tracking

Excludes: TOKEN-COUNT-DIFF, CHAR-COUNT-DIFF (simple length features)
"""

from typing import List, Dict, Any
from register_comparison.aligners.aligner import AlignedSentencePair
from register_comparison.comparators.comparator import DifferenceEvent
from register_comparison.utils.event_enricher import EventEnricher
from register_comparison.utils.context_extractor import ContextExtractor
import re
import string


class V5FeatureDetector:
    """Detector for schema v5.0 new features with context extraction."""

    def __init__(self, schema):
        self.schema = schema
        self.enricher = EventEnricher(schema)
        self.context_extractor = ContextExtractor()

    # ================== PUNCTUATION FEATURES ==================

    def _detect_punctuation_changes(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect all punctuation-related changes (PUNCT-DEL, PUNCT-ADD, PUNCT-SUBST)."""
        events = []

        # Extract punctuation with positions from both texts
        canonical_punct = self._extract_punctuation_with_positions(aligned_pair.canonical_text)
        headline_punct = self._extract_punctuation_with_positions(aligned_pair.headline_text)

        # Detect deletions and additions
        events.extend(self._detect_punct_deletion(aligned_pair, canonical_punct, headline_punct))
        events.extend(self._detect_punct_addition(aligned_pair, canonical_punct, headline_punct))

        # Detect substitutions (punctuation ↔ function words)
        events.extend(self._detect_punct_substitution(aligned_pair))

        return events

    def _extract_punctuation_with_positions(self, text: str) -> Dict[str, List[int]]:
        """Extract all punctuation marks with their positions."""
        punct_map = {
            ',': 'comma',
            ':': 'colon',
            ';': 'semicolon',
            '—': 'dash',
            '-': 'hyphen',
            '.': 'period',
            '!': 'exclamation mark',
            '?': 'question mark',
            '"': 'quote',
            '(': 'parenthesis',
            ')': 'parenthesis',
            '/': 'slash',
            '\u2019': 'apostrophe',  # Right single quotation mark
            "'": 'apostrophe'
        }

        result = {}
        for i, char in enumerate(text):
            if char in punct_map:
                punct_type = punct_map[char]
                if punct_type not in result:
                    result[punct_type] = []
                result[punct_type].append(i)

        return result

    def _detect_punct_deletion(self, aligned_pair: AlignedSentencePair,
                               canonical_punct: Dict[str, List[int]],
                               headline_punct: Dict[str, List[int]]) -> List[DifferenceEvent]:
        """Detect punctuation deletion (present in canonical, absent in headline)."""
        events = []

        # Compare punctuation counts
        for punct_type in canonical_punct:
            canonical_count = len(canonical_punct[punct_type])
            headline_count = len(headline_punct.get(punct_type, []))

            # Skip sentence-final period deletions unless headline also has a period.
            # This prevents trivial CR-only full-stop differences from dominating PUNCT stats.
            if punct_type == 'period' and headline_count == 0:
                continue

            if canonical_count > headline_count:
                # Punctuation was deleted - enrich with context
                extra = self.enricher.enrich_punctuation_deletion(aligned_pair, punct_type)

                # Extract windowed context (±4 tokens for punctuation)
                window_size = self.context_extractor.get_window_size('PUNCT-DEL')
                if extra.get('position', -1) >= 0:
                    canonical_context = self.context_extractor.extract_char_window(
                        aligned_pair.canonical_text,
                        extra['position'],
                        window_size * 5  # Characters, not tokens
                    )
                else:
                    canonical_context = aligned_pair.canonical_text[:60]

                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="both",
                        feature_id="PUNCT-DEL",
                        canonical_value=punct_type,
                        headline_value="",
                        feature_name="Punctuation Deletion",
                        feature_mnemonic="PUNCT-DEL",
                        canonical_context=canonical_context,
                        headline_context=aligned_pair.headline_text[:60],
                        extra=extra
                    )
                )

        return events

    def _detect_punct_addition(self, aligned_pair: AlignedSentencePair,
                               canonical_punct: Dict[str, List[int]],
                               headline_punct: Dict[str, List[int]]) -> List[DifferenceEvent]:
        """Detect punctuation addition (absent in canonical, present in headline)."""
        events = []

        # Compare punctuation counts
        for punct_type in headline_punct:
            headline_count = len(headline_punct[punct_type])
            canonical_count = len(canonical_punct.get(punct_type, []))

            if headline_count > canonical_count:
                # Punctuation was added - enrich with context
                extra = self.enricher.enrich_punctuation_addition(aligned_pair, punct_type)

                # Extract windowed context
                window_size = self.context_extractor.get_window_size('PUNCT-ADD')
                if extra.get('position', -1) >= 0:
                    headline_context = self.context_extractor.extract_char_window(
                        aligned_pair.headline_text,
                        extra['position'],
                        window_size * 5
                    )
                else:
                    headline_context = aligned_pair.headline_text[:60]

                events.append(
                    DifferenceEvent(
                        newspaper=aligned_pair.newspaper,
                        sent_id=aligned_pair.sent_id,
                        parse_type="both",
                        feature_id="PUNCT-ADD",
                        canonical_value="",
                        headline_value=punct_type,
                        feature_name="Punctuation Addition",
                        feature_mnemonic="PUNCT-ADD",
                        canonical_context=aligned_pair.canonical_text[:60],
                        headline_context=headline_context,
                        extra=extra
                    )
                )

        return events

    def _detect_punct_substitution(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect punctuation ↔ function word substitutions."""
        events = []

        canonical_text = aligned_pair.canonical_text.lower()
        headline_text = aligned_pair.headline_text.lower()

        # Define substitution patterns
        substitution_patterns = [
            # Colon ↔ conjunction
            {
                'punct': ':',
                'words': ['and', 'or', 'that', 'which', 'who'],
                'canonical_to_headline': 'conjunction to colon',
                'headline_to_canonical': 'colon to conjunction'
            },
            # Comma ↔ conjunction (and)
            {
                'punct': ',',
                'words': ['and', 'or'],
                'canonical_to_headline': 'conjunction to comma',
                'headline_to_canonical': 'comma to conjunction'
            },
            # Dash ↔ relative clause
            {
                'punct': '—',
                'words': ['who', 'which', 'that', 'whose', 'whom'],
                'canonical_to_headline': 'relative clause to dash',
                'headline_to_canonical': 'dash to relative clause'
            },
            # Dash ↔ conjunction
            {
                'punct': '—',
                'words': ['and', 'but', 'or'],
                'canonical_to_headline': 'conjunction to dash',
                'headline_to_canonical': 'dash to conjunction'
            },
            # Semicolon ↔ conjunction
            {
                'punct': ';',
                'words': ['and', 'but', 'or', 'however', 'therefore'],
                'canonical_to_headline': 'conjunction to semicolon',
                'headline_to_canonical': 'semicolon to conjunction'
            },
            # Quote ↔ reported speech
            {
                'punct': '"',
                'words': ['said', 'says', 'stated', 'according to', 'reported'],
                'canonical_to_headline': 'reported speech to quote',
                'headline_to_canonical': 'quote to reported speech'
            },
            # Comma ↔ preposition
            {
                'punct': ',',
                'words': ['with', 'without', 'in', 'on', 'at', 'for'],
                'canonical_to_headline': 'preposition to comma',
                'headline_to_canonical': 'comma to preposition'
            },
            # Slash ↔ conjunction
            {
                'punct': '/',
                'words': ['and', 'or'],
                'canonical_to_headline': 'conjunction to slash',
                'headline_to_canonical': 'slash to conjunction'
            }
        ]

        for pattern in substitution_patterns:
            punct = pattern['punct']
            words = pattern['words']

            # Check canonical → headline transformation (word → punct)
            for word in words:
                # Simple heuristic: if word appears in canonical but not headline,
                # and punct appears in headline but not canonical
                word_pattern = r'\b' + re.escape(word) + r'\b'

                canonical_has_word = bool(re.search(word_pattern, canonical_text))
                headline_has_word = bool(re.search(word_pattern, headline_text))
                canonical_has_punct = punct in aligned_pair.canonical_text
                headline_has_punct = punct in aligned_pair.headline_text

                # Canonical has word, headline has punct instead
                if canonical_has_word and not headline_has_word and headline_has_punct and not canonical_has_punct:
                    value = pattern['canonical_to_headline']
                    events.append(
                        DifferenceEvent(
                            newspaper=aligned_pair.newspaper,
                            sent_id=aligned_pair.sent_id,
                            parse_type="both",
                            feature_id="PUNCT-SUBST",
                            canonical_value=word,
                            headline_value=punct,
                            feature_name="Punctuation Substitution",
                            feature_mnemonic="PUNCT-SUBST",
                            canonical_context=aligned_pair.canonical_text,
                            headline_context=aligned_pair.headline_text
                        )
                    )
                    break  # Only report once per pattern

                # Headline has word, canonical has punct instead
                elif headline_has_word and not canonical_has_word and canonical_has_punct and not headline_has_punct:
                    value = pattern['headline_to_canonical']
                    events.append(
                        DifferenceEvent(
                            newspaper=aligned_pair.newspaper,
                            sent_id=aligned_pair.sent_id,
                            parse_type="both",
                            feature_id="PUNCT-SUBST",
                            canonical_value=punct,
                            headline_value=word,
                            feature_name="Punctuation Substitution",
                            feature_mnemonic="PUNCT-SUBST",
                            canonical_context=aligned_pair.canonical_text,
                            headline_context=aligned_pair.headline_text
                        )
                    )
                    break  # Only report once per pattern

        return events

    # ================== HEADLINE TYPOLOGY FEATURES ==================

    def _detect_headline_typology(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect headline typology features (H-STRUCT, H-TYPE, F-TYPE)."""
        events = []
        events.extend(self._detect_headline_structure(aligned_pair))
        events.extend(self._detect_headline_type(aligned_pair))
        return events

    def _detect_headline_structure(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect headline structure (H-STRUCT): single-line vs micro-discourse."""
        events = []

        # Count sentences in headline (simple heuristic: count sentence-ending punctuation)
        headline_text = aligned_pair.headline_text
        sentence_endings = headline_text.count('.') + headline_text.count('?') + headline_text.count('!')

        # Determine structure type
        if sentence_endings > 1:
            struct_type = "micro-discourse"
        else:
            struct_type = "single-line"

        events.append(
            DifferenceEvent(
                newspaper=aligned_pair.newspaper,
                sent_id=aligned_pair.sent_id,
                parse_type="both",
                feature_id="H-STRUCT",
                canonical_value="",
                headline_value=struct_type,
                feature_name="Headline Structure",
                feature_mnemonic="H-STRUCT",
                canonical_context=aligned_pair.canonical_text,
                headline_context=aligned_pair.headline_text
            )
        )

        return events

    def _detect_headline_type(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect headline type (H-TYPE): fragment vs non-fragment."""
        events = []

        if not aligned_pair.headline_dep:
            return events

        # Check if headline has a finite verb (full predication)
        headline_tokens = list(aligned_pair.headline_dep)
        has_finite_verb = False

        for token in headline_tokens:
            if token.get('upos') in ['VERB', 'AUX']:
                feats = token.get('feats', {}) or {}
                verbform = feats.get('VerbForm', '')
                if verbform == 'Fin':
                    has_finite_verb = True
                    break

        # Determine headline type
        if has_finite_verb:
            h_type = "non-fragment"
        else:
            h_type = "fragment"

        events.append(
            DifferenceEvent(
                newspaper=aligned_pair.newspaper,
                sent_id=aligned_pair.sent_id,
                parse_type="both",
                feature_id="H-TYPE",
                canonical_value="",
                headline_value=h_type,
                feature_name="Headline Type",
                feature_mnemonic="H-TYPE",
                canonical_context=aligned_pair.canonical_text,
                headline_context=aligned_pair.headline_text
            )
        )

        return events

    # ================== STRUCTURAL COMPLEXITY FEATURES ==================

    def _detect_structural_complexity(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect structural complexity differences (TREE-DEPTH-DIFF, CONST-COUNT-DIFF, DEP-DIST-DIFF, BRANCH-DIFF)."""
        events = []
        events.extend(self._detect_tree_depth_diff(aligned_pair))
        events.extend(self._detect_constituent_count_diff(aligned_pair))
        events.extend(self._detect_dep_distance_diff(aligned_pair))
        events.extend(self._detect_branching_factor_diff(aligned_pair))
        return events

    def _detect_tree_depth_diff(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect tree depth difference (TREE-DEPTH-DIFF)."""
        events = []

        if aligned_pair.canonical_const and aligned_pair.headline_const:
            canonical_depth = self._get_tree_depth(aligned_pair.canonical_const)
            headline_depth = self._get_tree_depth(aligned_pair.headline_const)

            events.append(
                DifferenceEvent(
                    newspaper=aligned_pair.newspaper,
                    sent_id=aligned_pair.sent_id,
                    parse_type="constituency",
                    feature_id="TREE-DEPTH-DIFF",
                    canonical_value=str(canonical_depth),
                    headline_value=str(headline_depth),
                    feature_name="Tree Depth Difference",
                    feature_mnemonic="TREE-DEPTH-DIFF",
                    canonical_context=aligned_pair.canonical_text,
                    headline_context=aligned_pair.headline_text
                )
            )

        return events

    def _detect_constituent_count_diff(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect constituent count difference (CONST-COUNT-DIFF)."""
        events = []

        if aligned_pair.canonical_const and aligned_pair.headline_const:
            canonical_count = self._count_constituents(aligned_pair.canonical_const)
            headline_count = self._count_constituents(aligned_pair.headline_const)

            events.append(
                DifferenceEvent(
                    newspaper=aligned_pair.newspaper,
                    sent_id=aligned_pair.sent_id,
                    parse_type="constituency",
                    feature_id="CONST-COUNT-DIFF",
                    canonical_value=str(canonical_count),
                    headline_value=str(headline_count),
                    feature_name="Constituent Count Difference",
                    feature_mnemonic="CONST-COUNT-DIFF",
                    canonical_context=aligned_pair.canonical_text,
                    headline_context=aligned_pair.headline_text
                )
            )

        return events

    def _detect_dep_distance_diff(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect dependency distance difference (DEP-DIST-DIFF)."""
        events = []

        if aligned_pair.canonical_dep and aligned_pair.headline_dep:
            canonical_avg_dist = self._calculate_avg_dep_distance(aligned_pair.canonical_dep)
            headline_avg_dist = self._calculate_avg_dep_distance(aligned_pair.headline_dep)

            events.append(
                DifferenceEvent(
                    newspaper=aligned_pair.newspaper,
                    sent_id=aligned_pair.sent_id,
                    parse_type="dependency",
                    feature_id="DEP-DIST-DIFF",
                    canonical_value=f"{canonical_avg_dist:.2f}",
                    headline_value=f"{headline_avg_dist:.2f}",
                    feature_name="Dependency Distance Difference",
                    feature_mnemonic="DEP-DIST-DIFF",
                    canonical_context=aligned_pair.canonical_text,
                    headline_context=aligned_pair.headline_text
                )
            )

        return events

    def _detect_branching_factor_diff(self, aligned_pair: AlignedSentencePair) -> List[DifferenceEvent]:
        """Detect branching factor difference (BRANCH-DIFF)."""
        events = []

        if aligned_pair.canonical_const and aligned_pair.headline_const:
            canonical_branching = self._calculate_avg_branching_factor(aligned_pair.canonical_const)
            headline_branching = self._calculate_avg_branching_factor(aligned_pair.headline_const)

            events.append(
                DifferenceEvent(
                    newspaper=aligned_pair.newspaper,
                    sent_id=aligned_pair.sent_id,
                    parse_type="constituency",
                    feature_id="BRANCH-DIFF",
                    canonical_value=f"{canonical_branching:.2f}",
                    headline_value=f"{headline_branching:.2f}",
                    feature_name="Branching Factor Difference",
                    feature_mnemonic="BRANCH-DIFF",
                    canonical_context=aligned_pair.canonical_text,
                    headline_context=aligned_pair.headline_text
                )
            )

        return events

    # ================== HELPER METHODS ==================

    def _get_tree_depth(self, tree) -> int:
        """Calculate depth of constituency tree."""
        if not hasattr(tree, 'label'):
            return 0
        if not tree:
            return 1
        max_child_depth = 0
        for child in tree:
            if hasattr(child, 'label'):
                child_depth = self._get_tree_depth(child)
                max_child_depth = max(max_child_depth, child_depth)
        return 1 + max_child_depth

    def _count_constituents(self, tree) -> int:
        """Count total constituents in constituency tree."""
        if not hasattr(tree, 'label'):
            return 0
        count = 1  # Count this node
        for child in tree:
            if hasattr(child, 'label'):
                count += self._count_constituents(child)
        return count

    def _calculate_avg_dep_distance(self, token_list) -> float:
        """Calculate average dependency distance."""
        if not token_list:
            return 0.0

        tokens = list(token_list)
        total_distance = 0
        count = 0

        for token in tokens:
            if token.get('head', 0) > 0:  # Not root
                distance = abs(token['id'] - token['head'])
                total_distance += distance
                count += 1

        return total_distance / count if count > 0 else 0.0

    def _calculate_avg_branching_factor(self, tree) -> float:
        """Calculate average branching factor of constituency tree."""
        if not hasattr(tree, 'label'):
            return 0.0

        total_children = 0
        num_nodes = 0

        def traverse(subtree):
            nonlocal total_children, num_nodes
            if not hasattr(subtree, 'label'):
                return

            # Count immediate children with labels
            children_with_labels = sum(1 for child in subtree if hasattr(child, 'label'))
            if children_with_labels > 0:
                total_children += children_with_labels
                num_nodes += 1

            # Recurse
            for child in subtree:
                if hasattr(child, 'label'):
                    traverse(child)

        traverse(tree)
        return total_children / num_nodes if num_nodes > 0 else 0.0
