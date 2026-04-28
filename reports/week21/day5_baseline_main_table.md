# Week 21 Day 5 — Baseline Main Table and Paper Positioning

## Decision

**FOG_RAG_MAIN_BEST_TEST_MRR_OR_TIED_WITH_STRUCTURE_BASELINE**

## Main conclusion

FOG-RAG main achieves the best locked-test reviewer-safe MRR@20, slightly above the strongest structure-only candidate generator.

## Key locked-test numbers

| Row | Gold@20 | MRR@20 | Hits@1 | Hits@3 | Hits@10 |
|---|---:|---:|---:|---:|---:|
| DrKGC-style backbone raw | 0.2400 | 0.064563 | 0.0240 | 0.0700 | 0.1920 |
| ComplEx | 0.5740 | 0.124731 | 0.0320 | 0.1180 | 0.3840 |
| FOG-RAG main | 0.2400 | 0.125326 | 0.0720 | 0.1660 | 0.2220 |

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

## Important deltas on test

### FOG-RAG main minus backbone raw

```json
{
  "delta_gold_present_at20": 0.0,
  "delta_mrr_at20": 0.06076335466219365,
  "delta_hits1_at20": 0.047999999999999994,
  "delta_hits3_at20": 0.096,
  "delta_hits10_at20": 0.03,
  "delta_avg_rank_absent_as_21": -0.8480000000000025
}
```

### FOG-RAG main minus ComplEx

```json
{
  "delta_gold_present_at20": -0.33399999999999996,
  "delta_mrr_at20": 0.000595088253679571,
  "delta_hits1_at20": 0.039999999999999994,
  "delta_hits3_at20": 0.048000000000000015,
  "delta_hits10_at20": -0.162,
  "delta_avg_rank_absent_as_21": 3.019999999999998
}
```

### ComplEx minus backbone raw

```json
{
  "delta_gold_present_at20": 0.33399999999999996,
  "delta_mrr_at20": 0.06016826640851408,
  "delta_hits1_at20": 0.008,
  "delta_hits3_at20": 0.04799999999999999,
  "delta_hits10_at20": 0.192,
  "delta_avg_rank_absent_as_21": -3.8680000000000003
}
```

## Interpretation

The result is scientifically useful because ComplEx is a strong candidate generator with much higher Gold@20, but FOG-RAG main still obtains slightly higher locked-test MRR@20.

Candidate coverage alone is not sufficient. Even with lower Gold@20, FOG-RAG improves rank placement under reviewer-safe MRR@20 by modeling support and evidence quality.

## Caveats

- ComplEx has much higher Gold@20 than FOG-RAG main on both validation and test.
- ComplEx is higher than FOG-RAG main on validation MRR@20.
- FOG-RAG main is slightly higher than ComplEx on locked-test MRR@20.
- The margin between FOG-RAG main and ComplEx on test is very small, so avoid overclaiming universal superiority.
- The strongest framing is that FOG-RAG improves the DrKGC-compatible raw source and remains competitive with a strong structure-only generator.

## Recommended paper text

Although ComplEx provides substantially higher top-20 gold coverage, FOG-RAG main achieves the highest locked-test reviewer-safe MRR@20. This indicates that candidate coverage alone is insufficient: ranking quality within the top-20 candidate list and evidence-aware support modeling remain important. We therefore report structure-only models as upstream candidate-generator baselines and position FOG-RAG as an evidence-aware extension of the DrKGC-compatible graph-augmented LLM pipeline.

## Files produced

- `results/week21/baseline_main_table.json`
- `results/week21/baseline_main_table.csv`
- `results/week21/baseline_main_table.tex`
- `results/week21/baseline_positioning_decision.json`

## Next step

Day 6 should build interpretation assets: Results paragraph, Discussion paragraph, updated LaTeX insertion, and reviewer-defense text about why ComplEx has much higher Gold@20 but FOG-RAG remains meaningful.
