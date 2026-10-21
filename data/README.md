# Corpus provenance

48 original English claim/passage pairs across 16 fictional source groups, authored for this project under MIT. Each group supplies one supported, one contradicted, and one insufficient reference label. Twelve development cases and 36 evaluation cases use disjoint passages and fictional entities. Eight evaluation categories cover exact wording, paraphrase, numbers, negation, quantifiers, time, multi-sentence inference, and missing facts.

All labels are synthetic reference judgments, not independently human-reviewed annotations. There are zero human reviews and no measured human disagreement rate. The evaluation is author-known, not blind. Templates and reference labels were frozen before model execution; no prompt or threshold tuning uses evaluation outcomes. Shared linguistic patterns across splits limit independence.

Offsets are zero-based Python Unicode character offsets with an exclusive end. Each quote must equal the source slice exactly. Sources are original fixtures, not claims about real organizations. Absence alone is not contradiction: a red bicycle does not rule out an additional blue bicycle.
