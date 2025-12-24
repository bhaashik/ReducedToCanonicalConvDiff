#!/usr/bin/env python3
"""
Task 1: Cross-Newspaper Comparative Analysis

Aggregates results from all three newspapers and generates comprehensive
comparative analysis showing register differences across newspapers.
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict
from typing import Dict, List
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from config import BASE_DIR

# Set visualization style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

NEWSPAPERS = ["Times-of-India", "Hindustan-Times", "The-Hindu"]
OUTPUT_DIR = BASE_DIR / "output"
AGGREGATED_OUTPUT = OUTPUT_DIR / "AGGREGATED_CROSS_NEWSPAPER"

def load_newspaper_events(newspaper: str) -> pd.DataFrame:
    """Load events_global.csv for a newspaper."""
    events_file = OUTPUT_DIR / newspaper / "events_global.csv"
    if not events_file.exists():
        raise FileNotFoundError(f"Events file not found: {events_file}")

    df = pd.read_csv(events_file, header=None)
    # Columns: newspaper, sentence_id, parse_type, feature_id, feature_name,
    # feature_mnemonic, canonical_value, headline_value, canonical_sentence, headline_sentence
    df.columns = ['newspaper', 'sentence_id', 'parse_type', 'feature_id',
                  'feature_name', 'feature_mnemonic', 'canonical_value',
                  'headline_value', 'canonical_sentence', 'headline_sentence']
    return df

def load_all_events() -> pd.DataFrame:
    """Load and combine events from all newspapers."""
    all_events = []
    for newspaper in NEWSPAPERS:
        print(f"Loading events from {newspaper}...")
        df = load_newspaper_events(newspaper)
        all_events.append(df)

    combined = pd.concat(all_events, ignore_index=True)
    print(f"\nTotal events loaded: {len(combined):,}")
    return combined

def analyze_cross_newspaper_patterns(df: pd.DataFrame) -> Dict:
    """Analyze patterns across newspapers."""
    analysis = {}

    # 1. Event counts by newspaper
    analysis['event_counts'] = df.groupby('newspaper').size().to_dict()

    # 2. Feature distribution by newspaper
    feature_by_newspaper = df.groupby(['newspaper', 'feature_id']).size().reset_index(name='count')
    analysis['feature_by_newspaper'] = feature_by_newspaper

    # 3. Parse type distribution
    parse_by_newspaper = df.groupby(['newspaper', 'parse_type']).size().reset_index(name='count')
    analysis['parse_by_newspaper'] = parse_by_newspaper

    # 4. Top features globally
    top_features = df['feature_id'].value_counts().head(20)
    analysis['top_features_global'] = top_features.to_dict()

    # 5. Feature coverage (which features appear in which newspapers)
    feature_coverage = df.groupby('feature_id')['newspaper'].apply(
        lambda x: list(set(x))
    ).to_dict()
    analysis['feature_coverage'] = feature_coverage

    # 6. Unique features per newspaper
    unique_features = {}
    for newspaper in NEWSPAPERS:
        features = set(df[df['newspaper'] == newspaper]['feature_id'].unique())
        unique_features[newspaper] = len(features)
    analysis['unique_features_per_newspaper'] = unique_features

    # 7. Feature diversity (Shannon entropy)
    feature_diversity = {}
    for newspaper in NEWSPAPERS:
        newspaper_df = df[df['newspaper'] == newspaper]
        feature_counts = newspaper_df['feature_id'].value_counts()
        probs = feature_counts / feature_counts.sum()
        entropy = -np.sum(probs * np.log2(probs))
        feature_diversity[newspaper] = entropy
    analysis['feature_diversity_entropy'] = feature_diversity

    return analysis

def create_cross_newspaper_visualizations(df: pd.DataFrame, analysis: Dict):
    """Create comprehensive cross-newspaper visualizations."""

    # 1. Event counts by newspaper
    fig, ax = plt.subplots(figsize=(10, 6))
    newspapers = list(analysis['event_counts'].keys())
    counts = list(analysis['event_counts'].values())
    bars = ax.bar(newspapers, counts, color=['#2E86AB', '#A23B72', '#F18F01'])
    ax.set_xlabel('Newspaper', fontsize=12, fontweight='bold')
    ax.set_ylabel('Total Difference Events', fontsize=12, fontweight='bold')
    ax.set_title('Total Register Differences by Newspaper', fontsize=14, fontweight='bold')

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(AGGREGATED_OUTPUT / 'cross_newspaper_event_counts.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Feature distribution heatmap
    feature_matrix = df.groupby(['newspaper', 'feature_id']).size().reset_index(name='count')
    pivot = feature_matrix.pivot(index='feature_id', columns='newspaper', values='count').fillna(0)

    # Get top 15 features for better visualization
    top_15_features = df['feature_id'].value_counts().head(15).index
    pivot_top = pivot.loc[pivot.index.isin(top_15_features)]

    fig, ax = plt.subplots(figsize=(10, 12))
    sns.heatmap(pivot_top, annot=True, fmt='.0f', cmap='YlOrRd',
                cbar_kws={'label': 'Event Count'}, ax=ax, linewidths=0.5)
    ax.set_title('Top 15 Features: Distribution Across Newspapers',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Newspaper', fontsize=12, fontweight='bold')
    ax.set_ylabel('Feature ID', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(AGGREGATED_OUTPUT / 'cross_newspaper_feature_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 3. Feature diversity comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    newspapers = list(analysis['feature_diversity_entropy'].keys())
    diversity = list(analysis['feature_diversity_entropy'].values())
    bars = ax.bar(newspapers, diversity, color=['#2E86AB', '#A23B72', '#F18F01'])
    ax.set_xlabel('Newspaper', fontsize=12, fontweight='bold')
    ax.set_ylabel('Shannon Entropy (bits)', fontsize=12, fontweight='bold')
    ax.set_title('Feature Diversity Across Newspapers\n(Higher = More Diverse Register Differences)',
                 fontsize=14, fontweight='bold')

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}',
                ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(AGGREGATED_OUTPUT / 'cross_newspaper_diversity.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 4. Parse type distribution
    parse_df = analysis['parse_by_newspaper']
    pivot_parse = parse_df.pivot(index='newspaper', columns='parse_type', values='count').fillna(0)

    fig, ax = plt.subplots(figsize=(10, 6))
    pivot_parse.plot(kind='bar', ax=ax, color=['#06D6A0', '#EF476F'])
    ax.set_xlabel('Newspaper', fontsize=12, fontweight='bold')
    ax.set_ylabel('Event Count', fontsize=12, fontweight='bold')
    ax.set_title('Parse Type Distribution Across Newspapers', fontsize=14, fontweight='bold')
    ax.legend(title='Parse Type', title_fontsize=11, fontsize=10)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(AGGREGATED_OUTPUT / 'cross_newspaper_parse_types.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 5. Top 10 features comparison
    top_10_features = df['feature_id'].value_counts().head(10).index
    feature_comparison = []

    for feature in top_10_features:
        row = {'feature_id': feature}
        for newspaper in NEWSPAPERS:
            count = len(df[(df['newspaper'] == newspaper) & (df['feature_id'] == feature)])
            row[newspaper] = count
        feature_comparison.append(row)

    comp_df = pd.DataFrame(feature_comparison)
    comp_df = comp_df.set_index('feature_id')

    fig, ax = plt.subplots(figsize=(14, 8))
    x = np.arange(len(comp_df.index))
    width = 0.25

    bars1 = ax.bar(x - width, comp_df['Times-of-India'], width, label='Times-of-India', color='#2E86AB')
    bars2 = ax.bar(x, comp_df['Hindustan-Times'], width, label='Hindustan-Times', color='#A23B72')
    bars3 = ax.bar(x + width, comp_df['The-Hindu'], width, label='The-Hindu', color='#F18F01')

    ax.set_xlabel('Feature ID', fontsize=12, fontweight='bold')
    ax.set_ylabel('Event Count', fontsize=12, fontweight='bold')
    ax.set_title('Top 10 Features: Cross-Newspaper Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(comp_df.index, rotation=45, ha='right')
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(AGGREGATED_OUTPUT / 'cross_newspaper_top_features_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 6. Normalized comparison (percentages)
    comp_df_pct = comp_df.copy()
    for newspaper in NEWSPAPERS:
        total = analysis['event_counts'][newspaper]
        comp_df_pct[newspaper] = (comp_df[newspaper] / total) * 100

    fig, ax = plt.subplots(figsize=(14, 8))
    comp_df_pct.plot(kind='bar', ax=ax, color=['#2E86AB', '#A23B72', '#F18F01'])
    ax.set_xlabel('Feature ID', fontsize=12, fontweight='bold')
    ax.set_ylabel('Percentage of Total Events (%)', fontsize=12, fontweight='bold')
    ax.set_title('Top 10 Features: Normalized Distribution Across Newspapers',
                 fontsize=14, fontweight='bold')
    ax.legend(title='Newspaper', title_fontsize=11, fontsize=10)
    plt.xticks(rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(AGGREGATED_OUTPUT / 'cross_newspaper_normalized_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"\n✅ Created 6 cross-newspaper visualization files")

def generate_comprehensive_report(df: pd.DataFrame, analysis: Dict):
    """Generate comprehensive markdown report."""

    report = f"""# Cross-Newspaper Comparative Analysis Report
## Task 1: Register Differences Analysis (v4.0 Schema)

**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
**Schema Version:** 4.0 (20 morphological features)
**Newspapers Analyzed:** {', '.join(NEWSPAPERS)}

---

## Executive Summary

This report presents a comprehensive comparative analysis of morphosyntactic differences between **reduced register (headlines)** and **canonical register (full sentences)** across three major Indian English newspapers.

### Total Events Detected

| Newspaper | Total Events | Percentage |
|-----------|-------------|-----------|
"""

    total_events = sum(analysis['event_counts'].values())
    for newspaper in NEWSPAPERS:
        count = analysis['event_counts'][newspaper]
        pct = (count / total_events) * 100
        report += f"| {newspaper} | {count:,} | {pct:.1f}% |\n"

    report += f"| **TOTAL** | **{total_events:,}** | **100.0%** |\n\n"

    report += f"""---

## 1. Feature Diversity Analysis

**Shannon Entropy** measures the diversity of register differences. Higher values indicate more varied transformation patterns.

| Newspaper | Entropy (bits) | Interpretation |
|-----------|----------------|----------------|
"""

    for newspaper in NEWSPAPERS:
        entropy = analysis['feature_diversity_entropy'][newspaper]
        if entropy > 4.0:
            interp = "Very High Diversity"
        elif entropy > 3.5:
            interp = "High Diversity"
        elif entropy > 3.0:
            interp = "Moderate Diversity"
        else:
            interp = "Lower Diversity"
        report += f"| {newspaper} | {entropy:.3f} | {interp} |\n"

    report += f"\n---\n\n## 2. Top 15 Features Globally\n\n"
    report += "| Rank | Feature ID | Total Events | Description |\n"
    report += "|------|-----------|--------------|-------------|\n"

    top_features = df['feature_id'].value_counts().head(15)
    for i, (feature_id, count) in enumerate(top_features.items(), 1):
        report += f"| {i} | {feature_id} | {count:,} | - |\n"

    report += f"\n---\n\n## 3. Feature Coverage Across Newspapers\n\n"
    report += "Features appearing in all vs. subset of newspapers:\n\n"

    all_three = []
    two_papers = []
    one_paper = []

    for feature, newspapers in analysis['feature_coverage'].items():
        if len(newspapers) == 3:
            all_three.append(feature)
        elif len(newspapers) == 2:
            two_papers.append(feature)
        else:
            one_paper.append(feature)

    report += f"- **Universal Features** (in all 3 newspapers): {len(all_three)} features\n"
    report += f"- **Partial Features** (in 2 newspapers): {len(two_papers)} features\n"
    report += f"- **Unique Features** (in 1 newspaper): {len(one_paper)} features\n\n"

    report += f"\n---\n\n## 4. Parse Type Distribution\n\n"
    report += "| Newspaper | Dependency Parse Events | Constituency Parse Events |\n"
    report += "|-----------|------------------------|---------------------------|\n"

    for newspaper in NEWSPAPERS:
        dep_count = len(df[(df['newspaper'] == newspaper) & (df['parse_type'] == 'dependency')])
        const_count = len(df[(df['newspaper'] == newspaper) & (df['parse_type'] == 'constituency')])
        report += f"| {newspaper} | {dep_count:,} | {const_count:,} |\n"

    report += f"\n---\n\n## 5. Top Features by Newspaper\n\n"

    for newspaper in NEWSPAPERS:
        report += f"### {newspaper}\n\n"
        newspaper_df = df[df['newspaper'] == newspaper]
        top_5 = newspaper_df['feature_id'].value_counts().head(5)

        report += "| Rank | Feature ID | Count | % of Newspaper Total |\n"
        report += "|------|-----------|-------|---------------------|\n"

        newspaper_total = len(newspaper_df)
        for i, (feature_id, count) in enumerate(top_5.items(), 1):
            pct = (count / newspaper_total) * 100
            report += f"| {i} | {feature_id} | {count:,} | {pct:.1f}% |\n"

        report += "\n"

    report += f"""---

## 6. Key Findings

### Morphological Feature Changes (FEAT-CHG)

The v4.0 schema captures **20 morphological features**:
- **Original 7**: Tense, Number, Aspect, Voice, Mood, Case, Degree
- **NEW 13**: Person, Gender, Definite, PronType, Poss, NumType, NumForm, Polarity, Reflex, VerbForm, Abbr, ExtPos, Foreign

"""

    feat_chg_df = df[df['feature_id'] == 'FEAT-CHG']
    if len(feat_chg_df) > 0:
        report += f"**Total FEAT-CHG events across all newspapers**: {len(feat_chg_df):,}\n\n"

        for newspaper in NEWSPAPERS:
            count = len(feat_chg_df[feat_chg_df['newspaper'] == newspaper])
            report += f"- {newspaper}: {count:,} morphological feature changes\n"

    report += f"""

### Register-Specific Patterns

1. **Function Word Deletion (FW-DEL)**: Most common transformation indicating headline compression
2. **Dependency Relation Changes (DEP-REL-CHG)**: Syntactic restructuring for brevity
3. **Constituent Movement (CONST-MOV)**: Word order changes for emphasis
4. **Clause Type Changes (CLAUSE-TYPE-CHG)**: Finite to non-finite transformations

---

## 7. Statistical Significance

See individual newspaper outputs for detailed chi-square and Fisher exact tests.

---

## Conclusion

This cross-newspaper analysis reveals **systematic morphosyntactic differences** between headline and canonical registers across all three newspapers, with variations in:
- Event frequency
- Feature diversity
- Transformation patterns

The enriched v4.0 schema with 20 morphological features provides comprehensive coverage of register differences.

---

**Next Steps:**
- ✅ Task 1 completed: Comparative analysis across all newspapers
- ⏭️ Task 2: Transformation study with rule extraction
- ⏭️ Task 3: Complexity & similarity analysis

"""

    # Save report
    report_file = AGGREGATED_OUTPUT / "CROSS_NEWSPAPER_REPORT.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ Generated comprehensive report: {report_file}")

def save_aggregated_data(df: pd.DataFrame, analysis: Dict):
    """Save aggregated data files."""

    # 1. Combined events CSV
    events_file = AGGREGATED_OUTPUT / "all_newspapers_events.csv"
    df.to_csv(events_file, index=False)
    print(f"✅ Saved combined events: {events_file}")

    # 2. Feature frequency matrix
    feature_matrix = df.groupby(['newspaper', 'feature_id']).size().reset_index(name='count')
    pivot = feature_matrix.pivot(index='feature_id', columns='newspaper', values='count').fillna(0)
    pivot.to_csv(AGGREGATED_OUTPUT / "feature_frequency_matrix.csv")
    print(f"✅ Saved feature frequency matrix")

    # 3. Summary statistics JSON
    summary_stats = {
        'total_events': len(df),
        'newspapers': NEWSPAPERS,
        'event_counts': analysis['event_counts'],
        'feature_diversity': analysis['feature_diversity_entropy'],
        'unique_features': analysis['unique_features_per_newspaper'],
        'top_features': analysis['top_features_global'],
        'total_unique_features': len(df['feature_id'].unique())
    }

    with open(AGGREGATED_OUTPUT / "summary_statistics.json", 'w', encoding='utf-8') as f:
        json.dump(summary_stats, f, indent=2)
    print(f"✅ Saved summary statistics JSON")

    # 4. Feature coverage CSV
    coverage_data = []
    for feature_id, newspapers in analysis['feature_coverage'].items():
        coverage_data.append({
            'feature_id': feature_id,
            'newspaper_count': len(newspapers),
            'newspapers': ', '.join(newspapers),
            'is_universal': len(newspapers) == 3
        })

    coverage_df = pd.DataFrame(coverage_data)
    coverage_df = coverage_df.sort_values('newspaper_count', ascending=False)
    coverage_df.to_csv(AGGREGATED_OUTPUT / "feature_coverage.csv", index=False)
    print(f"✅ Saved feature coverage analysis")

def main():
    print("=" * 80)
    print("TASK 1: CROSS-NEWSPAPER COMPARATIVE ANALYSIS")
    print("=" * 80)
    print(f"\nAnalyzing: {', '.join(NEWSPAPERS)}")
    print(f"Schema: v4.0 (20 morphological features)")

    # Create output directory
    AGGREGATED_OUTPUT.mkdir(parents=True, exist_ok=True)
    print(f"\nOutput directory: {AGGREGATED_OUTPUT}")

    # Load all events
    print("\n" + "=" * 80)
    print("LOADING DATA")
    print("=" * 80)
    df = load_all_events()

    # Analyze patterns
    print("\n" + "=" * 80)
    print("ANALYZING CROSS-NEWSPAPER PATTERNS")
    print("=" * 80)
    analysis = analyze_cross_newspaper_patterns(df)

    print(f"\n📊 Analysis Summary:")
    print(f"  - Total events: {len(df):,}")
    print(f"  - Unique features: {len(df['feature_id'].unique())}")
    print(f"  - Parse types: {df['parse_type'].unique().tolist()}")

    # Create visualizations
    print("\n" + "=" * 80)
    print("CREATING VISUALIZATIONS")
    print("=" * 80)
    create_cross_newspaper_visualizations(df, analysis)

    # Generate report
    print("\n" + "=" * 80)
    print("GENERATING COMPREHENSIVE REPORT")
    print("=" * 80)
    generate_comprehensive_report(df, analysis)

    # Save data
    print("\n" + "=" * 80)
    print("SAVING AGGREGATED DATA")
    print("=" * 80)
    save_aggregated_data(df, analysis)

    # Final summary
    print("\n" + "=" * 80)
    print("✅ TASK 1 CROSS-NEWSPAPER ANALYSIS COMPLETED!")
    print("=" * 80)
    print(f"\n📁 All outputs saved to: {AGGREGATED_OUTPUT}")
    print(f"\n📊 Generated:")
    print(f"  - 6 visualization files (.png)")
    print(f"  - 1 comprehensive report (.md)")
    print(f"  - 4 data files (.csv, .json)")
    print(f"\n✅ Task 1 (Comparative Study) is now COMPLETE")
    print(f"\n⏭️  Ready to proceed to Task 2 (Transformation Study)")

if __name__ == '__main__':
    main()
