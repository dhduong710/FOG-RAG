# Week 27 Day 5  DRKG FOG-RAG-ready packages

- Decision: `DAY5_DRKG_FOGRAG_READY`
- Main source: `distmult`
- Diagnostic source: `rgcn`

## Source: `distmult`

- Decision: `DAY5_DRKG_FOGRAG_READY`
- graph_num_rels: `85`
- embedding source: `dataset/setting_e_drkg/04_baseline_outputs/rgcn/entity_embeddings_rgcn.pt`

| Split | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Rank21 | Top1Dom | Avg graph | Schema pass |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train | 1.000 | 0.080341 | 0.014 | 0.040 | 0.100 | 0 | 1.000 | 100.00 | True |
| valid | 0.444 | 0.102717 | 0.020 | 0.108 | 0.324 | 278 | 0.070 | 100.00 | True |
| test | 0.432 | 0.099675 | 0.034 | 0.092 | 0.276 | 284 | 0.074 | 100.00 | True |

## Source: `rgcn`

- Decision: `DAY5_DRKG_FOGRAG_READY`
- graph_num_rels: `85`
- embedding source: `dataset/setting_e_drkg/04_baseline_outputs/rgcn/entity_embeddings_rgcn.pt`

| Split | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Rank21 | Top1Dom | Avg graph | Schema pass |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train | 1.000 | 0.080565 | 0.013 | 0.039 | 0.103 | 0 | 1.000 | 100.00 | True |
| valid | 0.218 | 0.061404 | 0.026 | 0.054 | 0.164 | 391 | 1.000 | 100.00 | True |
| test | 0.200 | 0.043242 | 0.010 | 0.042 | 0.120 | 400 | 1.000 | 100.00 | True |

## Interpretation

- DistMult is the main DRKG source because it has the best validation/test MRR and low top-1 dominance.
- R-GCN is kept as a graph-compatible diagnostic source but should not be the main DRKG source due to low Gold@20 and top-1 collapse.
- Day 6 should apply soft support first to DistMult. R-GCN can be processed after DistMult as a diagnostic.
