# Week 11 - Day 3 Setting B Valid (hard_main_test)

## Ranking metrics
- mrr: 0.44890444
- hits1: 0.29
- hits3: 0.48
- hits10: 0.932

## Setting B metrics
- num_queries: 500
- K: 10
- SafetyViolation@10: 0.002
- Contra@10: 0.002
- ConstraintViolationRate@10: 0.0
- QueryHasConstraintViolationRate@10: 0.0
- GoldInTopKRate: 0.31

## Case summary
- safety_violation_cases: 1
- constraint_violation_cases: 0
- gold_missing_cases: 20
- clean_cases: 20

## Notes
- Day 3 prioritizes the main candidate row under the frozen Setting B protocol.
- Day 4 will run the same evaluation on soft_best for trade-off comparison.
