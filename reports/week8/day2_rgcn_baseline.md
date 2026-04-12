# Day 2 R-GCN Structure Baseline

## 1. Scope
- Clean evaluation of existing R-GCN structure scorer on Setting A
- Full drug-only universe
- Valid split only

## 2. Source
- score_path: `dataset/setting_a/11_ranker_v2/valid_scores.pt`
- meta_path: `dataset/setting_a/11_ranker_v2/score_dump_meta.json`
- universe_source: `fallback_from_raw_indication_heads_sorted_by_entity_id`
- fallback_used: `True`

## 3. Main metrics
- MRR: 0.05388868
- Hits@1: 0.018
- Hits@3: 0.044
- Hits@10: 0.152

## 4. Supporting analysis
- top1_dominance_ratio: 0.482
- unique_top1_count: 3

## 5. Output files
- `dataset/setting_a/17_structure_baselines/rgcn_valid_scores.pt`
- `dataset/setting_a/17_structure_baselines/rgcn_valid_metrics.json`
- `dataset/setting_a/17_structure_baselines/rgcn_valid_top1_frequency.tsv`
- `dataset/setting_a/17_structure_baselines/rgcn_valid_case_samples.json`

## 6. Warning
- Universe ids were reconstructed from raw indication heads.
- Re-check top1 names manually before freezing this row into table v0.
## 7. Conclusion
- R-GCN clean structure-only evaluation completed on valid split.