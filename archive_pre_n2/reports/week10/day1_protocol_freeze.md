# Week 10 - Day 1 Protocol Freeze

## 1. Goal
Attach contraindication-aware handling to the week9 ontology-supported candidate branch without changing the backbone or moving beyond candidate-stage intervention.

## 2. Main references
- Backbone reference: `week7-v2`
- Ontology reference: `week9_ontology_only`
- Week9 role: `groundwork_supporting_row`

## 3. Injection point
- Novelty injection point: `candidate_stage_only`
- Decision split: `valid`
- Test usage: `not_used_for_decision_week10`

## 4. Rows to compare this week
- `backbone`: Main backbone reference row (source=week7-v2)
- `ontology`: Ontology-supported reference row (source=week9_ontology_only)
- `ontology_hard`: Ontology-supported + contraindication-aware hard filtering (source=week10_hard_main)
- `ontology_soft`: Ontology-supported + contraindication-aware soft penalization (source=week10_soft_best)

## 5. Hard policy
- Variants: hard_strict, hard_main
- hard_strict: Keep only ontology-supported and non-contra candidates; if empty, remain empty.
- hard_main: Keep ontology-supported and non-contra candidates; if empty, fallback only to non-contra candidates from the type-filtered list.
- Fallback source: `type_filtered_non_contra_only`
- Reintroduce contraindicated candidates allowed? `False`

## 6. Soft policy
- Base row: `week9_ontology_only`
- Candidate set behavior: `keep_candidate_set`
- Contra behavior: `demote_contra_candidates_only`
- Lambda sweep: [0.25, 0.5, 1.0, 2.0]

## 7. Main metrics for week10
### Ranking
- MRR
- Hits@1
- Hits@3
- Hits@10

### Safety proxy
- contra_candidates_final
- QueryHasContraCandidateRate
- strict_empty_after_hard
- fallback_after_hard
- fallback_after_soft
- gold_in_topk
- avg_candidate_size
- hard_removed_candidates
- soft_demoted_contra_candidates

## 8. Not main metrics this week
- SafetyViolation@10
- Contra@10
- final_setting_b_test_numbers
- fuzzy_path_confidence_metrics

## 9. Week11 handoff rule
- Main row for week11 must be selected from: ['hard_main', 'soft_best']
- Selection priority: Prefer the row that is clearly cleaner than backbone/week9 while remaining usable for week11 Setting B evaluation.
