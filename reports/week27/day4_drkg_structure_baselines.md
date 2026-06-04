# Week 26 Day 3  DRKG Structure Baselines

## Protocol

- Dataset: DRKG
- Task: `(?, DRUGBANK::treats, disease)`
- Relation normalized: `drugbank_treats`
- Candidate universe: `Compound`
- Top-K: 20
- Gold injection: false
- RR policy: RR = 1/rank if gold appears in top-20, else 0
- Absent rank sentinel: 21

## Validation metrics

| Model | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | H@20 | Avg rank | Rank21 | Unique top1 | Top1 dominance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| distmult | 0.444 | 0.102717 | 0.020 | 0.108 | 0.324 | 0.444 | 15.038 | 278 | 149 | 0.070 |
| complex | 0.460 | 0.081459 | 0.006 | 0.076 | 0.310 | 0.460 | 15.356 | 270 | 164 | 0.086 |
| hrgat | 0.228 | 0.066308 | 0.026 | 0.066 | 0.182 | 0.228 | 17.810 | 386 | 8 | 0.844 |
| transe | 0.296 | 0.061736 | 0.012 | 0.064 | 0.190 | 0.296 | 17.288 | 352 | 112 | 0.166 |
| rgcn | 0.218 | 0.061404 | 0.026 | 0.054 | 0.164 | 0.218 | 17.938 | 391 | 1 | 1.000 |
| rotate | 0.226 | 0.027579 | 0.000 | 0.008 | 0.126 | 0.226 | 18.612 | 387 | 225 | 0.052 |

## Test metrics

| Model | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | H@20 | Avg rank | Rank21 | Unique top1 | Top1 dominance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| distmult | 0.432 | 0.099675 | 0.034 | 0.092 | 0.276 | 0.432 | 15.652 | 284 | 147 | 0.074 |
| complex | 0.406 | 0.086269 | 0.024 | 0.070 | 0.260 | 0.406 | 15.978 | 297 | 169 | 0.066 |
| transe | 0.270 | 0.054830 | 0.020 | 0.040 | 0.160 | 0.270 | 17.936 | 365 | 119 | 0.154 |
| rgcn | 0.200 | 0.043242 | 0.010 | 0.042 | 0.120 | 0.200 | 18.510 | 400 | 1 | 1.000 |
| hrgat | 0.204 | 0.042223 | 0.010 | 0.046 | 0.134 | 0.204 | 18.484 | 398 | 9 | 0.872 |
| rotate | 0.182 | 0.023644 | 0.002 | 0.008 | 0.098 | 0.182 | 19.104 | 409 | 229 | 0.048 |

## Notes

- GNN v2 uses target-balanced sampling for sparse DRUGBANK::treats::Compound:Disease training.
- HRGAT uses chunked message passing to avoid full-batch edge-attention OOM.