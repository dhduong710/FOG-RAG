# Week 23 Day 1 — Transfer Protocol Freeze and Backbone Raw Evaluation

## Decision

`TRANSFER_BACKBONE_RAW_READY`

## Frozen transfer protocol

- Dataset: `PharmKG-8k`
- Setting: `setting_c_pharmkg`
- Task: `(?, T, disease)`
- Target relation raw: `T`
- Target relation normalized: `therapeutic_association_proxy`
- Paper label: `therapeutic association proxy`
- Source model: `rgcn`
- Candidate universe: `drug_only_from_train_T_heads`
- Top-K: `20`
- Gold injection: `False`
- Main metric: `reviewer_safe_mrr_at20`
- RR policy: `RR = 1/rank if gold is present in top-20 else 0`

Important wording:

Do **not** call relation `T` clinical indication. Use `therapeutic association proxy`.

## Backbone raw metrics

| Split | Gold@20 | MRR@20 | MRR present-only | H@1 | H@3 | H@10 | H@20 | Rank21 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| valid | 0.070 | 0.017846471743 | 0.254949596327 | 0.010 | 0.014 | 0.034 | 0.070 | 465 |
| test | 0.092 | 0.020480769841 | 0.222617063486 | 0.008 | 0.020 | 0.046 | 0.092 | 454 |

## Week 22 consistency check

- valid match Week 22 R-GCN: `True`
- test match Week 22 R-GCN: `True`

## Day 1 interpretation

The PharmKG transfer starts from a difficult R-GCN raw source:

- valid Gold@20 = `0.070`
- test Gold@20 = `0.092`

This means Week 23 should treat raw candidate bottleneck as a central diagnostic, not hide it.

## Files written

- `results/week23/dataset2_transfer_protocol_freeze.json`
- `dataset/setting_c_pharmkg/07_transfer_eval_ready/backbone_raw_valid.json`
- `dataset/setting_c_pharmkg/07_transfer_eval_ready/backbone_raw_test.json`
- `results/week23/backbone_raw_eval_valid.json`
- `results/week23/backbone_raw_eval_test.json`
- `reports/week23/day1_transfer_protocol_and_backbone.md`

## Next step

Day 2 will build candidate support features and hard-support negative control.
