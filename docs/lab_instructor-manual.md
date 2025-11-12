# Instructor Lab Manual

## Purpose
Guide students in extending and analyzing the Human-in-the-Loop Labeler project.  
Includes governance setup, enhancement roadmap, and evaluation steps.

## Student Assignments Overview
Students must implement and test **20 modular enhancements** (TUI, metadata, logging, reporting, etc.), mainly via `src/utils/`.

## Key Enhancements
1. Config centralization (`config.yaml`)
2. pyproject.toml setup with uv + lint/test defaults
3. Smart JSON editing (`util_edit_json.py`)
4. Annotator metadata capture
5. Human assignment system from CSV
6. Enhanced TUI using textual
7. Time-tracking per labeling event
8. Merge/aggregate/validate outputs
9. Report generation and visualization
10. Inter-annotator agreement stats
11. Logging refactor (`util_logging.py`)
12. Resume/review improvements
13. Session metadata + UUIDs
14. Configurable field limits
15. Performance summary reports
16. CLI menu-based UX
17. Metadata-aware aggregation
18. Advanced error handling/log masking
19. Outputs diffing on review
20. Automated documentation update.

## Evaluation Rubric
- ✅ Code modularity and clarity
- ✅ Functional correctness
- ✅ Logging and reporting completeness
- ✅ Governance compliance (PR, Issue, CI)
