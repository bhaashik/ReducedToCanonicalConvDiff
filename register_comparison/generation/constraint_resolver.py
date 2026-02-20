"""
Constraint Resolver: Priority-based conflict resolution for transformation rules.

When multiple rules target the same token, the resolver decides which to apply.
Lower priority numbers execute first (morphological before structural).
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


# Priority: lower number = higher priority (applied first, wins conflicts)
FEATURE_PRIORITY = {
    'FEAT-CHG': 10,
    'FORM-CHG': 20,
    'POS-CHG': 25,
    'DEP-REL-CHG': 30,
    'FW-DEL': 40,
    'FW-ADD': 45,
    'C-DEL': 50,
    'C-ADD': 55,
    'CLAUSE-TYPE-CHG': 60,
    'CONST-REM': 70,
    'CONST-MOV': 80,
}


@dataclass
class PlannedAction:
    """A concrete action to perform on a token or the token list."""
    action_type: str        # 'modify_feats', 'modify_form', 'modify_deprel',
                            # 'modify_upos', 'delete_token', 'insert_token',
                            # 'move_constituent', 'remove_constituent',
                            # 'change_clause_type'
    token_index: int        # Index in the token list (-1 for structural)
    feature_id: str         # Which schema feature produced this
    rule_id: str            # ID of the rule
    priority: int           # From FEATURE_PRIORITY
    confidence: float
    details: Dict[str, Any] = field(default_factory=dict)
    # details keys vary by action_type:
    #   modify_feats: {feat_name, old_value, new_value}
    #   modify_form: {old_form, new_form}
    #   modify_deprel: {old_deprel, new_deprel}
    #   modify_upos: {old_upos, new_upos}
    #   delete_token: {}
    #   insert_token: {form, lemma, upos, deprel, position}
    #   move_constituent: {pattern}
    #   remove_constituent: {pattern}
    #   change_clause_type: {old_type, new_type}


@dataclass
class ConflictRecord:
    """Records a detected conflict and how it was resolved."""
    token_index: int
    competing_actions: List[PlannedAction]
    winner: PlannedAction
    reason: str


class ConstraintResolver:
    """
    Resolves conflicts when multiple rules target the same token.

    Resolution strategy:
    1. Group actions by token_index
    2. Within each group, sort by priority (lower = higher priority)
    3. For conflicting action types on the same token, keep the
       highest-priority (lowest number) action
    4. Non-conflicting actions on the same token can coexist
       (e.g., modify_feats + modify_deprel)
    """

    # Action types that conflict with each other on the same token
    CONFLICT_GROUPS = [
        {'delete_token', 'modify_form', 'modify_feats', 'modify_deprel',
         'modify_upos', 'change_clause_type'},
    ]

    def __init__(self):
        self.conflicts: List[ConflictRecord] = []

    def resolve(self, candidates: List[PlannedAction]) -> List[PlannedAction]:
        """
        Resolve conflicts among candidate actions.

        Returns a list of non-conflicting PlannedActions to execute.
        """
        self.conflicts = []

        if not candidates:
            return []

        # Group by token_index
        by_token: Dict[int, List[PlannedAction]] = defaultdict(list)
        structural_actions = []

        for action in candidates:
            if action.token_index < 0:
                structural_actions.append(action)
            else:
                by_token[action.token_index].append(action)

        resolved = []

        # Resolve per-token conflicts
        for token_idx, actions in by_token.items():
            token_resolved = self._resolve_token_conflicts(token_idx, actions)
            resolved.extend(token_resolved)

        # Structural actions: delete wins over move on the same constituent
        resolved.extend(self._resolve_structural_conflicts(structural_actions))

        # Sort final list by priority (execute in order)
        resolved.sort(key=lambda a: a.priority)
        return resolved

    def _resolve_token_conflicts(self, token_idx: int,
                                 actions: List[PlannedAction]) -> List[PlannedAction]:
        """Resolve conflicts for actions targeting the same token."""
        if len(actions) <= 1:
            return actions

        # Sort by priority (lower = more important)
        actions.sort(key=lambda a: (a.priority, -a.confidence))

        # If any action is delete_token, it conflicts with everything else
        deletes = [a for a in actions if a.action_type == 'delete_token']
        if deletes:
            winner = deletes[0]  # highest priority delete
            others = [a for a in actions if a is not winner]
            if others:
                self.conflicts.append(ConflictRecord(
                    token_index=token_idx,
                    competing_actions=actions,
                    winner=winner,
                    reason="delete_token preempts all other actions"
                ))
            return [winner]

        # Otherwise, allow non-conflicting action types to coexist
        # e.g., modify_feats and modify_deprel can both apply
        seen_types = set()
        kept = []
        dropped = []

        for action in actions:
            if action.action_type not in seen_types:
                seen_types.add(action.action_type)
                kept.append(action)
            else:
                dropped.append(action)

        if dropped:
            self.conflicts.append(ConflictRecord(
                token_index=token_idx,
                competing_actions=actions,
                winner=kept[0],
                reason=f"kept {len(kept)} non-conflicting, dropped {len(dropped)} duplicates"
            ))

        return kept

    def _resolve_structural_conflicts(self,
                                      actions: List[PlannedAction]) -> List[PlannedAction]:
        """Resolve conflicts among structural (non-token-specific) actions."""
        if len(actions) <= 1:
            return actions

        # For structural actions, just sort by priority
        actions.sort(key=lambda a: (a.priority, -a.confidence))
        return actions

    def get_conflict_statistics(self) -> Dict[str, Any]:
        """Return statistics about resolved conflicts."""
        if not self.conflicts:
            return {'total_conflicts': 0}

        by_reason = defaultdict(int)
        by_feature = defaultdict(int)
        for c in self.conflicts:
            by_reason[c.reason] += 1
            by_feature[c.winner.feature_id] += 1

        return {
            'total_conflicts': len(self.conflicts),
            'by_reason': dict(by_reason),
            'by_winning_feature': dict(by_feature),
        }
