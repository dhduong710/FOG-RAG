# Novelty 1 Closeout (Post-fix Rerun)

## 1. Scope of this closeout
- This closeout replaces the old ranking summary with split-correct rerun results.
- Valid and test ranking metrics below are the official post-fix numbers.

## 2. Official valid ranking table

| Variant | MRR | Hits@1 | Hits@3 | Hits@10 |
|---|---:|---:|---:|---:|
| Backbone | 0.4242 | 0.3680 | 0.3940 | 0.5100 |
| + Ontology | 0.3687 | 0.1760 | 0.4540 | 0.8460 |
| + Ontology + Hard | 0.4675 | 0.2940 | 0.5380 | 0.9220 |
| + Ontology + Soft | 0.4322 | 0.2460 | 0.5180 | 0.9000 |

## 3. Official test ranking table

| Variant | MRR | Hits@1 | Hits@3 | Hits@10 |
|---|---:|---:|---:|---:|
| Backbone | 0.3931 | 0.3300 | 0.3580 | 0.5240 |
| + Ontology | 0.4355 | 0.2600 | 0.4860 | 0.9360 |
| + Ontology + Hard | 0.4489 | 0.2900 | 0.4800 | 0.9320 |
| + Ontology + Soft | 0.4172 | 0.2400 | 0.4680 | 0.9180 |

## 4. Decision
- **Main row**: `+ Ontology + Hard`
- **Supporting row**: `+ Ontology + Soft`

## 5. Reason for main row selection
- `+ Ontology + Hard` achieves the best test MRR among the compared rows.
- It also remains the cleanest main candidate-stage safety variant in the novelty story.
- `+ Ontology + Soft` remains useful as a supporting trade-off row.

## 6. Final narrative for presentation / paper
- The project first reproduced a DrKGC-style backbone.
- Novelty 1 then improved the candidate stage through ontology-aware and contraindication-aware retrieval.
- After the split fix, the final rerun confirms that the novelty rows outperform the backbone in overall ranking trade-off, with `+ Ontology + Hard` as the strongest main row.
