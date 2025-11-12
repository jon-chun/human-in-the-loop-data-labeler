# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview
**Human-in-the-loop Data Labeler** — Educational tool for interactive sentence classification and ranking tasks with timing/annotator metadata and session management.

## Development Commands

### Setup
```bash
python3 -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
```

### Running the CLI
```bash
# Classification (binary semantic similarity)
python src/label_sentences.py classify --input inputs/sentence_classifier.json \
  --annotator-id u001 --annotator-name "Ada Lovelace" --annotator-email ada@example.com

# Ranking (pairwise comparison)
python src/label_sentences.py rank --input inputs/sentence_similarity.json \
  --annotator-id u001 --annotator-name "Ada Lovelace" --annotator-email ada@example.com

# Merge outputs
python src/label_sentences.py merge
```

### Code Quality
```bash
# Lint
ruff check src/

# Type check
mypy src/

# Format
ruff format src/
```

### Testing
No automated tests currently exist. Manual testing is done by running the CLI commands.

## Architecture

### Entry Point Flow
- `src/label_sentences.py` → delegates to `hil.cli.main()`
- CLI parser in `hil.cli` routes to workflow modules:
  - `hil.workflows.classify` — binary t/f labeling
  - `hil.workflows.rank` — pairwise a/b labeling
  - `hil.merge` — deduplication/merging

### Core Module Structure (`src/hil/`)
- **`workflows/`** — Command implementations (classify, rank)
- **`config.py`** — Loads `config.yaml` (seed, max_len, dirs, features)
- **`paths.py`** — Path management using `Paths` class; auto-creates dirs, derives output filenames
- **`resume.py`** — Session resumption logic via `check_existing_output()`
- **`logging_utils.py`** — `SessionLog` class for per-session JSON logs with UUID, timing, and metrics
- **`metrics.py`** — Confusion matrices and metrics for binary/ab classification
- **`validation.py`** — ASCII validation and length checks
- **`io_utils.py`** — JSON read/write utilities
- **`reporting.py`** — Plain-text report generation
- **`merge.py`** — Deduplicates outputs by composite key, writes to `outputs-merged/`

### Workflow Pattern
Both `classify.py` and `rank.py` follow the same structure:
1. Load input JSON, shuffle by seed
2. Check for existing output (resume or review mode)
3. Initialize `SessionLog` with annotator metadata
4. Interactive loop: display sentences, capture human labels with timing (`elapsed_ms`)
5. Write output JSON with `label_*_human` field + `_annotator` metadata
6. Compute metrics (confusion matrix, accuracy, F1)
7. Finalize log and write report

**Resume/Review Logic** (in `resume.py`):
- Detects partial sessions → resume from last unlabeled item
- Detects complete sessions → offer review/revision mode
- In review mode, shows existing label and allows Enter to keep or new input to change

### Output Structure
- **Human labels**: `outputs/{inputname}_HUMAN.json` (single file per input, accumulates items across sessions)
- **Logs**: `logs/log_{timestamp}.json` (one per session, includes session_id, timing per item, metrics)
- **Reports**: `reports/report_{timestamp}.txt` (human-readable summary)
- **Merged**: `outputs-merged/merged_{timestamp}.json` (deduplicated across all outputs)

### Configuration
`config.yaml` controls:
- `seed`, `max_len` — defaults for shuffling and validation
- `dirs` — output directories (created automatically by `Paths`)
- `LABELING_OVERLAP` — metadata for multi-annotator studies
- `features.record_per_item_timing` — enables `elapsed_ms` tracking

## Development Workflow

### Branch Naming
- `feat/` — new features
- `fix/` — bug fixes
- `docs/` — documentation changes

### Commit Messages
Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat: add session review mode`
- `fix: handle empty input files`
- `docs: update technical spec`

### Pull Requests
- Keep PRs atomic (one feature/fix per PR)
- Ensure code passes `ruff check` and `mypy` before committing
- GitHub Actions configured for Claude Code integration (`.github/workflows/claude.yml`, `claude-code-review.yml`)

## Utilities (`src/utils/`)
- **`util_edit_json.py`** — Manual JSON editing utilities
- **`util_reporting.py`** — Additional reporting tools
- **`util_metaanalysis.py`** — Cross-session analysis
- **`util_human_assignments.py`** — Multi-annotator assignment generation
- **`util_tui_textual.py`** — Experimental Textual-based TUI (not enabled by default)

## Key Design Decisions
- **Single output file per input**: Accumulates labels across sessions to support resume/review
- **Per-item timing**: Captures `elapsed_ms` for each labeled item (user response time)
- **Annotator metadata**: Embeds `_annotator` dict (id, name, email) in each output record
- **Deterministic shuffling**: Uses fixed seed for reproducibility in multi-annotator studies
- **ASCII-only enforcement**: Validates fields for ASCII + length to prevent encoding issues






# "Merge to Main" Workflow

When the user says "merge to main", follow this complete workflow:

## Pre-Merge Preparation
1. **Pull latest main** - Fetch and merge the latest changes from remote main
2. **Validate branch naming** - Create a conventional commits conform branch using kebab-case:
   - `feat/feature-name` for new features
   - `fix/bug-name` for bug fixes
   - `docs/update-name` for documentation
   - `refactor/change-name` for code refactoring
   - `test/test-name` for test additions
   - `chore/task-name` for maintenance tasks
  
## Commit and Push
3. **Run pre-commit checks** - Execute tests and linters if applicable; report any failures
4. **Commit changes** - Use detailed conventional commits messages:
   - Format: `type(scope): description`
   - Examples: `feat(auth): add user authentication`, `fix(dashboard): resolve memory leak`
   - Include body with details if changes are complex
5. **Check for conflicts** - Ensure branch can merge cleanly with main
6. **Push branch** - Push the branch to remote
  
## Pull Request Creation
1. **Create Pull Request** - Generate PR to main with:
   - Descriptive title matching commit message format
   - Body containing: changes summary, testing done, breaking changes (if any)
   - Link related issues if applicable
   - 
## Confirmation and Merge
1. **Wait for CI/CD** - Allow automated checks to complete; report status
2. **Present summary** - Show user:
   - All commits to be merged
   - Files changed
   - CI/CD status
   - Any warnings or conflicts
3.  **Request confirmation** - Ask: "Ready to merge to main? (yes/no)"
4.  **Merge PR** - After confirmation, merge using squash or merge commit (ask user preference)
5.  **Verify merge** - Confirm merge was successful
   
## Cleanup
1.  **Delete remote branch** - Remove the feature branch from remote
2.  **Update local main** - Pull the updated main branch locally
3.  **Confirm completion** - Report successful merge with commit SHA
   
## Error Handling
- **If tests fail**: Report failures and ask whether to fix or abort
- **If merge conflicts exist**: Report conflicts and ask user to resolve manually
- **If PR creation fails**: Report error and suggest manual creation
- **If CI/CD fails**: Report failures and ask whether to fix or abort