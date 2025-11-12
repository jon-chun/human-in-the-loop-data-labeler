from __future__ import annotations
import random, time
from pathlib import Path
from typing import List

from ..io_utils import read_json, write_json
from ..validation import validate_ascii
from ..metrics import metrics_ab
from ..logging_utils import SessionLog
from ..reporting import write_report_header, write_report_results
from ..paths import Paths
from ..resume import check_existing_output

def confirm_review_revision() -> bool:
    while True:
        response = input("This input file has already been completely labeled. Do you want to review/revise? [Y/n]: ").strip().lower()
        if response in ("", "y", "yes"): return True
        if response in ("n", "no"): return False
        print("Please type 'y' or 'n'.")

def run(input_path: str, seed: int, max_len: int, paths: Paths, annotator: dict | None = None):
    data = read_json(input_path)
    rnd = random.Random(seed)
    order = list(range(len(data)))
    rnd.shuffle(order)

    out_human, log_path, report_path = paths.derive_paths(input_path)
    exists, is_complete, completed_indices, resume_idx = check_existing_output(out_human, data, "rank")

    if exists:
        if is_complete:
            if not confirm_review_revision():
                print("Exiting without changes.")
                return
            print("Review mode: You can revise any previous labels.")
        else:
            print(f"Resuming from item {resume_idx + 1}. {len(completed_indices)} items already completed.")

    log = SessionLog(log_path, {
        "cmd": "rank", "input": input_path, "seed": seed, "max_len": max_len,
        "resuming_from": resume_idx if exists else None,
        "existing_completed": len(completed_indices) if exists else 0,
        "annotator": annotator or {}
    })

    fields = ["sentence_base", "sentence_a", "sentence_b"]
    gold_key = "label_more_similar"

    y_true: List[str] = []
    y_pred: List[str] = []
    kept: list[dict] = []

    existing_records: list[dict] = []
    if exists:
        try:
            existing_records = read_json(out_human)
            for rec in existing_records:
                if "label_more_similar_human" in rec:
                    for orig in data:
                        if orig.get("sentence_base", "") == rec.get("sentence_base", "") and                            orig.get("sentence_a", "") == rec.get("sentence_a", "") and                            orig.get("sentence_b", "") == rec.get("sentence_b", ""):
                            gold = "a" if str(orig.get(gold_key)).lower()=="a" else "b"
                            y_true.append(gold)
                            y_pred.append(rec["label_more_similar_human"])
                            kept.append(rec)
                            break
        except Exception:
            pass

    with Path(report_path).open("w", encoding="utf-8") as rfp:
        resume_note = None
        if exists:
            resume_note = f"Resuming from item {resume_idx + 1}, {len(completed_indices)} already completed"
        write_report_header(rfp, "rank", input_path, seed, max_len, resume_note, annotator)

        print(f"\nLoaded {len(data)} items. Shuffled with seed={seed}.")
        if exists:
            print(f"Resuming from item {resume_idx + 1}. {len(completed_indices)} items already completed.")
        print("Choose 'a' or 'b'. 's' to skip.\n")

        start_pos = 0
        if exists and not is_complete:
            for pos, idx in enumerate(order):
                if idx == resume_idx:
                    start_pos = pos + 1
                    break

        for i, idx in enumerate(order[start_pos:], start_pos + 1):
            rec = data[idx]
            ok, a = validate_ascii(rec, fields, max_len, log.data)
            if not ok:
                continue

            base, sa, sb = a["sentence_base"], a["sentence_a"], a["sentence_b"]
            print("-"*60)
            print(f"[{len(kept)+1}] Base : {base}")
            print(f"      (a): {sa}")
            print(f"      (b): {sb}")

            existing_label = None
            if is_complete:
                for ex in existing_records:
                    if ex.get("sentence_base", "") == base and ex.get("sentence_a", "") == sa and ex.get("sentence_b", "") == sb:
                        existing_label = ex.get("label_more_similar_human")
                        print(f"      Current: {existing_label}")
                        break

            t0 = time.time()
            while True:
                if is_complete and existing_label is not None:
                    lab = input("Label ('a'/'b' or 's' to skip, Enter to keep current: ").strip().lower()
                    if lab == "":
                        lab = existing_label
                else:
                    lab = input("Label ('a'/'b' or 's' to skip): ").strip().lower()
                if lab in ("a","b","s"):
                    break
                print("Please type 'a', 'b', or 's'.")
            t1 = time.time()
            elapsed_ms = int((t1 - t0) * 1000)

            if lab == "s":
                from ..text_utils import hash_preview
                log.add_skip("user_skip", {"base": hash_preview(base), "a": hash_preview(sa), "b": hash_preview(sb)})
                continue

            human = lab
            kept.append(rec)
            y_pred.append(human)
            gold = "a" if str(rec.get(gold_key)).lower()=="a" else "b"
            y_true.append(gold)

            from ..text_utils import hash_preview
            log.add_item(idx=idx, base_preview=hash_preview(base), a_preview=hash_preview(sa), b_preview=hash_preview(sb), human=human, gold_hidden=True, elapsed_ms=elapsed_ms)

    out_records: list[dict] = []
    processed = {(r.get("sentence_base", ""), r.get("sentence_a", ""), r.get("sentence_b", "")) for r in kept}

    if is_complete:
        for rec, h in zip(kept, y_pred):
            new = dict(rec)
            new["label_more_similar_human"] = h
            if annotator:
                new.setdefault("_annotator", annotator)
            out_records.append(new)
    else:
        for ex in existing_records:
            key = (ex.get("sentence_base", ""), ex.get("sentence_a", ""), ex.get("sentence_b", ""))
            if key not in processed:
                out_records.append(ex)
        for rec, h in zip(kept, y_pred):
            new = dict(rec)
            new["label_more_similar_human"] = h
            if annotator:
                new.setdefault("_annotator", annotator)
            out_records.append(new)

    write_json(out_human, out_records)

    m = metrics_ab(y_true, y_pred)
    log.finalize(m)

    with Path(report_path).open("a", encoding="utf-8") as rfp:
        write_report_results(rfp, "rank", m, Path(out_human), Path(log_path))

    print("\nSaved:")
    print(f"  Human labels -> {out_human}")
    print(f"  Log JSON     -> {log_path}")
    print(f"  Report TXT   -> {report_path}\n")
