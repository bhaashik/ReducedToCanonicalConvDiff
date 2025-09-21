#!/usr/bin/env python3
"""
Create comprehensive feature-value transformation visualizations
Shows specific value→value mappings for each linguistic feature
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import json
from collections import defaultdict
import matplotlib.patches as mpatches

def load_feature_value_data():
    """Load all feature-value analysis files."""
    data_dir = Path("output/GLOBAL_ANALYSIS")
    feature_files = list(data_dir.glob("global_feature_value_analysis_feature_*.csv"))

    feature_data = {}
    for file_path in feature_files:
        feature_name = file_path.stem.replace("global_feature_value_analysis_feature_", "")
        df = pd.read_csv(file_path)
        feature_data[feature_name] = df

    return feature_data

def create_transformation_matrix(feature_name, df, output_dir):
    """Create a transformation matrix heatmap for a specific feature."""
    # Get top transformations to keep visualization readable
    top_transformations = df.head(20)  # Top 20 transformations

    if len(top_transformations) == 0:
        return

    # Create matrix data
    canonical_values = top_transformations['canonical_value'].unique()
    headline_values = top_transformations['headline_value'].unique()

    # Create transformation matrix
    matrix = np.zeros((len(canonical_values), len(headline_values)))
    can_to_idx = {val: idx for idx, val in enumerate(canonical_values)}
    head_to_idx = {val: idx for idx, val in enumerate(headline_values)}

    for _, row in top_transformations.iterrows():
        can_idx = can_to_idx[row['canonical_value']]
        head_idx = head_to_idx[row['headline_value']]
        matrix[can_idx, head_idx] = row['count']

    # Create the heatmap
    plt.figure(figsize=(14, 10))

    # Use log scale for better visualization of varying counts
    matrix_log = np.log1p(matrix)  # log(1+x) to handle zeros

    ax = sns.heatmap(matrix_log,
                     xticklabels=headline_values,
                     yticklabels=canonical_values,
                     annot=matrix.astype(int),  # Show actual counts
                     fmt='d',
                     cmap='YlOrRd',
                     cbar_kws={'label': 'Transformation Count (log scale)'})

    plt.title(f'{feature_name}: Canonical→Headline Value Transformations\n'
              f'Top {len(top_transformations)} Most Frequent Patterns',
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Headline Values', fontsize=14, fontweight='bold')
    plt.ylabel('Canonical Values', fontsize=14, fontweight='bold')

    # Rotate labels for better readability
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(rotation=0, fontsize=10)

    plt.tight_layout()
    plt.savefig(output_dir / f"{feature_name}_transformation_matrix.png",
                dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Created transformation matrix for {feature_name}")

def create_transformation_flow_diagram(feature_name, df, output_dir):
    """Create a flow diagram showing transformation patterns."""
    # Get top 15 transformations
    top_transformations = df.head(15)

    if len(top_transformations) == 0:
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 10))
    fig.suptitle(f'{feature_name}: Value Transformation Patterns',
                 fontsize=18, fontweight='bold')

    # Left plot: Top transformations bar chart
    transformations = top_transformations['transformation'].tolist()
    counts = top_transformations['count'].tolist()

    colors = sns.color_palette("viridis", len(transformations))
    bars = ax1.barh(range(len(transformations)), counts, color=colors, edgecolor='black', linewidth=0.5)

    ax1.set_yticks(range(len(transformations)))
    ax1.set_yticklabels([f"{t}" for t in transformations], fontsize=9)
    ax1.set_xlabel('Frequency (Number of Transformations)', fontsize=12, fontweight='bold')
    ax1.set_title(f'Top {len(transformations)} Transformations', fontsize=14, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3, linestyle='--')

    # Add value labels on bars
    for i, (bar, count) in enumerate(zip(bars, counts)):
        ax1.text(bar.get_width() + max(counts)*0.01, bar.get_y() + bar.get_height()/2,
                f'{count:,}', ha='left', va='center', fontsize=8, fontweight='bold')

    # Right plot: Percentage distribution pie chart
    percentages = top_transformations['percentage'].tolist()
    remaining_pct = 100 - sum(percentages)

    if remaining_pct > 0:
        labels = transformations[:10] + ['Others']  # Top 10 + others
        sizes = percentages[:10] + [remaining_pct]
    else:
        labels = transformations
        sizes = percentages

    # Create pie chart with better formatting
    wedges, texts, autotexts = ax2.pie(sizes, labels=None, autopct='%1.1f%%',
                                       startangle=90, colors=colors[:len(sizes)])

    # Enhance text formatting
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(8)

    ax2.set_title('Transformation Distribution', fontsize=14, fontweight='bold')

    # Add legend with transformation labels
    ax2.legend(wedges, [f"{label[:20]}..." if len(label) > 20 else label for label in labels],
               title="Transformations", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1),
               fontsize=8)

    plt.tight_layout()
    plt.savefig(output_dir / f"{feature_name}_transformation_flow.png",
                dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Created transformation flow diagram for {feature_name}")

def create_feature_value_distribution(feature_name, df, output_dir):
    """Create value distribution analysis for a feature."""
    if len(df) == 0:
        return

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle(f'{feature_name}: Comprehensive Value Analysis',
                 fontsize=18, fontweight='bold')

    # 1. Top canonical values
    canonical_counts = df.groupby('canonical_value')['count'].sum().sort_values(ascending=False)
    top_canonical = canonical_counts.head(15)

    bars1 = ax1.bar(range(len(top_canonical)), top_canonical.values,
                    color='steelblue', edgecolor='black', linewidth=0.5)
    ax1.set_xticks(range(len(top_canonical)))
    ax1.set_xticklabels(top_canonical.index, rotation=45, ha='right', fontsize=10)
    ax1.set_title('Top Canonical Values (Source)', fontweight='bold', fontsize=12)
    ax1.set_ylabel('Total Transformations', fontweight='bold')
    ax1.grid(axis='y', alpha=0.3, linestyle='--')

    # Add value labels
    for bar, count in zip(bars1, top_canonical.values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(top_canonical)*0.01,
                f'{count:,}', ha='center', va='bottom', fontsize=8, fontweight='bold')

    # 2. Top headline values
    headline_counts = df.groupby('headline_value')['count'].sum().sort_values(ascending=False)
    top_headline = headline_counts.head(15)

    bars2 = ax2.bar(range(len(top_headline)), top_headline.values,
                    color='lightcoral', edgecolor='black', linewidth=0.5)
    ax2.set_xticks(range(len(top_headline)))
    ax2.set_xticklabels(top_headline.index, rotation=45, ha='right', fontsize=10)
    ax2.set_title('Top Headline Values (Target)', fontweight='bold', fontsize=12)
    ax2.set_ylabel('Total Transformations', fontweight='bold')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')

    # Add value labels
    for bar, count in zip(bars2, top_headline.values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(top_headline)*0.01,
                f'{count:,}', ha='center', va='bottom', fontsize=8, fontweight='bold')

    # 3. Transformation diversity (canonical values that transform to multiple targets)
    diversity_data = df.groupby('canonical_value')['headline_value'].nunique().sort_values(ascending=False)
    top_diverse = diversity_data.head(15)

    bars3 = ax3.bar(range(len(top_diverse)), top_diverse.values,
                    color='mediumseagreen', edgecolor='black', linewidth=0.5)
    ax3.set_xticks(range(len(top_diverse)))
    ax3.set_xticklabels(top_diverse.index, rotation=45, ha='right', fontsize=10)
    ax3.set_title('Most Diverse Canonical Values\n(Number of Different Target Values)',
                  fontweight='bold', fontsize=12)
    ax3.set_ylabel('Number of Target Values', fontweight='bold')
    ax3.grid(axis='y', alpha=0.3, linestyle='--')

    # Add value labels
    for bar, count in zip(bars3, top_diverse.values):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f'{count}', ha='center', va='bottom', fontsize=8, fontweight='bold')

    # 4. Concentration analysis (most frequent vs distributed transformations)
    top_20 = df.head(20)

    # Create stacked bar showing concentration
    transformation_labels = [t[:15] + "..." if len(t) > 15 else t for t in top_20['transformation']]
    counts = top_20['count']
    percentages = top_20['percentage']

    bars4 = ax4.bar(range(len(transformation_labels)), percentages,
                    color=plt.cm.viridis(np.linspace(0, 1, len(transformation_labels))),
                    edgecolor='black', linewidth=0.5)

    ax4.set_xticks(range(len(transformation_labels)))
    ax4.set_xticklabels(transformation_labels, rotation=45, ha='right', fontsize=8)
    ax4.set_title('Top 20 Transformation Concentrations', fontweight='bold', fontsize=12)
    ax4.set_ylabel('Percentage of Feature Total (%)', fontweight='bold')
    ax4.grid(axis='y', alpha=0.3, linestyle='--')

    # Add percentage labels on bars
    for bar, pct in zip(bars4, percentages):
        if pct > 1:  # Only show labels for significant percentages
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                    f'{pct:.1f}%', ha='center', va='bottom', fontsize=7, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_dir / f"{feature_name}_value_distribution.png",
                dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Created value distribution analysis for {feature_name}")

def main():
    print("="*80)
    print("CREATING COMPREHENSIVE FEATURE-VALUE VISUALIZATIONS")
    print("="*80)

    # Create output directory
    output_dir = Path("output/FEATURE_VALUE_VISUALIZATIONS")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load feature-value data
    print("Loading feature-value analysis data...")
    feature_data = load_feature_value_data()
    print(f"Found data for {len(feature_data)} features")

    # Create visualizations for each feature
    for feature_name, df in feature_data.items():
        print(f"\nProcessing {feature_name} ({len(df)} transformations)...")

        if len(df) == 0:
            print(f"  Skipping {feature_name} - no data")
            continue

        # Create all three types of visualizations
        create_transformation_matrix(feature_name, df, output_dir)
        create_transformation_flow_diagram(feature_name, df, output_dir)
        create_feature_value_distribution(feature_name, df, output_dir)

    # Create summary visualization
    create_feature_summary_comparison(feature_data, output_dir)

    print(f"\n✅ FEATURE-VALUE VISUALIZATIONS COMPLETED!")
    print(f"📁 Output directory: {output_dir}")
    print(f"📊 Total visualizations created: {len(list(output_dir.glob('*.png')))}")
    print("="*80)

def create_feature_summary_comparison(feature_data, output_dir):
    """Create summary comparison across all features."""
    print("\nCreating feature summary comparison...")

    # Collect summary statistics
    summary_stats = []
    for feature_name, df in feature_data.items():
        if len(df) == 0:
            continue

        total_transformations = df['count'].sum()
        unique_transformations = len(df)
        top_transformation_pct = df.iloc[0]['percentage'] if len(df) > 0 else 0

        summary_stats.append({
            'feature': feature_name,
            'total_transformations': total_transformations,
            'unique_types': unique_transformations,
            'top_concentration': top_transformation_pct
        })

    summary_df = pd.DataFrame(summary_stats)
    summary_df = summary_df.sort_values('total_transformations', ascending=False)

    # Create summary visualization
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle('Feature-Value Analysis Summary: All Features Comparison',
                 fontsize=18, fontweight='bold')

    # 1. Total transformations by feature
    colors = plt.cm.viridis(np.linspace(0, 1, len(summary_df)))
    bars1 = ax1.bar(range(len(summary_df)), summary_df['total_transformations'],
                    color=colors, edgecolor='black', linewidth=0.5)
    ax1.set_xticks(range(len(summary_df)))
    ax1.set_xticklabels(summary_df['feature'], rotation=45, ha='right', fontsize=10)
    ax1.set_title('Total Transformations by Feature', fontweight='bold', fontsize=14)
    ax1.set_ylabel('Number of Transformations', fontweight='bold')
    ax1.grid(axis='y', alpha=0.3, linestyle='--')

    # 2. Unique transformation types
    bars2 = ax2.bar(range(len(summary_df)), summary_df['unique_types'],
                    color=colors, edgecolor='black', linewidth=0.5)
    ax2.set_xticks(range(len(summary_df)))
    ax2.set_xticklabels(summary_df['feature'], rotation=45, ha='right', fontsize=10)
    ax2.set_title('Transformation Diversity (Unique Types)', fontweight='bold', fontsize=14)
    ax2.set_ylabel('Number of Unique Transformations', fontweight='bold')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')

    # 3. Top transformation concentration
    bars3 = ax3.bar(range(len(summary_df)), summary_df['top_concentration'],
                    color=colors, edgecolor='black', linewidth=0.5)
    ax3.set_xticks(range(len(summary_df)))
    ax3.set_xticklabels(summary_df['feature'], rotation=45, ha='right', fontsize=10)
    ax3.set_title('Top Transformation Concentration (%)', fontweight='bold', fontsize=14)
    ax3.set_ylabel('Percentage of Feature Total', fontweight='bold')
    ax3.grid(axis='y', alpha=0.3, linestyle='--')

    # 4. Diversity vs Volume scatter plot
    ax4.scatter(summary_df['total_transformations'], summary_df['unique_types'],
               c=summary_df['top_concentration'], cmap='viridis', s=100,
               edgecolors='black', linewidth=0.5)

    # Add feature labels
    for _, row in summary_df.iterrows():
        ax4.annotate(row['feature'],
                    (row['total_transformations'], row['unique_types']),
                    xytext=(5, 5), textcoords='offset points', fontsize=8)

    ax4.set_xlabel('Total Transformations', fontweight='bold')
    ax4.set_ylabel('Unique Transformation Types', fontweight='bold')
    ax4.set_title('Transformation Volume vs Diversity', fontweight='bold', fontsize=14)
    ax4.grid(alpha=0.3, linestyle='--')

    # Add colorbar for concentration
    cbar = plt.colorbar(ax4.collections[0], ax=ax4)
    cbar.set_label('Top Transformation Concentration (%)', fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_dir / "feature_value_summary_comparison.png",
                dpi=300, bbox_inches='tight')
    plt.close()

    print("Created feature summary comparison")

if __name__ == "__main__":
    main()