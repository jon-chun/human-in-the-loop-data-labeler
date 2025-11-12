from __future__ import annotations
import json
from pathlib import Path
from typing import Any

def read_json(path: str | Path) -> Any:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path: str | Path, obj: Any) -> None:
    p = Path(path)
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
