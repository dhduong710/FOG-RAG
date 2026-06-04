# Week 15 - Day 1 Protocol Freeze

## Theme
Start retrieval-stage on top of frozen soft_support_raw.

## Main truth
- Main truth remains raw / no-injection.
- The raw source must remain unchanged during week 15.
- Decision split for this week is valid only.

## Main rows
- Reference row: backbone_raw
- Negative control: ontology_raw (comparison only, not a positive input)
- Main intermediate input: soft_support_raw
- Target output row of week 15: soft_support_fuzzy_retrieval_v1

## Allowed main inputs
1. dataset/setting_a/23_noinj_source/valid_top20_raw.json
2. dataset/setting_a/24b_noinj_evidence/valid_aligned_evidence.json
3. dataset/setting_a/26_n2_soft_support/valid_top20_soft_support_main.json

## Allowed lookup / metadata
1. dataset/setting_b/01_annotations/type_map.tsv
2. dataset/setting_b/01_annotations/schema_rules.json
3. dataset/setting_b/01_annotations/path_templates.yaml
4. dataset/setting_b/04_contra_checked/valid_b_annotations_contra_checked.json

## Week-15 object of scoring
- The scoring object is no longer candidate-stage ranking.
- The scoring object is triple / path / subgraph selection.

## Forbidden actions this week
- Do not change 23_noinj_source.
- Do not reopen b025 / b050 / bcap candidate-stage comparison.
- Do not use ontology_raw as a positive main signal.
- Do not run test.
- Do not add fuzzy encoder.
- Do not run end-to-end reranker training.

## Expected day-1 outputs
- reports/week15/day1_protocol_freeze.md
- results/week15/week15_input_manifest.json

## Go criterion for day 1
- All main inputs are present.
- Query alignment between raw, evidence, and soft_support_main is checked.
- No ambiguity remains about the official week-15 input files.