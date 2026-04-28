# Week 21 Closeout — Baseline Rerun and Reviewer-safe Comparison

## Final decision

**WEEK21_BASELINE_FREEZE_GO_DATASET2**

## Overall status

- Overall pass: `True`
- Failed checks: `[]`

## Frozen protocol

- `task`: `(?, indication, disease)`
- `missing_entity`: `drug`
- `candidate_universe`: `drug_only`
- `top_k`: `20`
- `gold_injection`: `forbidden`
- `main_metric`: `reviewer_safe_mrr_at20`
- `rr_rule`: `RR = 1/rank if rank <= 20 else 0`
- `absent_rank_sentinel`: `21`
- `rr_absent_policy`: `0`

## What was completed this week

- Day 1: froze baseline-as-candidate-generator protocol.
- Day 2: audited old baseline artifacts.
- Day 3: reran all 6 structure baselines from scratch.
- Day 4: recomputed reviewer-safe metrics for baselines and FOG-RAG rows.
- Day 5: built paper-ready baseline table and positioning decision.
- Day 6: generated Results, Discussion, and reviewer-defense snippets.
- Day 7: froze Week 21 closeout and GO decision for Dataset 2.

## Baselines rerun

| Model | Valid Gold@20 | Test Gold@20 | Valid rows | Test rows |
|---|---:|---:|---:|---:|
| `transe` | 0.1040 | 0.1040 | 500 | 500 |
| `distmult` | 0.3540 | 0.4340 | 500 | 500 |
| `complex` | 0.5600 | 0.5740 | 500 | 500 |
| `rotate` | 0.1380 | 0.1340 | 500 | 500 |
| `rgcn` | 0.1620 | 0.2200 | 500 | 500 |
| `hrgat` | 0.1640 | 0.2120 | 500 | 500 |

## Locked-test headline numbers

| Row | Gold@20 | MRR@20 | H@1 | H@3 | H@10 |
|---|---:|---:|---:|---:|---:|
| `backbone_raw` | 0.2400 | 0.064563 | 0.0240 | 0.0700 | 0.1920 |
| `complex` | 0.5740 | 0.124731 | 0.0320 | 0.1180 | 0.3840 |
| `soft_support_raw` | 0.2400 | 0.125326 | 0.0720 | 0.1660 | 0.2220 |
| `fograg_main` | 0.2400 | 0.125326 | 0.0720 | 0.1660 | 0.2220 |

## Full valid table

| Method | Group | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Avg. rank |
|---|---|---:|---:|---:|---:|---:|---:|
| TransE | Structure baseline | 0.1040 | 0.023681 | 0.0100 | 0.0220 | 0.0500 | 19.824 |
| DistMult | Structure baseline | 0.3540 | 0.074080 | 0.0180 | 0.0680 | 0.2240 | 16.680 |
| ComplEx | Structure baseline | 0.5600 | 0.117044 | 0.0360 | 0.1020 | 0.3540 | 14.176 |
| RotatE | Structure baseline | 0.1380 | 0.032682 | 0.0100 | 0.0340 | 0.0900 | 19.352 |
| R-GCN | Structure baseline | 0.1620 | 0.052191 | 0.0260 | 0.0540 | 0.1400 | 18.590 |
| HRGAT | Structure baseline | 0.1640 | 0.029981 | 0.0040 | 0.0340 | 0.1200 | 18.926 |
| DrKGC-style backbone raw | DrKGC-compatible | 0.2020 | 0.053803 | 0.0240 | 0.0460 | 0.1580 | 18.376 |
| Soft support raw | FOG-RAG | 0.2020 | 0.097644 | 0.0560 | 0.1340 | 0.1820 | 17.676 |
| FOG-RAG main | FOG-RAG | 0.2020 | 0.097644 | 0.0560 | 0.1340 | 0.1820 | 17.676 |

## Full test table

| Method | Group | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Avg. rank |
|---|---|---:|---:|---:|---:|---:|---:|
| TransE | Structure baseline | 0.1040 | 0.022207 | 0.0020 | 0.0240 | 0.0720 | 19.642 |
| DistMult | Structure baseline | 0.4340 | 0.089091 | 0.0280 | 0.0740 | 0.2640 | 15.916 |
| ComplEx | Structure baseline | 0.5740 | 0.124731 | 0.0320 | 0.1180 | 0.3840 | 13.784 |
| RotatE | Structure baseline | 0.1340 | 0.032958 | 0.0140 | 0.0360 | 0.0740 | 19.436 |
| R-GCN | Structure baseline | 0.2200 | 0.059713 | 0.0180 | 0.0680 | 0.1860 | 17.854 |
| HRGAT | Structure baseline | 0.2120 | 0.033064 | 0.0020 | 0.0280 | 0.1280 | 18.590 |
| DrKGC-style backbone raw | DrKGC-compatible | 0.2400 | 0.064563 | 0.0240 | 0.0700 | 0.1920 | 17.652 |
| Soft support raw | FOG-RAG | 0.2400 | 0.125326 | 0.0720 | 0.1660 | 0.2220 | 16.804 |
| FOG-RAG main | FOG-RAG | 0.2400 | 0.125326 | 0.0720 | 0.1660 | 0.2220 | 16.804 |

## Main interpretation

FOG-RAG main achieves the highest locked-test reviewer-safe MRR@20, slightly above the strongest structure-only baseline, ComplEx. The margin is small, so the paper must not overclaim universal superiority. The strongest and safest claim is that FOG-RAG improves the DrKGC-compatible raw candidate source substantially and remains competitive with a strong structure-only candidate generator.

## Key deltas on locked test

- FOG-RAG main minus backbone raw MRR@20: +0.060763
- FOG-RAG main minus ComplEx MRR@20: +0.000595
- FOG-RAG main minus ComplEx Gold@20: -0.334
- ComplEx minus backbone raw MRR@20: +0.060168

## Graph-efficiency reminder

- Soft/backbone average subgraph size: 59.93
- Retrieval-main average subgraph size: 32.34
- Reduction: 27.59 triples/query
- Ranking gain is driven by soft support.
- Retrieval main preserves ranking and improves graph compactness/evidence quality.

## Claims allowed in paper

- FOG-RAG main achieves the highest locked-test reviewer-safe MRR@20.
- FOG-RAG substantially improves the DrKGC-compatible raw backbone.
- ComplEx demonstrates that stronger pure structure retrievers can provide higher coverage.
- Coverage and ranking quality are complementary.
- FOG-RAG's retrieval module improves graph compactness and evidence quality while preserving the ranking gain.

## Claims to avoid

- Do not claim FOG-RAG universally outperforms all structure baselines.
- Do not claim FOG-RAG has better Gold@20 than ComplEx.
- Do not claim fuzzy retrieval improves ranking beyond soft support.
- Do not hide the fact that ComplEx is better on validation MRR@20.
- Do not call the metric a classical full-ranking filtered KGC metric.

## Recommended paper stance

Table~\ref{tab:week21-baseline-main} reports the locked-test reviewer-safe comparison between six structure-only candidate generators and the DrKGC-compatible FOG-RAG rows. Among the structure baselines, ComplEx is the strongest candidate generator, reaching Gold@20 of 0.574 and MRR@20 of 0.124731. However, the selected FOG-RAG main row obtains the highest locked-test MRR@20, 0.125326, slightly above ComplEx by 0.000595. This result is notable because FOG-RAG main has substantially lower Gold@20 (0.240) than ComplEx, but achieves better early-rank placement with Hits@1 of 0.072 versus 0.032, and Hits@3 of 0.166 versus 0.118. Compared with the DrKGC-style raw backbone, FOG-RAG improves MRR@20 by 0.060763, Hits@1 by 0.048, and Hits@3 by 0.096.

## Reviewer-defense note

A reviewer may note that ComplEx achieves substantially higher Gold@20 than FOG-RAG main. We agree and report this explicitly. Our conclusion is not that FOG-RAG has better candidate coverage than ComplEx; it does not. Instead, under the frozen reviewer-safe top-20 protocol, FOG-RAG main achieves slightly higher locked-test MRR@20 because it places the gold drug earlier when it is present, as reflected by H@1=0.072 and H@3=0.166, compared with ComplEx H@1=0.032 and H@3=0.118. The result should therefore be interpreted as evidence that coverage and ordering are complementary. A stronger upstream generator such as ComplEx is a promising future candidate source for FOG-RAG, while the current contribution focuses on soft evidence modeling and confidence-aware retrieval within the DrKGC-compatible pipeline.

## Important artifacts

- `protocol`: `results/week21/baseline_protocol_freeze.json`
- `inventory`: `results/week21/baseline_inventory.json`
- `rerun_summary`: `results/week21/baseline_rerun_summary.json`
- `day4_metrics`: `results/week21/day4_reviewer_safe_metrics_all.json`
- `main_table_json`: `results/week21/baseline_main_table.json`
- `main_table_tex`: `results/week21/baseline_main_table.tex`
- `positioning_decision`: `results/week21/baseline_positioning_decision.json`
- `interpretation_assets`: `results/week21/baseline_interpretation_assets.json`
- `closeout_json`: `results/week21/week21_closeout.json`
- `go_decision`: `results/week21/week21_go_decision.json`
- `week21_closeout_md`: `reports/week21/week21_closeout.md`

## GO decision for next week

Proceed to **Week 22 — Dataset 2 setup and transfer**.

Recommended first step:

> Inventory and select Dataset 2, likely PharmKG, then define the same reviewer-safe top-20 candidate-generator protocol before running FOG-RAG stages.

Do not do yet:

- Do not change FOG-RAG main row based only on ComplEx coverage.
- Do not promote ComplEx-source FOG-RAG before a separate controlled experiment.
- Do not open extra LLM ablations before Dataset 2 setup unless Dataset 2 is blocked.
