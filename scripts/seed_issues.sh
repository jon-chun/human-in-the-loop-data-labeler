#!/usr/bin/env bash
set -euo pipefail
make_issue() {
  local title="$1"; shift
  local body="$1"; shift
  local labels="$1"; shift
  gh issue create --title "$title" --body "$body" --label "$labels" --assignee "@me"
}
make_issue "fix(classify): handle empty strings without crash"   "Repro: {"sentence_base":"","sentence_test":"x"}. Expect skip + log."   "bug,easy"
make_issue "feat(cli): --summary to print metrics from HUMAN files"   "Non-interactive metrics summary from outputs/*.json"   "feature,medium"
