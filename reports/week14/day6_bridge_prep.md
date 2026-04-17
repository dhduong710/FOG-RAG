# Week 14 Day 6 — Bridge preparation for Week 15

## 1. Goal
Freeze the candidate-stage outputs of Week 14 and prepare a clean bridge into Week 15.

## 2. What was frozen
- `soft_support_raw` as the selected main intermediate row
- `backbone_raw` as the reference row
- `ontology_raw` as the negative control
- `soft_support_raw_bcap` as contrast only

## 3. Main outputs
- `dataset/setting_a/26_n2_soft_support/support_stage_freeze_manifest.json`
- `results/week14/soft_support_stage_report.json`
- `results/week14/soft_support_reference_table.json`
- `results/week14/soft_support_main_casepack.json`
- `results/week14/week14_to_week15_bridge.json`

## 4. Main conclusion
Week 14 candidate-stage work is sufficiently frozen.
Week 15 should not reopen candidate-stage formula search.

## 5. Remaining failure modes
- raw-candidate bottleneck
- weak-evidence failure
- candidate-stage limitations that motivate retrieval-stage work

## 6. Week 15 entry condition
Week 15 may start only if:
- `soft_support_raw` remains frozen,
- raw source remains unchanged,
- candidate-stage conclusions are no longer renegotiated.

## 7. Next step
Week 15 should begin retrieval-stage preparation on top of the frozen row:
`soft_support_raw`.