# 8B valid rerun report

## Current 8B valid metrics

- mrr = `0.43187144`
- hits1 = `0.37599999`
- hits3 = `0.40200001`
- hits10 = `0.51800001`
- num_examples = `500`

## Compare against week6 3B

- week6_mrr = `0.83680612`
- current_8b_mrr = `0.43187144`
- delta_vs_week6_mrr = `-0.40493468`

- week6_hits1 = `0.804`
- current_8b_hits1 = `0.37599999`
- delta_vs_week6_hits1 = `-0.42800001`

- week6_hits3 = `0.808`
- current_8b_hits3 = `0.40200001`
- delta_vs_week6_hits3 = `-0.40599999`

- week6_hits10 = `0.946`
- current_8b_hits10 = `0.51800001`
- delta_vs_week6_hits10 = `-0.42799999`

## Compare against week7 3B rerun

- week7_3b_mrr = `0.42424878`
- current_8b_mrr = `0.43187144`
- delta_vs_week7_3b_mrr = `0.00762266`

- week7_3b_hits1 = `0.368`
- current_8b_hits1 = `0.37599999`
- delta_vs_week7_3b_hits1 = `0.00799999`

- week7_3b_hits3 = `0.39399999`
- current_8b_hits3 = `0.40200001`
- delta_vs_week7_3b_hits3 = `0.00800002`

- week7_3b_hits10 = `0.50999999`
- current_8b_hits10 = `0.51800001`
- delta_vs_week7_3b_hits10 = `0.00800002`

## Candidate context

- valid_recall@20_raw = `0.192`
- valid_inject_ratio_ready = `0.808`
- valid_top1_hit_ratio_raw = `0.018`

## Error bucket counts

- prediction_equals_gold = `188`
- gold_not_in_candidate = `216`
- prediction_in_candidate_but_not_top = `96`
- prediction_not_in_candidate = `0`

## Interpretation

- This 8B run is a capacity sanity check on the same week7 candidate package.
- If 8B improves clearly over week7 3B, backbone capacity is part of the bottleneck.
- If 8B still struggles badly, candidate collapse/retrieval quality remains the dominant issue.
