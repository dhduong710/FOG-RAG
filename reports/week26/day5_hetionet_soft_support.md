# Week 26 Day 5  Hetionet support features and soft support

- Decision: `DAY5_HETIONET_SOFT_SUPPORT_READY`
- Variant: `soft_support_b050_hetionet_main`
- Source: `R-GCN backbone_raw`

## Raw vs soft metrics

| Split | Row | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Rank21 | Top1 dominance |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| train | raw | 1.000 | 0.091649 | 0.022 | 0.049 | 0.132 | 0 | 1.000 |
| train | soft | 1.000 | 0.098218 | 0.011 | 0.034 | 0.202 | 0 | 0.450 |
| valid | raw | 0.430 | 0.057458 | 0.010 | 0.040 | 0.190 | 57 | 1.000 |
| valid | soft | 0.430 | 0.103369 | 0.050 | 0.090 | 0.240 | 57 | 0.430 |
| test | raw | 0.440 | 0.099445 | 0.040 | 0.110 | 0.220 | 56 | 1.000 |
| test | soft | 0.440 | 0.095439 | 0.010 | 0.110 | 0.280 | 56 | 0.370 |

## Change summary

| Split | Improved | Worsened | Unchanged | Improved rate | Worsened rate |
|---|---:|---:|---:|---:|---:|
| train | 357 | 80 | 118 | 0.643 | 0.144 |
| valid | 22 | 17 | 61 | 0.220 | 0.170 |
| test | 23 | 17 | 60 | 0.230 | 0.170 |

## E2E package audit

| Split | Rows | Bad K | Bad prompt | Bad subgraph | Avg graph | Schema pass |
|---|---:|---:|---:|---:|---:|---:|
| train | 555 | 0 | 0 | 0 | 80.00 | True |
| valid | 100 | 0 | 0 | 0 | 80.00 | True |
| test | 100 | 0 | 0 | 0 | 80.00 | True |

## Interpretation note

- Valid/test Gold@20 should remain unchanged because soft support does not add candidates.
- The main Day 5 success criterion is improved early rank and reduced top-1 dominance.
- If valid MRR drops strongly or top-1 dominance remains high, run a Day 5b penalty sweep before fuzzy retrieval.