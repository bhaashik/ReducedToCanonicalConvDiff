#!/usr/bin/env python3
"""
Task 1: Comparative Study - Process All Newspapers with v4.0 Schema

Runs the comparison analysis for all three newspapers with the enriched
morphological feature schema (v4.0).
"""

import subprocess
import sys
from pathlib import Path

# Newspapers to process
NEWSPAPERS = ["Times-of-India", "Hindustan-Times", "The-Hindu"]

def run_newspaper_comparison(newspaper: str):
    """Run comparison for a specific newspaper."""
    print(f"\n{'='*80}")
    print(f"PROCESSING: {newspaper}")
    print(f"{'='*80}\n")

    # Path to compare_registers.py
    script_path = Path(__file__).parent / "register_comparison" / "compare_registers.py"

    # Modify the newspaper name in the script temporarily
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find and replace current_news_paper_name
    original_line = 'current_news_paper_name = "Times-of-India"'
    if original_line in content:
        modified_content = content.replace(
            original_line,
            f'current_news_paper_name = "{newspaper}"'
        )

        # Write modified content
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)

        # Run the script
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=Path(__file__).parent,
                capture_output=False,  # Show output in real-time
                text=True,
                timeout=1800  # 30 minute timeout per newspaper
            )

            if result.returncode == 0:
                print(f"\n✓ {newspaper} completed successfully")
                return True
            else:
                print(f"\n✗ {newspaper} failed with return code {result.returncode}")
                return False

        except subprocess.TimeoutExpired:
            print(f"\n✗ {newspaper} timed out")
            return False
        except Exception as e:
            print(f"\n✗ {newspaper} error: {e}")
            return False
        finally:
            # Restore original content
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(content)
    else:
        print(f"✗ Could not find newspaper configuration line in script")
        return False


def main():
    print("="*80)
    print("TASK 1: COMPARATIVE STUDY - ALL NEWSPAPERS")
    print("Schema: diff-ontology-ver-4.0.json (Enriched with 20 morphological features)")
    print("="*80)

    results = {}
    for newspaper in NEWSPAPERS:
        success = run_newspaper_comparison(newspaper)
        results[newspaper] = success

    # Summary
    print("\n" + "="*80)
    print("TASK 1 COMPLETION SUMMARY")
    print("="*80)

    for newspaper, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{newspaper}: {status}")

    successful = sum(1 for s in results.values() if s)
    print(f"\nTotal: {successful}/{len(NEWSPAPERS)} newspapers processed successfully")

    if successful == len(NEWSPAPERS):
        print("\n✅ All newspapers processed! Output in output/<newspaper>/ directories")
        print("\n📊 Generated files per newspaper:")
        print("  - events_global.csv (all difference events)")
        print("  - comprehensive_analysis.json")
        print("  - comprehensive_report.md")
        print("  - Various visualizations (.png files)")
        print("\n⚠️  NEXT STEP: Manual verification by user before proceeding to Tasks 2 & 3")
    else:
        print("\n⚠️  Some newspapers failed. Please check errors above.")
        sys.exit(1)


if __name__ == '__main__':
    main()
