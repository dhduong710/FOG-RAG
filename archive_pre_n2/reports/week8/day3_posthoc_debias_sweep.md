# Week8 — post-hoc debias sweep on week7-v2

## Scope

- Sweep lambda on valid using post-hoc score debias.
- Keep week7-v2 scores fixed and only penalize globally collapse-prone drugs.
- Check whether recall can be preserved while collapse decreases.

## Baseline (lambda = 0)

- recall@20_raw = `0.192`
- top1_hit_ratio_raw = `0.018`
- inject_ratio_ready = `0.808`
- unique_top1_count_raw = `3`
- top1_dominance_ratio_raw = `0.482`

## Best lambda

- lambda = `0.05`
- accepted_under_rule = `True`
- recall@20_raw = `0.192`
- top1_hit_ratio_raw = `0.018`
- inject_ratio_ready = `0.808`
- unique_top1_count_raw = `9`
- top1_dominance_ratio_raw = `0.416`

- delta_recall@20_raw = `0.0`
- delta_top1_hit_ratio_raw = `0.0`
- delta_inject_ratio_ready = `0.0`
- delta_unique_top1_count_raw = `6`
- delta_top1_dominance_ratio_raw = `-0.066`

## Acceptance rule

- recall_drop_tolerance = `0.01`
- min_top1_dominance_improve = `0.03`
- min_unique_top1_gain = `2`
- num_accepted_lambdas = `2`

## Sweep overview

- lambda=0.0 | recall@20=0.192 | top1_hit=0.018 | inject=0.808 | unique_top1=3 | dom=0.482
- lambda=0.05 | recall@20=0.192 | top1_hit=0.018 | inject=0.808 | unique_top1=9 | dom=0.416
- lambda=0.1 | recall@20=0.19 | top1_hit=0.018 | inject=0.81 | unique_top1=8 | dom=0.388
- lambda=0.2 | recall@20=0.18 | top1_hit=0.016 | inject=0.82 | unique_top1=9 | dom=0.32
- lambda=0.3 | recall@20=0.18 | top1_hit=0.012 | inject=0.82 | unique_top1=9 | dom=0.266
- lambda=0.5 | recall@20=0.18 | top1_hit=0.01 | inject=0.82 | unique_top1=9 | dom=0.276
- lambda=0.75 | recall@20=0.17 | top1_hit=0.006 | inject=0.83 | unique_top1=12 | dom=0.328
- lambda=1.0 | recall@20=0.17 | top1_hit=0.006 | inject=0.83 | unique_top1=11 | dom=0.416
- lambda=1.5 | recall@20=0.164 | top1_hit=0.006 | inject=0.836 | unique_top1=16 | dom=0.406
- lambda=2.0 | recall@20=0.162 | top1_hit=0.008 | inject=0.838 | unique_top1=15 | dom=0.414

## Interpretation

- If an accepted lambda exists, this is the last cheap improvement worth keeping before stopping refinement.
- If no accepted lambda exists, keep week7-v2 as the main retrieval result and stop further refinement.
