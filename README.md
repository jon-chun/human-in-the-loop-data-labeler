# Human Sentence Labeler

Collect human labels for two small NLP tasks with **zero dependencies**:

- **Classify** (True/False): Are two sentences semantically similar?
- **Rank** ('a' vs 'b'): Which sentence is closer to the base?

> Gold labels exist in the data but are **never shown** to the human labeler; they are used for **metrics** only.

## Features
- CLI with two subcommands: `classify`, `rank`
- Deterministic shuffle (`--seed`, default 42)
- ASCII 7-bit normalization for robust console UX
- Skips invalid records; logs precise reasons
- **Structured logs** in `./logs/log_{timestamp}.json`
- **Human-readable reports** in `./reports/report_{timestamp}.txt`
- Writes `{root}_HUMAN{ext}` with human labels added

## Quickstart
```bash
python label_sentences.py classify --input sentence_classifier.json
python label_sentences.py rank --input sentence_similarity.json
```

## Repo Structure
```
.
├── label_sentences.py
├── sentence_classifier.json
├── sentence_similarity.json
├── docs/
│   ├── tech-spec.md
│   └── user-manual.md
├── logs/
└── reports/
```

## Metrics
- **Classification**: accuracy, recall/F1 per class, confusion (TP/FP/FN/TN)
- **Ranking**: accuracy, recall/F1 per label ('a','b'), confusion grid

## License
MIT
