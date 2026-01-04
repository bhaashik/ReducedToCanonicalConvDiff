Project contains three tasks:
- Task-1: Comparative analysis of reduced vs canonical register using schema-based features and feature-value pairs.
- Task-2: Transformation study using morphosyntax-driven rules (coverage, effectiveness, and rule visualizations).
- Task-3: Complexity and similarity study with bidirectional transformations, perplexity, and correlations.

### Task-wise CLI
- Set up output layout: `python run_complete_pipeline.py setup`
- Reorganize existing outputs into task folders: `python run_complete_pipeline.py organize`
- Run a single task: `python run_complete_pipeline.py task1` (or `task2`, `task3`)
- Run everything: `python run_complete_pipeline.py all`
- Add `--organize-only` to skip re-running scripts and just clean layout; `--dry-run` to log actions only.

### Output layout (created under `output/`)
- `comparative-study/` → global tables/visuals + per-newspaper tables/visuals + reports
- `transformation-study/` → coverage-analysis (per-newspaper), morphological-rules, rule-effectiveness, visualizations, reports
- `complexity-similarity-study/` → bidirectional-transformation, transformation-traces, mt-evaluation, perplexity-analysis, correlation-analysis, reports

### Notes
- Earlier discussion history is in `claude-conversation-history/`.
- LaTeX write-ups live under `LaTeX/` (ignored by git); one subdirectory per task in ACL ARR format.
