# Recorded evaluation

Actual offline CPU inference on an Intel Xeon W-3223, macOS 26.7.1, Python 3.11.13, two threads. The 36 evaluation cases represent 12 source groups. Each group contributes three dependent claims. No human review was performed.

## Overall

| Method | Correct / 36 | Abstentions / 36 | Supported precision | Contradicted precision | Insufficient precision |
| --- | ---: | ---: | ---: | ---: | ---: |
| deterministic | 3 | 33 | 1.000 | 1.000 | n/a |
| flan | 21 | 0 | 0.500 | 0.583 | 0.833 |
| nli | 31 | 1 | 0.923 | 0.800 | 1.000 |

`n/a` means no predictions of that class. Precision is not recall or coverage: a rule that answers only a few easy cases can have perfect precision and low coverage.

## Per-category precision and abstentions

| Category | Method | N | Correct | Abstentions | Supported precision | Contradicted precision | Insufficient precision |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| exact | deterministic | 6 | 3 | 3 | 1.000 | 1.000 | n/a |
| missing | deterministic | 6 | 0 | 6 | n/a | n/a | n/a |
| multi_sentence | deterministic | 3 | 0 | 3 | n/a | n/a | n/a |
| negation | deterministic | 3 | 0 | 3 | n/a | n/a | n/a |
| numeric | deterministic | 6 | 0 | 6 | n/a | n/a | n/a |
| paraphrase | deterministic | 6 | 0 | 6 | n/a | n/a | n/a |
| scope | deterministic | 3 | 0 | 3 | n/a | n/a | n/a |
| temporal | deterministic | 3 | 0 | 3 | n/a | n/a | n/a |
| exact | flan | 6 | 6 | 0 | 1.000 | 1.000 | 1.000 |
| missing | flan | 6 | 5 | 0 | 1.000 | 0.667 | 1.000 |
| multi_sentence | flan | 3 | 2 | 0 | n/a | 0.500 | 1.000 |
| negation | flan | 3 | 1 | 0 | n/a | 0.333 | n/a |
| numeric | flan | 6 | 2 | 0 | 0.400 | n/a | 0.000 |
| paraphrase | flan | 6 | 3 | 0 | 0.333 | 0.500 | 1.000 |
| scope | flan | 3 | 1 | 0 | 0.333 | n/a | n/a |
| temporal | flan | 3 | 1 | 0 | 0.333 | n/a | n/a |
| exact | nli | 6 | 5 | 1 | 1.000 | 1.000 | 1.000 |
| missing | nli | 6 | 5 | 0 | 1.000 | 0.667 | 1.000 |
| multi_sentence | nli | 3 | 3 | 0 | 1.000 | 1.000 | 1.000 |
| negation | nli | 3 | 3 | 0 | 1.000 | 1.000 | 1.000 |
| numeric | nli | 6 | 4 | 0 | 1.000 | 0.500 | n/a |
| paraphrase | nli | 6 | 5 | 0 | 0.667 | 1.000 | 1.000 |
| scope | nli | 3 | 3 | 0 | 1.000 | 1.000 | 1.000 |
| temporal | nli | 3 | 3 | 0 | 1.000 | 1.000 | 1.000 |

## Every claim and exact passage

Reference labels below are synthetic, not human annotations. The linked source lines are pinned to the implementation commit; the raw report also stores the exact quote and character offsets.

| Claim | Reference | Rules | FLAN | NLI | Source |
| --- | --- | --- | --- | --- | --- |
| The Amber station opens on Monday. | supported | supported | supported | supported | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p05.txt#L1-L1) |
| The Amber station does not open on Monday. | contradicted | abstain | contradicted | contradicted | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p05.txt#L1-L1) |
| The Amber station closes on Friday. | insufficient | abstain | insufficient | abstain | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p05.txt#L1-L1) |
| The Bronze office is near the river. | supported | supported | supported | supported | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p06.txt#L1-L1) |
| The Bronze office is not near the river. | contradicted | contradicted | contradicted | contradicted | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p06.txt#L1-L1) |
| The Bronze office has ten employees. | insufficient | abstain | insufficient | insufficient | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p06.txt#L1-L1) |
| Entry to the Coral museum is free. | supported | abstain | supported | supported | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p07.txt#L1-L1) |
| Every visitor must pay to enter the Coral museum. | contradicted | abstain | supported | contradicted | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p07.txt#L1-L1) |
| The Coral museum is open at night. | insufficient | abstain | insufficient | insufficient | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p07.txt#L1-L1) |
| The Dune shuttle leaves hourly. | supported | abstain | contradicted | supported | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p08.txt#L1-L1) |
| The Dune shuttle never departs. | contradicted | abstain | contradicted | contradicted | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p08.txt#L1-L1) |
| The Dune shuttle takes an hour to reach its destination. | insufficient | abstain | supported | supported | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p08.txt#L1-L1) |
| There are 25 liters of water in the Echo tank. | supported | abstain | supported | supported | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p09.txt#L1-L1) |
| The Echo tank contains exactly 50 liters of water. | contradicted | abstain | supported | contradicted | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p09.txt#L1-L1) |
| The Echo tank can hold 100 liters of water. | insufficient | abstain | supported | contradicted | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p09.txt#L1-L1) |
| Eight people belong to the Flint team. | supported | abstain | supported | supported | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p10.txt#L1-L1) |
| The Flint team has exactly nine members. | contradicted | abstain | insufficient | contradicted | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p10.txt#L1-L1) |
| The Flint team has eight vehicles. | insufficient | abstain | supported | contradicted | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p10.txt#L1-L1) |
| Food is not allowed inside the Grove lab. | supported | abstain | contradicted | supported | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p11.txt#L1-L1) |
| The Grove lab allows food inside. | contradicted | abstain | contradicted | contradicted | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p11.txt#L1-L1) |
| The Grove lab allows water inside. | insufficient | abstain | contradicted | insufficient | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p11.txt#L1-L1) |
| At least one Harbor boat has solar panels. | supported | abstain | supported | supported | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p12.txt#L1-L1) |
| Every Harbor boat has solar panels. | contradicted | abstain | supported | contradicted | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p12.txt#L1-L1) |
| Most Harbor boats have solar panels. | insufficient | abstain | supported | insufficient | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p12.txt#L1-L1) |
| The Indigo gate opened at ten in 2025. | supported | abstain | supported | supported | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p13.txt#L1-L1) |
| The Indigo gate opened at nine in 2025. | contradicted | abstain | supported | contradicted | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p13.txt#L1-L1) |
| The Indigo gate opened at ten in 2026. | insufficient | abstain | supported | insufficient | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p13.txt#L1-L1) |
| The Jade parcel is in the north hall. | supported | abstain | contradicted | supported | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p14.txt#L1-L1) |
| The Jade parcel is not in the north hall. | contradicted | abstain | contradicted | contradicted | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p14.txt#L1-L1) |
| The Jade parcel is heavy. | insufficient | abstain | insufficient | insufficient | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p14.txt#L1-L1) |
| A red bicycle belongs to the Kite library. | supported | abstain | supported | supported | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p15.txt#L1-L1) |
| The Kite library owns no bicycles. | contradicted | abstain | contradicted | contradicted | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p15.txt#L1-L1) |
| The Kite library owns a blue bicycle. | insufficient | abstain | contradicted | contradicted | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p15.txt#L1-L1) |
| The stage at the Lilac theater is made of wood. | supported | abstain | supported | supported | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p16.txt#L1-L1) |
| The Lilac theater has no stage. | contradicted | abstain | contradicted | contradicted | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p16.txt#L1-L1) |
| The Lilac theater has 300 seats. | insufficient | abstain | insufficient | insufficient | [passage](https://github.com/lucioduran/citation-grounding-checker/blob/7fb3a7ca724d31fa4db75a1057d20659a8d33a45/data/passages/p16.txt#L1-L1) |

## Interpretation

DeBERTa correctly classified all 12 supported and all 12 contradicted references. Its four errors were all insufficient references: it inferred travel duration from departure frequency, confused current water volume with tank capacity, treated team size as evidence about vehicles, and treated ownership of a red bicycle as excluding a blue bicycle. It abstained on the remaining missed insufficient claim about the Amber closing day. These failures illustrate why semantic insufficiency must remain separate from contradiction.

No population-level winner is established. These categories contain only one or two source groups each. Class precision uses few predictions and is unstable. The saved confusion matrices and recall counts are more informative than a single aggregate score.

The baseline is intentionally selective: it cannot infer paraphrases, numeric contradictions, or missing facts. Model abstention depends on output parsing or a fixed NLI confidence threshold; neither is calibrated against independent human judgments.

See [raw evaluation report](../results/eval/report.json), [development report](../results/dev/report.json), and [methodology](methodology.md). CPU durations are recorded as individual observations; no load, energy, or peak-memory benchmark is claimed.
