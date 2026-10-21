# Local model notices

Both models are downloaded explicitly from Hugging Face and executed offline with safetensors and remote code disabled. Model weights are not redistributed in this repository.

- [Google FLAN-T5-small](https://huggingface.co/google/flan-t5-small), Apache-2.0, revision `0fc9ddf78a1e988dac52e2dac162b0ede4fd74ab`. General instruction model, used here as a small generative judge.
- [Cross-encoder NLI DeBERTa v3 xsmall](https://huggingface.co/cross-encoder/nli-deberta-v3-xsmall), Apache-2.0, revision `a150876415327c80daeff35ca6f68f5ed8cf5c24`. NLI classifier trained on SNLI and MultiNLI, used as a discriminative judge. The upstream model card specifies contradiction, entailment, neutral label order.

These choices establish two actual local architectures, not agreement with human adjudication. Upstream benchmark numbers are not reproduced here. Python packages retain their upstream licenses. The native dependency lock records the Intel macOS reference environment; other platforms may need compatible PyTorch builds. Portable CI installs only development tools and checks saved evidence without neural inference.
