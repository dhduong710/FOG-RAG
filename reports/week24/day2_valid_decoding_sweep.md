# Week 24 Day 2 — PrimeKG Valid Decoding Sweep

## Decision

**PRIMEKG_DECODING_CONFIG_FROZEN_FROM_VALID**

## Best config

```json
{
  "config_id": "cfg01_mnt16_rp100_ng0",
  "max_new_tokens": 16,
  "repetition_penalty": 1.0,
  "no_repeat_ngram_size": 0,
  "retrieval_main_valid_mrr": 0.05851818,
  "retrieval_main_invalid": 0.008,
  "retrieval_main_pred_in_candidate": 0.992,
  "avg_valid_mrr_all_rows": 0.05552675,
  "avg_invalid_all_rows": 0.02333333,
  "avg_pred_in_candidate_all_rows": 0.97666667
}
```

## Config rollup ranked

| Rank | Config | max_new_tokens | repetition_penalty | no_repeat_ngram_size | retrieval MRR | retrieval invalid | retrieval pred-in-cand | avg MRR |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | cfg01_mnt16_rp100_ng0 | 16 | 1.0 | 0 | 0.058518 | 0.008 | 0.992 | 0.055527 |
| 2 | cfg02_mnt16_rp105_ng0 | 16 | 1.05 | 0 | 0.058518 | 0.008 | 0.992 | 0.055527 |
| 3 | cfg03_mnt16_rp110_ng0 | 16 | 1.1 | 0 | 0.058518 | 0.008 | 0.992 | 0.055527 |
| 4 | cfg04_mnt16_rp110_ng3 | 16 | 1.1 | 3 | 0.058518 | 0.008 | 0.992 | 0.055527 |
| 5 | cfg05_mnt24_rp100_ng0 | 24 | 1.0 | 0 | 0.058518 | 0.008 | 0.992 | 0.055527 |
| 6 | cfg06_mnt24_rp105_ng0 | 24 | 1.05 | 0 | 0.058518 | 0.008 | 0.992 | 0.055527 |
| 7 | cfg07_mnt24_rp110_ng0 | 24 | 1.1 | 0 | 0.058518 | 0.008 | 0.992 | 0.055527 |
| 8 | cfg08_mnt24_rp110_ng3 | 24 | 1.1 | 3 | 0.058518 | 0.008 | 0.992 | 0.055527 |

## Full row-level table

| Config | Row | MRR@20 | H@1 | H@3 | H@10 | Pred-in-cand | Invalid | Top1-copy | List-frag |
|---|---|---|---|---|---|---|---|---|---|
| cfg01_mnt16_rp100_ng0 | backbone_raw | 0.048118 | 0.012 | 0.048 | 0.150 | 0.974 | 0.026 | 0.022 | 0.024 |
| cfg01_mnt16_rp100_ng0 | soft_support_raw | 0.059944 | 0.002 | 0.102 | 0.172 | 0.964 | 0.036 | 0.002 | 0.012 |
| cfg01_mnt16_rp100_ng0 | retrieval_main | 0.058518 | 0.000 | 0.100 | 0.174 | 0.992 | 0.008 | 0.008 | 0.010 |
| cfg02_mnt16_rp105_ng0 | backbone_raw | 0.048118 | 0.012 | 0.048 | 0.150 | 0.974 | 0.026 | 0.022 | 0.024 |
| cfg02_mnt16_rp105_ng0 | soft_support_raw | 0.059944 | 0.002 | 0.102 | 0.172 | 0.964 | 0.036 | 0.002 | 0.012 |
| cfg02_mnt16_rp105_ng0 | retrieval_main | 0.058518 | 0.000 | 0.100 | 0.174 | 0.992 | 0.008 | 0.008 | 0.010 |
| cfg03_mnt16_rp110_ng0 | backbone_raw | 0.048118 | 0.012 | 0.048 | 0.150 | 0.974 | 0.026 | 0.022 | 0.024 |
| cfg03_mnt16_rp110_ng0 | soft_support_raw | 0.059944 | 0.002 | 0.102 | 0.172 | 0.964 | 0.036 | 0.002 | 0.012 |
| cfg03_mnt16_rp110_ng0 | retrieval_main | 0.058518 | 0.000 | 0.100 | 0.174 | 0.992 | 0.008 | 0.008 | 0.010 |
| cfg04_mnt16_rp110_ng3 | backbone_raw | 0.048118 | 0.012 | 0.048 | 0.150 | 0.974 | 0.026 | 0.022 | 0.024 |
| cfg04_mnt16_rp110_ng3 | soft_support_raw | 0.059944 | 0.002 | 0.102 | 0.172 | 0.964 | 0.036 | 0.002 | 0.012 |
| cfg04_mnt16_rp110_ng3 | retrieval_main | 0.058518 | 0.000 | 0.100 | 0.174 | 0.992 | 0.008 | 0.008 | 0.010 |
| cfg05_mnt24_rp100_ng0 | backbone_raw | 0.048118 | 0.012 | 0.048 | 0.150 | 0.974 | 0.026 | 0.022 | 0.024 |
| cfg05_mnt24_rp100_ng0 | soft_support_raw | 0.059944 | 0.002 | 0.102 | 0.172 | 0.964 | 0.036 | 0.002 | 0.012 |
| cfg05_mnt24_rp100_ng0 | retrieval_main | 0.058518 | 0.000 | 0.100 | 0.174 | 0.992 | 0.008 | 0.008 | 0.010 |
| cfg06_mnt24_rp105_ng0 | backbone_raw | 0.048118 | 0.012 | 0.048 | 0.150 | 0.974 | 0.026 | 0.022 | 0.024 |
| cfg06_mnt24_rp105_ng0 | soft_support_raw | 0.059944 | 0.002 | 0.102 | 0.172 | 0.964 | 0.036 | 0.002 | 0.012 |
| cfg06_mnt24_rp105_ng0 | retrieval_main | 0.058518 | 0.000 | 0.100 | 0.174 | 0.992 | 0.008 | 0.008 | 0.010 |
| cfg07_mnt24_rp110_ng0 | backbone_raw | 0.048118 | 0.012 | 0.048 | 0.150 | 0.974 | 0.026 | 0.022 | 0.024 |
| cfg07_mnt24_rp110_ng0 | soft_support_raw | 0.059944 | 0.002 | 0.102 | 0.172 | 0.964 | 0.036 | 0.002 | 0.012 |
| cfg07_mnt24_rp110_ng0 | retrieval_main | 0.058518 | 0.000 | 0.100 | 0.174 | 0.992 | 0.008 | 0.008 | 0.010 |
| cfg08_mnt24_rp110_ng3 | backbone_raw | 0.048118 | 0.012 | 0.048 | 0.150 | 0.974 | 0.026 | 0.022 | 0.024 |
| cfg08_mnt24_rp110_ng3 | soft_support_raw | 0.059944 | 0.002 | 0.102 | 0.172 | 0.964 | 0.036 | 0.002 | 0.012 |
| cfg08_mnt24_rp110_ng3 | retrieval_main | 0.058518 | 0.000 | 0.100 | 0.174 | 0.992 | 0.008 | 0.008 | 0.010 |

## Notes

- This sweep uses valid only.
- Raw `infer.py` MRR is ignored for selection.
- Day 3 must use the frozen config from `decoding_sweep_best_config.json`.
- If the best config is effectively the old config, keep it and report no decoding gain.