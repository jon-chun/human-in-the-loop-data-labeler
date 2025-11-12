# Instructor Lab Manual (10-week cohort)

## What changed
- Entry script moved to `src/label_sentences.py`
- Governance: CI, commitlint, CODEOWNERS, Issue/PR templates
- Claude: `/issue <n>` command added at `.claude/commands/issue.md`

## Runbook (students)
1. Clone and open VS Code → Terminal.
2. Create venv and install: `pip install -e .[dev]`.
3. Start Claude Code CLI in terminal; run `/init`.
4. Create a small Issue (Feature/Bug/Chore).
5. Run `/issue <n>` to plan & implement.
6. Ensure CI green → squash merge.

## Prompts (copy/paste)
- “Explain Conventional Commits with examples for `feat`, `fix`, `docs`.”
- “Show me how to write a minimal plan for Issue #<n> based on the template.”
- “Summarize differences between branch, PR, and protected main with a diagram-level explanation.”
- “Describe what a CI job does in this repo and how to fix a failing Ruff lint.”
- “Given this error message from VS Code terminal, propose three minimal steps to resolve it.”

## Resources
- GitHub CLI Quickstart: https://docs.github.com/en/github-cli/github-cli/quickstart
- GitHub Flow: https://docs.github.com/get-started/quickstart/github-flow
- Ruff: https://docs.astral.sh/ruff/
- VS Code Integrated Terminal: https://code.visualstudio.com/docs/terminal/basics

## Assessment
- PRs are atomic, CI passes, correct Conventional Commit, and instructor/peer review completed.
