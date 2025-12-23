#!/usr/bin/env python3
"""
Create enhanced summary visualizations for correlation analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def create_significance_summary(output_dir: Path):
    """Create visual summary of significant correlations."""

    # Data from correlation analysis
    correlations = [
        {'Metric': 'ROUGE-1', 'Measure': 'Entropy', 'r': -0.923, 'p': 0.0086, 'R2': 0.853},
        {'Metric': 'ROUGE-1', 'Measure': 'Perplexity', 'r': -0.917, 'p': 0.0100, 'R2': 0.841},
        {'Metric': 'ROUGE-2', 'Measure': 'Norm. PP', 'r': -0.897, 'p': 0.0155, 'R2': 0.804},
        {'Metric': 'ROUGE-L', 'Measure': 'Perplexity', 'r': -0.775, 'p': 0.0703, 'R2': 0.601},
        {'Metric': 'ROUGE-L', 'Measure': 'Entropy', 'r': -0.769, 'p': 0.0737, 'R2': 0.592},
        {'Metric': 'METEOR', 'Measure': 'Norm. PP', 'r': -0.707, 'p': 0.1160, 'R2': 0.500},
        {'Metric': 'METEOR', 'Measure': 'Entropy', 'r': -0.692, 'p': 0.1274, 'R2': 0.479},
        {'Metric': 'METEOR', 'Measure': 'Perplexity', 'r': -0.664, 'p': 0.1502, 'R2': 0.441},
    ]

    df = pd.DataFrame(correlations)

    # Create figure with 2 panels
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Panel 1: Correlation strength with significance markers
    ax1 = axes[0]

    # Create labels
    labels = [f"{row['Metric']}\nvs\n{row['Measure']}" for _, row in df.iterrows()]
    y_pos = np.arange(len(labels))

    # Color by significance
    colors = []
    for _, row in df.iterrows():
        if row['p'] < 0.01:
            colors.append('darkred')
        elif row['p'] < 0.05:
            colors.append('red')
        elif row['p'] < 0.10:
            colors.append('orange')
        else:
            colors.append('gray')

    # Horizontal bar chart
    bars = ax1.barh(y_pos, df['r'].abs(), color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)

    # Add r values on bars
    for i, (_, row) in enumerate(df.iterrows()):
        ax1.text(row['r']/2 if row['r'] < 0 else -row['r']/2, i,
                f"r={row['r']:.3f}",
                ha='center', va='center', fontsize=10, weight='bold', color='white')

    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(labels, fontsize=9)
    ax1.set_xlabel('|Pearson Correlation Coefficient|', fontsize=12, weight='bold')
    ax1.set_title('Correlation Strength with Significance\n(Negative correlations shown as absolute values)',
                  fontsize=13, weight='bold', pad=15)
    ax1.axvline(x=0.7, color='blue', linestyle='--', linewidth=2, alpha=0.5, label='Strong (|r|>0.7)')
    ax1.axvline(x=0.5, color='green', linestyle='--', linewidth=2, alpha=0.5, label='Moderate (|r|>0.5)')
    ax1.set_xlim(0, 1.0)
    ax1.grid(axis='x', alpha=0.3)

    # Legend for colors
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='darkred', edgecolor='black', label='p < 0.01 (highly sig.)'),
        Patch(facecolor='red', edgecolor='black', label='p < 0.05 (significant)'),
        Patch(facecolor='orange', edgecolor='black', label='p < 0.10 (marginal)'),
        Patch(facecolor='gray', edgecolor='black', label='p ≥ 0.10 (not sig.)')
    ]
    ax1.legend(handles=legend_elements, loc='lower right', fontsize=9)

    # Panel 2: Variance explained (R²)
    ax2 = axes[1]

    # Create stacked bar showing explained vs unexplained variance
    explained = df['R2'] * 100
    unexplained = 100 - explained

    y_pos = np.arange(len(labels))

    # Stacked bars
    p1 = ax2.barh(y_pos, explained, color='steelblue', alpha=0.8, edgecolor='black', linewidth=1.5, label='Explained')
    p2 = ax2.barh(y_pos, unexplained, left=explained, color='lightgray', alpha=0.6, edgecolor='black', linewidth=1.5, label='Unexplained')

    # Add percentage labels
    for i, r2 in enumerate(explained):
        ax2.text(r2/2, i, f'{r2:.1f}%', ha='center', va='center', fontsize=10, weight='bold', color='white')

    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(labels, fontsize=9)
    ax2.set_xlabel('Variance Explained (%)', fontsize=12, weight='bold')
    ax2.set_title('Variance Explained (R²)\nHow much MT performance is predicted by perplexity?',
                  fontsize=13, weight='bold', pad=15)
    ax2.set_xlim(0, 100)
    ax2.axvline(x=50, color='red', linestyle='--', linewidth=2, alpha=0.5, label='50% threshold')
    ax2.legend(loc='lower right', fontsize=9)
    ax2.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'correlation_significance_summary.png', dpi=200, bbox_inches='tight')
    plt.close()

    print(f"Created: {output_dir / 'correlation_significance_summary.png'}")

def create_complexity_performance_comparison(output_dir: Path):
    """Create side-by-side comparison of complexity and performance by direction."""

    # Data from merged analysis
    data = {
        'Newspaper': ['ToI', 'HT', 'Hindu', 'ToI', 'HT', 'Hindu'],
        'Direction': ['H2C', 'H2C', 'H2C', 'C2H', 'C2H', 'C2H'],
        'Perplexity': [116.22, 124.92, 85.72, 70.03, 57.46, 53.35],
        'Entropy': [6.86, 6.96, 6.42, 6.13, 5.84, 5.74],
        'METEOR': [0.628, 0.566, 0.499, 0.765, 0.729, 0.733],
        'ROUGE-1': [0.804, 0.789, 0.840, 0.857, 0.851, 0.909],
        'ROUGE-L': [0.764, 0.728, 0.822, 0.807, 0.784, 0.891]
    }

    df = pd.DataFrame(data)

    # Create 2x2 grid
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Panel 1: Perplexity by Direction
    ax1 = axes[0, 0]
    x = np.arange(3)
    width = 0.35

    h2c_pp = df[df['Direction'] == 'H2C']['Perplexity'].values
    c2h_pp = df[df['Direction'] == 'C2H']['Perplexity'].values

    bars1 = ax1.bar(x - width/2, h2c_pp, width, label='H2C (Expansion)', color='red', alpha=0.7, edgecolor='black')
    bars2 = ax1.bar(x + width/2, c2h_pp, width, label='C2H (Reduction)', color='blue', alpha=0.7, edgecolor='black')

    ax1.set_ylabel('Perplexity', fontsize=12, weight='bold')
    ax1.set_xlabel('Newspaper', fontsize=12, weight='bold')
    ax1.set_title('Complexity: Perplexity by Direction\n(Higher = More Complex)', fontsize=13, weight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(['Times-of-India', 'Hindustan-Times', 'The-Hindu'])
    ax1.legend(fontsize=10)
    ax1.grid(axis='y', alpha=0.3)

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}',
                    ha='center', va='bottom', fontsize=9, weight='bold')

    # Panel 2: METEOR by Direction
    ax2 = axes[0, 1]

    h2c_meteor = df[df['Direction'] == 'H2C']['METEOR'].values
    c2h_meteor = df[df['Direction'] == 'C2H']['METEOR'].values

    bars1 = ax2.bar(x - width/2, h2c_meteor, width, label='H2C (Expansion)', color='red', alpha=0.7, edgecolor='black')
    bars2 = ax2.bar(x + width/2, c2h_meteor, width, label='C2H (Reduction)', color='blue', alpha=0.7, edgecolor='black')

    ax2.set_ylabel('METEOR Score', fontsize=12, weight='bold')
    ax2.set_xlabel('Newspaper', fontsize=12, weight='bold')
    ax2.set_title('Performance: METEOR by Direction\n(Higher = Better)', fontsize=13, weight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(['Times-of-India', 'Hindustan-Times', 'The-Hindu'])
    ax2.legend(fontsize=10)
    ax2.set_ylim(0, 1.0)
    ax2.grid(axis='y', alpha=0.3)

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}',
                    ha='center', va='bottom', fontsize=9, weight='bold')

    # Panel 3: Complexity-Performance Scatter (H2C)
    ax3 = axes[1, 0]

    h2c_data = df[df['Direction'] == 'H2C']
    ax3.scatter(h2c_data['Perplexity'], h2c_data['METEOR'], s=200, alpha=0.7,
               color='red', edgecolors='black', linewidth=2, label='H2C')

    # Add newspaper labels
    for _, row in h2c_data.iterrows():
        ax3.annotate(row['Newspaper'], (row['Perplexity'], row['METEOR']),
                    xytext=(5, 5), textcoords='offset points', fontsize=9)

    # Regression line
    z = np.polyfit(h2c_data['Perplexity'], h2c_data['METEOR'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(h2c_data['Perplexity'].min(), h2c_data['Perplexity'].max(), 100)
    ax3.plot(x_line, p(x_line), 'r--', alpha=0.7, linewidth=2)

    ax3.set_xlabel('Perplexity (Complexity)', fontsize=12, weight='bold')
    ax3.set_ylabel('METEOR Score (Performance)', fontsize=12, weight='bold')
    ax3.set_title('H2C: Complexity vs Performance\n(Negative Correlation)', fontsize=13, weight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=10)

    # Panel 4: Complexity-Performance Scatter (C2H)
    ax4 = axes[1, 1]

    c2h_data = df[df['Direction'] == 'C2H']
    ax4.scatter(c2h_data['Perplexity'], c2h_data['METEOR'], s=200, alpha=0.7,
               color='blue', edgecolors='black', linewidth=2, label='C2H')

    # Add newspaper labels
    for _, row in c2h_data.iterrows():
        ax4.annotate(row['Newspaper'], (row['Perplexity'], row['METEOR']),
                    xytext=(5, 5), textcoords='offset points', fontsize=9)

    # Regression line
    z = np.polyfit(c2h_data['Perplexity'], c2h_data['METEOR'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(c2h_data['Perplexity'].min(), c2h_data['Perplexity'].max(), 100)
    ax4.plot(x_line, p(x_line), 'b--', alpha=0.7, linewidth=2)

    ax4.set_xlabel('Perplexity (Complexity)', fontsize=12, weight='bold')
    ax4.set_ylabel('METEOR Score (Performance)', fontsize=12, weight='bold')
    ax4.set_title('C2H: Complexity vs Performance\n(Negative Correlation)', fontsize=13, weight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.legend(fontsize=10)

    plt.suptitle('Complexity-Performance Relationship by Direction\nHigher Complexity → Lower Performance',
                fontsize=16, weight='bold', y=1.00)
    plt.tight_layout()
    plt.savefig(output_dir / 'complexity_performance_by_direction.png', dpi=200, bbox_inches='tight')
    plt.close()

    print(f"Created: {output_dir / 'complexity_performance_by_direction.png'}")

def main():
    project_root = Path(__file__).parent
    output_dir = project_root / 'output' / 'correlation_analysis'
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Creating enhanced correlation visualizations...")
    create_significance_summary(output_dir)
    create_complexity_performance_comparison(output_dir)
    print("\n✓ Enhanced visualizations complete!")

if __name__ == '__main__':
    main()
