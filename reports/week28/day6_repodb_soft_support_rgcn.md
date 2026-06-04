# Week 28 Day 6  repoDB R-GCN soft support

- Decision: `DAY6_REPODB_SOFT_SUPPORT_READY`
- Selected variant: `soft_support_sweep_beta0.00_raw0.95`

## Raw vs selected

| Split | Row | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Rank21 | Top1Dom |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| valid | raw | 0.236 | 0.057024 | 0.026 | 0.048 | 0.144 | 382 | 0.528 |
| valid | soft | 0.236 | 0.057024 | 0.026 | 0.048 | 0.144 | 382 | 0.528 |
| test | raw | 0.214 | 0.048140 | 0.018 | 0.040 | 0.128 | 393 | 0.512 |
| test | soft | 0.214 | 0.048107 | 0.018 | 0.040 | 0.128 | 393 | 0.512 |

## Top valid variants

| Variant | beta | raw_weight | Valid MRR | Valid H@10 | Valid Top1Dom | Test MRR | Test H@10 | Test Top1Dom |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| soft_support_sweep_beta0.00_raw0.95 | 0.00 | 0.95 | 0.057024 | 0.144 | 0.528 | 0.048107 | 0.128 | 0.512 |
| soft_support_sweep_beta0.03_raw0.95 | 0.03 | 0.95 | 0.057024 | 0.144 | 0.528 | 0.048107 | 0.128 | 0.512 |
| soft_support_sweep_beta0.05_raw0.95 | 0.05 | 0.95 | 0.057024 | 0.144 | 0.528 | 0.048107 | 0.128 | 0.512 |
| soft_support_sweep_beta0.10_raw0.95 | 0.10 | 0.95 | 0.057024 | 0.144 | 0.528 | 0.048107 | 0.128 | 0.512 |
| soft_support_sweep_beta0.15_raw0.95 | 0.15 | 0.95 | 0.057024 | 0.144 | 0.528 | 0.048107 | 0.128 | 0.512 |
| soft_support_sweep_beta0.00_raw0.90 | 0.00 | 0.90 | 0.053892 | 0.142 | 0.532 | 0.045258 | 0.126 | 0.546 |
| soft_support_sweep_beta0.03_raw0.90 | 0.03 | 0.90 | 0.053892 | 0.142 | 0.532 | 0.045258 | 0.126 | 0.546 |
| soft_support_sweep_beta0.05_raw0.90 | 0.05 | 0.90 | 0.053892 | 0.142 | 0.532 | 0.045258 | 0.126 | 0.546 |
| soft_support_sweep_beta0.10_raw0.90 | 0.10 | 0.90 | 0.053892 | 0.142 | 0.532 | 0.045258 | 0.126 | 0.546 |
| soft_support_sweep_beta0.15_raw0.90 | 0.15 | 0.90 | 0.053892 | 0.142 | 0.532 | 0.045258 | 0.126 | 0.546 |
| soft_support_sweep_beta0.00_raw0.85 | 0.00 | 0.85 | 0.049792 | 0.140 | 0.520 | 0.041574 | 0.126 | 0.532 |
| soft_support_sweep_beta0.03_raw0.85 | 0.03 | 0.85 | 0.049792 | 0.140 | 0.520 | 0.041574 | 0.126 | 0.532 |
| soft_support_sweep_beta0.05_raw0.85 | 0.05 | 0.85 | 0.049792 | 0.140 | 0.520 | 0.041574 | 0.126 | 0.532 |
| soft_support_sweep_beta0.10_raw0.85 | 0.10 | 0.85 | 0.049792 | 0.140 | 0.520 | 0.041574 | 0.126 | 0.532 |
| soft_support_sweep_beta0.15_raw0.85 | 0.15 | 0.85 | 0.049792 | 0.140 | 0.520 | 0.041574 | 0.126 | 0.532 |
