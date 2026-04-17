# Week 5 - Day 2 Backbone Ready Report

## Goal
Build full Setting-A prompt/subgraph-ready JSON for week-5 backbone reproduction.

## Inputs
- input_dir: `dataset/setting_a/10_backbone_ready_real/week5_compat_input`
- split_dir: `dataset/setting_a/01_split`
- graph_path_used: `dataset/setting_a/02_graph/train_enriched_deg1000_final.tsv`
- map_dir: `dataset/setting_a/04_drkgc_json`
- lexicon_dir: `dataset/setting_a/05_prompt_subgraph_subset`
- graph_size: 100
- biomedical_prompt: True

## Full Input Counts
- train_input_count: 8388
- valid_input_count: 500
- test_input_count: 500

## Outputs
- `dataset/setting_a/10_backbone_ready_real/train.json`
- `dataset/setting_a/10_backbone_ready_real/valid.json`
- `dataset/setting_a/10_backbone_ready_real/test.json`
- `dataset/setting_a/10_backbone_ready_real/entity2id.pkl`
- `dataset/setting_a/10_backbone_ready_real/id2entity.pkl`
- `dataset/setting_a/10_backbone_ready_real/relation2id.pkl`
- `dataset/setting_a/10_backbone_ready_real/id2relation.pkl`
- `dataset/setting_a/10_backbone_ready_real/backbone_ready_manifest.json`

## Sanity Summary
### train.json
- num_samples: 8388
- missing_key_count: 0
- empty_subgraph_count: 0
- gold_in_candidate_count: 8388
- candidate_len_min: 20
- candidate_len_max: 20

### valid.json
- num_samples: 500
- missing_key_count: 0
- empty_subgraph_count: 0
- gold_in_candidate_count: 500
- valid_exact_leak_count: 0
- candidate_len_min: 20
- candidate_len_max: 20

### test.json
- num_samples: 500
- missing_key_count: 0
- empty_subgraph_count: 0
- gold_in_candidate_count: 500
- test_exact_leak_count: 0
- candidate_len_min: 20
- candidate_len_max: 20

## Judgment
READY for week-5 day-3 embedding export if all assertions passed.
