# Week 18 Day 3 — Valid Main Table + Ablation (Reviewer-safe)

## Metric policy
- Main metric: `mrr_at20`
- RR rule: `1/rank if rank <= 20 else 0`
- Descriptive rank rule: `gold_rank = 21 when gold is out of top20`

## Main valid table rows
- `backbone_raw` (reference)
- `ontology_raw` (negative_control)
- `soft_support_raw` (candidate_stage_main_intermediate)
- `soft_support_fuzzy_retrieval_main` (main_row_after_week17)

## Ranking summary
### backbone_raw
- **num_rows**: `500`
- **num_present**: `101`
- **gold_present_rate**: `0.202`
- **mrr_at20**: `0.053803`
- **mrr_present_only**: `0.266353`
- **hits1_at20**: `0.024`
- **hits3_at20**: `0.046`
- **hits10_at20**: `0.158`
- **avg_gold_rank**: `18.376`

### ontology_raw
- **num_rows**: `500`
- **num_present**: `7`
- **gold_present_rate**: `0.014`
- **mrr_at20**: `0.003917`
- **mrr_present_only**: `0.279762`
- **hits1_at20**: `0.002`
- **hits3_at20**: `0.004`
- **hits10_at20**: `0.012`
- **avg_gold_rank**: `20.818`

### soft_support_raw
- **num_rows**: `500`
- **num_present**: `101`
- **gold_present_rate**: `0.202`
- **mrr_at20**: `0.097644`
- **mrr_present_only**: `0.483385`
- **hits1_at20**: `0.056`
- **hits3_at20**: `0.134`
- **hits10_at20**: `0.182`
- **avg_gold_rank**: `17.676`

### soft_support_fuzzy_retrieval_main
- **num_rows**: `500`
- **num_present**: `101`
- **gold_present_rate**: `0.202`
- **mrr_at20**: `0.097644`
- **mrr_present_only**: `0.483385`
- **hits1_at20**: `0.056`
- **hits3_at20**: `0.134`
- **hits10_at20**: `0.182`
- **avg_gold_rank**: `17.676`

## Key takeaways
- ontology_raw remains a valid negative control and should not be treated as a competitive row.
- soft_support_raw is the candidate-stage main intermediate row.
- soft_support_fuzzy_retrieval_main preserves reviewer-safe ranking metrics over soft_support_raw while improving graph-side packaging.
- encoder probe remains appendix/supporting only and is not promoted to main row.

## Appendix note
- encoder probe positioning: `supporting_appendix_only`
- encoder probe decision: `deferred_not_promoted`
