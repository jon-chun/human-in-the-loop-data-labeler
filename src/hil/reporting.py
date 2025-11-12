from __future__ import annotations
from pathlib import Path
from datetime import datetime

def write_report_header(fp, cmd: str, input_path: str, seed: int, max_len: int, resume_note: str | None = None, annotator: dict | None = None):
    fp.write(f"REPORT {cmd} @ {datetime.now().isoformat()}\n")
    fp.write(f"Input: {input_path}\n")
    fp.write(f"Seed: {seed}  MaxLen: {max_len}\n")
    if annotator:
        fp.write(f"Annotator: {annotator.get('id','?')} {annotator.get('name','')} <{annotator.get('email','')}>\n")
    if resume_note:
        fp.write(resume_note + "\n")
    fp.write("-"*60 + "\n")

def write_report_results(fp, cmd: str, metrics: dict, human_out: Path, log_path: Path):
    fp.write("\nRESULTS\n")
    fp.write(f"Accuracy: {metrics['accuracy']:.4f}\n")
    if cmd == "classify":
        fp.write(f"Recall(pos): {metrics['recall_pos']:.4f}  F1(pos): {metrics['f1_pos']:.4f}\n")
        fp.write(f"Recall(neg): {metrics['recall_neg']:.4f}  F1(neg): {metrics['f1_neg']:.4f}\n")
        c = metrics["confusion"]
        fp.write(f"Confusion: TP={c['tp']} FP={c['fp']} FN={c['fn']} TN={c['tn']}\n")
    else:
        fp.write(f"Recall(a): {metrics['recall_a']:.4f}  F1(a): {metrics['f1_a']:.4f}\n")
        fp.write(f"Recall(b): {metrics['recall_b']:.4f}  F1(b): {metrics['f1_b']:.4f}\n")
        c = metrics["confusion"]
        fp.write(f"Confusion: a->a={c['a_to_a']} a->b={c['a_to_b']} b->a={c['b_to_a']} b->b={c['b_to_b']}\n")
    fp.write("\n")
    fp.write(f"Human output: {human_out}\n")
    fp.write(f"JSON log:     {log_path}\n")
