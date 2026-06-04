# Week 4 - Day 2A Report

## Goal
Prepare prompt/subgraph-ready pilot JSON from the pilot input subset.

## Inputs
- pilot_input_dir: `dataset/setting_a/06_pilot_subset`
- split_dir: `dataset/setting_a/01_split`
- graph_path_used: `dataset/setting_a/02_graph/train_enriched_deg1000_final.tsv`
- map_dir: `dataset/setting_a/04_drkgc_json`
- lexicon_dir: `dataset/setting_a/05_prompt_subgraph_subset`
- graph_size: 100
- biomedical_prompt: True

## Preparation
- train_input_count: 839
- valid_input_count: 100
- test_input_count: 100
- train_raw_subset_count: 839
- valid_raw_subset_count: 100
- test_raw_subset_count: 100

## Outputs
- `dataset/setting_a/07_pilot_ready/train.json`
- `dataset/setting_a/07_pilot_ready/valid.json`
- `dataset/setting_a/07_pilot_ready/test.json`
- `dataset/setting_a/07_pilot_ready/pilot_ready_meta.json`

## Sanity Summary
### train.json
- num_samples: 839
- missing_key_count: 0
- empty_subgraph_count: 0
- gold_in_candidate_count: 839
- candidate_len_min: 20
- candidate_len_max: 20

### valid.json
- num_samples: 100
- missing_key_count: 0
- empty_subgraph_count: 0
- gold_in_candidate_count: 100
- valid_exact_leak_count: 0
- candidate_len_min: 20
- candidate_len_max: 20

### test.json
- num_samples: 100
- missing_key_count: 0
- empty_subgraph_count: 0
- gold_in_candidate_count: 100
- test_exact_leak_count: 0
- candidate_len_min: 20
- candidate_len_max: 20

## Notes
- Retrieval graph remains train-only.
- This script follows the week-2 prompt_subgraph pattern, but upgrades it from the 20-sample sanity subset to the week-4 pilot subset.
- Output files are ready for the day-2 dry run stage.
