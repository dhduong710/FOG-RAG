# Day 2 — Type Filtering

## 1. Goal
Filter candidates so that every remaining candidate is of type `Drug`.

## 2. Inputs
- input_candidates: `dataset/setting_a/11_ranker_v2/valid_top20_drkgc_ready.json`
- type_map_tsv: `dataset/setting_b/01_annotations/type_map.tsv`
- fallback_type_json: `dataset/setting_b/01_ontology/entity_name_to_type.json`

## 3. Outputs
- filtered_candidates: `dataset/setting_a/18_ontology_only/valid_top20_type_filtered.json`
- filter_report_json: `dataset/setting_a/18_ontology_only/ontology_filter_report.json`

## 4. Summary
- total_queries: 500
- total_candidates_before: 10000
- total_candidates_after: 10000
- total_removed: 0
- empty_queries_after_filter: 0
- remaining_non_drug_candidates: 0
- top1_changed_queries: 0
- top5_changed_queries: 0

## 5. Removal breakdown by type

## 6. Type lookup source breakdown
- type_map.tsv: 10000

## 7. Empty-query examples
- none

## 8. Before/after samples
### Query: leukemia, lymphocytic, susceptibility to
- before_top5: ['Betamethasone', 'Hydrocortisone', 'Methylprednisolone', 'Triamcinolone', 'Cortisone acetate']
- after_top5: ['Betamethasone', 'Hydrocortisone', 'Methylprednisolone', 'Triamcinolone', 'Cortisone acetate']
- removed_types: {}

### Query: streptococcal infection
- before_top5: ['Fusidic acid', 'Oxytetracycline', 'Dexamethasone', 'Methylprednisolone', 'Prednisolone']
- after_top5: ['Fusidic acid', 'Oxytetracycline', 'Dexamethasone', 'Methylprednisolone', 'Prednisolone']
- removed_types: {}

### Query: dyspepsia
- before_top5: ['Fusidic acid', 'Oxytetracycline', 'Dexamethasone', 'Methylprednisolone', 'Methdilazine']
- after_top5: ['Fusidic acid', 'Oxytetracycline', 'Dexamethasone', 'Methylprednisolone', 'Methdilazine']
- removed_types: {}

### Query: basal cell carcinoma
- before_top5: ['Betamethasone', 'Hydrocortisone', 'Triamcinolone', 'Methylprednisolone', 'Cortisone acetate']
- after_top5: ['Betamethasone', 'Hydrocortisone', 'Triamcinolone', 'Methylprednisolone', 'Cortisone acetate']
- removed_types: {}

### Query: obsessive-compulsive disorder
- before_top5: ['Betamethasone', 'Methylprednisolone', 'Hydrocortisone', 'Cortisone acetate', 'Triamcinolone']
- after_top5: ['Betamethasone', 'Methylprednisolone', 'Hydrocortisone', 'Cortisone acetate', 'Triamcinolone']
- removed_types: {}

### Query: Norwegian scabies
- before_top5: ['Fusidic acid', 'Oxytetracycline', 'Tetracycline', 'Tobramycin', 'Dexamethasone']
- after_top5: ['Fusidic acid', 'Oxytetracycline', 'Tetracycline', 'Tobramycin', 'Dexamethasone']
- removed_types: {}

### Query: hypertension
- before_top5: ['Fusidic acid', 'Dexamethasone', 'Methylprednisolone', 'Prednisolone', 'Oxytetracycline']
- after_top5: ['Fusidic acid', 'Dexamethasone', 'Methylprednisolone', 'Prednisolone', 'Oxytetracycline']
- removed_types: {}

### Query: pneumococcal meningitis
- before_top5: ['Fusidic acid', 'Dexamethasone', 'Methylprednisolone', 'Prednisolone', 'Oxytetracycline']
- after_top5: ['Fusidic acid', 'Dexamethasone', 'Methylprednisolone', 'Prednisolone', 'Oxytetracycline']
- removed_types: {}

### Query: obsessive-compulsive disorder
- before_top5: ['Betamethasone', 'Methylprednisolone', 'Hydrocortisone', 'Cortisone acetate', 'Triamcinolone']
- after_top5: ['Betamethasone', 'Methylprednisolone', 'Hydrocortisone', 'Cortisone acetate', 'Triamcinolone']
- removed_types: {}

### Query: arthropathy
- before_top5: ['Betamethasone', 'Methylprednisolone', 'Hydrocortisone', 'Cortisone acetate', 'Triamcinolone']
- after_top5: ['Betamethasone', 'Methylprednisolone', 'Hydrocortisone', 'Cortisone acetate', 'Triamcinolone']
- removed_types: {}
