"""
Transformation Engine: Applies extracted rules to generate canonical transformations.

This engine uses the 3-tier rule architecture:
1. Lexical rules (word-specific, highest priority)
2. Syntactic rules (POS-pattern based, fallback)
3. Default rules (most common per feature, last resort)
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, Counter

from register_comparison.generation.rule_extractor import LexicalRule, SyntacticRule, DefaultRule
from register_comparison.comparators.enhanced_event import TokenContext, EnhancedDifferenceEvent


@dataclass
class TransformationResult:
    """Result of applying transformation rules to a token/event."""
    feature_id: str
    headline_value: str
    predicted_canonical_value: str
    actual_canonical_value: Optional[str] = None
    rule_type: str = ""  # 'lexical', 'syntactic', 'default', or 'none'
    rule_id: Optional[str] = None
    confidence: float = 0.0
    matched: bool = False  # Did prediction match actual?


@dataclass
class EngineStatistics:
    """Statistics about transformation engine performance."""
    total_events: int = 0
    lexical_rule_hits: int = 0
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
        covered = self.lexical_rule_hits + self.syntactic_rule_hits + self.default_rule_hits
        return (covered / self.total_events * 100) if self.total_events > 0 else 0


class TransformationEngine:
    """
    Applies transformation rules in 3-tier hierarchy.

    The engine:
    1. Tries to match lexical rules first (most specific)
    2. Falls back to syntactic rules (POS-based patterns)
    3. Uses default rules as last resort
    4. Returns None if no rule matches
    """

    def __init__(self, rules_file: Path):
        """
        Initialize engine with extracted rules.

        Args:
            rules_file: Path to extracted_rules.json from RuleExtractor
        """
        self.rules_file = Path(rules_file)

        # Load rules
        with open(self.rules_file, 'r') as f:
            rules_data = json.load(f)

        # Parse rules
        self.lexical_rules = self._load_lexical_rules(rules_data.get('lexical_rules', []))
        self.syntactic_rules = self._load_syntactic_rules(rules_data.get('syntactic_rules', []))
        self.default_rules = self._load_default_rules(rules_data.get('default_rules', []))

        # Index for fast lookup
        self._index_rules()

        # Statistics
        self.stats = EngineStatistics()

        print(f"✅ Loaded transformation engine:")
        print(f"   - Lexical rules: {len(self.lexical_rules)}")
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

    def _index_rules(self):
        """Create indexes for fast rule lookup."""

        # Index lexical rules by (lemma, pos, feature_id)
        self.lexical_index = defaultdict(list)
        for rule in self.lexical_rules:
            key = (rule.lemma, rule.pos, rule.feature_id)
            self.lexical_index[key].append(rule)

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
            return self._check_prediction(result, event.canonical_value)

        # Try Tier 2: Syntactic rules
        result = self._try_syntactic_rules(event)
        if result:
            self.stats.syntactic_rule_hits += 1
            return self._check_prediction(result, event.canonical_value)

        # Try Tier 3: Default rules
        result = self._try_default_rules(event)
        if result:
            self.stats.default_rule_hits += 1
            return self._check_prediction(result, event.canonical_value)

        # No rule matched
        self.stats.no_rule_hits += 1
        return TransformationResult(
            feature_id=event.feature_id,
            headline_value=event.headline_value,
            predicted_canonical_value=event.headline_value,  # Default: no change
            actual_canonical_value=event.canonical_value,
            rule_type='none',
            confidence=0.0,
            matched=False
        )

    def _try_lexical_rules(self, event: EnhancedDifferenceEvent) -> Optional[TransformationResult]:
        """Try to apply lexical rules."""

        if not event.headline_context:
            return None

        context = event.headline_context
        lemma = context.lemma
        pos = context.upos

        if not lemma or not pos:
            return None

        # Look up matching rules
        key = (lemma, pos, event.feature_id)
        matching_rules = self.lexical_index.get(key, [])

        if not matching_rules:
            return None

        # Use first matching rule (highest frequency)
        rule = matching_rules[0]

        return TransformationResult(
            feature_id=event.feature_id,
            headline_value=event.headline_value,
            predicted_canonical_value=rule.transformation,
            actual_canonical_value=None,  # Will be filled later
            rule_type='lexical',
            rule_id=f"LEX_{lemma}_{pos}",
            confidence=rule.confidence
        )

    def _try_syntactic_rules(self, event: EnhancedDifferenceEvent) -> Optional[TransformationResult]:
        """Try to apply syntactic rules."""

        if not event.headline_context:
            return None

        context = event.headline_context
        pos = context.upos

        if not pos:
            return None

        # Look up matching rules by POS
        key = (pos, event.feature_id)
        matching_rules = self.syntactic_index.get(key, [])

        if not matching_rules:
            return None

        # Filter by additional conditions
        for rule in matching_rules:
            if rule.applies_to({
                'pos': pos,
                'dep_rel': context.dep_rel,
                'position': context.position_category
            }):
                return TransformationResult(
                    feature_id=event.feature_id,
                    headline_value=event.headline_value,
                    predicted_canonical_value=rule.transformation,
                    actual_canonical_value=None,
                    rule_type='syntactic',
                    rule_id=rule.rule_id,
                    confidence=rule.confidence
                )

        # No rule matched conditions, use first one anyway
        rule = matching_rules[0]
        return TransformationResult(
            feature_id=event.feature_id,
            headline_value=event.headline_value,
            predicted_canonical_value=rule.transformation,
            actual_canonical_value=None,
            rule_type='syntactic',
            rule_id=rule.rule_id,
            confidence=rule.confidence
        )

    def _try_default_rules(self, event: EnhancedDifferenceEvent) -> Optional[TransformationResult]:
        """Try to apply default rules."""

        default_rule = self.default_index.get(event.feature_id)

        if not default_rule:
            return None

        return TransformationResult(
            feature_id=event.feature_id,
            headline_value=event.headline_value,
            predicted_canonical_value=default_rule.default_transformation,
            actual_canonical_value=None,
            rule_type='default',
            rule_id=f"DEFAULT_{event.feature_id}",
            confidence=default_rule.confidence
        )

    def _check_prediction(self, result: TransformationResult, actual_value: str) -> TransformationResult:
        """Check if prediction matches actual value and update statistics."""

        result.actual_canonical_value = actual_value
        result.matched = (result.predicted_canonical_value == actual_value)

        if result.matched:
            self.stats.correct_predictions += 1
        else:
            self.stats.incorrect_predictions += 1

        return result

    def apply_to_events(self, events: List[EnhancedDifferenceEvent]) -> List[TransformationResult]:
        """
        Apply transformation rules to multiple events.

        Args:
            events: List of enhanced difference events

        Returns:
            List of transformation results
        """

        results = []
        for i, event in enumerate(events):
            if (i + 1) % 1000 == 0:
                print(f"   Applied rules to {i+1}/{len(events)} events...", end='\r')

            result = self.apply_to_event(event)
            results.append(result)

        print(f"\n   ✅ Applied rules to {len(events)} events")
        return results

    def get_statistics(self) -> EngineStatistics:
        """Get current engine statistics."""
        return self.stats

    def print_statistics(self):
        """Print detailed statistics."""

        print(f"\n{'='*80}")
        print("TRANSFORMATION ENGINE STATISTICS")
        print(f"{'='*80}")

        print(f"\n📊 Rule Application:")
        print(f"  Total events: {self.stats.total_events:,}")
        print(f"  Lexical hits: {self.stats.lexical_rule_hits:,} ({self.stats.lexical_rule_hits / self.stats.total_events * 100:.1f}%)")
        print(f"  Syntactic hits: {self.stats.syntactic_rule_hits:,} ({self.stats.syntactic_rule_hits / self.stats.total_events * 100:.1f}%)")
        print(f"  Default hits: {self.stats.default_rule_hits:,} ({self.stats.default_rule_hits / self.stats.total_events * 100:.1f}%)")
        print(f"  No rule: {self.stats.no_rule_hits:,} ({self.stats.no_rule_hits / self.stats.total_events * 100:.1f}%)")

        print(f"\n🎯 Accuracy:")
        print(f"  Correct: {self.stats.correct_predictions:,}")
        print(f"  Incorrect: {self.stats.incorrect_predictions:,}")
        print(f"  Overall accuracy: {self.stats.accuracy():.1f}%")
        print(f"  Coverage: {self.stats.coverage():.1f}%")

        print(f"\n{'='*80}")

    def analyze_errors(self, results: List[TransformationResult]) -> Dict[str, Any]:
        """
        Analyze errors by rule type and feature.

        Args:
            results: List of transformation results

        Returns:
            Dictionary with error analysis
        """

        # Group errors by type
        errors_by_type = defaultdict(list)
        errors_by_feature = defaultdict(list)

        for result in results:
            if not result.matched:
                errors_by_type[result.rule_type].append(result)
                errors_by_feature[result.feature_id].append(result)

        # Calculate error rates
        error_analysis = {
            'total_errors': sum(len(errors) for errors in errors_by_type.values()),
            'errors_by_type': {
                rule_type: {
                    'count': len(errors),
                    'examples': [
                        {
                            'feature': e.feature_id,
                            'predicted': e.predicted_canonical_value,
                            'actual': e.actual_canonical_value,
                            'headline': e.headline_value
                        }
                        for e in errors[:5]  # Top 5 examples
                    ]
                }
                for rule_type, errors in errors_by_type.items()
            },
            'errors_by_feature': {
                feature: len(errors)
                for feature, errors in errors_by_feature.items()
            }
        }

        return error_analysis

    def save_results(self, results: List[TransformationResult], output_dir: Path):
        """Save transformation results to files."""

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save as JSON
        results_data = [
            {
                'feature_id': r.feature_id,
                'headline_value': r.headline_value,
                'predicted': r.predicted_canonical_value,
                'actual': r.actual_canonical_value,
                'rule_type': r.rule_type,
                'rule_id': r.rule_id,
                'confidence': r.confidence,
                'matched': r.matched
            }
            for r in results
        ]

        json_file = output_dir / 'transformation_results.json'
        with open(json_file, 'w') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved transformation results to: {json_file}")

        # Save statistics
        stats_file = output_dir / 'engine_statistics.json'
        with open(stats_file, 'w') as f:
            json.dump({
                'total_events': self.stats.total_events,
                'lexical_hits': self.stats.lexical_rule_hits,
                'syntactic_hits': self.stats.syntactic_rule_hits,
                'default_hits': self.stats.default_rule_hits,
                'no_rule': self.stats.no_rule_hits,
                'correct': self.stats.correct_predictions,
                'incorrect': self.stats.incorrect_predictions,
                'accuracy': self.stats.accuracy(),
                'coverage': self.stats.coverage()
            }, f, indent=2)

        print(f"✅ Saved statistics to: {stats_file}")

        # Error analysis
        error_analysis = self.analyze_errors(results)
        error_file = output_dir / 'error_analysis.json'
        with open(error_file, 'w') as f:
            json.dump(error_analysis, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved error analysis to: {error_file}")
