# Novelty 1 Safety Support Table v2

| Row | AvgCandidateSize | GoldInFinalListRate | RowsWithContraFinal | SafetyViolation@final | Contra@final |
|---|---:|---:|---:|---:|---:|
| backbone | 20.000000 | 1.000000 | 7 | 0.014000 | 0.014000 |
| ontology | 7.650000 | 0.236000 | 5 | 0.010000 | 0.010000 |
| hard_main | 8.184000 | 0.312000 | 0 | 0.000000 | 0.000000 |
| soft_best | 7.836000 | 0.292000 | 5 | 0.010000 | 0.010000 |

## Candidate-stage notes from week 10
- hard_main fallback_after_hard: 13
- hard_main hard_removed_candidates: 73
- soft_best soft_demoted_contra_candidates: 52

## Interpretation
- hard_main is the cleanest final-list row.
- soft_best is cleaner than ontology at candidate-stage demotion, but not cleaner than hard_main at final-list level.
- backbone remains a reference row, but its final-list coverage should not be over-interpreted as directly comparable.
