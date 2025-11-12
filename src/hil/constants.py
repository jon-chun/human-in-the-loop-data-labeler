from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Defaults:
    SEED: int = 42
    MAX_LEN: int = 1000
    LOG_DIR: str = "./logs"
    REPORT_DIR: str = "./reports"
    OUTPUT_DIR: str = "./outputs"
    INPUTS_DIR: str = "./inputs"
    OUTPUTS_MERGED_DIR: str = "./outputs-merged"
    RESOURCES_DIR: str = "./resources"
