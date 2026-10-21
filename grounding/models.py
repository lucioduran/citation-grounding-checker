"""Explicit downloads and offline CPU inference; no remote code execution."""

import json
from pathlib import Path

from grounding.core import digest, parse_flan, parse_nli

PROMPT = (
    "Classify the claim using only the passage. Reply with exactly one label: "
    "supported, contradicted, or insufficient. Supported means the passage entails the claim. "
    "Contradicted means it entails the opposite. Insufficient means neither.\n"
    "Passage: {passage}\nClaim: {claim}\nLabel:"
)


def specs() -> dict:
    return json.loads(Path("config/models.json").read_text())


def model_path(cache: Path, spec: dict) -> Path:
    return cache / spec["id"].replace("/", "--") / spec["revision"]


def download(cache: Path) -> None:
    from huggingface_hub import snapshot_download

    for spec in specs().values():
        snapshot_download(
            spec["id"],
            revision=spec["revision"],
            local_dir=model_path(cache, spec),
            token=False,
            allow_patterns=["*.json", "*.model", "model.safetensors"],
        )


class Judge:
    def __init__(self, method: str, cache: Path):
        import torch
        from transformers import (
            AutoModelForSeq2SeqLM,
            AutoModelForSequenceClassification,
            AutoTokenizer,
        )

        if method not in ("flan", "nli"):
            raise ValueError("Unknown judge")
        torch.set_num_threads(2)
        torch.manual_seed(1729)
        torch.use_deterministic_algorithms(True)
        self.torch, self.method = torch, method
        path = model_path(cache, specs()[method])
        self.files = {p.name: digest(p) for p in sorted(path.iterdir()) if p.is_file()}
        options = {"local_files_only": True, "trust_remote_code": False}
        self.tokenizer = AutoTokenizer.from_pretrained(path, **options)
        factory = AutoModelForSeq2SeqLM if method == "flan" else AutoModelForSequenceClassification
        self.model = factory.from_pretrained(path, use_safetensors=True, **options).eval()
        if method == "nli" and self.model.config.id2label != {
            0: "contradiction",
            1: "entailment",
            2: "neutral",
        }:
            raise ValueError("Unexpected NLI label mapping")

    def predict(self, passage: str, claim: str) -> dict:
        prompt = PROMPT.format(passage=passage, claim=claim)
        args = (prompt,) if self.method == "flan" else (passage, claim)
        encoded = self.tokenizer(*args, return_tensors="pt", truncation=False)
        count = encoded["input_ids"].shape[1]
        if count > 384:
            raise ValueError("Input exceeds 384 tokens; truncation is forbidden")
        with self.torch.inference_mode():
            if self.method == "flan":
                tokens = self.model.generate(
                    **encoded, max_new_tokens=8, do_sample=False, num_beams=1
                )
                raw = self.tokenizer.decode(tokens[0], skip_special_tokens=True)
                return {
                    "prediction": parse_flan(raw),
                    "raw": raw,
                    "prompt": prompt,
                    "input_tokens": count,
                }
            probabilities = self.model(**encoded).logits.softmax(dim=-1)[0].tolist()
            return {
                "prediction": parse_nli(probabilities),
                "probabilities": probabilities,
                "input_tokens": count,
            }
