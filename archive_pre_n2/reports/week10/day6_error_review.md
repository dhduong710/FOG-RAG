# Week 10 - Day 6 Error Review

## Ranking metrics
### hard_main
- MRR: 0.39310116
- Hits@1: 0.33
- Hits@3: 0.358
- Hits@10: 0.524

### soft_best
- MRR: 0.39310116
- Hits@1: 0.33
- Hits@3: 0.358
- Hits@10: 0.524

## Safety proxy metrics
### hard_main
- num_queries: 500
- contra_candidates_final: 0
- QueryHasContraCandidateRate: 0.0
- strict_empty_after_hard: 0
- fallback_after_hard: 13
- fallback_after_soft: 0
- gold_in_topk: 156
- gold_in_topk_rate: 0.312
- avg_candidate_size: 8.184
- hard_removed_candidates: 73
- soft_demoted_contra_candidates: 0

### soft_best
- num_queries: 500
- contra_candidates_final: 73
- QueryHasContraCandidateRate: 0.076
- strict_empty_after_hard: 0
- fallback_after_hard: 0
- fallback_after_soft: 0
- gold_in_topk: 146
- gold_in_topk_rate: 0.292
- avg_candidate_size: 7.836
- hard_removed_candidates: 0
- soft_demoted_contra_candidates: 52

## Case summary
- hard_fallback_case: 13
- gold_lost_by_hard: 3
- gold_saved_by_hard_vs_soft: 13
- soft_keeps_contra: 38
- hard_cleaner_same_or_better: 35
- needs_manual_review: 0

## Decision
- main_row: hard_main
- supporting_row: soft_best
- reason: Ranking metrics are identical, while hard_main fully removes contraindicated final candidates.

## Sample manual-review cases
## Notes
- If ranking metrics stay identical, safety dominates the week10 decision.
- hard_main should become the week11 main row unless fallback cases look biologically implausible.
- soft_best remains useful as a supporting ablation row showing the trade-off.
