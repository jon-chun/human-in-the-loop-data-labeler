from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import yaml
from .constants import Defaults

@dataclass
class AppConfig:
    seed: int = Defaults.SEED
    max_len: int = Defaults.MAX_LEN
    dirs: dict | None = None
    labeling_overlap: int = 3

    @classmethod
    def load(cls, path: str | None = "config.yaml") -> "AppConfig":
        cfg = cls()
        p = Path(path)
        if p.exists():
            with p.open("r", encoding="utf-8") as f:
                y = yaml.safe_load(f) or {}
            cfg.seed = int(y.get("seed", cfg.seed))
            cfg.max_len = int(y.get("max_len", cfg.max_len))
            cfg.labeling_overlap = int(y.get("LABELING_OVERLAP", cfg.labeling_overlap))
            cfg.dirs = y.get("dirs", {})
        else:
            cfg.dirs = {}
        return cfg
