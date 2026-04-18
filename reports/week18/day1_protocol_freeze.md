# Week 18 Day 1 — Protocol Freeze

## Theme
- lock_retrieval_main_and_prepare_clean_evaluation_package

## Day-1 decisions
- Main truth = raw_no_injection.
- Decision split = valid.
- Reference row = backbone_raw.
- Negative control row = ontology_raw.
- Intermediate row = soft_support_raw.
- Main row = soft_support_fuzzy_retrieval_main.
- Appendix row = soft_support_fuzzy_encoder_probe_v0.
- Test mode = readiness_only_not_official_locked_test.

## Row roles
- **reference_row**: `backbone_raw`
- **negative_control_row**: `ontology_raw`
- **intermediate_row**: `soft_support_raw`
- **main_row**: `soft_support_fuzzy_retrieval_main`
- **appendix_row**: `soft_support_fuzzy_encoder_probe_v0`

## Main valid table rows
- `backbone_raw`
- `ontology_raw`
- `soft_support_raw`
- `soft_support_fuzzy_retrieval_main`

## Appendix / supporting rows
- `soft_support_fuzzy_encoder_probe_v0`

## Forbidden actions
- Do not reopen candidate-stage.
- Do not change retrieval main row.
- Do not promote encoder probe to main row.
- Do not run official locked test this week.
- Do not introduce new retrieval or encoder variants.
- Do not mix appendix row into the main 4-row valid table.

## Input status
- `week17_go_decision`: OK — `results/week17/week17_go_decision.json`
- `backbone_reference_valid`: OK — `results/reference_rows/backbone_raw_valid`
- `raw_source_valid`: OK — `dataset/setting_a/23_noinj_source/valid_top20_raw.json`
- `ontology_raw_valid`: OK — `dataset/setting_a/24_noinj_ontology/valid_top20_ontology_raw.json`
- `soft_support_valid`: OK — `dataset/setting_a/26_n2_soft_support/valid_top20_soft_support_main.json`
- `retrieval_main_valid`: OK — `dataset/setting_a/27_n2_fuzzy_retrieval/valid_fuzzy_retrieval_main.json`
- `encoder_probe_valid`: OK — `dataset/setting_a/28_n2_fuzzy_encoder/valid_fuzzy_encoder_probe_v0.json`
- `setting_b_valid_annotations`: OK — `dataset/setting_b/04_contra_checked/valid_b_annotations_contra_checked.json`
- `type_map`: OK — `dataset/setting_b/01_annotations/type_map.tsv`
- `schema_rules`: OK — `dataset/setting_b/01_annotations/schema_rules.json`
- `path_templates`: OK — `dataset/setting_b/01_annotations/path_templates.yaml`

## Success criteria
- Week-18 protocol is frozen with no ambiguity about row roles.
- Retrieval main is explicitly locked as the main row after week 17.
- Encoder probe is explicitly positioned as appendix/supporting only.
- Valid is the decision split for week 18.
- Test is limited to readiness/package check only.
- Main table row set is fixed to 4 scientific rows.

## Conclusion
- Status: **READY**
- All required inputs are present. Week 18 can proceed to Day 2.
