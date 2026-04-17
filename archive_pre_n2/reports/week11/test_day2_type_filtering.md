# Day 2 — Type Filtering

## 1. Goal
Filter candidates so that every remaining candidate is of type `Drug`.

## 2. Inputs
- input_candidates: `dataset/setting_a/11_ranker_v2/test_top20_drkgc_ready.json`
- type_map_tsv: `dataset/setting_b/01_annotations/type_map.tsv`
- fallback_type_json: `dataset/setting_b/01_ontology/entity_name_to_type.json`

## 3. Outputs
- filtered_candidates: `dataset/setting_a/18_ontology_only/test_top20_type_filtered.json`
- filter_report_json: `dataset/setting_a/18_ontology_only/test_type_filter_report.json`

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
### Query: lung abscess (disease)
- before_top5: ['Fusidic acid', 'Methylprednisolone', 'Dexamethasone', 'Oxytetracycline', 'Prednisolone']
- after_top5: ['Fusidic acid', 'Methylprednisolone', 'Dexamethasone', 'Oxytetracycline', 'Prednisolone']
- removed_types: {}

### Query: acquired hyperprolactinemia
- before_top5: ['Betamethasone', 'Hydrocortisone', 'Methylprednisolone', 'Cortisone acetate', 'Triamcinolone']
- after_top5: ['Betamethasone', 'Hydrocortisone', 'Methylprednisolone', 'Cortisone acetate', 'Triamcinolone']
- removed_types: {}

### Query: allergic rhinitis
- before_top5: ['Fusidic acid', 'Dexamethasone', 'Methylprednisolone', 'Oxytetracycline', 'Prednisolone']
- after_top5: ['Fusidic acid', 'Dexamethasone', 'Methylprednisolone', 'Oxytetracycline', 'Prednisolone']
- removed_types: {}

### Query: blepharoconjunctivitis
- before_top5: ['Fusidic acid', 'Methylprednisolone', 'Dexamethasone', 'Prednisolone', 'Cortisone acetate']
- after_top5: ['Fusidic acid', 'Methylprednisolone', 'Dexamethasone', 'Prednisolone', 'Cortisone acetate']
- removed_types: {}

### Query: parkinsonian-pyramidal syndrome
- before_top5: ['Betamethasone', 'Hydrocortisone', 'Cortisone acetate', 'Triamcinolone', 'Methylprednisolone']
- after_top5: ['Betamethasone', 'Hydrocortisone', 'Cortisone acetate', 'Triamcinolone', 'Methylprednisolone']
- removed_types: {}

### Query: pharyngitis
- before_top5: ['Fusidic acid', 'Oxytetracycline', 'Dexamethasone', 'Methylprednisolone', 'Methdilazine']
- after_top5: ['Fusidic acid', 'Oxytetracycline', 'Dexamethasone', 'Methylprednisolone', 'Methdilazine']
- removed_types: {}

### Query: diabetes mellitus (disease)
- before_top5: ['Betamethasone', 'Methylprednisolone', 'Triamcinolone', 'Hydrocortisone', 'Cortisone acetate']
- after_top5: ['Betamethasone', 'Methylprednisolone', 'Triamcinolone', 'Hydrocortisone', 'Cortisone acetate']
- removed_types: {}

### Query: Trichinella spiralis infectious disease
- before_top5: ['Fusidic acid', 'Methylprednisolone', 'Dexamethasone', 'Cortisone acetate', 'Prednisolone']
- after_top5: ['Fusidic acid', 'Methylprednisolone', 'Dexamethasone', 'Cortisone acetate', 'Prednisolone']
- removed_types: {}

### Query: type 2 diabetes mellitus
- before_top5: ['Betamethasone', 'Methylprednisolone', 'Triamcinolone', 'Hydrocortisone', 'Cortisone acetate']
- after_top5: ['Betamethasone', 'Methylprednisolone', 'Triamcinolone', 'Hydrocortisone', 'Cortisone acetate']
- removed_types: {}

### Query: spondyloarthropathy
- before_top5: ['Betamethasone', 'Methylprednisolone', 'Triamcinolone', 'Hydrocortisone', 'Cortisone acetate']
- after_top5: ['Betamethasone', 'Methylprednisolone', 'Triamcinolone', 'Hydrocortisone', 'Cortisone acetate']
- removed_types: {}
