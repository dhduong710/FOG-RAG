# Day 4 — Direct comparison: week6 vs week7 candidate retrieval on valid

## Scope

- Compare week6 and week7 candidate retrieval artifacts directly on the same valid queries.
- Quantify retrieval improvement, inject reduction, and remaining collapse.

## Aggregate comparison

- week6_valid_recall@20_raw = `0.02`
- week7_valid_recall@20_raw = `0.192`
- delta_recall@20_raw = `0.172`

- week6_valid_top1_hit_ratio_raw = `0.0`
- week7_valid_top1_hit_ratio_raw = `0.018`
- delta_top1_hit_ratio_raw = `0.018`

- week6_valid_inject_ratio_ready = `0.98`
- week7_valid_inject_ratio_ready = `0.808`
- delta_inject_ratio_ready = `-0.172`

- week6_valid_unique_top1_count_raw = `None`
- week7_valid_unique_top1_count_raw = `3`
- delta_unique_top1_count_raw = `3`

- week6_valid_top1_dominance_ratio_raw = `None`
- week7_valid_top1_dominance_ratio_raw = `0.482`
- delta_top1_dominance_ratio_raw = `0.482`

## Per-query transitions

- improved_to_top20 = `96`
- worsened_out_of_top20 = `10`
- still_missing = `394`
- still_hit = `0`

- inject_removed = `96`
- inject_still_needed = `394`
- inject_newly_needed = `10`
- never_injected = `0`

## Rank delta summary

- mean_delta_rank = `596.18`
- median_delta_rank = `712.0`
- num_positive_delta = `396`
- num_zero_delta = `0`
- num_negative_delta = `104`

## Interpretation

- Week 7 is clearly better than week 6 on valid if recall@20_raw rises and inject_ratio_ready drops.
- If improved_to_top20 is much larger than worsened_out_of_top20, retrieval quality genuinely improved.
- If top1_dominance_ratio_raw remains high, score collapse is still a concern even after improvement.
- Day 5 should package backbone-ready v2 only after accepting that week7 retrieval is truly better but not fully solved.
