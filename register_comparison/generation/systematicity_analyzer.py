"""
Systematicity Analyzer: Measures how deterministic transformations are.

This module analyzes aligned canonical-headline pairs to determine what
percentage of transformations follow systematic, deterministic patterns
vs. variable/context-dependent patterns.
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict, Counter
import json
import pandas as pd
from dataclasses import dataclass, asdict

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import BASE_DIR
from register_comparison.meta_data.schema import FeatureSchema


@dataclass
class TransformationContext:
    """
    Represents the linguistic context in which a transformation occurs.

    ALL context features here must be deterministically extractable from
    the headline (reduced form) alone - no access to canonical form during
    rule application.
    """
    feature_id: str
    source_value: str  # What happens in transformation
    target_value: str

    # Deterministic context from headline parsing
    headline_pos: Optional[str] = None  # POS in headline
    headline_dep_rel: Optional[str] = None  # Dependency relation in headline
    headline_parent_pos: Optional[str] = None  # Parent's POS in headline
    headline_lemma: Optional[str] = None  # Lemma of affected word

    # Positional context (deterministic from headline)
    position_in_sentence: Optional[str] = None  # initial, medial, final
    token_index: Optional[int] = None

    # Phrasal context (from headline constituency parse)
    parent_phrase_type: Optional[str] = None  # NP, VP, PP, etc.
    phrase_depth: Optional[int] = None

    # Lexical context (deterministic from headline)
    is_proper_noun: Optional[bool] = None
    is_count_noun: Optional[bool] = None
    verb_form: Optional[str] = None  # VBZ, VBD, VBG, etc.

    # Local context (surrounding words in headline)
    left_pos: Optional[str] = None
    right_pos: Optional[str] = None
    has_determiner: Optional[bool] = None

    # Semantic features (from headline words)
    noun_type: Optional[str] = None  # person, organization, location, etc.

    def to_key(self, granularity='full') -> str:
        """
        Generate hashable key for grouping transformations.

        Different granularity levels test which contextual features
        are necessary for deterministic rules.
        """
        if granularity == 'feature_only':
            return f"{self.feature_id}"

        elif granularity == 'feature_value':
            return f"{self.feature_id}::{self.source_value}→{self.target_value}"

        elif granularity == 'with_pos':
            return f"{self.feature_id}::{self.source_value}→{self.target_value}::{self.headline_pos}"

        elif granularity == 'with_syntax':
            return (f"{self.feature_id}::{self.source_value}→{self.target_value}::"
                   f"{self.headline_pos}::{self.headline_dep_rel}::{self.position_in_sentence}")

        elif granularity == 'with_phrasal':
            return (f"{self.feature_id}::{self.source_value}→{self.target_value}::"
                   f"{self.headline_pos}::{self.parent_phrase_type}::{self.position_in_sentence}")

        elif granularity == 'with_lexical':
            return (f"{self.feature_id}::{self.source_value}→{self.target_value}::"
                   f"{self.headline_pos}::{self.headline_lemma}::{self.is_proper_noun}::{self.is_count_noun}")

        else:  # 'full' - use all available context
            return (f"{self.feature_id}::{self.source_value}→{self.target_value}::"
                   f"{self.headline_pos}::{self.headline_dep_rel}::{self.headline_parent_pos}::"
                   f"{self.position_in_sentence}::{self.parent_phrase_type}::{self.headline_lemma}::"
                   f"{self.is_proper_noun}::{self.has_determiner}::{self.left_pos}::{self.right_pos}")


@dataclass
class SystematicityMetrics:
    """Metrics for measuring transformation systematicity"""
    total_instances: int
    unique_transformations: int
    most_common_transformation: str
    most_common_count: int
    consistency_ratio: float  # most_common / total
    entropy: float
    is_deterministic: bool  # consistency > 0.95
    is_highly_systematic: bool  # consistency > 0.90
    is_systematic: bool  # consistency > 0.70


class SystematicityAnalyzer:
    """
    Analyzes how systematic/deterministic transformations are.

    Key Questions:
    1. What % of transformations are fully deterministic (>95% consistent)?
    2. How does systematicity vary by feature type?
    3. What contexts enable deterministic rules?
    4. What is the theoretical upper bound for rule-based generation?
    """

    def __init__(self, schema: FeatureSchema):
        self.schema = schema
        self.transformation_patterns: Dict[str, List[TransformationContext]] = defaultdict(list)
        self.statistics: Dict[str, SystematicityMetrics] = {}

    def analyze_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze transformation events to measure systematicity.

        Args:
            events: List of transformation events from aggregator

        Returns:
            Comprehensive systematicity analysis
        """

        print("\n" + "="*60)
        print("SYSTEMATICITY ANALYSIS")
        print("="*60)

        # Step 1: Extract transformation contexts
        print("\nExtracting transformation contexts...")
        self._extract_contexts(events)
        print(f"  Extracted {len(self.transformation_patterns)} unique patterns")

        # Step 2: Analyze at different granularities
        print("\nAnalyzing systematicity at multiple context levels...")
        print("  (Testing which contextual features enable deterministic rules)")
        feature_level = self._analyze_granularity('feature_only')
        feature_value_level = self._analyze_granularity('feature_value')
        with_pos_level = self._analyze_granularity('with_pos')
        with_syntax_level = self._analyze_granularity('with_syntax')
        with_phrasal_level = self._analyze_granularity('with_phrasal')
        with_lexical_level = self._analyze_granularity('with_lexical')
        full_context_level = self._analyze_granularity('full')

        # Step 3: Identify deterministic transformations
        print("\nIdentifying deterministic transformation rules...")
        deterministic_rules = self._find_deterministic_rules()

        # Step 4: Calculate overall metrics
        overall_metrics = self._calculate_overall_metrics()

        # Step 5: Analyze by feature type
        feature_analysis = self._analyze_by_feature()

        results = {
            'summary': overall_metrics,
            'by_granularity': {
                'feature_level': feature_level,
                'feature_value_level': feature_value_level,
                'with_pos_level': with_pos_level,
                'with_syntax_level': with_syntax_level,
                'with_phrasal_level': with_phrasal_level,
                'with_lexical_level': with_lexical_level,
                'full_context_level': full_context_level
            },
            'deterministic_rules': deterministic_rules,
            'by_feature': feature_analysis
        }

        self._print_summary(results)

        return results

    def _extract_contexts(self, events: List[Any]):
        """
        Extract rich linguistic context from transformation events.

        CRITICAL: All context features must be extractable from the headline alone,
        since during generation we only have access to the headline, not the canonical form.
        """

        for event in events:
            # Handle both DifferenceEvent objects and dicts
            if hasattr(event, 'feature_id'):
                feature_id = event.feature_id
                # For now, source is headline, target is canonical (what we're trying to generate)
                source_value = event.headline_value
                target_value = event.canonical_value
                headline_context_str = event.headline_context if hasattr(event, 'headline_context') else ''
            else:
                feature_id = event.get('feature_id')
                source_value = event.get('value', 'NONE')
                target_value = event.get('target_value', 'NONE')
                headline_context_str = event.get('headline_context', '')

            # Parse headline context string to extract features
            # Context string format may vary - need to parse it
            headline_features = self._parse_context_string(headline_context_str)

            context = TransformationContext(
                feature_id=feature_id,
                source_value=source_value,
                target_value=target_value,

                # Syntactic context from headline parse
                headline_pos=headline_features.get('pos'),
                headline_dep_rel=headline_features.get('dep_rel'),
                headline_parent_pos=headline_features.get('parent_pos'),
                headline_lemma=headline_features.get('lemma'),

                # Positional context (from headline)
                position_in_sentence=headline_features.get('position'),
                token_index=headline_features.get('index'),

                # Phrasal context (from headline constituency parse)
                parent_phrase_type=headline_features.get('parent_phrase'),
                phrase_depth=headline_features.get('phrase_depth'),

                # Lexical features (from headline)
                is_proper_noun=headline_features.get('is_proper_noun'),
                is_count_noun=headline_features.get('is_count_noun'),
                verb_form=headline_features.get('verb_form'),

                # Local context (surrounding words in headline)
                left_pos=headline_features.get('left_pos'),
                right_pos=headline_features.get('right_pos'),
                has_determiner=headline_features.get('has_determiner'),

                # Semantic features
                noun_type=headline_features.get('noun_type')
            )

            # Store in multiple granularity levels to test which context is needed
            granularities = ['feature_only', 'feature_value', 'with_pos', 'with_syntax',
                           'with_phrasal', 'with_lexical', 'full']
            for granularity in granularities:
                key = context.to_key(granularity)
                self.transformation_patterns[key].append(context)

    def _parse_context_string(self, context_str: str) -> Dict[str, Any]:
        """
        Parse context string to extract features.

        For now, returns empty dict - in future iterations, we'll enhance
        the event generation to include structured context.
        """
        # Placeholder - context string parsing would go here
        # The context strings in current system may not have all info we need
        # This is a limitation we'll document and address in next iteration
        return {}

    def _infer_position(self, token_info: Dict) -> str:
        """Infer position in sentence from token index"""
        idx = token_info.get('index', 0)
        if idx == 0 or idx == 1:
            return 'initial'
        elif token_info.get('is_last', False):
            return 'final'
        else:
            return 'medial'

    def _is_proper_noun(self, token_info: Dict) -> bool:
        """Check if token is a proper noun"""
        pos = token_info.get('pos', '')
        return pos == 'PROPN' or pos == 'NNP' or pos == 'NNPS'

    def _is_count_noun(self, token_info: Dict) -> bool:
        """Check if noun is countable (vs. mass)"""
        # This would need a countable noun lexicon in practice
        # For now, use POS tag heuristic
        pos = token_info.get('pos', '')
        return pos in ['NOUN', 'NN', 'NNS']

    def _infer_noun_type(self, token_info: Dict) -> Optional[str]:
        """Infer semantic type of noun"""
        # This would need NER in practice
        # For now, return None or use simple heuristics
        if self._is_proper_noun(token_info):
            # Could check capitalization patterns, name lists, etc.
            return 'proper'
        return None

    def _analyze_granularity(self, granularity: str) -> Dict[str, Any]:
        """Analyze systematicity at a specific granularity level"""

        metrics_by_pattern = {}

        for key, contexts in self.transformation_patterns.items():
            # Only analyze patterns at this granularity
            if not self._matches_granularity(key, granularity):
                continue

            total = len(contexts)

            # Count transformation outcomes
            if granularity == 'feature_only':
                # At feature level, count unique value transformations
                outcomes = Counter([f"{c.source_value}→{c.target_value}" for c in contexts])
            else:
                # At other levels, count outcomes
                outcomes = Counter([c.target_value for c in contexts])

            most_common_outcome, most_common_count = outcomes.most_common(1)[0]
            consistency = most_common_count / total

            # Calculate entropy
            entropy = self._calculate_entropy(outcomes, total)

            metrics = SystematicityMetrics(
                total_instances=total,
                unique_transformations=len(outcomes),
                most_common_transformation=most_common_outcome,
                most_common_count=most_common_count,
                consistency_ratio=consistency,
                entropy=entropy,
                is_deterministic=(consistency > 0.95),
                is_highly_systematic=(consistency > 0.90),
                is_systematic=(consistency > 0.70)
            )

            metrics_by_pattern[key] = metrics

        # Aggregate statistics for this granularity
        total_patterns = len(metrics_by_pattern)
        if total_patterns == 0:
            return {'total_patterns': 0}

        deterministic_count = sum(1 for m in metrics_by_pattern.values() if m.is_deterministic)
        highly_systematic_count = sum(1 for m in metrics_by_pattern.values() if m.is_highly_systematic)
        systematic_count = sum(1 for m in metrics_by_pattern.values() if m.is_systematic)

        avg_consistency = sum(m.consistency_ratio for m in metrics_by_pattern.values()) / total_patterns
        avg_entropy = sum(m.entropy for m in metrics_by_pattern.values()) / total_patterns

        return {
            'total_patterns': total_patterns,
            'deterministic_count': deterministic_count,
            'highly_systematic_count': highly_systematic_count,
            'systematic_count': systematic_count,
            'deterministic_percentage': (deterministic_count / total_patterns) * 100,
            'highly_systematic_percentage': (highly_systematic_count / total_patterns) * 100,
            'systematic_percentage': (systematic_count / total_patterns) * 100,
            'average_consistency': avg_consistency,
            'average_entropy': avg_entropy,
            'patterns': {k: asdict(v) for k, v in sorted(
                metrics_by_pattern.items(),
                key=lambda x: x[1].consistency_ratio,
                reverse=True
            )[:20]}  # Top 20 most consistent patterns
        }

    def _matches_granularity(self, key: str, granularity: str) -> bool:
        """Check if a key matches the specified granularity"""
        parts = key.split('::')

        granularity_part_counts = {
            'feature_only': 1,
            'feature_value': 2,
            'with_pos': 3,
            'with_syntax': 5,
            'with_phrasal': 5,
            'with_lexical': 6,
            'full': 12  # All context features
        }

        expected = granularity_part_counts.get(granularity, 100)
        return len(parts) == expected

    def _calculate_entropy(self, outcomes: Counter, total: int) -> float:
        """Calculate Shannon entropy of outcomes"""
        import math

        entropy = 0.0
        for count in outcomes.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)

        return entropy

    def _find_deterministic_rules(self, threshold: float = 0.95) -> Dict[str, Any]:
        """Find transformation patterns that are deterministic (>95% consistent)"""

        deterministic = {
            'feature_level': [],
            'feature_value_level': [],
            'with_pos_level': [],
            'full_context_level': []
        }

        granularity_map = {
            1: 'feature_level',
            2: 'feature_value_level',
            3: 'with_pos_level'
        }

        for key, contexts in self.transformation_patterns.items():
            parts = key.split('::')
            level = granularity_map.get(len(parts), 'full_context_level')

            total = len(contexts)
            if total < 5:  # Skip rare patterns
                continue

            # Count outcomes
            outcomes = Counter([c.target_value for c in contexts])
            most_common_outcome, most_common_count = outcomes.most_common(1)[0]
            consistency = most_common_count / total

            if consistency > threshold:
                deterministic[level].append({
                    'pattern': key,
                    'transformation': most_common_outcome,
                    'instances': total,
                    'consistency': consistency,
                    'confidence': consistency  # Same as consistency for now
                })

        # Sort by instances (frequency)
        for level in deterministic:
            deterministic[level].sort(key=lambda x: x['instances'], reverse=True)

        return deterministic

    def _calculate_overall_metrics(self) -> Dict[str, Any]:
        """Calculate overall systematicity metrics"""

        total_events = sum(len(contexts) for contexts in self.transformation_patterns.values())

        # Count events covered by deterministic rules
        deterministic_rules = self._find_deterministic_rules(0.95)
        highly_systematic_rules = self._find_deterministic_rules(0.90)
        systematic_rules = self._find_deterministic_rules(0.70)

        def count_covered_events(rules_dict):
            return sum(rule['instances'] for level_rules in rules_dict.values()
                      for rule in level_rules)

        deterministic_coverage = count_covered_events(deterministic_rules)
        highly_systematic_coverage = count_covered_events(highly_systematic_rules)
        systematic_coverage = count_covered_events(systematic_rules)

        return {
            'total_transformation_events': total_events,
            'events_with_deterministic_rules': deterministic_coverage,
            'events_with_highly_systematic_rules': highly_systematic_coverage,
            'events_with_systematic_rules': systematic_coverage,
            'deterministic_coverage_percentage': (deterministic_coverage / total_events * 100) if total_events > 0 else 0,
            'highly_systematic_coverage_percentage': (highly_systematic_coverage / total_events * 100) if total_events > 0 else 0,
            'systematic_coverage_percentage': (systematic_coverage / total_events * 100) if total_events > 0 else 0,
            'theoretical_ceiling_estimate': (systematic_coverage / total_events * 100) if total_events > 0 else 0
        }

    def _analyze_by_feature(self) -> Dict[str, Any]:
        """Analyze systematicity broken down by feature type"""

        feature_stats = {}

        for feature_id in self.schema.features.keys():
            # Get all events for this feature
            feature_contexts = [
                ctx for key, contexts in self.transformation_patterns.items()
                for ctx in contexts
                if ctx.feature_id == feature_id
            ]

            if not feature_contexts:
                continue

            total = len(feature_contexts)

            # Count transformation outcomes
            transformations = Counter([f"{c.source_value}→{c.target_value}"
                                      for c in feature_contexts])

            most_common, most_common_count = transformations.most_common(1)[0] if transformations else (None, 0)

            feature_stats[feature_id] = {
                'total_instances': total,
                'unique_transformations': len(transformations),
                'most_common_transformation': most_common,
                'most_common_count': most_common_count,
                'consistency_ratio': (most_common_count / total) if total > 0 else 0,
                'top_5_transformations': transformations.most_common(5)
            }

        # Sort by total instances
        return dict(sorted(feature_stats.items(),
                          key=lambda x: x[1]['total_instances'],
                          reverse=True))

    def _print_summary(self, results: Dict[str, Any]):
        """Print human-readable summary"""

        print("\n" + "="*60)
        print("SYSTEMATICITY ANALYSIS RESULTS")
        print("="*60)

        summary = results['summary']
        print(f"\n📊 Overall Coverage:")
        print(f"  Total transformation events: {summary['total_transformation_events']:,}")
        print(f"  Deterministic rules (>95%):  {summary['events_with_deterministic_rules']:,} "
              f"({summary['deterministic_coverage_percentage']:.1f}%)")
        print(f"  Highly systematic (>90%):    {summary['events_with_highly_systematic_rules']:,} "
              f"({summary['highly_systematic_coverage_percentage']:.1f}%)")
        print(f"  Systematic (>70%):           {summary['events_with_systematic_rules']:,} "
              f"({summary['systematic_coverage_percentage']:.1f}%)")

        print(f"\n🎯 Theoretical Ceiling for Rule-Based Generation:")
        print(f"  Estimated maximum accuracy: {summary['theoretical_ceiling_estimate']:.1f}%")

        print(f"\n📈 Systematicity by Granularity:")
        for level_name, level_data in results['by_granularity'].items():
            if level_data.get('total_patterns', 0) > 0:
                print(f"\n  {level_name}:")
                print(f"    Total patterns: {level_data['total_patterns']}")
                print(f"    Deterministic:  {level_data['deterministic_count']} ({level_data['deterministic_percentage']:.1f}%)")
                print(f"    Avg consistency: {level_data['average_consistency']:.3f}")
                print(f"    Avg entropy: {level_data['average_entropy']:.3f}")

        print(f"\n🔝 Top Features by Frequency:")
        for i, (feat_id, stats) in enumerate(list(results['by_feature'].items())[:10], 1):
            feature = self.schema.get_feature_by_mnemonic(feat_id)
            feat_name = feature.name if feature else feat_id
            print(f"  {i}. {feat_id} ({feat_name}): {stats['total_instances']:,} instances, "
                  f"{stats['unique_transformations']} unique transformations, "
                  f"{stats['consistency_ratio']:.1%} consistency")

        print("\n" + "="*60)

    def save_analysis(self, output_path: Path, results: Dict[str, Any]):
        """Save analysis results to JSON and CSV files"""

        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save JSON
        json_path = output_path / "systematicity_analysis.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Saved analysis to: {json_path}")

        # Save summary as CSV
        summary_df = pd.DataFrame([results['summary']])
        summary_csv = output_path / "systematicity_summary.csv"
        summary_df.to_csv(summary_csv, index=False)
        print(f"✅ Saved summary to: {summary_csv}")

        # Save feature analysis as CSV
        feature_data = []
        for feat_id, stats in results['by_feature'].items():
            feature = self.schema.get_feature_by_mnemonic(feat_id)
            row = {
                'feature_id': feat_id,
                'feature_name': feature.name if feature else feat_id,
                **stats
            }
            feature_data.append(row)

        feature_df = pd.DataFrame(feature_data)
        feature_csv = output_path / "systematicity_by_feature.csv"
        feature_df.to_csv(feature_csv, index=False)
        print(f"✅ Saved feature analysis to: {feature_csv}")

        # Save deterministic rules
        for level_name, rules in results['deterministic_rules'].items():
            if rules:
                rules_df = pd.DataFrame(rules)
                rules_csv = output_path / f"deterministic_rules_{level_name}.csv"
                rules_df.to_csv(rules_csv, index=False)
                print(f"✅ Saved {level_name} rules to: {rules_csv}")
