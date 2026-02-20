"""
Bidirectional Rule Extractor: Extracts transformation rules in both
canonical→reduced (C→R) and reduced→canonical (R→C) directions from
events data.

Rules are extracted at three tiers:
  Tier 1 (Feature-level): FEAT-CHG, FORM-CHG, DEP-REL-CHG, POS-CHG
  Tier 2 (Token-level): FW-DEL/FW-ADD, C-DEL/C-ADD
  Tier 3 (Structural): CONST-MOV, CONST-REM, CLAUSE-TYPE-CHG
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, Counter

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


# ---------------------------------------------------------------------------
# Data classes for different rule types
# ---------------------------------------------------------------------------

@dataclass
class FeatureRule:
    """Tier 1: Modifies a CoNLL-U column for an aligned token."""
    rule_id: str
    direction: str          # 'C2R' or 'R2C'
    feature_id: str         # e.g. FEAT-CHG, FORM-CHG, DEP-REL-CHG
    source_value: str       # value in the source register
    target_value: str       # value in the target register
    pos_pattern: str        # UPOS that this rule applies to (or '*')
    confidence: float
    frequency: int
    conditions: Dict[str, Any] = field(default_factory=dict)

    @property
    def tier(self) -> int:
        return 1

    def matches(self, token_upos: str, token_value: str) -> bool:
        pos_ok = self.pos_pattern == '*' or self.pos_pattern == token_upos
        val_ok = self.source_value == token_value or self.source_value == '*'
        return pos_ok and val_ok


@dataclass
class DeletionRule:
    """Tier 2: Deletes or inserts a token."""
    rule_id: str
    direction: str
    feature_id: str         # FW-DEL, FW-ADD, C-DEL, C-ADD
    action: str             # 'delete' or 'insert'
    token_category: str     # e.g. ART-DEL, AUX-DEL, SCONJ-DEL
    pos_pattern: str        # POS of the token to delete/insert
    deprel_pattern: str     # deprel of the token (or '*')
    lemma_pattern: str      # specific lemma (or '*')
    confidence: float
    frequency: int
    conditions: Dict[str, Any] = field(default_factory=dict)

    @property
    def tier(self) -> int:
        return 2


@dataclass
class FormRule:
    """Tier 1 variant: Changes the surface form of a token."""
    rule_id: str
    direction: str
    source_form: str
    target_form: str
    pos_pattern: str
    lemma: str
    confidence: float
    frequency: int

    @property
    def tier(self) -> int:
        return 1


@dataclass
class StructuralRule:
    """Tier 3: Reorders or removes constituents."""
    rule_id: str
    direction: str
    feature_id: str         # CONST-MOV, CONST-REM, CLAUSE-TYPE-CHG
    pattern: str            # e.g. CONST-FRONT, SBAR-REM, Fin→Inf
    confidence: float
    frequency: int
    conditions: Dict[str, Any] = field(default_factory=dict)

    @property
    def tier(self) -> int:
        return 3


@dataclass
class RuleSet:
    """A complete set of rules for one direction."""
    direction: str
    feature_rules: List[FeatureRule] = field(default_factory=list)
    deletion_rules: List[DeletionRule] = field(default_factory=list)
    form_rules: List[FormRule] = field(default_factory=list)
    structural_rules: List[StructuralRule] = field(default_factory=list)

    @property
    def total_rules(self) -> int:
        return (len(self.feature_rules) + len(self.deletion_rules)
                + len(self.form_rules) + len(self.structural_rules))

    def all_rules(self):
        return (self.feature_rules + self.deletion_rules
                + self.form_rules + self.structural_rules)

    def get_statistics(self) -> Dict[str, Any]:
        return {
            'direction': self.direction,
            'total_rules': self.total_rules,
            'feature_rules': len(self.feature_rules),
            'deletion_rules': len(self.deletion_rules),
            'form_rules': len(self.form_rules),
            'structural_rules': len(self.structural_rules),
            'by_feature_id': self._count_by_feature_id(),
            'avg_confidence': self._avg_confidence(),
        }

    def _count_by_feature_id(self) -> Dict[str, int]:
        counts: Dict[str, int] = defaultdict(int)
        for r in self.feature_rules:
            counts[r.feature_id] += 1
        for r in self.deletion_rules:
            counts[r.feature_id] += 1
        for r in self.form_rules:
            counts['FORM-CHG'] += 1
        for r in self.structural_rules:
            counts[r.feature_id] += 1
        return dict(counts)

    def _avg_confidence(self) -> float:
        all_r = self.all_rules()
        if not all_r:
            return 0.0
        return sum(r.confidence for r in all_r) / len(all_r)


# ---------------------------------------------------------------------------
# Actionable features (the rest are aggregate measures, not rule-able)
# ---------------------------------------------------------------------------

ACTIONABLE_FEATURES = {
    'FEAT-CHG', 'DEP-REL-CHG', 'FW-DEL', 'FW-ADD', 'C-DEL', 'C-ADD',
    'FORM-CHG', 'CLAUSE-TYPE-CHG', 'CONST-MOV', 'CONST-REM', 'POS-CHG',
}

# Map canonical_value patterns to POS/deprel for deletion rules
DELETION_VALUE_TO_POS = {
    # Function word deletions
    'ART-DEL': ('DET', 'det'),
    'AUX-DEL': ('AUX', 'aux'),
    'SCONJ-DEL': ('SCONJ', 'mark'),
    'PREP-DEL': ('ADP', 'case'),
    'CCONJ-DEL': ('CCONJ', 'cc'),
    'PRON-DEL': ('PRON', '*'),
    'DET-DEL': ('DET', 'det'),
    'PART-DEL': ('PART', 'mark'),
    # Content word deletions
    'NOUN-DEL': ('NOUN', '*'),
    'VERB-DEL': ('VERB', '*'),
    'ADJ-DEL': ('ADJ', '*'),
    'ADV-DEL': ('ADV', '*'),
    'PROPN-DEL': ('PROPN', '*'),
    'NUM-DEL': ('NUM', '*'),
    # Function word additions (reverse direction — insert with these POS)
    'ART-ADD': ('DET', 'det'),
    'AUX-ADD': ('AUX', 'aux'),
    'SCONJ-ADD': ('SCONJ', 'mark'),
    'PREP-ADD': ('ADP', 'case'),
    'CCONJ-ADD': ('CCONJ', 'cc'),
    'PRON-ADD': ('PRON', '*'),
    'DET-ADD': ('DET', 'det'),
    'PART-ADD': ('PART', 'mark'),
    # Content word additions
    'NOUN-ADD': ('NOUN', '*'),
    'VERB-ADD': ('VERB', '*'),
    'ADJ-ADD': ('ADJ', '*'),
    'ADV-ADD': ('ADV', '*'),
    'ADP-ADD': ('ADP', 'case'),
    'PROPN-ADD': ('PROPN', '*'),
    'NUM-ADD': ('NUM', '*'),
    # Punctuation
    'PUNCT-DEL': ('PUNCT', 'punct'),
    'PUNCT-ADD': ('PUNCT', 'punct'),
}


class BidirectionalRuleExtractor:
    """
    Extract transformation rules from events CSVs in both C→R and R→C
    directions.

    The events CSV has columns:
        newspaper, sentence_id, parse_type, feature_id, feature_name,
        mnemonic, canonical_value, headline_value, canonical_context,
        headline_context, ...

    For C→R direction: source=canonical_value, target=headline_value
    For R→C direction: source=headline_value, target=canonical_value
    """

    def __init__(self, min_frequency: int = 2, min_confidence: float = 0.3):
        self.min_frequency = min_frequency
        self.min_confidence = min_confidence
        self._rule_counter = 0

    def _next_id(self, prefix: str) -> str:
        self._rule_counter += 1
        return f"{prefix}_{self._rule_counter:04d}"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_from_events(self, events_csv: Path,
                            direction: str) -> RuleSet:
        """
        Extract a complete RuleSet from an events CSV file.

        Args:
            events_csv: Path to events_global.csv
            direction: 'C2R' or 'R2C'
        """
        events = self._load_events(events_csv)
        actionable = [e for e in events
                      if e['feature_id'] in ACTIONABLE_FEATURES]

        print(f"  [{direction}] Loaded {len(events)} total events, "
              f"{len(actionable)} actionable")

        ruleset = RuleSet(direction=direction)
        ruleset.feature_rules = self._extract_feature_rules(actionable, direction)
        ruleset.deletion_rules = self._extract_deletion_rules(actionable, direction)
        ruleset.form_rules = self._extract_form_rules(actionable, direction)
        ruleset.structural_rules = self._extract_structural_rules(actionable, direction)

        print(f"  [{direction}] Extracted {ruleset.total_rules} rules "
              f"(feat={len(ruleset.feature_rules)}, "
              f"del={len(ruleset.deletion_rules)}, "
              f"form={len(ruleset.form_rules)}, "
              f"struct={len(ruleset.structural_rules)})")

        return ruleset

    def extract_both_directions(self, events_csv: Path) -> Tuple[RuleSet, RuleSet]:
        """Extract rules for both C→R and R→C directions."""
        c2r = self.extract_from_events(events_csv, 'C2R')
        r2c = self.extract_from_events(events_csv, 'R2C')
        return c2r, r2c

    # ------------------------------------------------------------------
    # Events loading
    # ------------------------------------------------------------------

    def _load_events(self, csv_path: Path) -> List[Dict[str, str]]:
        events = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                events.append(dict(row))
        return events

    # ------------------------------------------------------------------
    # Source / target value helpers
    # ------------------------------------------------------------------

    def _source_value(self, event: Dict, direction: str) -> str:
        if direction == 'C2R':
            return event.get('canonical_value', '')
        else:
            return event.get('headline_value', '')

    def _target_value(self, event: Dict, direction: str) -> str:
        if direction == 'C2R':
            return event.get('headline_value', '')
        else:
            return event.get('canonical_value', '')

    # ------------------------------------------------------------------
    # Tier 1: Feature-level rules (FEAT-CHG, DEP-REL-CHG, POS-CHG)
    # ------------------------------------------------------------------

    def _extract_feature_rules(self, events: List[Dict],
                               direction: str) -> List[FeatureRule]:
        feature_ids = {'FEAT-CHG', 'DEP-REL-CHG', 'POS-CHG'}
        relevant = [e for e in events if e['feature_id'] in feature_ids]

        # Group by (feature_id, source_value, target_value) to get frequency
        pattern_counts: Dict[Tuple[str, str, str], int] = Counter()
        for e in relevant:
            src = self._source_value(e, direction)
            tgt = self._target_value(e, direction)
            if src and tgt and src != 'ABSENT' and tgt != 'ABSENT':
                pattern_counts[(e['feature_id'], src, tgt)] += 1

        # Compute confidence: for each (feature_id, source_value), what
        # fraction of the time does it map to this target_value?
        source_totals: Dict[Tuple[str, str], int] = Counter()
        for (fid, src, _), count in pattern_counts.items():
            source_totals[(fid, src)] += count

        rules = []
        for (fid, src, tgt), freq in pattern_counts.items():
            if freq < self.min_frequency:
                continue
            conf = freq / source_totals[(fid, src)]
            if conf < self.min_confidence:
                continue
            rules.append(FeatureRule(
                rule_id=self._next_id(f"FEAT_{direction}"),
                direction=direction,
                feature_id=fid,
                source_value=src,
                target_value=tgt,
                pos_pattern='*',
                confidence=conf,
                frequency=freq,
            ))

        rules.sort(key=lambda r: (-r.confidence, -r.frequency))
        return rules

    # ------------------------------------------------------------------
    # Tier 2: Deletion / insertion rules
    # ------------------------------------------------------------------

    def _extract_deletion_rules(self, events: List[Dict],
                                direction: str) -> List[DeletionRule]:
        # For C2R: FW-DEL/C-DEL events → delete action
        #          FW-ADD/C-ADD events → insert action
        # For R2C: FW-DEL/C-DEL events → insert action (reverse)
        #          FW-ADD/C-ADD events → delete action (reverse)

        del_features = {'FW-DEL', 'C-DEL'}
        add_features = {'FW-ADD', 'C-ADD'}

        rules = []

        # Deletion events
        del_events = [e for e in events if e['feature_id'] in del_features]
        add_events = [e for e in events if e['feature_id'] in add_features]

        if direction == 'C2R':
            # canonical_value tells us WHAT was deleted (e.g., ART-DEL)
            rules.extend(self._build_deletion_rules(del_events, direction,
                                                    'delete', 'canonical_value'))
            rules.extend(self._build_deletion_rules(add_events, direction,
                                                    'insert', 'headline_value'))
        else:
            # R2C: deletions in the event become insertions, and vice versa
            rules.extend(self._build_deletion_rules(del_events, direction,
                                                    'insert', 'canonical_value'))
            rules.extend(self._build_deletion_rules(add_events, direction,
                                                    'delete', 'headline_value'))

        rules.sort(key=lambda r: (-r.confidence, -r.frequency))
        return rules

    def _build_deletion_rules(self, events: List[Dict], direction: str,
                              action: str,
                              value_column: str) -> List[DeletionRule]:
        # Count (feature_id, category) patterns
        pattern_counts: Dict[Tuple[str, str], int] = Counter()
        for e in events:
            category = e.get(value_column, '')
            if category and category != 'ABSENT':
                pattern_counts[(e['feature_id'], category)] += 1

        # Confidence = frequency of this category / total events for this feature_id
        feature_totals: Dict[str, int] = Counter()
        for (fid, _), count in pattern_counts.items():
            feature_totals[fid] += count

        rules = []
        for (fid, category), freq in pattern_counts.items():
            if freq < self.min_frequency:
                continue
            conf = freq / feature_totals[fid] if feature_totals[fid] > 0 else 0
            # Look up POS/deprel from the category name
            pos, deprel = DELETION_VALUE_TO_POS.get(category, ('*', '*'))

            rules.append(DeletionRule(
                rule_id=self._next_id(f"DEL_{direction}"),
                direction=direction,
                feature_id=fid,
                action=action,
                token_category=category,
                pos_pattern=pos,
                deprel_pattern=deprel,
                lemma_pattern='*',
                confidence=conf,
                frequency=freq,
            ))

        return rules

    # ------------------------------------------------------------------
    # Tier 1 variant: Form change rules
    # ------------------------------------------------------------------

    def _extract_form_rules(self, events: List[Dict],
                            direction: str) -> List[FormRule]:
        relevant = [e for e in events if e['feature_id'] == 'FORM-CHG']

        pattern_counts: Dict[Tuple[str, str], int] = Counter()
        for e in relevant:
            src = self._source_value(e, direction)
            tgt = self._target_value(e, direction)
            if src and tgt and src != tgt:
                pattern_counts[(src, tgt)] += 1

        source_totals: Dict[str, int] = Counter()
        for (src, _), count in pattern_counts.items():
            source_totals[src] += count

        rules = []
        for (src, tgt), freq in pattern_counts.items():
            if freq < self.min_frequency:
                continue
            conf = freq / source_totals[src]
            if conf < self.min_confidence:
                continue
            rules.append(FormRule(
                rule_id=self._next_id(f"FORM_{direction}"),
                direction=direction,
                source_form=src,
                target_form=tgt,
                pos_pattern='*',
                lemma='*',
                confidence=conf,
                frequency=freq,
            ))

        rules.sort(key=lambda r: (-r.confidence, -r.frequency))
        return rules

    # ------------------------------------------------------------------
    # Tier 3: Structural rules
    # ------------------------------------------------------------------

    def _extract_structural_rules(self, events: List[Dict],
                                  direction: str) -> List[StructuralRule]:
        struct_features = {'CONST-MOV', 'CONST-REM', 'CLAUSE-TYPE-CHG'}
        relevant = [e for e in events if e['feature_id'] in struct_features]

        pattern_counts: Dict[Tuple[str, str], int] = Counter()
        for e in relevant:
            fid = e['feature_id']
            # Build a pattern from both values
            src = self._source_value(e, direction)
            tgt = self._target_value(e, direction)
            if src and tgt:
                pattern = f"{src}→{tgt}" if src != tgt else src
                pattern_counts[(fid, pattern)] += 1

        feature_totals: Dict[str, int] = Counter()
        for (fid, _), count in pattern_counts.items():
            feature_totals[fid] += count

        rules = []
        for (fid, pattern), freq in pattern_counts.items():
            if freq < self.min_frequency:
                continue
            conf = freq / feature_totals[fid] if feature_totals[fid] > 0 else 0
            if conf < self.min_confidence:
                continue
            rules.append(StructuralRule(
                rule_id=self._next_id(f"STRUCT_{direction}"),
                direction=direction,
                feature_id=fid,
                pattern=pattern,
                confidence=conf,
                frequency=freq,
            ))

        rules.sort(key=lambda r: (-r.confidence, -r.frequency))
        return rules

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def save_ruleset(self, ruleset: RuleSet, output_dir: Path):
        """Save a RuleSet to JSON."""
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"rules_{ruleset.direction.lower()}.json"
        path = output_dir / filename

        data = {
            'direction': ruleset.direction,
            'statistics': ruleset.get_statistics(),
            'feature_rules': [
                {
                    'rule_id': r.rule_id, 'direction': r.direction,
                    'feature_id': r.feature_id,
                    'source_value': r.source_value,
                    'target_value': r.target_value,
                    'pos_pattern': r.pos_pattern,
                    'confidence': r.confidence, 'frequency': r.frequency,
                    'conditions': r.conditions,
                }
                for r in ruleset.feature_rules
            ],
            'deletion_rules': [
                {
                    'rule_id': r.rule_id, 'direction': r.direction,
                    'feature_id': r.feature_id, 'action': r.action,
                    'token_category': r.token_category,
                    'pos_pattern': r.pos_pattern,
                    'deprel_pattern': r.deprel_pattern,
                    'lemma_pattern': r.lemma_pattern,
                    'confidence': r.confidence, 'frequency': r.frequency,
                    'conditions': r.conditions,
                }
                for r in ruleset.deletion_rules
            ],
            'form_rules': [
                {
                    'rule_id': r.rule_id, 'direction': r.direction,
                    'source_form': r.source_form,
                    'target_form': r.target_form,
                    'pos_pattern': r.pos_pattern,
                    'lemma': r.lemma,
                    'confidence': r.confidence, 'frequency': r.frequency,
                }
                for r in ruleset.form_rules
            ],
            'structural_rules': [
                {
                    'rule_id': r.rule_id, 'direction': r.direction,
                    'feature_id': r.feature_id, 'pattern': r.pattern,
                    'confidence': r.confidence, 'frequency': r.frequency,
                    'conditions': r.conditions,
                }
                for r in ruleset.structural_rules
            ],
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  Saved {ruleset.total_rules} rules to {path}")

    def save_ruleset_csv(self, ruleset: RuleSet, output_dir: Path):
        """Save a RuleSet inventory as CSV (for tables)."""
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"rule_inventory_{ruleset.direction.lower()}.csv"
        path = output_dir / filename

        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'rule_id', 'direction', 'tier', 'feature_id',
                'source_value', 'target_value', 'pos_pattern',
                'confidence', 'frequency'
            ])

            for r in ruleset.feature_rules:
                writer.writerow([
                    r.rule_id, r.direction, r.tier, r.feature_id,
                    r.source_value, r.target_value, r.pos_pattern,
                    f"{r.confidence:.4f}", r.frequency
                ])
            for r in ruleset.deletion_rules:
                writer.writerow([
                    r.rule_id, r.direction, r.tier, r.feature_id,
                    r.token_category, r.action, r.pos_pattern,
                    f"{r.confidence:.4f}", r.frequency
                ])
            for r in ruleset.form_rules:
                writer.writerow([
                    r.rule_id, r.direction, r.tier, 'FORM-CHG',
                    r.source_form, r.target_form, r.pos_pattern,
                    f"{r.confidence:.4f}", r.frequency
                ])
            for r in ruleset.structural_rules:
                writer.writerow([
                    r.rule_id, r.direction, r.tier, r.feature_id,
                    r.pattern, '', '',
                    f"{r.confidence:.4f}", r.frequency
                ])

        print(f"  Saved rule inventory CSV to {path}")
