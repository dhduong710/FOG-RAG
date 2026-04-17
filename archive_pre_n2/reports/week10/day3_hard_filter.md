# Week 10 - Day 3 Hard Filter

## Summary
- num_queries: 500
- strict_empty_after_hard: 13
- strict_empty_rate: 0.026000
- fallback_after_hard_main: 13
- fallback_rate_hard_main: 0.026000
- total_removed_candidates_strict: 73
- total_removed_candidates_main: 73
- gold_removed_by_hard_strict: 3
- gold_removed_by_hard_main: 3
- gold_in_topk_rate_hard_strict: 0.286000
- gold_in_topk_rate_hard_main: 0.312000
- missing_type_filtered_match: 0

## Policy
- hard_strict keeps only ontology-supported + non-contra candidates.
- hard_main also forbids contra candidates, but allows fallback to type-filtered non-contra candidates.
- hard_main fallback must never reintroduce contraindicated candidates.

## Sample strict vs main cases
### Case 0
- query_entity: hypertension
- gold_entity: Amiloride
- hard_strict_candidates: []
- hard_main_candidates: ['Fusidic acid', 'Methylprednisolone', 'Prednisolone', 'Oxytetracycline', 'Cortisone acetate', 'Triamcinolone', 'Hydrocortisone', 'Ofloxacin', 'Tobramycin', 'Benzylpenicillin']
- strict_empty_after_hard: 1
- fallback_after_hard: 1

### Case 1
- query_entity: hypertension
- gold_entity: Irbesartan
- hard_strict_candidates: []
- hard_main_candidates: ['Fusidic acid', 'Methylprednisolone', 'Prednisolone', 'Oxytetracycline', 'Cortisone acetate', 'Triamcinolone', 'Hydrocortisone', 'Ofloxacin', 'Tobramycin', 'Benzylpenicillin']
- strict_empty_after_hard: 1
- fallback_after_hard: 1

### Case 2
- query_entity: hypertensive disorder
- gold_entity: Paclitaxel
- hard_strict_candidates: []
- hard_main_candidates: ['Fusidic acid', 'Methylprednisolone', 'Oxytetracycline', 'Prednisolone', 'Ofloxacin', 'Cortisone acetate', 'Tobramycin', 'Methdilazine', 'Triamcinolone', 'Hydrocortisone']
- strict_empty_after_hard: 1
- fallback_after_hard: 1

### Case 3
- query_entity: hypertensive disorder
- gold_entity: Minoxidil
- hard_strict_candidates: []
- hard_main_candidates: ['Fusidic acid', 'Methylprednisolone', 'Oxytetracycline', 'Prednisolone', 'Ofloxacin', 'Cortisone acetate', 'Tobramycin', 'Methdilazine', 'Triamcinolone', 'Hydrocortisone']
- strict_empty_after_hard: 1
- fallback_after_hard: 1

### Case 4
- query_entity: hypertension
- gold_entity: Indapamide
- hard_strict_candidates: []
- hard_main_candidates: ['Fusidic acid', 'Methylprednisolone', 'Prednisolone', 'Oxytetracycline', 'Cortisone acetate', 'Triamcinolone', 'Hydrocortisone', 'Ofloxacin', 'Tobramycin', 'Benzylpenicillin']
- strict_empty_after_hard: 1
- fallback_after_hard: 1

## Notes
- Day 3 only builds hard variants and traces how strict the branch becomes.
- Day 4 will build soft-penalty variants for trade-off comparison.
