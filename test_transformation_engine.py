"""
Test Transformation Engine: Evaluate extracted rules on test data.

This script:
1. Loads extracted rules
2. Loads enhanced events (with context)
3. Applies transformation engine
4. Evaluates accuracy and coverage
5. Generates detailed error analysis
"""

import sys
import os
from pathlib import Path
import json

sys.path.append(os.path.dirname(__file__))

from config import BASE_DIR
from paths_config import SCHEMA_PATH
from register_comparison.meta_data.schema import FeatureSchema
from register_comparison.generation.transformation_engine import TransformationEngine
from register_comparison.comparators.enhanced_event import EnhancedDifferenceEvent
from test_enhanced_systematicity import EnhancedSystematicityAnalyzer
from register_comparison.aligners.aligner import Aligner
from register_comparison.extractors.extractor import FeatureExtractor
from register_comparison.aggregators.aggregator import Aggregator
from register_comparison.ted_config import TEDConfig
from register_comparison.comparators.schema_comparator import SchemaBasedComparator as Comparator
from data.loaded_data import loaded_data


def test_transformation_engine(newspaper: str = "Times-of-India"):
    """
    Test transformation engine on a newspaper dataset.

    Args:
        newspaper: Which newspaper to test on
    """

    print("="*80)
    print(f"TESTING TRANSFORMATION ENGINE: {newspaper}")
    print("="*80)

    # Paths
    rules_file = BASE_DIR / "output" / newspaper / "rule_analysis" / "extracted_rules" / "extracted_rules.json"
    output_dir = BASE_DIR / "output" / newspaper / "rule_analysis" / "evaluation"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not rules_file.exists():
        print(f"\n❌ Rules file not found: {rules_file}")
        print("   Run 'python run_complete_rule_analysis.py --newspaper {newspaper}' first")
        return

    # Step 1: Load transformation engine
    print(f"\n1. Loading transformation engine...")
    engine = TransformationEngine(rules_file)

    # Step 2: Load data and create enhanced events
    print(f"\n2. Loading data and creating enhanced events...")
    print(f"   Loading {newspaper} data...")

    schema = FeatureSchema(SCHEMA_PATH)
    schema.load_schema()

    loaded_data.load_newspaper_data(newspaper)

    aligner = Aligner(
        texts_canonical=loaded_data.get_canonical_text(newspaper),
        texts_headlines=loaded_data.get_headlines_text(newspaper),
        deps_canonical=loaded_data.get_canonical_deps(newspaper),
        deps_headlines=loaded_data.get_headlines_deps(newspaper),
        consts_canonical=loaded_data.get_canonical_const(newspaper),
        consts_headlines=loaded_data.get_headlines_const(newspaper),
        newspaper_name=newspaper
    )
    pairs = aligner.align()
    print(f"   ✅ Aligned {len(pairs)} pairs")

    # Extract baseline events
    print(f"\n   Extracting transformation events...")
    extractor = FeatureExtractor(schema)
    ted_config = TEDConfig.default()
    comparator = Comparator(schema, ted_config)
    aggregator = Aggregator()

    for i, pair in enumerate(pairs):
        if (i + 1) % 100 == 0:
            print(f"   Processed {i+1}/{len(pairs)} pairs...", end='\r')
        features = extractor.extract_features(pair)
        events = comparator.compare_pair(pair, features)
        aggregator.add_events(events)

    print(f"\n   ✅ Extracted {len(aggregator.global_events):,} events")

    # Enrich with context
    print(f"\n   Enriching events with context...")
    analyzer = EnhancedSystematicityAnalyzer(schema)
    enhanced_events = analyzer.enrich_existing_events(pairs, aggregator.global_events)

    # Step 3: Apply transformation engine
    print(f"\n3. Applying transformation engine...")
    results = engine.apply_to_events(enhanced_events)

    # Step 4: Print statistics
    print(f"\n4. Evaluation Results:")
    engine.print_statistics()

    # Step 5: Save results
    print(f"\n5. Saving results...")
    engine.save_results(results, output_dir)

    # Step 6: Analyze by tier
    print(f"\n6. Tier-by-Tier Analysis:")
    analyze_by_tier(results)

    # Step 7: Analyze by feature
    print(f"\n7. Feature-Level Analysis:")
    analyze_by_feature(results, output_dir)

    print(f"\n{'='*80}")
    print("EVALUATION COMPLETE")
    print(f"{'='*80}")
    print(f"\nResults saved to: {output_dir}")


def analyze_by_tier(results):
    """Analyze accuracy by rule tier."""

    from collections import defaultdict

    tier_stats = defaultdict(lambda: {'total': 0, 'correct': 0})

    for result in results:
        tier_stats[result.rule_type]['total'] += 1
        if result.matched:
            tier_stats[result.rule_type]['correct'] += 1

    print("\nAccuracy by Rule Tier:")
    print(f"{'='*60}")
    print(f"{'Tier':<15} {'Total':<10} {'Correct':<10} {'Accuracy'}")
    print(f"{'-'*60}")

    tier_order = ['lexical', 'syntactic', 'default', 'none']
    for tier in tier_order:
        if tier in tier_stats:
            stats = tier_stats[tier]
            accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"{tier.title():<15} {stats['total']:<10,} {stats['correct']:<10,} {accuracy:.1f}%")

    print(f"{'='*60}")


def analyze_by_feature(results, output_dir: Path):
    """Analyze accuracy by feature type."""

    from collections import defaultdict
    import pandas as pd

    feature_stats = defaultdict(lambda: {'total': 0, 'correct': 0, 'by_tier': defaultdict(int)})

    for result in results:
        feature_stats[result.feature_id]['total'] += 1
        if result.matched:
            feature_stats[result.feature_id]['correct'] += 1
        feature_stats[result.feature_id]['by_tier'][result.rule_type] += 1

    print("\nTop 10 Features by Volume:")
    print(f"{'='*70}")
    print(f"{'Feature':<20} {'Total':<10} {'Correct':<10} {'Accuracy':<12} {'Primary Tier'}")
    print(f"{'-'*70}")

    # Sort by total
    sorted_features = sorted(feature_stats.items(), key=lambda x: x[1]['total'], reverse=True)

    for feature_id, stats in sorted_features[:10]:
        accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        primary_tier = max(stats['by_tier'].items(), key=lambda x: x[1])[0] if stats['by_tier'] else 'none'
        print(f"{feature_id:<20} {stats['total']:<10,} {stats['correct']:<10,} {accuracy:<12.1f} {primary_tier}")

    print(f"{'='*70}")

    # Save complete feature analysis
    feature_data = []
    for feature_id, stats in sorted_features:
        accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        primary_tier = max(stats['by_tier'].items(), key=lambda x: x[1])[0] if stats['by_tier'] else 'none'

        feature_data.append({
            'feature_id': feature_id,
            'total': stats['total'],
            'correct': stats['correct'],
            'accuracy': f"{accuracy:.1f}%",
            'primary_tier': primary_tier,
            'lexical_hits': stats['by_tier']['lexical'],
            'syntactic_hits': stats['by_tier']['syntactic'],
            'default_hits': stats['by_tier']['default'],
            'no_rule_hits': stats['by_tier']['none']
        })

    df = pd.DataFrame(feature_data)
    df.to_csv(output_dir / 'feature_analysis.csv', index=False)
    print(f"\n✅ Saved complete feature analysis to: {output_dir / 'feature_analysis.csv'}")


def main():
    """Run transformation engine test."""

    import argparse

    parser = argparse.ArgumentParser(description="Test Transformation Engine")
    parser.add_argument(
        '--newspaper',
        type=str,
        default='Times-of-India',
        help='Newspaper to test on'
    )

    args = parser.parse_args()

    test_transformation_engine(args.newspaper)


if __name__ == "__main__":
    main()
