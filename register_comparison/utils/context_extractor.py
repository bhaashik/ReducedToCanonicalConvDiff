"""
Context Extraction Utility for Transformation Events

Extracts appropriate-sized context windows around transformation locations.
Window size varies by transformation type to capture relevant information.
"""

from typing import List, Dict, Any, Tuple, Optional


class ContextExtractor:
    """
    Extracts windowed context for linguistic transformation events.

    Context window sizes:
    - Lexical (word-level): ±3 tokens
    - Morphological: ±2 tokens
    - Syntactic (phrase-level): ±5 tokens
    - Structural (clause/sentence): ±7 tokens
    - Punctuation: ±4 tokens
    """

    # Context window sizes by feature category
    WINDOW_SIZES = {
        'lexical': 3,
        'morphological': 2,
        'syntactic': 5,
        'structural': 7,
        'punctuation': 4,
        'default': 3
    }

    # Feature category mapping
    FEATURE_CATEGORIES = {
        # Lexical
        'FW-DEL': 'lexical',
        'FW-ADD': 'lexical',
        'C-DEL': 'lexical',
        'C-ADD': 'lexical',
        'LEMMA-CHG': 'lexical',
        'FORM-CHG': 'lexical',
        'POS-CHG': 'lexical',

        # Morphological
        'FEAT-CHG': 'morphological',
        'VERB-FORM-CHG': 'morphological',

        # Syntactic
        'DEP-REL-CHG': 'syntactic',
        'HEAD-CHG': 'syntactic',
        'TOKEN-REORDER': 'syntactic',

        # Constituency/Structural
        'CONST-REM': 'structural',
        'CONST-ADD': 'structural',
        'CONST-MOV': 'structural',
        'CLAUSE-TYPE-CHG': 'structural',

        # Punctuation
        'PUNCT-DEL': 'punctuation',
        'PUNCT-ADD': 'punctuation',
        'PUNCT-SUBST': 'punctuation',

        # Structural metrics
        'TREE-DEPTH-DIFF': 'structural',
        'CONST-COUNT-DIFF': 'structural',
        'DEP-DIST-DIFF': 'structural',
        'BRANCH-DIFF': 'structural',

        # Headline typology
        'H-STRUCT': 'structural',
        'H-TYPE': 'structural',
        'F-TYPE': 'structural',

        # Other
        'LENGTH-CHG': 'structural',
    }

    @classmethod
    def get_window_size(cls, feature_id: str) -> int:
        """Get appropriate window size for a feature type."""
        category = cls.FEATURE_CATEGORIES.get(feature_id, 'default')
        return cls.WINDOW_SIZES.get(category, cls.WINDOW_SIZES['default'])

    @classmethod
    def extract_token_window(cls, tokens: List[Dict], position: int, window_size: int) -> str:
        """
        Extract a window of tokens around a position.

        Args:
            tokens: List of token dicts with 'form' field
            position: 0-indexed position of the target token
            window_size: Number of tokens on each side

        Returns:
            String of tokens in window
        """
        if not tokens or position < 0 or position >= len(tokens):
            return ""

        start = max(0, position - window_size)
        end = min(len(tokens), position + window_size + 1)

        window_tokens = tokens[start:end]

        # Mark the target token
        result_tokens = []
        for i, token in enumerate(window_tokens):
            token_form = token.get('form', str(token))
            if start + i == position:
                result_tokens.append(f"**{token_form}**")  # Mark target
            else:
                result_tokens.append(token_form)

        return " ".join(result_tokens)

    @classmethod
    def extract_char_window(cls, text: str, position: int, window_size: int = 30) -> str:
        """
        Extract a character-level window around a position.

        Args:
            text: Full text string
            position: Character position
            window_size: Number of characters on each side

        Returns:
            String window with target marked
        """
        if not text or position < 0 or position >= len(text):
            return text[:60] if text else ""  # Return start of text as fallback

        start = max(0, position - window_size)
        end = min(len(text), position + window_size + 1)

        before = text[start:position]
        target = text[position]
        after = text[position+1:end]

        return f"{before}**{target}**{after}"

    @classmethod
    def find_token_position(cls, tokens: List[Dict], wordform: str,
                           start_from: int = 0) -> Optional[int]:
        """
        Find position of a token by its wordform.

        Args:
            tokens: List of token dicts
            wordform: The word to find
            start_from: Start searching from this index

        Returns:
            Index of token or None
        """
        for i in range(start_from, len(tokens)):
            if tokens[i].get('form', '').lower() == wordform.lower():
                return i
        return None

    @classmethod
    def extract_dependency_context(cls, tokens: List[Dict], token_id: int,
                                   window_size: int = 2) -> Dict[str, Any]:
        """
        Extract dependency-based context including head and children.

        Args:
            tokens: CoNLL-U token list
            token_id: 1-indexed token ID
            window_size: Linear context window size

        Returns:
            Dict with dependency context info
        """
        if not tokens or token_id < 1 or token_id > len(tokens):
            return {}

        # Convert to 0-indexed
        token_idx = token_id - 1
        token = tokens[token_idx]

        # Get head
        head_id = token.get('head', 0)
        head_token = None
        if head_id > 0 and head_id <= len(tokens):
            head_token = tokens[head_id - 1]

        # Get children
        children = []
        for i, t in enumerate(tokens):
            if t.get('head', 0) == token_id:
                children.append(t)

        # Get linear window
        linear_window = cls.extract_token_window(tokens, token_idx, window_size)

        return {
            'token': token.get('form', ''),
            'lemma': token.get('lemma', ''),
            'pos': token.get('upos', ''),
            'deprel': token.get('deprel', ''),
            'head': head_token.get('form', '') if head_token else 'ROOT',
            'head_pos': head_token.get('upos', '') if head_token else '',
            'children': [c.get('form', '') for c in children],
            'linear_context': linear_window,
            'position': token_id
        }

    @classmethod
    def extract_punctuation_context(cls, text: str, punct_char: str,
                                    occurrence: int = 1) -> Dict[str, Any]:
        """
        Extract context around a punctuation mark.

        Args:
            text: Full text
            punct_char: The punctuation character
            occurrence: Which occurrence (1-indexed)

        Returns:
            Dict with punctuation context
        """
        positions = [i for i, c in enumerate(text) if c == punct_char]

        if occurrence < 1 or occurrence > len(positions):
            return {
                'punctuation': punct_char,
                'position': -1,
                'context': text[:40] if text else "",
                'before': "",
                'after': ""
            }

        pos = positions[occurrence - 1]
        window_size = 20

        before = text[max(0, pos-window_size):pos]
        after = text[pos+1:min(len(text), pos+window_size+1)]

        return {
            'punctuation': punct_char,
            'position': pos,
            'context': f"{before}**{punct_char}**{after}",
            'before': before.strip(),
            'after': after.strip()
        }

    @classmethod
    def extract_phrase_context(cls, const_tree, phrase_label: str) -> Dict[str, Any]:
        """
        Extract context for a phrase/constituent.

        Args:
            const_tree: NLTK Tree object
            phrase_label: The phrase label to find

        Returns:
            Dict with phrase context
        """
        if not const_tree or not hasattr(const_tree, 'label'):
            return {}

        # Find all subtrees with this label
        subtrees = [st for st in const_tree.subtrees() if st.label() == phrase_label]

        if not subtrees:
            return {
                'phrase_label': phrase_label,
                'text': '',
                'parent': '',
                'siblings': []
            }

        # Use first occurrence
        target = subtrees[0]
        target_text = " ".join(target.leaves())

        # Get parent
        parent_label = ''
        for parent in const_tree.subtrees():
            if target in list(parent):
                parent_label = parent.label()
                break

        return {
            'phrase_label': phrase_label,
            'text': target_text,
            'parent': parent_label,
            'depth': target.height(),
            'num_tokens': len(target.leaves())
        }
