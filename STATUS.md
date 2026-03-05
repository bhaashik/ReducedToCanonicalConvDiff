# Project Status

All three research tasks are complete for all three newspapers (Times-of-India, Hindustan-Times, The-Hindu). The codebase, documentation, and LaTeX outputs are in sync.

## Tasks

| Task | Status | Output |
|------|--------|--------|
| **Task 1** — Comparative Study | Complete | `output/comparative-study/` |
| **Task 2** — Transformation Study | Complete | `output/transformation-study/` |
| **Task 3** — Complexity & Similarity Study | Complete | `output/complexity-similarity-study/` |

The pipeline is generic and documented for adaptation to any two-register, two-language, or two-variety comparison.

---

## Changelog

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
