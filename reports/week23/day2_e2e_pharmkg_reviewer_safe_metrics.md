# Week 23 Day 2 — PharmKG E2E Reviewer-Safe Metrics

## Protocol

- Dataset: PharmKG therapeutic-association proxy task.
- Missing entity: drug/chemical head.
- Relation: `T`, normalized as `therapeutic_association_proxy`.
- Candidate size: top-20.
- No valid/test gold injection.
- Reviewer-safe RR: `1/rank` if rank <= 20, otherwise `0`.

## Summary table

| Split | Row | Gold@20 | Candidate MRR@20 | E2E MRR@20 | E2E H@1 | E2E H@3 | E2E H@10 | Pred-in-cand | Invalid pred | Rank21 |
|---|---|---|---|---|---|---|---|---|---|---|
| valid | backbone_raw | 0.070 | 0.017846 | 0.015410 | 0.006 | 0.014 | 0.034 | 0.526 | 0.474 | 465 |
| valid | soft_support_raw | 0.070 | 0.021308 | 0.017157 | 0.004 | 0.020 | 0.052 | 0.360 | 0.640 | 465 |
| valid | fuzzy_retrieval_main | 0.070 | 0.021308 | 0.017184 | 0.004 | 0.020 | 0.052 | 0.376 | 0.624 | 465 |
| test | backbone_raw | 0.092 | 0.020481 | 0.015575 | 0.000 | 0.018 | 0.044 | 0.510 | 0.490 | 454 |
| test | soft_support_raw | 0.092 | 0.028159 | 0.020587 | 0.000 | 0.030 | 0.062 | 0.390 | 0.610 | 454 |
| test | fuzzy_retrieval_main | 0.092 | 0.028159 | 0.020971 | 0.002 | 0.030 | 0.062 | 0.412 | 0.588 | 454 |

## Notes

- Candidate MRR@20 is computed from the fixed candidate order before generation.
- E2E MRR@20 is computed from generated predictions using reviewer-safe rank handling.
- Rows with rank 21 receive RR = 0.
- `fuzzy_retrieval_main` should preserve soft-support candidate order but use compressed subgraphs.