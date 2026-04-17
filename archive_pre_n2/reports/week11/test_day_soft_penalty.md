# Week 10 - Day 4 Soft Penalty

## Sweep summary
### lambda = 2.0
- num_queries: 500
- contra_candidates_final: 68
- QueryHasContraCandidateRate: 0.074000
- gold_in_topk_rate: 0.280000
- top1_changed_queries: 1
- top5_changed_queries: 10
- soft_demoted_contra_candidates: 42

## Current soft_best
- lambda_contra: 2.0
- gold_in_topk_rate: 0.280000
- soft_demoted_contra_candidates: 42

## Sample changed rows
### Sample 0
- query_entity: peptic esophagitis
- gold_entity: Esomeprazole
- top1_changed: 0
- top5_changed: 1
- contra_candidates: ['Cortisone acetate', 'Hydrocortisone', 'Hydrocortisone acetate', 'Scopolamine']
- reordered_candidates: ['Fusidic acid', 'Methylprednisolone', 'Dexamethasone', 'Prednisolone', 'Triamcinolone', 'Betamethasone', 'Oxytetracycline', 'Ofloxacin', 'Benzylpenicillin', 'Prednisone']

### Sample 1
- query_entity: esophagitis (disease)
- gold_entity: Pantoprazole
- top1_changed: 0
- top5_changed: 1
- contra_candidates: ['Cortisone acetate', 'Hydrocortisone', 'Hydrocortisone acetate', 'Scopolamine']
- reordered_candidates: ['Fusidic acid', 'Methylprednisolone', 'Dexamethasone', 'Prednisolone', 'Triamcinolone', 'Betamethasone', 'Oxytetracycline', 'Ofloxacin', 'Benzylpenicillin', 'Prednisone']

### Sample 2
- query_entity: gastroesophageal reflux disease
- gold_entity: Potassium bicarbonate
- top1_changed: 0
- top5_changed: 1
- contra_candidates: ['Cortisone acetate', 'Hydrocortisone', 'Hydrocortisone acetate', 'Scopolamine']
- reordered_candidates: ['Fusidic acid', 'Methylprednisolone', 'Dexamethasone', 'Prednisolone', 'Triamcinolone', 'Betamethasone', 'Oxytetracycline', 'Ofloxacin', 'Prednisone', 'Benzylpenicillin']

### Sample 3
- query_entity: glaucoma
- gold_entity: Bupranolol
- top1_changed: 0
- top5_changed: 1
- contra_candidates: ['Triamcinolone', 'Hydrocortisone', 'Cortisone acetate', 'Dexamethasone', 'Hydrocortisone acetate']
- reordered_candidates: ['Betamethasone', 'Methylprednisolone', 'Prednisolone', 'Prednisone', 'Doxorubicin', 'Propranolol', 'Carmustine', 'Vincristine', 'Bleomycin', 'Thiotepa']

### Sample 4
- query_entity: gastroesophageal reflux disease
- gold_entity: Sodium citrate
- top1_changed: 0
- top5_changed: 1
- contra_candidates: ['Cortisone acetate', 'Hydrocortisone', 'Hydrocortisone acetate', 'Scopolamine']
- reordered_candidates: ['Fusidic acid', 'Methylprednisolone', 'Dexamethasone', 'Prednisolone', 'Triamcinolone', 'Betamethasone', 'Oxytetracycline', 'Ofloxacin', 'Prednisone', 'Benzylpenicillin']

## Notes
- Day 4 keeps candidate set size fixed and only demotes contraindicated candidates.
- No strict-empty behavior should be introduced by soft penalty.
- Day 5 will run valid-side sanity evaluation with the backbone checkpoint.
