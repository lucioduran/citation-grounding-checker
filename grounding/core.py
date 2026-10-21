"""Input contracts, conservative rules, and transparent scoring."""

import hashlib
import json
import math
import re
from pathlib import Path

LABELS = ("supported", "contradicted", "insufficient")
PREDICTIONS = (*LABELS, "abstain")
FIELDS = {
    "id",
    "split",
    "category",
    "source",
    "start",
    "end",
    "quote",
    "claim",
    "label",
    "label_origin",
    "rationale",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_corpus(path: Path, root: Path) -> list[dict]:
    cases = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(cases, list) or not cases:
        raise ValueError("Corpus must be a nonempty list")
    ids: set[str] = set()
    sources: dict[str, str] = {}
    for case in cases:
        if not isinstance(case, dict) or set(case) != FIELDS:
            raise ValueError("Unexpected corpus fields")
        for field in FIELDS - {"start", "end"}:
            if not isinstance(case[field], str) or not case[field].strip():
                raise ValueError(f"Invalid string: {field}")
        if case["id"] in ids or not re.fullmatch(r"[a-z0-9-]+", case["id"]):
            raise ValueError("Duplicate or unsafe case ID")
        ids.add(case["id"])
        if case["split"] not in ("dev", "eval") or case["label"] not in LABELS:
            raise ValueError("Invalid split or label")
        if case["label_origin"] != "synthetic_reference":
            raise ValueError("This schema supports synthetic references only")
        source = case["source"]
        if not re.fullmatch(r"data/passages/[a-z0-9-]+\.txt", source):
            raise ValueError("Unsafe source path")
        resolved = (root / source).resolve()
        if not resolved.is_relative_to(root.resolve()):
            raise ValueError("Source escapes corpus root")
        if sources.setdefault(source, case["split"]) != case["split"]:
            raise ValueError("Source group overlaps splits")
        text = resolved.read_bytes().decode("utf-8")
        start, end = case["start"], case["end"]
        if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(text):
            raise ValueError("Invalid passage offsets")
        if text[start:end] != case["quote"]:
            raise ValueError("Passage does not match source slice")
    return cases


def deterministic(passage: str, claim: str) -> dict:
    sentences = [s.strip().casefold() for s in re.split(r"(?<=[.!?])\s+", passage)]
    normalized = claim.strip().casefold()
    if normalized in sentences:
        return {"prediction": "supported", "reason": "exact_sentence"}
    # Only explicit copula negation is recognized; absence is never contradiction.
    for sentence in sentences:
        for positive, negative in ((" is ", " is not "), (" are ", " are not ")):
            if negative in sentence and sentence.replace(negative, positive, 1) == normalized:
                return {"prediction": "contradicted", "reason": "explicit_negation"}
            if negative in normalized and normalized.replace(negative, positive, 1) == sentence:
                return {"prediction": "contradicted", "reason": "explicit_negation"}
    return {"prediction": "abstain", "reason": "outside_rule_grammar"}


def parse_flan(raw: str) -> str:
    value = raw.strip().casefold()
    return value if value in LABELS else "abstain"


def parse_nli(probabilities: list[float]) -> str:
    if (
        len(probabilities) != 3
        or any(
            not isinstance(x, (int, float)) or not math.isfinite(x) or not 0 <= x <= 1
            for x in probabilities
        )
        or not math.isclose(sum(probabilities), 1, abs_tol=1e-5)
    ):
        raise ValueError("Expected three finite normalized probabilities")
    index = max(range(3), key=probabilities.__getitem__)
    return (
        ("contradicted", "supported", "insufficient")[index]
        if probabilities[index] >= 0.6
        else "abstain"
    )


def score(rows: list[dict]) -> dict:
    if not rows or any(
        r["label"] not in LABELS or r["prediction"] not in PREDICTIONS for r in rows
    ):
        raise ValueError("Cannot score empty or invalid predictions")
    confusion = {label: {pred: 0 for pred in PREDICTIONS} for label in LABELS}
    for row in rows:
        confusion[row["label"]][row["prediction"]] += 1
    correct = sum(r["prediction"] == r["label"] for r in rows)
    abstentions = sum(r["prediction"] == "abstain" for r in rows)
    return {
        "n": len(rows),
        "correct": correct,
        "abstentions": abstentions,
        "accuracy": correct / len(rows),
        "coverage": 1 - abstentions / len(rows),
        "selective_accuracy": correct / (len(rows) - abstentions)
        if len(rows) > abstentions
        else None,
        "confusion": confusion,
        "precision": {
            label: confusion[label][label] / count
            if (count := sum(confusion[ref][label] for ref in LABELS))
            else None
            for label in LABELS
        },
        "recall": {
            label: confusion[label][label] / count
            if (count := sum(confusion[label].values()))
            else None
            for label in LABELS
        },
    }


def summaries(rows: list[dict]) -> dict:
    return {
        method: {
            "overall": score(group := [r for r in rows if r["method"] == method]),
            "categories": {
                category: score([r for r in group if r["category"] == category])
                for category in sorted({r["category"] for r in group})
            },
        }
        for method in sorted({r["method"] for r in rows})
    }


def passage_url(case: dict, revision: str, root: Path) -> str:
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Expected immutable Git revision")
    text = (root / case["source"]).read_bytes().decode("utf-8")
    first = text[: case["start"]].count("\n") + 1
    last = text[: case["end"] - 1].count("\n") + 1
    return f"https://github.com/lucioduran/citation-grounding-checker/blob/{revision}/{case['source']}#L{first}-L{last}"
