# Ablation v1 - Novelty 1

| Row | Story Role | MRR | Hits@1 | Hits@3 | Hits@10 | SafetyViolation@10 | Contra@10 | ConstraintViolationRate@10 | QueryHasConstraintViolationRate@10 | GoldInTopKRate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| backbone | reference | 0.424249 | 0.368000 | 0.394000 | 0.510000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 1.000000 |
| ontology | intermediate_ablation | 0.313018 | 0.244000 | 0.278000 | 0.434000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.236000 |
| hard_main | main_variant | 0.393101 | 0.330000 | 0.358000 | 0.524000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.312000 |
| soft_best | supporting_ablation | 0.393101 | 0.330000 | 0.358000 | 0.524000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.292000 |

## Main decision
- main_row: `hard_main`
- supporting_row: `soft_best`
- reason: hard_main and soft_best tie on Setting B @10 safety/constraint metrics, but hard_main has higher GoldInTopKRate and cleaner week10 candidate-stage safety proxies.

## Main takeaways
- The ontology-only row is more conservative than backbone and loses substantial ranking coverage.
- The hard_main row recovers ranking relative to ontology while remaining fully clean on Setting B @10.
- The soft_best row does not outperform hard_main and is therefore kept as a supporting ablation.
