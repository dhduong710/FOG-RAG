# Week 26 Day 3  Hetionet Structure Baselines

## Protocol

- Dataset: Hetionet v1.0
- Task: `(?, CtD, disease)`
- Relation normalized: `compound_treats_disease`
- Candidate universe: `Compound`
- Top-K: 20
- Gold injection: false
- RR policy: RR = 1/rank if gold appears in top-20, else 0
- Absent rank sentinel: 21

## Validation metrics

| Model | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | H@20 | Avg rank | Rank21 | Unique top1 | Top1 dominance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| complex | 0.400 | 0.075366 | 0.020 | 0.070 | 0.210 | 0.400 | 16.660 | 60 | 20 | 0.220 |
| transe | 0.370 | 0.074971 | 0.030 | 0.040 | 0.230 | 0.370 | 16.530 | 63 | 16 | 0.220 |
| distmult | 0.270 | 0.067917 | 0.020 | 0.060 | 0.200 | 0.270 | 17.440 | 73 | 9 | 0.560 |
| hrgat | 0.400 | 0.060458 | 0.010 | 0.040 | 0.220 | 0.400 | 16.600 | 60 | 1 | 1.000 |
| rgcn | 0.430 | 0.057458 | 0.010 | 0.040 | 0.190 | 0.430 | 17.020 | 57 | 1 | 1.000 |
| rotate | 0.190 | 0.040198 | 0.020 | 0.020 | 0.120 | 0.190 | 18.640 | 81 | 27 | 0.170 |

## Test metrics

| Model | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | H@20 | Avg rank | Rank21 | Unique top1 | Top1 dominance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| hrgat | 0.410 | 0.101304 | 0.040 | 0.080 | 0.290 | 0.410 | 15.460 | 59 | 1 | 1.000 |
| rgcn | 0.440 | 0.099445 | 0.040 | 0.110 | 0.220 | 0.440 | 16.410 | 56 | 1 | 1.000 |
| complex | 0.440 | 0.090303 | 0.020 | 0.100 | 0.250 | 0.440 | 15.850 | 56 | 24 | 0.130 |
| distmult | 0.390 | 0.071938 | 0.010 | 0.050 | 0.290 | 0.390 | 16.220 | 61 | 11 | 0.550 |
| transe | 0.270 | 0.045556 | 0.010 | 0.040 | 0.150 | 0.270 | 18.020 | 73 | 13 | 0.290 |
| rotate | 0.200 | 0.042597 | 0.010 | 0.040 | 0.120 | 0.200 | 18.620 | 80 | 29 | 0.170 |

## Notes

- GNN v2 uses target-balanced sampling for sparse CtD training.
- HRGAT uses chunked message passing to avoid full-batch edge-attention OOM.