"""Record all evidence and replay scoring without neural dependencies."""

import importlib.metadata
import json
import math
import platform
import re
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

from grounding.core import (
    deterministic,
    digest,
    load_corpus,
    parse_flan,
    parse_nli,
    passage_url,
    summaries,
)
from grounding.models import PROMPT, Judge, specs


def revision() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def run(split: str, output: Path, cache: Path) -> None:
    cases = [c for c in load_corpus(Path("data/corpus.json"), Path.cwd()) if c["split"] == split]
    if not cases:
        raise ValueError("Empty split")
    if subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"], text=True
    ).strip():
        raise ValueError("Commit tracked changes before recording evidence")
    output.mkdir(parents=True, exist_ok=False)
    rev = revision()
    rows, models = [], {}
    with (output / "trace.jsonl").open("w", encoding="utf-8") as trace:
        for method in ("deterministic", "flan", "nli"):
            start = time.perf_counter()
            judge = None if method == "deterministic" else Judge(method, cache)
            if judge:
                models[method] = {
                    "spec": specs()[method],
                    "files": judge.files,
                    "load_seconds": time.perf_counter() - start,
                }
            for case in cases:
                start = time.perf_counter()
                result = (
                    deterministic(case["quote"], case["claim"])
                    if judge is None
                    else judge.predict(case["quote"], case["claim"])
                )
                row = dict(
                    case,
                    method=method,
                    result=result,
                    prediction=result["prediction"],
                    seconds=time.perf_counter() - start,
                    passage_url=passage_url(case, rev, Path.cwd()),
                )
                trace.write(json.dumps(row) + "\n")
                trace.flush()
                rows.append(row)
            del judge
    cpu = platform.processor()
    if platform.system() == "Darwin":
        cpu = subprocess.check_output(
            ["sysctl", "-n", "machdep.cpu.brand_string"], text=True
        ).strip()
    report = {
        "schema_version": 1,
        "split": split,
        "revision": rev,
        "created_utc": datetime.now(UTC).isoformat(),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "cpu": cpu,
            "threads": 2,
            "seed": 1729,
            "device": "cpu",
            "packages": {
                name: importlib.metadata.version(name)
                for name in (
                    "torch",
                    "transformers",
                    "numpy",
                    "tokenizers",
                    "safetensors",
                    "sentencepiece",
                    "huggingface-hub",
                )
            },
        },
        "paid_api_cost_usd": 0,
        "human_reviews": 0,
        "hashes": {
            p.as_posix(): digest(p)
            for p in [
                Path("data/corpus.json"),
                Path("config/models.json"),
                *sorted(Path("data/passages").glob("*.txt")),
            ]
        },
        "models": models,
        "rows": rows,
        "summary": summaries(rows),
    }
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (output / "summary.json").write_text(
        json.dumps(report["summary"], indent=2) + "\n", encoding="utf-8"
    )


def verify(path: Path) -> dict:
    report = json.loads(path.read_text(encoding="utf-8"))
    if report["schema_version"] != 1 or report["split"] not in ("dev", "eval"):
        raise ValueError("Invalid report schema or split")
    if report["human_reviews"] != 0 or report["paid_api_cost_usd"] != 0:
        raise ValueError("Unexpected review or cost claims")
    environment = report["environment"]
    if any(
        environment[key] != value
        for key, value in {"threads": 2, "seed": 1729, "device": "cpu"}.items()
    ):
        raise ValueError("Execution settings changed")
    cases = {
        c["id"]: c
        for c in load_corpus(Path("data/corpus.json"), Path.cwd())
        if c["split"] == report["split"]
    }
    paths = [
        Path("data/corpus.json"),
        Path("config/models.json"),
        *sorted(Path("data/passages").glob("*.txt")),
    ]
    if report["hashes"] != {p.as_posix(): digest(p) for p in paths}:
        raise ValueError("Input hashes changed")
    expected = {(cid, method) for cid in cases for method in ("deterministic", "flan", "nli")}
    seen = set()
    for row in report["rows"]:
        key = (row["id"], row["method"])
        if key not in expected or key in seen:
            raise ValueError("Unexpected or duplicate prediction")
        seen.add(key)
        if (
            not isinstance(row["seconds"], (int, float))
            or not math.isfinite(row["seconds"])
            or row["seconds"] < 0
        ):
            raise ValueError("Invalid duration")
        case = cases[row["id"]]
        if any(row[k] != v for k, v in case.items()):
            raise ValueError("Case evidence changed")
        if row["passage_url"] != passage_url(case, report["revision"], Path.cwd()):
            raise ValueError("Passage link changed")
        result = row["result"]
        if row["method"] == "deterministic":
            if result != deterministic(case["quote"], case["claim"]):
                raise ValueError("Rule output changed")
            pred = result["prediction"]
        elif row["method"] == "flan":
            if result["prompt"] != PROMPT.format(passage=case["quote"], claim=case["claim"]):
                raise ValueError("Prompt changed")
            pred = parse_flan(result["raw"])
        else:
            pred = parse_nli(result["probabilities"])
        if row["method"] != "deterministic" and not 0 < result["input_tokens"] <= 384:
            raise ValueError("Invalid token count")
        if pred != row["prediction"] or pred != result["prediction"]:
            raise ValueError("Prediction does not match raw evidence")
    if seen != expected or report["summary"] != summaries(report["rows"]):
        raise ValueError("Missing predictions or incorrect metrics")
    if set(report["models"]) != {"flan", "nli"}:
        raise ValueError("Missing model provenance")
    for method, evidence in report["models"].items():
        if evidence["spec"] != specs()[method] or "model.safetensors" not in evidence["files"]:
            raise ValueError("Invalid model provenance")
        if any(
            not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value)
            for value in evidence["files"].values()
        ):
            raise ValueError("Invalid model file hash")
    return {"verified": True, "predictions": len(seen), "split": report["split"]}
