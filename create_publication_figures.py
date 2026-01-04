#!/usr/bin/env python3
"""
Create publication-quality figures for ACL ARR submission
Generates missing visualizations for Task-1, Task-2, and Task-3
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(__file__))
from config import BASE_DIR

# Set publication-quality plotting parameters
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 13
sns.set_palette("husl")

def create_task1_top_features_chart():
    """Create horizontal bar chart of top 15 features for Task-1"""
    # Data from global_statistical_summary_features.csv
    features = [
        ('CONST-MOV', 30289, 24.62),
        ('DEP-REL-CHG', 26935, 21.89),
        ('CLAUSE-TYPE-CHG', 7636, 6.21),
        ('FW-DEL', 7112, 5.78),
        ('PUNCT-DEL', 4042, 3.29),
        ('H-STRUCT', 3689, 3.00),
        ('C-DEL', 2572, 2.09),
        ('C-ADD', 1430, 1.16),
        ('PUNCT-ADD', 1344, 1.09),
        ('CONST-REM', 1008, 0.82),
        ('HEAD-CHG', 760, 0.62),
        ('PUNCT-SUBST', 618, 0.50),
        ('FW-ADD', 485, 0.39),
        ('FEAT-CHG', 408, 0.33),
        ('CONST-ADD', 329, 0.27)
    ]

    df = pd.DataFrame(features, columns=['Feature', 'Count', 'Percentage'])

    fig, ax = plt.subplots(figsize=(8, 6))

    # Color punctuation features differently
    colors = ['#d62728' if 'PUNCT' in f else '#1f77b4' for f in df['Feature']]

    bars = ax.barh(df['Feature'][::-1], df['Count'][::-1], color=colors[::-1])

    ax.set_xlabel('Event Count')
    ax.set_title('Top 15 Transformation Features\n(Punctuation Features in Red)', fontweight='bold')
    ax.grid(axis='x', alpha=0.3, linestyle='--')

    # Add count labels
    for i, (count, pct) in enumerate(zip(df['Count'][::-1], df['Percentage'][::-1])):
        ax.text(count + 500, i, f'{count:,} ({pct:.1f}%)',
                va='center', fontsize=8)

    plt.tight_layout()

    output_path = BASE_DIR / 'output' / 'publication_figures' / 'task1_top_features.png'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Created: {output_path}")
    return output_path

def create_task2_newspaper_comparison():
    """Create cross-newspaper morphological comparison for Task-2"""
    # Data from morphological statistics
    newspapers = ['Times-of-India', 'Hindustan-Times', 'The-Hindu']
    verb = [74.4, 59.5, 49.3]
    noun = [1.2, 3.6, 0.0]
    other = [24.4, 36.9, 50.7]

    x = np.arange(len(newspapers))
    width = 0.25

    fig, ax = plt.subplots(figsize=(8, 5))

    bars1 = ax.bar(x - width, verb, width, label='Verb Morphology', color='#2ca02c')
    bars2 = ax.bar(x, noun, width, label='Noun Morphology', color='#ff7f0e')
    bars3 = ax.bar(x + width, other, width, label='Other', color='#9467bd')

    ax.set_ylabel('Percentage (%)')
    ax.set_title('Cross-Newspaper Morphological Transformation Patterns', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(newspapers, rotation=15, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Add percentage labels
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            if height > 2:  # Only label if significant
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}%', ha='center', va='bottom', fontsize=8)

    plt.tight_layout()

    output_path = BASE_DIR / 'output' / 'publication_figures' / 'task2_newspaper_comparison.png'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Created: {output_path}")
    return output_path

def create_task3_feature_complexity_ranking():
    """Create feature-level entropy ranking chart for Task-3"""
    # Data from Results section Table 6
    features_high = [
        ('DEP-REL-CHG', 8.35),
        ('CLAUSE-TYPE-CHG', 6.92),
        ('FEAT-CHG (Tense)', 4.22)
    ]

    features_mod = [
        ('PUNCT-SUBST', 2.29),
        ('PUNCT-ADD', 1.88),
        ('FW-DEL', 1.80)
    ]

    features_low = [
        ('PUNCT-DEL', 1.10),
        ('C-ADD', 0.85),
        ('CONST-MOV', 0.40)
    ]

    all_features = features_high + features_mod + features_low
    features, entropy = zip(*all_features)

    fig, ax = plt.subplots(figsize=(8, 6))

    # Color by complexity level
    colors = ['#d62728'] * 3 + ['#ff7f0e'] * 3 + ['#2ca02c'] * 3

    bars = ax.barh(range(len(features)), entropy, color=colors)
    ax.set_yticks(range(len(features)))
    ax.set_yticklabels(features)
    ax.set_xlabel('Entropy (bits)')
    ax.set_title('Feature-Level Complexity Hierarchy\n(Red=High, Orange=Moderate, Green=Low)',
                 fontweight='bold')
    ax.grid(axis='x', alpha=0.3, linestyle='--')

    # Add entropy values
    for i, (feat, ent) in enumerate(all_features):
        ax.text(ent + 0.15, i, f'{ent:.2f}', va='center', fontsize=8)

    plt.tight_layout()

    output_path = BASE_DIR / 'output' / 'publication_figures' / 'task3_feature_complexity.png'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Created: {output_path}")
    return output_path

def main():
    """Generate all publication figures"""
    print("Creating publication-quality figures for ACL ARR submission...")
    print("=" * 60)

    print("\n[Task-1 Figures]")
    create_task1_top_features_chart()

    print("\n[Task-2 Figures]")
    create_task2_newspaper_comparison()

    print("\n[Task-3 Figures]")
    create_task3_feature_complexity_ranking()

    print("\n" + "=" * 60)
    print("✓ All publication figures created successfully!")
    print(f"Output directory: {BASE_DIR / 'output' / 'publication_figures'}")

if __name__ == '__main__':
    main()
