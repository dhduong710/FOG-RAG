# Week 6 - Day 2 Completion Check

## Final decision: **GO**

## 1. Overall summary
- passed_checks: 1
- failed_checks: 0
- warnings: 0

## 2. Required input readiness
- ready: True
- missing inputs: none

## 3. Checkpoint inspection
- checkpoint path: `dataset/setting_a/09_real_coarse_ranker/rgcn_ranker_checkpoint.pt`
- checkpoint_keys: ['dropout', 'drug_universe_ids', 'drug_universe_names', 'embedding_dim', 'entity2id_path', 'epochs', 'graph_path', 'learning_rate', 'model_state_dict', 'node_embeddings', 'num_layers', 'relation2id_path', 'relation_embeddings', 'seed', 'weight_decay']
- num_entities_expected: 10453
- num_relations_expected: 4
- node_embeddings_shape: [10453, 256]
- relation_embeddings_shape: [4, 256]
- drug_universe_size_in_checkpoint: 1801
- checkpoint errors: none

## 4. Score file inspection
### train
- path: `dataset/setting_a/09_real_coarse_ranker/train_scores.pt`
- split_name: train
- expected_num_queries: 8388
- actual_num_queries: 8388
- expected_num_candidates: 1801
- actual_num_candidates: 1801
- score_summary: {'shape': [8388, 1801], 'all_finite': True, 'min': -2110.1572265625, 'max': 390.4992980957031, 'mean': 9.286408424377441, 'std': 28.357460021972656}
- raw_top1_ratio: 0.000358
- errors: none
- warnings: none

### valid
- path: `dataset/setting_a/09_real_coarse_ranker/valid_scores.pt`
- split_name: valid
- expected_num_queries: 500
- actual_num_queries: 500
- expected_num_candidates: 1801
- actual_num_candidates: 1801
- score_summary: {'shape': [500, 1801], 'all_finite': True, 'min': -1952.4970703125, 'max': 360.85565185546875, 'mean': 9.851249694824219, 'std': 27.491445541381836}
- raw_top1_ratio: 0.0
- errors: none
- warnings: none

### test
- path: `dataset/setting_a/09_real_coarse_ranker/test_scores.pt`
- split_name: test
- expected_num_queries: 500
- actual_num_queries: 500
- expected_num_candidates: 1801
- actual_num_candidates: 1801
- score_summary: {'shape': [500, 1801], 'all_finite': True, 'min': -2110.1572265625, 'max': 390.4992980957031, 'mean': 9.0228910446167, 'std': 27.36125373840332}
- raw_top1_ratio: 0.0
- errors: none
- warnings: none

## 5. End-of-day interpretation
- Ngày 2 đạt: scorer thật đã train/export được và score dump cho train/valid/test dùng được.
- Bạn có thể sang ngày 3 để build top20_raw và top20_drkgc_ready.

## 6. Next step
- If GO: move to day 3 and build `top20_raw` / `top20_drkgc_ready`.
- If CONDITIONAL GO: fix warnings first if they affect scientific interpretation.
- If NO-GO: do not move to day 3 before fixing checkpoint/score dump issues.
