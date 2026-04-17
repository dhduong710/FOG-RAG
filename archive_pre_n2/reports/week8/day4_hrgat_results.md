# Day 4 HRGAT Valid Results

## 1. Scope
- Full valid evaluation for HRGAT structure-only baseline
- Same Setting A structure-only protocol as Day 2

## 2. Sources
- checkpoint_path: `results/week8/hrgat_baseline_full_v1/hrgat_checkpoint.pt`
- checkpoint_best_epoch: 9
- meta_path: `results/week8/hrgat_baseline_full_v1/hrgat_meta.json`
- graph_path: `dataset/setting_a/02_graph/train_enriched_deg1000_final.tsv`

## 3. Main metrics
- MRR: 0.09550672
- Hits@1: 0.016
- Hits@3: 0.066
- Hits@10: 0.29

## 4. Supporting analysis
- top1_dominance_ratio: 0.054
- unique_top1_count: 161

## 5. Output files
- `dataset/setting_a/17_structure_baselines/hrgat_valid_scores.pt`
- `dataset/setting_a/17_structure_baselines/hrgat_valid_metrics.json`
- `dataset/setting_a/17_structure_baselines/hrgat_valid_top1_frequency.tsv`
- `dataset/setting_a/17_structure_baselines/hrgat_valid_case_samples.json`

## 6. Decision on baseline #3
- Preferred: ComplEx
- Fallback: TransE

## 7. Conclusion
- HRGAT valid evaluation completed under clean structure-only protocol.
- If metrics and collapse profile are reasonable, move to ComplEx on Day 5.