# Citation Grounding Checker

[![CI](https://github.com/lucioduran/citation-grounding-checker/actions/workflows/ci.yml/badge.svg)](https://github.com/lucioduran/citation-grounding-checker/actions/workflows/ci.yml)

Compare exact-sentence rules with two real local model judges. Follow every verdict back to its exact source passage.

## Problem

Finding a source does not establish that it supports a claim. Numeric changes, negation, time, and missing context can turn an apparently relevant citation into unsupported evidence. This project exposes the claim, quoted passage, reference judgment, and checker output together.

## Scope

Project 07 of the engineering evidence series. The corpus has 48 original fictional claim/passage pairs: 12 development and 36 evaluation cases, grouped into 16 distinct source passages. Reference classes are supported, contradicted, and insufficient. A fourth output, abstain, means the checker declined classification.

Compare a conservative deterministic baseline, Google FLAN-T5-small, and an NLI DeBERTa v3 xsmall classifier. All model inference is local CPU execution. There are no paid APIs. Labels are synthetic reference judgments. **There is no independent human review and no measured human disagreement rate.**

## Quick start

With Python 3.11 or later, inspect and verify saved evidence without model dependencies:

```sh
git clone https://github.com/lucioduran/citation-grounding-checker.git
cd citation-grounding-checker
python -m grounding validate
python -m grounding verify --report results/eval/report.json
python -m grounding check --passage "The gate is open." --claim "The gate is not open."
```

Run commands from the repository root. The last command returns a contradicted verdict with the explicit-negation rule as its reason.

## Usage

| Command | Behavior |
| --- | --- |
| `validate` | Validate corpus fields, split isolation, paths, offsets, and exact quotes |
| `check --passage TEXT --claim TEXT` | Apply the deterministic baseline to a pair |
| `download` | Explicitly fetch the pinned free model files |
| `run --split dev --output PATH` | Run all three checkers on development cases |
| `run --split eval --output PATH` | Run the frozen evaluation |
| `verify --report PATH` | Replay source checks, output parsing, and scoring offline |

`download` and `run` accept `--cache PATH`. Each run requires a new output directory and a clean tracked Git tree. It writes an incremental `trace.jsonl`, then `report.json` and `summary.json` after successful completion. An interrupted run can leave partial evidence; retry into a new directory. Exit code 0 means success and 2 means invalid input or an execution error. `check` returning abstain is a valid result, not a process failure.

## Architecture

```text
Original passages + claims + synthetic reference labels
                      |
          exact quote / offset validation
                      |
         +------------+------------+
         |            |            |
    sentence rules  FLAN-T5     DeBERTa NLI
         |            |            |
         +------------+------------+
                      |
       raw evidence + immutable passage links
                      |
       category metrics + offline report replay
```

Judges receive only the passage and claim. Labels, rationales, and category names never enter model inputs. No source retrieval is involved. See [methodology](docs/methodology.md), [corpus provenance](data/README.md), and [model notices](docs/model-notices.md).

## Reproduction

The reference native environment is Python 3.11.13 on Intel macOS with two CPU threads. The pinned package lock is specific to that environment; other systems may require compatible PyTorch packages. Portable report replay is tested separately across Linux, macOS, and Windows.

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-local.lock
python -m grounding download
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 python -m grounding run --split dev --output build/dev
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 python -m grounding run --split eval --output build/eval
python -m grounding verify --report build/eval/report.json
```

On Windows, activate with `.venv\Scripts\Activate.ps1` and set environment variables in PowerShell before running Python. Model loading itself enforces local-only access. Downloads require internet and several hundred megabytes of storage. The published measurements were serialized through the project series' shared benchmark lock; that coordinator-specific wrapper is not required in standalone clones.

Frozen settings: seed 1729, two CPU threads, 384 input tokens with no truncation, eight generated tokens, greedy decoding, and NLI maximum-probability threshold 0.6. Reports include exact model revisions, weight hashes, package versions, CPU identity, code revision, corpus hashes, and UTC timestamps. No prompts, labels, or thresholds were tuned after evaluation.

## Results

Results are recorded in [development evidence](results/dev/report.json) and [evaluation evidence](results/eval/report.json). See [category metrics and error analysis](docs/results.md) for every category and exact passage links.

## Testing

```sh
python -m pip install -r requirements-dev.txt
python -m ruff check .
python -m ruff format --check .
python -m coverage run -m unittest discover -v
python -m coverage report --fail-under=90
python -m grounding verify --report results/dev/report.json
python -m grounding verify --report results/eval/report.json
```

Tests cover invalid corpus fields and offsets, split overlap, exact sentences, negation, abstentions, hand-calculated metrics, malformed model probabilities, pinned downloads, offline loading, token limits, CLI behavior, and tampered reports. Adapter unit tests use mocks; committed experiment records come from actual neural execution. CI enforces a 90% combined statement/branch coverage gate and replays both reports on three operating systems.

## Limitations

- Small, synthetic, author-known fixtures cannot establish real-world grounding accuracy or superiority. Claims sharing one passage are dependent, and some linguistic templates recur across splits.
- There are zero independent human annotations. Reference judgments can be wrong; no agreement statistics or human comparison is claimed.
- Exact-sentence rules are deliberately narrow and can be fooled by inconsistent or quoted statements. Their abstention is not a claim of insufficient evidence.
- Small local models can make confident errors. The NLI threshold is fixed and uncalibrated. Invalid generated labels abstain; semantic insufficiency is scored separately.
- Replay verifies internal consistency, not inference authenticity. It does not independently rerun neural inference or recount tokenizer tokens. Hashes identify bytes, not factual truth or authorship.
- Timings are single observations, not a benchmark of sustained throughput. Energy, memory peaks, and hardware cost are unmeasured. Zero paid API cost excludes electricity and equipment cost.
- English only, trusted local files, no retrieval, live web auditing, human review workflow, or production security certification.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md). Add regression tests and preserve prior experiment evidence. Report sensitive issues as described in [SECURITY.md](SECURITY.md).

## License

Code, original fictional passages, synthetic labels, documentation, and results use the [MIT license](LICENSE). Model weights are not redistributed and retain upstream Apache-2.0 licensing. Dependencies retain their own licenses.
