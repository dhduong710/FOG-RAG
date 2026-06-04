# Week 17 Day 4 — Probe Compare

## Rows compared
- `soft_support_raw`
- `soft_support_fuzzy_retrieval_main`
- `soft_support_fuzzy_encoder_probe_v0`

## Metrics
### soft_support_raw
- **num_rows**: `500`
- **gold_present_rate**: `0.202`
- **mrr_like**: `0.135644`
- **hits1_like**: `0.056`
- **hits3_like**: `0.134`
- **hits10_like**: `0.182`
- **avg_gold_rank**: `17.676`
- **avg_top5_direct_link_rate**: `0.0072`
- **avg_top5_evidence_positive_rate**: `1.0`
- **avg_top5_contra_rate**: `0.0`

### soft_support_fuzzy_retrieval_main
- **num_rows**: `500`
- **gold_present_rate**: `0.202`
- **mrr_like**: `0.135644`
- **hits1_like**: `0.056`
- **hits3_like**: `0.134`
- **hits10_like**: `0.182`
- **avg_gold_rank**: `17.676`
- **avg_subgraph_size**: `32.556`
- **avg_triple_score**: `0.499203`
- **avg_direct_shortcut_path_rate**: `0.0`
- **avg_contradiction_path_rate**: `0.0`
- **candidate_coverage_preserved_rate**: `1.0`

### soft_support_fuzzy_encoder_probe_v0
- **num_rows**: `500`
- **gold_present_rate**: `0.202`
- **mrr_like**: `0.091707`
- **hits1_like**: `0.012`
- **hits3_like**: `0.058`
- **hits10_like**: `0.176`
- **avg_gold_rank**: `17.98`
- **avg_probe_top5_direct_candidate_rate**: `0.01`
- **avg_probe_score**: `0.19096`
- **avg_incident_norm**: `0.434486`
- **avg_bridge_norm**: `0.0135`
- **avg_direct_norm**: `0.031146`
- **avg_weighted_edge_count**: `32.556`
- **avg_high_confidence_edge_rate**: `0.29781`

## Probe vs retrieval main
- **num_rows**: `500`
- **improved_vs_retrieval_main**: `8`
- **worsened_vs_retrieval_main**: `70`
- **same_rank_vs_retrieval_main**: `422`
- **same_top1_rate_vs_retrieval_main**: `0.274`
- **same_top5_exact_rate_vs_retrieval_main**: `0.102`
- **avg_rank_delta_probe_minus_retrieval**: `0.304`
