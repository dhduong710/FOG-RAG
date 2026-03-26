# Day 2 Dry Run Report

## Goal
Verify that one pilot batch can pass data -> collate -> forward -> loss.

## Inputs
- dataset_path: dataset/setting_a/07_pilot_ready
- model_name_or_path: TinyLlama/TinyLlama-1.1B-Chat-v1.0
- kge_embedding_path: dataset/setting_a/07_pilot_ready/mock_entity_embeddings.pt
- source_max_len: 768
- target_max_len: 32
- batch_size: 2
- steps: 2

## Dry Run Output
### Step 0
- actual_batch_size: 2
- sequence_length: 435
- num_candidates_per_sample: 20
- query_ids_shape: (2,)
- entity_ids_shape: (2, 20)
- loss: 0.418965607881546
- loss_is_finite: True
- peak_gpu_memory_mb: 4618.71

### Step 1
- actual_batch_size: 2
- sequence_length: 429
- num_candidates_per_sample: 20
- query_ids_shape: (2,)
- entity_ids_shape: (2, 20)
- loss: 0.5673664212226868
- loss_is_finite: True
- peak_gpu_memory_mb: 4757.14

## Interpretation
- pilot batch successfully passed data -> collate -> forward -> loss
- no OOM and no NaN were observed
- K=20 candidate setting remained intact
- current day-2 objective is achieved

## Notes
- this dry run used mock entity embeddings for plumbing verification only
- results should not be used for scientific conclusions
- testing a larger month-2 LLM is deferred to resource-planning stage, not required for day 2 completion

## Decision
- ready for day 3 pilot train