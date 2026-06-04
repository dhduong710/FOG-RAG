# Day 4 — E2E infer for retrieval_main

- status: **BUILT_REVIEWER_SAFE**
- main metric: `reviewer_safe_mrr_at20`
- RR rule: `1/rank if rank <= 20 else 0`
- gold absent from top-20: `RR@20 = 0`

## 1. retrieval_main — candidate ceiling reviewer-safe
- num_examples: `500`
- k: `20`
- gold_present_rate: `0.24`
- mrr_at20: `0.12532618`
- hits1_at20: `0.072`
- hits3_at20: `0.166`
- hits10_at20: `0.222`
- hits20_at20: `0.24`
- avg_gold_rank_with_absent_as_21: `16.804`
- gold_rank_21_count: `380`
- rr_rule: `1/rank if rank <= 20 else 0`

## 2. retrieval_main — E2E generation reviewer-safe
- num_examples: `500`
- k: `20`
- gold_present_rate: `0.24`
- mrr_at20: `0.07468653`
- hits1_at20: `0.0`
- hits3_at20: `0.132`
- hits10_at20: `0.218`
- hits20_at20: `0.24`
- avg_adjusted_rank_with_absent_as_21: `17.04`
- rank_21_count: `380`
- exact_generated_rate: `0.0`
- pred_in_candidate_rate: `0.998`
- rr_rule: `1/adjusted_rank if adjusted_rank <= 20 else 0`
- absent_gold_policy: `RR@20 = 0 no matter what the LLM generates`

## 3. retrieval_main — graph package
- num_rows: `500`
- selected_source_variant_set: `['soft_support_fuzzy_retrieval_tight']`
- avg_subgraph_size: `32.34`
- min_subgraph_size: `24`
- max_subgraph_size: `51`
- avg_candidate_coverage_preserved_rate: `1.0`
- avg_direct_shortcut_path_rate: `0.11081471`

## 4. delta_retrieval_minus_soft

### Candidate ceiling
- delta_mrr_at20: `0.0`
- delta_hits1_at20: `0.0`
- delta_hits3_at20: `0.0`
- delta_hits10_at20: `0.0`
- delta_hits20_at20: `0.0`

### E2E generation
- delta_mrr_at20: `1.099e-05`
- delta_hits1_at20: `0.0`
- delta_hits3_at20: `0.0`
- delta_hits10_at20: `0.0`
- delta_hits20_at20: `0.0`

## 5. delta_retrieval_minus_backbone

### Candidate ceiling
- delta_mrr_at20: `0.06076335`
- delta_hits1_at20: `0.048`
- delta_hits3_at20: `0.096`
- delta_hits10_at20: `0.03`
- delta_hits20_at20: `0.0`

### E2E generation
- delta_mrr_at20: `0.0270508`
- delta_hits1_at20: `-0.002`
- delta_hits3_at20: `0.084`
- delta_hits10_at20: `0.04`
- delta_hits20_at20: `0.0`

## 6. Audit note
Raw `infer.py` metrics are retained only for audit. Paper-facing metrics should use the reviewer-safe recomputation in this report.
