# Day 4 — Build test eval-ready package

- status: **BUILT**

## 1. Output files
- backbone_raw: `/home/duong/code/FOG-RAG/dataset/setting_b/08_n2_eval_test/test_backbone_raw_eval.json`
- ontology_raw: `/home/duong/code/FOG-RAG/dataset/setting_b/08_n2_eval_test/test_ontology_raw_eval.json`
- soft_support_raw: `/home/duong/code/FOG-RAG/dataset/setting_b/08_n2_eval_test/test_soft_support_raw_eval.json`
- retrieval_main: `/home/duong/code/FOG-RAG/dataset/setting_b/08_n2_eval_test/test_retrieval_main_eval.json`

## 2. Row summaries
### backbone_raw
- num_rows: `500`
- gold_present_rate: `0.24`
- mrr_at20: `0.06456283`
- mrr_present_only: `0.26901179`
- hits1_at20: `0.024`
- hits3_at20: `0.07`
- hits10_at20: `0.192`
- avg_gold_rank: `17.652`
- top_keys_match_valid: `True`
- metrics_keys_match_valid: `True`
- gold_rank_21_count: `380`

### ontology_raw
- num_rows: `500`
- gold_present_rate: `0.012`
- mrr_at20: `0.00313975`
- mrr_present_only: `0.26164622`
- hits1_at20: `0.002`
- hits3_at20: `0.002`
- hits10_at20: `0.01`
- avg_gold_rank: `20.84`
- top_keys_match_valid: `True`
- metrics_keys_match_valid: `True`
- gold_rank_21_count: `494`

### soft_support_raw
- num_rows: `500`
- gold_present_rate: `0.24`
- mrr_at20: `0.12532618`
- mrr_present_only: `0.52219244`
- hits1_at20: `0.072`
- hits3_at20: `0.166`
- hits10_at20: `0.222`
- avg_gold_rank: `16.804`
- top_keys_match_valid: `True`
- metrics_keys_match_valid: `True`
- gold_rank_21_count: `380`

### retrieval_main
- num_rows: `500`
- gold_present_rate: `0.24`
- mrr_at20: `0.12532618`
- mrr_present_only: `0.52219244`
- hits1_at20: `0.072`
- hits3_at20: `0.166`
- hits10_at20: `0.222`
- avg_gold_rank: `16.804`
- top_keys_match_valid: `True`
- metrics_keys_match_valid: `True`
- gold_rank_21_count: `380`

## 3. Global checks
- all_rows_have_500_examples: `True`
- all_query_sets_match: `True`
- all_top_level_keys_match_across_test_rows: `True`
- all_gold_rank_use_21_sentinel_when_missing: `True`
- all_row_metrics_keys_match_valid_refs: `True`
- all_top_keys_match_valid_refs: `True`

## 4. Metric policy
- main_metric: `mrr_at20`
- rr_rule: `1/rank if rank <= 20 else 0`
- gold_rank_out_of_top20: `21`

## 5. Day-4 conclusion
Built test eval-ready package for all four scientific rows under the frozen reviewer-safe policy, with unified schema, gold_rank sentinel=21 for out-of-top20, and row-level metrics ready for locked-test aggregation on Day 5.
