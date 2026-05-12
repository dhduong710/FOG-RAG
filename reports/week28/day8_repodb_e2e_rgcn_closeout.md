# Week 28 Day 8 — repoDB R-GCN E2E closeout

- Decision: `DAY8_REPODB_E2E_ALL_ROWS_READY`
- Dataset: `repoDB`
- Task: `(?, repoDB_approved_indication, disease)`
- Rows: `backbone_raw`, `soft_support_sweep`, `fuzzy_retrieval_main`

## Valid metrics

| Row | Cand Gold@20 | Cand MRR | E2E MRR | E2E H@1 | E2E H@3 | E2E H@10 | Pred-in-cand | Invalid | Exact match | Top1Dom | Avg graph |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fuzzy_retrieval_main | 0.236 | 0.057024 | 0.058823 | 0.030 | 0.050 | 0.140 | 1.000 | 0.000 | 0.004 | 0.528 | 55.00 |
| backbone_raw | 0.236 | 0.057024 | 0.058745 | 0.030 | 0.050 | 0.140 | 0.998 | 0.002 | 0.004 | 0.528 | 100.00 |
| soft_support_sweep | 0.236 | 0.057024 | 0.058420 | 0.030 | 0.050 | 0.140 | 1.000 | 0.000 | 0.004 | 0.528 | 100.00 |

## Test metrics

| Row | Cand Gold@20 | Cand MRR | E2E MRR | E2E H@1 | E2E H@3 | E2E H@10 | Pred-in-cand | Invalid | Exact match | Top1Dom | Avg graph |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fuzzy_retrieval_main | 0.214 | 0.048140 | 0.052868 | 0.024 | 0.046 | 0.134 | 1.000 | 0.000 | 0.006 | 0.512 | 55.00 |
| soft_support_sweep | 0.214 | 0.048107 | 0.050868 | 0.022 | 0.042 | 0.132 | 1.000 | 0.000 | 0.006 | 0.512 | 100.00 |
| backbone_raw | 0.214 | 0.048140 | 0.048716 | 0.020 | 0.040 | 0.130 | 1.000 | 0.000 | 0.002 | 0.512 | 100.00 |

## Interpretation guide

- `backbone_raw` is the main R-GCN source with display-name patch.
- `soft_support_sweep` is a diagnostic row; Day 6 showed it did not improve repoDB ranking.
- `fuzzy_retrieval_main` is the graph-efficiency row: it preserves candidate metrics and reduces graph size from 100 to 55.
- DistMult remains the strongest standalone structure-only baseline and should be reported separately.
