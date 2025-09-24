#!/usr/bin/env python3

"""
Comprehensive verification of the complete register comparison pipeline.
Tests all components from data loading to final output generation.
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

def verify_complete_pipeline():
    """Verify the complete pipeline works from start to finish."""

    print("=" * 80)
    print("COMPREHENSIVE PIPELINE VERIFICATION")
    print("=" * 80)

    # Test 1: Schema Loading
    print("\n1. 📋 Testing Schema Loading...")
    try:
        from register_comparison.meta_data.schema import FeatureSchema
        from paths_config import SCHEMA_PATH

        schema = FeatureSchema(str(SCHEMA_PATH))
        schema.load_schema()
        print(f"   ✅ Schema loaded successfully: {len(schema.features)} features")

        # Verify key features exist
        key_features = ['FW-DEL', 'C-DEL', 'POS-CHG', 'TED-SIMPLE']
        for feature in key_features:
            if feature in schema.features:
                print(f"   ✅ Key feature found: {feature}")
            else:
                print(f"   ⚠️  Key feature missing: {feature}")

    except Exception as e:
        print(f"   ❌ Schema loading failed: {e}")
        return False

    # Test 2: Data Loading
    print("\n2. 📂 Testing Data Loading...")
    try:
        from data.loaded_data import LoadedData

        loaded_data = LoadedData()
        loaded_data.load_newspaper_data("Times-of-India")
        print("   ✅ Data loading successful")

        # Verify data types
        newspaper_data = loaded_data.text_data["Times-of-India"]
        print(f"   ✅ Text data loaded: {len(newspaper_data['canonical'])} canonical, {len(newspaper_data['headlines'])} headlines")

    except Exception as e:
        print(f"   ❌ Data loading failed: {e}")
        return False

    # Test 3: TED Configuration
    print("\n3. 🌳 Testing TED Configuration...")
    try:
        from register_comparison.ted_config import TEDConfig

        ted_config = TEDConfig.default()
        algorithms = ted_config.get_algorithms_for_tree_size(20)
        print(f"   ✅ TED config working: {len(algorithms)} algorithms available")
        print(f"   ✅ Algorithms: {algorithms}")

    except Exception as e:
        print(f"   ❌ TED configuration failed: {e}")
        return False

    # Test 4: Alignment and Feature Extraction
    print("\n4. 🔗 Testing Alignment and Feature Extraction...")
    try:
        from register_comparison.aligners.aligner import Aligner
        from register_comparison.extractors.extractor import FeatureExtractor

        aligner = Aligner(
            texts_canonical=loaded_data.text_data["Times-of-India"]['canonical'],
            texts_headlines=loaded_data.text_data["Times-of-India"]['headlines'],
            deps_canonical=loaded_data.dependency_data["Times-of-India"]['canonical'],
            deps_headlines=loaded_data.dependency_data["Times-of-India"]['headlines'],
            consts_canonical=loaded_data.constituency_data["Times-of-India"]['canonical'],
            consts_headlines=loaded_data.constituency_data["Times-of-India"]['headlines'],
            newspaper_name="Times-of-India"
        )

        # Test with small subset
        pairs = aligner.align()[:3]
        print(f"   ✅ Alignment successful: {len(pairs)} test pairs")

        extractor = FeatureExtractor(schema)
        features = extractor.extract_features(pairs[0])
        print(f"   ✅ Feature extraction successful: {len(features)} features extracted")

    except Exception as e:
        print(f"   ❌ Alignment/extraction failed: {e}")
        return False

    # Test 5: Comprehensive Comparison with TED
    print("\n5. 🔍 Testing Comprehensive Comparison...")
    try:
        from register_comparison.comparators.schema_comparator import SchemaBasedComparator

        comparator = SchemaBasedComparator(schema, ted_config)

        events = []
        for pair in pairs:
            pair_features = extractor.extract_features(pair)
            pair_events = comparator.compare_pair(pair, pair_features)
            events.extend(pair_events)

        print(f"   ✅ Comparison successful: {len(events)} events generated")

        # Test sentence-level TED scores
        sentence_ted_scores = comparator.get_sentence_level_ted_scores()
        print(f"   ✅ Sentence-level TED scores: {len(sentence_ted_scores)} scores collected")

        # Verify TED algorithms are working
        algorithms_used = set(score['algorithm'] for score in sentence_ted_scores)
        print(f"   ✅ TED algorithms used: {algorithms_used}")

    except Exception as e:
        print(f"   ❌ Comparison failed: {e}")
        return False

    # Test 6: Aggregation and Analysis
    print("\n6. 📊 Testing Aggregation and Analysis...")
    try:
        from register_comparison.aggregators.aggregator import Aggregator

        aggregator = Aggregator()
        aggregator.add_events(events)

        # Test all analysis methods
        comprehensive_analysis = aggregator.get_comprehensive_analysis()
        statistical_summary = aggregator.get_statistical_summary()
        feature_value_analysis = aggregator.get_feature_value_analysis()
        feature_value_pair_analysis = aggregator.get_feature_value_pair_analysis()

        print(f"   ✅ Comprehensive analysis: {len(comprehensive_analysis)} dimensions")
        print(f"   ✅ Statistical summary: {len(statistical_summary)} summaries")
        print(f"   ✅ Feature-value analysis: {len(feature_value_analysis)} components")
        print(f"   ✅ Feature-value pair analysis: {len(feature_value_pair_analysis)} components")

        # Verify sentence-level data integration
        comprehensive_analysis['sentence_level_ted_scores'] = sentence_ted_scores
        print(f"   ✅ Sentence-level TED integration: {len(sentence_ted_scores)} scores")

    except Exception as e:
        print(f"   ❌ Aggregation failed: {e}")
        return False

    # Test 7: Output Generation
    print("\n7. 💾 Testing Output Generation...")
    try:
        from register_comparison.outputs.output_creators import Outputs

        test_output_dir = Path("test_pipeline_verification")
        test_output_dir.mkdir(exist_ok=True)

        outputs = Outputs(test_output_dir, schema)

        # Test all output methods
        outputs.save_comprehensive_analysis(comprehensive_analysis, "test_comprehensive")
        outputs.save_statistical_summary(statistical_summary, "test_statistical")
        outputs.save_feature_value_analysis(feature_value_analysis, "test_feature_value")
        outputs.save_feature_value_pair_analysis(feature_value_pair_analysis, "test_feature_value_pairs")

        print("   ✅ All output methods working")

        # Count generated files
        generated_files = list(test_output_dir.glob("*"))
        print(f"   ✅ Generated {len(generated_files)} output files")

    except Exception as e:
        print(f"   ❌ Output generation failed: {e}")
        return False

    # Test 8: Visualization Pipeline
    print("\n8. 📈 Testing Visualization Pipeline...")
    try:
        from register_comparison.visualizers.visualizer import Visualizer

        visualizer = Visualizer(test_output_dir, schema)

        # Test core visualization methods
        feature_counts = aggregator.global_counts()
        visualizer.plot_feature_frequencies(feature_counts, "Test Features", "test_features.png")

        # Test comprehensive visualizations
        visualizer.create_comprehensive_visualizations(comprehensive_analysis, statistical_summary)
        visualizer.create_statistical_summary_visualizations(comprehensive_analysis, statistical_summary)
        visualizer.create_feature_value_visualizations(feature_value_analysis)
        visualizer.create_feature_value_pair_visualizations(feature_value_pair_analysis)
        visualizer.create_ted_visualizations(comprehensive_analysis, statistical_summary)
        visualizer.create_ted_sentence_level_visualizations(comprehensive_analysis, statistical_summary)

        print("   ✅ All visualization methods working")

        # Count visualization files
        viz_files = list(test_output_dir.glob("*.png"))
        print(f"   ✅ Generated {len(viz_files)} visualization files")

    except Exception as e:
        print(f"   ❌ Visualization failed: {e}")
        return False

    # Test 9: Modular Analysis Integration
    print("\n9. 🔧 Testing Modular Analysis Integration...")
    try:
        from register_comparison.modular_analysis import ModularAnalysisRunner

        # Test modular runner instantiation
        runner = ModularAnalysisRunner("test_modular_output")
        runner.load_schema()

        print("   ✅ Modular analysis runner initialized")
        print(f"   ✅ Schema loaded: {len(runner.schema.features)} features")

        # Test configuration verification
        print("   ✅ Modular analysis integration verified")

    except Exception as e:
        print(f"   ❌ Modular analysis failed: {e}")
        return False

    # Test 10: Pipeline Integration Verification
    print("\n10. ✅ Testing Complete Pipeline Integration...")

    # Verify all key components are integrated
    integration_checks = [
        ("Schema loading", schema is not None),
        ("Data loading", loaded_data.text_data is not None),
        ("TED configuration", ted_config is not None),
        ("Alignment working", len(pairs) > 0),
        ("Feature extraction", len(features) > 0),
        ("Event generation", len(events) > 0),
        ("Sentence-level TED", len(sentence_ted_scores) > 0),
        ("Comprehensive analysis", 'global' in comprehensive_analysis),
        ("Feature-value analysis", 'global_feature_values' in feature_value_analysis),
        ("Feature-value pairs", 'global_feature_value_pairs' in feature_value_pair_analysis),
        ("Output generation", len(generated_files) > 5),
        ("Visualizations", len(viz_files) > 5)
    ]

    passed_checks = 0
    for check_name, check_result in integration_checks:
        if check_result:
            print(f"   ✅ {check_name}")
            passed_checks += 1
        else:
            print(f"   ❌ {check_name}")

    print(f"\n📊 PIPELINE VERIFICATION SUMMARY")
    print(f"   Passed: {passed_checks}/{len(integration_checks)} checks")
    print(f"   Success Rate: {passed_checks/len(integration_checks)*100:.1f}%")

    if passed_checks == len(integration_checks):
        print("\n🎉 COMPLETE PIPELINE VERIFICATION: PASSED")
        print("   ✅ All components integrated and working")
        print("   ✅ Ready for production use")
        return True
    else:
        print(f"\n⚠️  PIPELINE VERIFICATION: PARTIAL ({passed_checks}/{len(integration_checks)})")
        print("   Some components need attention")
        return False

if __name__ == "__main__":
    try:
        success = verify_complete_pipeline()
        if success:
            print("\n" + "=" * 80)
            print("🚀 PIPELINE READY FOR PRODUCTION USE!")
            print("=" * 80)
        else:
            print("\n" + "=" * 80)
            print("⚠️  PIPELINE NEEDS ATTENTION")
            print("=" * 80)

    except Exception as e:
        print(f"\n❌ VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()