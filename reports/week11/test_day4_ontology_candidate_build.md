# Day 4 — Ontology Candidate Build

## 1. Goal
Build the ontology-only candidate artifact using direct valid task edges and valid mechanism paths.

## 2. Inputs
- input_candidates: `dataset/setting_a/18_ontology_only/test_top20_type_filtered.json`
- input_evidence: `dataset/setting_a/12_backbone_ready_ranker_v2/test.json`
- type_map_tsv: `dataset/setting_b/01_annotations/type_map.tsv`
- schema_rules_json: `dataset/setting_b/01_annotations/schema_rules.json`
- path_templates_yaml: `dataset/setting_b/01_annotations/path_templates.yaml`

## 3. Output
- ontology_candidate_artifact: `dataset/setting_a/18_ontology_only/test_top20_ontology_only.json`
- ontology_filter_report: `dataset/setting_a/18_ontology_only/test_ontology_filter_report.json`

## 4. Summary
- total_queries: 500
- total_candidates_before: 10000
- total_candidates_after: 3865
- removed_unsupported_candidates: 7955
- candidates_kept_by_direct_support: 1780
- candidates_kept_by_mechanism_support: 265
- queries_with_any_direct_support: 303
- queries_with_any_mechanism_support: 176
- fallback_queries: 91
- empty_queries_before_fallback: 91
- gold_in_ontology_candidates: 140
- top1_changed_queries: 260
- top5_changed_queries: 378

## 5. Sample before/after
### Query: lung abscess (disease)
- before_top5: ['Fusidic acid', 'Methylprednisolone', 'Dexamethasone', 'Oxytetracycline', 'Prednisolone']
- after_top5: ['Benzylpenicillin']
- support_labels_top5_after: ['direct']
- fallback_used: False

### Query: acquired hyperprolactinemia
- before_top5: ['Betamethasone', 'Hydrocortisone', 'Methylprednisolone', 'Cortisone acetate', 'Triamcinolone']
- after_top5: ['Cabergoline']
- support_labels_top5_after: ['mechanism']
- fallback_used: False

### Query: allergic rhinitis
- before_top5: ['Fusidic acid', 'Dexamethasone', 'Methylprednisolone', 'Oxytetracycline', 'Prednisolone']
- after_top5: ['Dexamethasone', 'Methylprednisolone', 'Prednisolone', 'Methdilazine', 'Triamcinolone']
- support_labels_top5_after: ['direct', 'direct', 'direct', 'direct', 'direct']
- fallback_used: False

### Query: blepharoconjunctivitis
- before_top5: ['Fusidic acid', 'Methylprednisolone', 'Dexamethasone', 'Prednisolone', 'Cortisone acetate']
- after_top5: ['Fusidic acid', 'Dexamethasone', 'Prednisolone', 'Cortisone acetate', 'Hydrocortisone']
- support_labels_top5_after: ['direct', 'direct', 'direct', 'direct', 'direct']
- fallback_used: False

### Query: parkinsonian-pyramidal syndrome
- before_top5: ['Betamethasone', 'Hydrocortisone', 'Cortisone acetate', 'Triamcinolone', 'Methylprednisolone']
- after_top5: ['Betamethasone', 'Hydrocortisone', 'Cortisone acetate', 'Triamcinolone', 'Methylprednisolone']
- support_labels_top5_after: ['unsupported', 'unsupported', 'unsupported', 'unsupported', 'unsupported']
- fallback_used: True

### Query: pharyngitis
- before_top5: ['Fusidic acid', 'Oxytetracycline', 'Dexamethasone', 'Methylprednisolone', 'Methdilazine']
- after_top5: ['Fusidic acid', 'Oxytetracycline', 'Methdilazine', 'Tetracycline', 'Demeclocycline']
- support_labels_top5_after: ['direct', 'direct', 'direct', 'direct', 'direct']
- fallback_used: False

### Query: diabetes mellitus (disease)
- before_top5: ['Betamethasone', 'Methylprednisolone', 'Triamcinolone', 'Hydrocortisone', 'Cortisone acetate']
- after_top5: ['Dexamethasone']
- support_labels_top5_after: ['mechanism']
- fallback_used: False

### Query: Trichinella spiralis infectious disease
- before_top5: ['Fusidic acid', 'Methylprednisolone', 'Dexamethasone', 'Cortisone acetate', 'Prednisolone']
- after_top5: ['Cortisone acetate', 'Hydrocortisone', 'Hydrocortisone acetate', 'Betamethasone', 'Prednisone']
- support_labels_top5_after: ['direct', 'direct', 'direct', 'direct', 'direct']
- fallback_used: False

### Query: type 2 diabetes mellitus
- before_top5: ['Betamethasone', 'Methylprednisolone', 'Triamcinolone', 'Hydrocortisone', 'Cortisone acetate']
- after_top5: ['Dexamethasone']
- support_labels_top5_after: ['mechanism']
- fallback_used: False

### Query: spondyloarthropathy
- before_top5: ['Betamethasone', 'Methylprednisolone', 'Triamcinolone', 'Hydrocortisone', 'Cortisone acetate']
- after_top5: ['Betamethasone', 'Triamcinolone', 'Cortisone acetate', 'Prednisolone', 'Prednisone']
- support_labels_top5_after: ['direct', 'direct', 'direct', 'direct', 'direct']
- fallback_used: False
