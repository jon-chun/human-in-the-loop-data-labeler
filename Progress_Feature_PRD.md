# PRD: Progress Tracking Feature

## Objective
Enable automatic, persistent progress tracking across labeling sessions with a dynamic in-terminal progress bar and resume capability, while preserving the tool’s zero-dependency, single-file design.

## 1. Goals
- Show clear real-time progress during labeling (x/n, percent, bar)
- Save progress automatically after every question
- Resume from last labeled item automatically after restart
- Handle modified datasets gracefully (using record hashes)
- Integrate smoothly with timing and accuracy logging
- Maintain no external dependencies

## 2. User Experience
### 2.1 Display
```
Progress: [███████-----] 34/100 (34%)
```
- Updates dynamically after each label
- Keeps the rest of the labeling UI unchanged (t/f/s or a/b/s)

### 2.2 Session Behavior
- Detect and resume automatically from last progress
- Auto-save state after each label
- Skip already completed or user-skipped records

## 3. Architecture and Data Flow
### 3.1 New Directory
```
performance/
├── session_state.json
├── session_<timestamp>.json
```
### 3.2 Data Flow
```
Input JSON → Validate → Load Progress → Label → Auto-save → Report
```

## 4. Data Model
### Unified Session File (`performance/session_<timestamp>.json`)
```json
{
  "session_id": "20251029_2135",
  "task_type": "classify",
  "input_file": "inputs/sentence_classifier.json",
  "total_records": 100,
  "progress": {"completed": 34, "skipped": 2, "remaining": 64, "percent_complete": 0.34},
  "question_times": [{"record_hash": "abcd1234", "start": 1730244515.123, "end": 1730244522.789, "duration": 7.666}],
  "accuracy_summary": {"correct": 30, "incorrect": 4, "skipped": 2, "accuracy": 0.882},
  "last_saved": "2025-10-29T21:35:15"
}
```

## 5. Implementation Details
### 5.1 Progress Bar Logic
```python
filled = int(20 * completed / total)
bar = "█" * filled + "-" * (20 - filled)
print(f"Progress: [{bar}] {completed}/{total} ({completed/total:.0%})")
```
### 5.2 Auto-Save
- After every label, overwrite session JSON safely.
### 5.3 Resume Logic
- Match completed items by hash, not index.

## 6. Error Handling and Recovery
- Crash recovery via auto-save
- Auto-backup corrupted session files
- Warn if dataset hash mismatch
- `--reset` flag for fresh session

## 7. Reporting
### Dedicated Folder
```
performance/reports/
└── progress_summary_<timestamp>.md
```
### Report Content
```
# Progress Report
## Summary
- Dataset: sentence_classifier.json
- Completed: 34/100 (34%)
- Skipped: 2
- Remaining: 64

## Session Duration
- Total: 18m 42s
- Avg/question: 9.8s

## Accuracy
- Correct: 30
- Incorrect: 4
- Accuracy: 88.2%
██████████---------- (34%)
```

## 8. Testing Plan
| Test | Expected |
|------|-----------|
| Interrupt mid-session | Resume correctly |
| Add new lines | Skip duplicates via hash |
| Crash | Data intact |
| No prior session | Clean start |
| Repeated resume | Idempotent |
| 100% complete | Progress cleared |

## 9. Constraints
- 100% standard library
- Backward compatible
- Python 3.8+
- <50MB memory

## 10. Deliverables
- Updated `label_sentences.py`
- New `performance/` directory
- New report generator
- Updated documentation
