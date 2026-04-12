# Day 1 — Protocol Freeze for Novelty 1

## 1. Goal of Day 1
Freeze the protocol for Novelty 1 before any ontology-only candidate artifact is built.

## 2. Main decisions
1. Main task remains head prediction: (?, indication, disease).
2. Setting A remains the fairness anchor.
3. Backbone reference remains week7-v2.
4. Week8 posthoc debias stays as supporting analysis only.
5. Novelty 1 this week is ontology-only.
6. Novelty 1 is injected at the candidate stage only.
7. Comparison rows for week 9:
   - backbone
   - backbone + ontology
8. Decision split for this week is valid.
9. Test is not used for scientific decision this week.
10. Hard filter and soft penalty are postponed to week 10.

## 3. What "+ontology" means this week
- candidates must be Drug
- candidate/path/evidence must pass basic schema validity checks

## 4. Non-goals
- no fuzzy confidence
- no fuzzy retrieval
- no backbone change
- no hard filter
- no soft penalty
- no test-based decision
- no new structure baselines

## 5. Day-1 done definition
Day 1 is complete only if:
- protocol JSON is created
- backbone reference is fixed
- variant rows are fixed
- valid is fixed as the decision split
- non-goals are explicitly written