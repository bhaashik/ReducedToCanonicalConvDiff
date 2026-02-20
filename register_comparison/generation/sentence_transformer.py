"""
Sentence Transformer: Applies bidirectional transformation rules to CoNLL-U
parsed sentences to produce transformed sentences in the target register.

v2 — constituency-aware, with bug fixes for verb-fronting, auxiliary
doubling, and over-deletion.

Workflow:
  1. Load source-register CoNLL-U tokens (+ optional constituency tree)
  2. Build head chain from dependency tree to protect core arguments
  3. Find candidate rule applications with constituency-aware filtering
  4. Resolve conflicts via ConstraintResolver
  5. Apply planned actions (feature changes -> deletions -> structural)
  6. Realize surface text via SurfaceRealizer
"""

import copy
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from register_comparison.generation.bidirectional_rules import (
    RuleSet, FeatureRule, DeletionRule, FormRule, StructuralRule,
    DELETION_VALUE_TO_POS,
)
from register_comparison.generation.constraint_resolver import (
    ConstraintResolver, PlannedAction, FEATURE_PRIORITY,
)
from register_comparison.generation.surface_realizer import SurfaceRealizer


# Maximum fraction of tokens that may be deleted from a single sentence.
MAX_DELETION_FRACTION = 0.35

# Minimum confidence for a rule to actually fire during transformation.
MIN_APPLY_CONFIDENCE = 0.5

# Core dependency relations that should never be deleted
CORE_DEPRELS = {'nsubj', 'root', 'obj', 'nsubj:pass'}

# Peripheral constituent labels (safe to delete from)
PERIPHERAL_LABELS = {'PP', 'SBAR', 'ADVP', 'ADJP', 'PRN'}


@dataclass
class TransformedSentence:
    """Result of transforming a single sentence."""
    source_tokens: List[Dict]       # Original CoNLL-U tokens
    transformed_tokens: List[Dict]  # After applying rules
    generated_text: str             # Surface-realized text
    applied_actions: List[PlannedAction]
    skipped_actions: List[PlannedAction]
    conflict_count: int
    hypothesis_id: int = -1         # Which hypothesis strategy produced this


class ConstituencyHelper:
    """Parses a bracketed constituency tree and provides structural queries."""

    def __init__(self, tree_str: Optional[str] = None):
        self._tree = None
        self._leaves: List[str] = []
        self._leaf_labels: List[str] = []      # POS tag per leaf
        self._leaf_ancestors: List[List[str]] = []  # ancestor labels per leaf
        self._subject_span: Optional[Tuple[int, int]] = None
        self._available = False

        if tree_str:
            self._parse(tree_str)

    @property
    def available(self) -> bool:
        return self._available

    def _parse(self, tree_str: str):
        """Parse a bracketed tree string using nltk.Tree."""
        try:
            from nltk import Tree
        except ImportError:
            return

        try:
            tree = Tree.fromstring(tree_str)
        except (ValueError, IndexError):
            return

        self._tree = tree
        self._leaves = tree.leaves()
        self._extract_leaf_info(tree)
        self._find_subject_span(tree)
        self._available = True

    def _extract_leaf_info(self, tree):
        """Extract POS tags and ancestor labels for each leaf."""
        from nltk import Tree

        positions = tree.treepositions('leaves')
        for pos in positions:
            # POS tag is the parent node label
            parent_pos = pos[:-1]
            label = tree[parent_pos].label() if isinstance(tree[parent_pos], Tree) else ''
            self._leaf_labels.append(label)

            # Collect ancestor labels (from root down to parent)
            ancestors = []
            for depth in range(len(parent_pos)):
                node = tree[parent_pos[:depth + 1]]
                if isinstance(node, Tree):
                    ancestors.append(node.label())
            self._leaf_ancestors.append(ancestors)

    def _find_subject_span(self, tree):
        """Find the span of the subject NP (first NP directly under S)."""
        from nltk import Tree

        def find_s_node(t):
            if isinstance(t, Tree) and t.label() == 'S':
                return t
            if isinstance(t, Tree):
                for child in t:
                    result = find_s_node(child)
                    if result:
                        return result
            return None

        s_node = find_s_node(tree)
        if not s_node:
            return

        # Find first NP child of S (typically subject)
        offset = 0
        for child in s_node:
            if isinstance(child, Tree):
                n_leaves = len(child.leaves())
                if child.label() == 'NP':
                    self._subject_span = (offset, offset + n_leaves)
                    return
                offset += n_leaves
            else:
                offset += 1

    def is_in_subject_np(self, token_idx: int) -> bool:
        """Check if token_idx falls within the subject NP."""
        if not self._available or self._subject_span is None:
            return False
        start, end = self._subject_span
        return start <= token_idx < end

    def is_in_peripheral_constituent(self, token_idx: int) -> bool:
        """Check if a token is inside a PP, SBAR, ADVP, etc."""
        if not self._available or token_idx >= len(self._leaf_ancestors):
            return True  # default: allow deletion if no tree info
        ancestors = set(self._leaf_ancestors[token_idx])
        return bool(ancestors & PERIPHERAL_LABELS)

    def get_reporting_clause_pattern(self) -> Optional[Dict]:
        """
        Detect reporting clause pattern: (S (NP subj) (VP (VBD said) (SBAR ...))).

        Returns dict with 'verb_idx', 'sbar_start', 'sbar_end' if found.
        """
        if not self._available or not self._tree:
            return None

        from nltk import Tree

        def search_reporting(t, offset=0):
            if not isinstance(t, Tree):
                return None, offset + 1

            if t.label() == 'S':
                child_offset = offset
                vp_node = None
                vp_offset = 0
                for child in t:
                    if isinstance(child, Tree):
                        n_leaves = len(child.leaves())
                        if child.label() == 'VP':
                            vp_node = child
                            vp_offset = child_offset
                        child_offset += n_leaves
                    else:
                        child_offset += 1

                if vp_node:
                    result = self._check_vp_for_reporting(vp_node, vp_offset)
                    if result:
                        return result, child_offset

            # Recurse
            child_offset = offset
            for child in t:
                if isinstance(child, Tree):
                    result, child_offset = search_reporting(child, child_offset)
                    if result:
                        return result, child_offset
                else:
                    child_offset += 1
            return None, child_offset

        result, _ = search_reporting(self._tree)
        return result

    def _check_vp_for_reporting(self, vp_node, vp_offset: int) -> Optional[Dict]:
        """Check if a VP contains a reporting verb + SBAR."""
        from nltk import Tree

        reporting_verbs = {'said', 'says', 'told', 'stated', 'added',
                          'claimed', 'reported', 'announced', 'declared',
                          'noted', 'mentioned', 'remarked', 'explained'}

        verb_idx = None
        sbar_start = None
        sbar_end = None
        offset = vp_offset

        for child in vp_node:
            if isinstance(child, Tree):
                n_leaves = len(child.leaves())
                if child.label().startswith('VB'):
                    leaf = child.leaves()[0].lower() if child.leaves() else ''
                    if leaf in reporting_verbs:
                        verb_idx = offset
                elif child.label() == 'SBAR':
                    sbar_start = offset
                    sbar_end = offset + n_leaves
                # Also check nested VP (for "has said" patterns)
                elif child.label() == 'VP':
                    nested = self._check_vp_for_reporting(child, offset)
                    if nested:
                        return nested
                offset += n_leaves
            else:
                offset += 1

        if verb_idx is not None and sbar_start is not None:
            return {
                'verb_idx': verb_idx,
                'sbar_start': sbar_start,
                'sbar_end': sbar_end,
            }
        return None

    def align_to_tokens(self, tokens: List[Dict]) -> bool:
        """
        Check if constituency tree leaves align with CoNLL-U tokens.

        Returns True if leaves match token forms (allowing minor mismatches).
        """
        if not self._available:
            return False
        if len(self._leaves) != len(tokens):
            return False
        matches = sum(1 for leaf, tok in zip(self._leaves, tokens)
                      if leaf.lower() == (tok.get('form', '') or '').lower())
        return matches / max(1, len(tokens)) > 0.8


class SentenceTransformer:
    """
    Applies a RuleSet to CoNLL-U token lists to produce transformed sentences.

    v2 improvements:
    - Constituency-aware deletion filtering
    - Disabled blind verb-fronting (CONST-MOV)
    - Protected head chain (nsubj, root, obj)
    - Merged feature changes to prevent auxiliary doubling
    - Context-aware form rule matching
    """

    def __init__(self, ruleset: RuleSet, realizer: SurfaceRealizer,
                 constituency_trees: Optional[List[str]] = None):
        self.ruleset = ruleset
        self.realizer = realizer
        self.resolver = ConstraintResolver()
        self._constituency_trees = constituency_trees or []

    def transform(self, conllu_tokens: List[Dict],
                  const_tree_str: Optional[str] = None,
                  hypothesis_id: int = -1,
                  rule_filter: Optional[str] = None,
                  min_confidence: float = MIN_APPLY_CONFIDENCE,
                  allow_structural: bool = True,
                  allow_deletions: bool = True,
                  allow_feature_changes: bool = True,
                  allow_form_changes: Optional[bool] = None,
                  rule_sample_seed: Optional[int] = None,
                  rule_sample_frac: float = 1.0) -> TransformedSentence:
        """
        Transform a single sentence (list of CoNLL-U token dicts).

        Args:
            conllu_tokens: Source tokens.
            const_tree_str: Optional bracketed constituency tree string.
            hypothesis_id: Which hypothesis produced this (-1 = default).
            rule_filter: Not used currently (reserved).
            min_confidence: Minimum rule confidence to apply.
            allow_structural: Whether to apply structural rules.
            allow_deletions: Whether to apply deletion rules.
            allow_feature_changes: Whether to apply FEAT-CHG/DEP-REL-CHG rules.
            allow_form_changes: Whether to apply FORM-CHG rules.
                Defaults to same value as allow_feature_changes if None.
            rule_sample_seed: If set, randomly sample rules.
            rule_sample_frac: Fraction of rules to sample.
        """
        tokens = [copy.deepcopy(t) for t in conllu_tokens]

        # Resolve allow_form_changes default
        if allow_form_changes is None:
            allow_form_changes = allow_feature_changes

        # Build constituency helper
        const_helper = ConstituencyHelper(const_tree_str)

        # Build head chain from dependency tree
        head_chain = self._build_head_chain(tokens)

        # Phase 1: Find all candidate actions
        candidates = self._find_candidates(
            tokens, const_helper, head_chain,
            min_confidence=min_confidence,
            allow_structural=allow_structural,
            allow_deletions=allow_deletions,
            allow_feature_changes=allow_feature_changes,
            allow_form_changes=allow_form_changes,
            rule_sample_seed=rule_sample_seed,
            rule_sample_frac=rule_sample_frac,
        )

        # Phase 2: Resolve conflicts
        planned = self.resolver.resolve(candidates)
        skipped = [c for c in candidates if c not in planned]

        # Phase 3: Apply actions in tier order
        tokens = self._apply_feature_changes(tokens, planned)
        tokens = self._apply_deletions(tokens, planned)
        tokens = self._apply_structural_changes(tokens, planned, const_helper)

        # Post-deletion sanity check: ensure at least one verb/noun remains
        tokens = self._post_deletion_sanity(tokens, conllu_tokens)

        # Phase 4: Realize surface text
        text = self.realizer.realize(tokens)

        return TransformedSentence(
            source_tokens=conllu_tokens,
            transformed_tokens=tokens,
            generated_text=text,
            applied_actions=planned,
            skipped_actions=skipped,
            conflict_count=len(self.resolver.conflicts),
            hypothesis_id=hypothesis_id,
        )

    # ------------------------------------------------------------------
    # Head chain protection
    # ------------------------------------------------------------------

    @staticmethod
    def _build_head_chain(tokens: List[Dict]) -> Set[int]:
        """
        Build the set of token indices forming the head chain:
        root + its nsubj + its obj.

        These tokens should never be deleted or reordered.
        """
        chain = set()
        root_idx = None

        for idx, token in enumerate(tokens):
            deprel = token.get('deprel', '')
            if deprel == 'root':
                root_idx = idx
                chain.add(idx)
                break

        if root_idx is None:
            return chain

        # Find direct dependents of root
        root_id = tokens[root_idx].get('id', root_idx + 1)
        for idx, token in enumerate(tokens):
            head = token.get('head', -1)
            deprel = token.get('deprel', '')
            if head == root_id and deprel in CORE_DEPRELS:
                chain.add(idx)

        return chain

    # ------------------------------------------------------------------
    # Phase 1: Find candidate rule applications
    # ------------------------------------------------------------------

    def _find_candidates(self, tokens: List[Dict],
                         const_helper: ConstituencyHelper,
                         head_chain: Set[int],
                         min_confidence: float = MIN_APPLY_CONFIDENCE,
                         allow_structural: bool = True,
                         allow_deletions: bool = True,
                         allow_feature_changes: bool = True,
                         allow_form_changes: bool = True,
                         rule_sample_seed: Optional[int] = None,
                         rule_sample_frac: float = 1.0) -> List[PlannedAction]:
        """
        Scan tokens and find applicable rules with constituency-aware
        filtering and head chain protection.
        """
        candidates = []
        deletion_candidates = []
        n_tokens = len(tokens)

        # Optionally sample rules
        feature_rules = self.ruleset.feature_rules
        form_rules = self.ruleset.form_rules
        deletion_rules = self.ruleset.deletion_rules
        structural_rules = self.ruleset.structural_rules

        if rule_sample_seed is not None and rule_sample_frac < 1.0:
            import random
            rng = random.Random(rule_sample_seed)
            feature_rules = [r for r in feature_rules if rng.random() < rule_sample_frac]
            form_rules = [r for r in form_rules if rng.random() < rule_sample_frac]
            deletion_rules = [r for r in deletion_rules if rng.random() < rule_sample_frac]
            structural_rules = [r for r in structural_rules if rng.random() < rule_sample_frac]

        for idx, token in enumerate(tokens):
            deprel = token.get('deprel', '')
            form = token.get('form', '')

            # --- Feature rules (FEAT-CHG, DEP-REL-CHG) ---
            if allow_feature_changes:
                for rule in feature_rules:
                    if rule.confidence < min_confidence:
                        continue
                    if rule.feature_id == 'FEAT-CHG':
                        action = self._match_feat_chg(idx, token, rule)
                        if action:
                            candidates.append(action)
                    elif rule.feature_id == 'DEP-REL-CHG':
                        if rule.confidence >= 0.7:
                            action = self._match_deprel_chg(idx, token, rule)
                            if action:
                                candidates.append(action)

            # --- Form rules (FORM-CHG) — with context check ---
            if allow_form_changes:
                for rule in form_rules:
                    if rule.confidence < min_confidence:
                        continue
                    if form.lower() == rule.source_form.lower():
                        # Context check: for verb form changes, verify
                        # subject number agreement if possible
                        if self._form_rule_context_ok(idx, tokens, rule):
                            candidates.append(PlannedAction(
                                action_type='modify_form',
                                token_index=idx,
                                feature_id='FORM-CHG',
                                rule_id=rule.rule_id,
                                priority=FEATURE_PRIORITY.get('FORM-CHG', 20),
                                confidence=rule.confidence,
                                details={
                                    'old_form': form,
                                    'new_form': rule.target_form,
                                }
                            ))
                            break  # Only first matching form rule per token

            # --- Deletion rules (with constituency + head chain filtering) ---
            if allow_deletions:
                for rule in deletion_rules:
                    if rule.action != 'delete':
                        continue
                    if rule.confidence < min_confidence:
                        continue

                    # Protect head chain tokens
                    if idx in head_chain:
                        continue

                    # Protect core deprels
                    if deprel in CORE_DEPRELS:
                        continue

                    # Constituency-aware filtering: prefer deleting from
                    # peripheral constituents
                    confidence_adj = rule.confidence
                    if const_helper.available:
                        if const_helper.is_in_subject_np(idx):
                            continue  # Never delete from subject NP
                        if not const_helper.is_in_peripheral_constituent(idx):
                            confidence_adj *= 0.5  # Downgrade non-peripheral

                    # Downgrade wildcard deprel rules
                    if rule.deprel_pattern == '*':
                        confidence_adj *= 0.5

                    action = self._match_deletion(idx, token, rule,
                                                  confidence_override=confidence_adj)
                    if action:
                        deletion_candidates.append(action)
                        break  # At most one deletion rule per token

        # --- Rate-limit deletions ---
        max_deletions = max(1, int(n_tokens * MAX_DELETION_FRACTION))
        deletion_candidates.sort(key=lambda a: -a.confidence)
        kept_deletions = deletion_candidates[:max_deletions]
        candidates.extend(kept_deletions)

        # --- Structural rules (constituency-aware) ---
        if allow_structural:
            struct_candidates = []
            for rule in structural_rules:
                if rule.confidence < min_confidence:
                    continue
                actions = self._match_structural(tokens, rule, const_helper)
                struct_candidates.extend(actions)
            if struct_candidates:
                struct_candidates.sort(key=lambda a: -a.confidence)
                candidates.append(struct_candidates[0])

        return candidates

    # ------------------------------------------------------------------
    # Rule matching helpers
    # ------------------------------------------------------------------

    def _match_feat_chg(self, idx: int, token: Dict,
                        rule: FeatureRule) -> Optional[PlannedAction]:
        """Check if a FEAT-CHG rule matches this token's morphological features."""
        feats = token.get('feats') or {}
        src = rule.source_value
        tgt = rule.target_value

        if '=' in src:
            feat_name, feat_val = src.split('=', 1)
            if feats.get(feat_name) == feat_val:
                new_val = tgt.split('=', 1)[-1] if '=' in tgt else tgt
                return PlannedAction(
                    action_type='modify_feats',
                    token_index=idx,
                    feature_id='FEAT-CHG',
                    rule_id=rule.rule_id,
                    priority=FEATURE_PRIORITY.get('FEAT-CHG', 10),
                    confidence=rule.confidence,
                    details={
                        'feat_name': feat_name,
                        'old_value': feat_val,
                        'new_value': new_val,
                    }
                )
        else:
            for feat_name, feat_val in feats.items():
                if feat_val == src:
                    return PlannedAction(
                        action_type='modify_feats',
                        token_index=idx,
                        feature_id='FEAT-CHG',
                        rule_id=rule.rule_id,
                        priority=FEATURE_PRIORITY.get('FEAT-CHG', 10),
                        confidence=rule.confidence,
                        details={
                            'feat_name': feat_name,
                            'old_value': feat_val,
                            'new_value': tgt,
                        }
                    )
        return None

    def _match_deprel_chg(self, idx: int, token: Dict,
                          rule: FeatureRule) -> Optional[PlannedAction]:
        """Check if a DEP-REL-CHG rule matches this token's deprel."""
        deprel = token.get('deprel', '')
        if deprel == rule.source_value:
            return PlannedAction(
                action_type='modify_deprel',
                token_index=idx,
                feature_id='DEP-REL-CHG',
                rule_id=rule.rule_id,
                priority=FEATURE_PRIORITY.get('DEP-REL-CHG', 30),
                confidence=rule.confidence,
                details={
                    'old_deprel': deprel,
                    'new_deprel': rule.target_value,
                }
            )
        return None

    def _match_deletion(self, idx: int, token: Dict,
                        rule: DeletionRule,
                        confidence_override: Optional[float] = None
                        ) -> Optional[PlannedAction]:
        """Check if a deletion rule matches this token."""
        upos = token.get('upos', '') or token.get('upostag', '')
        deprel = token.get('deprel', '')

        pos_ok = rule.pos_pattern == '*' or rule.pos_pattern == upos
        deprel_ok = rule.deprel_pattern == '*' or rule.deprel_pattern == deprel
        lemma_ok = (rule.lemma_pattern == '*' or
                    rule.lemma_pattern == (token.get('lemma', '') or '').lower())

        if pos_ok and deprel_ok and lemma_ok:
            conf = confidence_override if confidence_override is not None else rule.confidence
            return PlannedAction(
                action_type='delete_token',
                token_index=idx,
                feature_id=rule.feature_id,
                rule_id=rule.rule_id,
                priority=FEATURE_PRIORITY.get(rule.feature_id, 50),
                confidence=conf,
                details={
                    'token_category': rule.token_category,
                    'form': token.get('form', ''),
                }
            )
        return None

    def _match_structural(self, tokens: List[Dict],
                          rule: StructuralRule,
                          const_helper: ConstituencyHelper
                          ) -> List[PlannedAction]:
        """Check if a structural rule matches, using constituency info."""
        actions = []
        pattern = rule.pattern

        if rule.feature_id == 'CLAUSE-TYPE-CHG':
            src_type = pattern.split('\u2192')[0] if '\u2192' in pattern else pattern
            tgt_type = pattern.split('\u2192')[1] if '\u2192' in pattern else pattern

            for idx, token in enumerate(tokens):
                upos = token.get('upos', '') or token.get('upostag', '')
                feats = token.get('feats') or {}
                if upos in ('VERB', 'AUX') and feats.get('VerbForm') == src_type:
                    actions.append(PlannedAction(
                        action_type='change_clause_type',
                        token_index=idx,
                        feature_id='CLAUSE-TYPE-CHG',
                        rule_id=rule.rule_id,
                        priority=FEATURE_PRIORITY.get('CLAUSE-TYPE-CHG', 60),
                        confidence=rule.confidence,
                        details={'old_type': src_type, 'new_type': tgt_type}
                    ))
                    break

        elif rule.feature_id == 'CONST-REM':
            # Only apply if we can identify the constituent via tree
            if const_helper.available or 'SBAR' in pattern:
                actions.append(PlannedAction(
                    action_type='remove_constituent',
                    token_index=-1,
                    feature_id='CONST-REM',
                    rule_id=rule.rule_id,
                    priority=FEATURE_PRIORITY.get('CONST-REM', 70),
                    confidence=rule.confidence,
                    details={'pattern': pattern}
                ))

        elif rule.feature_id == 'CONST-MOV':
            # Only apply movement if constituency tree can identify
            # a clear reporting clause pattern
            if const_helper.available:
                reporting = const_helper.get_reporting_clause_pattern()
                if reporting:
                    actions.append(PlannedAction(
                        action_type='move_constituent',
                        token_index=-1,
                        feature_id='CONST-MOV',
                        rule_id=rule.rule_id,
                        priority=FEATURE_PRIORITY.get('CONST-MOV', 80),
                        confidence=rule.confidence,
                        details={
                            'pattern': pattern,
                            'reporting': reporting,
                        }
                    ))
            # If no constituency tree or no reporting pattern, skip entirely
            # (instead of blindly fronting the verb)

        return actions

    def _form_rule_context_ok(self, idx: int, tokens: List[Dict],
                              rule: FormRule) -> bool:
        """
        Check whether a form rule should fire given surrounding context.

        For verb form changes (e.g. has->have), verify the subject's
        Number feature is compatible.
        """
        upos = tokens[idx].get('upos', '') or tokens[idx].get('upostag', '')
        if upos not in ('VERB', 'AUX'):
            return True  # Non-verb form rules: always OK

        # Find the subject of this token's clause
        head_id = tokens[idx].get('id', idx + 1)
        for tok in tokens:
            if tok.get('head') == head_id and tok.get('deprel', '') in ('nsubj', 'nsubj:pass'):
                subj_feats = tok.get('feats') or {}
                subj_number = subj_feats.get('Number', '')

                # has->have should only fire if subject is Plur
                src_lower = rule.source_form.lower()
                tgt_lower = rule.target_form.lower()

                # Singular -> plural verb forms
                if (src_lower, tgt_lower) in {('has', 'have'), ('is', 'are'),
                                               ('was', 'were'), ('does', 'do')}:
                    return subj_number == 'Plur'
                # Plural -> singular verb forms
                if (src_lower, tgt_lower) in {('have', 'has'), ('are', 'is'),
                                               ('were', 'was'), ('do', 'does')}:
                    return subj_number == 'Sing'
                break

        return True  # If we can't determine, allow it

    # ------------------------------------------------------------------
    # Phase 3: Apply planned actions
    # ------------------------------------------------------------------

    def _apply_feature_changes(self, tokens: List[Dict],
                               planned: List[PlannedAction]) -> List[Dict]:
        """
        Apply Tier 1 modifications (feats, deprel, upos, form).

        Bug fix: Merge multiple feature changes on the same token before
        clearing the form for re-inflection (prevents auxiliary doubling).
        """
        # Group feature changes by token index to merge them
        feat_changes_by_token: Dict[int, List[PlannedAction]] = defaultdict(list)
        other_actions = []

        for action in planned:
            if action.action_type == 'modify_feats':
                feat_changes_by_token[action.token_index].append(action)
            else:
                other_actions.append(action)

        # Apply merged feature changes
        for idx, feat_actions in feat_changes_by_token.items():
            if idx < 0 or idx >= len(tokens):
                continue
            feats = tokens[idx].get('feats') or {}
            for action in feat_actions:
                feat_name = action.details.get('feat_name', '')
                new_value = action.details.get('new_value', '')
                if new_value and new_value != 'ABSENT':
                    feats[feat_name] = new_value
                elif feat_name in feats:
                    del feats[feat_name]
            tokens[idx]['feats'] = feats
            # Clear form ONCE so realizer will re-inflect from lemma+feats
            tokens[idx]['form'] = ''

        # Apply other actions
        for action in other_actions:
            idx = action.token_index
            if idx < 0 or idx >= len(tokens):
                continue

            if action.action_type == 'modify_deprel':
                tokens[idx]['deprel'] = action.details.get('new_deprel', '')

            elif action.action_type == 'modify_upos':
                new_upos = action.details.get('new_upos', '')
                if 'upos' in tokens[idx]:
                    tokens[idx]['upos'] = new_upos
                if 'upostag' in tokens[idx]:
                    tokens[idx]['upostag'] = new_upos

            elif action.action_type == 'modify_form':
                tokens[idx]['form'] = action.details.get('new_form', '')

            elif action.action_type == 'change_clause_type':
                feats = tokens[idx].get('feats') or {}
                new_type = action.details.get('new_type', '')
                if new_type and new_type != 'ABSENT':
                    feats['VerbForm'] = new_type
                tokens[idx]['feats'] = feats
                tokens[idx]['form'] = ''

        return tokens

    def _apply_deletions(self, tokens: List[Dict],
                         planned: List[PlannedAction]) -> List[Dict]:
        """Apply Tier 2 deletions (remove tokens marked for deletion)."""
        delete_indices = set()
        for action in planned:
            if action.action_type == 'delete_token' and action.token_index >= 0:
                delete_indices.add(action.token_index)

        if not delete_indices:
            return tokens

        return [t for i, t in enumerate(tokens) if i not in delete_indices]

    def _apply_structural_changes(self, tokens: List[Dict],
                                  planned: List[PlannedAction],
                                  const_helper: ConstituencyHelper
                                  ) -> List[Dict]:
        """Apply Tier 3 structural changes (constituency-aware)."""
        for action in planned:
            if action.action_type == 'remove_constituent':
                pattern = action.details.get('pattern', '')
                tokens = self._heuristic_remove_constituent(tokens, pattern)
            elif action.action_type == 'move_constituent':
                reporting = action.details.get('reporting')
                if reporting:
                    tokens = self._constituency_move(tokens, reporting)
                # No blind verb-fronting fallback

        return tokens

    def _heuristic_remove_constituent(self, tokens: List[Dict],
                                      pattern: str) -> List[Dict]:
        """Heuristic: remove SBAR-like clauses by finding SCONJ + clause."""
        if 'SBAR' in pattern:
            for i, t in enumerate(tokens):
                upos = t.get('upos', '') or t.get('upostag', '')
                if upos == 'SCONJ':
                    end = i + 1
                    while end < len(tokens):
                        u = tokens[end].get('upos', '') or tokens[end].get('upostag', '')
                        if u == 'PUNCT':
                            break
                        end += 1
                    return tokens[:i] + tokens[end:]
        return tokens

    def _constituency_move(self, tokens: List[Dict],
                           reporting: Dict) -> List[Dict]:
        """
        Constituency-informed movement for reporting clauses.

        For C2R direction: Extract the reported clause content from SBAR,
        place it before the reporting clause attribution.
        """
        sbar_start = reporting.get('sbar_start', -1)
        sbar_end = reporting.get('sbar_end', -1)

        if sbar_start < 0 or sbar_end < 0 or sbar_start >= len(tokens):
            return tokens

        # Clamp to actual token count
        sbar_end = min(sbar_end, len(tokens))

        # Find the start of actual content in SBAR (skip subordinating conj)
        content_start = sbar_start
        for i in range(sbar_start, min(sbar_end, len(tokens))):
            upos = tokens[i].get('upos', '') or tokens[i].get('upostag', '')
            if upos in ('SCONJ', 'IN') or tokens[i].get('deprel', '') == 'mark':
                content_start = i + 1
            else:
                break

        if content_start >= sbar_end:
            return tokens

        # Build: reported_content + ", " + attribution (before SBAR)
        attribution = tokens[:sbar_start]
        reported = tokens[content_start:sbar_end]
        remaining = tokens[sbar_end:]

        return reported + attribution + remaining

    # ------------------------------------------------------------------
    # Post-processing
    # ------------------------------------------------------------------

    def _post_deletion_sanity(self, tokens: List[Dict],
                              original_tokens: List[Dict]) -> List[Dict]:
        """
        After deletions, verify that the result isn't catastrophically
        damaged. If no verb/aux or no noun/propn remains, fall back to
        the original tokens.
        """
        if not tokens:
            return [copy.deepcopy(t) for t in original_tokens]

        has_verb = any(
            (t.get('upos', '') or t.get('upostag', '')) in ('VERB', 'AUX')
            for t in tokens
        )
        has_noun = any(
            (t.get('upos', '') or t.get('upostag', '')) in ('NOUN', 'PROPN', 'PRON')
            for t in tokens
        )

        if not has_verb and not has_noun:
            return [copy.deepcopy(t) for t in original_tokens]

        return tokens

    # ------------------------------------------------------------------
    # Batch processing
    # ------------------------------------------------------------------

    def transform_corpus(self, sentence_pairs: List[Tuple[List[Dict], List[Dict]]],
                         direction: str,
                         const_trees: Optional[List[str]] = None
                         ) -> List[TransformedSentence]:
        """Transform a corpus of sentence pairs."""
        results = []
        for i, (can_tokens, hl_tokens) in enumerate(sentence_pairs):
            source = can_tokens if direction == 'C2R' else hl_tokens
            tree = const_trees[i] if const_trees and i < len(const_trees) else None
            result = self.transform(source, const_tree_str=tree)
            results.append(result)

            if (i + 1) % 50 == 0:
                print(f"    Transformed {i + 1}/{len(sentence_pairs)} sentences")

        print(f"    Completed {len(results)} transformations")
        return results
