from __future__ import annotations
import random, time
from pathlib import Path
from typing import List

from ..io_utils import read_json, write_json
from ..validation import validate_ascii
from ..metrics import metrics_binary
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
    exists, is_complete, completed_indices, resume_idx = check_existing_output(out_human, data, "classify")

    if exists:
        if is_complete:
            if not confirm_review_revision():
                print("Exiting without changes.")
                return
            print("Review mode: You can revise any previous labels.")
        else:
            print(f"Resuming from item {resume_idx + 1}. {len(completed_indices)} items already completed.")

    log = SessionLog(log_path, {
        "cmd": "classify", "input": input_path, "seed": seed, "max_len": max_len,
        "resuming_from": resume_idx if exists else None,
        "existing_completed": len(completed_indices) if exists else 0,
        "annotator": annotator or {}
    })

    fields = ["sentence_base", "sentence_test"]
    gold_key = "label_semantic_similarity"

    y_true: List[bool] = []
    y_pred: List[bool] = []
    kept: list[dict] = []

    existing_records: list[dict] = []
    if exists:
        try:
            existing_records = read_json(out_human)
            for rec in existing_records:
                if "label_semantic_similarity_human" in rec:
                    for orig in data:
                        if orig.get("sentence_base", "") == rec.get("sentence_base", "") and                            orig.get("sentence_test", "") == rec.get("sentence_test", ""):
                            y_true.append(bool(orig.get(gold_key)))
                            y_pred.append(bool(rec["label_semantic_similarity_human"]))
                            kept.append(rec)
                            break
        except Exception:
            pass

    with Path(report_path).open("w", encoding="utf-8") as rfp:
        resume_note = None
        if exists:
            resume_note = f"Resuming from item {resume_idx + 1}, {len(completed_indices)} already completed"
        write_report_header(rfp, "classify", input_path, seed, max_len, resume_note, annotator)

        print(f"\nLoaded {len(data)} items. Shuffled with seed={seed}.")
        if exists:
            print(f"Resuming from item {resume_idx + 1}. {len(completed_indices)} items already completed.")
        print("Label True/False (t/f). 's' to skip.\n")

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

            base, test = a["sentence_base"], a["sentence_test"]
            print("-"*60)
            print(f"[{len(kept)+1}] Base : {base}")
            print(f"      Test : {test}")

            existing_label = None
            if is_complete:
                for ex in existing_records:
                    if ex.get("sentence_base", "") == base and ex.get("sentence_test", "") == test:
                        existing_label = ex.get("label_semantic_similarity_human")
                        cur = "True" if existing_label else "False"
                        print(f"      Current: {cur}")
                        break

            t0 = time.time()
            while True:
                if is_complete and existing_label is not None:
                    lab = input("Label (t/f) or 's' to skip, Enter to keep current: ").strip().lower()
                    if lab == "":
                        lab = "t" if existing_label else "f"
                else:
                    lab = input("Label (t/f or s to skip): ").strip().lower()
                if lab in ("t","true","f","false","s"):
                    break
                print("Please type 't', 'f', or 's'.")
            t1 = time.time()

            elapsed_ms = int((t1 - t0) * 1000)
            if lab == "s":
                from ..text_utils import hash_preview
                log.add_skip("user_skip", {"base": hash_preview(base), "test": hash_preview(test)})
                continue

            human = (lab in ("t","true"))
            kept.append(rec)
            y_pred.append(human)
            gold = bool(rec.get(gold_key))
            y_true.append(gold)

            from ..text_utils import hash_preview
            log.add_item(
                idx=idx,
                base_preview=hash_preview(base),
                test_preview=hash_preview(test),
                human=human,
                gold_hidden=True,
                elapsed_ms=elapsed_ms
            )

    out_records: list[dict] = []
    processed_keys = {(r.get("sentence_base", ""), r.get("sentence_test", "")) for r in kept}

    if is_complete:
        for rec, h in zip(kept, y_pred):
            new = dict(rec)
            new["label_semantic_similarity_human"] = bool(h)
            if annotator:
                new.setdefault("_annotator", annotator)
            out_records.append(new)
    else:
        for ex in existing_records:
            key = (ex.get("sentence_base", ""), ex.get("sentence_test", ""))
            if key not in processed_keys:
                out_records.append(ex)
        for rec, h in zip(kept, y_pred):
            new = dict(rec)
            new["label_semantic_similarity_human"] = bool(h)
            if annotator:
                new.setdefault("_annotator", annotator)
            out_records.append(new)

    write_json(out_human, out_records)

    m = metrics_binary(y_true, y_pred)
    log.finalize(m)

    with Path(report_path).open("a", encoding="utf-8") as rfp:
        write_report_results(rfp, "classify", m, Path(out_human), Path(log_path))

    print("\nSaved:")
    print(f"  Human labels -> {out_human}")
    print(f"  Log JSON     -> {log_path}")
    print(f"  Report TXT   -> {report_path}\n")
