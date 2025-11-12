from __future__ import annotations
import json, time, uuid
from pathlib import Path

class SessionLog:
    def __init__(self, log_path: Path, base: dict):
        self.log_path = Path(log_path)
        self.data = {
            **base,
            "session_id": str(uuid.uuid4()),
            "start_ts": time.time(),
            "skips": [],
            "items": []
        }

    def add_skip(self, reason: str, record_preview: dict):
        self.data["skips"].append({"reason": reason, "record_preview": record_preview})

    def add_item(self, **kvs):
        self.data["items"].append(kvs)

    def finalize(self, metrics: dict):
        self.data["metrics"] = metrics
        self.data["end_ts"] = time.time()
        self.log_path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
