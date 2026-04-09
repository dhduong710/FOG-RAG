# Day 3 — Candidate quality from ranker_v2

## Scope

- Score full train/valid/test using the best ranker_v2 checkpoint.
- Build top20_raw and top20_drkgc_ready artifacts.
- Evaluate candidate retrieval quality on valid as the main scientific signal.

## Current valid numbers

- valid_recall@20_raw = `0.192`
- valid_top1_hit_ratio_raw = `0.018`
- valid_inject_ratio_ready = `0.808`
- valid_unique_top1_count_raw = `3`
- valid_top1_dominance_ratio_raw = `0.482`

## Comparison against week 6

- week6_valid_recall@20_raw = `0.02`
- week7_valid_recall@20_raw = `0.192`
- week6_valid_inject_ratio_ready = `0.98`
- week7_valid_inject_ratio_ready = `0.808`
- week6_valid_top1_hit_ratio_raw = `0.0`
- week7_valid_top1_hit_ratio_raw = `0.018`

## Interpretation

- If valid_recall@20_raw improved clearly over week 6, ranker_v2 is moving in the right direction.
- If valid_inject_ratio_ready decreased clearly, reranker is less dependent on gold injection.
- If top1_dominance_ratio_raw is still very high, score collapse is still a concern.
- Day 4 should compare week6 vs week7 directly on the same valid queries.
