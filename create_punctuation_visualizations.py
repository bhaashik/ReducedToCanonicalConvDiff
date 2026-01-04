#!/usr/bin/env python3
"""
Create punctuation-specific visualizations for LaTeX
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 11

OUTPUT_DIR = Path("output/punctuation_visualizations")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

LATEX_DIR = Path("LaTeX/figures")
LATEX_DIR.mkdir(exist_ok=True, parents=True)

print("=" * 80)
print("CREATING PUNCTUATION VISUALIZATIONS")
print("=" * 80)

#==============================================================================
# FIGURE 1: Punctuation Overview - Three Features
#==============================================================================

def create_punctuation_overview():
    """Create overview of three punctuation features"""

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Left: Counts
    features = ['PUNCT-DEL', 'PUNCT-ADD', 'PUNCT-SUBST']
    counts = [4042, 1344, 618]
    colors = ['#e74c3c', '#3498db', '#2ecc71']

    bars1 = ax1.bar(features, counts, color=colors, edgecolor='black', linewidth=2)
    for bar, count in zip(bars1, counts):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 100,
                f'{count:,}\n({count/sum(counts)*100:.1f}%)',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax1.set_ylabel('Event Count', fontsize=13, fontweight='bold')
    ax1.set_title('Punctuation Transformation Distribution\n(Total: 6,004 events)',
                  fontsize=14, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    ax1.set_ylim(0, max(counts) * 1.15)

    # Right: Pie chart
    ax2.pie(counts, labels=features, autopct='%1.1f%%', colors=colors,
            startangle=90, textprops={'fontsize': 12, 'fontweight': 'bold'},
            wedgeprops={'edgecolor': 'black', 'linewidth': 2})
    ax2.set_title('Proportional Distribution\nDeletion Dominates (67%)',
                  fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "punctuation_overview.png", dpi=300, bbox_inches='tight')
    plt.savefig(LATEX_DIR / "punctuation_overview.png", dpi=300, bbox_inches='tight')
    print(f"✓ Created: punctuation_overview.png")
    plt.close()


#==============================================================================
# FIGURE 2: Deletion Breakdown
#==============================================================================

def create_deletion_breakdown():
    """Create detailed PUNCT-DEL breakdown"""

    # Data from actual CSV
    types = ['Period', 'Comma', 'Quote', 'Apostrophe', 'Hyphen',
             'Semicolon', 'Question mark', 'Colon']
    counts = [3239, 407, 154, 153, 62, 19, 7, 1]
    percentages = [80.13, 10.07, 3.81, 3.79, 1.53, 0.47, 0.17, 0.02]

    fig, ax = plt.subplots(figsize=(12, 7))

    colors = plt.cm.Reds(np.linspace(0.4, 0.9, len(types)))
    bars = ax.barh(types, counts, color=colors, edgecolor='black')

    # Add value labels
    for bar, count, pct in zip(bars, counts, percentages):
        ax.text(bar.get_width() + 80, bar.get_y() + bar.get_height()/2,
                f'{count:,} ({pct:.2f}%)', va='center', fontsize=10, fontweight='bold')

    ax.set_xlabel('Event Count', fontsize=13, fontweight='bold')
    ax.set_ylabel('Punctuation Type', fontsize=13, fontweight='bold')
    ax.set_title('PUNCT-DEL: Punctuation Deletion Breakdown\n(Total: 4,042 events, 8 types)',
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)
    ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "punctuation_deletion.png", dpi=300, bbox_inches='tight')
    plt.savefig(LATEX_DIR / "punctuation_deletion.png", dpi=300, bbox_inches='tight')
    print(f"✓ Created: punctuation_deletion.png")
    plt.close()


#==============================================================================
# FIGURE 3: Addition Breakdown
#==============================================================================

def create_addition_breakdown():
    """Create detailed PUNCT-ADD breakdown"""

    # Data from actual CSV
    types = ['Colon', 'Comma', 'Apostrophe', 'Parenthesis', 'Hyphen',
             'Semicolon', 'Slash', 'Period', 'Question mark', 'Dash']
    counts = [733, 297, 169, 70, 49, 12, 5, 5, 3, 1]
    percentages = [54.54, 22.10, 12.57, 5.21, 3.65, 0.89, 0.37, 0.37, 0.22, 0.07]

    fig, ax = plt.subplots(figsize=(12, 7))

    colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(types)))
    bars = ax.barh(types, counts, color=colors, edgecolor='black')

    # Add value labels
    for bar, count, pct in zip(bars, counts, percentages):
        ax.text(bar.get_width() + 20, bar.get_y() + bar.get_height()/2,
                f'{count} ({pct:.2f}%)', va='center', fontsize=10, fontweight='bold')

    ax.set_xlabel('Event Count', fontsize=13, fontweight='bold')
    ax.set_ylabel('Punctuation Type', fontsize=13, fontweight='bold')
    ax.set_title('PUNCT-ADD: Punctuation Addition Breakdown\n(Total: 1,344 events, 10 types)',
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)
    ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "punctuation_addition.png", dpi=300, bbox_inches='tight')
    plt.savefig(LATEX_DIR / "punctuation_addition.png", dpi=300, bbox_inches='tight')
    print(f"✓ Created: punctuation_addition.png")
    plt.close()


#==============================================================================
# FIGURE 4: Substitution Breakdown
#==============================================================================

def create_substitution_breakdown():
    """Create detailed PUNCT-SUBST breakdown"""

    # Data from actual CSV (top 10)
    transformations = [
        'that → :',
        'and → ,',
        'and → :',
        '" → says',
        ', → on',
        'and → ;',
        'for → ,',
        'or → :',
        'or → ,',
        'in → ,'
    ]
    counts = [217, 215, 104, 24, 23, 8, 4, 3, 3, 3]
    percentages = [35.11, 34.79, 16.83, 3.88, 3.72, 1.29, 0.65, 0.49, 0.49, 0.49]

    fig, ax = plt.subplots(figsize=(12, 8))

    colors = plt.cm.Greens(np.linspace(0.4, 0.9, len(transformations)))
    bars = ax.barh(transformations, counts, color=colors, edgecolor='black')

    # Add value labels
    for bar, count, pct in zip(bars, counts, percentages):
        ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
                f'{count} ({pct:.2f}%)', va='center', fontsize=10, fontweight='bold')

    ax.set_xlabel('Event Count', fontsize=13, fontweight='bold')
    ax.set_ylabel('Transformation', fontsize=13, fontweight='bold')
    ax.set_title('PUNCT-SUBST: Punctuation Substitution Patterns\n(Top 10 of 20 types, Total: 618 events)',
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)
    ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "punctuation_substitution.png", dpi=300, bbox_inches='tight')
    plt.savefig(LATEX_DIR / "punctuation_substitution.png", dpi=300, bbox_inches='tight')
    print(f"✓ Created: punctuation_substitution.png")
    plt.close()


#==============================================================================
# FIGURE 5: Combined Three-Panel View
#==============================================================================

def create_combined_view():
    """Create combined three-panel visualization"""

    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

    # Panel 1: Overview (top, spanning both columns)
    ax1 = fig.add_subplot(gs[0, :])
    features = ['PUNCT-DEL\n(4,042)', 'PUNCT-ADD\n(1,344)', 'PUNCT-SUBST\n(618)']
    counts = [4042, 1344, 618]
    colors = ['#e74c3c', '#3498db', '#2ecc71']

    bars = ax1.bar(features, counts, color=colors, edgecolor='black', linewidth=2, width=0.6)
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 100,
                f'{count/sum(counts)*100:.1f}%',
                ha='center', va='bottom', fontsize=13, fontweight='bold')

    ax1.set_ylabel('Event Count', fontsize=13, fontweight='bold')
    ax1.set_title('Punctuation Transformation Overview (Total: 6,004 events)',
                  fontsize=15, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    ax1.set_ylim(0, max(counts) * 1.15)

    # Panel 2: Deletion (bottom left)
    ax2 = fig.add_subplot(gs[1:, 0])
    del_types = ['Period', 'Comma', 'Quote', 'Apostrophe', 'Hyphen']
    del_counts = [3239, 407, 154, 153, 62]
    colors2 = plt.cm.Reds(np.linspace(0.5, 0.9, len(del_types)))

    bars2 = ax2.barh(del_types, del_counts, color=colors2, edgecolor='black')
    for bar, count in zip(bars2, del_counts):
        ax2.text(bar.get_width() + 60, bar.get_y() + bar.get_height()/2,
                f'{count:,}', va='center', fontsize=10, fontweight='bold')

    ax2.set_xlabel('Count', fontsize=12, fontweight='bold')
    ax2.set_title('PUNCT-DEL (Top 5)', fontsize=13, fontweight='bold')
    ax2.invert_yaxis()
    ax2.grid(axis='x', alpha=0.3)

    # Panel 3: Addition + Substitution (bottom right)
    ax3 = fig.add_subplot(gs[1, 1])
    add_types = ['Colon', 'Comma', 'Apostrophe', 'Parenthesis']
    add_counts = [733, 297, 169, 70]
    colors3 = plt.cm.Blues(np.linspace(0.5, 0.9, len(add_types)))

    bars3 = ax3.barh(add_types, add_counts, color=colors3, edgecolor='black')
    for bar, count in zip(bars3, add_counts):
        ax3.text(bar.get_width() + 20, bar.get_y() + bar.get_height()/2,
                f'{count}', va='center', fontsize=10, fontweight='bold')

    ax3.set_xlabel('Count', fontsize=12, fontweight='bold')
    ax3.set_title('PUNCT-ADD (Top 4)', fontsize=13, fontweight='bold')
    ax3.invert_yaxis()
    ax3.grid(axis='x', alpha=0.3)

    ax4 = fig.add_subplot(gs[2, 1])
    subst_types = ['that → :', 'and → ,', 'and → :']
    subst_counts = [217, 215, 104]
    colors4 = plt.cm.Greens(np.linspace(0.5, 0.9, len(subst_types)))

    bars4 = ax4.barh(subst_types, subst_counts, color=colors4, edgecolor='black')
    for bar, count in zip(bars4, subst_counts):
        ax4.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
                f'{count}', va='center', fontsize=10, fontweight='bold')

    ax4.set_xlabel('Count', fontsize=12, fontweight='bold')
    ax4.set_title('PUNCT-SUBST (Top 3)', fontsize=13, fontweight='bold')
    ax4.invert_yaxis()
    ax4.grid(axis='x', alpha=0.3)

    fig.suptitle('Punctuation Transformations: Comprehensive Analysis',
                 fontsize=16, fontweight='bold', y=0.98)

    plt.savefig(OUTPUT_DIR / "punctuation_combined.png", dpi=300, bbox_inches='tight')
    plt.savefig(LATEX_DIR / "punctuation_combined.png", dpi=300, bbox_inches='tight')
    print(f"✓ Created: punctuation_combined.png")
    plt.close()


#==============================================================================
# Main Execution
#==============================================================================

if __name__ == "__main__":
    print("\n[1/5] Creating punctuation overview...")
    create_punctuation_overview()

    print("\n[2/5] Creating deletion breakdown...")
    create_deletion_breakdown()

    print("\n[3/5] Creating addition breakdown...")
    create_addition_breakdown()

    print("\n[4/5] Creating substitution breakdown...")
    create_substitution_breakdown()

    print("\n[5/5] Creating combined view...")
    create_combined_view()

    print("\n" + "=" * 80)
    print("ALL PUNCTUATION VISUALIZATIONS CREATED SUCCESSFULLY")
    print("=" * 80)
    print(f"\nOutput locations:")
    print(f"  - Primary: {OUTPUT_DIR}/")
    print(f"  - LaTeX:   {LATEX_DIR}/")
    print(f"\nFiles created:")
    print(f"  1. punctuation_overview.png")
    print(f"  2. punctuation_deletion.png")
    print(f"  3. punctuation_addition.png")
    print(f"  4. punctuation_substitution.png")
    print(f"  5. punctuation_combined.png")
