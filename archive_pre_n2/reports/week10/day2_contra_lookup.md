# Week 10 - Day 2 Contra Lookup

## Inputs
- ontology candidates: `dataset/setting_a/18_ontology_only/valid_top20_ontology_only.json`
- contra_by_disease: `dataset/setting_b/00_safety_labels/contra_by_disease.json`
- contra_by_drug: `dataset/setting_b/00_safety_labels/contra_by_drug.json`
- valid annotations: `dataset/setting_b/02_eval_ready/valid_b_annotations.json`

## Lookup summary
- num_queries: 500
- total_candidates: 3918
- total_contra_candidates: 73
- query_has_contra_candidate_count: 38
- query_has_contra_candidate_rate: 0.076000
- lookup_symmetry_mismatches: 0

## Valid annotation summary
- num_annotation_rows: 500
- num_annotation_candidate_pairs: 10000
- num_annotation_contra_pairs: 129

## Top diseases by contra count
- ocular hypertension: 18
- nephrocalcinosis: 12
- gastroesophageal reflux disease: 8
- hypertension: 5
- hypertensive disorder: 4
- peptic esophagitis: 4
- anxiety disorder: 3
- diabetes mellitus (disease): 3
- pulmonary emphysema: 2
- epilepsy: 2

## Sample flagged rows
### Sample 0
- query_entity: leukemia, lymphocytic, susceptibility to
- num_contra_candidates: 0
- contra_candidates: []

### Sample 1
- query_entity: streptococcal infection
- num_contra_candidates: 0
- contra_candidates: []

### Sample 2
- query_entity: dyspepsia
- num_contra_candidates: 0
- contra_candidates: []

## Notes
- Day 2 only builds traceable contra lookup and candidate flags.
- Day 3 will use these flags to build hard_strict and hard_main.
- Day 4 will use the same flags to build soft-penalty variants.
