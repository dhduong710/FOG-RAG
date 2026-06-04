# Week 15 - Day 3 Retrieval Build

- variant_name: soft_support_fuzzy_retrieval_v1
- scoring_level: triple-first
- ontology consistency disabled in v1
- candidate stage kept frozen from soft_support_raw

## Selection policy
- retain_ratio: 0.67
- min_keep: 20
- stage_a: best triple per candidate
- stage_b: global fill by triple_score

## Summary
- avg_original_subgraph_size: 60.45
- avg_selected_subgraph_size: 36.714
- direct_shortcut_rate_before: 0.165492
- direct_shortcut_rate_after: 0.124421
- contra_rate_before: 0.005459
- contra_rate_after: 0.006265
- avg_candidate_coverage_preserved_rate: 1.0
- avg_top_band_coverage_preserved_rate: 1.0