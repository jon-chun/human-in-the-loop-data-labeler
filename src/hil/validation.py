from __future__ import annotations
from typing import Dict
from .text_utils import ascii7, hash_preview

def validate_ascii(rec: Dict, fields: list[str], max_len: int, log: Dict) -> tuple[bool, dict]:
    out: dict = {}
    for k in fields:
        v = rec.get(k, "")
        if not isinstance(v, str) or not v.strip():
            msg = f"missing_or_empty:{k}"
            log.setdefault("skips", []).append({
                "reason": msg,
                "record_preview": {kk: hash_preview(str(rec.get(kk, ""))) for kk in fields}
            })
            return False, {}
        a = ascii7(v)
        if len(a) > max_len:
            msg = f"too_long:{k}:{len(a)}>{max_len}"
            log.setdefault("skips", []).append({
                "reason": msg,
                "record_preview": {kk: hash_preview(ascii7(str(rec.get(kk, "")))) for kk in fields}
            })
            return False, {}
        out[k] = a
    return True, out
