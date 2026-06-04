# Week 28 Day 7  repoDB fuzzy retrieval on R-GCN raw-display-control

- Decision: `DAY7_REPODB_FUZZY_RETRIEVAL_READY`
- Input: `dataset/setting_f_repodb/09_e2e_soft_support_ready/rgcn_raw_display_control`
- Output: `dataset/setting_f_repodb/11_e2e_fuzzy_retrieval_ready/rgcn`

## Candidate metrics and graph reduction

| Split | Raw MRR | Fuzzy MRR | Preserved | Source graph | Fuzzy graph | Reduction | Coverage | Direct source | Direct selected | Failed source | Failed selected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train | 0.083861 | 0.083861 | True | 100.00 | 55.00 | 0.450 | 1.000 | 3.06 | 2.54 | 0.02 | 0.01 |
| valid | 0.057024 | 0.057024 | True | 100.00 | 55.00 | 0.450 | 1.000 | 2.46 | 1.94 | 0.03 | 0.02 |
| test | 0.048140 | 0.048140 | True | 100.00 | 55.00 | 0.450 | 1.000 | 2.74 | 2.17 | 0.01 | 0.01 |

## Schema audit

| Split | Rows | Bad K | Bad prompt Q | Bad prompt E | Bad display | Leaks | Schema pass |
|---|---:|---:|---:|---:|---:|---:|---:|
| train | 5677 | 0 | 0 | 0 | 0 | 0 | True |
| valid | 500 | 0 | 0 | 0 | 0 | 0 | True |
| test | 500 | 0 | 0 | 0 | 0 | 0 | True |

## Interpretation

- Fuzzy retrieval preserves raw R-GCN candidate order.
- This is the main repoDB graph-efficiency row after Day 6 soft support failed to improve ranking.
- Day 8 should run E2E for raw-display-control and fuzzy_retrieval_main.
