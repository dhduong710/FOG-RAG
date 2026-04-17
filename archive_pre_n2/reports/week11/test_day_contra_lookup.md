# Week 10 - Day 2 Contra Lookup

## Inputs
- ontology candidates: `dataset/setting_a/18_ontology_only/test_top20_ontology_only.json`
- contra_by_disease: `dataset/setting_b/00_safety_labels/contra_by_disease.json`
- contra_by_drug: `dataset/setting_b/00_safety_labels/contra_by_drug.json`
- valid annotations: `dataset/setting_b/02_eval_ready/test_b_annotations.json`

## Lookup summary
- num_queries: 500
- total_candidates: 3865
- total_contra_candidates: 68
- query_has_contra_candidate_count: 37
- query_has_contra_candidate_rate: 0.074000
- lookup_symmetry_mismatches: 0

## Valid annotation summary
- num_annotation_rows: 500
- num_annotation_candidate_pairs: 10000
- num_annotation_contra_pairs: 139

## Top diseases by contra count
- gastroesophageal reflux disease: 12
- esophagitis (disease): 8
- hypercalcemia disease: 8
- hypertensive disorder: 7
- hypertension: 6
- glaucoma: 5
- diabetes mellitus (disease): 4
- peptic esophagitis: 4
- phosphorus metabolism disease: 4
- anxiety disorder: 2

## Sample flagged rows
### Sample 0
- query_entity: lung abscess (disease)
- num_contra_candidates: 0
- contra_candidates: []

### Sample 1
- query_entity: acquired hyperprolactinemia
- num_contra_candidates: 0
- contra_candidates: []

### Sample 2
- query_entity: allergic rhinitis
- num_contra_candidates: 0
- contra_candidates: []

## Notes
- Day 2 only builds traceable contra lookup and candidate flags.
- Day 3 will use these flags to build hard_strict and hard_main.
- Day 4 will use the same flags to build soft-penalty variants.
