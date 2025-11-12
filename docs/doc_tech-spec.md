# Technical Specification

## Overview
This system implements a modular **Human-in-the-Loop Data Labeler** supporting classification and ranking with annotator metadata, per-item timing, and merge functionality.

## Key Modules
- **src/label_sentences.py**: CLI entrypoint calling core workflows.
- **hil/**: Core library with IO, metrics, validation, and workflow logic.
- **utils/**: Support utilities (editing, analysis, TUI, logging, reporting).

## Data Flow
1. Input JSONs are loaded, validated, and presented interactively.
2. Annotator metadata and per-item timing are recorded.
3. Results stored in `outputs/*.json` with logs and reports.
4. Merge command consolidates outputs into `outputs-merged/`.
