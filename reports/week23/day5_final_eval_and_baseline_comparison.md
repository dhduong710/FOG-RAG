# Week 23 Day 5 — Final PharmKG Reviewer-Safe Evaluation and Baseline Comparison

## Decision

`DATASET2_FOGRAG_MAIN_TABLE_READY`

Candidate paper status:

`GO_PAPER_DATASET2_TRANSFER_RESULT`

## Protocol

- Dataset: PharmKG-8k
- Setting: `setting_c_pharmkg`
- Task: `(?, T, disease)`
- Relation label: `therapeutic_association_proxy`
- Candidate universe: `drug_only_from_train_T_heads`
- Top-K: 20
- Gold injection: false
- RR policy: RR = 1/rank if gold is present in top-20 else 0
- Absent rank sentinel: 21

## FOG-RAG transfer table — validation

| Row | Gold@20 | MRR@20 | MRR present-only | H@1 | H@3 | H@10 | H@20 | Rank21 | Avg subgraph |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Backbone raw | 0.070 | 0.017846 | 0.254950 | 0.010 | 0.014 | 0.034 | 0.070 | 465  100.00 |
| Hard support raw | 0.070 | 0.017846 | 0.254950 | 0.010 | 0.014 | 0.034 | 0.070 | 465  NA |
| Soft support raw | 0.070 | 0.021308 | 0.304394 | 0.010 | 0.020 | 0.054 | 0.070 | 465  100.00 |
| FOG-RAG main / fuzzy retrieval | 0.070 | 0.021308 | 0.304394 | 0.010 | 0.020 | 0.054 | 0.070 | 465  55.00 |

## FOG-RAG transfer table — test

| Row | Gold@20 | MRR@20 | MRR present-only | H@1 | H@3 | H@10 | H@20 | Rank21 | Avg subgraph |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Backbone raw | 0.092 | 0.020481 | 0.222617 | 0.008 | 0.020 | 0.046 | 0.092 | 454  100.00 |
| Hard support raw | 0.092 | 0.020481 | 0.222617 | 0.008 | 0.020 | 0.046 | 0.092 | 454  NA |
| Soft support raw | 0.092 | 0.028159 | 0.306076 | 0.012 | 0.030 | 0.068 | 0.092 | 454  100.00 |
| FOG-RAG main / fuzzy retrieval | 0.092 | 0.028159 | 0.306076 | 0.012 | 0.030 | 0.068 | 0.092 | 454  55.00 |

## Ranked comparison against structure baselines — validation

| Row | Gold@20 | MRR@20 | MRR present-only | H@1 | H@3 | H@10 | H@20 | Rank21 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Soft support raw | 0.070 | 0.021308 | 0.304394 | 0.010 | 0.020 | 0.054 | 0.070 | 465 |
| FOG-RAG main / fuzzy retrieval | 0.070 | 0.021308 | 0.304394 | 0.010 | 0.020 | 0.054 | 0.070 | 465 |
| DistMult | 0.104 | 0.019548 | 0.000000 | 0.008 | 0.018 | 0.038 | 0.104 | 448 |
| Backbone raw | 0.070 | 0.017846 | 0.254950 | 0.010 | 0.014 | 0.034 | 0.070 | 465 |
| Hard support raw | 0.070 | 0.017846 | 0.254950 | 0.010 | 0.014 | 0.034 | 0.070 | 465 |
| R-GCN | 0.070 | 0.017846 | 0.000000 | 0.010 | 0.014 | 0.034 | 0.070 | 465 |
| HRGAT | 0.060 | 0.013963 | 0.000000 | 0.006 | 0.016 | 0.032 | 0.060 | 470 |
| ComplEx | 0.050 | 0.005814 | 0.000000 | 0.000 | 0.004 | 0.018 | 0.050 | 475 |
| TransE | 0.042 | 0.005302 | 0.000000 | 0.000 | 0.000 | 0.022 | 0.042 | 479 |
| RotatE | 0.022 | 0.002318 | 0.000000 | 0.000 | 0.000 | 0.006 | 0.022 | 489 |

## Ranked comparison against structure baselines — test

| Row | Gold@20 | MRR@20 | MRR present-only | H@1 | H@3 | H@10 | H@20 | Rank21 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Soft support raw | 0.092 | 0.028159 | 0.306076 | 0.012 | 0.030 | 0.068 | 0.092 | 454 |
| FOG-RAG main / fuzzy retrieval | 0.092 | 0.028159 | 0.306076 | 0.012 | 0.030 | 0.068 | 0.092 | 454 |
| R-GCN | 0.092 | 0.020481 | 0.000000 | 0.008 | 0.020 | 0.046 | 0.092 | 454 |
| Backbone raw | 0.092 | 0.020481 | 0.222617 | 0.008 | 0.020 | 0.046 | 0.092 | 454 |
| Hard support raw | 0.092 | 0.020481 | 0.222617 | 0.008 | 0.020 | 0.046 | 0.092 | 454 |
| HRGAT | 0.094 | 0.018783 | 0.000000 | 0.010 | 0.014 | 0.044 | 0.094 | 453 |
| DistMult | 0.102 | 0.016576 | 0.000000 | 0.006 | 0.012 | 0.038 | 0.102 | 449 |
| TransE | 0.060 | 0.009319 | 0.000000 | 0.002 | 0.008 | 0.028 | 0.060 | 470 |
| ComplEx | 0.066 | 0.009066 | 0.000000 | 0.000 | 0.008 | 0.036 | 0.066 | 467 |
| RotatE | 0.024 | 0.001900 | 0.000000 | 0.000 | 0.000 | 0.004 | 0.024 | 488 |

## Key deltas

### FOG-RAG main vs R-GCN backbone

- valid MRR delta: `0.003461116747`
- test MRR delta: `0.007678248918`
- valid H@10 delta: `0.020000`
- test H@10 delta: `0.022000`

### FOG-RAG main vs best structure baseline

- valid best structure: `distmult`
- valid MRR delta: `0.001759791232`
- test best structure: `rgcn`
- test MRR delta: `0.007678248918`

## Main interpretation

On the PharmKG therapeutic-association proxy benchmark, frozen soft support improves R-GCN top-20 ranking without gold injection, and fuzzy retrieval preserves this gain while reducing the evidence subgraph from 100 to 55 triples.

## What to claim

- Soft support improves R-GCN ranking on PharmKG without valid/test gold injection.
- Fuzzy retrieval preserves soft-support ranking and compresses evidence from 100 to 55 triples.
- Under the task-specific reviewer-safe top-20 protocol, FOG-RAG main achieves the best MRR@20 on PharmKG.
- Gold@20 does not improve because FOG-RAG operates on fixed top-20 candidate lists.

## What not to claim

- Do not claim full-universe PharmKG KGC superiority.
- Do not call relation T a clinical indication relation.
- Do not claim fuzzy retrieval reduces shortcut rate on PharmKG; report evidence compression instead.
- Do not claim Gold@20/candidate recall improvement, because FOG-RAG reorders fixed top-20 candidates.

## Files written

- `dataset/setting_c_pharmkg/12_eval_rows/`
- `results/week23/dataset2_fograg_main_table_valid.json`
- `results/week23/dataset2_fograg_main_table_test.json`
- `results/week23/dataset2_vs_structure_baselines.json`
- `results/week23/dataset2_main_claim_summary.json`

## Next step

Day 6 will build diagnostics and failure analysis:
raw bottleneck, soft-support improvements, hard-support non-discrimination, and same-rank cleaner subgraphs.
