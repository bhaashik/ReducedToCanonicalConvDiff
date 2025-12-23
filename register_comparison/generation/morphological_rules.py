"""
Morphological Transformation Rules: Extract and apply morphological feature rules.

This module focuses specifically on morphological transformations which account for
~49% of all headline-to-canonical transformations.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from collections import defaultdict, Counter


@dataclass
class MorphologicalRule:
    """A morphological feature transformation rule."""
    rule_id: str
    pos: str  # POS tag
    morph_feature: str  # e.g., "VerbForm", "Tense", "Number"
    headline_value: str  # e.g., "Part", "Past", "Sing"
    canonical_value: str  # e.g., "Fin", "ABSENT", "Plur"
    confidence: float
    frequency: int
    conditions: Dict[str, Any] = field(default_factory=dict)  # Context conditions

    def applies_to(self, token_context: Any, morph_features: Dict[str, str]) -> bool:
        """Check if rule applies to given token context and morphological features."""

        # Check POS
        if hasattr(token_context, 'upos') and token_context.upos != self.pos:
            return False

        # Check if morphological feature matches
        current_value = morph_features.get(self.morph_feature, 'ABSENT')
        if current_value != self.headline_value:
            return False

        # Check contextual conditions
        for key, value in self.conditions.items():
            if hasattr(token_context, key):
                if getattr(token_context, key) != value:
                    return False
            elif key == 'has_aux':
                if hasattr(token_context, 'has_auxiliary'):
                    if token_context.has_auxiliary != (value == 'True'):
                        return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MorphologicalRuleExtractor:
    """Extracts morphological transformation rules from analysis."""

    def __init__(self):
        self.morphological_rules: List[MorphologicalRule] = []

    def extract_from_morphological_analysis(self,
                                            morph_analysis_path: str,
                                            min_confidence: float = 0.70,
                                            min_frequency: int = 10) -> List[MorphologicalRule]:
        """
        Extract morphological rules from morphological analysis results.

        Args:
            morph_analysis_path: Path to morphological_analysis.json
            min_confidence: Minimum confidence threshold
            min_frequency: Minimum frequency threshold

        Returns:
            List of extracted morphological rules
        """

        import json
        from pathlib import Path

        with open(morph_analysis_path, 'r') as f:
            morph_data = json.load(f)

        print(f"\n{'='*80}")
        print("EXTRACTING MORPHOLOGICAL RULES")
        print(f"{'='*80}")

        rule_id = 0

        # Extract rules from morphological systematicity data
        for morph_feature, feature_data in morph_data['morph_systematicity'].items():
            for pattern in feature_data.get('top_patterns', []):

                # Check thresholds
                consistency = pattern.get('consistency', 1.0)
                frequency = pattern.get('frequency', 0)

                if consistency < min_confidence or frequency < min_frequency:
                    continue

                # Parse pattern: "feature::h_value→c_value@POS"
                try:
                    pattern_str = pattern['pattern']
                    parts = pattern_str.split('::')
                    if len(parts) != 2:
                        continue

                    feature = parts[0]
                    transformation = parts[1].split('@')
                    if len(transformation) != 2:
                        continue

                    values = transformation[0].split('→')
                    if len(values) != 2:
                        continue

                    pos = transformation[1]
                    h_value = values[0]
                    c_value = values[1]

                    # Create rule
                    rule = MorphologicalRule(
                        rule_id=f"MORPH_{rule_id:04d}",
                        pos=pos,
                        morph_feature=feature,
                        headline_value=h_value,
                        canonical_value=c_value,
                        confidence=consistency,
                        frequency=frequency,
                        conditions={}  # Can be enriched with context later
                    )

                    self.morphological_rules.append(rule)
                    rule_id += 1

                except Exception as e:
                    continue

        # Sort by frequency
        self.morphological_rules.sort(key=lambda r: r.frequency, reverse=True)

        print(f"\n✅ Extracted {len(self.morphological_rules)} morphological rules")
        print(f"   Min confidence: {min_confidence:.0%}")
        print(f"   Min frequency: {min_frequency}")

        if self.morphological_rules:
            print(f"\n   Top 5 rules:")
            for rule in self.morphological_rules[:5]:
                print(f"   - {rule.pos} {rule.morph_feature}: {rule.headline_value}→{rule.canonical_value} "
                      f"({rule.frequency} instances, {rule.confidence:.0%} conf)")

        return self.morphological_rules

    def save_rules(self, output_path: str):
        """Save extracted morphological rules."""
        import json
        from pathlib import Path

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        rules_data = {
            'morphological_rules': [r.to_dict() for r in self.morphological_rules],
            'statistics': {
                'total_rules': len(self.morphological_rules),
                'avg_confidence': sum(r.confidence for r in self.morphological_rules) / len(self.morphological_rules) if self.morphological_rules else 0,
                'total_coverage': sum(r.frequency for r in self.morphological_rules)
            }
        }

        with open(output_path, 'w') as f:
            json.dump(rules_data, f, indent=2)

        print(f"   ✅ Saved morphological rules to: {output_path}")


class SubjectVerbAgreementModel:
    """Models subject-verb number agreement for rule application."""

    def __init__(self):
        self.agreement_patterns = Counter()

    def learn_from_events(self, enhanced_events: List[Any]):
        """Learn agreement patterns from enhanced events."""

        for event in enhanced_events:
            if not event.headline_context or not event.canonical_context:
                continue

            # Look for verb number changes
            h_morph = event.headline_context.morph_features
            c_morph = event.canonical_context.morph_features

            if event.headline_context.upos in ['VERB', 'AUX']:
                h_number = h_morph.get('Number', 'ABSENT')
                c_number = c_morph.get('Number', 'ABSENT')

                if h_number != c_number:
                    # Record the transformation
                    dep_rel = event.headline_context.dep_rel
                    pattern = f"{h_number}→{c_number}:{dep_rel}"
                    self.agreement_patterns[pattern] += 1

    def predict_verb_number(self, verb_context: Any, subject_number: str) -> str:
        """Predict verb number based on subject number."""

        # Simple rule: verb should agree with subject
        if subject_number in ['Sing', 'Plur']:
            return subject_number

        # Default to singular for news text (most common)
        return 'Sing'

    def get_statistics(self) -> Dict[str, Any]:
        """Get agreement pattern statistics."""
        return {
            'total_patterns': len(self.agreement_patterns),
            'top_patterns': dict(self.agreement_patterns.most_common(10))
        }
