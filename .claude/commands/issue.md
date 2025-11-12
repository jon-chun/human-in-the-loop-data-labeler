# /issue <number>
Process GitHub issue {{args.0}} with plan → implement → test → PR → review → merge.

Plan
- gh issue view {{args.0}}
- Write plan to scratchpads/issue-{{args.0}}.md
- Define acceptance, risks, tests, and a tiny branch name

Implement
- Create branch: issue-{{args.0}}-<slug>
- Make the smallest possible change; keep runtime deps zero

Test
- python -m py_compile src/label_sentences.py

PR
- gh pr create --fill --title "<Conventional summary>"
- Respond to review; iterate until CI is green
