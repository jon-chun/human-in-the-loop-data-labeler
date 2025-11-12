from __future__ import annotations
import argparse, random
from .config import AppConfig
from .paths import Paths
from .constants import Defaults
from .merge import run_merge

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Human labeling tool for sentence classification and pairwise similarity.\n\n"
            "Usage examples:\n  python label_sentences.py classify --input sentence_classifier.json\n"
            "  python label_sentences.py rank --input sentence_similarity.json\n"
            "  python label_sentences.py merge"
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--config", default="config.yaml", help="Path to YAML config.")
    p.add_argument("--seed", type=int, default=Defaults.SEED, help="Random seed for shuffling items.")
    p.add_argument("--max-len", type=int, default=Defaults.MAX_LEN, help="Max characters per field; skip records exceeding this.")
    # annotator metadata
    p.add_argument("--annotator-id", default=None, help="Annotator id (string).")
    p.add_argument("--annotator-name", default=None, help="Annotator full name.")
    p.add_argument("--annotator-email", default=None, help="Annotator email.")

    sub = p.add_subparsers(dest="cmd", required=True)

    pc = sub.add_parser("classify", help="Binary semantic similarity labeling (True/False).")
    pc.add_argument("--input", required=True, help="JSON array with fields: sentence_base, sentence_test, label_semantic_similarity.")

    pr = sub.add_parser("rank", help="Pairwise similarity labeling ('a' vs 'b').")
    pr.add_argument("--input", required=True, help="JSON array with fields: sentence_base, sentence_a, sentence_b, label_more_similar.")

    pm = sub.add_parser("merge", help="Merge all outputs/*.json into outputs-merged/merged_<ts>.json")
    pm.add_argument("--pattern", default="./outputs/*.json", help="Glob pattern to merge")

    return p

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    cfg = AppConfig.load(args.config)
    seed = args.seed if args.seed != Defaults.SEED else cfg.seed
    max_len = args.max_len if args.max_len != Defaults.MAX_LEN else cfg.max_len
    paths = Paths(cfg.dirs)

    annotator = None
    if any([args.annotator_id, args.annotator_name, args.annotator_email]):
        annotator = {"id": args.annotator_id, "name": args.annotator_name, "email": args.annotator_email}

    random.seed(seed)

    if args.cmd == "classify":
        input_path = paths.resolve_input(args.input)
        from .workflows import classify
        classify.run(input_path, seed, max_len, paths, annotator)
        return 0
    elif args.cmd == "rank":
        input_path = paths.resolve_input(args.input)
        from .workflows import rank
        rank.run(input_path, seed, max_len, paths, annotator)
        return 0
    elif args.cmd == "merge":
        out = run_merge(paths, args.pattern)
        print(f"Merged -> {out}")
        return 0
    else:
        parser.error("Unknown command")
        return 2
