# Week 11 - Day 3 Setting B Valid (backbone_test)

## Ranking metrics
- mrr: 0.39310116
- hits1: 0.33
- hits3: 0.358
- hits10: 0.524

## Setting B metrics
- num_queries: 500
- K: 10
- SafetyViolation@10: 0.006
- Contra@10: 0.006
- ConstraintViolationRate@10: 0.0
- QueryHasConstraintViolationRate@10: 0.0
- GoldInTopKRate: 1.0

## Case summary
- safety_violation_cases: 3
- constraint_violation_cases: 0
- gold_missing_cases: 0
- clean_cases: 20

## Notes
- Day 3 prioritizes the main candidate row under the frozen Setting B protocol.
- Day 4 will run the same evaluation on soft_best for trade-off comparison.
