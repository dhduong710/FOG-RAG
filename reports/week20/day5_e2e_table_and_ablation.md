# Day 5 — E2E main table and ablation

- status: **BUILT_REVIEWER_SAFE**
- provisional_main_row: **`soft_support_fuzzy_retrieval_main`**

## 1. Main E2E table
### backbone_raw
#### Candidate ceiling reviewer-safe
- num_examples: `500`
- k: `20`
- gold_present_rate: `0.24`
- mrr_at20: `0.06456283`
- hits1_at20: `0.024`
- hits3_at20: `0.07`
- hits10_at20: `0.192`
- hits20_at20: `0.24`
- avg_gold_rank_with_absent_as_21: `17.652`
- gold_rank_21_count: `380`
#### E2E generation reviewer-safe
- num_examples: `500`
- k: `20`
- gold_present_rate: `0.24`
- mrr_at20: `0.04763573`
- hits1_at20: `0.002`
- hits3_at20: `0.048`
- hits10_at20: `0.178`
- hits20_at20: `0.24`
- avg_adjusted_rank_with_absent_as_21: `17.8`
- rank_21_count: `380`
- exact_generated_rate: `0.002`
- pred_in_candidate_rate: `0.98`
#### Graph package
- num_rows: `500`
- avg_subgraph_size: `59.932`
- min_subgraph_size: `43`
- max_subgraph_size: `119`

### soft_support_raw
#### Candidate ceiling reviewer-safe
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
#### E2E generation reviewer-safe
- num_examples: `500`
- k: `20`
- gold_present_rate: `0.24`
- mrr_at20: `0.07467554`
- hits1_at20: `0.0`
- hits3_at20: `0.132`
- hits10_at20: `0.218`
- hits20_at20: `0.24`
- avg_adjusted_rank_with_absent_as_21: `17.042`
- rank_21_count: `380`
- exact_generated_rate: `0.0`
- pred_in_candidate_rate: `0.98`
#### Graph package
- num_rows: `500`
- avg_subgraph_size: `59.932`
- min_subgraph_size: `43`
- max_subgraph_size: `119`

### soft_support_fuzzy_retrieval_main
#### Candidate ceiling reviewer-safe
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
#### E2E generation reviewer-safe
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
#### Graph package
- num_rows: `500`
- avg_subgraph_size: `32.34`
- min_subgraph_size: `24`
- max_subgraph_size: `51`
- selected_source_variant_set: `['soft_support_fuzzy_retrieval_tight']`
- avg_candidate_coverage_preserved_rate: `1.0`
- avg_direct_shortcut_path_rate: `0.11081471`

## 2. Narrative checks
- soft_improves_candidate_mrr_vs_backbone: `True`
- soft_improves_e2e_mrr_vs_backbone: `True`
- retrieval_preserves_candidate_mrr_vs_soft: `True`
- retrieval_preserves_e2e_mrr_vs_soft: `True`
- retrieval_has_smaller_subgraph_than_soft: `True`
- retrieval_keeps_candidate_coverage: `True`
- encoder_remains_appendix_only: `True`

## 3. soft_minus_backbone
### Candidate ceiling
- delta_gold_present_rate: `0.0`
- delta_mrr_at20: `0.06076335`
- delta_hits1_at20: `0.048`
- delta_hits3_at20: `0.096`
- delta_hits10_at20: `0.03`
- delta_hits20_at20: `0.0`
### E2E generation
- delta_gold_present_rate: `0.0`
- delta_mrr_at20: `0.02703981`
- delta_hits1_at20: `-0.002`
- delta_hits3_at20: `0.084`
- delta_hits10_at20: `0.04`
- delta_hits20_at20: `0.0`

## 4. retrieval_minus_soft
### Candidate ceiling
- delta_gold_present_rate: `0.0`
- delta_mrr_at20: `0.0`
- delta_hits1_at20: `0.0`
- delta_hits3_at20: `0.0`
- delta_hits10_at20: `0.0`
- delta_hits20_at20: `0.0`
### E2E generation
- delta_gold_present_rate: `0.0`
- delta_mrr_at20: `1.099e-05`
- delta_hits1_at20: `0.0`
- delta_hits3_at20: `0.0`
- delta_hits10_at20: `0.0`
- delta_hits20_at20: `0.0`
### Graph package
- delta_avg_subgraph_size: `-27.592`
- retrieval_avg_subgraph_size: `32.34`
- soft_avg_subgraph_size: `59.932`
- retrieval_selected_source_variant_set: `['soft_support_fuzzy_retrieval_tight']`
- retrieval_avg_candidate_coverage_preserved_rate: `1.0`
- retrieval_avg_direct_shortcut_path_rate: `0.11081471`

## 5. Decision note
Keep retrieval_main as the paper-facing main row: soft support provides the main ranking gain over backbone, while retrieval_main preserves candidate/E2E performance and substantially reduces the evidence subgraph.

## 6. Known limitation
E2E Hits@1 remains weak because the frozen LLM often generates a plausible candidate instead of the exact gold string even when gold is ranked first.
