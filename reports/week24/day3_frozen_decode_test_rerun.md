# Week 24 Day 3 — Frozen Decoding Valid/Test Rerun

## Decision

**PRIMEKG_FROZEN_DECODE_E2E_READY**

## Frozen config

```json
{
  "decision": "PRIMEKG_DECODING_CONFIG_FROZEN_FROM_VALID",
  "best_config": {
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
  },
  "use_for_day3": {
    "max_new_tokens": 16,
    "repetition_penalty": 1.0,
    "no_repeat_ngram_size": 0,
    "do_sample": false,
    "num_beams": 1,
    "temperature": 1.0
  },
  "important_note": "Selected on valid only. Do not change after looking at test."
}
```

## Reviewer-safe final table

| Split | Row | Gold@20 | Cand MRR | E2E MRR | E2E H@1 | E2E H@3 | E2E H@10 | Pred-in-cand | Invalid | Top1-copy | List-frag | Avg subgraph |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| valid | backbone_raw | 0.202 | 0.053803 | 0.048118 | 0.012 | 0.048 | 0.150 | 0.974 | 0.026 | 0.022 | 0.024 | 60.450 |
| valid | soft_support_raw | 0.202 | 0.097644 | 0.059944 | 0.002 | 0.102 | 0.172 | 0.964 | 0.036 | 0.002 | 0.012 | 60.450 |
| valid | retrieval_main | 0.202 | 0.097644 | 0.058518 | 0.000 | 0.100 | 0.174 | 0.992 | 0.008 | 0.008 | 0.010 | 32.556 |
| test | backbone_raw | 0.240 | 0.064563 | 0.047636 | 0.002 | 0.048 | 0.178 | 0.980 | 0.020 | 0.038 | 0.046 | 59.932 |
| test | soft_support_raw | 0.240 | 0.125326 | 0.074676 | 0.000 | 0.132 | 0.218 | 0.980 | 0.020 | 0.008 | 0.010 | 59.932 |
| test | retrieval_main | 0.240 | 0.125326 | 0.074687 | 0.000 | 0.132 | 0.218 | 0.998 | 0.002 | 0.010 | 0.010 | 32.340 |

## Week20 vs Week24 test comparison

| Row | Week20 E2E MRR | Week24 E2E MRR | Delta |
|---|---:|---:|---:|
| backbone_raw | 0.047636 | 0.047636 | 0.000000 |
| soft_support_raw | 0.074676 | 0.074676 | 0.000000 |
| retrieval_main | 0.074687 | 0.074687 | 0.000000 |

## Checks

- `soft_improves_backbone_test_e2e`: `True`
- `retrieval_preserves_or_improves_soft_test_e2e`: `True`
- `retrieval_smaller_than_soft`: `True`
- `retrieval_candidate_coverage_preserved`: `True`

## Notes

- Metrics are reviewer-safe recomputation from prediction rows.
- Raw `infer.py` MRR is audit-only.
- This config was selected on valid only in Day 2.
- If Week24 equals Week20, this confirms the original decoding config was already optimal under the valid sweep.