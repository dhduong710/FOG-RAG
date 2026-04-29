# Week 23 Day 2 — Support Features and Hard-Support Negative Control

## Decision

`SUPPORT_FEATURES_READY_HARD_CONTROL_BUILT`

## Important wording

This is **not** PharmKG ontology filtering.

Use paper-safe wording:

`hard graph-support control on PharmKG therapeutic-association proxy task`

Relation `T` is still called `therapeutic_association_proxy`, not clinical indication.

## Support feature summary

| Split | Rows | Candidate rows | Evidence rate | Shortest-path rate | Direct-T rate | Gold with path rate |
|---|---:|---:|---:|---:|---:|---:|
| valid | 500 | 10000 | 1.0000 | 1.0000 | 0.4094 | 1.0000 |
| test | 500 | 10000 | 1.0000 | 1.0000 | 0.3897 | 1.0000 |

## Hard-support eval metrics

| Split | Gold@20 | MRR@20 | MRR present-only | H@1 | H@3 | H@10 | H@20 | Rank21 | Avg cand size |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| valid | 0.070 | 0.017846471743 | 0.254949596327 | 0.010 | 0.014 | 0.034 | 0.070 | 465 | 20.000 |
| test | 0.092 | 0.020480769841 | 0.222617063486 | 0.008 | 0.020 | 0.046 | 0.092 | 454 | 20.000 |

## Hard-support audit

| Split | Fallback rows | Raw gold present | Hard gold present | Gold removed | Gold removed rate | Avg cand size |
|---|---:|---:|---:|---:|---:|---:|
| valid | 0 | 35 | 35 | 0 | 0.0000 | 20.000 |
| test | 0 | 46 | 46 | 0 | 0.0000 | 20.000 |

## Interpretation

Day 2 prepares the candidate-level evidence layer for soft support.

The hard-support row is a negative control. If it removes gold or reduces MRR, that supports the same scientific motivation as PrimeKG Novelty 2: hard support is brittle under raw no-injection retrieval.

## Files written

- `dataset/setting_c_pharmkg/08_support_features/valid_support_features.json`
- `dataset/setting_c_pharmkg/08_support_features/test_support_features.json`
- `dataset/setting_c_pharmkg/08_support_features/support_feature_summary.json`
- `dataset/setting_c_pharmkg/09_hard_support_raw/valid_top20_hard_support_raw.json`
- `dataset/setting_c_pharmkg/09_hard_support_raw/test_top20_hard_support_raw.json`
- `dataset/setting_c_pharmkg/09_hard_support_raw/hard_support_audit.json`
- `results/week23/hard_support_raw_eval_valid.json`
- `results/week23/hard_support_raw_eval_test.json`

## Next step

Day 3 will run frozen soft support:

`support_score = 1.0 * evidence_positive - 0.50 * direct_T_candidate_query_flag`
