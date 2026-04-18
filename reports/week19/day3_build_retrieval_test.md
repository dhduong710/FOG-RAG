# Day 3 — Build retrieval_main_test

- status: **BUILT**
- selected_source_variant: `soft_support_fuzzy_retrieval_tight`
- output: `/home/duong/code/FOG-RAG/dataset/setting_a/27_n2_fuzzy_retrieval/test_fuzzy_retrieval_main.json`

## 1. Retrieval source freeze
- selected_source_variant: `soft_support_fuzzy_retrieval_tight`
- canonical_variant_name: `soft_support_fuzzy_retrieval_main`

## 2. Path feature summary
- num_rows: `500`
- avg_subgraph_num_triples_before_scoring: `59.932`
- touch_candidate_rate: `0.490089`
- touch_query_rate: `0.402223`
- touch_top_band_rate: `0.085997`
- direct_shortcut_rate_before: `0.190483`
- contra_rate_before: `0.000133`
- schema_consistency_rate_known_only: `None`
- top_relations_seen: `[('indication', 21253), ('associated_with', 6840), ('target', 1366), ('ppi', 507)]`

## 3. Retrieval-main summary
- num_rows: `500`
- avg_original_subgraph_size: `59.932`
- avg_selected_subgraph_size: `32.34`
- avg_triple_score: `0.504186`
- direct_shortcut_path_rate: `0.099505`
- contradiction_path_rate: `0.000247`
- candidate_coverage_preserved_rate: `1.0`
- top_band_coverage_preserved_rate: `1.0`

## 4. Policy checks
- retrieval_logic_changed: `False`
- selected_source_variant_changed: `False`
- candidate_stage_reopened: `False`
- encoder_promoted: `False`

## 5. Day-3 conclusion
Built `test_fuzzy_retrieval_main.json` by reusing the frozen selected retrieval source variant from valid-side, preserving graph-side fields and canonicalizing the row name to `soft_support_fuzzy_retrieval_main`.
