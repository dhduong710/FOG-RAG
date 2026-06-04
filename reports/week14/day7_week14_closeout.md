# Week 14 Day 7 — Week 14 closeout

## 1. Theme of Week 14
Build the first proper `soft_support_raw` branch on valid raw/no-injection candidates.

## 2. What Week 14 completed
- froze the Week 14 protocol for candidate-stage soft-support work
- built three support-score variants:
  - `soft_support_raw_b025`
  - `soft_support_raw_b050`
  - `soft_support_raw_bcap`
- compared all variants against:
  - `backbone_raw`
  - `ontology_raw`
- confirmed that:
  - `b025` and `b050` are exactly the same ordering family
  - `bcap` is weaker
- manually reviewed improved / unchanged-bad / contrast cases
- selected:
  - `soft_support_raw_b050`
as the canonical main intermediate row
- exported:
  - `valid_top20_soft_support_main.json`
- froze the candidate-stage bridge into Week 15

## 3. Main factual findings
### 3.1 Candidate-stage main row
Selected main row:
- `soft_support_raw`

Origin:
- `soft_support_raw_b050`

### 3.2 Why this row was selected
- it improves over `backbone_raw`
- it has zero worsened cases vs `backbone_raw`
- it outperforms `bcap`
- it matches the Week 13 policy:
  evidence-aware + anti-shortcut, without reviving hard ontology gating

### 3.3 Role of scientific rows
- `backbone_raw` = reference row
- `ontology_raw` = negative control
- `soft_support_raw` = main intermediate row

## 4. Main metrics
### backbone_raw
- mrr_like = 0.091803
- hits1_like = 0.024
- hits3_like = 0.046
- hits10_like = 0.158
- avg_gold_rank = 18.376

### ontology_raw
- mrr_like = 0.050869
- hits1_like = 0.002
- hits3_like = 0.004
- hits10_like = 0.012
- avg_gold_rank = 20.818

### soft_support_raw
- mrr_like = 0.135644
- hits1_like = 0.056
- hits3_like = 0.134
- hits10_like = 0.182
- avg_gold_rank = 17.676

## 5. Case-level conclusion
- improved vs backbone = 80
- worsened vs backbone = 0
- unchanged_bad vs backbone = 401
- improved vs bcap = 80
- worsened vs bcap = 1

## 6. Failure taxonomy after Week 14
- shortcut-noise failure
- raw-candidate bottleneck
- weak-evidence failure
- evidence-overreward failure (seen in `bcap`)

## 7. Decision
Week 14 status: **GO**

Reason:
- candidate-stage selection is complete,
- the main intermediate row is frozen,
- the row roles are frozen,
- and Week 15 can start retrieval-stage preparation without renegotiating candidate-stage conclusions.

## 8. Week 15 policy
Week 15 must:
- keep raw/no-injection as main truth
- keep `soft_support_raw` frozen
- keep `backbone_raw` as reference
- keep `ontology_raw` as negative control
- avoid reopening candidate-stage formula search
- begin retrieval-stage preparation on top of frozen `soft_support_raw`

## 9. Final note
Week 14 does not close Novelty 2.
It closes the candidate-stage soft-support branch and prepares the transition to retrieval-stage work.