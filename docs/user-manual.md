# User Manual: Human-in-the-Loop Data Labeler

## Table of Contents
1. [System Requirements](#1-system-requirements)
2. [Installation & Setup](#2-installation--setup)
3. [Project Structure](#3-project-structure)
4. [Input Data Formats](#4-input-data-formats)
5. [Getting Started](#5-getting-started)
6. [Labeling Workflows](#6-labeling-workflows)
7. [Command Line Options](#7-command-line-options)
8. [Output Files](#8-output-files)
9. [Understanding Metrics](#9-understanding-metrics)
10. [Error Handling](#10-error-handling)
11. [Troubleshooting](#11-troubleshooting)
12. [Best Practices](#12-best-practices)
13. [Frequently Asked Questions](#13-frequently-asked-questions)

## 1. System Requirements

### Minimum Requirements
- **Python**: Version 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Terminal**: Command line/terminal access
- **Disk Space**: Minimal (application is ~15KB)
- **Memory**: Variable based on dataset size

### What You DON'T Need
- ❌ No external packages or dependencies
- ❌ No database installation
- ❌ No internet connection
- ❌ No special hardware

### Verification
```bash
# Check Python version
python --version

# Verify syntax
python -m py_compile label_sentences.py
```

## 2. Installation & Setup

### Quick Setup
1. **Download**: Obtain `label_sentences.py` and sample datasets
2. **Verify**: Ensure Python 3.8+ is installed
3. **Run**: Start labeling immediately (no installation required)

### Directory Creation
The application automatically creates these directories on first run:
```
logs/          # Structured JSON logs
reports/       # Human-readable reports
outputs/       # Human-labeled data files
```

## 3. Project Structure

```
human-in-the-loop-data-labeler/
├── label_sentences.py              # Main application (single file)
├── inputs/                         # Input data directory
│   ├── sentence_classifier.json    # Sample classification dataset
│   └── sentence_similarity.json    # Sample ranking dataset
├── outputs/                        # Created automatically
│   ├── sentence_classifier_HUMAN.json
│   └── sentence_similarity_HUMAN.json
├── docs/                          # Documentation
│   ├── tech-spec.md              # Technical specifications
│   └── user-manual.md            # This file
├── logs/                         # Created automatically
│   └── log_20241023_143022.json  # Timestamped JSON logs
└── reports/                      # Created automatically
    └── report_20241023_143022.txt # Human-readable reports
```

## 4. Input Data Formats

### Classification Task Format
**File**: JSON array of objects

```json
[
  {
    "sentence_base": "Turn off the lights when you leave.",
    "sentence_test": "Please switch the lights off before exiting.",
    "label_semantic_similarity": true
  },
  {
    "sentence_base": "The meeting starts at 9 AM.",
    "sentence_test": "The conference begins at 9 o'clock in the morning.",
    "label_semantic_similarity": true
  }
]
```

**Required Fields**:
- `sentence_base`: Reference sentence (string, non-empty)
- `sentence_test`: Sentence to evaluate (string, non-empty)
- `label_semantic_similarity`: Gold label (boolean, hidden from user)

### Pairwise Ranking Task Format
**File**: JSON array of objects

```json
[
  {
    "sentence_base": "The restaurant opens at noon.",
    "sentence_a": "They start serving lunch at 12:00 PM.",
    "sentence_b": "Breakfast is served until 9:00 PM.",
    "label_more_similar": "a"
  },
  {
    "sentence_base": "I need to buy groceries.",
    "sentence_a": "I should go shopping for food.",
    "sentence_b": "I want to purchase a car.",
    "label_more_similar": "a"
  }
]
```

**Required Fields**:
- `sentence_base`: Reference sentence (string, non-empty)
- `sentence_a`: First candidate sentence (string, non-empty)
- `sentence_b`: Second candidate sentence (string, non-empty)
- `label_more_similar`: Gold label (string: "a" or "b", hidden from user)

### Data Validation Rules
- All string fields must be non-empty after trimming
- Field length cannot exceed `--max-len` characters (default: 1000)
- JSON must be a valid array of objects
- Gold labels are never shown to human labelers

## 5. Getting Started

### Your First Labeling Session

1. **Navigate to Project Directory**
   ```bash
   cd /path/to/human-in-the-loop-data-labeler
   ```

2. **Run Classification Task**
   ```bash
   python label_sentences.py classify --input inputs/sentence_classifier.json
   ```

3. **Follow Terminal Prompts**
   - Read the base sentence
   - Read the test sentence
   - Enter `t` (True), `f` (False), or `s` (Skip)
   - Repeat for all items

4. **Review Results**
   - Check `outputs/` for human-labeled data
   - Review `reports/` for metrics summary
   - Examine `logs/` for detailed session data

### Basic Commands

```bash
# Get help
python label_sentences.py --help

# Classification with custom seed
python label_sentences.py classify --input inputs/sentence_classifier.json --seed 123

# Ranking with length limit
python label_sentences.py rank --input inputs/sentence_similarity.json --max-len 500

# Using full file paths
python label_sentences.py classify --input /full/path/to/data.json
```

## 6. Labeling Workflows

### Classification Workflow (`classify`)

**Purpose**: Determine if two sentences are semantically similar

**Interactive Session Example**:
```
=== Classification Labeling ===
Items to label: 30
Seed: 42 | Max length: 1000

--- Item 1/30 ---
Base:   Turn off the lights when you leave.
Test:   Please switch the lights off before exiting.

Are these sentences semantically similar? [t/f/s]: t
Labeled: t | Gold: (hidden) | Correct: Yes

--- Item 2/30 ---
Base:   The meeting starts at 9 AM.
Test:   The conference begins at 9 o'clock in the morning.

Are these sentences semantically similar? [t/f/s]: f
Labeled: f | Gold: (hidden) | Correct: No

...

Session Summary:
Total labeled: 28
Skipped: 2
Accuracy: 85.7%
Report saved to: reports/report_20241023_143022.txt
```

**Valid Inputs**:
- `t` or `true` → Mark as semantically similar
- `f` or `false` → Mark as not semantically similar
- `s` or `skip` → Skip current item

### Ranking Workflow (`rank`)

**Purpose**: Choose which sentence is more similar to the base

**Interactive Session Example**:
```
=== Pairwise Ranking Labeling ===
Items to label: 30
Seed: 42 | Max length: 1000

--- Item 1/30 ---
Base:   The restaurant opens at noon.
Option A: They start serving lunch at 12:00 PM.
Option B: Breakfast is served until 9:00 PM.

Which option is more similar to the base? [a/b/s]: a
Labeled: a | Gold: (hidden) | Correct: Yes

--- Item 2/30 ---
Base:   I need to buy groceries.
Option A: I should go shopping for food.
Option B: I want to purchase a car.

Which option is more similar to the base? [a/b/s]: a
Labeled: a | Gold: (hidden) | Correct: Yes

...

Session Summary:
Total labeled: 29
Skipped: 1
Accuracy: 89.7%
Report saved to: reports/report_20241023_143022.txt
```

**Valid Inputs**:
- `a` or `option a` → Choose Option A
- `b` or `option b` → Choose Option B
- `s` or `skip` → Skip current item

## 7. Command Line Options

### Global Options
```bash
--seed <int>          # Random seed for shuffling (default: 42)
--max-len <int>       # Maximum field length (default: 1000)
--input <path>        # Input JSON file path (required)
```

### Option Details

**`--seed`** (Reproducibility)
- Controls the order in which items are presented
- Same seed + same input = same order every time
- Useful for consistent labeling sessions
- Default: 42

**`--max-len`** (Performance/Safety)
- Maximum characters allowed in any text field
- Prevents console display issues with very long text
- Items exceeding limit are skipped with logging
- Default: 1000 characters

**`--input`** (Data Source)
- Path to JSON input file
- Can be filename (looks in `inputs/` directory) or full path
- Required parameter
- Must contain valid JSON array

### Examples
```bash
# Basic classification
python label_sentences.py classify --input my_data.json

# With custom settings
python label_sentences.py classify --input my_data.json --seed 999 --max-len 500

# Ranking task
python label_sentences.py rank --input ranking_data.json

# Using absolute path
python label_sentences.py classify --input /Users/me/data/classify.json
```

## 8. Output Files

### Human-Labeled Data (`outputs/`)

**Classification Output**:
```json
[
  {
    "sentence_base": "Turn off the lights when you leave.",
    "sentence_test": "Please switch the lights off before exiting.",
    "label_semantic_similarity": true,
    "label_semantic_similarity_human": true
  }
]
```

**Ranking Output**:
```json
[
  {
    "sentence_base": "The restaurant opens at noon.",
    "sentence_a": "They start serving lunch at 12:00 PM.",
    "sentence_b": "Breakfast is served until 9:00 PM.",
    "label_more_similar": "a",
    "label_more_similar_human": "a"
  }
]
```

### Structured Logs (`logs/`)

**Format**: JSON with complete session data

**Contents**:
- Timestamp and configuration
- Skipped items with reasons
- Individual item results (gold vs human labels)
- Calculated metrics
- Privacy-preserving text previews

**Sample Log Structure**:
```json
{
  "timestamp": "2024-10-23T14:30:22",
  "args": {
    "command": "classify",
    "seed": 42,
    "max_len": 1000,
    "input": "inputs/sentence_classifier.json"
  },
  "skips": [
    {
      "index": 5,
      "reason": "too_long:sentence_test:1200>1000",
      "previews": {
        "sentence_base": "This is a normal sentence...<hash>",
        "sentence_test": "This is an extremely long...<hash>"
      }
    }
  ],
  "items": [
    {
      "index": 0,
      "gold": true,
      "human": true,
      "correct": true
    }
  ],
  "metrics": {
    "accuracy": 0.857,
    "f1_scores": {"True": 0.85, "False": 0.86},
    "confusion_matrix": {"TP": 12, "FP": 2, "FN": 2, "TN": 10}
  }
}
```

### Human-Readable Reports (`reports/`)

**Format**: Plain text summary

**Contents**:
- Session configuration
- Processing statistics
- Skip reasons and counts
- Detailed metrics breakdown
- Output file paths
- Timestamp and duration

**Sample Report**:
```
Human-in-the-Loop Data Labeling Report
Generated: 2024-10-23 14:30:22

Configuration:
Command: classify
Input file: inputs/sentence_classifier.json
Seed: 42
Max length: 1000

Processing Summary:
Total input items: 30
Successfully labeled: 28
Skipped items: 2

Skip Reasons:
- too_long:sentence_test: 1
- user_skip: 1

Performance Metrics:
Overall Accuracy: 85.7% (24/28)

Class-wise Metrics:
True:  Precision=0.86, Recall=0.81, F1=0.83
False: Precision=0.85, Recall=0.89, F1=0.87

Confusion Matrix:
              Predicted
              True    False
Actual True    13       3
      False    1       11

Output Files:
- Human labels: outputs/sentence_classifier_HUMAN.json
- Structured log: logs/log_20241023_143022.json
- This report: reports/report_20241023_143022.txt
```

## 9. Understanding Metrics

### Classification Metrics

**Accuracy**: Overall correctness percentage
- Formula: (TP + TN) / Total
- Range: 0% to 100%
- Interpretation: How many predictions were correct overall

**Precision**: Proportion of positive predictions that were actually correct
- Formula: TP / (TP + FP)
- Interpretation: When you predicted "True", how often were you right?

**Recall**: Proportion of actual positives that were correctly identified
- Formula: TP / (TP + FN)
- Interpretation: Of all the actual "True" cases, how many did you find?

**F1 Score**: Harmonic mean of precision and recall
- Formula: 2 × (Precision × Recall) / (Precision + Recall)
- Interpretation: Balanced measure considering both precision and recall

**Confusion Matrix**:
- TP (True Positives): Correctly predicted "True"
- TN (True Negatives): Correctly predicted "False"
- FP (False Positives): Incorrectly predicted "True"
- FN (False Negatives): Incorrectly predicted "False"

### Ranking Metrics

**Accuracy**: Overall correctness of rankings
- Formula: Correct rankings / Total rankings
- Interpretation: How often you chose the more similar option

**Label-specific Metrics**: Separate precision/recall/F1 for each option ('a' and 'b')
- Helps identify if you have bias toward one option
- Useful for understanding labeling patterns

**Confusion Grid**: 2×2 matrix showing transitions
- a→a: Correctly chose option A
- a→b: Incorrectly chose B when A was correct
- b→a: Incorrectly chose A when B was correct
- b→b: Correctly chose option B

## 10. Error Handling

### Automatic Skips

Items are automatically skipped when:

**Missing or Empty Fields**:
```
Skip reason: missing_or_empty:sentence_base
Console message: Skipping item 5: missing or empty field 'sentence_base'
```

**Length Limit Exceeded**:
```
Skip reason: too_long:sentence_test:1250>1000
Console message: Skipping item 12: field 'sentence_test' too long (1250 > 1000)
```

**Invalid JSON Structure**:
```
Error: Invalid JSON format in input file
Console message: Fatal error during input processing
```

### Manual Skips

User-initiated skips during labeling:
```
Input: s
Console message: Item 15 skipped by user
Log entry: {"reason": "user_skip", "index": 15}
```

### Error Recovery

- **Graceful Degradation**: Processing continues after skips
- **Detailed Logging**: All errors recorded with context
- **Session Completion**: Partial results saved even with errors
- **Clear Messaging**: Console shows skip reasons in real-time

## 11. Troubleshooting

### Common Issues

**"File not found" Error**:
```bash
# Check if file exists
ls inputs/sentence_classifier.json

# Use full path
python label_sentences.py classify --input /full/path/to/file.json
```

**"Invalid JSON" Error**:
```bash
# Validate JSON syntax
python -m json.tool inputs/sentence_classifier.json

# Check common JSON issues:
# - Missing commas between objects
# - Trailing commas
# - Unclosed brackets/braces
```

**Low Labeling Quality**:
- Take breaks between sessions
- Use consistent criteria for similarity
- Review sample gold labels in logs
- Adjust `--seed` to change item order

**Performance Issues**:
- Reduce `--max-len` for faster processing
- Split large datasets into smaller files
- Close other applications using memory

### Debugging Steps

1. **Verify Input Data**:
   ```bash
   # Check JSON structure
   python -c "import json; print(len(json.load(open('input.json'))))"
   ```

2. **Test with Small Sample**:
   ```bash
   # Create test file with 2-3 items
   python label_sentences.py classify --input test_small.json
   ```

3. **Examine Logs**:
   ```bash
   # Check recent log for issues
   cat logs/log_*.json | python -m json.tool
   ```

4. **Validate Schema**:
   ```bash
   # Check required fields exist
   python -c "
import json
data = json.load(open('input.json'))
for i, item in enumerate(data):
    if 'sentence_base' not in item:
        print(f'Item {i}: missing sentence_base')
"
```

### Performance Optimization

**For Large Datasets**:
- Use `--max-len 500` to skip very long items
- Process in batches using multiple files
- Ensure sufficient available memory

**For Consistent Results**:
- Always use the same `--seed` for comparable sessions
- Keep original input files unchanged
- Document labeling criteria for consistency

## 12. Best Practices

### Before Labeling

1. **Understand Your Task Definition**
   - Clear criteria for "semantic similarity"
   - Consistent standards for ranking decisions
   - Handle edge cases in advance

2. **Prepare Your Environment**
   - Quiet workspace for concentration
   - Comfortable seating for extended sessions
   - Minimize distractions

3. **Validate Input Data**
   - Check JSON syntax
   - Verify required fields
   - Review sample items

### During Labeling

1. **Maintain Consistency**
   - Apply same criteria throughout session
   - Take breaks to avoid fatigue
   - Review previous decisions periodically

2. **Handle Difficult Cases**
   - Use skip (`s`) for ambiguous items
   - Document challenging patterns
   - Consider edge case policies

3. **Monitor Progress**
   - Watch accuracy metrics (if available)
   - Track skip rates
   - Pace yourself appropriately

### After Labeling

1. **Review Results**
   - Check output files for completeness
   - Review metrics in reports
   - Examine logs for issues

2. **Quality Assurance**
   - Spot-check labeled items
   - Verify skip reasons make sense
   - Consider re-labeling problematic items

3. **Documentation**
   - Save labeling criteria used
   - Note any policy decisions
   - Document session conditions

### Reproducibility

1. **Save Configuration**
   ```bash
   # Document exact command used
   python label_sentences.py classify --input data.json --seed 123 --max-len 800
   ```

2. **Preserve Input Files**
   - Don't modify original datasets
   - Version control input files
   - Backup important datasets

3. **Track Session Metadata**
   - Date and time of labeling
   - Labeler identity (if multiple)
   - Environmental conditions

## 13. Frequently Asked Questions

### General Questions

**Q: Can I pause and resume labeling sessions?**
A: Currently not supported. Each session processes all items from start to finish. For large datasets, consider splitting into smaller files.

**Q: Can multiple people label the same data?**
A: Yes, but each person should use a different output filename or coordinate to avoid overwriting each other's results.

**Q: Is there a web interface or GUI version?**
A: No, this tool is command-line only to maintain zero dependencies and simplicity.

### Technical Questions

**Q: Can I change the output directory?**
A: Not in the current version. Output files are written to `./outputs/`, `./logs/`, and `./reports/`. This can be modified by editing the source code.

**Q: What happens if I interrupt the process with Ctrl+C?**
A: The session stops immediately and all progress up to that point is lost. No partial files are saved.

**Q: Can I process multiple files at once?**
A: Not directly. You would need to write a shell script to run the tool multiple times with different input files.

### Data Questions

**Q: Can I use CSV or Excel files instead of JSON?**
A: Not directly. Input must be JSON format, but you can convert CSV/Excel to JSON using external tools.

**Q: Is there a limit to dataset size?**
A: Limited primarily by available memory. Very large datasets (>100,000 items) may cause performance issues.

**Q: Can I add custom fields to my JSON data?**
A: Yes, extra fields are preserved in the output, but they must not conflict with required schema fields.

### Privacy and Security

**Q: Are my labels and data sent anywhere?**
A: No, all processing happens locally on your machine. No network access is used.

**Q: How is privacy protected in logs?**
A: Text content is replaced with hashed previews (first 40 characters + SHA-256 hash) to maintain privacy while preserving traceability.

**Q: Can I disable the privacy hashing?**
A: This would require modifying the source code. The current design prioritizes privacy by default.

### Customization

**Q: Can I add new labeling tasks?**
A: Yes, but this requires programming knowledge. See the technical specification for guidance on extending the application.

**Q: Can I customize the metrics calculated?**
A: This would require modifying the source code in the metrics calculation functions.

**Q: Is the source code available for modification?**
A: Yes, the application is open source and can be modified to suit specific needs.
