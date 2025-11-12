from __future__ import annotations
from pathlib import Path
import json, glob
from .paths import Paths

def run_merge(paths: Paths, pattern: str = "./outputs/*.json") -> str:
    records = []
    for p in glob.glob(pattern):
        try:
            data = json.loads(Path(p).read_text(encoding="utf-8"))
            if isinstance(data, list):
                records.extend(data)
        except Exception:
            continue
    seen = set()
    out = []
    for r in records:
        key = (
            r.get("sentence_base",""),
            r.get("sentence_test",""),
            r.get("sentence_a",""),
            r.get("sentence_b",""),
            r.get("label_semantic_similarity_human",""),
            r.get("label_more_similar_human",""),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    out_path = paths.outputs_merged / f"merged_{paths.timestamp()}.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(out_path)
