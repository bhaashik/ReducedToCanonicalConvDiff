"""
Test Morphological Analysis: Run morphological feature analysis on all newspapers.

This analyzes morphological transformations specifically, which are crucial for
headline-to-canonical conversion.
"""

import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(__file__))

from config import BASE_DIR
from paths_config import SCHEMA_PATH
from register_comparison.meta_data.schema import FeatureSchema
from register_comparison.generation.morphological_analyzer import MorphologicalAnalyzer
from test_enhanced_systematicity import EnhancedSystematicityAnalyzer
from register_comparison.aligners.aligner import Aligner
from register_comparison.extractors.extractor import FeatureExtractor
from register_comparison.aggregators.aggregator import Aggregator
from register_comparison.ted_config import TEDConfig
from register_comparison.comparators.schema_comparator import SchemaBasedComparator as Comparator
from data.loaded_data import loaded_data


def run_morphological_analysis(newspaper: str):
    """Run morphological analysis for a newspaper."""

    print("="*80)
    print(f"MORPHOLOGICAL ANALYSIS: {newspaper}")
    print("="*80)

    # Setup
    schema = FeatureSchema(SCHEMA_PATH)
    schema.load_schema()

    output_dir = BASE_DIR / "output" / newspaper / "morphological_analysis"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    print(f"\n1. Loading data for {newspaper}...")
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

    # Extract events
    print(f"\n2. Extracting transformation events...")
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

    # Enrich with context (to get morphological features)
    print(f"\n3. Enriching events with morphological context...")
    sys_analyzer = EnhancedSystematicityAnalyzer(schema)
    enhanced_events = sys_analyzer.enrich_existing_events(pairs, aggregator.global_events)

    # Run morphological analysis
    print(f"\n4. Running morphological analysis...")
    morph_analyzer = MorphologicalAnalyzer(schema)
    results = morph_analyzer.analyze_morphological_events(enhanced_events)

    # Save results
    print(f"\n5. Saving results...")
    morph_analyzer.save_results(results, output_dir)

    print(f"\n{'='*80}")
    print(f"MORPHOLOGICAL ANALYSIS COMPLETE: {newspaper}")
    print(f"{'='*80}")
    print(f"\nResults saved to: {output_dir}")

    return results


def main():
    """Run morphological analysis for all newspapers."""

    newspapers = ["Times-of-India", "Hindustan-Times", "The-Hindu"]

    print("="*80)
    print("MORPHOLOGICAL ANALYSIS - ALL NEWSPAPERS")
    print("="*80)

    all_results = {}

    for newspaper in newspapers:
        print(f"\n{'='*80}")
        results = run_morphological_analysis(newspaper)
        all_results[newspaper] = results
        print("\n")

    # Create comparative summary
    print(f"\n{'='*80}")
    print("CROSS-NEWSPAPER MORPHOLOGICAL COMPARISON")
    print(f"{'='*80}")

    print("\n📊 Morphological Transformations by Newspaper:\n")
    print(f"{'Newspaper':<20} {'Total Morph':<15} {'Verb':<10} {'VerbForm':<12} {'Tense':<10}")
    print("-"*80)

    for newspaper, results in all_results.items():
        verb = results['verb_analysis']
        print(f"{newspaper:<20} {results['total_transformations']:<15,} "
              f"{verb['total_verb_transformations']:<10,} "
              f"{verb['verbform_changes']:<12,} "
              f"{verb['tense_changes']:<10,}")

    print("\n" + "="*80)
    print("All morphological analyses complete!")
    print("="*80)


if __name__ == "__main__":
    main()
