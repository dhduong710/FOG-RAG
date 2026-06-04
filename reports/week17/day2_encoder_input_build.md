# Week 17 Day 2 — Encoder Input Build

## Goal
- Build `valid_encoder_inputs.json` from retrieval main row.
- Convert retrieval triple scores into normalized edge weights for encoder probe.

## Source
- input row: `soft_support_fuzzy_retrieval_main`
- output row: `encoder_inputs_from_retrieval_main`

## Summary
- **week**: `17`
- **day**: `2`
- **source_row**: `soft_support_fuzzy_retrieval_main`
- **output_row**: `encoder_inputs_from_retrieval_main`
- **num_rows**: `500`
- **num_missing_valid_b_rows**: `0`
- **contra_alignment_exact_row_count**: `500`
- **avg_num_edges**: `32.556`
- **avg_edge_weight**: `0.356898`
- **avg_high_confidence_edge_rate**: `0.29781`
- **avg_weighted_shortcut_rate**: `0.028452`
- **avg_query_incident_weight_mass**: `0.591558`
- **avg_candidate_incident_weight_mass_mean**: `0.553007`
- **avg_candidate_incident_weight_mass_max**: `1.519407`
- **edge_confidence_band_counts**: `{'high': 4826, 'low': 8599, 'medium': 2853}`

## Notes
- No reranking was performed on day 2.
- No probe message passing was run on day 2.
- The output is intended for day-3 encoder probe only.
