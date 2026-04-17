# Week 11 - Patch Before Closeout

## Why this patch is needed
- The previous v1 table hid the novelty signal because GoldInTopKRate unfairly favored the backbone reference row.
- Setting B @10 metrics were saturated at 0 for all rows, so @10 alone could not show where the novelty helps.
- The patch therefore adds final-list safety metrics and moves GoldInFinalListRate to a supporting table.

## What was changed
- No model retraining.
- No candidate logic change.
- Added SafetyViolation@final and Contra@final for all rows.
- Rewrote the main ablation table to remove GoldInTopKRate from the main comparison.

## Main decision after patch
- main_row: `hard_main`
- supporting_row: `soft_best`
- reason: hard_main and soft_best tie on Setting B @10 safety/constraint metrics, but hard_main has higher GoldInTopKRate and cleaner week10 candidate-stage safety proxies.

## Main takeaway
- hard_main remains the main row because it is fully clean at both @10 and final-list level while recovering ranking over ontology.
- soft_best remains a supporting ablation.
