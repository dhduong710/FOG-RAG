# Day 6 — valid rerun with backbone-ready v2

## Scope

- Run a short backbone rerun on week7 candidate package.
- Evaluate valid only.
- Check whether better candidate retrieval transfers to reranker behavior.

## Current valid metrics (week7 v2 rerun)

- mrr = `0.42424878`
- hits1 = `0.368`
- hits3 = `0.39399999`
- hits10 = `0.50999999`
- num_examples = `500`

## Comparison against week6 valid reranker

- week6_mrr = `0.83680612`
- week7_v2_mrr = `0.42424878`
- delta_mrr = `-0.41255734`

- week6_hits1 = `0.804`
- week7_v2_hits1 = `0.368`
- delta_hits1 = `-0.436`

- week6_hits3 = `0.808`
- week7_v2_hits3 = `0.39399999`
- delta_hits3 = `-0.41400001`

- week6_hits10 = `0.946`
- week7_v2_hits10 = `0.50999999`
- delta_hits10 = `-0.43600001`

## Candidate context from Day 3

- valid_recall@20_raw = `0.192`
- valid_inject_ratio_ready = `0.808`
- valid_top1_hit_ratio_raw = `0.018`

## Error bucket counts

- prediction_equals_gold = `184`
- gold_not_in_candidate = `220`
- prediction_in_candidate_but_not_top = `96`
- prediction_not_in_candidate = `0`

## Interpretation

- If week7 v2 valid metrics hold or improve versus week6, the candidate improvement is transferring into reranker behavior.
- If metrics drop sharply despite much better candidate retrieval, the new candidate distribution may be exposing reranker weakness.
- Day 7 should close out with GO / CONDITIONAL GO / NO-GO based on both candidate quality and reranker validity.
