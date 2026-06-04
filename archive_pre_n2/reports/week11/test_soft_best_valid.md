# Week 11 - Day 3 Setting B Valid (soft_best_test)

## Ranking metrics
- mrr: 0.41719476
- hits1: 0.24
- hits3: 0.468
- hits10: 0.918

## Setting B metrics
- num_queries: 500
- K: 10
- SafetyViolation@10: 0.002
- Contra@10: 0.002
- ConstraintViolationRate@10: 0.0
- QueryHasConstraintViolationRate@10: 0.0
- GoldInTopKRate: 0.28

## Case summary
- safety_violation_cases: 1
- constraint_violation_cases: 0
- gold_missing_cases: 20
- clean_cases: 20

## Notes
- Day 3 prioritizes the main candidate row under the frozen Setting B protocol.
- Day 4 will run the same evaluation on soft_best for trade-off comparison.
