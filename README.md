# Human-in-the-Loop Data Labeler (Modular)

## Quick Start
```bash
python3 -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
python src/label_sentences.py --help
```

### Label
```bash
python src/label_sentences.py classify --input inputs/sentence_classifier.json   --annotator-id u001 --annotator-name "Ada Lovelace" --annotator-email ada@example.com
```

### Merge
```bash
python src/label_sentences.py merge
```

## Project Structure
- `src/label_sentences.py` — CLI entrypoint
- `src/hil/*` — core modules
- `docs/*` — user/instructor manuals, tech spec
- `.github/*` — governance (templates, CI)
- `.claude/commands` — CLI slash commands for Claude Code

## Troubleshooting
- If `pyenv` not found, use system Python 3.10+
- For permission errors on scripts: `chmod +x scripts/*.sh`

