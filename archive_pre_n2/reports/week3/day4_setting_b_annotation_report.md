# Day 4 Setting B Annotation Report

## Output files
- dataset/setting_b/02_eval_ready/valid_b_annotations.json
- dataset/setting_b/02_eval_ready/test_b_annotations.json

## Valid stats
- num_samples: 500
- all_candidates_have_type: True
- non_drug_candidates: 0
- gold_missing_annotation: 0
- contra_positive_samples: 71

## Test stats
- num_samples: 500
- all_candidates_have_type: True
- non_drug_candidates: 0
- gold_missing_annotation: 0
- contra_positive_samples: 75

## Final checks
- valid/test sample count preserved: 500 / 500
- candidate type failures: 0
- gold missing annotation: 0

## Required checklist
- every candidate has type
- contra_flags length matches candidate list
- no non-Drug candidate remains
- every gold drug has annotation
- Setting B sample count matches Setting A candidate files