# Week 10 Closeout

## 1. Goal of week 10
Week 10 attached contraindication-aware handling to the ontology-supported branch from week 9, without changing the backbone. Two branches were evaluated: hard_main and soft_best.

## 2. Main results
- hard_main ranking: {'mrr': 0.39310116, 'hits1': 0.33, 'hits3': 0.358, 'hits10': 0.524}
- soft_best ranking: {'mrr': 0.39310116, 'hits1': 0.33, 'hits3': 0.358, 'hits10': 0.524}
- hard_main safety proxy: {'num_queries': 500, 'contra_candidates_final': 0, 'QueryHasContraCandidateRate': 0.0, 'strict_empty_after_hard': 0, 'fallback_after_hard': 13, 'fallback_after_soft': 0, 'gold_in_topk': 156, 'gold_in_topk_rate': 0.312, 'avg_candidate_size': 8.184, 'hard_removed_candidates': 73, 'soft_demoted_contra_candidates': 0}
- soft_best safety proxy: {'num_queries': 500, 'contra_candidates_final': 73, 'QueryHasContraCandidateRate': 0.076, 'strict_empty_after_hard': 0, 'fallback_after_hard': 0, 'fallback_after_soft': 0, 'gold_in_topk': 146, 'gold_in_topk_rate': 0.292, 'avg_candidate_size': 7.836, 'hard_removed_candidates': 0, 'soft_demoted_contra_candidates': 52}

## 3. Error review summary
- hard_fallback_case: 13
- gold_lost_by_hard: 3
- gold_saved_by_hard_vs_soft: 13
- soft_keeps_contra: 38
- hard_cleaner_same_or_better: 35
- needs_manual_review: 0

## 4. Decision
- main_row: hard_main
- supporting_row: soft_best
- reason: Ranking metrics are identical, while hard_main fully removes contraindicated final candidates.

## 5. Interpretation
- hard_main is selected as the main week11 candidate because it fully removes contraindicated final candidates while keeping the same ranking metrics as soft_best.
- soft_best remains useful as a supporting ablation because it demonstrates a softer trade-off without empty rows, but it still keeps contraindicated final candidates.
- hard_main still uses fallback in a small number of queries, so week11 should include targeted case review to make sure fallback outputs remain interpretable.

## 6. Handoff to week 11
- Main row for week 11: hard_main
- Supporting ablation row: soft_best
- Main metrics for week 11:
  - MRR / Hits@1 / Hits@3 / Hits@10
  - SafetyViolation@10
  - Contra@10
  - ConstraintViolationRate
  - QueryHasConstraintViolationRate
- Split priority: valid first, test only after the valid protocol is stable.

## 7. Final status
CONDITIONAL GO to week 11.
