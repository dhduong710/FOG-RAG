# Week 12 Day 1 — Novelty 2 Protocol Freeze

## 1. Goal of week 12
Week 12 focuses on fixed-confidence fuzzy retrieval on top of the current hard-main branch.
This week does not modify candidate generation, ontology filtering, hard/soft safety logic,
or the LLM backbone.

## 2. Main reference rows
- Backbone reference row: week7-v2 backbone
- Main Novelty-1 row: +Ontology+Hard
- Optional supporting row: +Ontology+Soft (not the main comparison row this week)

## 3. Novelty-2 injection point
Novelty 2 in week 12 is applied only at the subgraph retrieval stage:
- confidence-aware path scoring
- confidence-aware path retention
- confidence-aware subgraph assembly

Candidate generation remains unchanged from Novelty 1.

## 4. Primary comparison rows for week 12
Minimum rows:
1. Backbone
2. +Ontology+Hard
3. +Ontology+Hard+FuzzyRetrieval

Optional supporting row if time permits:
4. +Ontology+Soft+FuzzyRetrieval

## 5. Decision split
- Primary decision split: valid
- Test split: not used for scientific decision in week 12

## 6. Out of scope
- learned confidence
- fuzzy graph encoder
- LLM changes
- candidate-stage redesign
- test-side final claims

## 7. Main metrics for week 12
### Ranking-side
- MRR
- Hits@1
- Hits@3
- Hits@10

### Retrieval/evidence-side
- average subgraph size
- average retained path count
- average path confidence
- average path relevance score
- proportion of low-confidence dropped paths
- ontology-valid retained path rate

## 8. Base artifacts
### Main development package
- dataset/setting_a/19_contra_aware_eval_ready/hard_main

### Official frozen comparison package
- dataset/setting_a/20_test_rerun_eval_ready/hard_main

## 9. Success condition for week 12
Week 12 is successful if:
- a fixed-confidence fuzzy retrieval branch runs cleanly on valid,
- ranking does not collapse,
- path/subgraph selection becomes more interpretable,
- a small tau/path-budget sensitivity can be completed.

## 10. Failure conditions
Week 12 is not successful if:
- the protocol changes mid-week,
- fuzzy logic accidentally changes candidate generation,
- valid/test are mixed,
- confidence design becomes too heuristic to explain,
- retrieval artifacts are not traceable.