# Week 26 Day 7 — Hetionet E2E closeout

- Decision: `DAY7_HETIONET_E2E_ALL_ROWS_READY`
- Model row count: `3`
- Rows: `backbone_raw`, `soft_support_raw`, `fuzzy_retrieval_main`

## Valid metrics

| Row | Cand MRR | E2E adj MRR | E2E H@1 | E2E H@3 | E2E H@10 | Pred-in-cand | Invalid | Avg graph |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| fuzzy_retrieval_main | 0.103369 | 0.130880 | 0.080 | 0.120 | 0.270 | 1.000 | 0.000 | 44.00 |
| soft_support_raw | 0.103369 | 0.119999 | 0.070 | 0.110 | 0.250 | 1.000 | 0.000 | 80.00 |
| backbone_raw | 0.057458 | 0.072037 | 0.030 | 0.060 | 0.190 | 1.000 | 0.000 | 80.00 |

## Test metrics

| Row | Cand MRR | E2E adj MRR | E2E H@1 | E2E H@3 | E2E H@10 | Pred-in-cand | Invalid | Avg graph |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| soft_support_raw | 0.095439 | 0.110927 | 0.030 | 0.130 | 0.280 | 1.000 | 0.000 | 80.00 |
| backbone_raw | 0.099445 | 0.104514 | 0.050 | 0.120 | 0.210 | 0.980 | 0.020 | 80.00 |
| fuzzy_retrieval_main | 0.095439 | 0.099142 | 0.020 | 0.110 | 0.280 | 1.000 | 0.000 | 44.00 |

## Notes

- Candidate metrics should match Day 5/Day 6 values.
- Fuzzy retrieval should preserve candidate metrics while reducing graph size from 80 to 44.
- Strict exact-match metrics are saved in JSON files for diagnostics.
