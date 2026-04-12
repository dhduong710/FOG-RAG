# Day 7 — Week 9 Closeout

## 1. Goal of Week 9
Lock ontology-aware retrieval groundwork before adding contraindication-aware hard/soft handling in week 10.

## 2. What was completed
- Protocol for Novelty 1 was frozen with week7-v2 kept as the fairness anchor.
- Candidate type filtering confirmed the candidate list was Drug-only.
- Schema validity checker for candidate/path/evidence became traceable after parser fixes.
- Ontology-only candidate artifact was built and evaluated on valid.
- Error review separated strict-empty behavior from fallback-driven behavior.

## 3. Backbone vs +ontology
- backbone MRR: 0.42424878
- backbone Hits@1: 0.36800000
- backbone Hits@3: 0.39399999
- backbone Hits@10: 0.50999999

- +ontology MRR: 0.31301793
- +ontology Hits@1: 0.24400000
- +ontology Hits@3: 0.27800000
- +ontology Hits@10: 0.43400000

### Delta (+ontology - backbone)
- ΔMRR: -0.11123085
- ΔHits@1: -0.12400000
- ΔHits@3: -0.11599999
- ΔHits@10: -0.07599999

## 4. Ontology-only branch summary
- removed_unsupported_candidates: 8082
- fallback_queries: 100
- gold_in_ontology_candidates: 146
- ConstraintViolationRate: 0.51046452
- QueryHasConstraintViolationRate: 0.2

## 5. Main error-review findings
- strict_empty_queries: 100
- gold_removed_queries: 354
- singleton_queries: 104
- direct_only_queries: 221
- mechanism_only_queries: 118
- mixed_support_queries: 61
- all_unsupported_queries: 100

## 6. Main interpretation
- Week 9 succeeded as ontology-aware retrieval groundwork, not as a final winning novelty row.
- The ontology-only branch is clean and traceable, but still too conservative.
- The main trade-off is between cleanliness and ranking usability.
- Strict ontology support is real, but fallback reintroduces unsupported candidates for 100 queries.
- Direct support currently dominates mechanism support, so the branch is not yet a strong mechanism-grounded main path.

## 7. Decision for end of week 9
- Decision: CONDITIONAL GO

## 8. Week 10 handoff
- Keep week7-v2 as the main backbone reference.
- Treat week9 ontology-only as a supporting / groundwork row, not the final main variant.
- Apply hard-filter and soft-penalty safety handling first on the ontology-supported subset.
- Do not use the fallback-heavy row as the main safety row without an explicit note.
- Use valid as the decision split again in week 10.

## 9. What not to overclaim
- Do not claim ontology-only already improves ranking over the backbone.
- Do not claim current ontology-only row is the final novelty winner.
- Do not hide that 100 queries required fallback and 354 queries lost the gold candidate.
- Do not present the fallback-heavy row as a purely clean ontology-constrained row.
