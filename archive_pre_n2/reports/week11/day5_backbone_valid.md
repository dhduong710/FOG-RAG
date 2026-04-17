# Week 11 - Day 3 Setting B Valid (backbone)

## Ranking metrics
- mrr: 0.42424878
- hits1: 0.368
- hits3: 0.39399999
- hits10: 0.50999999
- num_examples: 500
- split: valid

## Setting B metrics
- num_queries: 500
- K: 10
- SafetyViolation@10: 0.0
- Contra@10: 0.0
- ConstraintViolationRate@10: 0.0
- QueryHasConstraintViolationRate@10: 0.0
- GoldInTopKRate: 1.0

## Case summary
- safety_violation_cases: 0
- constraint_violation_cases: 0
- gold_missing_cases: 0
- clean_cases: 20

## Notes
- Day 3 prioritizes the main candidate row under the frozen Setting B protocol.
- Day 4 will run the same evaluation on soft_best for trade-off comparison.
