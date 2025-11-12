# CLAUDE.md (Starter)

## Overview
This repository contains the **Human-in-the-loop Data Labeler** built for interactive sentence classification and ranking tasks.
The refactor modularizes code, adds per-item timing and annotator metadata, and supports advanced logging and merging.

## Contract for Claude Code
- Use `/init` to initialize context.
- Use `/issue <num>` to handle GitHub issues automatically (plan → code → test → PR → review → merge).
- Branches follow `feat/`, `fix/`, or `docs/` naming conventions.
- Always ensure CI (`CI`, `commitlint`) passes before merge.
- After merge, `/clear` resets context.

## Repository Layout
```
src/
  label_sentences.py      # Main CLI entrypoint
  hil/                    # Core modules (io, metrics, validation, etc.)
  utils/                  # Support utilities for editing, reporting, TUI, etc.
docs/
  doc_tech-spec.md
  user-manual.md
  lab_instructor-manual.md
.github/
  workflows/
    ci.yml
    commitlint.yml
config.yaml
pyproject.toml
```

## Slash Commands
- `/issue <num>` → Automate feature/bug issue flow.
- `/analyze outputs` → Summarize labeling and agreement stats.
- `/merge` → Merge all HUMAN outputs into `outputs-merged/`.

## Best Practices
- Atomic PRs only.
- Commit messages follow Conventional Commits.
- Review by Code Owners enforced.
