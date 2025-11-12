# Technical Spec — HITL Labeler

- Entry: `src/label_sentences.py` → `hil.cli`
- Subcommands: `classify`, `rank`, `merge`
- Timing metadata: `elapsed_ms` per item
- Annotator metadata: `_annotator` on HUMAN outputs
- Merge: de-dupes to `outputs-merged/merged_<ts>.json`
- Config: `config.yaml` (dirs, seed, max_len, overlap)
- CI: Ruff lint + compile check
