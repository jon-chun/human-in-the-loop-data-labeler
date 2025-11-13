# Pedagogical Critique

**Clarity:** Improved with step-by-step runbook and copy/paste prompts.  
**Conciseness:** Guides split into install vs workflow.  
**Robustness:** CI, commitlint, and CODEOWNERS reduce regressions; `.gitignore` avoids noise.  
**Failsafe:** Added troubleshooting and scripts; suggest adding screenshots for non-CS students.


Here’s a tight, no-fluff upgrade with concrete fixes and a ready-to-drop patch.

# 1) Repo audit (missing/dead files + actions)

## Findings

* **Missing governance**: no `.github/` directory (workflows, issue templates, PR template, CODEOWNERS).
* **No Claude slash commands**: you reference `/issue <n>`, but there’s no `.claude/commands/issue.md`.
* **No helper scripts** for seeding issues; onboarding friction for students.
* **No `.gitignore`**: `__pycache__`, logs, outputs, and reports could be committed by accident.
* **Stale bytecode**: `__pycache__/label_sentences.cpython-312.pyc` likely points to the old entrypoint path.
* **Docs drift**: your manuals are short and likely don’t reflect the move to `src/label_sentences.py` nor the 10-week Claude+VS Code workflow.
* **Suspicious output**: `outputs/sentence_similarity_HUMAN.json` is only **2 bytes** — probably a truncated/empty run. Keep it, but call it out in QA.

## Fix/Move/Delete recommendations

* **ADD**:

  * `.github/workflows/{ci.yml, commitlint.yml}`
  * `.github/ISSUE_TEMPLATE/{feature.yml, bug.yml, chore.yml}`
  * `.github/CODEOWNERS`, `.github/PULL_REQUEST_TEMPLATE.md`
  * `.claude/commands/issue.md` (project slash command)
  * `scripts/seed_issues.sh` (seed labels/issues)
  * `.gitignore`
* **UPDATE**:

  * `README.md` (point to `src/label_sentences.py`, quickstart, troubleshooting)
  * `docs/{doc_tech-spec.md,user-manual.md,lab_instructor-manual.md}` with clearer steps + prompts
  * `config.yaml`, `pyproject.toml` for reproducibility (done in earlier pass; included again here)
* **DELETE from VCS**:

  * `__pycache__/` directory entries (add to `.gitignore`; remove from repo history if already committed)
* **KEEP but review data**:

  * `outputs/sentence_similarity_HUMAN.json` (2 bytes) — run a sanity check via your planned edit/validate utility.

---

# 2) Revised docs: clearer, concise, robust, and student-friendly

I updated all affected docs with:

* precise commands using the new entrypoint (`src/label_sentences.py`)
* copy/paste friendly runbooks
* minimal troubleshooting
* curated resource links
* focused LLM prompts students can paste into Claude to learn concepts fast

### What changed (highlights)

* **`docs/user-manual.md`**: one-page quick start; classify/rank/merge commands; “what to type” during interactive prompts; concise troubleshooting.
* **`docs/doc_tech-spec.md`**: crisp system map (entrypoint → subcommands → outputs → config → CI).
* **`docs/lab_instructor-manual.md`**: 10-week cohort runbook, ready-made prompts for learning (Conventional Commits, CI debugging, Git/GitHub concepts), and assessment rubric.
* **`README.md`**: friendly quickstart, structure, and FAQ.
* **`docs/pedagogical_critique.md`**: added summary of clarity/conciseness/robustness for non-CS learners.

### Focused Claude prompts (included in the instructor manual)

* “Explain **Conventional Commits** with examples for `feat`, `fix`, `docs`.”
* “Write a **minimal plan** for Issue #<n> using Given/When/Then acceptance criteria.”
* “Compare **branch vs PR vs protected main** at a diagram level.”
* “What does the **`ci` workflow** do here? Show how to fix a simple **Ruff** error.”
* “Given this **VS Code terminal error**, propose three minimal steps to fix it.”

### Resources (added to docs)

* GitHub CLI Quickstart, GitHub Flow, Ruff docs, VS Code terminal basics.

---

# 3) Download the updated patch (adds/updates only)

Everything above is packaged as a **drop-in patch** that adds what’s missing and updates the docs (no destructive changes to your data).

**What’s inside the patch**

* `.github/` (workflows, templates, CODEOWNERS, PR template)
* `.claude/commands/issue.md` (for `/issue`)
* `scripts/seed_issues.sh`
* `.gitignore`
* Updated `README.md`, `docs/*`, `pyproject.toml`, `config.yaml`

**Zip download:**
[Download hitl_patch_bundle_20251112_210143.zip](sandbox:/mnt/data/hitl_patch_bundle_20251112_210143.zip)

Unzip at your repo root and commit as a single PR like:

```bash
unzip -o hitl_patch_bundle_20251112_210143.zip -d .
git add .
git commit -m "chore(repo): add governance files, slash command, updated docs, and ignores"
git push origin -u <branch>
```

---

## Post-merge checklist

* Delete previously committed `__pycache__/` paths (if any show up in `git status` after adding `.gitignore`).
* Run CI on a small PR to verify `ci` and `commitlint` work.
* Test `/issue <n>` in Claude Code from VS Code Terminal to confirm the commands resolve.
* (Optional) seed a few issues: `chmod +x scripts/seed_issues.sh && ./scripts/seed_issues.sh`.

If you want, I can also generate a **validation utility** that flags empty/truncated HUMAN files and a **pre-commit** config to catch bytecode/logs before they hit the repo.
