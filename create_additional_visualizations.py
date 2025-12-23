"""
Additional Visualizations: Create enhanced comparative and analytical plots.

Creates:
1. Systematicity comparison across granularities
2. Rule efficiency analysis (accuracy vs coverage)
3. Feature-level performance heatmaps
4. Tier contribution breakdown
5. Cross-newspaper systematicity comparison
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import Dict, List, Any


def create_systematicity_comparison(newspapers: List[str], output_dir: Path):
    """Create bar chart comparing systematicity across granularities and newspapers."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Collect data
    data = []
    for newspaper in newspapers:
        sys_file = Path(f"output/{newspaper}/rule_analysis/enhanced_systematicity.json")
        if not sys_file.exists():
            print(f"⚠️  Skipping {newspaper} - no systematicity data")
            continue

        with open(sys_file, 'r') as f:
            sys_data = json.load(f)

        for gran_name, gran_data in sys_data['by_granularity'].items():
            data.append({
                'Newspaper': newspaper,
                'Granularity': gran_name.title(),
                'Deterministic (%)': gran_data['deterministic_percentage'],
                'Systematic (%)': gran_data['systematic_percentage']
            })

    if not data:
        print("⚠️  No data available for systematicity comparison")
        return

    df = pd.DataFrame(data)

    # Create grouped bar chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Plot 1: Deterministic percentage
    granularities = ['Minimal', 'Lexical', 'Syntactic', 'Phrasal', 'Full']
    x = np.arange(len(granularities))
    width = 0.25

    for i, newspaper in enumerate(newspapers):
        news_data = df[df['Newspaper'] == newspaper]
        if news_data.empty:
            continue
        values = [news_data[news_data['Granularity'] == g]['Deterministic (%)'].values[0]
                  if not news_data[news_data['Granularity'] == g].empty else 0
                  for g in granularities]
        ax1.bar(x + i*width, values, width, label=newspaper)

    ax1.set_xlabel('Context Granularity', fontweight='bold', fontsize=12)
    ax1.set_ylabel('Deterministic (%)', fontweight='bold', fontsize=12)
    ax1.set_title('Systematicity Across Granularities', fontweight='bold', fontsize=14)
    ax1.set_xticks(x + width)
    ax1.set_xticklabels(granularities, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    ax1.axhline(y=74.3, color='red', linestyle='--', alpha=0.5, label='Lexical optimum')

    # Plot 2: Pattern counts
    for i, newspaper in enumerate(newspapers):
        news_data = df[df['Newspaper'] == newspaper]
        if news_data.empty:
            continue
        # Get pattern counts from systematicity data
        sys_file = Path(f"output/{newspaper}/rule_analysis/enhanced_systematicity.json")
        with open(sys_file, 'r') as f:
            sys_data = json.load(f)

        pattern_counts = [sys_data['by_granularity'][g.lower()]['total_patterns']
                         for g in granularities]
        ax2.plot(granularities, pattern_counts, marker='o', linewidth=2,
                markersize=8, label=newspaper)

    ax2.set_xlabel('Context Granularity', fontweight='bold', fontsize=12)
    ax2.set_ylabel('Total Patterns', fontweight='bold', fontsize=12)
    ax2.set_title('Pattern Fragmentation by Granularity', fontweight='bold', fontsize=14)
    ax2.set_xticklabels(granularities, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_yscale('log')

    plt.tight_layout()
    plt.savefig(output_dir / 'systematicity_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✅ Saved systematicity comparison to: {output_dir / 'systematicity_comparison.png'}")


def create_rule_efficiency_plot(newspapers: List[str], output_dir: Path):
    """Create plot showing rule efficiency (accuracy vs coverage vs rule count)."""

    output_dir = Path(output_dir)

    fig, axes = plt.subplots(1, len(newspapers), figsize=(6*len(newspapers), 5))
    if len(newspapers) == 1:
        axes = [axes]

    for ax, newspaper in zip(axes, newspapers):
        eval_file = Path(f"output/{newspaper}/rule_analysis/evaluation/engine_statistics.json")
        if not eval_file.exists():
            ax.text(0.5, 0.5, f'No data for\n{newspaper}',
                   ha='center', va='center', fontsize=12)
            ax.set_title(newspaper, fontweight='bold')
            continue

        with open(eval_file, 'r') as f:
            stats = json.load(f)

        # Create data for visualization
        tiers = ['Lexical', 'Syntactic', 'Default', 'No Rule']
        hits = [stats['lexical_hits'], stats['syntactic_hits'],
                stats['default_hits'], stats['no_rule']]
        total = stats['total_events']
        coverages = [h/total*100 for h in hits]

        # Get accuracies by tier from feature analysis
        feat_file = Path(f"output/{newspaper}/rule_analysis/evaluation/feature_analysis.csv")
        if feat_file.exists():
            feat_df = pd.DataFrame(pd.read_csv(feat_file))

            # Calculate accuracy by tier
            tier_accs = []
            for tier in ['lexical', 'syntactic', 'default', 'none']:
                tier_col = f"{tier}_hits"
                if tier_col in feat_df.columns:
                    tier_events = feat_df[tier_col].sum()
                    if tier_events > 0:
                        # Weighted accuracy
                        tier_correct = 0
                        for _, row in feat_df.iterrows():
                            if row[tier_col] > 0:
                                acc = float(row['accuracy'].rstrip('%')) / 100
                                tier_correct += row[tier_col] * acc
                        tier_accs.append(tier_correct / tier_events * 100)
                    else:
                        tier_accs.append(0)
                else:
                    tier_accs.append(0)
        else:
            tier_accs = [0, 0, 0, 0]

        # Create bubble chart
        colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
        for i, (tier, cov, acc) in enumerate(zip(tiers, coverages, tier_accs)):
            ax.scatter(cov, acc, s=hits[i]/10, c=colors[i], alpha=0.6,
                      edgecolors='black', linewidth=2, label=f'{tier} ({hits[i]:,} events)')

        ax.set_xlabel('Coverage (%)', fontweight='bold', fontsize=11)
        ax.set_ylabel('Accuracy (%)', fontweight='bold', fontsize=11)
        ax.set_title(f'{newspaper}\nRule Tier Efficiency', fontweight='bold', fontsize=12)
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-5, max(coverages) + 10)
        ax.set_ylim(-5, 105)

    plt.tight_layout()
    plt.savefig(output_dir / 'rule_efficiency.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✅ Saved rule efficiency plot to: {output_dir / 'rule_efficiency.png'}")


def create_feature_heatmap(newspaper: str, output_dir: Path):
    """Create heatmap showing performance by feature and rule tier."""

    output_dir = Path(output_dir)

    feat_file = Path(f"output/{newspaper}/rule_analysis/evaluation/feature_analysis.csv")
    if not feat_file.exists():
        print(f"⚠️  No feature analysis for {newspaper}")
        return

    df = pd.read_csv(feat_file)

    # Select top features by volume
    df = df.nlargest(15, 'total')

    # Create heatmap data
    heatmap_data = df[['lexical_hits', 'syntactic_hits', 'default_hits', 'no_rule_hits']].values
    features = df['feature_id'].values

    fig, ax = plt.subplots(figsize=(10, 8))

    im = ax.imshow(heatmap_data, cmap='YlOrRd', aspect='auto')

    ax.set_xticks(np.arange(4))
    ax.set_yticks(np.arange(len(features)))
    ax.set_xticklabels(['Lexical', 'Syntactic', 'Default', 'No Rule'])
    ax.set_yticklabels(features)

    # Annotate cells
    for i in range(len(features)):
        for j in range(4):
            text = ax.text(j, i, f'{int(heatmap_data[i, j]):,}',
                          ha="center", va="center", color="black", fontsize=8)

    ax.set_title(f'{newspaper}: Rule Tier Usage by Feature\n(Top 15 Features by Volume)',
                fontweight='bold', fontsize=14)
    ax.set_xlabel('Rule Tier', fontweight='bold', fontsize=12)
    ax.set_ylabel('Feature', fontweight='bold', fontsize=12)

    plt.colorbar(im, ax=ax, label='Event Count')
    plt.tight_layout()
    plt.savefig(output_dir / f'feature_heatmap_{newspaper}.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✅ Saved feature heatmap to: {output_dir / f'feature_heatmap_{newspaper}.png'}")


def create_tier_contribution_pie(newspapers: List[str], output_dir: Path):
    """Create pie charts showing tier contribution to overall accuracy."""

    output_dir = Path(output_dir)

    fig, axes = plt.subplots(1, len(newspapers), figsize=(6*len(newspapers), 5))
    if len(newspapers) == 1:
        axes = [axes]

    for ax, newspaper in zip(axes, newspapers):
        eval_file = Path(f"output/{newspaper}/rule_analysis/evaluation/engine_statistics.json")
        if not eval_file.exists():
            continue

        with open(eval_file, 'r') as f:
            stats = json.load(f)

        # Calculate contribution to correct predictions
        feat_file = Path(f"output/{newspaper}/rule_analysis/evaluation/feature_analysis.csv")
        if feat_file.exists():
            feat_df = pd.read_csv(feat_file)

            contributions = []
            for tier in ['lexical', 'syntactic', 'default', 'none']:
                tier_col = f"{tier}_hits"
                if tier_col in feat_df.columns:
                    tier_correct = 0
                    for _, row in feat_df.iterrows():
                        if row[tier_col] > 0:
                            acc = float(row['accuracy'].rstrip('%')) / 100
                            tier_correct += row[tier_col] * acc
                    contributions.append(tier_correct)
                else:
                    contributions.append(0)
        else:
            contributions = [0, 0, 0, 0]

        # Create pie chart
        labels = ['Lexical', 'Syntactic', 'Default', 'No Rule']
        colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']

        wedges, texts, autotexts = ax.pie(contributions, labels=labels, colors=colors,
                                          autopct='%1.1f%%', startangle=90)

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        ax.set_title(f'{newspaper}\nContribution to Correct Predictions',
                    fontweight='bold', fontsize=12)

    plt.tight_layout()
    plt.savefig(output_dir / 'tier_contributions.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✅ Saved tier contribution chart to: {output_dir / 'tier_contributions.png'}")


def main():
    """Create all additional visualizations."""

    newspapers = ["Times-of-India", "Hindustan-Times", "The-Hindu"]
    output_dir = Path("output/additional_visualizations")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*80)
    print("CREATING ADDITIONAL VISUALIZATIONS")
    print("="*80)

    # Check which newspapers have data
    available = []
    for newspaper in newspapers:
        if Path(f"output/{newspaper}/rule_analysis").exists():
            available.append(newspaper)

    if not available:
        print("\n⚠️  No newspaper data available yet. Run analysis first.")
        return

    print(f"\nCreating visualizations for: {', '.join(available)}")

    # 1. Systematicity comparison
    print("\n1. Creating systematicity comparison...")
    create_systematicity_comparison(available, output_dir)

    # 2. Rule efficiency
    print("2. Creating rule efficiency plot...")
    create_rule_efficiency_plot(available, output_dir)

    # 3. Feature heatmaps
    print("3. Creating feature heatmaps...")
    for newspaper in available:
        create_feature_heatmap(newspaper, output_dir)

    # 4. Tier contribution pies
    print("4. Creating tier contribution charts...")
    create_tier_contribution_pie(available, output_dir)

    print(f"\n{'='*80}")
    print("ADDITIONAL VISUALIZATIONS COMPLETE")
    print(f"{'='*80}")
    print(f"\nAll visualizations saved to: {output_dir}")


if __name__ == "__main__":
    main()
