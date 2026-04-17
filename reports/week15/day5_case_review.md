# Week 15 - Day 5 Case Review

## Main framing
- fuzzy retrieval v1 did not change ranking-like proxy vs soft_support_raw
- therefore, manual review focuses on subgraph quality and failure interpretation

## Bucket counts
{
  "preserved_improvement_vs_backbone": 80,
  "same_rank_cleaner_subgraph": 251,
  "unchanged_bad": 415,
  "raw_bottleneck_failure": 407
}

## Day-5 takeaway
- preserved_improvement_vs_backbone: check whether fuzzy retrieval preserves soft-support gains
- same_rank_cleaner_subgraph: check whether evidence becomes cleaner without rank movement
- unchanged_bad: inspect stable failures
- raw_bottleneck_failure: separate candidate-source bottlenecks from retrieval-stage issues