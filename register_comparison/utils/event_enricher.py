"""
Event Enricher for Transformation Events

Enriches DifferenceEvent objects with:
- Windowed context extraction
- Schema-defined extra metadata fields
- Position, POS, wordform, and structural information
"""

from typing import Dict, Any, List, Optional
from register_comparison.utils.context_extractor import ContextExtractor
from register_comparison.aligners.aligner import AlignedSentencePair


class EventEnricher:
    """
    Enriches transformation events with context and metadata.

    Uses schema-defined "extra" fields to populate event metadata.
    """

    def __init__(self, schema):
        self.schema = schema
        self.context_extractor = ContextExtractor()

    def enrich_lexical_deletion(self, aligned_pair: AlignedSentencePair,
                               feature_id: str, deleted_value: str,
                               token_position: int = None) -> Dict[str, Any]:
        """
        Enrich FW-DEL or C-DEL event.

        Extra fields: deleted_wordform, pos, position
        """
        extra = {}

        if not aligned_pair.canonical_dep:
            return extra

        canonical_tokens = list(aligned_pair.canonical_dep)

        # Find the deleted token
        if token_position is None:
            # Try to find by value mnemonic (e.g., "ART-DEL" -> look for articles)
            token_position = self._find_deleted_token(canonical_tokens, deleted_value)

        if token_position is not None and 0 <= token_position < len(canonical_tokens):
            token = canonical_tokens[token_position]

            extra['deleted_wordform'] = token.get('form', '')
            extra['pos'] = token.get('upos', '')
            extra['position'] = token_position + 1  # 1-indexed

            # Extract context window
            window_size = self.context_extractor.get_window_size(feature_id)
            dep_context = self.context_extractor.extract_dependency_context(
                canonical_tokens, token_position + 1, window_size
            )

            extra['lemma'] = dep_context.get('lemma', '')
            extra['deprel'] = dep_context.get('deprel', '')
            extra['context_window'] = dep_context.get('linear_context', '')

        return extra

    def enrich_lexical_addition(self, aligned_pair: AlignedSentencePair,
                               feature_id: str, added_value: str,
                               token_position: int = None) -> Dict[str, Any]:
        """
        Enrich FW-ADD or C-ADD event.

        Extra fields: added_wordform, pos, position
        """
        extra = {}

        if not aligned_pair.headline_dep:
            return extra

        headline_tokens = list(aligned_pair.headline_dep)

        # Find the added token
        if token_position is None:
            token_position = self._find_added_token(headline_tokens, added_value)

        if token_position is not None and 0 <= token_position < len(headline_tokens):
            token = headline_tokens[token_position]

            extra['added_wordform'] = token.get('form', '')
            extra['pos'] = token.get('upos', '')
            extra['position'] = token_position + 1  # 1-indexed

            # Extract context window
            window_size = self.context_extractor.get_window_size(feature_id)
            dep_context = self.context_extractor.extract_dependency_context(
                headline_tokens, token_position + 1, window_size
            )

            extra['lemma'] = dep_context.get('lemma', '')
            extra['deprel'] = dep_context.get('deprel', '')
            extra['context_window'] = dep_context.get('linear_context', '')

        return extra

    def enrich_morphological_change(self, aligned_pair: AlignedSentencePair,
                                   canonical_value: str, headline_value: str,
                                   feature_name: str) -> Dict[str, Any]:
        """
        Enrich FEAT-CHG event.

        Extra fields: source_feats, target_feats, feature_name, source_value, target_value
        """
        extra = {
            'feature_name': feature_name,
            'source_value': canonical_value,
            'target_value': headline_value,
            'source_feats': canonical_value,
            'target_feats': headline_value
        }

        # Try to find the token with this morphological difference
        if aligned_pair.canonical_dep and aligned_pair.headline_dep:
            canonical_tokens = list(aligned_pair.canonical_dep)
            headline_tokens = list(aligned_pair.headline_dep)

            # Simple heuristic: find matching lemmas with different features
            for c_tok in canonical_tokens:
                c_lemma = c_tok.get('lemma', '')
                c_feats = c_tok.get('feats', {}) or {}

                for h_tok in headline_tokens:
                    h_lemma = h_tok.get('lemma', '')
                    h_feats = h_tok.get('feats', {}) or {}

                    if c_lemma == h_lemma and c_lemma:  # Same lemma
                        # Check if this feature differs
                        if str(c_feats.get(feature_name, '')) == canonical_value and \
                           str(h_feats.get(feature_name, '')) == headline_value:
                            extra['wordform_canonical'] = c_tok.get('form', '')
                            extra['wordform_headline'] = h_tok.get('form', '')
                            extra['lemma'] = c_lemma
                            extra['pos'] = c_tok.get('upos', '')
                            break

        return extra

    def enrich_punctuation_deletion(self, aligned_pair: AlignedSentencePair,
                                   punct_type: str) -> Dict[str, Any]:
        """
        Enrich PUNCT-DEL event.

        Extra fields: deleted_punctuation, position, context
        """
        extra = {
            'deleted_punctuation': punct_type,
            'position': -1,
            'context': ''
        }

        # Map punctuation type to character
        punct_map = {
            'comma': ',',
            'period': '.',
            'colon': ':',
            'semicolon': ';',
            'dash': '—',
            'hyphen': '-',
            'exclamation mark': '!',
            'question mark': '?',
            'quote': '"',
            'parenthesis': '(',
            'slash': '/',
            'apostrophe': "'"
        }

        punct_char = punct_map.get(punct_type, punct_type)

        # Extract context around punctuation in canonical
        punct_context = self.context_extractor.extract_punctuation_context(
            aligned_pair.canonical_text, punct_char
        )

        extra['position'] = punct_context.get('position', -1)
        extra['context'] = punct_context.get('context', '')
        extra['before'] = punct_context.get('before', '')
        extra['after'] = punct_context.get('after', '')

        return extra

    def enrich_punctuation_addition(self, aligned_pair: AlignedSentencePair,
                                   punct_type: str) -> Dict[str, Any]:
        """
        Enrich PUNCT-ADD event.

        Extra fields: added_punctuation, position, context
        """
        extra = {
            'added_punctuation': punct_type,
            'position': -1,
            'context': ''
        }

        # Map punctuation type to character
        punct_map = {
            'comma': ',',
            'period': '.',
            'colon': ':',
            'semicolon': ';',
            'dash': '—',
            'hyphen': '-',
            'exclamation mark': '!',
            'question mark': '?',
            'quote': '"',
            'parenthesis': '(',
            'slash': '/',
            'apostrophe': "'"
        }

        punct_char = punct_map.get(punct_type, punct_type)

        # Extract context around punctuation in headline
        punct_context = self.context_extractor.extract_punctuation_context(
            aligned_pair.headline_text, punct_char
        )

        extra['position'] = punct_context.get('position', -1)
        extra['context'] = punct_context.get('context', '')
        extra['before'] = punct_context.get('before', '')
        extra['after'] = punct_context.get('after', '')

        return extra

    def enrich_punctuation_substitution(self, aligned_pair: AlignedSentencePair,
                                       canonical_value: str, headline_value: str) -> Dict[str, Any]:
        """
        Enrich PUNCT-SUBST event.

        Extra fields: source_element, target_element, transformation_type, context
        """
        extra = {
            'source_element': canonical_value,
            'target_element': headline_value,
            'transformation_type': f"{canonical_value} → {headline_value}",
            'context': ''
        }

        # Extract context from both sides
        if len(canonical_value) == 1:  # Punctuation character
            punct_context = self.context_extractor.extract_punctuation_context(
                aligned_pair.canonical_text, canonical_value
            )
            extra['context_canonical'] = punct_context.get('context', '')

        if len(headline_value) == 1:  # Punctuation character
            punct_context = self.context_extractor.extract_punctuation_context(
                aligned_pair.headline_text, headline_value
            )
            extra['context_headline'] = punct_context.get('context', '')

        extra['context'] = f"C: {extra.get('context_canonical', '')} | H: {extra.get('context_headline', '')}"

        return extra

    def enrich_structural_complexity(self, aligned_pair: AlignedSentencePair,
                                    feature_id: str, canonical_value: str,
                                    headline_value: str) -> Dict[str, Any]:
        """
        Enrich structural complexity features (TREE-DEPTH-DIFF, etc.).

        Extra fields depend on specific feature.
        """
        extra = {}

        if feature_id == 'TREE-DEPTH-DIFF':
            extra['canonical_depth'] = canonical_value
            extra['headline_depth'] = headline_value
            try:
                c_depth = float(canonical_value)
                h_depth = float(headline_value)
                extra['depth_ratio'] = h_depth / c_depth if c_depth > 0 else 0
            except (ValueError, ZeroDivisionError):
                extra['depth_ratio'] = 0

        elif feature_id == 'CONST-COUNT-DIFF':
            extra['canonical_constituent_count'] = canonical_value
            extra['headline_constituent_count'] = headline_value
            try:
                c_count = float(canonical_value)
                h_count = float(headline_value)
                extra['reduction_ratio'] = h_count / c_count if c_count > 0 else 0
            except (ValueError, ZeroDivisionError):
                extra['reduction_ratio'] = 0

        elif feature_id == 'DEP-DIST-DIFF':
            extra['canonical_avg_dep_distance'] = canonical_value
            extra['headline_avg_dep_distance'] = headline_value
            try:
                c_dist = float(canonical_value)
                h_dist = float(headline_value)
                extra['distance_ratio'] = h_dist / c_dist if c_dist > 0 else 0
            except (ValueError, ZeroDivisionError):
                extra['distance_ratio'] = 0

        elif feature_id == 'BRANCH-DIFF':
            extra['canonical_avg_branching'] = canonical_value
            extra['headline_avg_branching'] = headline_value
            try:
                c_branch = float(canonical_value)
                h_branch = float(headline_value)
                extra['branching_ratio'] = h_branch / c_branch if c_branch > 0 else 0
            except (ValueError, ZeroDivisionError):
                extra['branching_ratio'] = 0

        return extra

    def _find_deleted_token(self, canonical_tokens: List[Dict], deleted_value: str) -> Optional[int]:
        """Find position of deleted token based on value mnemonic."""
        # This is a heuristic - actual implementation depends on alignment
        # For now, return None and let caller specify position
        return None

    def _find_added_token(self, headline_tokens: List[Dict], added_value: str) -> Optional[int]:
        """Find position of added token based on value mnemonic."""
        # This is a heuristic - actual implementation depends on alignment
        # For now, return None and let caller specify position
        return None
