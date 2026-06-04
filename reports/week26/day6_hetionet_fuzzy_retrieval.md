# Week 26 Day 6  Hetionet confidence-aware fuzzy retrieval

- Decision: `DAY6_HETIONET_FUZZY_RETRIEVAL_READY`
- Variant: `fuzzy_retrieval_main_hetionet`
- Candidate order: preserved from soft support

## Candidate metrics check

| Split | Soft MRR | Fuzzy MRR | Metrics preserved | Soft graph | Fuzzy graph | Reduction | Coverage preserved |
|---|---:|---:|---:|---:|---:|---:|---:|
| train | 0.098218 | 0.098218 | True | 80.00 | 44.00 | 0.450 | 1.000 |
| valid | 0.103369 | 0.103369 | True | 80.00 | 44.00 | 0.450 | 1.000 |
| test | 0.095439 | 0.095439 | True | 80.00 | 44.00 | 0.450 | 1.000 |

## Audit

| Split | Rows | Bad K | Bad prompt | Bad subgraph | Min graph | Max graph | Schema pass |
|---|---:|---:|---:|---:|---:|---:|---:|
| train | 555 | 0 | 0 | 0 | 44 | 44 | True |
| valid | 100 | 0 | 0 | 0 | 44 | 44 | True |
| test | 100 | 0 | 0 | 0 | 44 | 44 | True |

## Interpretation

- Day 6 should not change candidate metrics.
- The main gain is evidence efficiency: smaller selected subgraphs with candidate coverage preserved.
- Day 7 can train/infer Llama-3.2-3B on backbone_raw, soft_support_raw, and fuzzy_retrieval_main if compute allows.