# Week 14 Day 1 — Soft-support protocol freeze

## 1. Role of Week 14
Week 14 builds the first proper `soft_support_raw` branch on valid raw/no-injection candidates.

This is still a candidate-stage week.
It is not a fuzzy retrieval week and not a fuzzy encoder week.

## 2. Main truth
The main scientific truth remains raw / no-injection evaluation.

Injected rows remain supporting diagnostics only and are forbidden as the main path.

## 3. Decision split
Valid is the only decision split in Week 14.
Test must remain untouched this week.

## 4. Reference rows
Week 14 compares the following rows:
- backbone_raw
- ontology_raw
- soft_support_raw variants

## 5. Surviving formula family from Week 13
The surviving formula family is:
- evidence-aware scoring
- anti-shortcut direct-link penalty
- no hard ontology gating revival

The current starting family is:
`B_evidence_minus_direct`

## 6. Features not allowed as positive main signals
The following are forbidden as positive main support-score signals:
- type_valid_flag
- schema_valid_flag
- type_filtered_keep_flag
- ontology_keep_flag
- candidate_query_edge_count

## 7. Features that may be used only as supporting/diagnostic
The following are not primary support signals:
- contra_flag
- contra_penalty
- query_edge_touch_count

## 8. Variant plan for Week 14
Week 14 will build exactly three support-score variants:
- b025
- b050
- bcap

These are candidate reordering variants only.
No pruning is allowed.

## 9. Success criterion
By the end of Week 14, the project must choose one row:
`soft_support_raw`

This row will become the main intermediate row for Novelty 2.

## 10. Non-goals
Week 14 does not:
- run test,
- build fuzzy retrieval,
- train fuzzy encoder,
- revive hard ontology gating,
- mix candidate-stage results with end-to-end ranking claims.