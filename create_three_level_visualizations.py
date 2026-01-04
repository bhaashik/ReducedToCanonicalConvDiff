#!/usr/bin/env python3
"""
Create visualizations for three-level data hierarchy
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11

OUTPUT_DIR = Path("output/three_level_visualizations")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# Create LaTeX output directory
LATEX_DIR = Path("LaTeX/figures")
LATEX_DIR.mkdir(exist_ok=True, parents=True)

print("=" * 80)
print("CREATING THREE-LEVEL DATA HIERARCHY VISUALIZATIONS")
print("=" * 80)

#==============================================================================
# FIGURE 1: Three-Level Data Hierarchy Overview
#==============================================================================

def create_hierarchy_diagram():
    """Create conceptual diagram of three-level hierarchy"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.axis('off')

    # Level 1: Features
    level1_y = 0.85
    ax.add_patch(plt.Rectangle((0.1, level1_y - 0.05), 0.8, 0.1,
                                fill=True, facecolor='#3498db', alpha=0.3, edgecolor='black', linewidth=2))
    ax.text(0.5, level1_y, 'LEVEL 1: FEATURES (30 features)',
            ha='center', va='center', fontsize=16, fontweight='bold')
    ax.text(0.5, level1_y - 0.03, 'Aggregate counts without value detail',
            ha='center', va='center', fontsize=11, style='italic')

    # Example boxes for Level 1
    examples_l1 = [
        "CONST-MOV\n30,289 events\n(24.62%)",
        "DEP-REL-CHG\n26,935 events\n(21.89%)",
        "FW-DEL\n7,112 events\n(5.78%)",
        "FEAT-CHG\n408 events\n(0.33%)"
    ]
    x_positions_l1 = [0.15, 0.35, 0.55, 0.75]
    for x, text in zip(x_positions_l1, examples_l1):
        ax.add_patch(plt.Rectangle((x - 0.06, level1_y - 0.13), 0.12, 0.08,
                                    fill=True, facecolor='#3498db', alpha=0.5, edgecolor='black'))
        ax.text(x, level1_y - 0.09, text, ha='center', va='center', fontsize=8)

    # Arrow down
    ax.annotate('', xy=(0.5, 0.5), xytext=(0.5, level1_y - 0.15),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    ax.text(0.53, 0.63, 'Drill down', fontsize=10, rotation=-90)

    # Level 2: Feature-Value Pairs
    level2_y = 0.48
    ax.add_patch(plt.Rectangle((0.1, level2_y - 0.08), 0.8, 0.16,
                                fill=True, facecolor='#2ecc71', alpha=0.3, edgecolor='black', linewidth=2))
    ax.text(0.5, level2_y + 0.05, 'LEVEL 2: FEATURE-VALUE PAIRS (5,000+ transformations)',
            ha='center', va='center', fontsize=16, fontweight='bold')
    ax.text(0.5, level2_y + 0.02, 'Specific canonical → headline transformations',
            ha='center', va='center', fontsize=11, style='italic')

    # Example boxes for Level 2 (showing FEAT-CHG breakdown)
    examples_l2 = [
        "Tense=Past→\nTense=Pres\n115 (28%)",
        "Number=ABSENT→\nNumber=Sing\n26 (6%)",
        "Number=Plur→\nNumber=Sing\n26 (6%)",
        "Person=ABSENT→\nPerson=3\n22 (5%)"
    ]
    x_positions_l2 = [0.15, 0.35, 0.55, 0.75]
    for x, text in zip(x_positions_l2, examples_l2):
        ax.add_patch(plt.Rectangle((x - 0.06, level2_y - 0.06), 0.12, 0.08,
                                    fill=True, facecolor='#2ecc71', alpha=0.5, edgecolor='black'))
        ax.text(x, level2_y - 0.02, text, ha='center', va='center', fontsize=7)

    ax.text(0.5, level2_y - 0.09, '(FEAT-CHG: 408 events across 45 transformation types)',
            ha='center', va='center', fontsize=9, style='italic', color='#27ae60')

    # Arrow down
    ax.annotate('', xy=(0.5, 0.1), xytext=(0.5, level2_y - 0.11),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    ax.text(0.53, 0.25, 'Aggregate statistics', fontsize=10, rotation=-90)

    # Level 3: Value Statistics
    level3_y = 0.08
    ax.add_patch(plt.Rectangle((0.1, level3_y - 0.05), 0.8, 0.1,
                                fill=True, facecolor='#e74c3c', alpha=0.3, edgecolor='black', linewidth=2))
    ax.text(0.5, level3_y, 'LEVEL 3: VALUE STATISTICS (30 features)',
            ha='center', va='center', fontsize=16, fontweight='bold')
    ax.text(0.5, level3_y - 0.03, 'Entropy, diversity, concentration metrics',
            ha='center', va='center', fontsize=11, style='italic')

    # Example boxes for Level 3
    examples_l3 = [
        "FEAT-CHG\n45 types\n4.22 bits",
        "FW-DEL\n6 types\n2.01 bits",
        "DEP-REL-CHG\n1,023 types\n8.35 bits",
        "CONST-MOV\n2 types\n0.40 bits"
    ]
    for x, text in zip(x_positions_l1, examples_l3):
        ax.add_patch(plt.Rectangle((x - 0.06, level3_y - 0.06), 0.12, 0.05,
                                    fill=True, facecolor='#e74c3c', alpha=0.5, edgecolor='black'))
        ax.text(x, level3_y - 0.035, text, ha='center', va='center', fontsize=7)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "three_level_hierarchy.png", dpi=300, bbox_inches='tight')
    plt.savefig(LATEX_DIR / "three_level_hierarchy.png", dpi=300, bbox_inches='tight')
    print(f"✓ Created: {OUTPUT_DIR}/three_level_hierarchy.png")
    plt.close()


#==============================================================================
# FIGURE 2: Feature Frequency (Level 1)
#==============================================================================

def create_level1_visualization():
    """Create Level 1 feature frequency visualization"""

    # Load GLOBAL data
    df = pd.read_csv("output/GLOBAL_ANALYSIS/global_statistical_summary_features.csv")

    # Top 15 features
    df_top = df.head(15).copy()

    fig, ax = plt.subplots(figsize=(12, 8))

    colors = plt.cm.Set3(np.linspace(0, 1, len(df_top)))
    bars = ax.barh(df_top['feature_id'], df_top['total_occurrences'], color=colors, edgecolor='black')

    # Add value labels
    for i, (bar, count, pct) in enumerate(zip(bars, df_top['total_occurrences'], df_top['percentage_of_total'])):
        ax.text(bar.get_width() + 500, bar.get_y() + bar.get_height()/2,
                f'{count:,} ({pct:.1f}%)', va='center', fontsize=9)

    ax.set_xlabel('Event Count', fontsize=13, fontweight='bold')
    ax.set_ylabel('Feature (Mnemonic)', fontsize=13, fontweight='bold')
    ax.set_title('LEVEL 1: Feature Frequency Distribution\nTop 15 Features (Total: 123,042 events)',
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)
    ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "level1_feature_frequency.png", dpi=300, bbox_inches='tight')
    plt.savefig(LATEX_DIR / "level1_feature_frequency.png", dpi=300, bbox_inches='tight')
    print(f"✓ Created: {OUTPUT_DIR}/level1_feature_frequency.png")
    plt.close()


#==============================================================================
# FIGURE 3: Feature-Value Pairs (Level 2) - FEAT-CHG Example
#==============================================================================

def create_level2_visualization():
    """Create Level 2 feature-value pair visualization for FEAT-CHG"""

    # Load FEAT-CHG data
    df = pd.read_csv("output/GLOBAL_ANALYSIS/global_feature_value_analysis_feature_FEAT-CHG.csv")

    # Top 15 transformations
    df_top = df.head(15).copy()

    fig, ax = plt.subplots(figsize=(14, 8))

    colors = plt.cm.Paired(np.linspace(0, 1, len(df_top)))
    bars = ax.barh(df_top['transformation'], df_top['count'], color=colors, edgecolor='black')

    # Add value labels
    for bar, count, pct in zip(bars, df_top['count'], df_top['percentage']):
        ax.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height()/2,
                f'{count} ({pct:.1f}%)', va='center', fontsize=9)

    ax.set_xlabel('Event Count', fontsize=13, fontweight='bold')
    ax.set_ylabel('Transformation (Canonical → Headline)', fontsize=13, fontweight='bold')
    ax.set_title('LEVEL 2: Feature-Value Pairs for FEAT-CHG\nTop 15 Morphological Transformations (Total: 408 events, 45 types)',
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)
    ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "level2_featchange_transformations.png", dpi=300, bbox_inches='tight')
    plt.savefig(LATEX_DIR / "level2_featchange_transformations.png", dpi=300, bbox_inches='tight')
    print(f"✓ Created: {OUTPUT_DIR}/level2_featchange_transformations.png")
    plt.close()


#==============================================================================
# FIGURE 4: Value Statistics (Level 3) - Entropy Comparison
#==============================================================================

def create_level3_visualization():
    """Create Level 3 entropy and diversity visualization"""

    # Load value statistics
    df = pd.read_csv("output/GLOBAL_ANALYSIS/global_feature_value_analysis_value_statistics.csv")

    # Select interesting features
    df = df.sort_values('transformation_entropy', ascending=False).head(15)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Entropy plot
    colors_entropy = plt.cm.viridis(df['transformation_entropy'] / df['transformation_entropy'].max())
    bars1 = ax1.barh(df['feature_id'], df['transformation_entropy'], color=colors_entropy, edgecolor='black')

    for bar, ent in zip(bars1, df['transformation_entropy']):
        ax1.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                f'{ent:.2f}', va='center', fontsize=9)

    ax1.set_xlabel('Shannon Entropy (bits)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Feature', fontsize=12, fontweight='bold')
    ax1.set_title('Transformation Entropy\n(Higher = More Unpredictable)', fontsize=13, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    ax1.invert_yaxis()

    # Diversity plot
    colors_div = plt.cm.plasma(df['unique_transformation_types'] / df['unique_transformation_types'].max())
    bars2 = ax2.barh(df['feature_id'], df['unique_transformation_types'], color=colors_div, edgecolor='black')

    for bar, types in zip(bars2, df['unique_transformation_types']):
        ax2.text(bar.get_width() + 15, bar.get_y() + bar.get_height()/2,
                f'{int(types)}', va='center', fontsize=9)

    ax2.set_xlabel('Unique Transformation Types', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Feature', fontsize=12, fontweight='bold')
    ax2.set_title('Transformation Diversity\n(Number of Unique Types)', fontsize=13, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)
    ax2.invert_yaxis()

    fig.suptitle('LEVEL 3: Value Statistics - Entropy and Diversity',
                 fontsize=15, fontweight='bold', y=0.98)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "level3_entropy_diversity.png", dpi=300, bbox_inches='tight')
    plt.savefig(LATEX_DIR / "level3_entropy_diversity.png", dpi=300, bbox_inches='tight')
    print(f"✓ Created: {OUTPUT_DIR}/level3_entropy_diversity.png")
    plt.close()


#==============================================================================
# FIGURE 5: Cross-Level Comparison
#==============================================================================

def create_cross_level_comparison():
    """Create visualization comparing same information across levels"""

    fig, axes = plt.subplots(3, 1, figsize=(14, 12))

    # Example: FEAT-CHG across three levels

    # Level 1: Just the count
    ax1 = axes[0]
    ax1.bar(['FEAT-CHG'], [408], color='#3498db', edgecolor='black', width=0.3)
    ax1.set_ylabel('Event Count', fontsize=12, fontweight='bold')
    ax1.set_title('LEVEL 1: Feature Count\n"How many FEAT-CHG events?"',
                  fontsize=13, fontweight='bold')
    ax1.text(0, 408 + 10, '408 events\n(0.33% of total)', ha='center', fontsize=11)
    ax1.set_ylim(0, 500)
    ax1.grid(axis='y', alpha=0.3)

    # Level 2: Top transformations
    ax2 = axes[1]
    transformations = ['Tense=Past→Pres', 'Num=ABSENT→Sing', 'Num=Plur→Sing',
                       'Person=ABSENT→3', 'Mood=ABSENT→Ind', 'Others (40)']
    counts = [115, 26, 26, 22, 22, 197]
    colors = ['#2ecc71'] * 5 + ['#95a5a6']

    bars = ax2.barh(transformations, counts, color=colors, edgecolor='black')
    for bar, count in zip(bars, counts):
        ax2.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                f'{count}', va='center', fontsize=10)

    ax2.set_xlabel('Event Count', fontsize=12, fontweight='bold')
    ax2.set_title('LEVEL 2: Feature-Value Pairs\n"What specific transformations occur?"',
                  fontsize=13, fontweight='bold')
    ax2.invert_yaxis()
    ax2.grid(axis='x', alpha=0.3)

    # Level 3: Statistics
    ax3 = axes[2]
    stats = ['Unique\nTypes', 'Canonical\nDiversity', 'Headline\nDiversity',
             'Entropy\n(bits)', 'Top-3\nConcentration']
    values = [45, 29, 28, 4.22, 0.41]
    colors3 = plt.cm.Reds(np.linspace(0.3, 0.9, len(stats)))

    bars = ax3.bar(stats, values, color=colors3, edgecolor='black')
    for bar, val in zip(bars, values):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val:.1f}' if val < 10 else f'{int(val)}',
                ha='center', fontsize=10, fontweight='bold')

    ax3.set_ylabel('Value', fontsize=12, fontweight='bold')
    ax3.set_title('LEVEL 3: Statistical Properties\n"What are the distributional characteristics?"',
                  fontsize=13, fontweight='bold')
    ax3.grid(axis='y', alpha=0.3)

    fig.suptitle('Cross-Level Comparison: FEAT-CHG Analysis',
                 fontsize=16, fontweight='bold', y=0.995)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "cross_level_comparison.png", dpi=300, bbox_inches='tight')
    plt.savefig(LATEX_DIR / "cross_level_comparison.png", dpi=300, bbox_inches='tight')
    print(f"✓ Created: {OUTPUT_DIR}/cross_level_comparison.png")
    plt.close()


#==============================================================================
# Main Execution
#==============================================================================

if __name__ == "__main__":
    print("\n[1/5] Creating hierarchy diagram...")
    create_hierarchy_diagram()

    print("\n[2/5] Creating Level 1 visualization...")
    create_level1_visualization()

    print("\n[3/5] Creating Level 2 visualization...")
    create_level2_visualization()

    print("\n[4/5] Creating Level 3 visualization...")
    create_level3_visualization()

    print("\n[5/5] Creating cross-level comparison...")
    create_cross_level_comparison()

    print("\n" + "=" * 80)
    print("ALL VISUALIZATIONS CREATED SUCCESSFULLY")
    print("=" * 80)
    print(f"\nOutput locations:")
    print(f"  - Primary: {OUTPUT_DIR}/")
    print(f"  - LaTeX:   {LATEX_DIR}/")
    print(f"\nFiles created:")
    print(f"  1. three_level_hierarchy.png")
    print(f"  2. level1_feature_frequency.png")
    print(f"  3. level2_featchange_transformations.png")
    print(f"  4. level3_entropy_diversity.png")
    print(f"  5. cross_level_comparison.png")
    print("\nThese figures are ready for inclusion in LaTeX documents.")
