#!/usr/bin/env python3
"""
Test script for Tree Edit Distance algorithms implementation.
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from register_comparison.ted_config import TEDConfig, get_ted_config
from register_comparison.comparators.schema_comparator import SchemaBasedComparator
from register_comparison.meta_data.schema import FeatureSchema
from register_comparison.aligners.aligner import AlignedSentencePair
from nltk.tree import Tree


def create_test_trees():
    """Create test trees for TED algorithm testing."""
    # Simple test trees
    tree1 = Tree.fromstring("(S (NP (DT The) (NN cat)) (VP (VBZ sits)))")
    tree2 = Tree.fromstring("(S (NP (DT A) (NN dog)) (VP (VBZ runs)))")

    # More complex trees
    tree3 = Tree.fromstring("(S (NP (DT The) (JJ big) (NN cat)) (VP (VBZ sits) (PP (IN on) (NP (DT the) (NN mat)))))")
    tree4 = Tree.fromstring("(S (NP (DT A) (NN dog)) (VP (VBZ runs)))")

    return [(tree1, tree2), (tree3, tree4), (tree1, tree3)]


def test_ted_algorithms():
    """Test all TED algorithms with different configurations."""
    print("=" * 80)
    print("TESTING TREE EDIT DISTANCE ALGORITHMS")
    print("=" * 80)

    # Create dummy schema for testing
    class DummySchema:
        pass

    schema = DummySchema()
    test_cases = create_test_trees()

    # Test different configurations
    configs = {
        'default': TEDConfig.default(),
        'simple_only': TEDConfig.simple_only(),
        'standard_only': TEDConfig.standard_only(),
        'performance': TEDConfig.performance_optimized()
    }

    for config_name, ted_config in configs.items():
        print(f"\n{'='*60}")
        print(f"TESTING CONFIGURATION: {config_name.upper()}")
        print(f"Enabled algorithms: {ted_config.enabled_algorithms}")
        print(f"{'='*60}")

        comparator = SchemaBasedComparator(schema, ted_config)

        for i, (tree1, tree2) in enumerate(test_cases, 1):
            print(f"\nTest Case {i}:")
            print(f"Tree 1: {tree1}")
            print(f"Tree 2: {tree2}")

            # Test tree sizes
            tree1_size = comparator._tree_size(tree1)
            tree2_size = comparator._tree_size(tree2)
            max_size = max(tree1_size, tree2_size)

            print(f"Tree sizes: {tree1_size}, {tree2_size} (max: {max_size})")

            # Get algorithms for this tree size
            algorithms = ted_config.get_algorithms_for_tree_size(max_size)
            print(f"Algorithms to use: {algorithms}")

            # Test each algorithm
            results = {}
            for algorithm in algorithms:
                try:
                    distance = comparator._calculate_tree_edit_distance(tree1, tree2, algorithm)
                    results[algorithm] = distance
                    print(f"  {algorithm}: {distance}")
                except Exception as e:
                    print(f"  {algorithm}: ERROR - {e}")
                    results[algorithm] = f"ERROR: {e}"

            print(f"Results summary: {results}")


def test_individual_algorithms():
    """Test individual algorithm implementations directly."""
    print("\n" + "=" * 80)
    print("TESTING INDIVIDUAL ALGORITHM IMPLEMENTATIONS")
    print("=" * 80)

    # Create dummy comparator
    class DummySchema:
        pass

    schema = DummySchema()
    comparator = SchemaBasedComparator(schema)

    # Simple test case
    tree1 = Tree.fromstring("(S (NP (DT The) (NN cat)) (VP (VBZ sits)))")
    tree2 = Tree.fromstring("(S (NP (DT A) (NN dog)) (VP (VBZ runs)))")

    algorithms = ['simple', 'zhang_shasha', 'klein', 'rted']

    print(f"\nTesting with trees:")
    print(f"Tree 1: {tree1}")
    print(f"Tree 2: {tree2}")

    for algorithm in algorithms:
        print(f"\n--- Testing {algorithm.upper()} ---")
        try:
            # Test the specific algorithm implementation
            if algorithm == 'simple':
                result = comparator._calculate_simple_ted(tree1, tree2)
            elif algorithm == 'zhang_shasha':
                result = comparator._calculate_zhang_shasha_ted(tree1, tree2)
            elif algorithm == 'klein':
                result = comparator._calculate_klein_ted(tree1, tree2)
            elif algorithm == 'rted':
                result = comparator._calculate_rted(tree1, tree2)

            print(f"Result: {result}")

            # Test helper functions
            if algorithm == 'zhang_shasha':
                nodes1, labels1 = comparator._tree_to_postorder(tree1)
                nodes2, labels2 = comparator._tree_to_postorder(tree2)
                print(f"Post-order labels 1: {labels1}")
                print(f"Post-order labels 2: {labels2}")

            if algorithm == 'klein':
                key1 = comparator._tree_to_string_key(tree1)
                key2 = comparator._tree_to_string_key(tree2)
                print(f"String key 1: {key1}")
                print(f"String key 2: {key2}")

            if algorithm == 'rted':
                nodes1 = comparator._tree_to_rted_format(tree1)
                nodes2 = comparator._tree_to_rted_format(tree2)
                print(f"RTED format 1: {len(nodes1)} nodes")
                print(f"RTED format 2: {len(nodes2)} nodes")

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()


def test_config_loading():
    """Test configuration loading and validation."""
    print("\n" + "=" * 80)
    print("TESTING CONFIGURATION LOADING")
    print("=" * 80)

    # Test predefined configurations
    config_names = ['default', 'simple_only', 'standard_only', 'performance']

    for config_name in config_names:
        print(f"\n--- Testing config: {config_name} ---")
        try:
            config = get_ted_config(config_name)
            print(f"Enabled algorithms: {config.enabled_algorithms}")
            print(f"Max tree size for complex algorithms: {config.max_tree_size_for_complex_algorithms}")
            print(f"Use memoization: {config.use_memoization}")

            # Test algorithm descriptions
            for alg in config.enabled_algorithms:
                desc = config.get_algorithm_description(alg)
                mnemonic = config.get_algorithm_mnemonic(alg)
                print(f"  {alg}: {desc} ({mnemonic})")

        except Exception as e:
            print(f"ERROR: {e}")


if __name__ == "__main__":
    print("Starting TED Algorithm Tests...")

    try:
        test_config_loading()
        test_individual_algorithms()
        test_ted_algorithms()

        print("\n" + "=" * 80)
        print("ALL TESTS COMPLETED")
        print("=" * 80)

    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()