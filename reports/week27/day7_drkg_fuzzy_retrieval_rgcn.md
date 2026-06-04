# Week 27 Day 7  DRKG fuzzy retrieval for R-GCN sweep-selected

- Decision: `DAY7_DRKG_FUZZY_RETRIEVAL_READY`
- Variant: `fuzzy_retrieval_main_drkg_rgcn`
- Candidate order: preserved from Day 6b soft-support sweep

## Candidate metrics and graph reduction

| Split | Soft MRR | Fuzzy MRR | Preserved | Source graph | Fuzzy graph | Reduction | Coverage | Direct source | Direct selected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train | 0.081540 | 0.081540 | True | 100.00 | 55.00 | 0.450 | 1.000 | 3.56 | 2.78 |
| valid | 0.065191 | 0.065191 | True | 100.00 | 55.00 | 0.450 | 1.000 | 2.95 | 2.13 |
| test | 0.046556 | 0.046556 | True | 100.00 | 55.00 | 0.450 | 1.000 | 2.51 | 1.82 |

## Schema audit

| Split | Rows | Bad K | Bad prompt | Bad subgraph | Min graph | Max graph | Schema pass |
|---|---:|---:|---:|---:|---:|---:|---:|
| train | 3968 | 0 | 0 | 0 | 55 | 55 | True |
| valid | 500 | 0 | 0 | 0 | 55 | 55 | True |
| test | 500 | 0 | 0 | 0 | 55 | 55 | True |

## Interpretation

- Fuzzy retrieval should preserve all candidate-stage metrics.
- The main value is graph efficiency before E2E LLM training/inference.
- Day 8 should run E2E for backbone_raw, soft_support_sweep, and fuzzy_retrieval_main.
