#!/usr/bin/env python3
"""
Task-aware pipeline runner and organizer for the Reduced → Canonical
register study. Provides a CLI to:
- set up a clean task-wise output layout
- run individual tasks or the full pipeline
- reorganize legacy outputs into the task layout
"""

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Sequence

DEFAULT_NEWSPAPERS = ["Times-of-India", "Hindustan-Times", "The-Hindu"]
# New standardized layout under output/
COMMON_DIR = "common"
COMPARATIVE_DIR = "comparative-study"
TRANSFORMATION_DIR = "transformation-study"
COMPLEXITY_DIR = "complexity-similarity-study"
LEXICAL_DIR = "lexical"
PUNCTUATION_DIR = "punctuation"
MORPHO_DIR = "morphological"
SYNTACTIC_DIR = "syntactic"
SYN_DEP_DIR = "dependency"
SYN_CONST_DIR = "constituency"
SYN_COMBINED_DIR = "combined"
OVERVIEW_DIR = "overview"
COMPARE_EVENTS = "events"
TABLES = "tables"
VISUALS = "visualizations"
REPORTS = "reports"
TABLE_PATTERNS = ("*.csv", "*.json", "*.md", "*.tex")
VISUAL_PATTERNS = ("*.png", "*.jpg", "*.jpeg", "*.svg", "*.pdf")
TRACE_PATTERNS = ("*.csv", "*.json", "*.txt")


class PipelineExecutor:
    """Executes tasks and organizes outputs into a consistent layout."""

    def __init__(
        self,
        output_root: Path | None = None,
        newspapers: Sequence[str] | None = None,
        dry_run: bool = False,
    ):
        self.project_root = Path(__file__).parent
        self.output_root = Path(output_root) if output_root else self.project_root / "output"
        self.newspapers = list(newspapers) if newspapers else list(DEFAULT_NEWSPAPERS)
        self.dry_run = dry_run
        self.start_time = datetime.now()
        base_env = os.environ.copy()
        # Limit thread-heavy libs to avoid SHM issues in constrained environments.
        base_env.update(
            {
                "OMP_NUM_THREADS": "1",
                "MKL_NUM_THREADS": "1",
                "OPENBLAS_NUM_THREADS": "1",
                "NUMEXPR_NUM_THREADS": "1",
                "KMP_AFFINITY": "disabled",
                "KMP_INIT_AT_FORK": "FALSE",
            }
        )
        self.exec_env = base_env

    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    # ------------------------------------------------------------------ #
    # Directory layout helpers
    # ------------------------------------------------------------------ #
    def setup_directories(self):
        """Create task-wise output layout with global and per-newspaper slots."""
        base = self.output_root
        dirs: List[Path] = []

        # Common
        dirs.append(base / COMMON_DIR)

        # Task 1: Comparative Study
        comp = base / COMPARATIVE_DIR
        dirs += [
            comp,
            comp / "global" / TABLES,
            comp / "global" / VISUALS,
            comp / REPORTS,
            comp / VISUALS,
            comp / COMPARE_EVENTS,
        ]
        for paper in self.newspapers:
            dirs += [
                comp / "per-newspaper" / paper / TABLES,
                comp / "per-newspaper" / paper / VISUALS,
                comp / COMPARE_EVENTS / paper,
            ]

        # Task 2: Transformation Study
        trans = base / TRANSFORMATION_DIR
        dirs += [
            trans,
            trans / "coverage-analysis",
            trans / LEXICAL_DIR,
            trans / PUNCTUATION_DIR,
            trans / MORPHO_DIR,
            trans / SYNTACTIC_DIR / SYN_DEP_DIR,
            trans / SYNTACTIC_DIR / SYN_CONST_DIR,
            trans / SYNTACTIC_DIR / SYN_COMBINED_DIR,
            trans / OVERVIEW_DIR,
            trans / "rule-effectiveness",
            trans / VISUALS,
            trans / REPORTS,
        ]
        for paper in self.newspapers:
            dirs.append(trans / "coverage-analysis" / paper)

        # Task 3: Complexity & Similarity Study
        comp_sim = base / COMPLEXITY_DIR
        dirs += [
            comp_sim,
            comp_sim / "bidirectional-transformation",
            comp_sim / "transformation-traces",
            comp_sim / "mt-evaluation",
            comp_sim / "perplexity",
            comp_sim / "correlation",
            comp_sim / VISUALS,
            comp_sim / REPORTS,
            comp_sim / "events",
        ]

        for directory in dirs:
            if not self.dry_run:
                directory.mkdir(parents=True, exist_ok=True)
        self.log(f"Prepared {len(dirs)} output directories under {base}")

    # ------------------------------------------------------------------ #
    # File copy helpers
    # ------------------------------------------------------------------ #
    def _copy_from_dir(self, src: Path, dest: Path, patterns: Sequence[str]) -> int:
        if not src.exists():
            return 0
        if src.resolve() == dest.resolve():
            return 0

        matched_files = []
        for pattern in patterns:
            matched_files.extend(src.glob(pattern))

        if not matched_files:
            return 0

        if not self.dry_run:
            dest.mkdir(parents=True, exist_ok=True)
            for file_path in matched_files:
                target_path = dest / file_path.name
                if target_path.resolve() == file_path.resolve():
                    continue
                shutil.copy2(file_path, target_path)

        self.log(f"Collected {len(matched_files)} files from {src} -> {dest}")
        return len(matched_files)

    def _copy_reports(self, report_files: Iterable[Path], dest: Path) -> int:
        count = 0
        for file_path in report_files:
            if file_path.exists():
                if not self.dry_run:
                    dest.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest / file_path.name)
                count += 1
        if count:
            self.log(f"Collected {count} reports into {dest}")
        return count

    # ------------------------------------------------------------------ #
    # Task organization
    # ------------------------------------------------------------------ #
    def organize_comparative_study_outputs(self) -> int:
        """Collect Task 1 outputs into comparative-study layout."""
        task_root = self.output_root / COMPARATIVE_DIR
        total = 0

        # Per-newspaper tables and visualizations
        for paper in self.newspapers:
            source = self.output_root / paper
            total += self._copy_from_dir(source, task_root / "per-newspaper" / paper / "tables", TABLE_PATTERNS)
            total += self._copy_from_dir(
                source, task_root / "per-newspaper" / paper / "visualizations", VISUAL_PATTERNS
            )

        # Global aggregates and figures
        global_sources = [
            self.output_root / "AGGREGATED_CROSS_NEWSPAPER",
            self.output_root / "GLOBAL_ANALYSIS",
            self.output_root / "cross_newspaper_analysis",
        ]
        for src in global_sources:
            total += self._copy_from_dir(src, task_root / "global" / "tables", TABLE_PATTERNS)
            total += self._copy_from_dir(src, task_root / "global" / "visualizations", VISUAL_PATTERNS)

        # Publication visuals and punctuation/three-level visuals as task-wide visuals
        visual_sources = [
            self.output_root / "publication_figures",
            self.output_root / "punctuation_visualizations",
            self.output_root / "three_level_visualizations",
            task_root / "visualizations",  # keep anything already present
        ]
        for src in visual_sources:
            total += self._copy_from_dir(src, task_root / "visualizations", VISUAL_PATTERNS)

        # Reports
        reports = [
            self.output_root / "COMPLETE_ANALYSIS_SUMMARY.md",
            self.output_root / "CONTEXT_EXTRACTION_COMPLETE_SUMMARY.md",
        ]
        total += self._copy_reports(reports, task_root / "reports")
        return total

    def organize_transformation_study_outputs(self) -> int:
        """Collect Task 2 outputs into transformation-study layout."""
        task_root = self.output_root / TRANSFORMATION_DIR
        total = 0

        # Coverage analysis (per-newspaper CSVs go into per-newspaper folders)
        coverage_src = self.output_root / "progressive_coverage_with_morphology"
        total += self._copy_from_dir(coverage_src, task_root / "coverage-analysis", TABLE_PATTERNS)
        for paper in self.newspapers:
            total += self._copy_from_dir(
                coverage_src, task_root / "coverage-analysis" / paper, (f"*{paper}*.csv", f"*{paper}*.png")
            )

        # Morphological rule comparisons and related visualizations
        total += self._copy_from_dir(
            self.output_root / "morphological_comparative_analysis",
            task_root / MORPHO_DIR,
            TABLE_PATTERNS + VISUAL_PATTERNS,
        )
        total += self._copy_from_dir(
            self.output_root / "comprehensive_morphological_visualizations",
            task_root / MORPHO_DIR,
            VISUAL_PATTERNS,
        )
        total += self._copy_from_dir(
            self.output_root / "task2_visualizations", task_root / MORPHO_DIR, VISUAL_PATTERNS
        )
        total += self._copy_from_dir(
            self.output_root / "punctuation_visualizations", task_root / PUNCTUATION_DIR, VISUAL_PATTERNS
        )
        total += self._copy_from_dir(
            self.output_root / "three_level_visualizations", task_root / SYNTACTIC_DIR / SYN_COMBINED_DIR, VISUAL_PATTERNS
        )
        # Lexical and overview visuals/tables (placeholders: use publication_figures as overview)
        total += self._copy_from_dir(
            self.output_root / "publication_figures", task_root / OVERVIEW_DIR, VISUAL_PATTERNS
        )

        # Rule effectiveness summaries
        reports = [
            self.output_root / "RULE_ANALYSIS_SUMMARY.md",
            self.output_root / "TASK2_V5_SUMMARY_REPORT.md",
        ]
        total += self._copy_reports(reports, task_root / "reports")
        return total

    def organize_complexity_similarity_outputs(self) -> int:
        """Collect Task 3 outputs into complexity-similarity-study layout."""
        task_root = self.output_root / COMPLEXITY_DIR
        total = 0

        total += self._copy_from_dir(
            self.output_root / "bidirectional_evaluation",
            task_root / "mt-evaluation",
            TABLE_PATTERNS + VISUAL_PATTERNS,
        )
        total += self._copy_from_dir(
            self.output_root / "perplexity_analysis",
            task_root / "perplexity",
            TABLE_PATTERNS + VISUAL_PATTERNS,
        )
        total += self._copy_from_dir(
            self.output_root / "directional_perplexity",
            task_root / "perplexity",
            TABLE_PATTERNS + VISUAL_PATTERNS,
        )
        total += self._copy_from_dir(
            self.output_root / "correlation_analysis",
            task_root / "correlation",
            TABLE_PATTERNS + VISUAL_PATTERNS,
        )
        total += self._copy_from_dir(
            self.output_root / "multilevel_complexity",
            task_root / "perplexity",
            TABLE_PATTERNS + VISUAL_PATTERNS,
        )
        total += self._copy_from_dir(
            self.output_root / "multilevel_similarity",
            task_root / "transformation-traces",
            TABLE_PATTERNS + VISUAL_PATTERNS,
        )

        reports = [self.output_root / "MASTER_ANALYSIS_REPORT.md"]
        total += self._copy_reports(reports, task_root / "reports")
        return total

    def organize_all_outputs(self, tasks: Sequence[str] | None = None):
        """Organize outputs for the provided tasks (or all by default)."""
        selected = set(tasks) if tasks else {"task1", "task2", "task3"}
        if "task1" in selected:
            self.organize_comparative_study_outputs()
        if "task2" in selected:
            self.organize_transformation_study_outputs()
        if "task3" in selected:
            self.organize_complexity_similarity_outputs()

    # ------------------------------------------------------------------ #
    # Event generation for complexity study
    # ------------------------------------------------------------------ #
    def generate_directional_events(self):
        """
        Create direction-tagged event CSVs for complexity/similarity study.
        Uses existing canonical→headline events (Direction=C2H) and synthesizes
        a headline→canonical view (Direction=H2C) by swapping canonical/headline values.
        """
        events_dir = self.output_root / COMPLEXITY_DIR / "events"
        events_dir.mkdir(parents=True, exist_ok=True)

        for paper in self.newspapers:
            src = self.output_root / paper / "events_global.csv"
            if not src.exists():
                self.log(f"[TASK-3] Missing events file for {paper}: {src}", "WARN")
                continue
            try:
                import pandas as pd  # Local import to avoid hard dependency at startup

                df_c2h = pd.read_csv(src)
                df_c2h["Direction"] = "C2H"

                # Synthesize H2C by swapping canonical/headline fields; keep feature_id as-is.
                df_h2c = df_c2h.copy()
                swap_cols = [
                    ("canonical_value", "headline_value"),
                    ("canonical_context", "headline_context"),
                    ("deleted_punctuation", "added_punctuation"),
                ]
                for c_col, h_col in swap_cols:
                    if c_col in df_h2c.columns and h_col in df_h2c.columns:
                        df_h2c[c_col], df_h2c[h_col] = df_h2c[h_col], df_h2c[c_col]
                df_h2c["Direction"] = "H2C"

                combined = pd.concat([df_c2h, df_h2c], ignore_index=True)

                dest = events_dir / f"{paper}_events_combined.csv"
                if not self.dry_run:
                    combined.to_csv(dest, index=False)
                # Also write per-direction files for clarity
                if not self.dry_run:
                    df_c2h.to_csv(events_dir / f"{paper}_events_c2h.csv", index=False)
                    df_h2c.to_csv(events_dir / f"{paper}_events_h2c.csv", index=False)

                self.log(f"[TASK-3] Wrote directional events for {paper} -> {dest}")
            except Exception as exc:  # pylint: disable=broad-except
                self.log(f"[TASK-3] Failed to create directional events for {paper}: {exc}", "ERROR")

    # ------------------------------------------------------------------ #
    # Script runners
    # ------------------------------------------------------------------ #
    def run_script(self, script_path: str, description: str, task: str) -> bool:
        """Run a Python script and handle errors."""
        self.log(f"[{task}] Running: {description}...", "TASK")

        if self.dry_run:
            self.log(f"[{task}] Dry run: skipped execution of {script_path}", "INFO")
            return True

        script_file = self.project_root / script_path
        if not script_file.exists():
            self.log(f"Script not found: {script_path}", "ERROR")
            return False

        try:
            result = subprocess.run(
                [sys.executable, str(script_file)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=1800,  # 30 minute timeout
                env=self.exec_env,
            )

            if result.returncode == 0:
                self.log(f"✓ Completed: {description}", "SUCCESS")
                return True

            self.log(f"✗ Failed: {description}", "ERROR")
            self.log(f"Error: {result.stderr[:500]}", "ERROR")
            return False

        except subprocess.TimeoutExpired:
            self.log(f"✗ Timeout: {description}", "ERROR")
            return False
        except Exception as exc:  # pylint: disable=broad-except
            self.log(f"✗ Exception: {description} - {exc}", "ERROR")
            return False

    # ------------------------------------------------------------------ #
    # Task execution
    # ------------------------------------------------------------------ #
    def task1_comparative_study(self, run_scripts: bool = True, organize: bool = True) -> bool:
        """Task 1: Comparative Study - difference analysis."""
        self.log("=" * 80)
        self.log("TASK 1: COMPARATIVE STUDY - Difference Analysis")
        self.log("=" * 80)

        scripts = [("register_comparison/compare_registers.py", "Extract and analyze difference events")]

        results = []
        if run_scripts:
            for script, desc in scripts:
                success = self.run_script(script, desc, "TASK-1")
                results.append(success)
        else:
            results.append(True)

        if organize:
            self.organize_comparative_study_outputs()

        successful = sum(1 for success in results if success)
        self.log(f"Task 1 Complete: {successful}/{len(results)} scripts succeeded")
        return all(results)

    def task2_transformation_study(self, run_scripts: bool = True, organize: bool = True) -> bool:
        """Task 2: Transformation Study - rule-based coverage and morphology."""
        self.log("=" * 80)
        self.log("TASK 2: TRANSFORMATION STUDY - Rule-Based Analysis")
        self.log("=" * 80)

        scripts = [
            ("progressive_coverage_with_morphology.py", "Progressive coverage with morphological rules"),
            ("create_morphological_comparative_analysis.py", "Morphological comparative analysis"),
            ("create_comprehensive_morphological_visualizations.py", "Create comprehensive visualizations"),
        ]

        results = []
        if run_scripts:
            for script, desc in scripts:
                success = self.run_script(script, desc, "TASK-2")
                results.append(success)
        else:
            results.append(True)

        if organize:
            self.organize_transformation_study_outputs()

        successful = sum(1 for success in results if success)
        self.log(f"Task 2 Complete: {successful}/{len(results)} scripts succeeded")
        return all(results)

    def task3_complexity_similarity_study(self, run_scripts: bool = True, organize: bool = True) -> bool:
        """Task 3: Complexity & Similarity Study - bidirectional analysis."""
        self.log("=" * 80)
        self.log("TASK 3: COMPLEXITY & SIMILARITY STUDY - Bidirectional Analysis")
        self.log("=" * 80)

        scripts = [
            ("bidirectional_transformation_with_traces.py", "Bidirectional transformation with detailed traces"),
            ("bidirectional_transformation_system.py", "Bidirectional transformation with MT eval"),
            ("perplexity_register_analysis.py", "Perplexity analysis (mono & cross-register)"),
            ("directional_perplexity_analysis.py", "Directional complexity analysis"),
            ("correlation_analysis.py", "Correlation analysis (MT metrics vs perplexity)"),
            ("create_correlation_summary_viz.py", "Create correlation visualizations"),
        ]

        results = []
        if run_scripts:
            for script, desc in scripts:
                success = self.run_script(script, desc, "TASK-3")
                results.append(success)
        else:
            results.append(True)

        if organize:
            self.organize_complexity_similarity_outputs()

        successful = sum(1 for success in results if success)
        self.log(f"Task 3 Complete: {successful}/{len(results)} scripts succeeded")
        return all(results)

    # ------------------------------------------------------------------ #
    # Reporting
    # ------------------------------------------------------------------ #
    def generate_master_report(self):
        """Generate master report combining all three tasks."""
        self.log("=" * 80)
        self.log("Generating Master Report")
        self.log("=" * 80)

        report_path = self.output_root / "MASTER_ANALYSIS_REPORT.md"
        if self.dry_run:
            self.log(f"[Dry run] Would write report to {report_path}")
            return

        with open(report_path, "w", encoding="utf-8") as handle:
            handle.write(self.create_master_report_content())

        self.log(f"✓ Created master report: {report_path}")

    def create_master_report_content(self) -> str:
        """Create content for master report."""
        report = []
        report.append("# Cross-Register Morphosyntactic Analysis: Complete Report")
        report.append("")
        report.append(f"**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        report.append("## Research Framework")
        report.append("")
        report.append(
            "This study investigates morphosyntactic complexity and similarity differences "
            "between reduced register news headlines and their full-sentence canonical versions "
            "using an information-theoretic, controlled experimental approach."
        )
        report.append("")
        report.append("**Key Characteristics**:")
        report.append("- **Morphosyntactic focus**: Purely formal patterns (not semantic/pragmatic)")
        report.append("- **Information-theoretic**: Perplexity, entropy, pattern diversity")
        report.append("- **Controlled experiments**: Conditional language model approach (linguistic)")
        report.append("- **Bidirectional**: Studies both C→H and H→C transformations")
        report.append("")
        report.append("## Three Research Tasks")
        report.append("")
        report.append("### Task 1: Comparative Study")
        report.append("")
        report.append("**Objective**: Quantitative analysis of morphosyntactic differences")
        report.append("")
        report.append("**Methods**:")
        report.append("- Feature-value schema for difference classification")
        report.append("- Constituency and dependency parse comparison")
        report.append("- Event-level statistical analysis (global and per-newspaper)")
        report.append("")
        report.append("**Output**: `output/comparative-study/`")
        report.append("")
        report.append("### Task 2: Transformation Study")
        report.append("")
        report.append("**Objective**: How many rules capture how many transformations?")
        report.append("")
        report.append("**Methods**:")
        report.append("- Morphological rule extraction and integration")
        report.append("- Progressive coverage analysis (per-newspaper and global)")
        report.append("- Rule effectiveness measurement and visualizations")
        report.append("")
        report.append("**Output**: `output/transformation-study/`")
        report.append("")
        report.append("### Task 3: Complexity & Similarity Study")
        report.append("")
        report.append("**Objective**: Which transformation direction is more complex?")
        report.append("")
        report.append("**Methods**:")
        report.append("- Bidirectional MT-like transformation scenario with traces")
        report.append("- Perplexity analysis (mono-register, cross-register, directional)")
        report.append("- Correlation analysis (complexity vs performance)")
        report.append("")
        report.append("**Output**: `output/complexity-similarity-study/`")
        report.append("")
        report.append("## Directory Structure")
        report.append("")
        report.append("```")
        report.append("output/")
        report.append("├── comparative-study/           # Task 1: Difference analysis")
        report.append("│   ├── global/{tables,visualizations}")
        report.append("│   ├── per-newspaper/<paper>/{tables,visualizations}")
        report.append("│   └── reports/")
        report.append("│")
        report.append("├── transformation-study/        # Task 2: Rule coverage")
        report.append("│   ├── coverage-analysis[/<paper>]/")
        report.append("│   ├── morphological-rules/")
        report.append("│   ├── rule-effectiveness/")
        report.append("│   ├── visualizations/")
        report.append("│   └── reports/")
        report.append("│")
        report.append("└── complexity-similarity-study/ # Task 3: Bidirectional analysis")
        report.append("    ├── bidirectional-transformation/")
        report.append("    ├── transformation-traces/")
        report.append("    ├── mt-evaluation/")
        report.append("    ├── perplexity-analysis/")
        report.append("    ├── correlation-analysis/")
        report.append("    └── reports/")
        report.append("```")
        report.append("")
        report.append("---")
        report.append("")
        report.append(f"**Pipeline executed**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Newspapers analyzed**: {', '.join(self.newspapers)}")
        report.append("")
        return "\n".join(report)

    # ------------------------------------------------------------------ #
    # High level orchestrators
    # ------------------------------------------------------------------ #
    def run_complete_pipeline(self):
        """Execute the complete three-task pipeline."""
        self.log("=" * 80)
        self.log("STARTING COMPLETE PIPELINE EXECUTION")
        self.log("=" * 80)
        self.log(f"Project root: {self.project_root}")
        self.log(f"Output directory: {self.output_root}")
        self.log("")

        self.setup_directories()
        # Prepare directional events for complexity/similarity (C2H baseline).
        self.generate_directional_events()

        task1_success = self.task1_comparative_study()
        task2_success = self.task2_transformation_study()
        task3_success = self.task3_complexity_similarity_study()

        self.generate_master_report()

        elapsed = datetime.now() - self.start_time
        self.log("=" * 80)
        self.log("PIPELINE EXECUTION COMPLETE")
        self.log("=" * 80)
        self.log(f"Task 1 (Comparative Study): {'✓ SUCCESS' if task1_success else '✗ FAILED'}")
        self.log(f"Task 2 (Transformation Study): {'✓ SUCCESS' if task2_success else '✗ FAILED'}")
        self.log(f"Task 3 (Complexity & Similarity): {'✓ SUCCESS' if task3_success else '✗ FAILED'}")
        self.log(f"Total elapsed time: {elapsed}")
        self.log("=" * 80)
        return task1_success and task2_success and task3_success


# ---------------------------------------------------------------------- #
# CLI
# ---------------------------------------------------------------------- #
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Task-aware pipeline runner for comparative, transformation, and complexity studies.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="Root directory for outputs (default: <repo>/output)",
    )
    parser.add_argument(
        "--newspapers",
        type=str,
        default=",".join(DEFAULT_NEWSPAPERS),
        help="Comma-separated list of newspapers to organize (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Prepare layout and organization without copying or running scripts.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("setup", help="Create task-wise output layout only.")
    subparsers.add_parser("organize", help="Reorganize legacy outputs into the task layout.")
    subparsers.add_parser("task1", help="Run Task 1 pipeline and organize outputs.")
    subparsers.add_parser("task2", help="Run Task 2 pipeline and organize outputs.")
    subparsers.add_parser("task3", help="Run Task 3 pipeline and organize outputs.")
    subparsers.add_parser("all", help="Run all tasks sequentially and organize outputs.")
    subparsers.add_parser("report", help="Regenerate the master analysis report only.")

    for name in ["task1", "task2", "task3", "all"]:
        sub = subparsers.choices[name]
        sub.add_argument(
            "--organize-only",
            action="store_true",
            help="Skip running scripts and only organize outputs for this task.",
        )

    return parser.parse_args()


def main():
    args = parse_args()
    papers = [item.strip() for item in args.newspapers.split(",") if item.strip()]
    executor = PipelineExecutor(output_root=args.output_root, newspapers=papers, dry_run=args.dry_run)

    if args.command == "setup":
        executor.setup_directories()
        return

    if args.command == "organize":
        executor.setup_directories()
        executor.organize_all_outputs()
        return

    if args.command == "task1":
        executor.setup_directories()
        executor.task1_comparative_study(run_scripts=not args.organize_only, organize=True)
        return

    if args.command == "task2":
        executor.setup_directories()
        executor.task2_transformation_study(run_scripts=not args.organize_only, organize=True)
        return

    if args.command == "task3":
        executor.setup_directories()
        executor.task3_complexity_similarity_study(run_scripts=not args.organize_only, organize=True)
        return

    if args.command == "all":
        executor.setup_directories()
        executor.task1_comparative_study(run_scripts=not args.organize_only, organize=True)
        executor.task2_transformation_study(run_scripts=not args.organize_only, organize=True)
        executor.task3_complexity_similarity_study(run_scripts=not args.organize_only, organize=True)
        executor.generate_master_report()
        return

    if args.command == "report":
        executor.setup_directories()
        executor.generate_master_report()
        return


if __name__ == "__main__":
    main()
