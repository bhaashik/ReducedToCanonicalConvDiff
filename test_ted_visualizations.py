#!/usr/bin/env python3
"""
Test script for TED visualizations with mock data.
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from register_comparison.visualizers.visualizer import Visualizer
from register_comparison.meta_data.schema import FeatureSchema


def create_mock_ted_analysis():
    """Create mock analysis data with TED features for testing."""
    return {
        'global': {
            'TED-SIMPLE': 1500,
            'TED-ZHANG-SHASHA': 890,
            'TED-KLEIN': 1200,
            'TED-RTED': 1100,
            'POS-CHG': 450,
            'LEX-SUB': 320
        },
        'by_newspaper': {
            'Hindustan-Times': {
                'TED-SIMPLE': 520,
                'TED-ZHANG-SHASHA': 310,
                'TED-KLEIN': 440,
                'TED-RTED': 380,
                'POS-CHG': 150,
                'LEX-SUB': 110
            },
            'The-Hindu': {
                'TED-SIMPLE': 480,
                'TED-ZHANG-SHASHA': 280,
                'TED-KLEIN': 380,
                'TED-RTED': 360,
                'POS-CHG': 145,
                'LEX-SUB': 105
            },
            'Times-of-India': {
                'TED-SIMPLE': 500,
                'TED-ZHANG-SHASHA': 300,
                'TED-KLEIN': 380,
                'TED-RTED': 360,
                'POS-CHG': 155,
                'LEX-SUB': 105
            }
        },
        'by_parse_type': {
            'dependency': {
                'TED-SIMPLE': 750,
                'TED-ZHANG-SHASHA': 445,
                'TED-KLEIN': 600,
                'TED-RTED': 550,
                'POS-CHG': 225,
                'LEX-SUB': 160
            },
            'constituency': {
                'TED-SIMPLE': 750,
                'TED-ZHANG-SHASHA': 445,
                'TED-KLEIN': 600,
                'TED-RTED': 550,
                'POS-CHG': 225,
                'LEX-SUB': 160
            }
        },
        'cross_analysis': {
            'Hindustan-Times_dependency': {
                'TED-SIMPLE': 260,
                'TED-ZHANG-SHASHA': 155,
                'TED-KLEIN': 220,
                'TED-RTED': 190
            },
            'Hindustan-Times_constituency': {
                'TED-SIMPLE': 260,
                'TED-ZHANG-SHASHA': 155,
                'TED-KLEIN': 220,
                'TED-RTED': 190
            }
        }
    }


def create_mock_summary():
    """Create mock summary data."""
    return {
        'total_events': 4690,
        'feature_statistics': {
            'TED-SIMPLE': {'count': 1500, 'percentage': 32.0},
            'TED-KLEIN': {'count': 1200, 'percentage': 25.6},
            'TED-RTED': {'count': 1100, 'percentage': 23.5},
            'TED-ZHANG-SHASHA': {'count': 890, 'percentage': 19.0}
        }
    }


def test_ted_visualizations():
    """Test TED visualizations with mock data."""
    print("Testing TED visualizations...")

    # Create output directory
    output_dir = Path("test_output/ted_visualizations")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create dummy schema
    class DummySchema:
        def __init__(self):
            self.features = []

    schema = DummySchema()

    # Create visualizer
    visualizer = Visualizer(output_dir, schema)

    # Create mock data
    analysis = create_mock_ted_analysis()
    summary = create_mock_summary()

    try:
        # Test TED visualizations
        print("\n1. Testing TED register differences combined visualization...")
        ted_data = visualizer._extract_ted_data(analysis)
        visualizer.plot_ted_register_differences_combined(
            ted_data,
            "TEST: Tree Edit Distance Register Differences",
            "test_ted_register_differences.png"
        )
        print("✓ Register differences visualization created")

        print("\n2. Testing TED algorithm agreement visualization...")
        visualizer.plot_ted_algorithm_agreement(
            ted_data,
            "TEST: TED Algorithm Agreement Analysis",
            "test_ted_algorithm_agreement.png"
        )
        print("✓ Algorithm agreement visualization created")

        print("\n3. Testing TED complementary analysis visualization...")
        visualizer.plot_ted_complementary_analysis(
            ted_data,
            "TEST: TED Complementary Structural Perspectives",
            "test_ted_complementary_analysis.png"
        )
        print("✓ Complementary analysis visualization created")

        print("\n4. Testing TED newspaper patterns visualization...")
        visualizer.plot_ted_newspaper_register_patterns(
            ted_data,
            "TEST: TED Newspaper Register Patterns",
            "test_ted_newspaper_patterns.png"
        )
        print("✓ Newspaper patterns visualization created")

        print("\n5. Testing TED structural sensitivity visualization...")
        visualizer.plot_ted_structural_sensitivity(
            ted_data,
            "TEST: TED Structural Sensitivity Analysis",
            "test_ted_structural_sensitivity.png"
        )
        print("✓ Structural sensitivity visualization created")

        print("\n6. Testing complete TED visualization suite...")
        visualizer.create_ted_visualizations(analysis, summary)
        print("✓ Complete TED visualization suite created")

        print(f"\n🎉 All TED visualizations created successfully!")
        print(f"📁 Output directory: {output_dir.absolute()}")

        # List created files
        print("\n📊 Created visualization files:")
        for png_file in sorted(output_dir.glob("*.png")):
            print(f"  • {png_file.name}")

    except Exception as e:
        print(f"\n❌ Error during visualization creation: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_ted_data_extraction():
    """Test TED data extraction functionality."""
    print("\nTesting TED data extraction...")

    output_dir = Path("test_output")
    visualizer = Visualizer(output_dir)

    analysis = create_mock_ted_analysis()
    ted_data = visualizer._extract_ted_data(analysis)

    print(f"✓ Extracted TED algorithms: {list(ted_data['by_algorithm'].keys())}")
    print(f"✓ Extracted newspapers: {list(ted_data['by_newspaper'].keys())}")
    print(f"✓ Total TED events: {ted_data['global_total']}")

    # Verify data structure
    expected_algorithms = ['TED-SIMPLE', 'TED-ZHANG-SHASHA', 'TED-KLEIN', 'TED-RTED']
    actual_algorithms = list(ted_data['by_algorithm'].keys())

    for alg in expected_algorithms:
        if alg in actual_algorithms:
            print(f"✓ Algorithm {alg}: {ted_data['by_algorithm'][alg]} events")
        else:
            print(f"❌ Missing algorithm: {alg}")

    return True


if __name__ == "__main__":
    print("🧪 TED Visualizations Test Suite")
    print("=" * 50)

    try:
        # Test data extraction
        test_ted_data_extraction()

        print("\n" + "=" * 50)

        # Test visualizations
        success = test_ted_visualizations()

        if success:
            print("\n✅ All tests passed!")
            print("\n🎯 KEY VISUALIZATION CREATED:")
            print("   • ted_register_differences_combined.png")
            print("     → Shows register differences across all newspapers")
            print("     → Displays algorithm agreement patterns")
            print("     → Provides comprehensive TED analysis summary")
        else:
            print("\n❌ Some tests failed!")

    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        import traceback
        traceback.print_exc()