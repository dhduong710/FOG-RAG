# Week 2 - Day 7 Report

## Part A - Prepare prompt_subgraph subset
- subset_n: 20
- seed: 2025
- source_train_graph: `dataset/setting_a/02_graph/train_enriched.tsv`
- source_valid_raw: `dataset/setting_a/01_split/valid.tsv`
- source_test_raw: `dataset/setting_a/01_split/test.tsv`
- source_train_json: `dataset/setting_a/04_drkgc_json/train_mock_ranked.json`
- source_valid_json: `dataset/setting_a/04_drkgc_json/valid_mock_ranked.json`
- source_test_json: `dataset/setting_a/04_drkgc_json/test_mock_ranked.json`

## Prepared files
- `dataset/setting_a/05_prompt_subgraph_subset/train_enriched_noheader.tsv`
- `dataset/setting_a/05_prompt_subgraph_subset/valid_20_raw_noheader.tsv`
- `dataset/setting_a/05_prompt_subgraph_subset/test_20_raw_noheader.tsv`
- `dataset/setting_a/05_prompt_subgraph_subset/train_20_input.json`
- `dataset/setting_a/05_prompt_subgraph_subset/valid_20_input.json`
- `dataset/setting_a/05_prompt_subgraph_subset/test_20_input.json`
- `dataset/setting_a/05_prompt_subgraph_subset/head_prediction_lexicon.json`
- `dataset/setting_a/05_prompt_subgraph_subset/tail_prediction_lexicon.json`
- `dataset/setting_a/05_prompt_subgraph_subset/rules.json`

## Notes
- train raw for graph building uses full enriched train graph.
- valid/test raw are 20-sample subsets.
- input raw TSV files are exported WITHOUT header for compatibility with prompt_subgraph.py.
