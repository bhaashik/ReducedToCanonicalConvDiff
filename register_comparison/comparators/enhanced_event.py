"""
Enhanced DifferenceEvent with rich bi-parse context.

Captures detailed linguistic context from BOTH dependency and constituency parses
to enable highly deterministic transformation rules.

CRITICAL: All context captured from HEADLINE side (deterministically available during generation).
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict


@dataclass
class TokenContext:
    """
    Complete linguistic context for a single token.

    Combines information from BOTH dependency and constituency parses.
    ALL features deterministically extractable from headline.
    """

    # Basic token info
    token_id: Optional[int] = None
    form: Optional[str] = None
    lemma: Optional[str] = None

    # Dependency parse features
    upos: Optional[str] = None  # Universal POS
    xpos: Optional[str] = None  # Language-specific POS
    dep_rel: Optional[str] = None  # Dependency relation to head
    head_id: Optional[int] = None  # Head token ID
    head_lemma: Optional[str] = None  # Head's lemma
    head_upos: Optional[str] = None  # Head's POS

    # Morphological features (from CoNLL-U)
    morph_features: Dict[str, str] = field(default_factory=dict)  # Number, Tense, etc.

    # Constituency parse features
    parent_phrase_label: Optional[str] = None  # NP, VP, PP, etc.
    phrase_depth: Optional[int] = None  # Depth in constituency tree
    is_phrase_head: Optional[bool] = None  # Is this the head of its phrase?

    # Positional context
    token_index: Optional[int] = None  # Position in sentence (0-based)
    sentence_length: Optional[int] = None
    position_category: Optional[str] = None  # 'initial', 'medial', 'final'
    distance_to_root: Optional[int] = None  # In dependency tree

    # Local syntactic context (from dependency parse)
    left_sibling_upos: Optional[str] = None  # Left dependent's POS
    right_sibling_upos: Optional[str] = None  # Right dependent's POS
    children_dep_rels: List[str] = field(default_factory=list)  # Relations of dependents
    has_determiner: Optional[bool] = None
    has_auxiliary: Optional[bool] = None
    has_copula: Optional[bool] = None

    # Lexical semantic features
    is_proper_noun: Optional[bool] = None
    is_pronoun: Optional[bool] = None
    is_content_word: Optional[bool] = None  # vs function word
    is_finite_verb: Optional[bool] = None
    is_participle: Optional[bool] = None

    # Phrasal context (from constituency)
    parent_phrase_siblings: List[str] = field(default_factory=list)  # Sister constituents
    grandparent_phrase_label: Optional[str] = None
    clause_type: Optional[str] = None  # From parent S/SBAR

    # Definiteness and referential features
    has_definite_article: Optional[bool] = None
    has_indefinite_article: Optional[bool] = None
    is_bare_noun: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    def get_context_signature(self, granularity: str = 'full') -> str:
        """
        Generate context signature for rule matching.

        Different granularities for testing which features matter:
        - minimal: Just POS
        - lexical: POS + lemma + is_proper_noun
        - syntactic: + dep_rel + head_upos + position
        - phrasal: + parent_phrase + clause_type
        - full: All features
        """

        if granularity == 'minimal':
            return f"{self.upos}"

        elif granularity == 'lexical':
            return f"{self.upos}:{self.lemma}:{self.is_proper_noun}"

        elif granularity == 'syntactic':
            return (f"{self.upos}:{self.dep_rel}:{self.head_upos}:"
                   f"{self.position_category}:{self.has_determiner}")

        elif granularity == 'phrasal':
            return (f"{self.upos}:{self.dep_rel}:{self.parent_phrase_label}:"
                   f"{self.clause_type}:{self.is_phrase_head}")

        else:  # full
            return (f"{self.upos}:{self.dep_rel}:{self.head_upos}:"
                   f"{self.parent_phrase_label}:{self.position_category}:"
                   f"{self.has_determiner}:{self.is_proper_noun}:"
                   f"{self.clause_type}:{self.phrase_depth}:"
                   f"{self.morph_features.get('Tense')}:"
                   f"{self.morph_features.get('Number')}")


@dataclass
class EnhancedDifferenceEvent:
    """
    Enhanced event capturing rich bi-parse context.

    Stores BOTH headline and canonical contexts to enable:
    1. Rule extraction (what changes?)
    2. Pattern analysis (when does it change?)
    3. Deterministic generation (how to predict change?)
    """

    # Basic event metadata
    newspaper: str
    sent_id: int
    parse_type: str  # "dependency" or "constituency" (but has info from both!)
    feature_id: str
    feature_name: str

    # Transformation values
    canonical_value: str  # What it becomes in canonical form
    headline_value: str  # What it is in headline (often "ABSENT")

    # RICH CONTEXT from headline (deterministically available during generation)
    headline_context: Optional[TokenContext] = None

    # Context from canonical (for analysis only - not available during generation)
    canonical_context: Optional[TokenContext] = None

    # Sentence-level context
    headline_sentence: Optional[str] = None
    canonical_sentence: Optional[str] = None
    headline_length: Optional[int] = None
    canonical_length: Optional[int] = None

    # Additional metadata
    confidence: Optional[float] = None  # Filled in by systematicity analyzer
    frequency: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'newspaper': self.newspaper,
            'sent_id': self.sent_id,
            'parse_type': self.parse_type,
            'feature_id': self.feature_id,
            'feature_name': self.feature_name,
            'canonical_value': self.canonical_value,
            'headline_value': self.headline_value,
            'headline_context': self.headline_context.to_dict() if self.headline_context else None,
            'canonical_context': self.canonical_context.to_dict() if self.canonical_context else None,
            'headline_sentence': self.headline_sentence,
            'canonical_sentence': self.canonical_sentence,
            'headline_length': self.headline_length,
            'canonical_length': self.canonical_length,
            'confidence': self.confidence,
            'frequency': self.frequency
        }

    def get_transformation_pattern(self, context_granularity: str = 'full') -> str:
        """
        Generate transformation pattern key for systematicity analysis.

        Format: FEATURE::headline_context→canonical_value

        This allows us to test: "Given this headline context, what transformation occurs?"
        """

        if self.headline_context:
            context_sig = self.headline_context.get_context_signature(context_granularity)
        else:
            context_sig = "NO_CONTEXT"

        return f"{self.feature_id}::{self.headline_value}@{context_sig}→{self.canonical_value}"

    def is_deletion_event(self) -> bool:
        """Check if this is a deletion (headline has something canonical doesn't)"""
        return "DEL" in self.feature_id or self.canonical_value == "ABSENT"

    def is_insertion_event(self) -> bool:
        """Check if this is an insertion (canonical has something headline doesn't)"""
        return "ADD" in self.feature_id or self.headline_value == "ABSENT"

    def is_modification_event(self) -> bool:
        """Check if this is a modification (both have something, but different)"""
        return (not self.is_deletion_event() and
                not self.is_insertion_event() and
                self.headline_value != self.canonical_value)


def extract_token_context_from_dep_parse(token, sent, sent_text: str = "") -> TokenContext:
    """
    Extract rich context from a dependency parse token.

    Args:
        token: CoNLL-U token from parsed sentence
        sent: Full sentence object (for accessing other tokens)
        sent_text: Original sentence text

    Returns:
        TokenContext with all extractable features
    """

    context = TokenContext()

    # Basic token info
    context.token_id = int(token['id']) if isinstance(token['id'], (int, str)) and str(token['id']).isdigit() else None
    context.form = token.get('form', '')
    context.lemma = token.get('lemma', '')

    # POS tags
    context.upos = token.get('upos', '')
    context.xpos = token.get('xpos', '')

    # Dependency info
    context.dep_rel = token.get('deprel', '')
    context.head_id = int(token['head']) if 'head' in token and str(token['head']).isdigit() else None

    # Find head token for more context
    if context.head_id and context.head_id > 0:
        try:
            head_token = sent[context.head_id - 1]  # CoNLL-U is 1-indexed
            context.head_lemma = head_token.get('lemma', '')
            context.head_upos = head_token.get('upos', '')
        except (IndexError, KeyError):
            pass

    # Morphological features
    feats = token.get('feats')
    if feats and isinstance(feats, dict):
        context.morph_features = feats

    # Positional info
    if context.token_id:
        context.token_index = context.token_id - 1  # 0-based
        context.sentence_length = len(sent)

        if context.token_index == 0:
            context.position_category = 'initial'
        elif context.token_index == len(sent) - 1:
            context.position_category = 'final'
        else:
            context.position_category = 'medial'

    # Lexical semantic features
    context.is_proper_noun = (context.upos == 'PROPN')
    context.is_pronoun = (context.upos == 'PRON')
    context.is_content_word = context.upos in ['NOUN', 'VERB', 'ADJ', 'ADV', 'PROPN']

    # Verb features
    if context.upos == 'VERB' or context.upos == 'AUX':
        verb_form = context.morph_features.get('VerbForm', '')
        context.is_finite_verb = (verb_form == 'Fin')
        context.is_participle = (verb_form in ['Part', 'Ger'])

    # Check for dependents (children)
    children_rels = []
    has_det = False
    has_aux = False
    has_cop = False

    for other_token in sent:
        other_head = other_token.get('head')
        if other_head == context.token_id:
            child_rel = other_token.get('deprel', '')
            children_rels.append(child_rel)

            if child_rel == 'det':
                has_det = True
                # Check if definite or indefinite
                child_lemma = other_token.get('lemma', '').lower()
                if child_lemma == 'the':
                    context.has_definite_article = True
                elif child_lemma in ['a', 'an']:
                    context.has_indefinite_article = True
            elif child_rel == 'aux':
                has_aux = True
            elif child_rel == 'cop':
                has_cop = True

    context.children_dep_rels = children_rels
    context.has_determiner = has_det
    context.has_auxiliary = has_aux
    context.has_copula = has_cop

    # Bare noun check
    if context.upos == 'NOUN' or context.upos == 'PROPN':
        context.is_bare_noun = not has_det

    return context


def extract_token_context_from_const_parse(token_index: int, const_tree, sent_text: str = "") -> TokenContext:
    """
    Extract constituency-based context features.

    Args:
        token_index: Token position in sentence
        const_tree: NLTK Tree object of constituency parse
        sent_text: Original sentence

    Returns:
        TokenContext with constituency features populated
    """

    context = TokenContext()
    context.token_index = token_index

    # Find the token's position in tree and extract phrasal context
    # This would require tree traversal to find the token's parent phrases

    # Placeholder - full implementation would traverse tree
    # For now, return minimal context

    return context


def merge_contexts(dep_context: TokenContext, const_context: TokenContext) -> TokenContext:
    """
    Merge dependency and constituency contexts into single rich context.

    This is the KEY insight: Rules can use BOTH parse types simultaneously!
    """

    merged = TokenContext()

    # Copy all dependency features
    for field_name, field_value in asdict(dep_context).items():
        if field_value is not None:
            setattr(merged, field_name, field_value)

    # Add constituency features (only if not already set)
    for field_name, field_value in asdict(const_context).items():
        if field_value is not None and getattr(merged, field_name, None) is None:
            setattr(merged, field_name, field_value)

    return merged
