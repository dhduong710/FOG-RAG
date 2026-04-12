# Week8 / retrieval-v3 Day 1 — hard negatives + bias stats

## Scope

- Prepare collapse-aware hard negatives for retrieval-v3.
- Build drug bias statistics from week7 score dumps.
- Confirm that retrieval, not backbone size, remains the main bottleneck.

## Current week7 retrieval context

- valid_recall@20_raw = `0.192`
- valid_top1_hit_ratio_raw = `0.018`
- valid_inject_ratio_ready = `0.808`
- valid_unique_top1_count_raw = `3`
- valid_top1_dominance_ratio_raw = `0.482`

## Collapse drugs

- Betamethasone | collapse_score=83.02726846 | train_top1=3700 | valid_top1=241 | mean_score_train=2.39484406
- Fusidic acid | collapse_score=70.31505873 | train_top1=3407 | valid_top1=186 | mean_score_train=0.58188719
- Methylprednisolone | collapse_score=30.2668213 | train_top1=1277 | valid_top1=73 | mean_score_train=2.2399981
- Cortisone acetate | collapse_score=5.43282104 | train_top1=1 | valid_top1=0 | mean_score_train=2.19408917
- Hydrocortisone | collapse_score=5.21520392 | train_top1=1 | valid_top1=0 | mean_score_train=2.22459936
- Prednisolone | collapse_score=5.13139603 | train_top1=1 | valid_top1=0 | mean_score_train=2.00061488
- Triamcinolone | collapse_score=5.01072327 | train_top1=1 | valid_top1=0 | mean_score_train=2.19044399
- Dexamethasone | collapse_score=4.99412066 | train_top1=0 | valid_top1=0 | mean_score_train=1.88144433
- Prednisone | collapse_score=4.0734223 | train_top1=0 | valid_top1=0 | mean_score_train=1.6621747
- Hydrocortisone acetate | collapse_score=3.84200701 | train_top1=0 | valid_top1=0 | mean_score_train=1.6700089

## Hard negative pool summary

- num_queries = `8388`
- hard_pool_size_min = `25`
- hard_pool_size_max = `36`
- hard_pool_size_mean = `29.5548`

Top hard negatives:
- Vinblastine: 8362
- Methotrexate: 8361
- Propranolol: 8360
- Vincristine: 8357
- Paclitaxel: 8357
- Bleomycin: 8355
- Thiotepa: 8353
- Minocycline: 8349
- Ofloxacin: 8345
- Norfloxacin: 8344

## Conclusion

- Day 2 should train retrieval-v3 with mixed negatives: raw top-k non-gold + collapse drugs + bias-heavy drugs.
- If retrieval-v3 still collapses after this, it becomes reasonable to stop refinement and use the current results.

## Note

- 8B only improved very slightly over week7 3B, so this refinement focuses on retrieval quality rather than LLM capacity.
