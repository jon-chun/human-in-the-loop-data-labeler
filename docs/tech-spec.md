# Technical Specification: Human Sentence Labeler

## Overview
`label_sentences.py` is a terminal UI for collecting **human labels** on two NLP tasks:
1. **Binary Semantic Similarity** (`classify`): label whether `sentence_base` and `sentence_test` are semantically similar (True/False).
2. **Pairwise Similarity** (`rank`): choose which sentence (`a` or `b`) is **more similar** to `sentence_base`.

Gold labels are provided in the datasets but are **never displayed** to the operator. They are used only for **metrics** after labeling.

## Data Contracts
### Classification
- Input keys: `sentence_base: str`, `sentence_test: str`, `label_semantic_similarity: bool`
- Output adds: `label_semantic_similarity_human: bool`

### Pairwise Ranking
- Input keys: `sentence_base: str`, `sentence_a: str`, `sentence_b: str`, `label_more_similar: 'a'|'b'`
- Output adds: `label_more_similar_human: 'a'|'b'`

Inputs are JSON arrays of objects. Outputs write to `{root}_HUMAN{ext}` in JSON.

## Determinism & Shuffling
- A fixed `--seed` governs item shuffling. Default: `42`.
- ASCII 7-bit normalization is applied for display and validation.

## Validation & Skips
- Each required string must be non-empty and <= `--max-len` (default 1000).
- Violations are **skipped** and recorded to structured log with previews (prefix + hash).

## Logging & Reporting
- **Logs**: `./logs/log_{timestamp}.json` include: args, skips with reasons, per-item previews, and metrics.
- **Reports**: `./reports/report_{timestamp}.txt` provide a human-readable run summary (config, counts, metrics, artifact paths).

## Metrics
- **Classification**: accuracy, class-wise recall/F1 (pos=True / neg=False), and confusion (TP/FP/FN/TN).
- **Ranking**: accuracy, label-wise recall/F1 for `a` and `b`, and a 2x2 confusion summary.

## Terminal UI
- `classify`: prompt `t/f/s` for each item.
- `rank`: prompt `a/b/s` for each item.

## Complexity & Constraints
- All computations are O(N), memory O(N) for captured outputs.
- No external dependencies; standard library only.
- Large strings > `--max-len` are skipped to avoid awkward console UX.

## Security & Privacy Notes
- Logs store **previews** (first 40 chars + SHA-256 hash) instead of full text.
- No network calls. Filesystem-only.
- Operator can adjust `--seed` and `--max-len` to fit labeling sessions.

## Extensibility Hooks
- Add new tasks by implementing a `run_<task>` method, adding subparser, and mirroring logging/reporting calls.
- Replace preview hashing policy in `hash_preview` if stricter redaction is required.
