"""
Transformation Engine with Morphological Tier: 4-tier rule architecture.

This enhanced engine uses:
1. Lexical rules (word-specific, highest priority)
2. Morphological rules (morphological feature-based)
3. Syntactic rules (POS-pattern based)
4. Default rules (most common per feature, last resort)
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, Counter

from register_comparison.generation.rule_extractor import LexicalRule, SyntacticRule, DefaultRule
from register_comparison.generation.morphological_rules import MorphologicalRule
from register_comparison.comparators.enhanced_event import TokenContext, EnhancedDifferenceEvent


@dataclass
class TransformationResult:
    """Result of applying transformation rules to a token/event."""
    feature_id: str
    headline_value: str
    predicted_canonical_value: str
    actual_canonical_value: Optional[str] = None
    rule_type: str = ""  # 'lexical', 'morphological', 'syntactic', 'default', or 'none'
    rule_id: Optional[str] = None
    confidence: float = 0.0
    matched: bool = False  # Did prediction match actual?


@dataclass
class EngineStatistics:
    """Statistics about transformation engine performance."""
    total_events: int = 0
    lexical_rule_hits: int = 0
    morphological_rule_hits: int = 0
    syntactic_rule_hits: int = 0
    default_rule_hits: int = 0
    no_rule_hits: int = 0
    correct_predictions: int = 0
    incorrect_predictions: int = 0

    def accuracy(self) -> float:
        """Calculate overall accuracy."""
        total = self.correct_predictions + self.incorrect_predictions
        return (self.correct_predictions / total * 100) if total > 0 else 0

    def coverage(self) -> float:
        """Calculate rule coverage."""
        covered = (self.lexical_rule_hits + self.morphological_rule_hits +
                  self.syntactic_rule_hits + self.default_rule_hits)
        return (covered / self.total_events * 100) if self.total_events > 0 else 0

    def tier_breakdown(self) -> Dict[str, Dict[str, float]]:
        """Get breakdown by tier."""
        total = self.total_events
        if total == 0:
            return {}

        return {
            'lexical': {
                'hits': self.lexical_rule_hits,
                'coverage': self.lexical_rule_hits / total * 100
            },
            'morphological': {
                'hits': self.morphological_rule_hits,
                'coverage': self.morphological_rule_hits / total * 100
            },
            'syntactic': {
                'hits': self.syntactic_rule_hits,
                'coverage': self.syntactic_rule_hits / total * 100
            },
            'default': {
                'hits': self.default_rule_hits,
                'coverage': self.default_rule_hits / total * 100
            },
            'none': {
                'hits': self.no_rule_hits,
                'coverage': self.no_rule_hits / total * 100
            }
        }


class TransformationEngineWithMorphology:
    """
    Applies transformation rules in 4-tier hierarchy with morphological tier.

    The engine:
    1. Tries to match lexical rules first (most specific)
    2. Falls back to morphological rules (morphological features)
    3. Falls back to syntactic rules (POS-based patterns)
    4. Uses default rules as last resort
    5. Returns None if no rule matches
    """

    def __init__(self, rules_file: Path, morphological_rules_file: Optional[Path] = None):
        """
        Initialize engine with extracted rules.

        Args:
            rules_file: Path to extracted_rules.json from RuleExtractor
            morphological_rules_file: Path to morphological_rules.json
        """
        self.rules_file = Path(rules_file)
        self.morphological_rules_file = morphological_rules_file

        # Load rules
        with open(self.rules_file, 'r') as f:
            rules_data = json.load(f)

        # Parse rules
        self.lexical_rules = self._load_lexical_rules(rules_data.get('lexical_rules', []))
        self.syntactic_rules = self._load_syntactic_rules(rules_data.get('syntactic_rules', []))
        self.default_rules = self._load_default_rules(rules_data.get('default_rules', []))

        # Load morphological rules if available
        self.morphological_rules = []
        if morphological_rules_file and Path(morphological_rules_file).exists():
            self.morphological_rules = self._load_morphological_rules(morphological_rules_file)

        # Index for fast lookup
        self._index_rules()

        # Statistics
        self.stats = EngineStatistics()

        print(f"✅ Loaded transformation engine with morphology:")
        print(f"   - Lexical rules: {len(self.lexical_rules)}")
        print(f"   - Morphological rules: {len(self.morphological_rules)}")
        print(f"   - Syntactic rules: {len(self.syntactic_rules)}")
        print(f"   - Default rules: {len(self.default_rules)}")

    def _load_lexical_rules(self, rules_data: List[Dict]) -> List[LexicalRule]:
        """Load lexical rules from JSON data."""
        return [
            LexicalRule(**rule_dict)
            for rule_dict in rules_data
        ]

    def _load_syntactic_rules(self, rules_data: List[Dict]) -> List[SyntacticRule]:
        """Load syntactic rules from JSON data."""
        return [
            SyntacticRule(**rule_dict)
            for rule_dict in rules_data
        ]

    def _load_default_rules(self, rules_data: List[Dict]) -> List[DefaultRule]:
        """Load default rules from JSON data."""
        return [
            DefaultRule(**rule_dict)
            for rule_dict in rules_data
        ]

    def _load_morphological_rules(self, morph_rules_file: Path) -> List[MorphologicalRule]:
        """Load morphological rules from JSON or CSV."""
        morph_rules_file = Path(morph_rules_file)

        if morph_rules_file.suffix == '.json':
            with open(morph_rules_file, 'r') as f:
                morph_data = json.load(f)
                rules_list = morph_data.get('morphological_rules', [])
                return [MorphologicalRule(**rule_dict) for rule_dict in rules_list]
        elif morph_rules_file.suffix == '.csv':
            import pandas as pd
            df = pd.read_csv(morph_rules_file)
            rules = []
            for _, row in df.iterrows():
                rule = MorphologicalRule(
                    rule_id=row['rule_id'],
                    pos=row['pos'],
                    morph_feature=row['morph_feature'],
                    headline_value=row['headline_value'],
                    canonical_value=row['canonical_value'],
                    confidence=row['confidence'],
                    frequency=row['frequency'],
                    conditions={}
                )
                rules.append(rule)
            return rules
        else:
            return []

    def _index_rules(self):
        """Create indexes for fast rule lookup."""

        # Index lexical rules by (lemma, pos, feature_id)
        self.lexical_index = defaultdict(list)
        for rule in self.lexical_rules:
            key = (rule.lemma, rule.pos, rule.feature_id)
            self.lexical_index[key].append(rule)

        # Index morphological rules by (pos, morph_feature, headline_value)
        self.morphological_index = defaultdict(list)
        for rule in self.morphological_rules:
            key = (rule.pos, rule.morph_feature, rule.headline_value)
            self.morphological_index[key].append(rule)

        # Index syntactic rules by (pos_pattern, feature_id)
        self.syntactic_index = defaultdict(list)
        for rule in self.syntactic_rules:
            key = (rule.pos_pattern, rule.feature_id)
            self.syntactic_index[key].append(rule)

        # Index default rules by feature_id
        self.default_index = {}
        for rule in self.default_rules:
            self.default_index[rule.feature_id] = rule

    def apply_to_event(self, event: EnhancedDifferenceEvent) -> TransformationResult:
        """
        Apply transformation rules to a single event.

        Args:
            event: Enhanced difference event with full context

        Returns:
            TransformationResult with prediction and rule information
        """

        self.stats.total_events += 1

        # Try Tier 1: Lexical rules
        result = self._try_lexical_rules(event)
        if result:
            self.stats.lexical_rule_hits += 1
            return self._finalize_result(result, event)

        # Try Tier 2: Morphological rules
        result = self._try_morphological_rules(event)
        if result:
            self.stats.morphological_rule_hits += 1
            return self._finalize_result(result, event)

        # Try Tier 3: Syntactic rules
        result = self._try_syntactic_rules(event)
        if result:
            self.stats.syntactic_rule_hits += 1
            return self._finalize_result(result, event)

        # Try Tier 4: Default rules
        result = self._try_default_rules(event)
        if result:
            self.stats.default_rule_hits += 1
            return self._finalize_result(result, event)

        # No rule matched
        self.stats.no_rule_hits += 1
        return self._create_no_match_result(event)

    def _try_lexical_rules(self, event: EnhancedDifferenceEvent) -> Optional[TransformationResult]:
        """Try to match lexical rules."""
        if not event.headline_context:
            return None

        lemma = event.headline_context.lemma
        pos = event.headline_context.upos
        feature_id = event.feature_id

        key = (lemma, pos, feature_id)
        matching_rules = self.lexical_index.get(key, [])

        if not matching_rules:
            return None

        # Use highest confidence rule
        best_rule = max(matching_rules, key=lambda r: r.confidence)

        return TransformationResult(
            feature_id=feature_id,
            headline_value=event.headline_value,
            predicted_canonical_value=best_rule.canonical_value,
            rule_type='lexical',
            rule_id=best_rule.rule_id,
            confidence=best_rule.confidence
        )

    def _try_morphological_rules(self, event: EnhancedDifferenceEvent) -> Optional[TransformationResult]:
        """Try to match morphological rules."""
        if not event.headline_context:
            return None

        pos = event.headline_context.upos
        morph_features = event.headline_context.morph_features

        # Extract the morphological feature from feature_id
        # feature_id format: "MORPH_FEAT::feature_name"
        if not event.feature_id.startswith('MORPH_FEAT::'):
            return None

        morph_feature = event.feature_id.replace('MORPH_FEAT::', '')
        headline_value = event.headline_value

        key = (pos, morph_feature, headline_value)
        matching_rules = self.morphological_index.get(key, [])

        if not matching_rules:
            return None

        # Filter rules that apply to this context
        applicable_rules = [
            rule for rule in matching_rules
            if rule.applies_to(event.headline_context, morph_features)
        ]

        if not applicable_rules:
            return None

        # Use highest frequency rule (most common transformation)
        best_rule = max(applicable_rules, key=lambda r: r.frequency)

        return TransformationResult(
            feature_id=event.feature_id,
            headline_value=headline_value,
            predicted_canonical_value=best_rule.canonical_value,
            rule_type='morphological',
            rule_id=best_rule.rule_id,
            confidence=best_rule.confidence
        )

    def _try_syntactic_rules(self, event: EnhancedDifferenceEvent) -> Optional[TransformationResult]:
        """Try to match syntactic rules."""
        if not event.headline_context:
            return None

        pos = event.headline_context.upos
        feature_id = event.feature_id

        # Try exact POS match first
        key = (pos, feature_id)
        matching_rules = self.syntactic_index.get(key, [])

        if not matching_rules:
            # Try wildcard POS
            key = ('*', feature_id)
            matching_rules = self.syntactic_index.get(key, [])

        if not matching_rules:
            return None

        # Use highest confidence rule
        best_rule = max(matching_rules, key=lambda r: r.confidence)

        return TransformationResult(
            feature_id=feature_id,
            headline_value=event.headline_value,
            predicted_canonical_value=best_rule.canonical_value,
            rule_type='syntactic',
            rule_id=best_rule.rule_id,
            confidence=best_rule.confidence
        )

    def _try_default_rules(self, event: EnhancedDifferenceEvent) -> Optional[TransformationResult]:
        """Try to match default rules."""
        feature_id = event.feature_id
        default_rule = self.default_index.get(feature_id)

        if not default_rule:
            return None

        return TransformationResult(
            feature_id=feature_id,
            headline_value=event.headline_value,
            predicted_canonical_value=default_rule.canonical_value,
            rule_type='default',
            rule_id=default_rule.rule_id,
            confidence=default_rule.confidence
        )

    def _finalize_result(self, result: TransformationResult,
                        event: EnhancedDifferenceEvent) -> TransformationResult:
        """Finalize result with actual value and match status."""
        result.actual_canonical_value = event.canonical_value

        if result.predicted_canonical_value == event.canonical_value:
            result.matched = True
            self.stats.correct_predictions += 1
        else:
            result.matched = False
            self.stats.incorrect_predictions += 1

        return result

    def _create_no_match_result(self, event: EnhancedDifferenceEvent) -> TransformationResult:
        """Create result for when no rule matched."""
        result = TransformationResult(
            feature_id=event.feature_id,
            headline_value=event.headline_value,
            predicted_canonical_value="<NO_RULE>",
            actual_canonical_value=event.canonical_value,
            rule_type='none',
            matched=False
        )
        self.stats.incorrect_predictions += 1
        return result

    def apply_to_events(self, events: List[EnhancedDifferenceEvent]) -> List[TransformationResult]:
        """Apply rules to multiple events."""
        return [self.apply_to_event(event) for event in events]

    def get_statistics(self) -> EngineStatistics:
        """Get current engine statistics."""
        return self.stats

    def get_tier_performance(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed performance breakdown by tier."""
        total = self.stats.total_events
        if total == 0:
            return {}

        # Calculate accuracy per tier
        tier_results = defaultdict(lambda: {'correct': 0, 'incorrect': 0, 'total': 0})

        # This requires storing per-tier results, which we'll add

        return {
            'lexical': {
                'coverage': self.stats.lexical_rule_hits / total * 100,
                'hits': self.stats.lexical_rule_hits
            },
            'morphological': {
                'coverage': self.stats.morphological_rule_hits / total * 100,
                'hits': self.stats.morphological_rule_hits
            },
            'syntactic': {
                'coverage': self.stats.syntactic_rule_hits / total * 100,
                'hits': self.stats.syntactic_rule_hits
            },
            'default': {
                'coverage': self.stats.default_rule_hits / total * 100,
                'hits': self.stats.default_rule_hits
            },
            'overall': {
                'coverage': self.stats.coverage(),
                'accuracy': self.stats.accuracy(),
                'total': total
            }
        }

    def print_statistics(self):
        """Print detailed statistics."""
        print(f"\n{'='*80}")
        print("TRANSFORMATION ENGINE STATISTICS (WITH MORPHOLOGY)")
        print(f"{'='*80}\n")

        print(f"Total Events: {self.stats.total_events}")
        print(f"Overall Accuracy: {self.stats.accuracy():.1f}%")
        print(f"Overall Coverage: {self.stats.coverage():.1f}%")

        print(f"\nRule Tier Breakdown:")
        breakdown = self.stats.tier_breakdown()
        for tier, data in breakdown.items():
            print(f"  {tier.capitalize():15s}: {data['hits']:6d} hits ({data['coverage']:5.1f}%)")

        print(f"\nPrediction Results:")
        print(f"  Correct:   {self.stats.correct_predictions}")
        print(f"  Incorrect: {self.stats.incorrect_predictions}")
