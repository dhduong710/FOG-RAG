# Day 1 Pilot Subset Report

## Goal
Create a reproducible Setting-A pilot subset for week-4 end-to-end debugging.

## Source Files
- dataset/setting_a/04_drkgc_json/train_mock_ranked.json
- dataset/setting_a/04_drkgc_json/valid_mock_ranked.json
- dataset/setting_a/04_drkgc_json/test_mock_ranked.json

## Pilot Config
- seed: 2025
- train_ratio: 0.10
- valid_target: 100
- test_target: 100

## Output Files
- dataset/setting_a/06_pilot_subset/train_pilot_input.json
- dataset/setting_a/06_pilot_subset/valid_pilot_input.json
- dataset/setting_a/06_pilot_subset/test_pilot_input.json
- dataset/setting_a/06_pilot_subset/pilot_subset_meta.json

## Sanity Summary
- train num samples: 839
- valid num samples: 100
- test num samples: 100
- train unique queries: 491
- train unique gold drugs: 508
- valid gold in candidate count: 100
- test gold in candidate count: 100
- bad format count: 0

## Notes
- pilot subset is built from full mock-ranked inputs in 04_drkgc_json
- 05_prompt_subgraph_subset is only a 20-sample sanity subset, not the full benchmark input
- subgraph checks are deferred until prompt/subgraph generation for the pilot subset

## Decision
- ready for day 2