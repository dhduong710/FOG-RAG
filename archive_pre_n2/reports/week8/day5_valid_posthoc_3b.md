# Week8 — valid rerun on posthoc debias package (3B)

## Current valid metrics

- mrr = `0.31621575`
- hits1 = `0.25400001`
- hits3 = `0.28200001`
- hits10 = `0.384`
- num_examples = `500`

## Compare against week6 3B

- week6_mrr = `0.83680612`
- posthoc_mrr = `0.31621575`
- delta_vs_week6_mrr = `-0.52059037`

- week6_hits1 = `0.804`
- posthoc_hits1 = `0.25400001`
- delta_vs_week6_hits1 = `-0.54999999`

- week6_hits3 = `0.808`
- posthoc_hits3 = `0.28200001`
- delta_vs_week6_hits3 = `-0.52599999`

- week6_hits10 = `0.946`
- posthoc_hits10 = `0.384`
- delta_vs_week6_hits10 = `-0.562`

## Compare against week7 3B

- week7_mrr = `0.42424878`
- posthoc_mrr = `0.31621575`
- delta_vs_week7_mrr = `-0.10803303`

- week7_hits1 = `0.368`
- posthoc_hits1 = `0.25400001`
- delta_vs_week7_hits1 = `-0.11399999`

- week7_hits3 = `0.39399999`
- posthoc_hits3 = `0.28200001`
- delta_vs_week7_hits3 = `-0.11199998`

- week7_hits10 = `0.50999999`
- posthoc_hits10 = `0.384`
- delta_vs_week7_hits10 = `-0.12599999`

## Compare against week7 8B

- week7_8b_mrr = `0.43187144`
- posthoc_3b_mrr = `0.31621575`
- delta_vs_week7_8b_mrr = `-0.11565569`

- week7_8b_hits1 = `0.37599999`
- posthoc_3b_hits1 = `0.25400001`
- delta_vs_week7_8b_hits1 = `-0.12199998`

- week7_8b_hits3 = `0.40200001`
- posthoc_3b_hits3 = `0.28200001`
- delta_vs_week7_8b_hits3 = `-0.12`

- week7_8b_hits10 = `0.51800001`
- posthoc_3b_hits10 = `0.384`
- delta_vs_week7_8b_hits10 = `-0.13400001`

## Candidate context

- valid_recall@20_raw = `0.192`
- valid_inject_ratio_ready = `0.808`
- valid_top1_hit_ratio_raw = `0.018`
- valid_unique_top1_count_raw = `9`
- valid_top1_dominance_ratio_raw = `0.416`

## Error bucket counts

- prediction_equals_gold = `127`
- gold_not_in_candidate = `277`
- prediction_in_candidate_but_not_top = `96`
- prediction_not_in_candidate = `0`

## Interpretation

- This is the final clean check of whether post-hoc debias improves end-to-end reranker behavior.
- If valid improves over week7 3B without hurting candidate metrics, keep post-hoc debias as the final retrieval package.
- If valid stays flat or worsens, keep post-hoc debias only as a retrieval-side analysis result.
