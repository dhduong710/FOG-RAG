# Week 14 Day 5 — Main row decision

## 1. Goal
Select the Week 14 main intermediate row for the candidate stage of Novelty 2.

## 2. Candidates considered
- soft_support_raw_b025
- soft_support_raw_b050
- soft_support_raw_bcap

## 3. Decision
Selected main row:
- `soft_support_raw_b050`

Exported as:
- `dataset/setting_a/26_n2_soft_support/valid_top20_soft_support_main.json`

## 4. Why b050 was selected
- `b025` is exactly identical to `b050` in ordering, so `b050` is used as the canonical representative.
- `b050` improves over `backbone_raw` with zero worsened cases.
- `b050` outperforms `bcap`.
- `b050` avoids the evidence-overreward behavior seen in `bcap`.
- `b050` remains compatible with the Week 13 policy: evidence-aware + anti-shortcut, without reviving hard ontology gating.

## 5. Scientific role after selection
- `backbone_raw` = reference row
- `ontology_raw` = negative control
- `soft_support_raw` = main intermediate row

## 6. Remaining failure modes
- raw-candidate bottleneck
- weak-evidence failure
- candidate-stage limitations that will later motivate retrieval-stage work

## 7. Next step
Day 6 will freeze artifacts and prepare the clean bridge from Week 14 candidate-stage work into the next stage.