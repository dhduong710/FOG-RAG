# Day 4 Pilot Inference Report

## 1. Goal
Run pilot inference on valid/test to verify generation, ranking pipeline, and manual error readability.

## 2. Inputs
- dataset_path: `dataset/setting_a/07_pilot_ready`
- model_name_or_path: `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
- checkpoint_dir: `results/week4/pilot_train_tinyllama_mock/checkpoint-final`
- kge_embedding_path: `dataset/setting_a/07_pilot_ready/mock_entity_embeddings.pt`

## 3. Output Files
- `results/week4/pilot_infer_tinyllama_mock/valid_predictions.json`
- `results/week4/pilot_infer_tinyllama_mock/test_predictions.json`
- `results/week4/pilot_infer_tinyllama_mock/metrics.json`
- `results/week4/pilot_infer_tinyllama_mock/case_review.md`

## 4. Main Metrics
### Valid
- num_samples: 100
- exact_match: 1.0
- mrr: 1.0
- hits1: 1.0
- hits3: 1.0
- hits10: 1.0
- avg_subgraph_size: 74.15
- all_coarse_rank_is_one: true

### Test
- num_samples: 100
- exact_match: 1.0
- mrr: 1.0
- hits1: 1.0
- hits3: 1.0
- hits10: 1.0
- avg_subgraph_size: 73.63
- all_coarse_rank_is_one: true

## 5. Interpretation
- Pilot inference succeeded end-to-end on valid/test.
- Metrics are saturated (exact_match/MRR/Hits all 1.0).
- Because the current pilot still uses the week-2 mock coarse ranking with gold fixed at rank 1, these results are sanity-only and not scientific.
- No meaningful failure cases were surfaced under the current mock pilot configuration, so error-type analysis is deferred to fuller month-2 backbone reproduction or harder evaluation settings.

## 6. Decision
- ready for day 5 resource planning
- do not use this pilot metric as paper evidence
- do not jump to full run before writing the resource plan