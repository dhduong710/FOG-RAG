# Week 21 Day 7 — Closeout

## Decision

**WEEK21_BASELINE_FREEZE_GO_DATASET2**

## Check summary

- Overall pass: `True`
- Failed keys: `[]`

## Passed checks

- `protocol_top_k_is_20`: `True`
- `protocol_gold_injection_forbidden`: `True`
- `protocol_rr_absent_is_zero`: `True`
- `protocol_absent_rank_is_21`: `True`
- `all_6_baselines_rerun`: `True`
- `all_rerun_rows_and_candidate_sizes_pass`: `True`
- `all_day4_query_sets_match`: `True`
- `all_day4_absent_rr_pass`: `True`
- `baseline_no_gold_injection`: `True`
- `fograg_main_mrr_above_complex`: `True`
- `complex_gold_above_fograg_main`: `True`
- `soft_and_retrieval_same_ranking_metrics`: `True`
- `fograg_main_improves_backbone_mrr`: `True`
- `decision_headline_ok`: `True`
- `assets_ready`: `True`

## Main numbers

- `backbone_raw`: Gold@20=0.2400, MRR@20=0.064563, H@1=0.0240, H@3=0.0700, H@10=0.1920
- `complex`: Gold@20=0.5740, MRR@20=0.124731, H@1=0.0320, H@3=0.1180, H@10=0.3840
- `soft_support_raw`: Gold@20=0.2400, MRR@20=0.125326, H@1=0.0720, H@3=0.1660, H@10=0.2220
- `fograg_main`: Gold@20=0.2400, MRR@20=0.125326, H@1=0.0720, H@3=0.1660, H@10=0.2220

## Next

Week 22 should start Dataset 2 setup and protocol adaptation.
