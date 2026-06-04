# Week 21 Day 4 — Reviewer-safe Metric Recompute

## Decision

**DAY4_REVIEWER_SAFE_METRICS_RECOMPUTED_READY_FOR_MAIN_TABLE**

## Frozen metric rule

- `RR = 1/rank if rank <= 20 else 0`
- Gold absent from top-20 uses descriptive rank `21`
- RR for absent gold is `0`
- No `1/21`
- No gold injection

## Best rows after recomputation

| Split | Best row | Family | MRR@20 | Gold@20 | Hits@10 |
|---|---|---|---:|---:|---:|
| valid | `complex` | `structure_baseline` | 0.117044 | 0.5600 | 0.3540 |
| test | `soft_support_fuzzy_retrieval_main` | `fograg` | 0.125326 | 0.2400 | 0.2220 |

## Valid split — all rows

| Row | Family | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Avg rank | Rank21 | Top1 uniq |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `complex` | `structure_baseline` | 0.5600 | 0.117044 | 0.0360 | 0.1020 | 0.3540 | 14.176 | 220 | 101 |
| `soft_support_fuzzy_retrieval_main` | `fograg` | 0.2020 | 0.097644 | 0.0560 | 0.1340 | 0.1820 | 17.676 | 399 | 11 |
| `soft_support_raw` | `fograg` | 0.2020 | 0.097644 | 0.0560 | 0.1340 | 0.1820 | 17.676 | 399 | 11 |
| `distmult` | `structure_baseline` | 0.3540 | 0.074080 | 0.0180 | 0.0680 | 0.2240 | 16.680 | 323 | 47 |
| `backbone_raw` | `fograg` | 0.2020 | 0.053803 | 0.0240 | 0.0460 | 0.1580 | 18.376 | 399 | 3 |
| `rgcn` | `structure_baseline` | 0.1620 | 0.052191 | 0.0260 | 0.0540 | 0.1400 | 18.590 | 419 | 1 |
| `rotate` | `structure_baseline` | 0.1380 | 0.032682 | 0.0100 | 0.0340 | 0.0900 | 19.352 | 431 | 155 |
| `hrgat` | `structure_baseline` | 0.1640 | 0.029981 | 0.0040 | 0.0340 | 0.1200 | 18.926 | 418 | 6 |
| `transe` | `structure_baseline` | 0.1040 | 0.023681 | 0.0100 | 0.0220 | 0.0500 | 19.824 | 448 | 173 |

## Test split — all rows

| Row | Family | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Avg rank | Rank21 | Top1 uniq |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `soft_support_fuzzy_retrieval_main` | `fograg` | 0.2400 | 0.125326 | 0.0720 | 0.1660 | 0.2220 | 16.804 | 380 | 10 |
| `soft_support_raw` | `fograg` | 0.2400 | 0.125326 | 0.0720 | 0.1660 | 0.2220 | 16.804 | 380 | 10 |
| `complex` | `structure_baseline` | 0.5740 | 0.124731 | 0.0320 | 0.1180 | 0.3840 | 13.784 | 213 | 92 |
| `distmult` | `structure_baseline` | 0.4340 | 0.089091 | 0.0280 | 0.0740 | 0.2640 | 15.916 | 283 | 51 |
| `backbone_raw` | `fograg` | 0.2400 | 0.064563 | 0.0240 | 0.0700 | 0.1920 | 17.652 | 380 | 3 |
| `rgcn` | `structure_baseline` | 0.2200 | 0.059713 | 0.0180 | 0.0680 | 0.1860 | 17.854 | 390 | 1 |
| `hrgat` | `structure_baseline` | 0.2120 | 0.033064 | 0.0020 | 0.0280 | 0.1280 | 18.590 | 394 | 7 |
| `rotate` | `structure_baseline` | 0.1340 | 0.032958 | 0.0140 | 0.0360 | 0.0740 | 19.436 | 433 | 153 |
| `transe` | `structure_baseline` | 0.1040 | 0.022207 | 0.0020 | 0.0240 | 0.0720 | 19.642 | 448 | 174 |

## Query-set checks

All rows should have `same_query_set_as_raw_source = true`.

### Valid

- `complex`: `True`
- `soft_support_fuzzy_retrieval_main`: `True`
- `soft_support_raw`: `True`
- `distmult`: `True`
- `backbone_raw`: `True`
- `rgcn`: `True`
- `rotate`: `True`
- `hrgat`: `True`
- `transe`: `True`

### Test

- `soft_support_fuzzy_retrieval_main`: `True`
- `soft_support_raw`: `True`
- `complex`: `True`
- `distmult`: `True`
- `backbone_raw`: `True`
- `rgcn`: `True`
- `hrgat`: `True`
- `rotate`: `True`
- `transe`: `True`

## Absent-RR checks

All rows should have `absent_rr_check_pass = true`.

### Valid

- `complex`: `True`
- `soft_support_fuzzy_retrieval_main`: `True`
- `soft_support_raw`: `True`
- `distmult`: `True`
- `backbone_raw`: `True`
- `rgcn`: `True`
- `rotate`: `True`
- `hrgat`: `True`
- `transe`: `True`

### Test

- `soft_support_fuzzy_retrieval_main`: `True`
- `soft_support_raw`: `True`
- `complex`: `True`
- `distmult`: `True`
- `backbone_raw`: `True`
- `rgcn`: `True`
- `hrgat`: `True`
- `rotate`: `True`
- `transe`: `True`

## Interpretation note for Day 5

Day 5 should build the final baseline comparison table and decide paper positioning:

- If FOG-RAG main remains best among DrKGC-compatible rows but not best among pure structure candidate generators, frame structure baselines as stronger upstream candidates and FOG-RAG as evidence-aware refinement of the DrKGC-compatible pipeline.
- If a baseline such as ComplEx is clearly stronger as a candidate generator, consider adding a future/appendix branch: `ComplEx-source + FOG-RAG soft/retrieval`.
- Do not change the paper main row before Day 5 interpretation.
