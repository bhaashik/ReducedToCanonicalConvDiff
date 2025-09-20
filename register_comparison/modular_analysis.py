#!/usr/bin/env python3

"""
Modular Register Comparison Analysis System

This script allows running different levels of analysis independently:
1. Per-newspaper analysis
2. Feature-level analysis
3. Feature-value analysis
4. Global multi-newspaper analysis
5. Enhanced value transformation visualizations

Usage:
    python modular_analysis.py --newspapers "Times-of-India" --analysis basic
    python modular_analysis.py --newspapers "all" --analysis feature-value
    python modular_analysis.py --analysis global --enhance-visuals
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from register_comparison.meta_data.schema import FeatureSchema
from data.loaded_data import LoadedData
from register_comparison.comparators.schema_comparator import SchemaBasedComparator as Comparator
from register_comparison.aligners.aligner import Aligner
from register_comparison.extractors.extractor import FeatureExtractor
from register_comparison.aggregators.aggregator import Aggregator
from register_comparison.outputs.output_creators import Outputs
from register_comparison.visualizers.visualizer import Visualizer
from register_comparison.stat_runners.stats import StatsRunner
from paths_config import NEWSPAPERS, SCHEMA_PATH
import pandas as pd

class ModularAnalysisRunner:
    """Modular analysis runner supporting independent analysis levels."""

    def __init__(self, base_output_dir: str = "output"):
        self.base_output_dir = Path(base_output_dir)
        self.schema = None
        self.global_aggregator = Aggregator()  # For multi-newspaper aggregation
        self.newspaper_aggregators = {}  # Individual newspaper aggregators

    def load_schema(self):
        """Load the feature schema."""
        print("Loading feature schema...")
        self.schema = FeatureSchema(str(SCHEMA_PATH))
        self.schema.load_schema()
        print(f"✅ Loaded schema with {len(self.schema.features)} features")

    def run_newspaper_analysis(self, newspapers: List[str], analysis_level: str = "basic"):
        """Run analysis for specific newspapers."""
        print(f"\\n{'='*60}")
        print(f"RUNNING {analysis_level.upper()} ANALYSIS FOR: {', '.join(newspapers)}")
        print(f"{'='*60}")

        loaded_data = LoadedData()

        for newspaper in newspapers:
            print(f"\\nProcessing {newspaper}...")

            # Load data
            try:
                loaded_data.load_newspaper_data(newspaper)
                print(f"  ✅ Loaded data for {newspaper}")
            except Exception as e:
                print(f"  ❌ Error loading {newspaper}: {e}")
                continue

            # Create aligner and get pairs
            try:
                aligner = Aligner(
                    texts_canonical=loaded_data.text_data[newspaper]['canonical'],
                    texts_headlines=loaded_data.text_data[newspaper]['headlines'],
                    deps_canonical=loaded_data.dependency_data[newspaper]['canonical'],
                    deps_headlines=loaded_data.dependency_data[newspaper]['headlines'],
                    consts_canonical=loaded_data.constituency_data[newspaper]['canonical'],
                    consts_headlines=loaded_data.constituency_data[newspaper]['headlines'],
                    newspaper_name=newspaper
                )
                pairs = aligner.align()
                print(f"  ✅ Generated {len(pairs)} aligned sentence pairs")
            except Exception as e:
                print(f"  ❌ Error in alignment for {newspaper}: {e}")
                continue

            # Run comparison
            try:
                extractor = FeatureExtractor(self.schema)
                comparator = Comparator(self.schema)
                events = []

                for pair in pairs:
                    features = extractor.extract_features(pair)
                    pair_events = comparator.compare_pair(pair, features)
                    events.extend(pair_events)

                print(f"  ✅ Generated {len(events)} difference events")
            except Exception as e:
                print(f"  ❌ Error in comparison for {newspaper}: {e}")
                continue

            # Create newspaper-specific aggregator
            newspaper_aggregator = Aggregator()
            newspaper_aggregator.add_events(events)
            self.newspaper_aggregators[newspaper] = newspaper_aggregator

            # Also add to global aggregator
            self.global_aggregator.add_events(events)

            # Run newspaper-specific analysis
            self._run_newspaper_specific_analysis(newspaper, newspaper_aggregator, analysis_level)

    def _run_newspaper_specific_analysis(self, newspaper: str, aggregator: Aggregator, analysis_level: str):
        """Run analysis for a specific newspaper."""
        output_dir = self.base_output_dir / newspaper
        output_dir.mkdir(parents=True, exist_ok=True)

        outputs = Outputs(output_dir, self.schema)
        visualizer = Visualizer(output_dir, self.schema)
        stats_runner = StatsRunner()

        print(f"  Running {analysis_level} analysis for {newspaper}...")

        if analysis_level in ["basic", "comprehensive", "feature-value"]:
            # Basic feature analysis
            feature_counts = aggregator.global_counts()

            # Save basic outputs
            outputs.save_feature_matrix_csv(feature_counts, "feature_freq_global.csv")
            outputs.save_events_csv(aggregator.global_events, "events_global.csv")

            # Statistical testing
            stats_data = aggregator.to_stats_runner_format()
            stats_df = pd.DataFrame(stats_data)
            if not stats_df.empty:
                summary_stats_df = stats_runner.run_for_dataframe(stats_df, "canonical", "headlines")
                outputs.save_summary_stats_csv(summary_stats_df, "summary_stats_global.csv")

            # Basic visualizations
            visualizer.plot_feature_frequencies(feature_counts, f"{newspaper} Feature Frequencies", "feature_freq_global.png")

        if analysis_level in ["comprehensive", "feature-value"]:
            # Comprehensive analysis
            comprehensive_analysis = aggregator.get_comprehensive_analysis()
            statistical_summary = aggregator.get_statistical_summary()

            # Save comprehensive outputs
            outputs.save_comprehensive_analysis(comprehensive_analysis, "comprehensive_analysis")
            outputs.save_statistical_summary(statistical_summary, "statistical_summary")

            # Comprehensive visualizations
            visualizer.create_comprehensive_visualizations(comprehensive_analysis, statistical_summary)
            visualizer.create_statistical_summary_visualizations(comprehensive_analysis, statistical_summary)

        if analysis_level == "feature-value":
            # Feature-value analysis
            feature_value_analysis = aggregator.get_feature_value_analysis()

            # Save feature-value outputs
            outputs.save_feature_value_analysis(feature_value_analysis, "feature_value_analysis")

            # Feature-value visualizations
            visualizer.create_feature_value_visualizations(feature_value_analysis)

            # Generate enhanced reports with feature-value analysis
            outputs.generate_enhanced_latex_report(comprehensive_analysis, statistical_summary,
                                                 feature_value_analysis, "enhanced_comprehensive_report.tex")
            outputs.generate_enhanced_markdown_report(comprehensive_analysis, statistical_summary,
                                                    feature_value_analysis, "enhanced_comprehensive_report.md")

        print(f"  ✅ {analysis_level.title()} analysis completed for {newspaper}")

    def run_global_analysis(self, analysis_level: str = "comprehensive"):
        """Run global analysis across all newspapers."""
        print(f"\\n{'='*60}")
        print(f"RUNNING GLOBAL {analysis_level.upper()} ANALYSIS")
        print(f"{'='*60}")

        if not self.global_aggregator.global_events:
            print("❌ No events in global aggregator. Run newspaper analysis first.")
            return

        output_dir = self.base_output_dir / "GLOBAL_ANALYSIS"
        output_dir.mkdir(parents=True, exist_ok=True)

        outputs = Outputs(output_dir, self.schema)
        visualizer = Visualizer(output_dir, self.schema)

        print(f"Analyzing {len(self.global_aggregator.global_events)} global events...")

        # Global comprehensive analysis
        comprehensive_analysis = self.global_aggregator.get_comprehensive_analysis()
        statistical_summary = self.global_aggregator.get_statistical_summary()

        # Save global outputs
        outputs.save_comprehensive_analysis(comprehensive_analysis, "global_comprehensive_analysis")
        outputs.save_statistical_summary(statistical_summary, "global_statistical_summary")

        # Global visualizations
        visualizer.create_comprehensive_visualizations(comprehensive_analysis, statistical_summary)
        visualizer.create_statistical_summary_visualizations(comprehensive_analysis, statistical_summary)

        if analysis_level == "feature-value":
            # Global feature-value analysis
            feature_value_analysis = self.global_aggregator.get_feature_value_analysis()
            outputs.save_feature_value_analysis(feature_value_analysis, "global_feature_value_analysis")
            visualizer.create_feature_value_visualizations(feature_value_analysis)

            # Generate enhanced global reports
            outputs.generate_enhanced_latex_report(comprehensive_analysis, statistical_summary,
                                                 feature_value_analysis, "global_enhanced_report.tex")
            outputs.generate_enhanced_markdown_report(comprehensive_analysis, statistical_summary,
                                                    feature_value_analysis, "global_enhanced_report.md")

        # Cross-newspaper comparison
        self._create_cross_newspaper_analysis(outputs, visualizer)

        print("✅ Global analysis completed")

    def _create_cross_newspaper_analysis(self, outputs: Outputs, visualizer: Visualizer):
        """Create cross-newspaper comparison analysis."""
        print("Creating cross-newspaper comparison...")

        # Compare newspapers
        newspaper_stats = {}
        for newspaper, aggregator in self.newspaper_aggregators.items():
            newspaper_stats[newspaper] = {
                'total_events': len(aggregator.global_events),
                'feature_counts': aggregator.global_counts(),
                'unique_features': len(aggregator.global_counts())
            }

        # Save cross-newspaper comparison
        comparison_data = []
        for newspaper, stats in newspaper_stats.items():
            comparison_data.append({
                'newspaper': newspaper,
                'total_events': stats['total_events'],
                'unique_features': stats['unique_features'],
                'most_frequent_feature': max(stats['feature_counts'].items(), key=lambda x: x[1])[0] if stats['feature_counts'] else 'None'
            })

        df = pd.DataFrame(comparison_data)
        df.to_csv(outputs.output_dir / "cross_newspaper_comparison.csv", index=False)

        # Cross-newspaper visualization
        self._create_cross_newspaper_visualizations(newspaper_stats, visualizer)

    def _create_cross_newspaper_visualizations(self, newspaper_stats: Dict, visualizer: Visualizer):
        """Create cross-newspaper comparison visualizations."""
        import matplotlib.pyplot as plt
        import numpy as np

        newspapers = list(newspaper_stats.keys())

        # 1. Total events comparison
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        total_events = [newspaper_stats[np]['total_events'] for np in newspapers]
        ax1.bar(newspapers, total_events, color=['steelblue', 'lightcoral', 'mediumseagreen'])
        ax1.set_title("Total Events by Newspaper")
        ax1.set_ylabel("Number of Events")
        ax1.tick_params(axis='x', rotation=45)

        # 2. Feature diversity comparison
        unique_features = [newspaper_stats[np]['unique_features'] for np in newspapers]
        ax2.bar(newspapers, unique_features, color=['orange', 'purple', 'brown'])
        ax2.set_title("Feature Diversity by Newspaper")
        ax2.set_ylabel("Number of Unique Features")
        ax2.tick_params(axis='x', rotation=45)

        # 3. Top 5 features comparison
        all_features = set()
        for stats in newspaper_stats.values():
            all_features.update(stats['feature_counts'].keys())

        top_features = sorted(all_features,
                            key=lambda f: sum(newspaper_stats[np]['feature_counts'].get(f, 0) for np in newspapers),
                            reverse=True)[:5]

        x = np.arange(len(top_features))
        width = 0.25

        for i, newspaper in enumerate(newspapers):
            counts = [newspaper_stats[newspaper]['feature_counts'].get(f, 0) for f in top_features]
            ax3.bar(x + i*width, counts, width, label=newspaper, alpha=0.8)

        ax3.set_title("Top 5 Features Across Newspapers")
        ax3.set_ylabel("Count")
        ax3.set_xticks(x + width)
        ax3.set_xticklabels(top_features, rotation=45, ha='right')
        ax3.legend()

        # 4. Proportional comparison (events per unique feature)
        efficiency = [total_events[i]/unique_features[i] if unique_features[i] > 0 else 0
                     for i in range(len(newspapers))]
        ax4.bar(newspapers, efficiency, color=['darkblue', 'darkred', 'darkgreen'])
        ax4.set_title("Event Intensity (Events per Unique Feature)")
        ax4.set_ylabel("Events/Feature Ratio")
        ax4.tick_params(axis='x', rotation=45)

        plt.suptitle("Cross-Newspaper Analysis")
        plt.tight_layout()
        plt.savefig(visualizer.output_dir / "cross_newspaper_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()

        print("✅ Cross-newspaper visualizations created")

    def create_enhanced_transformation_visualizations(self):
        """Create enhanced value→value transformation visualizations."""
        print("Creating enhanced transformation visualizations...")

        output_dir = self.base_output_dir / "ENHANCED_TRANSFORMATIONS"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get feature-value analysis from global aggregator
        feature_value_analysis = self.global_aggregator.get_feature_value_analysis()

        # Create enhanced visualizer
        from register_comparison.visualizers.enhanced_visualizer import EnhancedVisualizer
        enhanced_viz = EnhancedVisualizer(output_dir)

        # Create enhanced transformation visualizations
        enhanced_viz.create_value_to_value_transformations(feature_value_analysis)
        enhanced_viz.create_transformation_networks(feature_value_analysis)
        enhanced_viz.create_transformation_flow_diagrams(feature_value_analysis)

        print("✅ Enhanced transformation visualizations completed")

def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(description='Modular Register Comparison Analysis')
    parser.add_argument('--newspapers', default='all',
                       help='Newspapers to analyze: "all", "Times-of-India", "The-Hindu", "Hindustan-Times", or comma-separated list')
    parser.add_argument('--analysis', choices=['basic', 'comprehensive', 'feature-value'], default='comprehensive',
                       help='Analysis level to run')
    parser.add_argument('--global-only', action='store_true',
                       help='Run only global analysis (requires previous newspaper analysis)')
    parser.add_argument('--output-dir', default='output',
                       help='Output directory for results')
    parser.add_argument('--enhance-visuals', action='store_true',
                       help='Create enhanced value→value transformation visualizations')

    args = parser.parse_args()

    # Initialize runner
    runner = ModularAnalysisRunner(args.output_dir)
    runner.load_schema()

    # Determine newspapers to analyze
    if args.newspapers.lower() == 'all':
        newspapers_to_analyze = NEWSPAPERS
    else:
        newspapers_to_analyze = [np.strip() for np in args.newspapers.split(',')]

    # Validate newspaper names
    for newspaper in newspapers_to_analyze:
        if newspaper not in NEWSPAPERS:
            print(f"❌ Unknown newspaper: {newspaper}")
            print(f"Available newspapers: {', '.join(NEWSPAPERS)}")
            return

    # Run analysis
    if not args.global_only:
        runner.run_newspaper_analysis(newspapers_to_analyze, args.analysis)

    runner.run_global_analysis(args.analysis)

    if args.enhance_visuals:
        print("\\nCreating enhanced value→value transformation visualizations...")
        runner.create_enhanced_transformation_visualizations()

    print(f"\\n{'='*60}")
    print("MODULAR ANALYSIS COMPLETED!")
    print(f"{'='*60}")
    print(f"✅ Analysis level: {args.analysis}")
    print(f"✅ Newspapers: {', '.join(newspapers_to_analyze)}")
    print(f"✅ Output directory: {args.output_dir}")
    if args.enhance_visuals:
        print("✅ Enhanced visualizations created")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()