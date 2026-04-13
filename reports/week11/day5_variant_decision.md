# Week 11 - Day 5 Variant Decision

| Row | MRR | Hits@1 | Hits@3 | Hits@10 | SafetyViolation@10 | Contra@10 | ConstraintViolationRate@10 | QueryHasConstraintViolationRate@10 | GoldInTopKRate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| backbone | 0.424249 | 0.368000 | 0.394000 | 0.510000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 1.000000 |
| ontology | 0.313018 | 0.244000 | 0.278000 | 0.434000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.236000 |
| hard_main | 0.393101 | 0.330000 | 0.358000 | 0.524000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.312000 |
| soft_best | 0.393101 | 0.330000 | 0.358000 | 0.524000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.292000 |

## Decision
- main_row: `hard_main`
- supporting_row: `soft_best`
- reason: hard_main and soft_best tie on Setting B @10 safety/constraint metrics, but hard_main has higher GoldInTopKRate and cleaner week10 candidate-stage safety proxies.

## Notes
- backbone and ontology are reference rows.
- hard_main and soft_best are the Novelty 1 safety rows.
- The final choice is based on valid-first protocol.
