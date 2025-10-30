#!/usr/bin/env python3
"""
label_sentences.py (enhanced)

A human-in-the-loop data labeling tool for NLP tasks that supports two workflows:

1. CLASSIFICATION: Label semantic similarity between sentence pairs as True/False
   - Input: JSON with sentence_base, sentence_test, label_semantic_similarity
   - Usage: python label_sentences.py classify --input sentence_classifier.json

2. RANKING: Choose which of two sentences is more similar to a base sentence
   - Input: JSON with sentence_base, sentence_a, sentence_b, label_more_similar
   - Usage: python label_sentences.py rank --input sentence_similarity.json

Enhanced features:
- Structured JSON logging to ./logs/log_{datetime}.json
- Plain-text reporting to ./reports/report_{datetime}.txt
- ASCII 7-bit normalization; skip-invalid logging
- Reproducible shuffling with --seed
- Outputs human-labeled file: <root>_HUMAN<ext>
- Console summary of metrics

The tool automatically looks in the 'inputs/' directory for input files if only a filename is provided.
All outputs are saved to organized subdirectories (outputs/, logs/, reports/).
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

# ----- Help System -----

def print_help_menu(workflow_type="general"):
    """Display comprehensive help menu based on workflow type."""
    print("\n" + "=" * 70)
    print("HELP MENU")
    print("=" * 70)
    print()
    print("Help options:")
    print("  1 - Show task-specific help")
    print("  2 - Recall introduction message")
    print("  3 - Show general help")
    print()

    while True:
        choice = input("Select help option (1-3) or Enter to exit help: ").strip()
        if not choice or choice == "":
            break
        elif choice == "1":
            print("\n" + "-" * 70)
            if workflow_type == "classify":
                print_classification_help()
            elif workflow_type == "rank":
                print_ranking_help()
            else:
                print_general_help()
            print("\n" + "-" * 70)
            print()
        elif choice == "2":
            print("\n" + "-" * 70)
            print_introduction_message(workflow_type)
            print("-" * 70)
            print()
        elif choice == "3":
            print("\n" + "-" * 70)
            print_general_help()
            print("\n" + "-" * 70)
            print()
        else:
            print("Please select 1, 2, 3, or press Enter to exit help.")

    print("Returning to labeling...")

def print_general_help():
    """Print general help information applicable to all workflows."""
    print("GENERAL HELP")
    print("-" * 40)
    print()
    print("KEYBOARD SHORTCUTS:")
    print("  h     - Show this help menu")
    print("  s     - Skip current item (continue to next)")
    print("  Ctrl+C - Exit the program")
    print()
    print("INPUT VALIDATION:")
    print("  • All text is normalized to 7-bit ASCII for console compatibility")
    print("  • Records longer than max_len characters are skipped automatically")
    print("  • Missing or empty required fields are skipped automatically")
    print("  • All skipped items are logged with privacy-preserving hashes")
    print()
    print("OUTPUT FILES:")
    print("  • outputs/ - Human-labeled data files")
    print("  • logs/    - Structured JSON logs with metrics and metadata")
    print("  • reports/ - Human-readable text reports")
    print()
    print("REPRODUCIBILITY:")
    print("  • Items are shuffled using the seed value (--seed)")
    print("  • Same seed = same order across different runs")
    print("  • Default seed is 42")
    print()
    print("METRICS EXPLANATION:")
    print("  • Accuracy: Overall correct labeling rate")
    print("  • Precision: Of items labeled X, how many were actually X")
    print("  • Recall: Of actual X items, how many were labeled X")
    print("  • F1 Score: Harmonic mean of precision and recall")
    print()
    print("PRIVACY NOTES:")
    print("  • Logs store text previews with SHA256 hashes, not full text")
    print("  • Human output files contain original text content")
    print("  • No personal data is collected or transmitted")
    print()

def print_classification_help():
    """Print classification-specific help."""
    print_general_help()
    print("CLASSIFICATION WORKFLOW HELP:")
    print("-" * 40)
    print()
    print("YOUR TASK:")
    print("  Determine if two sentences have similar semantic meaning")
    print()
    print("LABELING OPTIONS:")
    print("  t, true  - Sentences ARE semantically similar")
    print("  f, false - Sentences are NOT semantically similar")
    print("  s        - Skip this item")
    print()
    print("INPUT FORMAT:")
    print("  • sentence_base: The reference sentence")
    print("  • sentence_test: The sentence to compare against base")
    print("  • label_semantic_similarity: Gold label (hidden from you)")
    print()
    print("EXAMPLES:")
    print("  Base: 'The cat sits on the mat'")
    print("  Test: 'A feline rests on the rug'")
    print("  Label: t (true - similar meaning)")
    print()
    print("  Base: 'I love programming'")
    print("  Test: 'The weather is cold today'")
    print("  Label: f (false - different meaning)")
    print()

def print_ranking_help():
    """Print ranking-specific help."""
    print_general_help()
    print("RANKING WORKFLOW HELP:")
    print("-" * 40)
    print()
    print("YOUR TASK:")
    print("  Choose which sentence is more similar to the base sentence")
    print()
    print("LABELING OPTIONS:")
    print("  a - Sentence (a) is more similar to base")
    print("  b - Sentence (b) is more similar to base")
    print("  s - Skip this item")
    print()
    print("INPUT FORMAT:")
    print("  • sentence_base: The reference sentence")
    print("  • sentence_a: First comparison option")
    print("  • sentence_b: Second comparison option")
    print("  • label_more_similar: Gold label (hidden from you)")
    print()
    print("EXAMPLES:")
    print("  Base: 'The weather is nice today'")
    print("  (a): 'It\\'s a beautiful sunny day'")
    print("  (b): 'I need to buy groceries'")
    print("  Label: a (sentence a is more similar)")
    print()
    print("  Base: 'Programming in Python is fun'")
    print("  (a): 'Java is also a programming language'")
    print("  (b): 'The cat is sleeping'")
    print("  Label: a (sentence a is more similar to programming)")
    print()

def print_introduction_message(workflow_type):
    """Print the introduction message (can be recalled from help)."""
    if workflow_type == "classify":
        print_classify_intro()
    elif workflow_type == "rank":
        print_rank_intro()

# ----- Workflows -----

def print_classify_intro():
    """Print introduction specific to the classification workflow."""
    print("=" * 70)
    print("CLASSIFICATION Workflow: Semantic Similarity Labeling")
    print("=" * 70)
    print("You will label whether sentence pairs are semantically similar.")
    print("For each item, you'll see:")
    print("  • A base sentence")
    print("  • A test sentence to compare against the base")
    print()
    print("Your task: Determine if the test sentence has similar meaning to the base sentence.")
    print("  • Type 't' (true) if they ARE semantically similar")
    print("  • Type 'f' (false) if they are NOT semantically similar")
    print("  • Type 's' to skip the current item")
    print("  • Type 'h' to show help menu")
    print()
    print("Example:")
    print("  Base: 'The cat sits on the mat'")
    print("  Test: 'A feline is resting on the rug'")
    print("  Label: 't' (true - they have similar meaning)")
    print()
    print("All outputs are saved to outputs/, logs/, and reports/ directories")
    print("Press Ctrl+C to exit at any time")
    print()
    print("Starting classification workflow...\n")

def print_rank_intro():
    """Print introduction specific to the ranking workflow."""
    print("=" * 70)
    print("RANKING Workflow: Pairwise Similarity Comparison")
    print("=" * 70)
    print("You will choose which of two sentences is more similar to a base sentence.")
    print("For each item, you'll see:")
    print("  • A base sentence")
    print("  • Sentence (a): First comparison option")
    print("  • Sentence (b): Second comparison option")
    print()
    print("Your task: Determine which sentence (a or b) is more similar to the base.")
    print("  • Type 'a' if sentence (a) is more similar to the base")
    print("  • Type 'b' if sentence (b) is more similar to the base")
    print("  • Type 's' to skip the current item")
    print("  • Type 'h' to show help menu")
    print()
    print("Example:")
    print("  Base: 'The weather is nice today'")
    print("  (a): 'It\'s a beautiful sunny day'")
    print("  (b): 'I need to buy groceries'")
    print("  Label: 'a' (sentence a is more similar to the base)")
    print()
    print("All outputs are saved to outputs/, logs/, and reports/ directories")
    print("Press Ctrl+C to exit at any time")
    print()
    print("Starting ranking workflow...\n")

def run_classify(args):
    print_classify_intro()

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
                lab = input("Label (t/f/h or s to skip): ").strip().lower()
                if lab == "h":
                    print_help_menu("classify")
                    # Redisplay current item after help
                    print("-"*60)
                    print(f"[{len(kept)+1}] Base : {base}")
                    print(f"      Test : {test}")
                    continue
                elif lab in ("t","true","f","false","s"):
                    break
                print("Please type 't', 'f', 'h', or 's'.")
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
    print_rank_intro()

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
                lab = input("Label ('a'/'b'/'h' or 's' to skip): ").strip().lower()
                if lab == "h":
                    print_help_menu("rank")
                    # Redisplay current item after help
                    print("-"*60)
                    print(f"[{len(kept)+1}] Base : {base}")
                    print(f"      (a): {sa}")
                    print(f"      (b): {sb}")
                    continue
                elif lab in ("a","b","s"):
                    break
                print("Please type 'a', 'b', 'h', or 's'.")
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
        description="Human labeling tool for sentence classification and pairwise similarity.\n\nUsage examples:\n  python label_sentences.py classify --input sentence_classifier.json\n  python label_sentences.py rank --input sentence_similarity.json",
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
