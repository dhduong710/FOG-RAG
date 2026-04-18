# Day 2 — Build soft_support_raw_test

- status: **BUILT**
- output: `/home/duong/code/FOG-RAG/dataset/setting_a/26_n2_soft_support/test_top20_soft_support_main.json`
- variant_name: `soft_support_raw_b050`

## 1. Frozen formula
- score_family: `B_evidence_minus_direct`
- evidence_positive_weight: `1.0`
- direct_link_penalty: `0.5`
- contra_penalty_weight: `0.1`
- use_capped_evidence: `False`

## 2. Build summary
- num_rows: `500`
- num_candidates_total: `10000`
- avg_candidates_per_query: `20.0`
- rows_with_exactly_20_candidates: `500`
- gold_present_rate_after_reorder: `0.24`
- avg_top5_direct_link_rate: `0.0076`
- avg_top5_evidence_positive_rate: `1.0`
- avg_top5_ontology_keep_rate: `0.2616`
- avg_top5_contra_rate: `0.0`

## 3. Schema check vs valid main
- valid_main_top_keys: `['split', 'query_entity', 'query_entity_id', 'gold_entity', 'gold_entity_id', 'gold_rank_in_full_universe', 'gold_in_topk_raw', 'variant_name', 'candidate_entities', 'candidate_entity_ids', 'support_scores', 'support_rank_order', 'candidate_debug_rows']`
- test_main_top_keys: `['split', 'query_entity', 'query_entity_id', 'gold_entity', 'gold_entity_id', 'gold_rank_in_full_universe', 'gold_in_topk_raw', 'variant_name', 'candidate_entities', 'candidate_entity_ids', 'support_scores', 'support_rank_order', 'candidate_debug_rows']`
- top_keys_match: `True`
- valid_main_debug_keys: `['candidate_entity', 'candidate_entity_id', 'base_rank', 'support_rank', 'support_score', 'evidence_edge_touch_count', 'candidate_query_edge_count', 'ontology_keep_flag', 'contra_flag']`
- test_main_debug_keys: `['candidate_entity', 'candidate_entity_id', 'base_rank', 'support_rank', 'support_score', 'evidence_edge_touch_count', 'candidate_query_edge_count', 'ontology_keep_flag', 'contra_flag']`
- debug_keys_match: `True`

## 4. Policy checks
- reorder_only: `True`
- no_pruning: `True`
- formula_changed: `False`
- row_naming_changed: `False`

## 5. Day-2 conclusion
Built `test_top20_soft_support_main.json` by applying the frozen soft-support reorder logic to the test raw/no-injection source without pruning, formula change, or row-role change.
