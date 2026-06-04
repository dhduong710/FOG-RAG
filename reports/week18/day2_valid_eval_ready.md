# Week 18 Day 2 — Valid Eval-Ready Package

## Goal
- Standardize 4 valid rows into one eval-ready schema.
- Prepare clean inputs for day-3 valid main table building.

## Output files
- `backbone_raw` -> `dataset/setting_b/07_n2_eval_valid/valid_backbone_raw_eval.json`
- `ontology_raw` -> `dataset/setting_b/07_n2_eval_valid/valid_ontology_raw_eval.json`
- `soft_support_raw` -> `dataset/setting_b/07_n2_eval_valid/valid_soft_support_raw_eval.json`
- `retrieval_main` -> `dataset/setting_b/07_n2_eval_valid/valid_retrieval_main_eval.json`

## Summaries
### backbone_raw
- **eval_row_name**: `backbone_raw`
- **num_rows**: `500`
- **missing_valid_b_rows**: `0`
- **gold_present_rate**: `0.202`
- **mrr_like**: `0.091803`
- **hits1_like**: `0.024`
- **hits3_like**: `0.046`
- **hits10_like**: `0.158`
- **avg_gold_rank**: `18.376`

### ontology_raw
- **eval_row_name**: `ontology_raw`
- **num_rows**: `500`
- **missing_valid_b_rows**: `0`
- **gold_present_rate**: `0.014`
- **mrr_like**: `0.050869`
- **hits1_like**: `0.002`
- **hits3_like**: `0.004`
- **hits10_like**: `0.012`
- **avg_gold_rank**: `20.818`

### soft_support_raw
- **eval_row_name**: `soft_support_raw`
- **num_rows**: `500`
- **missing_valid_b_rows**: `0`
- **gold_present_rate**: `0.202`
- **mrr_like**: `0.135644`
- **hits1_like**: `0.056`
- **hits3_like**: `0.134`
- **hits10_like**: `0.182`
- **avg_gold_rank**: `17.676`

### retrieval_main
- **eval_row_name**: `retrieval_main`
- **num_rows**: `500`
- **missing_valid_b_rows**: `0`
- **gold_present_rate**: `0.202`
- **mrr_like**: `0.135644`
- **hits1_like**: `0.056`
- **hits3_like**: `0.134`
- **hits10_like**: `0.182`
- **avg_gold_rank**: `17.676`

## Notes
- No table or ablation decision is made on day 2.
- Day 2 only standardizes row schemas and joins Setting-B annotations.
