# Week 16 - Day 1 Protocol Freeze

## Theme
Retrieval sweep and main-row selection on valid.

## Main truth
- Main truth remains raw / no-injection.
- Raw source must remain unchanged.
- Decision split remains valid only.

## Main rows
- Reference row: backbone_raw
- Negative control: ontology_raw (comparison only)
- Main intermediate input: soft_support_raw
- Reference retrieval row from week 15: soft_support_fuzzy_retrieval_v1
- Target output of week 16: soft_support_fuzzy_retrieval_main

## Allowed main inputs
1. dataset/setting_a/23_noinj_source/valid_top20_raw.json
2. dataset/setting_a/24b_noinj_evidence/valid_aligned_evidence.json
3. dataset/setting_a/26_n2_soft_support/valid_top20_soft_support_main.json
4. dataset/setting_a/27_n2_fuzzy_retrieval/valid_fuzzy_retrieval_v1.json
5. dataset/setting_a/27_n2_fuzzy_retrieval/path_score_manifest.json

## Allowed lookup / metadata
1. dataset/setting_b/01_annotations/type_map.tsv
2. dataset/setting_b/01_annotations/schema_rules.json
3. dataset/setting_b/01_annotations/path_templates.yaml
4. dataset/setting_b/04_contra_checked/valid_b_annotations_contra_checked.json

## Sweep axes allowed this week
1. retrieval budget / retain ratio
2. direct-shortcut penalty
3. at most one small coverage-policy tweak if really needed

## Forbidden actions this week
- Do not change 23_noinj_source.
- Do not reopen candidate-stage variants.
- Do not change soft_support_raw.
- Do not use ontology_raw as a positive main signal.
- Do not run test.
- Do not enable fuzzy encoder.
- Do not run end-to-end reranker training.
- Do not open too many retrieval variants.

## Planned retrieval variants
- soft_support_fuzzy_retrieval_v1        # frozen week-15 reference
- soft_support_fuzzy_retrieval_tight     # tighter budget
- soft_support_fuzzy_retrieval_directplus # stronger direct-shortcut penalty
- optional: soft_support_fuzzy_retrieval_loose

## Success criterion for week 16
- choose exactly one main retrieval row on valid
- cleaner evidence than v1 or clearer trade-off
- no ranking-like collapse vs soft_support_raw
- enough confidence to decide whether week 17 can move toward encoder stage