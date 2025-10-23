# User / Operator Manual

## 1. Requirements
- Python 3.8+ (no extra packages required).
- Terminal session with ability to read/write local files.

## 2. Project Layout
```
.
├── label_sentences.py
├── sentence_classifier.json         # sample dataset (30 rows)
├── sentence_similarity.json         # sample dataset (30 rows)
├── docs/
│   ├── tech-spec.md
│   └── user-manual.md
├── logs/                            # created on first run
└── reports/                         # created on first run
```

## 3. Input Formats
### 3.1 Classification
Each record:
```json
{
  "sentence_base": "Turn off the lights when you leave.",
  "sentence_test": "Please switch the lights off before exiting.",
  "label_semantic_similarity": true
}
```

### 3.2 Pairwise
Each record:
```json
{
  "sentence_base": "The restaurant opens at noon.",
  "sentence_a": "They start serving lunch at 12:00.",
  "sentence_b": "Breakfast ends at 9:00 p.m.",
  "label_more_similar": "a"
}
```

> The gold labels are never shown to the operator.

## 4. Running
```bash
# Classification (True/False)
python label_sentences.py classify --input sentence_classifier.json

# Pairwise (a vs b)
python label_sentences.py rank --input sentence_similarity.json

# Command help
python label_sentences.py --help
```
Flags:
- `--seed 42`  (default): reproducible shuffle order.
- `--max-len 1000` (default): skip records with overly long fields.

## 5. What Gets Written
- **Human labels** → `{root}_HUMAN{ext}` in the current directory.
- **Structured log** → `./logs/log_{YYYYMMDD_HHMMSS}.json` (args, skips, item previews, metrics).
- **Report** → `./reports/report_{YYYYMMDD_HHMMSS}.txt` (readable summary with metrics and artifact paths).

## 6. Skips & Errors
- Missing or empty required fields → skip, log reason `missing_or_empty:<key>`.
- Field longer than `--max-len` → skip, log reason `too_long:<key>:<len>>max`.
- Manual skip (`s`) during labeling → logged as `user_skip`.

A console message is printed for each skip; details live in the log JSON.

## 7. Metrics Explained
- **Accuracy**: overall correctness.
- **Recall / F1**: per-class and macro where applicable.
- **Confusion**:
  - Classify: TP/FP/FN/TN (pos=True).
  - Rank: a→a, a→b, b→a, b→b.

## 8. Debugging Tips
- If results look off, verify your input keys match the spec exactly.
- Check `./logs/log_*.json` for skipped items and counts.
- Re-run with a different `--seed` to vary item order.
- If the console shows odd characters, remember the tool normalizes to ASCII—inspect original JSON to confirm content.

## 9. Reproducibility
- Set an explicit `--seed` and keep your input JSON unchanged. The item order presented will repeat exactly.

## 10. FAQ
**Q:** Can I hide the console metrics?
**A:** Not currently; metrics are part of the session summary. You can ignore them and read the report instead.

**Q:** Can I change the logs/report directories?
**A:** The current version writes to `./logs` and `./reports`. Modify `ensure_dirs()` and `make_paths()` to customize.
