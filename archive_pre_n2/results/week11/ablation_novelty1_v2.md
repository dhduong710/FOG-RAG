# Ablation v2 - Novelty 1 (patched)

| Row | MRR | Hits@1 | Hits@3 | Hits@10 | SafetyViolation@10 | Contra@10 | SafetyViolation@final | Contra@final |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| backbone | 0.424249 | 0.368000 | 0.394000 | 0.510000 | 0.000000 | 0.000000 | 0.014000 | 0.014000 |
| ontology | 0.313018 | 0.244000 | 0.278000 | 0.434000 | 0.000000 | 0.000000 | 0.010000 | 0.010000 |
| hard_main | 0.393101 | 0.330000 | 0.358000 | 0.524000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| soft_best | 0.393101 | 0.330000 | 0.358000 | 0.524000 | 0.000000 | 0.000000 | 0.010000 | 0.010000 |

## Decision
- main_row: `hard_main`
- supporting_row: `soft_best`
- reason: hard_main and soft_best tie on Setting B @10 safety/constraint metrics, but hard_main has higher GoldInTopKRate and cleaner week10 candidate-stage safety proxies.

## Notes
- GoldInFinalListRate is not used in the main table because the backbone reference row is not directly comparable on this axis.
- The main table now combines ranking + Setting B @10 + final-list safety.
