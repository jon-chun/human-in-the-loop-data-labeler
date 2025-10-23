# Technical Specification: Human-in-the-Loop Data Labeler

## Overview

`label_sentences.py` is a single-file Python application (~373 lines) that provides interactive terminal-based workflows for collecting human labels on NLP tasks. The application operates with zero external dependencies and implements robust data validation, comprehensive metrics calculation, and privacy-preserving logging.

### Supported Tasks

1. **Binary Semantic Similarity Classification** (`classify`): Determine whether two sentences are semantically similar (True/False)
2. **Pairwise Similarity Ranking** (`rank`): Choose which of two sentences is more similar to a base sentence

Gold labels are provided in input datasets but are **never displayed** to the human operator; they are used exclusively for metrics calculation after labeling completion.

## Architecture

### Single-File Structure
The application is organized into distinct sections:

- **Lines 1-49**: Imports, constants, and utility functions
  - `ascii7()`: 7-bit ASCII normalization for console compatibility
  - `hash_preview()`: Privacy-preserving text preview generation
  - File I/O helper functions

- **Lines 50-107**: Metrics calculation functions
  - `metrics_binary()`: Binary classification metrics (accuracy, F1, confusion)
  - `metrics_ab()`: Multi-class metrics for ranking tasks

- **Lines 108-125**: Input validation and normalization
  - ASCII normalization and length limit enforcement
  - Schema validation with detailed error reporting

- **Lines 126-144**: I/O and logging infrastructure
  - Structured JSON logging with timestamped files
  - Report generation utilities

- **Lines 145-327**: Core workflow implementations
  - `run_classify()`: Classification labeling workflow
  - `run_rank()`: Pairwise ranking workflow

- **Lines 328-373**: CLI argument parsing and entry point
  - `build_parser()`: Command-line interface configuration
  - Main execution logic with error handling

### Data Flow Architecture

```
Input JSON → Validation → ASCII Normalization → Deterministic Shuffling → Interactive Labeling → Metrics Calculation → Output Generation
```

1. **Input Processing**: JSON files loaded and validated against schemas
2. **Normalization**: All text normalized to 7-bit ASCII for console compatibility
3. **Shuffling**: Deterministic ordering using configurable seed (default: 42)
4. **Labeling**: Interactive terminal UI with skip functionality
5. **Metrics**: Real-time calculation of accuracy, F1 scores, confusion matrices
6. **Output**: Human-labeled files, structured logs, and readable reports

## Data Contracts & Schemas

### Classification Input Schema
```json
{
  "sentence_base": "string",           // Reference sentence
  "sentence_test": "string",           // Sentence to evaluate
  "label_semantic_similarity": "boolean"  // Gold label (hidden)
}
```

**Output Extension**:
```json
{
  // ... original fields
  "label_semantic_similarity_human": "boolean"  // Human annotation
}
```

### Pairwise Ranking Input Schema
```json
{
  "sentence_base": "string",     // Reference sentence
  "sentence_a": "string",        // First candidate
  "sentence_b": "string",        // Second candidate
  "label_more_similar": "string" // Gold label: "a" or "b" (hidden)
}
```

**Output Extension**:
```json
{
  // ... original fields
  "label_more_similar_human": "string"  // Human annotation: "a" or "b"
}
```

## Determinism & Reproducibility

### Shuffling Algorithm
- Uses Python's `random.Random(seed)` for deterministic ordering
- Seed configurable via `--seed` parameter (default: 42)
- Consistent behavior across runs with identical inputs and seed

### ASCII Normalization
- All text normalized to 7-bit ASCII using `ascii7()` function
- Removes non-ASCII characters that could cause console display issues
- Ensures cross-platform compatibility

## Validation & Error Handling

### Input Validation Rules
- **Required Fields**: All schema-required keys must be present
- **Non-empty Strings**: String fields cannot be empty or whitespace-only
- **Length Limits**: Fields exceeding `--max-len` (default: 1000) are rejected
- **Type Validation**: Basic type checking for boolean and enum values

### Skip Categories
1. **Missing Fields**: `missing_or_empty:<field_name>`
2. **Length Violations**: `too_long:<field_name>:<length>><max_len>`
3. **User Skips**: `user_skip` (manual 's' input during labeling)
4. **Invalid Input**: Malformed JSON or unsupported data types

### Error Recovery
- Invalid records are skipped with detailed logging
- Processing continues with remaining valid records
- All skips recorded in structured logs with timestamps

## Logging & Reporting System

### Structured JSON Logs
**Location**: `./logs/log_{YYYYMMDD_HHMMSS}.json`

**Structure**:
```json
{
  "timestamp": "ISO 8601 timestamp",
  "args": {"command": "classify|rank", "seed": int, "max_len": int},
  "skips": [
    {"index": int, "reason": "skip_category", "previews": {...}}
  ],
  "items": [
    {"index": int, "gold": value, "human": value, "correct": boolean}
  ],
  "metrics": {
    "accuracy": float,
    "f1_scores": {...},
    "confusion_matrix": {...}
  }
}
```

### Privacy-Preserving Previews
- Text content replaced with `hash_preview()` function
- Format: `first_40_chars...<SHA256_hash>`
- Prevents storage of sensitive text in logs while maintaining traceability

### Human-Readable Reports
**Location**: `./reports/report_{YYYYMMDD_HHMMSS}.txt`

**Content**:
- Run configuration and summary statistics
- Skip counts and reasons
- Detailed metrics breakdown
- Output file paths and artifact locations
- Time-based performance information

## Metrics Calculation

### Classification Metrics
- **Accuracy**: (TP + TN) / (TP + TN + FP + FN)
- **Precision (Positive)**: TP / (TP + FP)
- **Recall (Positive)**: TP / (TP + FN)
- **F1 Score (Positive)**: 2 × (Precision × Recall) / (Precision + Recall)
- **Confusion Matrix**: TP, FP, FN, TN counts

### Ranking Metrics
- **Accuracy**: Correct rankings / Total rankings
- **Precision (per label)**: Correct predictions / Total predictions for label
- **Recall (per label)**: Correct predictions / Actual instances of label
- **F1 Score (per label)**: Harmonic mean of precision and recall
- **Confusion Grid**: 2×2 matrix showing label transitions

## Terminal Interface Design

### Classification UI
- **Prompt Format**: `[t/f/s]` (True/False/Skip)
- **Display**: Base sentence and test sentence shown side-by-side
- **Input Validation**: Accepts case-insensitive t/f/s, full words

### Ranking UI
- **Prompt Format**: `[a/b/s]` (Choice A/Choice B/Skip)
- **Display**: Base sentence followed by two candidate sentences
- **Input Validation**: Accepts case-insensitive a/b/s, full words

### Session Management
- Real-time progress tracking (current/total items)
- Immediate feedback on invalid inputs
- Graceful interruption handling (Ctrl+C)
- Session summary displayed on completion

## Performance Characteristics

### Time Complexity
- **Overall**: O(N) where N = number of input records
- **Validation**: O(N) with constant-time per-record checks
- **Metrics**: O(N) for calculation and aggregation
- **I/O**: O(N) for file reading and writing

### Space Complexity
- **Memory**: O(N) for storing processed records and outputs
- **Logs**: O(N) for JSON log storage (disk-based)
- **Reports**: O(1) additional memory (streaming generation)

### Scalability Considerations
- Large datasets limited primarily by available memory
- Length limits prevent memory exhaustion from extremely long strings
- Streaming design allows processing of datasets larger than available memory with modifications

## Security & Privacy Features

### Data Protection
- **No Network Access**: Entirely filesystem-based operation
- **Text Hashing**: Sensitive content replaced in logs
- **Local Processing**: No data transmission to external services
- **Deterministic Behavior**: Predictable processing without randomness

### Privacy Controls
- Configurable length limits to prevent data leakage through logs
- Hash previews maintain auditability without exposing full content
- No persistent storage of user input beyond human annotations

## Extensibility Framework

### Adding New Tasks
1. **Implement Workflow Function**: Following `run_<task>()` pattern
2. **Add CLI Subparser**: Using `argparse` subcommands
3. **Update Validation Logic**: Schema validation for new data formats
4. **Implement Metrics**: Task-specific metric calculations
5. **Configure Logging**: Structured logging for new task type

### Customization Points
- **Hash Preview Policy**: Modify `hash_preview()` for different privacy levels
- **Validation Rules**: Extend validation functions for new constraints
- **Metrics Calculations**: Add custom metric functions
- **Output Formats**: Modify report generation for different formats
- **Directory Structure**: Customize paths in `ensure_dirs()` and `make_paths()`

## Development Guidelines

### Code Style
- Type hints throughout for clarity
- Comprehensive docstrings for all functions
- Error handling with specific exception types
- Modular function design for testability

### Testing Strategy
- No external testing framework (zero dependencies principle)
- Manual testing via `python -m py_compile` for syntax validation
- Functional testing with provided sample datasets
- Reproducibility testing with different seed values

### Maintenance Considerations
- Single-file design simplifies deployment and versioning
- Standard library only ensures long-term compatibility
- Comprehensive logging aids in debugging and monitoring
- Modular structure facilitates incremental improvements
