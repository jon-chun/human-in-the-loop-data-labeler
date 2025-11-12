from __future__ import annotations
from pathlib import Path
from datetime import datetime
from .constants import Defaults

class Paths:
    def __init__(self, cfg_dirs: dict | None = None):
        d = cfg_dirs or {}
        self.logs = Path(d.get("logs", Defaults.LOG_DIR))
        self.reports = Path(d.get("reports", Defaults.REPORT_DIR))
        self.outputs = Path(d.get("outputs", Defaults.OUTPUT_DIR))
        self.inputs = Path(d.get("inputs", Defaults.INPUTS_DIR))
        self.outputs_merged = Path(d.get("outputs_merged", Defaults.OUTPUTS_MERGED_DIR))
        self.resources = Path(d.get("resources", Defaults.RESOURCES_DIR))
        for p in (self.logs, self.reports, self.outputs, self.outputs_merged, self.inputs, self.resources):
            p.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def timestamp() -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def derive_paths(self, input_path: str):
        ip = Path(input_path)
        ts = self.timestamp()
        root = ip.stem
        ext = ip.suffix or ".json"
        out_human = self.outputs / f"{root}_HUMAN{ext}"
        log_path = self.logs / f"log_{ts}.json"
        report_path = self.reports / f"report_{ts}.txt"
        return out_human, log_path, report_path

    def resolve_input(self, arg: str) -> str:
        p = Path(arg)
        if p.exists() and p.is_file():
            return str(p)
        cand = self.inputs / arg
        return str(cand if cand.exists() else p)
