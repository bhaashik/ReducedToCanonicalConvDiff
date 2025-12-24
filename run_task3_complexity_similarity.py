#!/usr/bin/env python3
"""
Task 3: Complexity & Similarity Study

Bidirectional MT-like scenario with information-theoretic analysis including
morphological feature transformations from v4.0 schema.

Components:
1. Bidirectional transformation (H→C and C→H) with morphological rules
2. MT evaluation metrics (BLEU, METEOR, ROUGE)
3. Perplexity analysis (register complexity)
4. Correlation analysis (transformation difficulty vs MT metrics)
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

class Task3Runner:
    """Runs complete Task 3 pipeline with morphological features."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.newspapers = ['Times-of-India', 'Hindustan-Times', 'The-Hindu']
        self.start_time = datetime.now()

    def log(self, message: str, level: str = "INFO"):
        """Log pipeline messages."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def run_script(self, script_path: str, description: str) -> bool:
        """Run a Python script and handle errors."""
        self.log(f"Running: {description}...", "TASK-3")

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
                timeout=1800  # 30 minute timeout
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

    def run(self):
        """Execute complete Task 3 pipeline."""

        print("="*80)
        print("TASK 3: COMPLEXITY & SIMILARITY STUDY")
        print("="*80)
        print(f"\nObjective: Bidirectional transformation analysis with information-theoretic")
        print(f"           complexity metrics including morphological feature transformations")
        print(f"\nSchema: v4.0 (20 morphological features)")
        print(f"Newspapers: {', '.join(self.newspapers)}")
        print("="*80)

        # Define Task 3 scripts
        scripts = [
            ("bidirectional_transformation_with_traces.py",
             "Bidirectional transformation with detailed traces"),
            ("bidirectional_transformation_system.py",
             "Bidirectional transformation with MT evaluation"),
            ("perplexity_register_analysis.py",
             "Perplexity analysis (mono & cross-register)"),
            ("directional_perplexity_analysis.py",
             "Directional complexity analysis"),
        ]

        results = []
        for script, desc in scripts:
            print(f"\n{'='*80}")
            success = self.run_script(script, desc)
            results.append((script, success))

        # Check if correlation scripts exist
        correlation_scripts = [
            ("correlation_analysis.py", "Correlation analysis (MT metrics vs perplexity)"),
            ("create_correlation_summary_viz.py", "Create correlation visualizations"),
        ]

        for script, desc in correlation_scripts:
            if (self.project_root / script).exists():
                print(f"\n{'='*80}")
                success = self.run_script(script, desc)
                results.append((script, success))

        # Summary
        print(f"\n{'='*80}")
        print("TASK 3 COMPLETION SUMMARY")
        print("="*80)

        successful = sum(1 for _, success in results if success)
        total = len(results)

        print(f"\nScripts executed: {total}")
        print(f"  - Successful: {successful}")
        print(f"  - Failed: {total - successful}")

        print(f"\n📊 Generated outputs:")
        print(f"  - Bidirectional transformations (H→C and C→H)")
        print(f"  - MT evaluation metrics (BLEU, METEOR, ROUGE)")
        print(f"  - Perplexity analysis (register complexity)")
        print(f"  - Transformation traces with morphological features")

        if successful == total:
            print(f"\n✅ Task 3 completed successfully!")
            print(f"\n📁 Check output directories for results:")
            print(f"  - output/bidirectional_evaluation/")
            print(f"  - output/perplexity_analysis/")
            print(f"  - output/directional_perplexity/")
            return True
        else:
            print(f"\n⚠️  Task 3 completed with {total - successful} failures")
            print(f"\n📋 Review errors above for failed scripts")
            return False

if __name__ == '__main__':
    runner = Task3Runner()
    success = runner.run()
    sys.exit(0 if success else 1)
