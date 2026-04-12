# Day 5 — Valid Sanity Evaluation

## 1. Goal
Run valid-side sanity evaluation for the ontology-only branch using the frozen backbone reference checkpoint.

## 2. Ranking metrics (`backbone + ontology`)
- mrr: 0.31301793
- hits1: 0.244
- hits3: 0.278
- hits10: 0.434

## 3. Comparison vs backbone reference
- baseline metrics file not found; comparison skipped

## 4. Constraint metrics
- ConstraintViolationRate: 0.51046452
- QueryHasConstraintViolationRate: 0.2
- remaining_non_drug_candidates: 0
- unsupported_final_candidates: 2000
- fallback_queries: 100
- gold_in_topk_ontology: 146
- invalid_evidence_triples_day3: 10858
- unsupported_path_sequences_day3: 28306

## 5. Candidate summary
- total_queries: 500
- total_final_candidates: 3918
- direct_final_candidates: 1642
- mechanism_final_candidates: 276
- unsupported_final_candidates: 2000
- fallback_queries: 100
- gold_in_topk_ontology: 146
- removed_unsupported_candidates_day4: 8082
- queries_with_any_direct_support_day4: 282
- queries_with_any_mechanism_support_day4: 179

## 6. Interpretation
- This is a sanity evaluation, not a final paper result.
- If ranking drops but constraint cleanliness improves clearly, the row can still be useful as ontology-only groundwork.
- High fallback and low gold coverage indicate the ontology-only branch is still conservative.

## 7. Day-5 decision
- Decision: CONDITIONAL GO (baseline comparison unavailable)
