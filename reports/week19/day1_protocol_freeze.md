# Day 1 Protocol Freeze — Week 19

- status: **READY_FOR_LOCKED_TEST_WEEK**
- theme: **Build missing main test artifacts then run official locked test**
- decision split: **test**

## 1. Locked row roles
- reference_row: `backbone_raw`
- negative_control: `ontology_raw`
- candidate_stage_intermediate: `soft_support_raw`
- main_row: `soft_support_fuzzy_retrieval_main`
- appendix_only: `['soft_support_fuzzy_encoder_probe_v0']`

## 2. Metric policy
- main_metric: `mrr_at20`
- rr_rule: `1/rank if rank <= 20 else 0`
- gold_rank_out_of_top20: `21`
- secondary_metrics:
  - `gold_present_rate`
  - `mrr_present_only`
  - `hits1_at20`
  - `hits3_at20`
  - `hits10_at20`
  - `avg_gold_rank`

## 3. Required week18 prerequisites
- [OK] `results/week18/retrieval_main_lock_report.json`
- [OK] `results/week18/novelty2_valid_main_table.json`
- [OK] `results/week18/novelty2_valid_ablation.json`
- [OK] `results/week18/encoder_probe_appendix_note.json`
- [OK] `results/week18/test_readiness_manifest.json`
- [OK] `results/week18/week18_go_decision.json`
- [OK] `dataset/setting_b/07_n2_eval_valid/valid_backbone_raw_eval.json`
- [OK] `dataset/setting_b/07_n2_eval_valid/valid_ontology_raw_eval.json`
- [OK] `dataset/setting_b/07_n2_eval_valid/valid_soft_support_raw_eval.json`
- [OK] `dataset/setting_b/07_n2_eval_valid/valid_retrieval_main_eval.json`

## 4. Missing test artifacts to build next
- `dataset/setting_a/26_n2_soft_support/test_top20_soft_support_main.json`
- `dataset/setting_a/27_n2_fuzzy_retrieval/test_fuzzy_retrieval_main.json`

## 5. Forbidden changes this week
- reopen candidate-stage
- change soft_support_raw formula
- change retrieval main variant
- promote encoder to main path
- add new novelty
- change reviewer-safe metric policy
- change row roles frozen on valid

## 6. Day-1 conclusion
Week 19 is officially frozen as a locked-test week. Next steps are to build `soft_support_raw_test` and `retrieval_main_test` without changing formula, retrieval variant, or row roles.
