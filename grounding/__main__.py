"""Command line interface."""

import argparse
import json
from pathlib import Path

from grounding.core import deterministic, load_corpus
from grounding.experiment import run, verify
from grounding.models import download


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate")
    check = commands.add_parser("check")
    check.add_argument("--passage", required=True)
    check.add_argument("--claim", required=True)
    fetch = commands.add_parser("download")
    fetch.add_argument("--cache", type=Path, default=Path(".cache/models"))
    evaluate = commands.add_parser("run")
    evaluate.add_argument("--split", choices=("dev", "eval"), required=True)
    evaluate.add_argument("--output", type=Path, required=True)
    evaluate.add_argument("--cache", type=Path, default=Path(".cache/models"))
    replay = commands.add_parser("verify")
    replay.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            result = {"cases": len(load_corpus(Path("data/corpus.json"), Path.cwd()))}
        elif args.command == "check":
            result = deterministic(args.passage, args.claim)
        elif args.command == "download":
            download(args.cache)
            result = {"downloaded": True}
        elif args.command == "run":
            run(args.split, args.output, args.cache)
            result = {"report": str(args.output / "report.json")}
        else:
            result = verify(args.report)
        print(json.dumps(result))
        return 0
    except (OSError, ValueError, KeyError, TypeError, ImportError, RuntimeError) as error:
        print(json.dumps({"error": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
