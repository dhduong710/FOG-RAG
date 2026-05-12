# Week 28 Day 5  repoDB FOG-RAG-ready packages

- Decision: `DAY5_REPODB_FOGRAG_READY`
- Main source: `rgcn`
- Diagnostic source: `distmult`

## Source: `rgcn`

- Decision: `DAY5_REPODB_FOGRAG_READY`
- graph_num_rels: `63`
- embedding source: `dataset/setting_f_repodb/04_baseline_outputs/rgcn/entity_embeddings_rgcn.pt`

| Split | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Rank21 | Top1Dom | Avg graph | Schema pass |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train | 1.000 | 0.083861 | 0.015 | 0.042 | 0.120 | 0 | 1.000 | 100.00 | True |
| valid | 0.236 | 0.057024 | 0.026 | 0.048 | 0.144 | 382 | 0.528 | 100.00 | True |
| test | 0.214 | 0.048140 | 0.018 | 0.040 | 0.128 | 393 | 0.512 | 100.00 | True |

## Source: `distmult`

- Decision: `DAY5_REPODB_FOGRAG_READY`
- graph_num_rels: `63`
- embedding source: `dataset/setting_f_repodb/04_baseline_outputs/rgcn/entity_embeddings_rgcn.pt`

| Split | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Rank21 | Top1Dom | Avg graph | Schema pass |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train | 1.000 | 0.074601 | 0.007 | 0.032 | 0.095 | 0 | 1.000 | 100.00 | True |
| valid | 0.510 | 0.101277 | 0.016 | 0.094 | 0.362 | 245 | 0.134 | 99.96 | True |
| test | 0.482 | 0.104139 | 0.026 | 0.094 | 0.320 | 259 | 0.146 | 99.98 | True |

## Interpretation

- R-GCN is the main DrKGC/SoftFuse consistency source.
- DistMult remains the strongest standalone structure-only comparator.
- Day 6 should run support features and soft support on R-GCN first.
