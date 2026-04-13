# Week 10 - Day 4 Soft Penalty

## Sweep summary
### lambda = 0.25
- num_queries: 500
- contra_candidates_final: 73
- QueryHasContraCandidateRate: 0.076000
- gold_in_topk_rate: 0.292000
- top1_changed_queries: 4
- top5_changed_queries: 12
- soft_demoted_contra_candidates: 49

### lambda = 0.5
- num_queries: 500
- contra_candidates_final: 73
- QueryHasContraCandidateRate: 0.076000
- gold_in_topk_rate: 0.292000
- top1_changed_queries: 4
- top5_changed_queries: 12
- soft_demoted_contra_candidates: 49

### lambda = 1.0
- num_queries: 500
- contra_candidates_final: 73
- QueryHasContraCandidateRate: 0.076000
- gold_in_topk_rate: 0.292000
- top1_changed_queries: 4
- top5_changed_queries: 13
- soft_demoted_contra_candidates: 50

### lambda = 2.0
- num_queries: 500
- contra_candidates_final: 73
- QueryHasContraCandidateRate: 0.076000
- gold_in_topk_rate: 0.292000
- top1_changed_queries: 6
- top5_changed_queries: 13
- soft_demoted_contra_candidates: 52

## Current soft_best
- lambda_contra: 2.0
- gold_in_topk_rate: 0.292000
- soft_demoted_contra_candidates: 52

## Sample changed rows
### Sample 0
- query_entity: gastroesophageal reflux disease
- gold_entity: Magnesium carbonate
- top1_changed: 0
- top5_changed: 1
- contra_candidates: ['Cortisone acetate', 'Hydrocortisone', 'Hydrocortisone acetate', 'Scopolamine']
- reordered_candidates: ['Fusidic acid', 'Methylprednisolone', 'Dexamethasone', 'Prednisolone', 'Triamcinolone', 'Betamethasone', 'Oxytetracycline', 'Ofloxacin', 'Prednisone', 'Benzylpenicillin']

### Sample 1
- query_entity: psoriasis
- gold_entity: Cortisone acetate
- top1_changed: 1
- top5_changed: 1
- contra_candidates: ['Betamethasone']
- reordered_candidates: ['Hydrocortisone', 'Methylprednisolone', 'Triamcinolone', 'Prednisolone', 'Dexamethasone', 'Prednisone', 'Hydrocortisone acetate', 'Methotrexate', 'Betamethasone']

### Sample 2
- query_entity: gastroesophageal reflux disease
- gold_entity: Pantoprazole
- top1_changed: 0
- top5_changed: 1
- contra_candidates: ['Cortisone acetate', 'Hydrocortisone', 'Hydrocortisone acetate', 'Scopolamine']
- reordered_candidates: ['Fusidic acid', 'Methylprednisolone', 'Dexamethasone', 'Prednisolone', 'Triamcinolone', 'Betamethasone', 'Oxytetracycline', 'Ofloxacin', 'Prednisone', 'Benzylpenicillin']

### Sample 3
- query_entity: epilepsy
- gold_entity: Phenytoin
- top1_changed: 1
- top5_changed: 0
- contra_candidates: ['Dexamethasone']
- reordered_candidates: ['Propranolol', 'Dexamethasone']

### Sample 4
- query_entity: Cushing syndrome
- gold_entity: Pasireotide
- top1_changed: 0
- top5_changed: 1
- contra_candidates: ['Cortisone acetate']
- reordered_candidates: ['Betamethasone', 'Triamcinolone', 'Hydrocortisone', 'Methylprednisolone', 'Prednisolone', 'Dexamethasone', 'Prednisone', 'Hydrocortisone acetate', 'Doxorubicin', 'Propranolol']

## Notes
- Day 4 keeps candidate set size fixed and only demotes contraindicated candidates.
- No strict-empty behavior should be introduced by soft penalty.
- Day 5 will run valid-side sanity evaluation with the backbone checkpoint.
