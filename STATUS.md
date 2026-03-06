# Project Status

All three research tasks are complete for all three newspapers (Times-of-India, Hindustan-Times, The-Hindu). The codebase, documentation, and output directory are in a clean, task-oriented state (v10.0).

## Tasks

| Task | Status | Output |
|------|--------|--------|
| **Task 1** — Comparative Study | Complete | `output/task-1-comparative-study/` |
| **Task 2** — Transformation Study | Complete | `output/task-2-transformation-study/` |
| **Task 3** — Complexity & Similarity Study | Complete | `output/task-3-complexity-similarity-study/` |

The pipeline is generic and documented for adaptation to any two-register, two-language, or two-variety comparison.

---

## Changelog

### 2026-03-06 (tag `v10.0`)
- **Visualizations**: Added `generate_supplementary_visualizations.py` — config-driven script producing consistent, publication-quality figures across all three newspapers for all three tasks
- **Task 1**: Per-newspaper `visualizations/` subdirs with 7 summary figures + per-feature `feature_analysis/` subfolder; global `visualizations/` with 6 cross-newspaper comparison figures (t1g_*)
- **Task 2**: Per-newspaper `visualizations/` subdirs with 4 morphological rule figures (t2_*); global `visualizations/` with 7 figures including cross-newspaper aggregates
- **Task 3**: Per-newspaper `figures/` subdirs with 6 figures (t3_*) — identical structure for all 3 newspapers; global `figures/` with 25 figures (accumulated curves, heatmaps, cross-newspaper profiles)
- **Config files**: `output/figures_config.json` (369 entries) and `output/tables_config.json` (247 entries) — structured by global/per-newspaper × task; each entry includes path, title, description, axis labels, data source
- **Design**: One function per figure type called identically for every newspaper — guarantees structural identity for cross-newspaper comparison; t1_*/t2_*/t3_* prefixes for per-newspaper, t1g_*/t2g_*/t3g_* for global

### 2026-03-05 (tag `v9.0`)
- **Output**: Reorganised `output/` into a clean task-oriented structure — `task-1-comparative-study/`, `task-2-transformation-study/`, `task-3-complexity-similarity-study/`, `common/`, `perhaps-useful/`; no stray directories remain at the top level
- **Script**: Added `reorganize_output.py` — idempotent, dry-run capable; merges per-newspaper flat dirs into `task-1/per-newspaper/{NP}/`, routes morphological rules to `task-2/per-newspaper/{NP}/morphological-rules/`, moves bidirectional/global outputs to `task-2/global/`, moves Task 3 subtree verbatim, and archives legacy multilevel runners under `perhaps-useful/`
- **Pipeline**: Updated `run_complete_pipeline.py` constants (`COMPARATIVE_DIR`, `TRANSFORMATION_DIR`, `COMPLEXITY_DIR`) to write future runs directly to `task-N-*` directories
- **Bug fixes**: Three TED visualisation fixes in `register_comparison/visualizers/visualizer.py` — dynamic subplot grid sizing (was hardcoded 2×2), hidden unused axes when fewer algorithms have data, `np.polyfit` guarded with `std() > 0` and sorted x-axis for trend lines
- **Docs**: Updated `README.md`, `STATUS.md`, `CLAUDE.md` to reflect new output layout

### 2026-02-20
- **Docs**: Added `TUTORIAL.md` (§1–11: pipeline walkthrough; §12: controlled Stanza parser training on UD treebank data — finetuning, training-quantity control, per-register LAS evaluation, three experiment designs)
- **Docs**: Rewrote `README.md` (~260 lines, 10 sections including output layout and LaTeX directory guide)
- **Docs**: Patched `CLAUDE.md` — Python version, LaTeX 6-directory description, parser-bias caveat, `comprehensive_task3_runner.py` CLI entry
- **Env**: Added `environment.yml` (conda, platform-agnostic); updated `requirements.txt` (version floors bumped, `click`, `pillow` added, optional section for spacy/rouge-score/sacrebleu)
- **LaTeX**: Populated Task 3 deposit directory (`Canonical-Reduced-Register-Complexity-Part-3-ACL-ARR/`) — 8 figures, 4 new `.tex` tables via `LaTeX/convert_task3_tables.py`, new `\section` in `Task-3-Comprehensive-Figures.tex`
- **Git**: Removed zip archives from commit history; added `.gitattributes` with LFS tracking rules (`*.zip`, `*.pt`, `*.bin`, `*.h5`, `*.pkl`, `*.tar.gz`)

### 2026-02-19 (commit `ab9d1a0`)
- **Task 3 extended**: `multilevel_complexity_analyzer.py` v2 — character level, MATTR/MTLD/HD-D/Yule's K/Brunet's W/Honore's H, normalised MDD, constituency subordination index
- **Task 3 extended**: `multilevel_similarity_analyzer.py` v2 — character-level similarity (chrF, char n-gram Jaccard, NCD), Wasserstein distance, explicit C2H/H2C columns, symmetrised metrics
- **Task 3 new**: `transformation_based_analyzer.py` — complexity/similarity through transformation rule lens
- **Task 3 new**: `accumulated_level_analyzer.py` — L1–L6 accumulated curves with information gain
- **Task 3 new**: `comprehensive_task3_runner.py` — unified runner producing 8 figures and global CSVs
- **Task 2 extended**: Bidirectional transformation system v2 (`sentence_transformer.py`, `hypothesis_generator.py`, `candidate_ranker.py`, `ngram_scorer.py`) — 80/20 train/test split, 8 hypothesis strategies, trigram LM ranking

### 2026-02-15 (commit `707f247`)
- Tasks 1, 2, 3 completed for all three newspapers
- Extension scaffold for other varieties (Stanza training) started
