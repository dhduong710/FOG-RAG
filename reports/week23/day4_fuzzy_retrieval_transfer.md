# Week 23 Day 4 — Fuzzy Retrieval Transfer on PharmKG

## Decision

`FUZZY_RETRIEVAL_TRANSFER_READY`

## Variant

- Variant name: `fuzzy_retrieval_main`
- Source variant: `soft_support_pharmkg_b050`
- Ranking policy: preserve soft-support candidate order
- Gold injection: false
- Target relation: `T`
- Relation label: `therapeutic_association_proxy`

## Retrieval config

- retain_ratio: `0.55`
- min_keep: `18`
- top/mid/tail band weights: `1.0`, `0.6`, `0.25`
- touch_candidate_weight: `0.35`
- touch_query_weight: `0.05`
- direct_shortcut_penalty: `-0.8`
- contra_penalty: `0.0`
- density_weight: `0.05`

## Ranking metrics

| Split | Gold@20 | MRR@20 | MRR present-only | H@1 | H@3 | H@10 | H@20 | Rank21 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| valid | 0.070 | 0.021307588490 | 0.304394121285 | 0.010 | 0.020 | 0.054 | 0.070 | 465 |
| test | 0.092 | 0.028159018759 | 0.306076290859 | 0.012 | 0.030 | 0.068 | 0.092 | 454 |

## Deltas vs soft_support_raw

| Split | Delta Gold@20 | Delta MRR@20 | Delta H@1 | Delta H@3 | Delta H@10 |
|---|---:|---:|---:|---:|---:|
| valid | 0.000000 | 0.000000000000 | 0.000000 | 0.000000 | 0.000000 |
| test | 0.000000 | 0.000000000000 | 0.000000 | 0.000000 | 0.000000 |

## Retrieval compression and coverage

| Split | Original size | Selected size | Retain ratio | Candidate coverage | Top-band coverage | Direct shortcut original | Direct shortcut selected |
|---|---:|---:|---:|---:|---:|---:|---:|
| valid | 100.00 | 55.00 | 0.550 | 1.000 | 1.000 | 0.117 | 0.208 |
| test | 100.00 | 55.00 | 0.550 | 1.000 | 1.000 | 0.112 | 0.199 |

## Interpretation

Fuzzy retrieval is not intended to improve ranking directly on Day 4. Its goal is to preserve the Day 3 soft-support ranking while reducing evidence budget and prioritizing high-confidence candidate-support triples.

If MRR is unchanged and selected subgraph size is substantially smaller, this is a positive FOG-RAG result: cleaner evidence without ranking collapse.

## Files written

- `dataset/setting_c_pharmkg/11_fuzzy_retrieval/valid_path_features.json`
- `dataset/setting_c_pharmkg/11_fuzzy_retrieval/test_path_features.json`
- `dataset/setting_c_pharmkg/11_fuzzy_retrieval/valid_fuzzy_retrieval_main.json`
- `dataset/setting_c_pharmkg/11_fuzzy_retrieval/test_fuzzy_retrieval_main.json`
- `dataset/setting_c_pharmkg/11_fuzzy_retrieval/retrieval_config.json`
- `dataset/setting_c_pharmkg/11_fuzzy_retrieval/retrieval_summary.json`
- `results/week23/fuzzy_retrieval_eval_valid.json`
- `results/week23/fuzzy_retrieval_eval_test.json`

## Next step

Day 5 will build the final reviewer-safe PharmKG table comparing backbone_raw, hard_support_raw, soft_support_raw, fuzzy_retrieval_main, and six Week 22 structure baselines.
