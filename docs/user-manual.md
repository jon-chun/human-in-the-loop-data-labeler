# User Manual

## Getting Started
Run labeling tasks interactively from the terminal.

### Commands
- **classify** — Binary True/False labeling
- **rank** — Choose 'a' or 'b'
- **merge** — Combine all labeled outputs

### Example
```bash
python src/label_sentences.py classify --input inputs/sentence_classifier.json   --annotator-id u001 --annotator-name "Ada Lovelace" --annotator-email ada@example.com
```

## Outputs
- **./outputs/**: Human-labeled JSONs
- **./logs/**: JSON logs per session
- **./reports/**: Plain-text summaries
- **./outputs-merged/**: Consolidated data

## Tips
- Use `--seed` to reproduce order.
- Use `--max-len` to limit input field length.
