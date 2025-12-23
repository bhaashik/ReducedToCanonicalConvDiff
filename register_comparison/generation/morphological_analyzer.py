"""
Morphological Feature Analysis: Analyze transformation systematicity based on morphological features.

This module specifically focuses on morphological transformations which are crucial for
headline-to-canonical generation, especially:
- Tense/Aspect changes (VerbForm, Tense, Aspect)
- Number agreement (Number)
- Definiteness (Definite)
- Person/Case features

Unlike the general systematicity analyzer which found pattern fragmentation,
this analyzer treats morphological features as PRIMARY predictors.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from collections import defaultdict, Counter
from dataclasses import dataclass, field
import pandas as pd


@dataclass
class MorphologicalTransformation:
    """A specific morphological feature transformation."""
    feature_name: str  # e.g., "Tense", "VerbForm", "Number"
    headline_value: str  # e.g., "Pres", "Inf", "Sing"
    canonical_value: str  # e.g., "Past", "Fin", "Plur"
    pos: str  # POS tag
    lemma: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


class MorphologicalAnalyzer:
    """
    Analyzes morphological feature transformations in headline-to-canonical conversion.

    Focuses specifically on morphology rather than syntax, as morphological changes
    are often deterministic and rule-based.
    """

    def __init__(self, schema):
        self.schema = schema
        self.morph_transformations: List[MorphologicalTransformation] = []

        # Track patterns by morphological feature
        self.patterns_by_morph_feature = defaultdict(lambda: defaultdict(list))

        # Common morphological features to track
        self.morph_features = [
            'Tense',      # Past, Pres, Fut
            'VerbForm',   # Fin, Inf, Part, Ger
            'Aspect',     # Imp, Perf, Prog
            'Number',     # Sing, Plur
            'Person',     # 1, 2, 3
            'Case',       # Nom, Acc, etc.
            'Definite',   # Def, Ind
            'Mood',       # Ind, Sub, Imp
            'Voice',      # Act, Pass
        ]

    def analyze_morphological_events(self, enhanced_events: List[Any]) -> Dict[str, Any]:
        """
        Extract and analyze morphological transformations from enhanced events.

        Args:
            enhanced_events: List of EnhancedDifferenceEvent objects

        Returns:
            Dictionary with morphological analysis results
        """

        print(f"\n{'='*80}")
        print("MORPHOLOGICAL FEATURE ANALYSIS")
        print(f"{'='*80}")

        # Extract morphological transformations
        print("\n1. Extracting morphological transformations...")
        self._extract_morph_transformations(enhanced_events)

        # Analyze systematicity by morphological feature
        print("2. Analyzing systematicity by morphological feature...")
        morph_systematicity = self._analyze_morph_systematicity()

        # Analyze verb morphology specifically (most important)
        print("3. Analyzing verb morphology...")
        verb_analysis = self._analyze_verb_morphology()

        # Analyze noun morphology
        print("4. Analyzing noun morphology...")
        noun_analysis = self._analyze_noun_morphology()

        # Create morphological transformation rules
        print("5. Extracting morphological rules...")
        morph_rules = self._extract_morph_rules()

        results = {
            'morph_systematicity': morph_systematicity,
            'verb_analysis': verb_analysis,
            'noun_analysis': noun_analysis,
            'morphological_rules': morph_rules,
            'total_transformations': len(self.morph_transformations)
        }

        self._print_summary(results)

        return results

    def _extract_morph_transformations(self, enhanced_events: List[Any]):
        """Extract morphological feature changes from events."""

        morph_change_count = 0

        for event in enhanced_events:
            if not event.headline_context or not event.canonical_context:
                continue

            headline_morph = event.headline_context.morph_features
            canonical_morph = event.canonical_context.morph_features

            # Compare morphological features
            all_morph_keys = set(headline_morph.keys()) | set(canonical_morph.keys())

            for morph_feature in all_morph_keys:
                h_value = headline_morph.get(morph_feature, 'ABSENT')
                c_value = canonical_morph.get(morph_feature, 'ABSENT')

                if h_value != c_value:
                    # Morphological transformation detected
                    transformation = MorphologicalTransformation(
                        feature_name=morph_feature,
                        headline_value=h_value,
                        canonical_value=c_value,
                        pos=event.headline_context.upos or 'UNK',
                        lemma=event.headline_context.lemma,
                        context={
                            'dep_rel': event.headline_context.dep_rel,
                            'is_proper_noun': event.headline_context.is_proper_noun,
                            'has_aux': event.headline_context.has_auxiliary,
                            'clause_type': event.headline_context.clause_type
                        }
                    )

                    self.morph_transformations.append(transformation)
                    morph_change_count += 1

                    # Index by feature
                    pattern_key = f"{morph_feature}::{h_value}→{c_value}@{transformation.pos}"
                    self.patterns_by_morph_feature[morph_feature][pattern_key].append(transformation)

        print(f"   ✅ Extracted {morph_change_count:,} morphological transformations")
        print(f"   ✅ From {len(enhanced_events):,} total events")

    def _analyze_morph_systematicity(self) -> Dict[str, Any]:
        """Analyze systematicity of morphological transformations."""

        feature_stats = {}

        for morph_feature in self.morph_features:
            if morph_feature not in self.patterns_by_morph_feature:
                continue

            patterns = self.patterns_by_morph_feature[morph_feature]
            total_instances = sum(len(instances) for instances in patterns.values())

            if total_instances == 0:
                continue

            # Calculate consistency for each pattern
            deterministic_count = 0
            pattern_details = []

            for pattern_key, instances in patterns.items():
                frequency = len(instances)

                # For morphological features, we track the transformation itself
                # Pattern is already "feature::h_value→c_value@POS"
                # So consistency is always 100% by definition
                consistency = 1.0

                deterministic_count += frequency

                pattern_details.append({
                    'pattern': pattern_key,
                    'frequency': frequency,
                    'consistency': consistency,
                    'percentage': frequency / total_instances * 100
                })

            # Sort by frequency
            pattern_details.sort(key=lambda x: x['frequency'], reverse=True)

            feature_stats[morph_feature] = {
                'total_instances': total_instances,
                'unique_patterns': len(patterns),
                'deterministic_percentage': 100.0,  # By definition
                'top_patterns': pattern_details[:20]
            }

        return feature_stats

    def _analyze_verb_morphology(self) -> Dict[str, Any]:
        """Special analysis for verb morphology (most important for headlines)."""

        verb_transformations = [t for t in self.morph_transformations if t.pos in ['VERB', 'AUX']]

        # Group by transformation type
        tense_changes = [t for t in verb_transformations if t.feature_name == 'Tense']
        verbform_changes = [t for t in verb_transformations if t.feature_name == 'VerbForm']
        aspect_changes = [t for t in verb_transformations if t.feature_name == 'Aspect']

        # Analyze VerbForm changes (crucial for headlines: Inf/Part → Fin)
        verbform_patterns = Counter()
        for t in verbform_changes:
            pattern = f"{t.headline_value} → {t.canonical_value}"
            verbform_patterns[pattern] += 1

        # Analyze Tense changes
        tense_patterns = Counter()
        for t in tense_changes:
            pattern = f"{t.headline_value} → {t.canonical_value}"
            tense_patterns[pattern] += 1

        # Analyze by context
        verbform_with_aux = Counter()
        verbform_without_aux = Counter()
        for t in verbform_changes:
            pattern = f"{t.headline_value} → {t.canonical_value}"
            if t.context.get('has_aux'):
                verbform_with_aux[pattern] += 1
            else:
                verbform_without_aux[pattern] += 1

        return {
            'total_verb_transformations': len(verb_transformations),
            'tense_changes': len(tense_changes),
            'verbform_changes': len(verbform_changes),
            'aspect_changes': len(aspect_changes),
            'verbform_patterns': dict(verbform_patterns.most_common(10)),
            'tense_patterns': dict(tense_patterns.most_common(10)),
            'verbform_with_aux': dict(verbform_with_aux.most_common(5)),
            'verbform_without_aux': dict(verbform_without_aux.most_common(5))
        }

    def _analyze_noun_morphology(self) -> Dict[str, Any]:
        """Analyze noun morphology (number, definiteness)."""

        noun_transformations = [t for t in self.morph_transformations if t.pos in ['NOUN', 'PROPN']]

        number_changes = [t for t in noun_transformations if t.feature_name == 'Number']

        number_patterns = Counter()
        for t in number_changes:
            pattern = f"{t.headline_value} → {t.canonical_value}"
            number_patterns[pattern] += 1

        return {
            'total_noun_transformations': len(noun_transformations),
            'number_changes': len(number_changes),
            'number_patterns': dict(number_patterns.most_common(10))
        }

    def _extract_morph_rules(self, min_frequency: int = 10) -> Dict[str, List[Dict]]:
        """Extract morphological transformation rules."""

        rules_by_feature = {}

        for morph_feature, patterns in self.patterns_by_morph_feature.items():
            rules = []

            for pattern_key, instances in patterns.items():
                if len(instances) < min_frequency:
                    continue

                # Parse pattern: "feature::h_value→c_value@POS"
                parts = pattern_key.split('::')
                if len(parts) != 2:
                    continue

                transformation = parts[1].split('@')
                if len(transformation) != 2:
                    continue

                h_to_c = transformation[0].split('→')
                if len(h_to_c) != 2:
                    continue

                pos = transformation[1]
                h_value = h_to_c[0]
                c_value = h_to_c[1]

                # Collect context conditions
                contexts = defaultdict(Counter)
                for instance in instances:
                    for ctx_key, ctx_value in instance.context.items():
                        if ctx_value is not None:
                            contexts[ctx_key][str(ctx_value)] += 1

                # Find most common context values
                common_contexts = {}
                for ctx_key, ctx_counter in contexts.items():
                    most_common = ctx_counter.most_common(1)[0]
                    if most_common[1] / len(instances) > 0.7:  # >70% consistency
                        common_contexts[ctx_key] = most_common[0]

                rules.append({
                    'feature': morph_feature,
                    'pos': pos,
                    'headline_value': h_value,
                    'canonical_value': c_value,
                    'frequency': len(instances),
                    'context': common_contexts,
                    'rule_description': f"When {pos} has {morph_feature}={h_value}, change to {c_value}"
                })

            # Sort by frequency
            rules.sort(key=lambda x: x['frequency'], reverse=True)
            rules_by_feature[morph_feature] = rules

        return rules_by_feature

    def _print_summary(self, results: Dict[str, Any]):
        """Print analysis summary."""

        print(f"\n{'='*80}")
        print("MORPHOLOGICAL ANALYSIS SUMMARY")
        print(f"{'='*80}")

        print(f"\n📊 Overall:")
        print(f"  Total morphological transformations: {results['total_transformations']:,}")

        print(f"\n🔤 Verb Morphology:")
        verb = results['verb_analysis']
        print(f"  Total verb transformations: {verb['total_verb_transformations']:,}")
        print(f"  VerbForm changes: {verb['verbform_changes']:,}")
        print(f"  Tense changes: {verb['tense_changes']:,}")
        print(f"  Aspect changes: {verb['aspect_changes']:,}")

        print(f"\n  Top VerbForm transformations:")
        for pattern, count in list(verb['verbform_patterns'].items())[:5]:
            print(f"    {pattern}: {count:,} instances")

        print(f"\n📝 Noun Morphology:")
        noun = results['noun_analysis']
        print(f"  Total noun transformations: {noun['total_noun_transformations']:,}")
        print(f"  Number changes: {noun['number_changes']:,}")

        print(f"\n🎯 Morphological Features Tracked:")
        for feature, stats in results['morph_systematicity'].items():
            print(f"  {feature}: {stats['total_instances']:,} transformations, {stats['unique_patterns']} unique patterns")

        print(f"\n{'='*80}")

    def save_results(self, results: Dict[str, Any], output_dir: Path):
        """Save morphological analysis results."""

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save complete results as JSON
        json_file = output_dir / 'morphological_analysis.json'
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Saved morphological analysis to: {json_file}")

        # Save morphological rules as CSV
        all_rules = []
        for feature, rules in results['morphological_rules'].items():
            for rule in rules:
                rule_copy = rule.copy()
                rule_copy['context'] = json.dumps(rule_copy['context'])
                all_rules.append(rule_copy)

        if all_rules:
            df = pd.DataFrame(all_rules)
            csv_file = output_dir / 'morphological_rules.csv'
            df.to_csv(csv_file, index=False)
            print(f"✅ Saved {len(all_rules)} morphological rules to: {csv_file}")

        # Save verb analysis as CSV
        verb_data = []
        for pattern, count in results['verb_analysis']['verbform_patterns'].items():
            parts = pattern.split(' → ')
            if len(parts) == 2:
                verb_data.append({
                    'transformation_type': 'VerbForm',
                    'headline_value': parts[0],
                    'canonical_value': parts[1],
                    'frequency': count
                })

        for pattern, count in results['verb_analysis']['tense_patterns'].items():
            parts = pattern.split(' → ')
            if len(parts) == 2:
                verb_data.append({
                    'transformation_type': 'Tense',
                    'headline_value': parts[0],
                    'canonical_value': parts[1],
                    'frequency': count
                })

        if verb_data:
            df = pd.DataFrame(verb_data)
            verb_file = output_dir / 'verb_morphology.csv'
            df.to_csv(verb_file, index=False)
            print(f"✅ Saved verb morphology analysis to: {verb_file}")
