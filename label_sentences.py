#!/usr/bin/env python3
"""
label_sentences.py (enhanced)

Adds:
- Structured JSON logging to ./logs/log_{datetime}.json
- Plain-text reporting to ./reports/report_{datetime}.txt

Other features:
- Two subcommands: classify (t/f), rank (a/b)
- Input: JSON arrays; gold labels trusted but hidden during labeling
- ASCII 7-bit normalization; skip-invalid logging
- Reproducible shuffling with --seed
- Outputs human-labeled file: <root>_HUMAN<ext>
- Console summary of metrics
"""

from __future__ import annotations
import argparse, json, os, random, sys, time, unicodedata, hashlib
from typing import List, Dict, Any, Tuple
from datetime import datetime

DEFAULT_SEED = 42
DEFAULT_MAX_LEN = 1000

def ensure_dirs():
    os.makedirs("./logs", exist_ok=True)
    os.makedirs("./reports", exist_ok=True)
    os.makedirs("./outputs", exist_ok=True)

def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def ascii7(s: str) -> str:
    return unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode("ascii")

def root_ext(path: str):
    root, ext = os.path.splitext(path)
    return root, ext if ext else ".json"

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def hash_preview(text: str) -> str:
    """Return a short stable preview hash so logs don't leak full text but are debuggable."""
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    # include small prefix for human context without PII risk
    prefix = text[:40].replace("\n"," ")
    return f"{prefix}...|{h}" if len(text) > 40 else f"{text}|{h}"

# ----- Metrics -----

def confusion_binary(y_true, y_pred):
    tp=fp=fn=tn=0
    for t,p in zip(y_true,y_pred):
        if t and p: tp+=1
        elif not t and p: fp+=1
        elif t and not p: fn+=1
        else: tn+=1
    return tp,fp,fn,tn

def metrics_binary(y_true, y_pred):
    tp,fp,fn,tn = confusion_binary(y_true, y_pred)
    total = tp+fp+fn+tn
    acc = (tp+tn)/total if total else 0.0
    prec_pos = tp/(tp+fp) if (tp+fp) else 0.0
    rec_pos  = tp/(tp+fn) if (tp+fn) else 0.0
    f1_pos   = (2*prec_pos*rec_pos)/(prec_pos+rec_pos) if (prec_pos+rec_pos) else 0.0
    prec_neg = tn/(tn+fn) if (tn+fn) else 0.0
    rec_neg  = tn/(tn+fp) if (tn+fp) else 0.0
    f1_neg   = (2*prec_neg*rec_neg)/(prec_neg+rec_neg) if (prec_neg+rec_neg) else 0.0
    return {
        "accuracy": acc,
        "recall_pos": rec_pos, "f1_pos": f1_pos,
        "recall_neg": rec_neg, "f1_neg": f1_neg,
        "confusion": {"tp":tp,"fp":fp,"fn":fn,"tn":tn}
    }

def confusion_ab(y_true, y_pred):
    taa=tab=tba=tbb=0
    for t,p in zip(y_true,y_pred):
        if t=="a" and p=="a": taa+=1
        elif t=="a" and p=="b": tab+=1
        elif t=="b" and p=="a": tba+=1
        elif t=="b" and p=="b": tbb+=1
    return taa,tab,tba,tbb

def metrics_ab(y_true, y_pred):
    taa,tab,tba,tbb = confusion_ab(y_true,y_pred)
    total = taa+tab+tba+tbb
    acc = (taa+tbb)/total if total else 0.0
    # 'a'
    tp_a, fn_a, fp_a = taa, tab, tba
    prec_a = tp_a/(tp_a+fp_a) if (tp_a+fp_a) else 0.0
    rec_a  = tp_a/(tp_a+fn_a) if (tp_a+fn_a) else 0.0
    f1_a   = (2*prec_a*rec_a)/(prec_a+rec_a) if (prec_a+rec_a) else 0.0
    # 'b'
    tp_b, fn_b, fp_b = tbb, tba, tab
    prec_b = tp_b/(tp_b+fp_b) if (tp_b+fp_b) else 0.0
    rec_b  = tp_b/(tp_b+fn_b) if (tp_b+fn_b) else 0.0
    f1_b   = (2*prec_b*rec_b)/(prec_b+rec_b) if (prec_b+rec_b) else 0.0
    return {
        "accuracy": acc,
        "recall_a": rec_a, "f1_a": f1_a,
        "recall_b": rec_b, "f1_b": f1_b,
        "confusion": {"a_to_a":taa,"a_to_b":tab,"b_to_a":tba,"b_to_b":tbb}
    }

# ----- Validation -----

def validate_ascii(rec, fields, max_len, log):
    out = {}
    for k in fields:
        v = rec.get(k, "")
        if not isinstance(v, str) or not v.strip():
            msg = f"missing_or_empty:{k}"
            log["skips"].append({"reason": msg, "record_preview": {kk: hash_preview(str(rec.get(kk,''))) for kk in fields}})
            return False, {}
        a = ascii7(v)
        if len(a) > max_len:
            msg = f"too_long:{k}:{len(a)}>{max_len}"
            log["skips"].append({"reason": msg, "record_preview": {kk: hash_preview(ascii7(str(rec.get(kk,'')))) for kk in fields}})
            return False, {}
        out[k] = a
    return True, out

# ----- IO Helpers -----

def make_paths(input_path):
    ensure_dirs()
    root, ext = os.path.splitext(os.path.basename(input_path))
    ts = timestamp()
    out_human = os.path.join("outputs", f"{root}_HUMAN{ext or '.json'}")
    log_path = os.path.join("logs", f"log_{ts}.json")
    report_path = os.path.join("reports", f"report_{ts}.txt")
    return out_human, log_path, report_path

def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def append_report_line(report_fp, line=""):
    report_fp.write(line + "\n")

# ----- Workflows -----

def run_classify(args):
    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)
    rnd = random.Random(args.seed)
    order = list(range(len(data)))
    rnd.shuffle(order)

    out_human, log_path, report_path = make_paths(args.input)
    log = {
        "cmd": "classify", "input": args.input, "seed": args.seed, "max_len": args.max_len,
        "start_ts": time.time(), "skips": [], "items": []
    }

    fields = ["sentence_base", "sentence_test"]
    gold_key = "label_semantic_similarity"

    y_true, y_pred = [], []
    kept = []

    with open(report_path, "w", encoding="utf-8") as rfp:
        append_report_line(rfp, f"REPORT classify @ {datetime.now().isoformat()}")
        append_report_line(rfp, f"Input: {args.input}")
        append_report_line(rfp, f"Seed: {args.seed}  MaxLen: {args.max_len}")
        append_report_line(rfp, "-"*60)

        print(f"\nLoaded {len(data)} items. Shuffled with seed={args.seed}.")
        print("Label True/False (t/f). 's' to skip.\n")

        for i, idx in enumerate(order, 1):
            rec = data[idx]
            ok, a = validate_ascii(rec, fields, args.max_len, log)
            if not ok: continue

            base, test = a["sentence_base"], a["sentence_test"]
            print("-"*60)
            print(f"[{len(kept)+1}] Base : {base}")
            print(f"      Test : {test}")
            while True:
                lab = input("Label (t/f or s to skip): ").strip().lower()
                if lab in ("t","true","f","false","s"): break
                print("Please type 't', 'f', or 's'.")
            if lab == "s":
                log["skips"].append({"reason":"user_skip", "record_preview":{"base":hash_preview(base),"test":hash_preview(test)}})
                continue

            human = (lab in ("t","true"))
            kept.append(rec)
            y_pred.append(human)
            gold = bool(rec.get(gold_key))
            y_true.append(gold)

            log["items"].append({
                "idx": idx,
                "base_preview": hash_preview(base),
                "test_preview": hash_preview(test),
                "human": human,
                "gold_hidden": True
            })

    # Output HUMAN file
    out_records = []
    for rec, h in zip(kept, y_pred):
        new = dict(rec)
        new["label_semantic_similarity_human"] = bool(h)
        out_records.append(new)
    write_json(out_human, out_records)

    # Metrics + report
    m = metrics_binary(y_true, y_pred)
    log["metrics"] = m
    log["end_ts"] = time.time()
    write_json(log_path, log)

    with open(report_path, "a", encoding="utf-8") as rfp:
        append_report_line(rfp, "")
        append_report_line(rfp, "RESULTS")
        append_report_line(rfp, f"Accuracy: {m['accuracy']:.4f}")
        append_report_line(rfp, f"Recall(pos): {m['recall_pos']:.4f}  F1(pos): {m['f1_pos']:.4f}")
        append_report_line(rfp, f"Recall(neg): {m['recall_neg']:.4f}  F1(neg): {m['f1_neg']:.4f}")
        c = m["confusion"]
        append_report_line(rfp, f"Confusion: TP={c['tp']} FP={c['fp']} FN={c['fn']} TN={c['tn']}")
        append_report_line(rfp, "")
        append_report_line(rfp, f"Human output: {out_human}")
        append_report_line(rfp, f"JSON log:     {log_path}")

    print("\nSaved:")
    print(f"  Human labels -> {out_human}")
    print(f"  Log JSON     -> {log_path}")
    print(f"  Report TXT   -> {report_path}\n")

def run_rank(args):
    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)
    rnd = random.Random(args.seed)
    order = list(range(len(data)))
    rnd.shuffle(order)

    out_human, log_path, report_path = make_paths(args.input)
    log = {
        "cmd": "rank", "input": args.input, "seed": args.seed, "max_len": args.max_len,
        "start_ts": time.time(), "skips": [], "items": []
    }

    fields = ["sentence_base", "sentence_a", "sentence_b"]
    gold_key = "label_more_similar"

    y_true, y_pred = [], []
    kept = []

    with open(report_path, "w", encoding="utf-8") as rfp:
        append_report_line(rfp, f"REPORT rank @ {datetime.now().isoformat()}")
        append_report_line(rfp, f"Input: {args.input}")
        append_report_line(rfp, f"Seed: {args.seed}  MaxLen: {args.max_len}")
        append_report_line(rfp, "-"*60)

        print(f"\nLoaded {len(data)} items. Shuffled with seed={args.seed}.")
        print("Choose 'a' or 'b'. 's' to skip.\n")

        for i, idx in enumerate(order, 1):
            rec = data[idx]
            ok, a = validate_ascii(rec, fields, args.max_len, log)
            if not ok: continue

            base, sa, sb = a["sentence_base"], a["sentence_a"], a["sentence_b"]
            print("-"*60)
            print(f"[{len(kept)+1}] Base : {base}")
            print(f"      (a): {sa}")
            print(f"      (b): {sb}")
            while True:
                lab = input("Label ('a'/'b' or 's' to skip): ").strip().lower()
                if lab in ("a","b","s"): break
                print("Please type 'a', 'b', or 's'.")
            if lab == "s":
                log["skips"].append({"reason":"user_skip", "record_preview":{"base":hash_preview(base),"a":hash_preview(sa),"b":hash_preview(sb)}})
                continue

            human = lab
            kept.append(rec)
            y_pred.append(human)
            gold = "a" if str(rec.get(gold_key)).lower()=="a" else "b"
            y_true.append(gold)

            log["items"].append({
                "idx": idx,
                "base_preview": hash_preview(base),
                "a_preview": hash_preview(sa),
                "b_preview": hash_preview(sb),
                "human": human,
                "gold_hidden": True
            })

    # Output HUMAN file
    out_records = []
    for rec, h in zip(kept, y_pred):
        new = dict(rec)
        new["label_more_similar_human"] = h
        out_records.append(new)
    write_json(out_human, out_records)

    # Metrics + report
    m = metrics_ab(y_true, y_pred)
    log["metrics"] = m
    log["end_ts"] = time.time()
    write_json(log_path, log)

    with open(report_path, "a", encoding="utf-8") as rfp:
        append_report_line(rfp, "")
        append_report_line(rfp, "RESULTS")
        append_report_line(rfp, f"Accuracy: {m['accuracy']:.4f}")
        append_report_line(rfp, f"Recall(a): {m['recall_a']:.4f}  F1(a): {m['f1_a']:.4f}")
        append_report_line(rfp, f"Recall(b): {m['recall_b']:.4f}  F1(b): {m['f1_b']:.4f}")
        c = m["confusion"]
        append_report_line(rfp, f"Confusion: a->a={c['a_to_a']} a->b={c['a_to_b']} b->a={c['b_to_a']} b->b={c['b_to_b']}")
        append_report_line(rfp, "")
        append_report_line(rfp, f"Human output: {out_human}")
        append_report_line(rfp, f"JSON log:     {log_path}")

    print("\nSaved:")
    print(f"  Human labels -> {out_human}")
    print(f"  Log JSON     -> {log_path}")
    print(f"  Report TXT   -> {report_path}\n")

# ----- CLI -----

def resolve_input_path(input_arg):
    """Resolve input path: if just a filename, look in inputs/; if full path, use as-is."""
    if os.path.sep in input_arg or input_arg.startswith("./"):
        return input_arg  # Already a path
    else:
        # Just a filename, look in inputs/
        inputs_path = os.path.join("inputs", input_arg)
        if os.path.exists(inputs_path):
            return inputs_path
        else:
            return input_arg  # Fallback to original

def build_parser():
    p = argparse.ArgumentParser(
        description="Human labeling tool for sentence classification and pairwise similarity.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    p.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed for shuffling items.")
    p.add_argument("--max-len", type=int, default=DEFAULT_MAX_LEN, help="Max characters per field; skip records exceeding this.")
    sub = p.add_subparsers(dest="cmd", required=True)

    pc = sub.add_parser("classify", help="Binary semantic similarity labeling (True/False).")
    pc.add_argument("--input", required=True, help="Path to JSON array with fields: sentence_base, sentence_test, label_semantic_similarity. If filename only, looks in inputs/ directory.")
    pc.set_defaults(func=run_classify)

    pr = sub.add_parser("rank", help="Pairwise similarity labeling ('a' vs 'b').")
    pr.add_argument("--input", required=True, help="Path to JSON array with fields: sentence_base, sentence_a, sentence_b, label_more_similar. If filename only, looks in inputs/ directory.")
    pr.set_defaults(func=run_rank)

    return p

def main():
    parser = build_parser()
    args = parser.parse_args()
    args.input = resolve_input_path(args.input)
    random.seed(args.seed)
    try:
        args.func(args)
    except KeyboardInterrupt:
        eprint("\nInterrupted by user."); sys.exit(130)

if __name__ == "__main__":
    main()
