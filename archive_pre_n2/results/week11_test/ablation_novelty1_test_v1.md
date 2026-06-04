# Novelty 1 — Full Test Evaluation

| Row | MRR | Hits@1 | Hits@3 | Hits@10 | SafetyViolation@10 | Contra@10 | SafetyViolation@final | Contra@final |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| backbone | 0.393101 | 0.330000 | 0.358000 | 0.524000 | 0.006000 | 0.006000 | 0.014000 | 0.014000 |
| ontology | 0.435489 | 0.260000 | 0.486000 | 0.936000 | 0.006000 | 0.006000 | 0.012000 | 0.012000 |
| hard_main | 0.448904 | 0.290000 | 0.480000 | 0.932000 | 0.002000 | 0.002000 | 0.002000 | 0.002000 |
| soft_best | 0.417195 | 0.240000 | 0.468000 | 0.918000 | 0.002000 | 0.002000 | 0.012000 | 0.012000 |

## Decision
- main_row: `hard_main`
- supporting_row: `soft_best`
- reason: hard_main is at least as safe as soft_best on final-list test metrics and is not worse on ranking.

## Main takeaways
- hard_main is the best overall test-time trade-off row for Novelty 1.
- soft_best remains a useful supporting ablation but does not outperform hard_main.
- The test results confirm the valid-side decision and support closing Novelty 1 before moving to Novelty 2.

## Note for paper writing
- Test is the official split for final reporting.
- Valid is used for variant selection and protocol freezing.
