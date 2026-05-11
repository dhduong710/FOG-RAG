# Week 26 Day 4  Hetionet FOG-RAG-ready package

- Decision: `DAY4_HETIONET_FOGRAG_READY`
- Source model: `rgcn`
- Target task: `(? , CtD, disease)`
- graph_num_rels: `24`
- R-GCN embedding shape: `[47031, 128]`

## Candidate metrics

| Split | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Rank21 | Top1 dominance |
|---|---:|---:|---:|---:|---:|---:|---:|
| train | 1.000 | 0.091649 | 0.022 | 0.049 | 0.132 | 0 | 1.000 |
| valid | 0.430 | 0.057458 | 0.010 | 0.040 | 0.190 | 57 | 1.000 |
| test | 0.440 | 0.099445 | 0.040 | 0.110 | 0.220 | 56 | 1.000 |

## Ready package audit

| Split | Rows | Bad K | Bad prompt | Avg graph | Min graph | Max graph | Leaks | Schema pass |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| train | 555 | 0 | 0 | 80.00 | 80 | 80 | 0 | True |
| valid | 100 | 0 | 0 | 80.00 | 80 | 80 | 0 | True |
| test | 100 | 0 | 0 | 80.00 | 80 | 80 | 0 | True |

## Notes

- R-GCN is retained as the main graph-compatible source despite top-1 collapse.
- Valid/test rows remain no-gold-injection.
- `train_gold_forced_into_candidates` only affects supervised train prompts when the observed train answer is absent from top-20.
- Day 5 should test whether soft-support can reduce top-1 collapse and improve early ranking.