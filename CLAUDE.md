# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a human-in-the-loop data labeling tool for NLP tasks, built as a single-file Python application with **zero external dependencies**. The tool provides two main labeling workflows:

1. **Classification** (`classify`): Binary semantic similarity labeling (True/False)
2. **Ranking** (`rank`): Pairwise similarity labeling (choose 'a' or 'b')

The application is designed as a CLI tool with structured logging and comprehensive reporting capabilities.

## Commands

### Core Usage
```bash
# Run classification labeling (auto-detects inputs/ directory)
python label_sentences.py classify --input sentence_classifier.json

# Run pairwise ranking labeling (auto-detects inputs/ directory)
python label_sentences.py rank --input sentence_similarity.json

# Or use full paths
python label_sentences.py classify --input inputs/sentence_classifier.json

# Get help
python label_sentences.py --help
```

### Command Options
- `--seed <int>`: Random seed for reproducible shuffling (default: 42)
- `--max-len <int>`: Maximum character length per field before skipping (default: 1000)
- `--input <path>`: Required input JSON file path. If filename only, automatically looks in `inputs/` directory

## Architecture

### Single-File Structure
The entire application is contained in `label_sentences.py` (~599 lines) with these key sections:

- **Lines 1-49**: Imports, constants, utility functions (`ascii7`, `hash_preview`, file helpers)
- **Lines 50-107**: Metrics calculation functions (`metrics_binary`, `metrics_ab`)
- **Lines 108-125**: Input validation with ASCII normalization and length limits
- **Lines 126-201**: I/O helpers for structured logging, report generation, and session management
- **Lines 202-552**: Core workflow functions (`run_classify`, `run_rank`) with resume/review capabilities
- **Lines 554-599**: CLI argument parsing, path resolution, and main entry point

### Data Flow
1. **Input**: JSON arrays from `inputs/` directory with specific schemas (see docs/user-manual.md)
2. **Processing**: Deterministic shuffling, ASCII normalization, validation
3. **Labeling**: Interactive terminal UI with skip functionality
4. **Output**:
   - Human-labeled data (`./outputs/{root}_HUMAN{ext}`)
   - Structured JSON logs (`./logs/log_{timestamp}.json`)
   - Human-readable reports (`./reports/report_{timestamp}.txt`)

### Key Design Patterns
- **Deterministic behavior**: Fixed seed for reproducible item ordering
- **Privacy-aware**: Logs store hashed previews, not full text content
- **Robust validation**: Skips invalid records with detailed logging
- **Metrics calculation**: Binary and multi-class confusion matrices with F1 scores
- **Session resumption**: Automatically detects incomplete sessions and allows continuation from where you left off
- **Review mode**: Completed sessions can be reviewed/revised, showing existing labels with option to keep or change them
- **Incremental saving**: Preserves existing labeled data when resuming, preventing data loss

## Data Schemas

### Classification Input
```json
{
  "sentence_base": "string",
  "sentence_test": "string",
  "label_semantic_similarity": boolean
}
```

### Ranking Input
```json
{
  "sentence_base": "string",
  "sentence_a": "string",
  "sentence_b": "string",
  "label_more_similar": "a"|"b"
}
```

## Testing

The project uses **no external testing framework**. To test:

```bash
# Basic syntax validation
python -m py_compile label_sentences.py

# Functional testing with sample data
python label_sentences.py classify --input sentence_classifier.json
python label_sentences.py rank --input sentence_similarity.json
```

## File Structure

```
.
├── label_sentences.py          # Main application (single-file)
├── inputs/
│   ├── sentence_classifier.json    # Sample classification dataset
│   └── sentence_similarity.json    # Sample ranking dataset
├── outputs/                   # Created automatically (human-labeled files)
├── docs/
│   ├── tech-spec.md           # Technical specifications
│   └── user-manual.md         # Detailed user guide
├── logs/                      # Created automatically (JSON logs)
└── reports/                   # Created automatically (TXT reports)
```

## Development Notes

- **Zero dependencies**: Uses only Python standard library
- **Python 3.8+ required**: For type hints and f-strings
- **ASCII normalization**: All text normalized to 7-bit ASCII for console compatibility
- **Structured logging**: JSON logs contain hashed previews for privacy
- **Reproducible**: Fixed seed ensures consistent labeling order across runs
- **Error handling**: Graceful skipping of invalid records with detailed logging

## Session Management

### Resume Functionality
The tool automatically detects existing output files and provides smart session management:

- **Incomplete Sessions**: Automatically resumes from the last processed item
- **Complete Sessions**: Prompts user to review/revise existing labels (with confirmation)
- **Session Tracking**: Uses item content matching to identify already-labeled records
- **Progress Preservation**: Existing labels are preserved in output files during resume

### How Sessions Work
1. When you run a command, the tool checks for existing `outputs/{filename}_HUMAN.json`
2. If found, it compares existing output with input to determine completion status
3. For incomplete sessions: resumes automatically from the next unlabeled item
4. For complete sessions: asks if you want to review/revise (Y/n prompt)
5. During review: shows current label and allows keeping (Enter) or changing it

### Important Notes
- Session state is determined by matching sentence content, not by position
- The same `--seed` should be used for consistent ordering across sessions
- Review mode processes all items sequentially (no partial review)
- Logs track resume state with `resuming_from` and `existing_completed` fields

## Adding New Tasks

To add new labeling tasks:

1. Implement `run_<task>()` function following existing pattern (see `run_classify` at line 204 or `run_rank` at line 377)
2. Add subparser in `build_parser()` (line 568)
3. Update validation logic and metrics calculation as needed
4. Implement session management using `check_existing_output()` pattern
5. Follow existing logging/reporting structure with timestamped files