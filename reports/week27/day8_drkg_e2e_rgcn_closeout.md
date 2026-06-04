# Week 27 Day 8 — DRKG R-GCN E2E closeout

- Decision: `DAY8_DRKG_E2E_RGCN_ALL_ROWS_READY`
- Rows: `backbone_raw`, `soft_support_sweep`, `fuzzy_retrieval_main`
- Source family: `R-GCN consistency source`

## Valid metrics

| Row | Cand Gold@20 | Cand MRR | E2E adj MRR | E2E H@1 | E2E H@3 | E2E H@10 | Pred-in-cand | Invalid | Top1Dom | Avg graph |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| soft_support_sweep | 0.218 | 0.065191 | 0.079749 | 0.050 | 0.080 | 0.172 | 0.998 | 0.002 | 0.886 | 100.00 |
| fuzzy_retrieval_main | 0.218 | 0.065191 | 0.071746 | 0.038 | 0.074 | 0.170 | 1.000 | 0.000 | 0.886 | 55.00 |
| backbone_raw | 0.218 | 0.061404 | 0.063304 | 0.028 | 0.056 | 0.166 | 1.000 | 0.000 | 1.000 | 100.00 |

## Test metrics

| Row | Cand Gold@20 | Cand MRR | E2E adj MRR | E2E H@1 | E2E H@3 | E2E H@10 | Pred-in-cand | Invalid | Top1Dom | Avg graph |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fuzzy_retrieval_main | 0.200 | 0.046556 | 0.054915 | 0.024 | 0.054 | 0.140 | 1.000 | 0.000 | 0.878 | 55.00 |
| backbone_raw | 0.200 | 0.043242 | 0.052742 | 0.020 | 0.052 | 0.130 | 1.000 | 0.000 | 1.000 | 100.00 |
| soft_support_sweep | 0.200 | 0.046556 | 0.051379 | 0.022 | 0.052 | 0.134 | 0.998 | 0.002 | 0.878 | 100.00 |

## Interpretation guide

- DRKG is expected to be harder because R-GCN Gold@20 is only around 0.20–0.218.
- Soft-support sweep should be evaluated as a modest R-GCN-source improvement, not as a claim over DistMult.
- Fuzzy retrieval should preserve candidate metrics while reducing graph size from 100 to 55.
