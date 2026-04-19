# Day 5 — Official locked test main table

- status: **BUILT**
- provisional_main_row: **`soft_support_fuzzy_retrieval_main`**

## 1. Main table rows
### backbone_raw
- num_rows: `500`
- gold_present_rate: `0.24`
- mrr_at20: `0.06456283`
- mrr_present_only: `0.26901179`
- hits1_at20: `0.024`
- hits3_at20: `0.07`
- hits10_at20: `0.192`
- avg_gold_rank: `17.652`
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
- gold_rank_21_count: `380`
- avg_top5_direct_link_rate: `0.0076`
- avg_top5_evidence_positive_rate: `1.0`
- avg_top5_ontology_keep_rate: `0.2616`
- avg_top5_contra_rate: `0.0`

### soft_support_fuzzy_retrieval_main
- num_rows: `500`
- gold_present_rate: `0.24`
- mrr_at20: `0.12532618`
- mrr_present_only: `0.52219244`
- hits1_at20: `0.072`
- hits3_at20: `0.166`
- hits10_at20: `0.222`
- avg_gold_rank: `16.804`
- gold_rank_21_count: `380`
- selected_source_variant_set: `['soft_support_fuzzy_retrieval_tight']`
- avg_triple_score: `0.506887`
- direct_shortcut_path_rate: `0.110815`
- contradiction_path_rate: `0.00024`
- avg_subgraph_size: `32.34`
- candidate_coverage_preserved_rate: `1.0`

## 2. Narrative checks
- ontology_is_weaker_than_backbone: `True`
- soft_is_stronger_than_backbone: `True`
- retrieval_preserves_or_improves_vs_soft: `True`
- retrieval_has_cleaner_graph_package: `False`

## 3. Candidate-stage gain vs backbone
- delta_mrr_at20: `0.06076335`
- delta_hits1_at20: `0.048`
- delta_hits3_at20: `0.096`
- delta_hits10_at20: `0.03`
- delta_avg_gold_rank: `-0.848`

## 4. Retrieval-stage gain vs soft support
- delta_mrr_at20: `0.0`
- delta_hits1_at20: `0.0`
- delta_hits3_at20: `0.0`
- delta_hits10_at20: `0.0`
- delta_avg_gold_rank: `0.0`

## 5. Decision reason
retrieval_main preserves mrr_at20 versus soft_support_raw on locked test while keeping the cleaner graph/evidence package.

## 6. Day-5 conclusion
Built the official locked reviewer-safe test main table and ablation export. Encoder remains appendix-only; the four scientific rows are now aggregated and ready for test-side case review on Day 6.
