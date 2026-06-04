# Week 12B Day 1 — No-Injection Protocol Freeze

## 1. Goal
Week 12B is a no-injection rerun of Novelty 1 before entering Novelty 2.
The goal is to evaluate Novelty 1 more transparently on raw R-GCN candidate retrieval without using gold injection as the main scientific truth.

## 2. Main truth vs supporting truth
- Main scientific check: no-injection results
- Supporting / diagnostic results: injected reranker-ready results from earlier weeks

Injected results are not deleted, but they are no longer treated as the main truth.

## 3. Frozen raw source of truth
Chosen raw source:
- dataset/setting_a/21_ranker_rescue

Reason:
- it is the best frozen raw retriever output currently available,
- even though the improvement over the previous retriever is small,
- and it does not imply a full project-wide base reset.

## 4. Frozen rows for Week 12B
The week must evaluate four no-injection rows:
1. backbone_raw
2. ontology_raw
3. hard_main_raw
4. soft_best_raw

## 5. Frozen split policy
- Primary decision split: valid
- Test is only run after valid no-injection evaluation is clean

## 6. Frozen evaluator semantics for later eval-ready build
For no-injection eval-ready packages:
- if the gold entity is inside the candidate list:
  rank = gold_position + 1
- if the gold entity is not inside the candidate list:
  rank = len(candidate_list) + 1

No hidden fallback or gold injection is allowed in the main no-injection branch.

## 7. Out of scope
- Novelty 2
- fuzzy retrieval
- fuzzy graph encoder
- retriever finetuning
- hard/soft redesign
- ontology redesign

## 8. Success condition of Week 12B
Week 12B is successful if:
- the no-injection protocol is frozen,
- raw source is frozen,
- candidate-stage no-injection rows are built cleanly,
- valid no-injection evaluation runs cleanly,
- injected vs no-injection roles are clearly separated in the project story.

## 9. Failure condition
Week 12B fails if:
- raw and injected branches are mixed,
- the raw source changes mid-week,
- hidden gold injection is reintroduced,
- valid and test are mixed during decision making.