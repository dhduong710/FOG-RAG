# Day 6 Eval Smoke Report

## 1. Files created
- scripts/eval_safety_metrics.py
- scripts/eval_constraint_metrics.py

## 2. Mock safety test
- input: mock_safety_eval.json
- expected logic:
  - SafetyViolation@1 = 0.0
  - SafetyViolation@3 = 0.5
  - Contra@1 = 0.0
  - Contra@3 = 0.5
- status: passed

## 3. Mock constraint test
- input: mock_constraint_eval.json
- expected logic:
  - one valid prediction
  - one invalid prediction
  - ConstraintViolationRate@2 = 0.5
- status: passed

## 4. Real Setting B files
- valid_b_annotations.json: evaluator runs without error
- test_b_annotations.json: evaluator runs without error

## 5. Conclusion
Setting B metrics are now implemented as runnable evaluator skeletons.
This reduces ambiguity before Month 2 reproduction and before Month 3 safety-aware experiments.