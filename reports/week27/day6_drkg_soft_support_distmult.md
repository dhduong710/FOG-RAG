# Week 27 Day 6  DRKG soft support (distmult)

- Decision: `DAY6_DRKG_SOFT_SUPPORT_READY`
- Source: `distmult`
- Variant: `soft_support_b050_drkg_distmult_diag`

## Raw vs soft metrics

| Split | Row | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Rank21 | Top1Dom |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| train | raw | 1.000 | 0.080341 | 0.014 | 0.040 | 0.100 | 0 | 1.000 |
| train | soft | 1.000 | 0.107723 | 0.021 | 0.064 | 0.247 | 0 | 0.278 |
| valid | raw | 0.444 | 0.102717 | 0.020 | 0.108 | 0.324 | 278 | 0.070 |
| valid | soft | 0.444 | 0.079734 | 0.020 | 0.070 | 0.232 | 278 | 0.050 |
| test | raw | 0.432 | 0.099675 | 0.034 | 0.092 | 0.276 | 284 | 0.074 |
| test | soft | 0.432 | 0.083184 | 0.026 | 0.070 | 0.236 | 284 | 0.042 |

## Change summary

| Split | Improved | Worsened | Unchanged | Improved rate | Worsened rate |
|---|---:|---:|---:|---:|---:|
| train | 1616 | 403 | 1949 | 0.407 | 0.102 |
| valid | 68 | 139 | 293 | 0.136 | 0.278 |
| test | 74 | 132 | 294 | 0.148 | 0.264 |

## E2E package audit

| Split | Rows | Bad K | Bad prompt | Bad subgraph | Avg graph | Schema pass |
|---|---:|---:|---:|---:|---:|---:|
| train | 3968 | 0 | 0 | 0 | 100.00 | True |
| valid | 500 | 0 | 0 | 0 | 100.00 | True |
| test | 500 | 0 | 0 | 0 | 100.00 | True |