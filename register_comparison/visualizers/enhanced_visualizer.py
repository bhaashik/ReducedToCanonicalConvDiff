#!/usr/bin/env python3

"""
Enhanced Visualizer for Value→Value Transformations

This module creates detailed visualizations showing specific value-to-value transformations
within each feature, making it clear which canonical values change to which headline values.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from pathlib import Path
import networkx as nx
from matplotlib.patches import FancyBboxPatch
import matplotlib.patches as mpatches

class EnhancedVisualizer:
    """Enhanced visualizer for detailed value→value transformation analysis."""

    def __init__(self, output_dir: Path, feature_labels: Dict[str, str] = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.feature_labels = feature_labels or {}

    def _get_feature_label(self, feature_id: str) -> str:
        """Get readable label for feature ID."""
        return self.feature_labels.get(feature_id, feature_id)

    def create_value_to_value_transformations(self, feature_value_analysis: Dict[str, Any]):
        """Create detailed value→value transformation visualizations for each feature."""
        print("Creating value→value transformation visualizations...")

        global_feature_values = feature_value_analysis['global_feature_values']

        for feature_id, transformations in global_feature_values.items():
            if not transformations:
                continue

            # Create transformation matrix for this feature
            self._create_transformation_matrix(feature_id, transformations)

            # Create transformation sankey diagram
            self._create_transformation_sankey(feature_id, transformations)

            # Create top transformations detailed view
            self._create_detailed_transformation_view(feature_id, transformations)

        print("✅ Value→value transformation visualizations completed")

    def _create_transformation_matrix(self, feature_id: str, transformations: Dict[str, int]):
        """Create a matrix showing canonical→headline value transformations."""
        # Parse transformations to get canonical and headline values
        canonical_values = set()
        headline_values = set()
        transformation_data = []

        for transformation, count in transformations.items():
            if '→' in transformation:
                canonical_val, headline_val = transformation.split('→', 1)
                canonical_values.add(canonical_val)
                headline_values.add(headline_val)
                transformation_data.append((canonical_val, headline_val, count))

        if not transformation_data:
            return

        # Create matrix
        canonical_list = sorted(list(canonical_values))
        headline_list = sorted(list(headline_values))

        matrix = np.zeros((len(canonical_list), len(headline_list)))

        for canonical_val, headline_val, count in transformation_data:
            can_idx = canonical_list.index(canonical_val)
            head_idx = headline_list.index(headline_val)
            matrix[can_idx, head_idx] = count

        # Create heatmap
        fig, ax = plt.subplots(figsize=(max(8, len(headline_list) * 0.8), max(6, len(canonical_list) * 0.5)))

        # Use log scale for better visualization if there are large differences
        if matrix.max() > matrix[matrix > 0].min() * 100:
            matrix_viz = np.log1p(matrix)  # log(1 + x) to handle zeros
            fmt = '.0f'
            cbar_label = 'Log(Count + 1)'
        else:
            matrix_viz = matrix
            fmt = 'd'
            cbar_label = 'Count'

        im = sns.heatmap(matrix_viz,
                        xticklabels=headline_list,
                        yticklabels=canonical_list,
                        annot=matrix.astype(int),
                        fmt=fmt,
                        cmap='YlOrRd',
                        ax=ax,
                        cbar_kws={'label': cbar_label})

        feature_label = self._get_feature_label(feature_id)
        ax.set_title(f"{feature_label}: Canonical → Headline Value Transformations")
        ax.set_xlabel("Headline Values")
        ax.set_ylabel("Canonical Values")

        # Rotate labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        plt.setp(ax.get_yticklabels(), rotation=0)

        plt.tight_layout()
        plt.savefig(self.output_dir / f"{feature_id}_transformation_matrix.png", dpi=300, bbox_inches='tight')
        plt.close()

    def _create_transformation_sankey(self, feature_id: str, transformations: Dict[str, int]):
        """Create a Sankey-style diagram showing value transformations."""
        # Parse transformations
        transformation_data = []
        for transformation, count in transformations.items():
            if '→' in transformation and count >= 5:  # Only show significant transformations
                canonical_val, headline_val = transformation.split('→', 1)
                transformation_data.append((canonical_val, headline_val, count))

        if len(transformation_data) < 2:
            return

        # Sort by count
        transformation_data.sort(key=lambda x: x[2], reverse=True)
        top_transformations = transformation_data[:15]  # Top 15 transformations

        # Create flow diagram
        fig, ax = plt.subplots(figsize=(14, max(8, len(top_transformations) * 0.5)))

        # Get unique values
        canonical_values = list(set(t[0] for t in top_transformations))
        headline_values = list(set(t[1] for t in top_transformations))

        # Position nodes
        canonical_y_positions = {val: i for i, val in enumerate(sorted(canonical_values))}
        headline_y_positions = {val: i for i, val in enumerate(sorted(headline_values))}

        # Draw canonical values (left side)
        for val, y_pos in canonical_y_positions.items():
            ax.text(0.1, y_pos, val, ha='right', va='center', fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))

        # Draw headline values (right side)
        for val, y_pos in headline_y_positions.items():
            ax.text(0.9, y_pos, val, ha='left', va='center', fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='lightcoral', alpha=0.7))

        # Draw transformation arrows
        max_count = max(t[2] for t in top_transformations)
        for canonical_val, headline_val, count in top_transformations:
            can_y = canonical_y_positions[canonical_val]
            head_y = headline_y_positions[headline_val]

            # Arrow width proportional to count
            arrow_width = (count / max_count) * 0.02

            ax.annotate('', xy=(0.88, head_y), xytext=(0.12, can_y),
                       arrowprops=dict(arrowstyle='->', lw=arrow_width*100,
                                     color='gray', alpha=0.6))

            # Add count label
            mid_x = 0.5
            mid_y = (can_y + head_y) / 2
            ax.text(mid_x, mid_y, str(count), ha='center', va='center',
                   fontsize=8, bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))

        ax.set_xlim(0, 1)
        ax.set_ylim(-0.5, max(len(canonical_values), len(headline_values)) - 0.5)
        feature_label = self._get_feature_label(feature_id)
        ax.set_title(f"{feature_label}: Value Transformation Flow\\n(Canonical → Headline)", fontsize=14, fontweight='bold')
        ax.axis('off')

        # Add legend
        legend_elements = [
            mpatches.Rectangle((0, 0), 1, 1, facecolor='lightblue', alpha=0.7, label='Canonical Values'),
            mpatches.Rectangle((0, 0), 1, 1, facecolor='lightcoral', alpha=0.7, label='Headline Values')
        ]
        ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2)

        plt.tight_layout()
        plt.savefig(self.output_dir / f"{feature_id}_transformation_flow.png", dpi=300, bbox_inches='tight')
        plt.close()

    def _create_detailed_transformation_view(self, feature_id: str, transformations: Dict[str, int]):
        """Create a detailed view of transformations with percentages and statistics."""
        # Sort transformations by count
        sorted_transformations = sorted(transformations.items(), key=lambda x: x[1], reverse=True)
        top_transformations = sorted_transformations[:20]  # Top 20

        if not top_transformations:
            return

        total_transformations = sum(transformations.values())

        # Create detailed view
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, max(8, len(top_transformations) * 0.4)))

        # Left panel: Bar chart with counts and percentages
        transformation_labels = [t[0] for t in top_transformations]
        counts = [t[1] for t in top_transformations]
        percentages = [(c / total_transformations) * 100 for c in counts]

        y_positions = range(len(transformation_labels))

        bars = ax1.barh(y_positions, counts, color=plt.cm.viridis(np.linspace(0, 1, len(counts))))

        # Add percentage labels on bars
        for i, (count, percentage) in enumerate(zip(counts, percentages)):
            ax1.text(count + max(counts) * 0.01, i, f'{count} ({percentage:.1f}%)',
                    va='center', fontsize=9)

        ax1.set_yticks(y_positions)
        ax1.set_yticklabels(transformation_labels, fontsize=10)
        ax1.set_xlabel('Count')
        feature_label = self._get_feature_label(feature_id)
        ax1.set_title(f'Top Transformations: {feature_label}')
        ax1.grid(axis='x', alpha=0.3)

        # Right panel: Transformation statistics
        ax2.axis('off')

        # Calculate statistics
        unique_canonical = len(set(t.split('→')[0] if '→' in t else t for t in transformations.keys()))
        unique_headline = len(set(t.split('→')[1] if '→' in t else t for t in transformations.keys()))

        deletions = sum(1 for t in transformations.keys() if t.endswith('→ABSENT'))
        additions = sum(1 for t in transformations.keys() if t.startswith('ABSENT→'))
        changes = len(transformations) - deletions - additions

        # Most frequent transformation
        most_frequent = top_transformations[0] if top_transformations else ('None', 0)

        stats_text = [
            f"Feature: {feature_id}",
            f"",
            f"Total Transformations: {total_transformations:,}",
            f"Unique Transformation Types: {len(transformations)}",
            f"",
            f"Value Diversity:",
            f"  • Canonical Values: {unique_canonical}",
            f"  • Headline Values: {unique_headline}",
            f"",
            f"Transformation Categories:",
            f"  • Deletions (→ABSENT): {deletions}",
            f"  • Additions (ABSENT→): {additions}",
            f"  • Changes: {changes}",
            f"",
            f"Most Frequent Transformation:",
            f"  {most_frequent[0]}",
            f"  Count: {most_frequent[1]:,}",
            f"  Percentage: {(most_frequent[1]/total_transformations)*100:.1f}%",
            f"",
            f"Top 3 Concentration: {sum(counts[:3])/total_transformations*100:.1f}%"
        ]

        ax2.text(0.05, 0.95, '\\n'.join(stats_text), transform=ax2.transAxes,
                fontsize=11, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray', alpha=0.8))

        plt.suptitle(f"Detailed Analysis: {feature_id} Transformations", fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.output_dir / f"{feature_id}_detailed_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()

    def create_transformation_networks(self, feature_value_analysis: Dict[str, Any]):
        """Create network graphs showing transformation relationships."""
        print("Creating transformation network graphs...")

        global_feature_values = feature_value_analysis['global_feature_values']

        # Create overall transformation network
        self._create_overall_transformation_network(global_feature_values)

        # Create per-feature networks for complex features
        complex_features = ['DEP-REL-CHG', 'CONST-MOV', 'CLAUSE-TYPE-CHG', 'HEAD-CHG']
        for feature_id in complex_features:
            if feature_id in global_feature_values:
                self._create_feature_transformation_network(feature_id, global_feature_values[feature_id])

        print("✅ Transformation networks completed")

    def _create_overall_transformation_network(self, global_feature_values: Dict[str, Dict[str, int]]):
        """Create a network showing all transformations across features."""
        fig, ax = plt.subplots(figsize=(16, 12))

        G = nx.DiGraph()

        # Add edges for transformations (sample to avoid overcrowding)
        feature_colors = plt.cm.Set3(np.linspace(0, 1, len(global_feature_values)))

        for feature_idx, (feature_id, transformations) in enumerate(global_feature_values.items()):
            # Only add top transformations to avoid clutter
            top_transformations = sorted(transformations.items(), key=lambda x: x[1], reverse=True)[:5]

            for transformation, count in top_transformations:
                if '→' in transformation and count >= 10:  # Only significant transformations
                    canonical_val, headline_val = transformation.split('→', 1)
                    G.add_edge(canonical_val, headline_val, weight=count, feature=feature_id, color=feature_colors[feature_idx])

        if G.number_of_nodes() > 0:
            # Layout
            pos = nx.spring_layout(G, k=2, iterations=50)

            # Draw edges with different colors for different features
            for feature_idx, (feature_id, _) in enumerate(global_feature_values.items()):
                feature_edges = [(u, v) for u, v, d in G.edges(data=True) if d['feature'] == feature_id]
                if feature_edges:
                    nx.draw_networkx_edges(G, pos, edgelist=feature_edges,
                                         edge_color=feature_colors[feature_idx],
                                         alpha=0.6, arrows=True, arrowsize=20)

            # Draw nodes
            nx.draw_networkx_nodes(G, pos, node_color='lightblue',
                                 node_size=300, alpha=0.8)

            # Draw labels
            nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')

            ax.set_title("Overall Transformation Network\\n(Values connected by transformation relationships)",
                        fontsize=14, fontweight='bold')
            ax.axis('off')

        plt.tight_layout()
        plt.savefig(self.output_dir / "overall_transformation_network.png", dpi=300, bbox_inches='tight')
        plt.close()

    def _create_feature_transformation_network(self, feature_id: str, transformations: Dict[str, int]):
        """Create a network graph for a specific feature's transformations."""
        fig, ax = plt.subplots(figsize=(12, 10))

        G = nx.DiGraph()

        # Add transformations as edges
        for transformation, count in transformations.items():
            if '→' in transformation and count >= 2:  # Filter very rare transformations
                canonical_val, headline_val = transformation.split('→', 1)
                G.add_edge(canonical_val, headline_val, weight=count)

        if G.number_of_nodes() == 0:
            plt.close()
            return

        # Layout
        pos = nx.spring_layout(G, k=3, iterations=100)

        # Draw edges with width proportional to weight
        weights = [G[u][v]['weight'] for u, v in G.edges()]
        max_weight = max(weights) if weights else 1

        for (u, v, d) in G.edges(data=True):
            width = (d['weight'] / max_weight) * 5
            nx.draw_networkx_edges(G, pos, edgelist=[(u, v)],
                                 width=width, alpha=0.6, arrows=True,
                                 arrowsize=20, edge_color='gray')

        # Color nodes by type
        canonical_nodes = [n for n in G.nodes() if any(n == edge.split('→')[0] for edge in transformations.keys() if '→' in edge)]
        headline_nodes = [n for n in G.nodes() if any(n == edge.split('→')[1] for edge in transformations.keys() if '→' in edge)]

        if canonical_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=canonical_nodes,
                                 node_color='lightblue', node_size=500, alpha=0.8, label='Canonical Values')
        if headline_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=headline_nodes,
                                 node_color='lightcoral', node_size=500, alpha=0.8, label='Headline Values')

        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold')

        # Add weight labels on edges
        edge_labels = {(u, v): str(d['weight']) for u, v, d in G.edges(data=True) if d['weight'] >= 10}
        nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8)

        feature_label = self._get_feature_label(feature_id)
        ax.set_title(f"{feature_label}: Transformation Network\\n(Node size and edge width represent frequency)",
                    fontsize=14, fontweight='bold')
        ax.axis('off')
        ax.legend()

        plt.tight_layout()
        plt.savefig(self.output_dir / f"{feature_id}_transformation_network.png", dpi=300, bbox_inches='tight')
        plt.close()

    def create_transformation_flow_diagrams(self, feature_value_analysis: Dict[str, Any]):
        """Create flow diagrams showing transformation patterns."""
        print("Creating transformation flow diagrams...")

        # Create summary flow diagram
        self._create_summary_flow_diagram(feature_value_analysis)

        print("✅ Transformation flow diagrams completed")

    def _create_summary_flow_diagram(self, feature_value_analysis: Dict[str, Any]):
        """Create a summary flow diagram of all transformations."""
        transformation_patterns = feature_value_analysis['transformation_patterns']

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        # 1. Deletion patterns
        deletions = transformation_patterns['transformation_types']['deletions']
        if deletions:
            top_deletions = sorted(deletions.items(), key=lambda x: x[1], reverse=True)[:10]
            if top_deletions:
                labels, counts = zip(*top_deletions)
                ax1.barh(range(len(labels)), counts, color='red', alpha=0.7)
                ax1.set_yticks(range(len(labels)))
                ax1.set_yticklabels([l.replace('→ABSENT', '') for l in labels], fontsize=8)
                ax1.set_title("Top Deletions (→ABSENT)")
                ax1.set_xlabel("Count")

        # 2. Addition patterns
        additions = transformation_patterns['transformation_types']['additions']
        if additions:
            top_additions = sorted(additions.items(), key=lambda x: x[1], reverse=True)[:10]
            if top_additions:
                labels, counts = zip(*top_additions)
                ax2.barh(range(len(labels)), counts, color='green', alpha=0.7)
                ax2.set_yticks(range(len(labels)))
                ax2.set_yticklabels([l.replace('ABSENT→', '') for l in labels], fontsize=8)
                ax2.set_title("Top Additions (ABSENT→)")
                ax2.set_xlabel("Count")

        # 3. Change patterns (value to value)
        changes = transformation_patterns['transformation_types']['changes']
        if changes:
            top_changes = sorted(changes.items(), key=lambda x: x[1], reverse=True)[:10]
            if top_changes:
                labels, counts = zip(*top_changes)
                ax3.barh(range(len(labels)), counts, color='blue', alpha=0.7)
                ax3.set_yticks(range(len(labels)))
                ax3.set_yticklabels(labels, fontsize=8)
                ax3.set_title("Top Value Changes")
                ax3.set_xlabel("Count")

        # 4. Overall transformation type distribution
        type_counts = {
            'Deletions': sum(deletions.values()),
            'Additions': sum(additions.values()),
            'Changes': sum(changes.values())
        }

        ax4.pie(type_counts.values(), labels=type_counts.keys(), autopct='%1.1f%%',
               colors=['red', 'green', 'blue'], alpha=0.7)
        ax4.set_title("Transformation Type Distribution")

        plt.suptitle("Transformation Flow Summary", fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.output_dir / "transformation_flow_summary.png", dpi=300, bbox_inches='tight')
        plt.close()