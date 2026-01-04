#!/usr/bin/env python3
"""
Morphological Feature Transformation Rule Extraction

Extracts transformation rules for the 20 morphological features from v4.0 schema:
- Original 7: Tense, Number, Aspect, Voice, Mood, Case, Degree
- NEW 13: Person, Gender, Definite, PronType, Poss, NumType, NumForm, Polarity,
          Reflex, VerbForm, Abbr, ExtPos, Foreign

Processes FEAT-CHG events from events_global.csv to extract systematic patterns.
"""

import pandas as pd
import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple
from config import BASE_DIR

NEWSPAPERS = ["Times-of-India", "Hindustan-Times", "The-Hindu"]
OUTPUT_DIR = BASE_DIR / "output"

# All 20 morphological features from v4.0 schema
MORPHOLOGICAL_FEATURES = [
    'Tense', 'Number', 'Aspect', 'Voice', 'Mood', 'Case', 'Degree',  # Original 7
    'Person', 'Gender', 'Definite', 'PronType', 'Poss', 'NumType',   # NEW 13
    'NumForm', 'Polarity', 'Reflex', 'VerbForm', 'Abbr', 'ExtPos', 'Foreign'
]

def parse_feature_value(value_str: str) -> Tuple[str, str]:
    """Parse 'Feature=Value' string."""
    if '=' in value_str:
        parts = value_str.split('=', 1)
        return parts[0], parts[1]
    return '', value_str

def extract_morphological_rules_from_events(newspaper: str,
                                            min_frequency: int = 1,
                                            min_confidence: float = 0.50) -> Dict:
    """Extract morphological transformation rules from FEAT-CHG events."""

    print(f"\n{'='*80}")
    print(f"EXTRACTING MORPHOLOGICAL RULES: {newspaper}")
    print(f"{'='*80}")

    events_file = OUTPUT_DIR / newspaper / "events_global.csv"
    if not events_file.exists():
        print(f"✗ Events file not found: {events_file}")
        return {}

    # Load events with headers (CSV now has extra context columns)
    df = pd.read_csv(events_file, header=0, low_memory=False)

    # Verify required columns exist
    required_cols = ['newspaper', 'sentence_id', 'parse_type', 'feature_id',
                     'feature_name', 'mnemonic', 'canonical_value', 'headline_value']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"✗ Missing required columns: {missing_cols}")
        return {}

    # Filter FEAT-CHG events
    feat_chg = df[df['feature_id'] == 'FEAT-CHG'].copy()
    print(f"Found {len(feat_chg)} FEAT-CHG events")

    if len(feat_chg) == 0:
        print("✗ No FEAT-CHG events found!")
        return {}

    # Extract patterns
    patterns = defaultdict(list)

    for _, row in feat_chg.iterrows():
        canonical_val = row['canonical_value']
        headline_val = row['headline_value']

        # Parse feature name and values
        can_feature, can_value = parse_feature_value(canonical_val)
        head_feature, head_value = parse_feature_value(headline_val)

        # Should be same feature
        if can_feature and can_feature == head_feature:
            feature = can_feature
        elif can_feature:
            feature = can_feature
        elif head_feature:
            feature = head_feature
        else:
            continue

        # Create transformation pattern: Feature: head_value → can_value
        pattern = f"{feature}: {head_value} → {can_value}"
        patterns[feature].append({
            'pattern': pattern,
            'headline_value': head_value,
            'canonical_value': can_value,
            'sentence_id': row['sentence_id']
        })

    # Aggregate and calculate statistics
    rules_by_feature = {}
    all_rules = []

    for feature, instances in patterns.items():
        # Count transformation types
        transformations = Counter()
        for inst in instances:
            trans = f"{inst['headline_value']} → {inst['canonical_value']}"
            transformations[trans] += 1

        # Extract high-frequency transformations as rules
        feature_rules = []
        total_instances = len(instances)

        for transformation, frequency in transformations.most_common():
            if frequency < min_frequency:
                continue

            confidence = frequency / total_instances
            if confidence < min_confidence:
                continue

            h_val, c_val = transformation.split(' → ')

            rule = {
                'feature': feature,
                'headline_value': h_val,
                'canonical_value': c_val,
                'transformation': transformation,
                'frequency': frequency,
                'confidence': confidence,
                'coverage': (frequency / total_instances) * 100
            }

            feature_rules.append(rule)
            all_rules.append(rule)

        if feature_rules:
            rules_by_feature[feature] = {
                'total_instances': total_instances,
                'num_rules': len(feature_rules),
                'rules': feature_rules
            }

    # Summary
    total_rules = sum(r['num_rules'] for r in rules_by_feature.values())
    total_instances = sum(r['total_instances'] for r in rules_by_feature.values())

    print(f"\n📊 Morphological Rule Extraction Results:")
    print(f"  - Total morphological features with rules: {len(rules_by_feature)}")
    print(f"  - Total transformation rules extracted: {total_rules}")
    print(f"  - Total FEAT-CHG instances covered: {total_instances}")

    if rules_by_feature:
        print(f"\n  Top morphological features by rule count:")
        sorted_features = sorted(rules_by_feature.items(),
                                key=lambda x: x[1]['num_rules'],
                                reverse=True)
        for feature, data in sorted_features[:5]:
            print(f"    - {feature}: {data['num_rules']} rules "
                  f"({data['total_instances']} instances)")

    return {
        'newspaper': newspaper,
        'min_frequency': min_frequency,
        'min_confidence': min_confidence,
        'summary': {
            'total_features': len(rules_by_feature),
            'total_rules': total_rules,
            'total_instances': total_instances
        },
        'rules_by_feature': rules_by_feature,
        'all_rules': sorted(all_rules, key=lambda x: x['frequency'], reverse=True)
    }

def save_morphological_rules(newspaper: str, rules_data: Dict):
    """Save morphological rules to multiple formats."""

    output_dir = OUTPUT_DIR / newspaper / "morphological_analysis"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Save complete JSON
    json_file = output_dir / "morphological_rules.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(rules_data, f, indent=2)
    print(f"\n✅ Saved complete rules: {json_file}")

    # 2. Save rules as CSV
    if rules_data.get('all_rules'):
        rules_df = pd.DataFrame(rules_data['all_rules'])
        csv_file = output_dir / "morphological_rules.csv"
        rules_df.to_csv(csv_file, index=False)
        print(f"✅ Saved rules CSV: {csv_file}")

    # 3. Save per-feature rules
    for feature, data in rules_data.get('rules_by_feature', {}).items():
        feature_df = pd.DataFrame(data['rules'])
        feature_file = output_dir / f"morphological_rules_{feature}.csv"
        feature_df.to_csv(feature_file, index=False)

    print(f"✅ Saved {len(rules_data.get('rules_by_feature', {}))} per-feature rule files")

    # 4. Save summary statistics
    summary = {
        'newspaper': newspaper,
        'total_features_with_rules': rules_data['summary']['total_features'],
        'total_transformation_rules': rules_data['summary']['total_rules'],
        'total_feat_chg_instances': rules_data['summary']['total_instances'],
        'features_covered': list(rules_data.get('rules_by_feature', {}).keys())
    }

    summary_file = output_dir / "morphological_rules_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print(f"✅ Saved summary: {summary_file}")

def create_cross_newspaper_morphological_analysis(all_results: Dict):
    """Create cross-newspaper morphological rule analysis."""

    print(f"\n{'='*80}")
    print("CROSS-NEWSPAPER MORPHOLOGICAL RULE ANALYSIS")
    print(f"{'='*80}")

    output_dir = OUTPUT_DIR / "AGGREGATED_CROSS_NEWSPAPER"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Aggregate by feature across newspapers
    feature_aggregation = defaultdict(lambda: {
        'total_instances': 0,
        'total_rules': 0,
        'newspapers': []
    })

    for newspaper, results in all_results.items():
        for feature, data in results.get('rules_by_feature', {}).items():
            feature_aggregation[feature]['total_instances'] += data['total_instances']
            feature_aggregation[feature]['total_rules'] += data['num_rules']
            feature_aggregation[feature]['newspapers'].append(newspaper)

    # Create summary table
    summary_data = []
    for feature, data in sorted(feature_aggregation.items(),
                                key=lambda x: x[1]['total_instances'],
                                reverse=True):
        summary_data.append({
            'feature': feature,
            'total_instances': data['total_instances'],
            'total_rules': data['total_rules'],
            'newspaper_count': len(data['newspapers']),
            'newspapers': ', '.join(data['newspapers'])
        })

    summary_df = pd.DataFrame(summary_data)
    summary_file = output_dir / "morphological_features_cross_newspaper.csv"
    summary_df.to_csv(summary_file, index=False)

    print(f"\n📊 Cross-Newspaper Summary:")
    print(f"  - Total morphological features: {len(feature_aggregation)}")
    print(f"  - Total transformation instances: {sum(d['total_instances'] for d in feature_aggregation.values()):,}")
    print(f"  - Total transformation rules: {sum(d['total_rules'] for d in feature_aggregation.values())}")

    print(f"\n  Top 10 features by instance count:")
    for i, row in summary_df.head(10).iterrows():
        print(f"    {i+1}. {row['feature']}: {row['total_instances']} instances, "
              f"{row['total_rules']} rules")

    print(f"\n✅ Saved cross-newspaper summary: {summary_file}")

    # Save complete aggregation
    aggregation_file = output_dir / "morphological_rules_aggregated.json"
    with open(aggregation_file, 'w', encoding='utf-8') as f:
        json.dump({
            'newspapers': list(all_results.keys()),
            'feature_aggregation': dict(feature_aggregation),
            'summary_table': summary_data,
            'all_newspaper_results': all_results
        }, f, indent=2)
    print(f"✅ Saved complete aggregation: {aggregation_file}")

def main():
    print("="*80)
    print("MORPHOLOGICAL FEATURE TRANSFORMATION RULE EXTRACTION")
    print("="*80)
    print(f"\nSchema v4.0: Extracting rules for {len(MORPHOLOGICAL_FEATURES)} morphological features")
    print(f"Features: {', '.join(MORPHOLOGICAL_FEATURES[:7])}")
    print(f"         + {', '.join(MORPHOLOGICAL_FEATURES[7:])}")

    all_results = {}

    for newspaper in NEWSPAPERS:
        rules_data = extract_morphological_rules_from_events(newspaper)

        if rules_data:
            save_morphological_rules(newspaper, rules_data)
            all_results[newspaper] = rules_data

    # Cross-newspaper analysis
    if all_results:
        create_cross_newspaper_morphological_analysis(all_results)

    print(f"\n{'='*80}")
    print("✅ MORPHOLOGICAL RULE EXTRACTION COMPLETE!")
    print(f"{'='*80}")
    print(f"\n📁 Outputs saved to:")
    for newspaper in NEWSPAPERS:
        print(f"  - output/{newspaper}/morphological_analysis/")
    print(f"  - output/AGGREGATED_CROSS_NEWSPAPER/")

if __name__ == '__main__':
    main()
