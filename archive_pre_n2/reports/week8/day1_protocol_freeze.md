# Day 1 Protocol Freeze

## 1. Scope
- Freeze structural baseline protocol for Setting A
- Freeze baseline registry for the week
- Freeze table schema v0

## 2. Locked protocol
- Task: head prediction `(?, indication, disease)`
- Universe: drug-only
- Main decision split: valid
- Main metrics: MRR, Hits@1, Hits@3, Hits@10
- Detected valid size: 500

## 3. Backbone reference policy
- Main backbone reference: week7-v2
- Supporting analysis only: posthoc debias λ=0.05

## 4. Baseline registry
### Required
- R-GCN
- HRGAT

### Preferred
- ComplEx

### Optional
- TransE

## 5. Table policy
- Use 2 sections:
  1. Structure-only baselines
  2. Candidate-aware reranker reference rows
- Do not mix both protocols into one undifferentiated table.

## 6. Required path check
- [OK] `valid_split` -> `dataset/setting_a/01_split/valid.tsv`
- [OK] `test_split` -> `dataset/setting_a/01_split/test.tsv`
- [OK] `train_split` -> `dataset/setting_a/01_split/train.tsv`
- [OK] `entity2id` -> `dataset/setting_a/04_drkgc_json/entity2id.pkl`
- [OK] `id2entity` -> `dataset/setting_a/04_drkgc_json/id2entity.pkl`
- [OK] `relation2id` -> `dataset/setting_a/04_drkgc_json/relation2id.pkl`
- [OK] `id2relation` -> `dataset/setting_a/04_drkgc_json/id2relation.pkl`
- [OK] `week7_backbone_reference` -> `results/week7/backbone_valid_v2_short/valid_eval_v2/eval_valid_v2_metrics.json`
- [OK] `week7_backbone_reference_8b` -> `results/week7/backbone_valid_v2_8b_full/valid_eval_8b/eval_valid_8b_metrics.json`
- [OK] `week8_posthoc_reference` -> `results/week8/backbone_valid_posthoc_3b/valid_eval_posthoc_3b/eval_valid_posthoc_3b_metrics.json`

## 7. Main warning
If protocol is not frozen on day 1, all following metrics/tables can become inconsistent.

## 8. Day-1 conclusion
Protocol is frozen for:
- valid-first structural baseline evaluation
- drug-only universe
- clean structure-only table v0
- separate reference section for candidate-aware reranker rows
