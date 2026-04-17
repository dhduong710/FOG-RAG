# Week 11 - Day 3 Setting B Valid (ontology_test)

## Ranking metrics
- mrr: 0.43548887
- hits1: 0.26
- hits3: 0.486
- hits10: 0.936

## Setting B metrics
- num_queries: 500
- K: 10
- SafetyViolation@10: 0.006
- Contra@10: 0.006
- ConstraintViolationRate@10: 0.0
- QueryHasConstraintViolationRate@10: 0.0
- GoldInTopKRate: 0.28

## Case summary
- safety_violation_cases: 3
- constraint_violation_cases: 0
- gold_missing_cases: 20
- clean_cases: 20

## Notes
- Day 3 prioritizes the main candidate row under the frozen Setting B protocol.
- Day 4 will run the same evaluation on soft_best for trade-off comparison.
