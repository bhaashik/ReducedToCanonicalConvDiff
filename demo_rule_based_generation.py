"""
Demo: Rule-Based Headline-to-Canonical Generation

This script demonstrates the complete pipeline:
1. Load deterministic transformation rules
2. Load test headline-canonical pairs
3. Apply rules to generate canonical forms from headlines
4. Evaluate against gold standard canonical forms
5. Analyze success/failure patterns

This is a PROOF-OF-CONCEPT showing the viability of rule-based generation.
Full implementation would require enhanced context capture (see SYSTEMATICITY_FINDINGS.md).
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple, Dict, Any

sys.path.append(os.path.dirname(__file__))

from config import BASE_DIR
from paths_config import SCHEMA_PATH
from register_comparison.meta_data.schema import FeatureSchema
from register_comparison.generation.rule_base import RuleBase
from data.loaded_data import loaded_data


def load_test_data(newspaper: str, num_samples: int = 50) -> List[Tuple[str, str]]:
    """Load test headline-canonical pairs"""
    loaded_data.load_newspaper_data(newspaper)

    canonical_texts = loaded_data.get_canonical_text(newspaper)
    headline_texts = loaded_data.get_headlines_text(newspaper)

    # Take first num_samples pairs
    pairs = list(zip(headline_texts[:num_samples], canonical_texts[:num_samples]))

    return pairs


def simple_token_match_score(generated: str, gold: str) -> float:
    """
    Calculate simple token-level match score.

    This is a placeholder - full evaluation would use:
    - Exact match
    - Token accuracy
    - POS sequence match
    - Dependency structure match (UAS/LAS)
    """
    gen_tokens = generated.lower().split()
    gold_tokens = gold.lower().split()

    # Simple overlap
    if not gold_tokens:
        return 0.0

    matches = sum(1 for t in gen_tokens if t in gold_tokens)
    return matches / len(gold_tokens)


def demonstrate_rule_based_generation():
    """Main demonstration function"""

    print("="*80)
    print("RULE-BASED HEADLINE-TO-CANONICAL GENERATION DEMO")
    print("="*80)

    # Step 1: Load schema
    print("\n1. Loading schema...")
    schema = FeatureSchema(SCHEMA_PATH)
    schema.load_schema()
    print(f"   Loaded {len(schema.features)} features")

    # Step 2: Load deterministic rules
    print("\n2. Loading deterministic transformation rules...")
    rule_base = RuleBase()

    rules_path = (BASE_DIR / "output" / "Times-of-India" /
                  "systematicity_analysis" / "deterministic_rules_feature_value_level.csv")

    if not rules_path.exists():
        print(f"   ERROR: Rules file not found at {rules_path}")
        print(f"   Please run test_systematicity_analysis.py first!")
        return

    rule_base.load_from_csv(rules_path)

    # Print statistics
    stats = rule_base.get_statistics()
    print(f"\n   Rule Base Statistics:")
    print(f"   - Total rules: {stats['total_rules']}")
    print(f"   - Deterministic (>95%): {stats['by_confidence']['deterministic']}")
    print(f"   - By level:")
    for level, count in stats['by_level'].items():
        print(f"     - {level}: {count} rules")

    # Step 3: Load test data
    print("\n3. Loading test data...")
    test_pairs = load_test_data("Times-of-India", num_samples=20)
    print(f"   Loaded {len(test_pairs)} test pairs")

    # Step 4: Demonstrate transformations
    print("\n4. Demonstrating rule-based generation...")
    print("   " + "="*76)

    exact_matches = 0
    total_token_score = 0.0

    for i, (headline, canonical) in enumerate(test_pairs, 1):
        print(f"\n   Example {i}:")
        print(f"   Headline:  {headline}")
        print(f"   Gold:      {canonical}")

        # PLACEHOLDER: Actual transformation
        # In full version, this would:
        # 1. Parse headline with Stanza
        # 2. Apply rules in order (morphological → lexical → syntactic)
        # 3. Generate surface form

        # For now, simple demonstration:
        generated = simple_rule_application(headline, rule_base)

        print(f"   Generated: {generated}")

        # Evaluate
        exact_match = (generated.lower().strip() == canonical.lower().strip())
        token_score = simple_token_match_score(generated, canonical)

        print(f"   Exact match: {'✓' if exact_match else '✗'}")
        print(f"   Token overlap: {token_score:.1%}")

        if exact_match:
            exact_matches += 1
        total_token_score += token_score

    # Step 5: Overall results
    print("\n" + "="*80)
    print("RESULTS SUMMARY")
    print("="*80)

    print(f"\nExact match accuracy: {exact_matches}/{len(test_pairs)} ({exact_matches/len(test_pairs)*100:.1f}%)")
    print(f"Average token overlap: {total_token_score/len(test_pairs)*100:.1f}%")

    print("\n📊 INTERPRETATION:")
    print("\nThis is a SIMPLIFIED DEMO. The low accuracy is expected because:")
    print("  1. Current rules lack linguistic context (POS, syntax, position)")
    print("  2. No actual parse tree transformation implemented yet")
    print("  3. Rules are patterns, not executable transformations")

    print("\n✅ WHAT THIS DEMONSTRATES:")
    print("  1. Rules can be extracted from parallel data")
    print("  2. Rule base organization is feasible")
    print("  3. ~88.5% theoretical ceiling is achievable WITH proper implementation")

    print("\n🔧 NEXT STEPS FOR FULL IMPLEMENTATION:")
    print("  1. Enhance DifferenceEvent to capture headline-side context")
    print("  2. Implement actual parse tree transformations")
    print("  3. Add article/auxiliary insertion rules with context")
    print("  4. Implement rule application engine")
    print("  5. Full evaluation framework")

    print("\nSee GENERATION_ARCHITECTURE.md and SYSTEMATICITY_FINDINGS.md for details.")
    print("="*80)


def simple_rule_application(headline: str, rule_base: RuleBase) -> str:
    """
    Simplified rule application for demonstration.

    PLACEHOLDER: This is a mock implementation.
    Full version would parse headline and apply transformation rules.
    """

    # For now, just return headline with simple heuristic additions
    # This demonstrates the CONCEPT, not actual transformation

    generated = headline

    # Simple heuristic: add articles before nouns
    # (Real version would use POS tagging and context rules)
    words = headline.split()
    result = []

    for i, word in enumerate(words):
        # Extremely simple heuristic for demo purposes
        if word[0].isupper() and i > 0:  # Might be proper noun
            result.append("the")
        result.append(word)

    generated = " ".join(result)

    return generated


if __name__ == "__main__":
    demonstrate_rule_based_generation()
