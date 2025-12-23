"""
Rule Extraction Module: Extracts executable transformation rules from systematicity analysis.

This module takes the systematicity analysis results and creates three tiers of rules:
1. Lexical rules (word-specific transformations)
2. Syntactic rules (POS-pattern based)
3. Probabilistic defaults (corpus frequencies)
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass, field, asdict
import pandas as pd


@dataclass
class LexicalRule:
    """A lexically-conditioned transformation rule"""
    lemma: str
    pos: str
    feature_id: str
    transformation: str
    confidence: float
    frequency: int
    context: Dict[str, Any] = field(default_factory=dict)

    def applies_to(self, token_lemma: str, token_pos: str) -> bool:
        """Check if rule applies to given token"""
        return self.lemma == token_lemma and self.pos == token_pos

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SyntacticRule:
    """A pattern-based transformation rule"""
    rule_id: str
    pos_pattern: str
    dep_pattern: Optional[str]
    position_pattern: Optional[str]
    feature_id: str
    transformation: str
    confidence: float
    frequency: int
    conditions: Dict[str, Any] = field(default_factory=dict)

    def applies_to(self, token_context: Dict[str, Any]) -> bool:
        """Check if rule applies given token context"""
        if token_context.get('pos') != self.pos_pattern:
            return False

        if self.dep_pattern and token_context.get('dep_rel') != self.dep_pattern:
            return False

        if self.position_pattern and token_context.get('position') != self.position_pattern:
            return False

        # Check additional conditions
        for key, value in self.conditions.items():
            if token_context.get(key) != value:
                return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DefaultRule:
    """Probabilistic default for a feature"""
    feature_id: str
    default_transformation: str
    confidence: float
    frequency: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RuleExtractor:
    """
    Extracts transformation rules from systematicity analysis.

    Creates three tiers:
    1. High-confidence lexical rules (specific words)
    2. General syntactic rules (POS patterns)
    3. Feature defaults (most common per feature)
    """

    def __init__(self, schema):
        self.schema = schema
        self.lexical_rules: List[LexicalRule] = []
        self.syntactic_rules: List[SyntacticRule] = []
        self.default_rules: List[DefaultRule] = []

    def extract_from_analysis(self, analysis_path: Path,
                              min_confidence: float = 0.90,
                              min_frequency: int = 5) -> Dict[str, Any]:
        """
        Extract rules from enhanced systematicity analysis.

        Args:
            analysis_path: Path to enhanced_analysis.json
            min_confidence: Minimum consistency for rule extraction
            min_frequency: Minimum instances for reliability

        Returns:
            Dictionary with extracted rules and statistics
        """

        print(f"\n{'='*80}")
        print("EXTRACTING TRANSFORMATION RULES")
        print(f"{'='*80}")

        # Load analysis
        with open(analysis_path, 'r') as f:
            analysis = json.load(f)

        # Extract lexical rules (best granularity)
        print("\n1. Extracting lexical rules...")
        self._extract_lexical_rules(
            analysis['by_granularity']['lexical'],
            min_confidence,
            min_frequency
        )

        # Extract syntactic rules (for fallback)
        print("2. Extracting syntactic rules...")
        self._extract_syntactic_rules(
            analysis['by_granularity']['syntactic'],
            min_confidence,
            min_frequency
        )

        # Extract defaults
        print("3. Extracting default rules...")
        self._extract_default_rules(analysis)

        # Calculate statistics
        stats = self._calculate_statistics()

        print(f"\n{'='*80}")
        print("RULE EXTRACTION COMPLETE")
        print(f"{'='*80}")
        print(f"\nExtracted Rules:")
        print(f"  Lexical:   {len(self.lexical_rules):,}")
        print(f"  Syntactic: {len(self.syntactic_rules):,}")
        print(f"  Defaults:  {len(self.default_rules):,}")
        print(f"  TOTAL:     {sum([len(self.lexical_rules), len(self.syntactic_rules), len(self.default_rules)]):,}")

        return {
            'lexical_rules': [r.to_dict() for r in self.lexical_rules],
            'syntactic_rules': [r.to_dict() for r in self.syntactic_rules],
            'default_rules': [r.to_dict() for r in self.default_rules],
            'statistics': stats
        }

    def _extract_lexical_rules(self, lexical_data: Dict, min_conf: float, min_freq: int):
        """Extract lexical rules from lexical granularity patterns"""

        patterns = lexical_data.get('top_patterns', [])

        for pattern in patterns:
            # Check thresholds
            if pattern['consistency'] < min_conf or pattern['instances'] < min_freq:
                continue

            # Parse pattern: "FEATURE::VALUE@POS:lemma:is_proper"
            try:
                pattern_str = pattern['pattern']
                parts = pattern_str.split('::')
                if len(parts) != 2:
                    continue

                feature_id = parts[0]
                context_part = parts[1].split('@')
                if len(context_part) != 2:
                    continue

                headline_value = context_part[0]
                context_sig = context_part[1]

                # Parse context: "POS:lemma:is_proper"
                context_parts = context_sig.split(':')
                if len(context_parts) >= 2:
                    pos = context_parts[0]
                    lemma = context_parts[1]

                    # Create lexical rule
                    rule = LexicalRule(
                        lemma=lemma if lemma != 'None' else '',
                        pos=pos if pos != 'None' else '',
                        feature_id=feature_id,
                        transformation=pattern['most_common'],
                        confidence=pattern['consistency'],
                        frequency=pattern['instances']
                    )

                    # Only add if we have meaningful lemma
                    if rule.lemma and rule.lemma != 'None':
                        self.lexical_rules.append(rule)

            except Exception as e:
                # Skip malformed patterns
                continue

        # Sort by frequency
        self.lexical_rules.sort(key=lambda r: r.frequency, reverse=True)

        print(f"   Extracted {len(self.lexical_rules)} lexical rules")
        if self.lexical_rules:
            print(f"   Top rule: {self.lexical_rules[0].lemma} ({self.lexical_rules[0].frequency} instances)")

    def _extract_syntactic_rules(self, syntactic_data: Dict, min_conf: float, min_freq: int):
        """Extract syntactic pattern rules"""

        patterns = syntactic_data.get('top_patterns', [])

        rule_id = 0
        for pattern in patterns:
            # Check thresholds
            if pattern['consistency'] < min_conf or pattern['instances'] < min_freq:
                continue

            try:
                pattern_str = pattern['pattern']
                parts = pattern_str.split('::')
                if len(parts) != 2:
                    continue

                feature_id = parts[0]
                context_part = parts[1].split('@')
                if len(context_part) != 2:
                    continue

                context_sig = context_part[1]
                context_parts = context_sig.split(':')

                # Parse: "POS:dep_rel:head_pos:position:has_det"
                pos_pattern = context_parts[0] if len(context_parts) > 0 else None
                dep_pattern = context_parts[1] if len(context_parts) > 1 else None
                position_pattern = context_parts[3] if len(context_parts) > 3 else None

                if pos_pattern and pos_pattern != 'None':
                    rule = SyntacticRule(
                        rule_id=f"SYN_{rule_id:04d}",
                        pos_pattern=pos_pattern,
                        dep_pattern=dep_pattern if dep_pattern != 'None' else None,
                        position_pattern=position_pattern if position_pattern != 'None' else None,
                        feature_id=feature_id,
                        transformation=pattern['most_common'],
                        confidence=pattern['consistency'],
                        frequency=pattern['instances']
                    )

                    self.syntactic_rules.append(rule)
                    rule_id += 1

            except Exception as e:
                continue

        # Sort by frequency
        self.syntactic_rules.sort(key=lambda r: r.frequency, reverse=True)

        print(f"   Extracted {len(self.syntactic_rules)} syntactic rules")

    def _extract_default_rules(self, analysis: Dict):
        """Extract default transformation for each feature"""

        # Collect most common transformation per feature across all data
        feature_transformations = defaultdict(Counter)

        # Use minimal granularity to get feature-level statistics
        minimal = analysis['by_granularity']['minimal']
        for pattern in minimal.get('top_patterns', []):
            feature_id = pattern['pattern'].split('::')[0] if '::' in pattern['pattern'] else pattern['pattern']
            transformation = pattern['most_common']
            frequency = pattern['instances']

            feature_transformations[feature_id][transformation] += frequency

        # Create default rules
        for feature_id, trans_counter in feature_transformations.items():
            if trans_counter:
                most_common_trans, freq = trans_counter.most_common(1)[0]
                total = sum(trans_counter.values())

                rule = DefaultRule(
                    feature_id=feature_id,
                    default_transformation=most_common_trans,
                    confidence=freq / total if total > 0 else 0,
                    frequency=freq
                )

                self.default_rules.append(rule)

        print(f"   Extracted {len(self.default_rules)} default rules")

    def _calculate_statistics(self) -> Dict[str, Any]:
        """Calculate statistics about extracted rules"""

        # Group by feature
        lexical_by_feature = defaultdict(list)
        for rule in self.lexical_rules:
            lexical_by_feature[rule.feature_id].append(rule)

        syntactic_by_feature = defaultdict(list)
        for rule in self.syntactic_rules:
            syntactic_by_feature[rule.feature_id].append(rule)

        # Calculate coverage (total instances covered by rules)
        total_lexical_coverage = sum(r.frequency for r in self.lexical_rules)
        total_syntactic_coverage = sum(r.frequency for r in self.syntactic_rules)

        # Average confidence
        avg_lexical_conf = sum(r.confidence for r in self.lexical_rules) / len(self.lexical_rules) if self.lexical_rules else 0
        avg_syntactic_conf = sum(r.confidence for r in self.syntactic_rules) / len(self.syntactic_rules) if self.syntactic_rules else 0

        return {
            'total_rules': len(self.lexical_rules) + len(self.syntactic_rules) + len(self.default_rules),
            'lexical_count': len(self.lexical_rules),
            'syntactic_count': len(self.syntactic_rules),
            'default_count': len(self.default_rules),
            'lexical_coverage': total_lexical_coverage,
            'syntactic_coverage': total_syntactic_coverage,
            'avg_lexical_confidence': avg_lexical_conf,
            'avg_syntactic_confidence': avg_syntactic_conf,
            'features_with_lexical_rules': len(lexical_by_feature),
            'features_with_syntactic_rules': len(syntactic_by_feature),
            'features_with_defaults': len(self.default_rules)
        }

    def save_rules(self, output_dir: Path):
        """Save extracted rules to JSON and CSV files"""

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save as JSON (complete)
        rules_data = {
            'lexical_rules': [r.to_dict() for r in self.lexical_rules],
            'syntactic_rules': [r.to_dict() for r in self.syntactic_rules],
            'default_rules': [r.to_dict() for r in self.default_rules],
            'statistics': self._calculate_statistics()
        }

        json_path = output_dir / 'extracted_rules.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(rules_data, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Saved complete rules to: {json_path}")

        # Save lexical rules as CSV
        if self.lexical_rules:
            lex_df = pd.DataFrame([r.to_dict() for r in self.lexical_rules])
            lex_csv = output_dir / 'lexical_rules.csv'
            lex_df.to_csv(lex_csv, index=False)
            print(f"✅ Saved {len(self.lexical_rules)} lexical rules to: {lex_csv}")

        # Save syntactic rules as CSV
        if self.syntactic_rules:
            syn_df = pd.DataFrame([r.to_dict() for r in self.syntactic_rules])
            syn_csv = output_dir / 'syntactic_rules.csv'
            syn_df.to_csv(syn_csv, index=False)
            print(f"✅ Saved {len(self.syntactic_rules)} syntactic rules to: {syn_csv}")

        # Save defaults as CSV
        if self.default_rules:
            def_df = pd.DataFrame([r.to_dict() for r in self.default_rules])
            def_csv = output_dir / 'default_rules.csv'
            def_df.to_csv(def_csv, index=False)
            print(f"✅ Saved {len(self.default_rules)} default rules to: {def_csv}")

        return output_dir

    def get_top_n_rules(self, n: int, rule_type: str = 'lexical') -> List[Any]:
        """Get top N rules by frequency"""

        if rule_type == 'lexical':
            return self.lexical_rules[:n]
        elif rule_type == 'syntactic':
            return self.syntactic_rules[:n]
        else:
            return []

    def calculate_coverage_by_rule_count(self, total_events: int) -> List[Tuple[int, float, float]]:
        """
        Calculate cumulative coverage as we add more rules.

        Returns list of (rule_count, coverage_percentage, accuracy_estimate)
        """

        coverage_curve = []

        # Lexical rules
        cumulative = 0
        for i, rule in enumerate(self.lexical_rules, 1):
            cumulative += rule.frequency
            coverage = (cumulative / total_events) * 100 if total_events > 0 else 0

            # Accuracy estimate = weighted average confidence
            avg_conf = sum(r.confidence * r.frequency for r in self.lexical_rules[:i]) / cumulative if cumulative > 0 else 0

            coverage_curve.append((i, coverage, avg_conf * 100))

        return coverage_curve
