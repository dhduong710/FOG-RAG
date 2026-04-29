# Week 23 Day 3 — Soft Support Transfer on PharmKG

## Decision

`SOFT_SUPPORT_TRANSFER_READY`

## Variant

- Variant name: `soft_support_pharmkg_b050`
- Formula: `support_score = 1.0*evidence_positive - 0.50*direct_T_candidate_query_flag - 0.10*contra_flag`
- Pruning: `false`
- Candidate size: `20`
- Gold injection: `false`

Because PharmKG uses compact relation codes and no explicit contraindication relation is used, `contra_flag = 0`.

## Main metrics

| Split | Gold@20 | MRR@20 | MRR present-only | H@1 | H@3 | H@10 | H@20 | Rank21 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| valid | 0.070 | 0.021307588490 | 0.304394121285 | 0.010 | 0.020 | 0.054 | 0.070 | 465 |
| test | 0.092 | 0.028159018759 | 0.306076290859 | 0.012 | 0.030 | 0.068 | 0.092 | 454 |

## Deltas vs backbone_raw

| Split | Delta Gold@20 | Delta MRR@20 | Delta H@1 | Delta H@3 | Delta H@10 |
|---|---:|---:|---:|---:|---:|
| valid | 0.000000 | 0.003461116747 | 0.000000 | 0.006000 | 0.020000 |
| test | 0.000000 | 0.007678248918 | 0.004000 | 0.010000 | 0.022000 |

## Change summary vs backbone

### Valid

- Improved rows: `24`
- Worsened rows: `0`
- Unchanged rows: `476`
- Raw gold-present rows: `35`
- Improved among gold-present: `24`
- Worsened among gold-present: `0`

### Test

- Improved rows: `33`
- Worsened rows: `0`
- Unchanged rows: `467`
- Raw gold-present rows: `46`
- Improved among gold-present: `33`
- Worsened among gold-present: `0`

## Interpretation

Soft support is a no-pruning candidate reordering step. Therefore, Gold@20 should stay identical to backbone_raw. Any metric change comes from rank movement among already-present gold candidates.

On PharmKG, the main available signal is the direct-T shortcut penalty, because evidence and shortest-path features are saturated after Day 2.

## Files written

- `dataset/setting_c_pharmkg/10_soft_support/valid_top20_soft_support_main.json`
- `dataset/setting_c_pharmkg/10_soft_support/test_top20_soft_support_main.json`
- `dataset/setting_c_pharmkg/10_soft_support/soft_support_config.json`
- `dataset/setting_c_pharmkg/10_soft_support/soft_support_debug_summary.json`
- `results/week23/soft_support_raw_eval_valid.json`
- `results/week23/soft_support_raw_eval_test.json`

## Next step

Day 4 will build fuzzy retrieval / confidence-aware subgraph selection.
