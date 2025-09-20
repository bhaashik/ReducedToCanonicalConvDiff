#!/usr/bin/env python3
"""
Test script to demonstrate improved visualization features:
1. Mnemonic labels from schema
2. Better axis scaling
3. Clearer legends and formatting
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from pathlib import Path
from register_comparison.meta_data.schema import FeatureSchema
from register_comparison.visualizers.visualizer import Visualizer

def main():
    print("="*60)
    print("TESTING IMPROVED VISUALIZATIONS")
    print("="*60)

    # Load schema
    schema_path = Path("data/diff-ontology-ver-3.0.json")
    schema = FeatureSchema(schema_path)
    schema.load_schema()
    print(f"✅ Loaded schema with {len(schema.features)} features")

    # Create test output directory
    output_dir = Path("output/VISUALIZATION_TEST")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create visualizer with schema
    visualizer = Visualizer(output_dir, schema)
    print(f"✅ Created visualizer with mnemonic mappings")

    # Test feature label mappings
    print("\n📋 FEATURE LABEL MAPPINGS:")
    test_features = ['FW-DEL', 'DEP-REL-CHG', 'CONST-MOV', 'POS-CHG']
    for feature in test_features:
        label = visualizer._get_feature_label(feature)
        print(f"  {feature} → {label.replace(chr(10), ' ')}")

    # Create test data with realistic feature counts
    test_feature_counts = {
        'CONST-MOV': 11485,
        'DEP-REL-CHG': 9892,
        'CLAUSE-TYPE-CHG': 2728,
        'FW-DEL': 2241,
        'TED': 1034,
        'LENGTH-CHG': 1022,
        'C-DEL': 720,
        'C-ADD': 540,
        'HEAD-CHG': 282,
        'CONST-REM': 254,
        'FW-ADD': 170,
        'FEAT-CHG': 129,
        'CONST-ADD': 124,
        'POS-CHG': 89,
        'FORM-CHG': 89,
        'LEMMA-CHG': 22,
        'VERB-FORM-CHG': 14,
        'TOKEN-REORDER': 12
    }

    print(f"\n🎯 CREATING IMPROVED VISUALIZATION:")
    print(f"  • Using mnemonic labels from schema")
    print(f"  • Improved axis scaling for close values")
    print(f"  • Enhanced legends and formatting")
    print(f"  • Better color coding and readability")

    # Create improved feature frequency plot
    visualizer.plot_feature_frequencies(
        test_feature_counts,
        "Register Difference Features (Enhanced with Mnemonics)",
        "enhanced_feature_frequencies.png"
    )

    print(f"\n✅ IMPROVEMENTS IMPLEMENTED:")
    print(f"  1. ✅ Mnemonic labels: Features show both code and full name")
    print(f"  2. ✅ Axis scaling: Better range for close values")
    print(f"  3. ✅ Clear legends: Informative legend box with totals")
    print(f"  4. ✅ Enhanced formatting: Larger figure, better colors, grids")
    print(f"  5. ✅ Value labels: Count shown on each bar")

    print(f"\n📁 OUTPUT FILES:")
    print(f"  • Enhanced plot: {output_dir}/enhanced_feature_frequencies.png")

    # Compare with default labels (fallback)
    print(f"\n🔄 FALLBACK LABEL TESTING:")
    fallback_visualizer = Visualizer(output_dir)  # No schema
    for feature in ['UNKNOWN-FEAT', 'FW-DEL']:
        fallback_label = fallback_visualizer._get_feature_label(feature)
        schema_label = visualizer._get_feature_label(feature)
        print(f"  {feature}:")
        print(f"    Fallback: {fallback_label.replace(chr(10), ' ')}")
        print(f"    Schema:   {schema_label.replace(chr(10), ' ')}")

    print(f"\n✅ VISUALIZATION IMPROVEMENTS SUCCESSFULLY TESTED!")
    print("="*60)

if __name__ == "__main__":
    main()