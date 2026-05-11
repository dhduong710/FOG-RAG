# Week 27 Day 6  DRKG soft support (rgcn)

- Decision: `DAY6_DRKG_SOFT_SUPPORT_READY`
- Source: `rgcn`
- Variant: `soft_support_b050_drkg_rgcn_main`

## Raw vs soft metrics

| Split | Row | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Rank21 | Top1Dom |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| train | raw | 1.000 | 0.080565 | 0.013 | 0.039 | 0.103 | 0 | 1.000 |
| train | soft | 1.000 | 0.106025 | 0.023 | 0.065 | 0.229 | 0 | 0.335 |
| valid | raw | 0.218 | 0.061404 | 0.026 | 0.054 | 0.164 | 391 | 1.000 |
| valid | soft | 0.218 | 0.041900 | 0.012 | 0.040 | 0.130 | 391 | 0.320 |
| test | raw | 0.200 | 0.043242 | 0.010 | 0.042 | 0.120 | 400 | 1.000 |
| test | soft | 0.200 | 0.039818 | 0.016 | 0.028 | 0.120 | 400 | 0.324 |

## Change summary

| Split | Improved | Worsened | Unchanged | Improved rate | Worsened rate |
|---|---:|---:|---:|---:|---:|
| train | 1547 | 441 | 1980 | 0.390 | 0.111 |
| valid | 32 | 67 | 401 | 0.064 | 0.134 |
| test | 37 | 55 | 408 | 0.074 | 0.110 |

## E2E package audit

| Split | Rows | Bad K | Bad prompt | Bad subgraph | Avg graph | Schema pass |
|---|---:|---:|---:|---:|---:|---:|
| train | 3968 | 0 | 0 | 0 | 100.00 | True |
| valid | 500 | 0 | 0 | 0 | 100.00 | True |
| test | 500 | 0 | 0 | 0 | 100.00 | True |