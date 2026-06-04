# Week 15 - Day 2 Path/Triple Feature Build

## Main decision
- Feature table was built on valid only.
- Row alignment used row index, not query_entity_id only.
- Total rows: 500
- Unique query ids: 316

## Summary
- avg_subgraph_size: 60.45
- avg_triple_feature_rows_per_row: 60.45
- touch_query_rate: 0.394607
- touch_candidate_rate: 0.452341
- touch_top_band_candidate_rate: 0.085591
- direct_candidate_query_rate: 0.165492
- contra_flag_rate: 0.005459
- schema_known_count: 0
- schema_consistent_rate_among_known: None

## Candidate band counts
{
  "top_band": 2500,
  "mid_band": 2500,
  "tail_band": 5000
}

## Notes
- This day only builds retrieval-ready features.
- No path/triple score has been finalized yet.
- No subgraph was reselected yet.