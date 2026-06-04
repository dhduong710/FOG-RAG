# Week 13 Day 7 — Week 13 closeout

## 1. Theme of Week 13
Freeze the Novelty 2 workspace and audit support features on valid raw/no-injection candidates.

## 2. What Week 13 completed
- created and switched to branch `week_13`
- froze the Novelty 2 file registry
- soft-pruned the repo and moved legacy branches to `archive_pre_n2`
- copied reference backbone rows into `results/reference_rows`
- built `valid_support_features.json`
- audited support-feature usefulness
- probed lightweight support-score formulas
- manually reviewed improved / unchanged-bad cases

## 3. Main factual findings
### 3.1 Constant or useless features
- `type_valid_flag`
- `schema_valid_flag`
- `type_filtered_keep_flag`
- `conflict_flag`
- `candidate_in_aligned_evidence`

These are not useful as main support-score features.

### 3.2 Ontology finding
`ontology_keep_flag` is not a good positive main signal on raw candidates.
Gold is kept by ontology_raw much less often than non-gold candidates.

### 3.3 Evidence finding
`evidence_edge_touch_count` contains signal, but should not be used as an unbounded linear reward.

### 3.4 Direct-link finding
Penalizing direct candidate-query links is useful.
This suppresses shortcut/noisy candidates and improves gold rank without producing worsened cases.

## 4. Formula probe result
Best formula family:
- `B_evidence_minus_direct`

Key metrics:
- mrr_like = 0.135644
- hits1_like = 0.056
- hits3_like = 0.134
- hits10_like = 0.182
- avg_gold_rank = 17.676

Compared with Formula A:
- improved queries = 77
- worsened queries = 0

## 5. Failure taxonomy after Week 13
### A. Shortcut-noise failure
Formula B helps here by demoting noisy direct-link candidates.

### B. Raw-candidate bottleneck
If gold is absent from top-k raw, support scoring cannot rescue it.

### C. Weak-evidence failure
Gold may still remain low when evidence support is too weak.

### D. Potential over-penalization
No strong evidence yet in Week 13 because worsened cases = 0.

## 6. Decision
Week 13 status: **GO**

Reason:
- the workspace is now clean for Novelty 2,
- the input registry is frozen,
- a viable support-score family has been identified,
- and the remaining failure modes are interpretable.

## 7. Week 14 policy
Week 14 should:
- keep raw/no-injection as main truth,
- keep Formula-B-style support scoring as the starting family,
- avoid reviving hard ontology gating,
- avoid using ontology_keep as the main positive signal,
- build the first proper `soft_support_raw` branch on valid only.

## 8. Final note
Week 13 does not yet claim a final Novelty 2 method.
It only identifies the correct candidate-stage direction:
evidence-aware + anti-shortcut soft support.