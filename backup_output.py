"""
backup_output.py
================
Backup the output/ directory to a separate local git repository
(Reduced2CanonicalOutput), with incrementing version tags.

The backup repository lives at the same level as the project root, so it is
never affected by commits to the main project.  Because output/ is git-ignored
in the main project, this script is the single authoritative record of every
pipeline run.

Repository structure
--------------------
  Reduced2CanonicalOutput/
    README.md          overview + usage instructions
    CHANGELOG.md       append-only, one section per backup
    MANIFEST.md        current inventory (regenerated each backup)
    output/            copy of the project's output/ directory

Versioning
----------
  Each backup gets tag  output-v{N}  (N = 1, 2, 3, ...).
  N is determined by counting existing output-v* tags in the repo.

Usage
-----
  python backup_output.py                          # auto message
  python backup_output.py -m "added fair-comparison outputs"
  python backup_output.py --dry-run                # preview only
"""

import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from config import BASE_DIR

# ── paths ─────────────────────────────────────────────────────────────────
OUTPUT_SRC        = BASE_DIR / "output"
OUTPUT_MINIMAL_SRC = BASE_DIR / "output-minimal"
BACKUP_ROOT       = BASE_DIR.parent / "Reduced2CanonicalOutput"
OUTPUT_DEST       = BACKUP_ROOT / "output"
OUTPUT_MINIMAL_DEST = BACKUP_ROOT / "output-minimal"
CHANGELOG         = BACKUP_ROOT / "CHANGELOG.md"
MANIFEST          = BACKUP_ROOT / "MANIFEST.md"
README            = BACKUP_ROOT / "README.md"


# ══════════════════════════════════════════════════════════════════════════
# Git helpers
# ══════════════════════════════════════════════════════════════════════════

def _git(args: list, cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args, cwd=str(cwd),
        capture_output=True, text=True, check=check
    )


def _git_out(args: list, cwd: Path) -> str:
    r = _git(args, cwd, check=False)
    return r.stdout.strip()


def _get_next_version() -> int:
    """Return next version number (1 if no tags yet)."""
    tags = _git_out(["tag", "--list", "output-v*"], BACKUP_ROOT)
    if not tags:
        return 1
    nums = [int(m.group(1)) for t in tags.splitlines()
            if (m := re.match(r"output-v(\d+)$", t))]
    return max(nums) + 1 if nums else 1


def _get_project_version() -> str:
    """Return the current tag of the main project (HEAD or nearest)."""
    out = _git_out(["describe", "--tags", "--abbrev=0", "HEAD"], BASE_DIR)
    return out or "unknown"


# ══════════════════════════════════════════════════════════════════════════
# Repo initialisation
# ══════════════════════════════════════════════════════════════════════════

_README_CONTENT = """\
# Reduced2CanonicalOutput

Local backup repository for the `output/` directory of the
**ReducedToCanonicalConvDiff** project.

This repository is **not pushed to any remote**.  It maintains a versioned
history of all pipeline outputs, so that earlier runs are never lost when
the `output/` directory is regenerated.

## Directory structure

```
output/
├── task-1-comparative-study/     Task 1 — Comparative Study
├── task-2-transformation-study/  Task 2 — Transformation Study
└── task-3-complexity-similarity-study/  Task 3 — Complexity & Similarity
```

## Backup tags

Each backup creates a commit + tag:

| Tag         | Meaning                          |
|-------------|----------------------------------|
| output-v1   | First backup                     |
| output-v2   | Second backup                    |
| ...         | ...                              |

## Working with this repository

```bash
# List all backups
git tag --list "output-v*"

# See what changed between two backups
git diff output-v3..output-v4 --stat

# Restore a specific backup
git checkout output-v3

# Return to latest
git checkout master
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a human-readable record of each backup.

## Manifest

See [MANIFEST.md](MANIFEST.md) for the current output inventory.
"""


def _init_repo(dry_run: bool) -> None:
    """Create and initialise the backup repository if it does not exist."""
    if (BACKUP_ROOT / ".git").exists():
        return
    print(f"Initialising backup repository at {BACKUP_ROOT}")
    if dry_run:
        print("  [dry-run] would create and init repo"); return
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    _git(["init", "-b", "master"], BACKUP_ROOT)
    _git(["config", "user.name",  "Backup Bot"],  BACKUP_ROOT)
    _git(["config", "user.email", "backup@local"], BACKUP_ROOT)
    README.write_text(_README_CONTENT, encoding="utf-8")
    CHANGELOG.write_text("# Output Changelog\n\n", encoding="utf-8")
    MANIFEST.write_text("# Output Manifest\n\n*(generated on first backup)*\n",
                         encoding="utf-8")
    _git(["add", "-A"], BACKUP_ROOT)
    _git(["commit", "-m", "Initialize backup repository"], BACKUP_ROOT)
    print("  Repo initialised.")


# ══════════════════════════════════════════════════════════════════════════
# Sync
# ══════════════════════════════════════════════════════════════════════════

def _sync_one(src: Path, dest: Path, label: str, dry_run: bool) -> None:
    """Mirror src/ → dest/ using rsync or shutil."""
    if not src.exists():
        return
    if dry_run:
        print(f"  [dry-run] would rsync {src} → {dest}"); return
    rsync = shutil.which("rsync")
    if rsync:
        subprocess.run(
            [rsync, "-a", "--delete", str(src) + "/", str(dest) + "/"],
            check=True
        )
    else:
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
    print(f"  Synced {label} → {dest.relative_to(BACKUP_ROOT.parent)}")


def _sync_output(dry_run: bool) -> None:
    """Mirror output/ and output-minimal/ → backup repo."""
    if not OUTPUT_SRC.exists():
        print(f"[ERROR] output/ not found at {OUTPUT_SRC}"); sys.exit(1)
    _sync_one(OUTPUT_SRC,         OUTPUT_DEST,         "output/",         dry_run)
    _sync_one(OUTPUT_MINIMAL_SRC, OUTPUT_MINIMAL_DEST, "output-minimal/", dry_run)


# ══════════════════════════════════════════════════════════════════════════
# Manifest
# ══════════════════════════════════════════════════════════════════════════

def _human_size(n_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n_bytes < 1024:
            return f"{n_bytes:.1f} {unit}"
        n_bytes /= 1024
    return f"{n_bytes:.1f} TB"


def _dir_summary(path: Path) -> tuple[int, int]:
    """Return (file_count, total_bytes) for a directory."""
    count = total = 0
    for f in path.rglob("*"):
        if f.is_file():
            count += 1
            total += f.stat().st_size
    return count, total


def _manifest_section(root: Path, heading: str) -> tuple[list, int, int]:
    """Return (lines, total_files, total_bytes) for one top-level directory."""
    lines = [f"## {heading}\n",
             "| Directory | Files | Size |",
             "|-----------|------:|-----:|"]
    total_files = total_bytes = 0
    if not root.exists():
        lines.append("*(not present)*")
        lines.append("")
        return lines, 0, 0
    task_dirs = sorted(root.glob("task-*"))
    for td in task_dirs:
        n, b = _dir_summary(td)
        lines.append(f"| `{td.name}/` | {n:,} | {_human_size(b)} |")
        total_files += n; total_bytes += b
    other = [d for d in root.iterdir()
             if d.is_dir() and not d.name.startswith("task-")]
    for od in sorted(other):
        n, b = _dir_summary(od)
        lines.append(f"| `{od.name}/` | {n:,} | {_human_size(b)} |")
        total_files += n; total_bytes += b
    for f in sorted(root.glob("*.json")):
        b = f.stat().st_size
        lines.append(f"| `{f.name}` | 1 | {_human_size(b)} |")
        total_files += 1; total_bytes += b
    lines.append("")
    return lines, total_files, total_bytes


def _generate_manifest(tag: str, timestamp: str) -> str:
    lines = [
        f"# Output Manifest\n",
        f"**Last updated**: {timestamp}  |  **Backup tag**: `{tag}`\n",
        "",
    ]
    grand_files = grand_bytes = 0
    for dest, heading in [
        (OUTPUT_DEST,         "`output/` — main pipeline outputs"),
        (OUTPUT_MINIMAL_DEST, "`output-minimal/` — compact cross-newspaper outputs"),
    ]:
        sec, n, b = _manifest_section(dest, heading)
        lines.extend(sec)
        grand_files += n; grand_bytes += b

    lines += [
        f"**Grand total**: {grand_files:,} files  /  {_human_size(grand_bytes)}",
        "",
        "## Per-task breakdown (`output/`)\n",
    ]
    task_dirs = sorted(OUTPUT_DEST.glob("task-*")) if OUTPUT_DEST.exists() else []
    for td in task_dirs:
        lines.append(f"### `{td.name}/`\n")
        lines.append("| Subdirectory | Files | Size |")
        lines.append("|-------------|------:|-----:|")
        for sub in sorted(td.iterdir()):
            if sub.is_dir():
                n, b = _dir_summary(sub)
                lines.append(f"| `{sub.name}/` | {n:,} | {_human_size(b)} |")
            elif sub.is_file():
                b = sub.stat().st_size
                lines.append(f"| `{sub.name}` | 1 | {_human_size(b)} |")
        lines.append("")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════
# Changelog
# ══════════════════════════════════════════════════════════════════════════

def _changelog_entry(tag: str, timestamp: str,
                     project_ver: str, message: str,
                     diff_stat: str) -> str:
    lines = [
        f"## {tag} — {timestamp}\n",
        f"**Source project version**: `{project_ver}`  ",
        f"**Message**: {message}\n",
    ]
    if diff_stat:
        lines += ["### Changed files\n", "```", diff_stat, "```", ""]
    lines.append("---\n")
    return "\n".join(lines)


def _prepend_changelog(entry: str) -> None:
    """Insert entry at the top of CHANGELOG.md (after the heading)."""
    existing = CHANGELOG.read_text(encoding="utf-8")
    header_end = existing.find("\n\n")
    if header_end == -1:
        CHANGELOG.write_text(existing + "\n" + entry, encoding="utf-8")
    else:
        CHANGELOG.write_text(
            existing[: header_end + 2] + entry + existing[header_end + 2:],
            encoding="utf-8"
        )


# ══════════════════════════════════════════════════════════════════════════
# Main backup logic
# ══════════════════════════════════════════════════════════════════════════

def run_backup(message: str, dry_run: bool) -> None:
    _init_repo(dry_run)

    version     = _get_next_version()
    tag         = f"output-v{version}"
    timestamp   = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    project_ver = _get_project_version()

    print(f"\n{'='*60}")
    print(f"  Backup  {tag}  (project {project_ver})  [{timestamp}]")
    print(f"{'='*60}")

    # Sync files
    _sync_output(dry_run)
    if dry_run:
        print("  [dry-run] no commit created"); return

    # Stage everything to compute diff
    _git(["add", "-A"], BACKUP_ROOT)
    diff_stat = _git_out(["diff", "--cached", "--stat"], BACKUP_ROOT)
    if not diff_stat:
        print("  No changes detected — backup skipped.")
        _git(["restore", "--staged", "."], BACKUP_ROOT)
        return

    # Update docs
    manifest_text = _generate_manifest(tag, timestamp)
    MANIFEST.write_text(manifest_text, encoding="utf-8")

    entry = _changelog_entry(tag, timestamp, project_ver, message, diff_stat)
    _prepend_changelog(entry)

    # Commit
    _git(["add", "-A"], BACKUP_ROOT)
    commit_msg = f"Backup {tag}: {message} [project {project_ver}]"
    _git(["commit", "-m", commit_msg], BACKUP_ROOT)
    _git(["tag", tag], BACKUP_ROOT)

    # Summary
    changed_lines = [l for l in diff_stat.splitlines() if "|" in l]
    print(f"  Committed {len(changed_lines)} changed file(s) as {tag}")
    print(f"  Tag:    {tag}")
    print(f"  Commit: {_git_out(['rev-parse', '--short', 'HEAD'], BACKUP_ROOT)}")
    print("\nDone.")


# ══════════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Backup output/ to Reduced2CanonicalOutput local git repo"
    )
    parser.add_argument("-m", "--message", default="",
                        help="Human-readable description of this backup")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview actions without writing anything")
    args = parser.parse_args()

    message = args.message or _auto_message()
    run_backup(message, args.dry_run)


def _auto_message() -> str:
    """Generate a default message from recently modified task directories."""
    if not OUTPUT_SRC.exists():
        return "output backup"
    # Find task dirs modified in the last 24 h
    import time
    cutoff = time.time() - 86400
    recent = []
    for td in sorted(OUTPUT_SRC.glob("task-*")):
        if any(f.stat().st_mtime > cutoff for f in td.rglob("*") if f.is_file()):
            recent.append(td.name)
    if recent:
        return "updated: " + ", ".join(recent)
    return "periodic output backup"


if __name__ == "__main__":
    main()
