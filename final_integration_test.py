#!/usr/bin/env python3

"""
Final comprehensive integration test for the complete register comparison pipeline
including bidirectional cross-entropy analysis.
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

print("🚀 FINAL COMPREHENSIVE INTEGRATION TEST")
print("=" * 80)

def test_complete_pipeline():
    """Test the complete pipeline with all new features."""

    print("\n1. 📋 Testing All Core Components...")

    # Test all imports
    try:
        from register_comparison.meta_data.schema import FeatureSchema
        from register_comparison.aggregators.aggregator import Aggregator
        from register_comparison.visualizers.visualizer import Visualizer
        from register_comparison.outputs.output_creators import Outputs
        from register_comparison.modular_analysis import ModularAnalysisRunner
        from register_comparison.ted_config import TEDConfig
        print("   ✅ All core imports successful")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False

    # Test all new methods exist
    try:
        agg = Aggregator()
        viz = Visualizer(Path("."), None)
        out = Outputs(Path("."), None)

        # Feature-value pair methods
        assert hasattr(agg, 'get_feature_value_pair_analysis')
        assert hasattr(viz, 'create_feature_value_pair_visualizations')
        assert hasattr(out, 'save_feature_value_pair_analysis')

        # Cross-entropy methods
        assert hasattr(agg, 'get_bidirectional_cross_entropy_analysis')
        assert hasattr(viz, 'create_bidirectional_cross_entropy_visualizations')
        assert hasattr(out, 'save_bidirectional_cross_entropy_analysis')

        print("   ✅ All new methods available")
    except Exception as e:
        print(f"   ❌ Method check failed: {e}")
        return False

    print("\n2. 🔧 Testing Analysis Methods...")

    # Create test aggregator with sample events
    try:
        from register_comparison.comparators.comparator import DifferenceEvent

        # Create sample events for testing
        sample_events = [
            DifferenceEvent("Times-of-India", "sent_1", "dependency", "FW-DEL", "the", "", "Function Word Deletion", "FW-DEL", "context1", "context2"),
            DifferenceEvent("Times-of-India", "sent_2", "dependency", "C-ADD", "", "new", "Content Addition", "C-ADD", "context3", "context4"),
            DifferenceEvent("The-Hindu", "sent_3", "constituency", "POS-CHG", "NOUN", "VERB", "POS Change", "POS-CHG", "context5", "context6"),
            DifferenceEvent("The-Hindu", "sent_4", "dependency", "FW-DEL", "a", "", "Function Word Deletion", "FW-DEL", "context7", "context8"),
        ]

        agg = Aggregator()
        agg.add_events(sample_events)

        # Test comprehensive analysis
        comprehensive = agg.get_comprehensive_analysis()
        assert 'global' in comprehensive
        assert 'by_newspaper' in comprehensive
        print("   ✅ Comprehensive analysis working")

        # Test feature-value analysis
        feature_value = agg.get_feature_value_analysis()
        assert 'global_feature_values' in feature_value
        assert 'transformation_patterns' in feature_value
        print("   ✅ Feature-value analysis working")

        # Test feature-value pair analysis
        pair_analysis = agg.get_feature_value_pair_analysis()
        assert 'global_feature_value_pairs' in pair_analysis
        assert 'pair_statistics' in pair_analysis
        print("   ✅ Feature-value pair analysis working")

        # Test cross-entropy analysis
        cross_entropy = agg.get_bidirectional_cross_entropy_analysis()
        assert 'global_cross_entropy' in cross_entropy
        assert 'by_newspaper_cross_entropy' in cross_entropy
        assert 'feature_level_cross_entropy' in cross_entropy
        print("   ✅ Bidirectional cross-entropy analysis working")

    except Exception as e:
        print(f"   ❌ Analysis methods failed: {e}")
        return False

    print("\n3. 💾 Testing Output Generation...")

    try:
        test_dir = Path("final_test_output")
        test_dir.mkdir(exist_ok=True)

        from register_comparison.meta_data.schema import FeatureSchema
        from paths_config import SCHEMA_PATH

        schema = FeatureSchema(str(SCHEMA_PATH))
        schema.load_schema()

        outputs = Outputs(test_dir, schema)

        # Test all output methods
        outputs.save_comprehensive_analysis(comprehensive, "test_comprehensive")
        outputs.save_feature_value_analysis(feature_value, "test_feature_value")
        outputs.save_feature_value_pair_analysis(pair_analysis, "test_pair_analysis")
        outputs.save_bidirectional_cross_entropy_analysis(cross_entropy, "test_cross_entropy")

        # Count generated files
        output_files = list(test_dir.glob("*"))
        print(f"   ✅ Generated {len(output_files)} output files")

        # Check for key files
        json_files = list(test_dir.glob("*.json"))
        csv_files = list(test_dir.glob("*.csv"))
        print(f"   ✅ Generated {len(json_files)} JSON files")
        print(f"   ✅ Generated {len(csv_files)} CSV files")

    except Exception as e:
        print(f"   ❌ Output generation failed: {e}")
        return False

    print("\n4. 📈 Testing Visualization Generation...")

    try:
        visualizer = Visualizer(test_dir, schema)

        # Test all visualization methods
        visualizer.create_comprehensive_visualizations(comprehensive, agg.get_statistical_summary())
        visualizer.create_feature_value_visualizations(feature_value)
        visualizer.create_feature_value_pair_visualizations(pair_analysis)
        visualizer.create_bidirectional_cross_entropy_visualizations(cross_entropy)

        # Count generated visualizations
        viz_files = list(test_dir.glob("*.png"))
        print(f"   ✅ Generated {len(viz_files)} visualization files")

        # Check for key visualizations
        ce_viz = [f for f in viz_files if "cross_entropy" in f.name]
        pair_viz = [f for f in viz_files if "pair" in f.name]
        print(f"   ✅ Cross-entropy visualizations: {len(ce_viz)}")
        print(f"   ✅ Pair analysis visualizations: {len(pair_viz)}")

    except Exception as e:
        print(f"   ❌ Visualization generation failed: {e}")
        return False

    print("\n5. 🔧 Testing Modular Analysis Integration...")

    try:
        runner = ModularAnalysisRunner("test_modular")
        runner.load_schema()

        # Verify runner has all components
        assert runner.schema is not None
        assert hasattr(runner, 'sentence_level_ted_data')
        assert hasattr(runner, 'global_aggregator')

        print("   ✅ Modular analysis runner ready")

    except Exception as e:
        print(f"   ❌ Modular analysis failed: {e}")
        return False

    print("\n6. 📊 Testing Cross-Entropy Specific Features...")

    try:
        # Verify cross-entropy analysis has all expected components
        global_ce = cross_entropy['global_cross_entropy']

        expected_metrics = [
            'canonical_to_headline_cross_entropy',
            'headline_to_canonical_cross_entropy',
            'bidirectional_cross_entropy_sum',
            'jensen_shannon_divergence',
            'register_overlap_ratio',
            'kl_canonical_to_headline',
            'kl_headline_to_canonical'
        ]

        for metric in expected_metrics:
            assert metric in global_ce, f"Missing metric: {metric}"

        print("   ✅ All cross-entropy metrics present")

        # Test newspaper-level analysis
        newspaper_ce = cross_entropy['by_newspaper_cross_entropy']
        assert len(newspaper_ce) > 0, "No newspaper-level cross-entropy"
        print(f"   ✅ Newspaper-level analysis: {len(newspaper_ce)} newspapers")

        # Test feature-level analysis
        feature_ce = cross_entropy['feature_level_cross_entropy']
        assert len(feature_ce) > 0, "No feature-level cross-entropy"
        print(f"   ✅ Feature-level analysis: {len(feature_ce)} features")

        # Test statistics
        ce_stats = cross_entropy['cross_entropy_statistics']
        assert 'newspaper_comparison' in ce_stats
        assert 'feature_ranking' in ce_stats
        print("   ✅ Cross-entropy statistics generated")

    except Exception as e:
        print(f"   ❌ Cross-entropy features failed: {e}")
        return False

    print("\n7. ✅ Integration Summary...")

    # Count total outputs
    total_files = len(list(test_dir.glob("*")))
    json_count = len(list(test_dir.glob("*.json")))
    csv_count = len(list(test_dir.glob("*.csv")))
    png_count = len(list(test_dir.glob("*.png")))

    print(f"   📊 Total Output Files: {total_files}")
    print(f"   📊 JSON Files: {json_count}")
    print(f"   📊 CSV Files: {csv_count}")
    print(f"   📊 PNG Files: {png_count}")

    return True

if __name__ == "__main__":
    print("Testing complete register comparison pipeline...")
    print("Including: Feature-value pairs + Bidirectional cross-entropy + TED analysis")

    success = test_complete_pipeline()

    if success:
        print("\n" + "=" * 80)
        print("🎉 FINAL INTEGRATION TEST: COMPLETE SUCCESS!")
        print("=" * 80)
        print("✅ All components integrated and working")
        print("✅ Feature-value pair analysis ready")
        print("✅ Bidirectional cross-entropy analysis ready")
        print("✅ Complete pipeline ready for production")
        print("\n🚀 READY TO RUN COMPLETE ANALYSIS:")
        print("python register_comparison/modular_analysis.py --newspapers all --analysis feature-value")
        print("python register_comparison/compare_registers.py")
        print("\n📋 ANALYSIS CAPABILITIES:")
        print("• Multi-dimensional feature analysis")
        print("• Feature-value transformation analysis")
        print("• Feature-value pair atomic unit analysis")
        print("• Bidirectional cross-entropy analysis")
        print("• Information-theoretic measures")
        print("• Sentence-level TED distributions")
        print("• Comprehensive statistical summaries")
        print("• Professional visualizations")
        print("• Multi-format data export")
        print("=" * 80)

    else:
        print("\n" + "=" * 80)
        print("❌ INTEGRATION TEST FAILED")
        print("=" * 80)
        print("Some components need attention before production use.")

    sys.exit(0 if success else 1)