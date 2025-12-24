#!/usr/bin/env python3
"""
Task 2: Transformation Study

Analyzes transformation patterns and rule coverage to answer:
1. How many transformation rules capture how many difference events?
2. Which transformation direction (C→H or H→C) is easier and why?
3. How do morphological, lexical, and syntactic rules contribute to coverage?

Components:
1. Rule extraction from Task 1 events
2. Progressive coverage analysis (adding rules incrementally)
3. Morphological rule integration
4. Comparative analysis across newspapers
5. Visualization of transformation patterns and effectiveness
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import argparse


class Task2Runner:
    """Runs complete Task 2: Transformation Study pipeline."""

    def __init__(self, newspapers=None, skip_extraction=False, skip_visualization=False):
        self.project_root = Path(__file__).parent
        self.newspapers = newspapers or ['Times-of-India', 'Hindustan-Times', 'The-Hindu']
        self.skip_extraction = skip_extraction
        self.skip_visualization = skip_visualization
        self.start_time = datetime.now()
        self.output_dir = self.project_root / 'output' / 'transformation-study'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
        """Log pipeline messages."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def run_script(self, script_path: str, description: str) -> bool:
        """Run a Python script and handle errors."""
        self.log(f"Running: {description}...", "TASK-2")

        script_file = self.project_root / script_path
        if not script_file.exists():
            self.log(f"Script not found: {script_path}", "WARNING")
            return False

        try:
            result = subprocess.run(
                [sys.executable, str(script_file)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=2400  # 40 minute timeout
            )

            if result.returncode == 0:
                self.log(f"✓ Completed: {description}", "SUCCESS")
                return True
            else:
                self.log(f"✗ Failed: {description}", "ERROR")
                if result.stderr:
                    self.log(f"Error output: {result.stderr[:500]}", "ERROR")
                return False

        except subprocess.TimeoutExpired:
            self.log(f"✗ Timeout: {description}", "ERROR")
            return False
        except Exception as e:
            self.log(f"✗ Exception: {description} - {str(e)}", "ERROR")
            return False

    def verify_task1_outputs(self) -> bool:
        """Verify that Task 1 outputs exist for all newspapers."""
        self.log("Verifying Task 1 outputs...", "INFO")

        missing = []
        for newspaper in self.newspapers:
            events_file = self.project_root / 'output' / newspaper / 'events_global.csv'
            if not events_file.exists():
                missing.append(newspaper)

        if missing:
            self.log(f"Missing Task 1 outputs for: {', '.join(missing)}", "ERROR")
            self.log("Please run Task 1 first: python run_task1_all_newspapers.py", "ERROR")
            return False

        self.log("✓ All Task 1 outputs verified", "SUCCESS")
        return True

    def run_rule_extraction(self) -> list:
        """Extract transformation rules from difference events."""
        if self.skip_extraction:
            self.log("Skipping rule extraction (--skip-extraction flag)", "INFO")
            return []

        self.log("="*80, "INFO")
        self.log("STEP 1: RULE EXTRACTION", "INFO")
        self.log("="*80, "INFO")

        scripts = []

        # Check if extract_morphological_rules.py exists
        if (self.project_root / "extract_morphological_rules.py").exists():
            scripts.append((
                "extract_morphological_rules.py",
                "Extract morphological transformation rules"
            ))

        # Run rule extraction (implement if needed)
        # For now, assume rules are extracted during Task 1 analysis

        if not scripts:
            self.log("No additional rule extraction needed (rules extracted during Task 1)", "INFO")
            return []

        results = []
        for script, desc in scripts:
            success = self.run_script(script, desc)
            results.append((script, success))

        return results

    def run_progressive_coverage_analysis(self) -> list:
        """Run progressive coverage analysis with morphological integration."""
        self.log("="*80, "INFO")
        self.log("STEP 2: PROGRESSIVE COVERAGE ANALYSIS", "INFO")
        self.log("="*80, "INFO")

        scripts = [
            ("progressive_coverage_with_morphology.py",
             "Progressive coverage analysis with morphological rules"),
        ]

        results = []
        for script, desc in scripts:
            success = self.run_script(script, desc)
            results.append((script, success))

        return results

    def run_morphological_analysis(self) -> list:
        """Run morphological comparative analysis."""
        self.log("="*80, "INFO")
        self.log("STEP 3: MORPHOLOGICAL COMPARATIVE ANALYSIS", "INFO")
        self.log("="*80, "INFO")

        scripts = [
            ("create_morphological_comparative_analysis.py",
             "Morphological transformation patterns across newspapers"),
        ]

        results = []
        for script, desc in scripts:
            success = self.run_script(script, desc)
            results.append((script, success))

        return results

    def run_visualizations(self) -> list:
        """Generate comprehensive visualizations."""
        if self.skip_visualization:
            self.log("Skipping visualizations (--skip-visualization flag)", "INFO")
            return []

        self.log("="*80, "INFO")
        self.log("STEP 4: VISUALIZATION GENERATION", "INFO")
        self.log("="*80, "INFO")

        scripts = [
            ("create_comprehensive_morphological_visualizations.py",
             "Comprehensive morphological visualizations"),
        ]

        results = []
        for script, desc in scripts:
            success = self.run_script(script, desc)
            results.append((script, success))

        return results

    def organize_outputs(self):
        """Organize outputs into transformation-study directory structure."""
        self.log("Organizing Task 2 outputs...", "INFO")

        import shutil

        # Define source-to-target mappings
        mappings = [
            ('progressive_coverage_with_morphology', 'coverage-analysis'),
            ('morphological_comparative_analysis', 'morphological-rules'),
            ('comprehensive_morphological_visualizations', 'visualizations'),
        ]

        for source_name, target_name in mappings:
            source_dir = self.project_root / 'output' / source_name
            target_dir = self.output_dir / target_name

            if source_dir.exists():
                target_dir.mkdir(parents=True, exist_ok=True)

                # Copy files
                for file in source_dir.glob('*'):
                    if file.is_file():
                        target_file = target_dir / file.name
                        shutil.copy2(file, target_file)

                self.log(f"  Copied {source_name} → {target_name}", "INFO")

        self.log("✓ Output organization complete", "SUCCESS")

    def generate_summary_report(self, all_results: list):
        """Generate a summary report for Task 2."""
        self.log("Generating Task 2 summary report...", "INFO")

        report_path = self.output_dir / 'TASK2_SUMMARY_REPORT.md'

        successful = sum(1 for _, success in all_results if success)
        total = len(all_results)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Task 2: Transformation Study - Summary Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Newspapers Analyzed**: {', '.join(self.newspapers)}\n\n")

            f.write("## Research Questions\n\n")
            f.write("1. How many transformation rules capture how many difference events?\n")
            f.write("2. Which transformation direction (C→H or H→C) is easier and why?\n")
            f.write("3. How do morphological, lexical, and syntactic rules contribute to coverage?\n\n")

            f.write("## Pipeline Execution Summary\n\n")
            f.write(f"- Total scripts executed: {total}\n")
            f.write(f"- Successful: {successful}\n")
            f.write(f"- Failed: {total - successful}\n\n")

            f.write("## Generated Outputs\n\n")
            f.write("### Coverage Analysis\n")
            f.write("- Progressive coverage curves showing rule effectiveness\n")
            f.write("- Comparison of lexical, syntactic, and morphological rule contributions\n")
            f.write("- Coverage saturation analysis\n\n")

            f.write("### Morphological Rules\n")
            f.write("- Extracted morphological transformation patterns\n")
            f.write("- Feature-value transformation rules (20 morphological features)\n")
            f.write("- Rule frequency and confidence scores\n\n")

            f.write("### Visualizations\n")
            f.write("- Progressive coverage plots\n")
            f.write("- Morphological transformation matrices\n")
            f.write("- Rule effectiveness comparisons\n\n")

            f.write("## Output Directory Structure\n\n")
            f.write("```\n")
            f.write("output/transformation-study/\n")
            f.write("├── coverage-analysis/          # Progressive coverage data\n")
            f.write("├── morphological-rules/        # Extracted transformation rules\n")
            f.write("├── visualizations/             # Comprehensive visualizations\n")
            f.write("└── TASK2_SUMMARY_REPORT.md    # This report\n")
            f.write("```\n\n")

            f.write("## Key Findings\n\n")
            f.write("*(To be populated based on analysis results)*\n\n")
            f.write("- Rule coverage: X% of difference events captured by Y rules\n")
            f.write("- Most effective rule type: [lexical/syntactic/morphological]\n")
            f.write("- Transformation direction: C→H vs H→C regularity comparison\n\n")

            elapsed = datetime.now() - self.start_time
            f.write(f"\n---\n\n**Total execution time**: {elapsed}\n")

        self.log(f"✓ Summary report saved: {report_path}", "SUCCESS")

    def run(self):
        """Execute complete Task 2 pipeline."""

        print("="*80)
        print("TASK 2: TRANSFORMATION STUDY")
        print("="*80)
        print(f"\nObjective: Analyze transformation patterns and rule coverage")
        print(f"\nResearch Questions:")
        print(f"  1. How many rules capture how many difference events?")
        print(f"  2. Which transformation direction (C→H or H→C) is easier?")
        print(f"  3. How do different rule types contribute to coverage?")
        print(f"\nNewspapers: {', '.join(self.newspapers)}")
        print("="*80)
        print()

        # Verify Task 1 outputs exist
        if not self.verify_task1_outputs():
            return False

        # Execute pipeline steps
        all_results = []

        # Step 1: Rule extraction (if needed)
        all_results.extend(self.run_rule_extraction())

        # Step 2: Progressive coverage analysis
        all_results.extend(self.run_progressive_coverage_analysis())

        # Step 3: Morphological analysis
        all_results.extend(self.run_morphological_analysis())

        # Step 4: Visualizations
        all_results.extend(self.run_visualizations())

        # Organize outputs
        self.organize_outputs()

        # Generate summary report
        self.generate_summary_report(all_results)

        # Final summary
        print(f"\n{'='*80}")
        print("TASK 2 COMPLETION SUMMARY")
        print("="*80)

        successful = sum(1 for _, success in all_results if success)
        total = len(all_results)

        print(f"\nScripts executed: {total}")
        print(f"  - Successful: {successful}")
        print(f"  - Failed: {total - successful}")

        print(f"\n📊 Generated outputs:")
        print(f"  - Progressive coverage analysis")
        print(f"  - Morphological transformation rules")
        print(f"  - Comprehensive visualizations")
        print(f"  - Summary report")

        if total > 0 and successful == total:
            print(f"\n✅ Task 2 completed successfully!")
            print(f"\n📁 Check output directory for results:")
            print(f"  {self.output_dir}")
            return True
        elif total == 0:
            print(f"\n⚠️  No scripts were executed")
            return False
        else:
            print(f"\n⚠️  Task 2 completed with {total - successful} failures")
            print(f"\n📋 Review errors above for failed scripts")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Task 2: Transformation Study - Rule-based transformation analysis"
    )
    parser.add_argument(
        '--newspapers',
        nargs='+',
        default=['Times-of-India', 'Hindustan-Times', 'The-Hindu'],
        help='Newspapers to analyze (default: all three)'
    )
    parser.add_argument(
        '--skip-extraction',
        action='store_true',
        help='Skip rule extraction step (rules already extracted)'
    )
    parser.add_argument(
        '--skip-visualization',
        action='store_true',
        help='Skip visualization generation step'
    )

    args = parser.parse_args()

    runner = Task2Runner(
        newspapers=args.newspapers,
        skip_extraction=args.skip_extraction,
        skip_visualization=args.skip_visualization
    )
    success = runner.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
