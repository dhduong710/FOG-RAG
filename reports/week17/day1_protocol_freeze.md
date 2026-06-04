# Week 17 Day 1 — Protocol Freeze

## Theme
- encoder_readiness_check

## Day-1 decisions
- Week 17 is encoder-readiness week, not full encoder week.
- Decision split = valid.
- Main input row = soft_support_fuzzy_retrieval_main.
- Main output row = soft_support_fuzzy_encoder_probe_v0.
- Exactly one encoder probe v0 is allowed this week.
- Reference comparisons will use soft_support_raw and retrieval_main.
- Test split is forbidden this week.
- Candidate-stage and retrieval-stage main rows remain frozen.

## Main rows
- Main input row: `soft_support_fuzzy_retrieval_main`
- Main output row: `soft_support_fuzzy_encoder_probe_v0`
- Decision split: `valid`

## Reference rows for compare
- `soft_support_raw`
- `soft_support_fuzzy_retrieval_main`

## Allowed actions this week
- build encoder input package from retrieval main
- run one minimal encoder probe v0
- valid-only comparison
- subset dryrun before any full-valid run

## Forbidden actions this week
- Do not change raw source.
- Do not reopen candidate-stage formulas or rows.
- Do not change retrieval main row during day 1.
- Do not run test split.
- Do not commit to full encoder stage yet.
- Do not introduce multiple encoder variants in week 17.
- Do not start long-run end-to-end training.

## Input file status
- `raw_source`: OK — `dataset/setting_a/23_noinj_source/valid_top20_raw.json`
- `soft_support_main`: OK — `dataset/setting_a/26_n2_soft_support/valid_top20_soft_support_main.json`
- `retrieval_main`: OK — `dataset/setting_a/27_n2_fuzzy_retrieval/valid_fuzzy_retrieval_main.json`
- `type_map`: OK — `dataset/setting_b/01_annotations/type_map.tsv`
- `schema_rules`: OK — `dataset/setting_b/01_annotations/schema_rules.json`
- `path_templates`: OK — `dataset/setting_b/01_annotations/path_templates.yaml`
- `valid_b_annotations`: OK — `dataset/setting_b/04_contra_checked/valid_b_annotations_contra_checked.json`

## Success criteria
- All week-17 folders exist.
- All required input files exist.
- Protocol freeze markdown is written.
- Encoder readiness manifest is written.
- Week-17 main input/output and constraints are unambiguous.

## Day-1 conclusion
- Status: **READY**
- All required inputs are present. Week 17 can proceed to Day 2.
