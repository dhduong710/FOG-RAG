# Week 26 Day 3  repoDB Structure Baselines

## Protocol

- Dataset: repoDB
- Task: `(?, repoDB_approved_indication, disease)`
- Relation normalized: `repodb_approved_indication`
- Candidate universe: `Compound`
- Top-K: 20
- Gold injection: false
- RR policy: RR = 1/rank if gold appears in top-20, else 0
- Absent rank sentinel: 21

## Validation metrics

| Model | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | H@20 | Avg rank | Rank21 | Unique top1 | Top1 dominance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| distmult | 0.510 | 0.101277 | 0.016 | 0.094 | 0.362 | 0.510 | 14.512 | 245 | 142 | 0.134 |
| complex | 0.540 | 0.087644 | 0.004 | 0.064 | 0.350 | 0.540 | 14.610 | 230 | 141 | 0.106 |
| transe | 0.282 | 0.062313 | 0.024 | 0.062 | 0.152 | 0.282 | 17.760 | 359 | 91 | 0.242 |
| rgcn | 0.236 | 0.057024 | 0.026 | 0.048 | 0.144 | 0.236 | 18.184 | 382 | 2 | 0.528 |
| hrgat | 0.240 | 0.052105 | 0.016 | 0.050 | 0.150 | 0.240 | 18.076 | 380 | 8 | 0.452 |
| rotate | 0.198 | 0.022475 | 0.000 | 0.012 | 0.090 | 0.198 | 19.198 | 401 | 225 | 0.022 |

## Test metrics

| Model | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | H@20 | Avg rank | Rank21 | Unique top1 | Top1 dominance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| distmult | 0.482 | 0.104139 | 0.026 | 0.094 | 0.320 | 0.482 | 14.934 | 259 | 134 | 0.146 |
| complex | 0.502 | 0.083648 | 0.004 | 0.076 | 0.312 | 0.502 | 15.092 | 249 | 140 | 0.124 |
| transe | 0.248 | 0.052983 | 0.020 | 0.054 | 0.130 | 0.248 | 18.256 | 376 | 88 | 0.218 |
| hrgat | 0.222 | 0.052314 | 0.016 | 0.060 | 0.146 | 0.222 | 18.236 | 389 | 9 | 0.482 |
| rgcn | 0.214 | 0.048140 | 0.018 | 0.040 | 0.128 | 0.214 | 18.378 | 393 | 2 | 0.512 |
| rotate | 0.202 | 0.021712 | 0.000 | 0.002 | 0.100 | 0.202 | 19.016 | 399 | 209 | 0.026 |

## Notes

- GNN v2 uses target-balanced sampling for sparse repoDB::approved_indication::Compound:Disease training.
- HRGAT uses chunked message passing to avoid full-batch edge-attention OOM.