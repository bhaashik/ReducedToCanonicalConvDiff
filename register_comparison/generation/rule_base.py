"""
Rule Base: Storage and organization of transformation rules.

Stores deterministic transformation rules extracted from aligned data
and provides efficient lookup during generation.
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class TransformationRule:
    """A single transformation rule"""
    feature_id: str
    source_pattern: str  # Pattern in headline
    target_value: str  # What to generate in canonical
    confidence: float
    frequency: int
    context: Dict[str, Any] = field(default_factory=dict)

    def applies_to(self, headline_features: Dict[str, Any]) -> bool:
        """Check if this rule applies given headline features"""
        # Simple pattern matching for now
        # In full version, would check all context features
        return True  # Placeholder

    def apply(self, headline_parse: Any) -> Any:
        """Apply this rule to transform headline parse"""
        # Placeholder - actual transformation would modify parse tree
        return headline_parse


class RuleBase:
    """
    Organizes and stores transformation rules for efficient lookup.

    Rules are organized by:
    - Feature type (FW-DEL, CONST-MOV, etc.)
    - Confidence level (deterministic >95%, high >90%, etc.)
    - Application order (morphological → lexical → syntactic → discourse)
    """

    def __init__(self):
        self.rules_by_feature: Dict[str, List[TransformationRule]] = defaultdict(list)
        self.rules_by_confidence: Dict[str, List[TransformationRule]] = {
            'deterministic': [],  # >95%
            'high': [],  # 90-95%
            'medium': [],  # 70-90%
            'low': []  # <70%
        }
        self.all_rules: List[TransformationRule] = []

        # Rule application order (from GENERATION_ARCHITECTURE.md)
        self.application_order = [
            'morphological',  # Tense, agreement
            'lexical',  # Function word insertion
            'syntactic',  # Structure changes
            'discourse'  # Sentence-level
        ]

        self.feature_to_level = {
            # Morphological
            'FEAT-CHG': 'morphological',
            'FORM-CHG': 'morphological',
            'VERB-FORM-CHG': 'morphological',

            # Lexical
            'FW-DEL': 'lexical',
            'FW-ADD': 'lexical',
            'C-DEL': 'lexical',
            'C-ADD': 'lexical',
            'LEMMA-CHG': 'lexical',

            # Syntactic
            'DEP-REL-CHG': 'syntactic',
            'HEAD-CHG': 'syntactic',
            'CONST-MOV': 'syntactic',
            'CONST-ADD': 'syntactic',
            'CONST-REM': 'syntactic',
            'CLAUSE-TYPE-CHG': 'syntactic',
            'TOKEN-REORDER': 'syntactic',

            # Discourse
            'LENGTH-CHG': 'discourse',
            'POS-CHG': 'discourse'
        }

    def load_from_csv(self, csv_path: Path):
        """
        Load rules from systematicity analysis CSV.

        CSV format: pattern,transformation,instances,consistency,confidence
        """
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse pattern: "FEATURE::source→target"
                pattern = row['pattern']
                parts = pattern.split('::')
                if len(parts) != 2:
                    continue

                feature_id = parts[0]
                source_target = parts[1]

                # Parse source→target
                if '→' in source_target:
                    source, _ = source_target.split('→')
                else:
                    source = source_target

                rule = TransformationRule(
                    feature_id=feature_id,
                    source_pattern=source,
                    target_value=row['transformation'],
                    confidence=float(row['confidence']),
                    frequency=int(row['instances'])
                )

                self.add_rule(rule)

        print(f"Loaded {len(self.all_rules)} rules from {csv_path}")

    def add_rule(self, rule: TransformationRule):
        """Add a rule to the rule base"""
        self.all_rules.append(rule)
        self.rules_by_feature[rule.feature_id].append(rule)

        # Categorize by confidence
        if rule.confidence > 0.95:
            self.rules_by_confidence['deterministic'].append(rule)
        elif rule.confidence > 0.90:
            self.rules_by_confidence['high'].append(rule)
        elif rule.confidence > 0.70:
            self.rules_by_confidence['medium'].append(rule)
        else:
            self.rules_by_confidence['low'].append(rule)

    def get_rules_for_feature(self, feature_id: str,
                             min_confidence: float = 0.95) -> List[TransformationRule]:
        """Get all rules for a specific feature above confidence threshold"""
        return [r for r in self.rules_by_feature[feature_id]
                if r.confidence >= min_confidence]

    def get_ordered_rules(self, min_confidence: float = 0.95) -> List[TransformationRule]:
        """
        Get rules ordered by application level (morphological → discourse)
        """
        ordered = []

        for level in self.application_order:
            # Find features at this level
            features_at_level = [f for f, l in self.feature_to_level.items()
                                if l == level]

            # Add rules for these features
            for feature in features_at_level:
                rules = self.get_rules_for_feature(feature, min_confidence)
                ordered.extend(rules)

        return ordered

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the rule base"""
        return {
            'total_rules': len(self.all_rules),
            'by_confidence': {
                k: len(v) for k, v in self.rules_by_confidence.items()
            },
            'by_feature': {
                k: len(v) for k, v in self.rules_by_feature.items()
            },
            'by_level': {
                level: sum(len(self.rules_by_feature[f])
                          for f, l in self.feature_to_level.items()
                          if l == level)
                for level in self.application_order
            }
        }

    def save_to_json(self, output_path: Path):
        """Save rule base to JSON"""
        data = {
            'rules': [
                {
                    'feature_id': r.feature_id,
                    'source_pattern': r.source_pattern,
                    'target_value': r.target_value,
                    'confidence': r.confidence,
                    'frequency': r.frequency,
                    'context': r.context
                }
                for r in self.all_rules
            ],
            'statistics': self.get_statistics()
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Saved rule base to {output_path}")
