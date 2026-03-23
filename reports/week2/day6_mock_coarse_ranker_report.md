# Week 2 - Day 6 Report

## Goal
Build a deterministic type-safe mock coarse ranker and replace gold-only placeholder ranking.

## Candidate policy
- K: 20
- candidate_type: drug
- gold_included: True
- ranking_policy: gold-first + deterministic shuffled negatives
- drug_universe_source: `dataset/setting_a/01_split/train.tsv`
- drug_universe_size: 1801

## Split outputs
- train samples: 8388
- valid samples: 500
- test samples: 500

## Output files
- `dataset/setting_a/03_candidates/train_mock_candidates.json`
- `dataset/setting_a/03_candidates/valid_mock_candidates.json`
- `dataset/setting_a/03_candidates/test_mock_candidates.json`
- `dataset/setting_a/03_candidates/candidate_meta.json`
- `dataset/setting_a/04_drkgc_json/train_mock_ranked.json`
- `dataset/setting_a/04_drkgc_json/valid_mock_ranked.json`
- `dataset/setting_a/04_drkgc_json/test_mock_ranked.json`

## Notes
- This is NOT a learned ranker.
- This is a schema- and pipeline-locking mock coarse ranker.
- Gold is always placed at rank 1 for deterministic sanity checking.
