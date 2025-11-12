from __future__ import annotations
from pathlib import Path
import json

def check_existing_output(out_human: Path, input_data: list[dict], cmd_type: str):
    if not Path(out_human).exists():
        return False, False, set(), 0
    try:
        existing_data = json.loads(Path(out_human).read_text(encoding="utf-8"))
        completed: set[int] = set()
        for item in existing_data:
            if cmd_type == "classify":
                key = (item.get("sentence_base", ""), item.get("sentence_test", ""))
            else:
                key = (item.get("sentence_base", ""), item.get("sentence_a", ""), item.get("sentence_b", ""))
            for idx, orig in enumerate(input_data):
                if cmd_type == "classify":
                    okey = (orig.get("sentence_base", ""), orig.get("sentence_test", ""))
                else:
                    okey = (orig.get("sentence_base", ""), orig.get("sentence_a", ""), orig.get("sentence_b", ""))
                if okey == key:
                    completed.add(idx); break
        is_complete = len(completed) == len(input_data)
        resume_index = 0 if is_complete else (max(completed) + 1 if completed else 0)
        return True, is_complete, completed, resume_index
    except Exception:
        return False, False, set(), 0
