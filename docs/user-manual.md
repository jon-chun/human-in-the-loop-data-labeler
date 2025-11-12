# User Manual

## Install (one-time)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
```

## Run
- **Classify**
  ```bash
  python src/label_sentences.py classify --input inputs/sentence_classifier.json     --annotator-id u001 --annotator-name "Ada Lovelace" --annotator-email ada@example.com
  ```
- **Rank**
  ```bash
  python src/label_sentences.py rank --input inputs/sentence_similarity.json     --annotator-id u001 --annotator-name "Ada Lovelace" --annotator-email ada@example.com
  ```
- **Merge**
  ```bash
  python src/label_sentences.py merge
  ```

## Troubleshooting
- If terminal waits for input, type: `t` or `f` (classify), `a` or `b` (rank), or `s` to skip.
- Outputs appear in `./outputs/`, logs in `./logs/`, and reports in `./reports/`.
