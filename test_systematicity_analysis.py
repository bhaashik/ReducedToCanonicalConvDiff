"""
Test the Systematicity Analyzer to measure how deterministic transformations are.

This script analyzes existing transformation events to determine what percentage
can be handled by deterministic rules vs. require context-dependent decisions.
"""

import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(__file__))

from config import BASE_DIR
from paths_config import SCHEMA_PATH, NEWSPAPERS
from register_comparison.meta_data.schema import FeatureSchema
from register_comparison.aligners.aligner import Aligner
from register_comparison.extractors.extractor import FeatureExtractor
from register_comparison.comparators.schema_comparator import SchemaBasedComparator as Comparator
from register_comparison.aggregators.aggregator import Aggregator
from register_comparison.ted_config import TEDConfig
from data.loaded_data import loaded_data
from register_comparison.generation.systematicity_analyzer import SystematicityAnalyzer


def main():
    print("="*70)
    print("SYSTEMATICITY ANALYSIS - Testing Rule-Based Generation Feasibility")
    print("="*70)

    # Load schema
    print("\n1. Loading schema...")
    schema = FeatureSchema(SCHEMA_PATH)
    schema.load_schema()
    print(f"   Loaded {len(schema.features)} features")

    # Choose newspaper(s) to analyze
    newspaper_name = "Times-of-India"
    print(f"\n2. Loading data for {newspaper_name}...")

    # Load data
    loaded_data.load_newspaper_data(newspaper_name)

    # Prepare aligner
    aligner = Aligner(
        texts_canonical=loaded_data.get_canonical_text(newspaper_name),
        texts_headlines=loaded_data.get_headlines_text(newspaper_name),
        deps_canonical=loaded_data.get_canonical_deps(newspaper_name),
        deps_headlines=loaded_data.get_headlines_deps(newspaper_name),
        consts_canonical=loaded_data.get_canonical_const(newspaper_name),
        consts_headlines=loaded_data.get_headlines_const(newspaper_name),
        newspaper_name=newspaper_name
    )
    pairs = aligner.align()
    print(f"   Aligned {len(pairs)} sentence pairs")

    # Extract features and compare
    print("\n3. Extracting transformation events...")
    extractor = FeatureExtractor(schema)
    ted_config = TEDConfig.default()
    comparator = Comparator(schema, ted_config)
    aggregator = Aggregator()

    for i, pair in enumerate(pairs):
        if (i + 1) % 100 == 0:
            print(f"   Processed {i + 1}/{len(pairs)} pairs...", end='\r')
        features = extractor.extract_features(pair)
        events = comparator.compare_pair(pair, features)
        aggregator.add_events(events)

    print(f"\n   Extracted {len(aggregator.global_events)} total events")

    # Run systematicity analysis
    print("\n4. Running systematicity analysis...")
    analyzer = SystematicityAnalyzer(schema)
    results = analyzer.analyze_events(aggregator.global_events)

    # Save results
    output_dir = BASE_DIR / "output" / newspaper_name / "systematicity_analysis"
    print(f"\n5. Saving analysis results...")
    analyzer.save_analysis(output_dir, results)

    print("\n" + "="*70)
    print("SYSTEMATICITY ANALYSIS COMPLETE")
    print("="*70)

    # Print key insights
    summary = results['summary']
    print("\n🎯 KEY FINDINGS:")
    print(f"\n   Theoretical ceiling for rule-based generation:")
    print(f"   → {summary['theoretical_ceiling_estimate']:.1f}% of transformations are systematic")
    print(f"\n   Deterministic rules (>95% consistency):")
    print(f"   → Cover {summary['deterministic_coverage_percentage']:.1f}% of all events")
    print(f"\n   Highly systematic patterns (>90% consistency):")
    print(f"   → Cover {summary['highly_systematic_coverage_percentage']:.1f}% of all events")

    print(f"\n📊 NEXT STEPS:")
    print(f"   1. Review deterministic rules in: {output_dir}/deterministic_rules_*.csv")
    print(f"   2. Implement high-confidence rules first (>95% consistency)")
    print(f"   3. Add context-sensitive rules for 70-95% consistency patterns")
    print(f"   4. Develop fallback strategies for remaining {100 - summary['systematic_coverage_percentage']:.1f}%")

    print("\n" + "="*70)


if __name__ == "__main__":
    main()
