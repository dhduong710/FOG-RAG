# Week 24 Extension Day 6B — PharmKG Valid Decoding Sweep

## Decision

**PHARMKG_DECODING_CONFIG_FROZEN_FROM_VALID**

## Best config

```json
{
  "config_id": "cfg02_mnt16_rp105_ng0",
  "max_new_tokens": 16,
  "repetition_penalty": 1.05,
  "no_repeat_ngram_size": 0,
  "fuzzy_valid_mrr": 0.01718446,
  "fuzzy_invalid": 0.624,
  "fuzzy_pred_in_candidate": 0.376,
  "fuzzy_top1_copy": 0.376,
  "fuzzy_list_fragment": 0.618,
  "avg_valid_mrr_all_rows": 0.01658118,
  "avg_invalid_all_rows": 0.58,
  "avg_pred_in_candidate_all_rows": 0.42,
  "avg_top1_copy_all_rows": 0.42,
  "avg_list_fragment_all_rows": 0.57533333,
  "top1_collapsed": false
}
```

## Ranked configs

| Rank | Config | max_new | rep penalty | ngram | fuzzy MRR | invalid | pred-in-cand | top1-copy | list-frag | avg MRR | top1 collapsed |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | cfg02_mnt16_rp105_ng0 | 16 | 1.05 | 0 | 0.017184 | 0.624 | 0.376 | 0.376 | 0.618 | 0.016581 | False |
| 2 | cfg03_mnt16_rp110_ng0 | 16 | 1.1 | 0 | 0.017184 | 0.624 | 0.376 | 0.376 | 0.618 | 0.016581 | False |
| 3 | cfg04_mnt16_rp110_ng3 | 16 | 1.1 | 3 | 0.017184 | 0.624 | 0.376 | 0.376 | 0.618 | 0.016581 | False |
| 4 | cfg06_mnt24_rp105_ng0 | 24 | 1.05 | 0 | 0.017184 | 0.624 | 0.376 | 0.376 | 0.618 | 0.016581 | False |
| 5 | cfg07_mnt24_rp110_ng0 | 24 | 1.1 | 0 | 0.017184 | 0.624 | 0.376 | 0.376 | 0.618 | 0.016581 | False |
| 6 | cfg08_mnt24_rp110_ng3 | 24 | 1.1 | 3 | 0.017184 | 0.624 | 0.376 | 0.376 | 0.618 | 0.016581 | False |
| 7 | cfg01_mnt16_rp100_ng0 | 16 | 1.0 | 0 | 0.017184 | 0.624 | 0.376 | 0.376 | 0.624 | 0.016581 | False |
| 8 | cfg05_mnt24_rp100_ng0 | 24 | 1.0 | 0 | 0.017184 | 0.624 | 0.376 | 0.376 | 0.624 | 0.016581 | False |

## Full row-level table

| Config | Row | Gold@20 | Cand MRR | E2E MRR | H@1 | H@3 | H@10 | Pred-in-cand | Invalid | Top1-copy | List-frag |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cfg01_mnt16_rp100_ng0 | backbone_raw | 0.070 | 0.017846 | 0.015402 | 0.006 | 0.014 | 0.034 | 0.524 | 0.476 | 0.524 | 0.474 |
| cfg01_mnt16_rp100_ng0 | soft_support_raw | 0.070 | 0.021308 | 0.017157 | 0.004 | 0.020 | 0.052 | 0.360 | 0.640 | 0.360 | 0.640 |
| cfg01_mnt16_rp100_ng0 | fuzzy_retrieval_main | 0.070 | 0.021308 | 0.017184 | 0.004 | 0.020 | 0.052 | 0.376 | 0.624 | 0.376 | 0.624 |
| cfg02_mnt16_rp105_ng0 | backbone_raw | 0.070 | 0.017846 | 0.015402 | 0.006 | 0.014 | 0.034 | 0.524 | 0.476 | 0.524 | 0.474 |
| cfg02_mnt16_rp105_ng0 | soft_support_raw | 0.070 | 0.021308 | 0.017157 | 0.004 | 0.020 | 0.052 | 0.360 | 0.640 | 0.360 | 0.634 |
| cfg02_mnt16_rp105_ng0 | fuzzy_retrieval_main | 0.070 | 0.021308 | 0.017184 | 0.004 | 0.020 | 0.052 | 0.376 | 0.624 | 0.376 | 0.618 |
| cfg03_mnt16_rp110_ng0 | backbone_raw | 0.070 | 0.017846 | 0.015402 | 0.006 | 0.014 | 0.034 | 0.524 | 0.476 | 0.524 | 0.474 |
| cfg03_mnt16_rp110_ng0 | soft_support_raw | 0.070 | 0.021308 | 0.017157 | 0.004 | 0.020 | 0.052 | 0.360 | 0.640 | 0.360 | 0.616 |
| cfg03_mnt16_rp110_ng0 | fuzzy_retrieval_main | 0.070 | 0.021308 | 0.017184 | 0.004 | 0.020 | 0.052 | 0.376 | 0.624 | 0.376 | 0.618 |
| cfg04_mnt16_rp110_ng3 | backbone_raw | 0.070 | 0.017846 | 0.015402 | 0.006 | 0.014 | 0.034 | 0.524 | 0.476 | 0.524 | 0.474 |
| cfg04_mnt16_rp110_ng3 | soft_support_raw | 0.070 | 0.021308 | 0.017157 | 0.004 | 0.020 | 0.052 | 0.360 | 0.640 | 0.360 | 0.616 |
| cfg04_mnt16_rp110_ng3 | fuzzy_retrieval_main | 0.070 | 0.021308 | 0.017184 | 0.004 | 0.020 | 0.052 | 0.376 | 0.624 | 0.376 | 0.618 |
| cfg05_mnt24_rp100_ng0 | backbone_raw | 0.070 | 0.017846 | 0.015402 | 0.006 | 0.014 | 0.034 | 0.524 | 0.476 | 0.524 | 0.474 |
| cfg05_mnt24_rp100_ng0 | soft_support_raw | 0.070 | 0.021308 | 0.017157 | 0.004 | 0.020 | 0.052 | 0.360 | 0.640 | 0.360 | 0.640 |
| cfg05_mnt24_rp100_ng0 | fuzzy_retrieval_main | 0.070 | 0.021308 | 0.017184 | 0.004 | 0.020 | 0.052 | 0.376 | 0.624 | 0.376 | 0.624 |
| cfg06_mnt24_rp105_ng0 | backbone_raw | 0.070 | 0.017846 | 0.015402 | 0.006 | 0.014 | 0.034 | 0.524 | 0.476 | 0.524 | 0.474 |
| cfg06_mnt24_rp105_ng0 | soft_support_raw | 0.070 | 0.021308 | 0.017157 | 0.004 | 0.020 | 0.052 | 0.360 | 0.640 | 0.360 | 0.634 |
| cfg06_mnt24_rp105_ng0 | fuzzy_retrieval_main | 0.070 | 0.021308 | 0.017184 | 0.004 | 0.020 | 0.052 | 0.376 | 0.624 | 0.376 | 0.618 |
| cfg07_mnt24_rp110_ng0 | backbone_raw | 0.070 | 0.017846 | 0.015402 | 0.006 | 0.014 | 0.034 | 0.524 | 0.476 | 0.524 | 0.474 |
| cfg07_mnt24_rp110_ng0 | soft_support_raw | 0.070 | 0.021308 | 0.017157 | 0.004 | 0.020 | 0.052 | 0.360 | 0.640 | 0.360 | 0.616 |
| cfg07_mnt24_rp110_ng0 | fuzzy_retrieval_main | 0.070 | 0.021308 | 0.017184 | 0.004 | 0.020 | 0.052 | 0.376 | 0.624 | 0.376 | 0.618 |
| cfg08_mnt24_rp110_ng3 | backbone_raw | 0.070 | 0.017846 | 0.015402 | 0.006 | 0.014 | 0.034 | 0.524 | 0.476 | 0.524 | 0.474 |
| cfg08_mnt24_rp110_ng3 | soft_support_raw | 0.070 | 0.021308 | 0.017157 | 0.004 | 0.020 | 0.052 | 0.360 | 0.640 | 0.360 | 0.616 |
| cfg08_mnt24_rp110_ng3 | fuzzy_retrieval_main | 0.070 | 0.021308 | 0.017184 | 0.004 | 0.020 | 0.052 | 0.376 | 0.624 | 0.376 | 0.618 |

## Notes

- This sweep uses PharmKG valid only.
- Test split is not used for selection.
- Raw `infer.py` metrics are ignored for paper-facing selection.
- `top1_copy_rate >= 0.90` is treated as top-1-copy collapse diagnostic.