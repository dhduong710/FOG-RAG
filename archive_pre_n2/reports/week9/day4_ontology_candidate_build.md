# Day 4 — Ontology Candidate Build

## 1. Goal
Build the ontology-only candidate artifact using direct valid task edges and valid mechanism paths.

## 2. Inputs
- input_candidates: `dataset/setting_a/18_ontology_only/valid_top20_type_filtered.json`
- input_evidence: `dataset/setting_a/12_backbone_ready_ranker_v2/valid.json`
- type_map_tsv: `dataset/setting_b/01_annotations/type_map.tsv`
- schema_rules_json: `dataset/setting_b/01_annotations/schema_rules.json`
- path_templates_yaml: `dataset/setting_b/01_annotations/path_templates.yaml`

## 3. Output
- ontology_candidate_artifact: `dataset/setting_a/18_ontology_only/valid_top20_ontology_only.json`
- ontology_filter_report: `dataset/setting_a/18_ontology_only/ontology_filter_report.json`

## 4. Summary
- total_queries: 500
- total_candidates_before: 10000
- total_candidates_after: 3918
- removed_unsupported_candidates: 8082
- candidates_kept_by_direct_support: 1642
- candidates_kept_by_mechanism_support: 276
- queries_with_any_direct_support: 282
- queries_with_any_mechanism_support: 179
- fallback_queries: 100
- empty_queries_before_fallback: 100
- gold_in_ontology_candidates: 146
- top1_changed_queries: 271
- top5_changed_queries: 369

## 5. Sample before/after
### Query: leukemia, lymphocytic, susceptibility to
- before_top5: ['Betamethasone', 'Hydrocortisone', 'Methylprednisolone', 'Triamcinolone', 'Cortisone acetate']
- after_top5: ['Betamethasone', 'Hydrocortisone', 'Methylprednisolone', 'Triamcinolone', 'Prednisolone']
- support_labels_top5_after: ['direct', 'direct', 'direct', 'direct', 'direct']
- fallback_used: False

### Query: streptococcal infection
- before_top5: ['Fusidic acid', 'Oxytetracycline', 'Dexamethasone', 'Methylprednisolone', 'Prednisolone']
- after_top5: ['Fusidic acid', 'Ofloxacin', 'Benzylpenicillin', 'Ciprofloxacin']
- support_labels_top5_after: ['direct', 'direct', 'direct', 'direct']
- fallback_used: False

### Query: dyspepsia
- before_top5: ['Fusidic acid', 'Oxytetracycline', 'Dexamethasone', 'Methylprednisolone', 'Methdilazine']
- after_top5: ['Fusidic acid', 'Oxytetracycline', 'Dexamethasone', 'Methylprednisolone', 'Methdilazine']
- support_labels_top5_after: ['unsupported', 'unsupported', 'unsupported', 'unsupported', 'unsupported']
- fallback_used: True

### Query: basal cell carcinoma
- before_top5: ['Betamethasone', 'Hydrocortisone', 'Triamcinolone', 'Methylprednisolone', 'Cortisone acetate']
- after_top5: ['Vismodegib']
- support_labels_top5_after: ['mechanism']
- fallback_used: False

### Query: obsessive-compulsive disorder
- before_top5: ['Betamethasone', 'Methylprednisolone', 'Hydrocortisone', 'Cortisone acetate', 'Triamcinolone']
- after_top5: ['Propranolol']
- support_labels_top5_after: ['mechanism']
- fallback_used: False

### Query: Norwegian scabies
- before_top5: ['Fusidic acid', 'Oxytetracycline', 'Tetracycline', 'Tobramycin', 'Dexamethasone']
- after_top5: ['Fusidic acid', 'Oxytetracycline', 'Tetracycline', 'Tobramycin', 'Dexamethasone']
- support_labels_top5_after: ['unsupported', 'unsupported', 'unsupported', 'unsupported', 'unsupported']
- fallback_used: True

### Query: hypertension
- before_top5: ['Fusidic acid', 'Dexamethasone', 'Methylprednisolone', 'Prednisolone', 'Oxytetracycline']
- after_top5: ['Dexamethasone']
- support_labels_top5_after: ['mechanism']
- fallback_used: False

### Query: pneumococcal meningitis
- before_top5: ['Fusidic acid', 'Dexamethasone', 'Methylprednisolone', 'Prednisolone', 'Oxytetracycline']
- after_top5: ['Benzylpenicillin']
- support_labels_top5_after: ['direct']
- fallback_used: False

### Query: obsessive-compulsive disorder
- before_top5: ['Betamethasone', 'Methylprednisolone', 'Hydrocortisone', 'Cortisone acetate', 'Triamcinolone']
- after_top5: ['Propranolol', 'Paroxetine']
- support_labels_top5_after: ['mechanism', 'mechanism']
- fallback_used: False

### Query: arthropathy
- before_top5: ['Betamethasone', 'Methylprednisolone', 'Hydrocortisone', 'Cortisone acetate', 'Triamcinolone']
- after_top5: ['Fusidic acid']
- support_labels_top5_after: ['direct']
- fallback_used: False
