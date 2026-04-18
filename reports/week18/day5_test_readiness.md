# Week 18 Day 5 — Test Readiness

## Decision
- **PARTIAL_READY**
- Recommended next step: `Do not run official locked test yet; finish missing main test sources first.`

## Required test sources
- `backbone_raw_test_source`: exists=`True` is_file=`False` is_dir=`True` path=`results/reference_rows/backbone_raw_test`
- `raw_source_test`: exists=`True` is_file=`True` is_dir=`False` path=`dataset/setting_a/23_noinj_source/test_top20_raw.json`
- `ontology_raw_test`: exists=`True` is_file=`True` is_dir=`False` path=`dataset/setting_a/24_noinj_ontology/test_top20_ontology_raw.json`
- `soft_support_raw_test`: exists=`False` is_file=`False` is_dir=`False` path=`dataset/setting_a/26_n2_soft_support/test_top20_soft_support_main.json`
- `retrieval_main_test`: exists=`False` is_file=`False` is_dir=`False` path=`dataset/setting_a/27_n2_fuzzy_retrieval/test_fuzzy_retrieval_main.json`
- `setting_b_test_annotations`: exists=`True` is_file=`True` is_dir=`False` path=`dataset/setting_b/04_contra_checked/test_b_annotations_contra_checked.json`

## Optional test sources
- `encoder_probe_test_optional`: exists=`False` is_file=`False` is_dir=`False` path=`dataset/setting_a/28_n2_fuzzy_encoder/test_fuzzy_encoder_probe_v0.json`

## Schema notes
- No obvious schema issues detected in the inspected test files.

## Decision notes
- Missing required test sources: ['soft_support_raw_test', 'retrieval_main_test']
- Main locked-test sources still missing: ['soft_support_raw_test', 'retrieval_main_test']
