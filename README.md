# Human-in-the-Loop Data Labeler

A single-file Python application for collecting human labels on NLP tasks with **zero external dependencies**. This tool provides interactive terminal-based labeling workflows for classification and ranking tasks.

## Features

- 🎯 **Two labeling workflows**: Binary classification and pairwise ranking
- 🛡️ **Zero dependencies**: Uses only Python standard library
- 🔧 **Robust data handling**: ASCII normalization, length limits, validation
- 📊 **Comprehensive metrics**: Accuracy, F1 scores, confusion matrices
- 📝 **Structured logging**: JSON logs with privacy-preserving hashes
- 📈 **Detailed reports**: Human-readable summaries with metrics
- 🎲 **Reproducible**: Deterministic shuffling with configurable seeds
- ⚡ **Skip functionality**: Graceful handling of invalid or ambiguous data

## Quick Start

```bash
# Classification labeling (binary semantic similarity)
python label_sentences.py classify --input sentence_classifier.json

# Pairwise ranking labeling (choose more similar sentence)
python label_sentences.py rank --input sentence_similarity.json

# Get help and see all options
python label_sentences.py --help
```

## Repository Structure

```
.
├── label_sentences.py          # Main application (single-file, ~373 lines)
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

## Supported Tasks

### Classification (`classify`)
Binary semantic similarity labeling:
- **Input**: Two sentences to compare
- **Output**: True/False for semantic similarity
- **Use case**: Training sentence similarity classifiers

### Ranking (`rank`)
Pairwise similarity ranking:
- **Input**: Base sentence + two candidate sentences
- **Output**: Choose 'a' or 'b' (more similar to base)
- **Use case**: Training semantic ranking models

## Command Options

- `--seed <int>`: Random seed for reproducible shuffling (default: 42)
- `--max-len <int>`: Maximum character length per field before skipping (default: 1000)
- `--input <path>`: Required input JSON file path. If filename only, automatically looks in `inputs/` directory

## Metrics & Reporting

- **Classification**: Accuracy, recall/F1 per class, confusion matrix (TP/FP/FN/TN)
- **Ranking**: Accuracy, recall/F1 per label ('a','b'), 2x2 confusion grid
- **Structured logs**: `./logs/log_{timestamp}.json` with hashed previews for privacy
- **Human reports**: `./reports/report_{timestamp}.txt` with comprehensive summaries

## Requirements

- Python 3.8+ (for type hints and f-strings)
- No external dependencies (standard library only)
- Terminal/console access for interactive labeling

## Documentation

- 📖 [User Manual](docs/user-manual.md) - Complete usage instructions and examples
- 🔧 [Technical Specifications](docs/tech-spec.md) - Architecture and implementation details

## License

MIT License - see LICENSE file for details.
