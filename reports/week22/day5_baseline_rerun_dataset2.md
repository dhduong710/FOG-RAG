# Week 22 Day 5 — PharmKG Dataset 2 Structure Baselines

## Protocol

- Dataset: PharmKG-8k task-specific benchmark
- Task: `(?, T, disease)`
- Relation normalized: `therapeutic_association_proxy`
- Candidate universe: `drug_only_from_train_T_heads`
- Top-K: 20
- Gold injection: false
- RR policy: RR = 1/rank if gold appears in top-20, else 0
- Absent rank sentinel: 21

## Validation metrics

| Model | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | H@20 | Avg rank | Rank21 | Unique top1 | Top1 dominance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| distmult | 0.104 | 0.019548 | 0.008 | 0.018 | 0.038 | 0.104 | 19.962 | 448 | 138 | 0.038 |
| complex | 0.050 | 0.005814 | 0.000 | 0.004 | 0.018 | 0.050 | 20.556 | 475 | 166 | 0.034 |
| transe | 0.042 | 0.005302 | 0.000 | 0.000 | 0.022 | 0.042 | 20.556 | 479 | 144 | 0.104 |
| rotate | 0.022 | 0.002318 | 0.000 | 0.000 | 0.006 | 0.022 | 20.810 | 489 | 211 | 0.032 |

## Test metrics

| Model | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | H@20 | Avg rank | Rank21 | Unique top1 | Top1 dominance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| distmult | 0.102 | 0.016576 | 0.006 | 0.012 | 0.038 | 0.102 | 20.078 | 449 | 138 | 0.036 |
| transe | 0.060 | 0.009319 | 0.002 | 0.008 | 0.028 | 0.060 | 20.466 | 470 | 148 | 0.082 |
| complex | 0.066 | 0.009066 | 0.000 | 0.008 | 0.036 | 0.066 | 20.320 | 467 | 154 | 0.032 |
| rotate | 0.024 | 0.001900 | 0.000 | 0.000 | 0.004 | 0.024 | 20.824 | 488 | 199 | 0.030 |

## Notes

This script currently trains TransE, DistMult, ComplEx, and RotatE.
R-GCN and HRGAT should be exported with the same JSON schema if using the exact Week21 implementations.

## Files written

- `results/week22/dataset2_baseline_reviewer_safe_valid.json`
- `results/week22/dataset2_baseline_reviewer_safe_test.json`
- `results/week22/dataset2_baseline_main_table.json`
- `reports/week22/day5_baseline_rerun_dataset2.md`
