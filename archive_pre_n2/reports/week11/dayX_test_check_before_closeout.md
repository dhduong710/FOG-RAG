# Novelty 1 Test Comparison

| Row | MRR | Hits@1 | Hits@3 | Hits@10 | SafetyViolation@10 | Contra@10 | SafetyViolation@final | Contra@final | GoldInFinalListRate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| backbone | 0.393101 | 0.330000 | 0.358000 | 0.524000 | 0.006000 | 0.006000 | 0.014000 | 0.014000 | 1.000000 |
| ontology | 0.435489 | 0.260000 | 0.486000 | 0.936000 | 0.006000 | 0.006000 | 0.012000 | 0.012000 | 0.280000 |
| hard_main | 0.448904 | 0.290000 | 0.480000 | 0.932000 | 0.002000 | 0.002000 | 0.002000 | 0.002000 | 0.310000 |
| soft_best | 0.417195 | 0.240000 | 0.468000 | 0.918000 | 0.002000 | 0.002000 | 0.012000 | 0.012000 | 0.280000 |

## Decision
- main_row: `hard_main`
- supporting_row: `soft_best`
- reason: hard_main is at least as safe as soft_best on final-list test metrics and is not worse on ranking.
