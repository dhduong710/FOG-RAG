# Day 5 ComplEx / TransE

## 1. Scope
- Train and evaluate ComplEx structure-only baseline
- Keep the same Setting A structure-only protocol

## 2. ComplEx sources
- checkpoint_path: `results/week8/complex_baseline_full_v1/complex_checkpoint.pt`
- checkpoint_best_epoch: 18
- meta_path: `results/week8/complex_baseline_full_v1/complex_meta.json`

## 3. ComplEx main metrics
- MRR: 0.13171101
- Hits@1: 0.028
- Hits@3: 0.102
- Hits@10: 0.41

## 4. Supporting analysis
- top1_dominance_ratio: 0.056
- unique_top1_count: 154

## 5. Current decision
- ComplEx is the preferred baseline #3.
- TransE remains optional if there is still enough time after table v0 is stable.

## 6. Output files
- `dataset/setting_a/17_structure_baselines/complex_valid_scores.pt`
- `dataset/setting_a/17_structure_baselines/complex_valid_metrics.json`
- `dataset/setting_a/17_structure_baselines/complex_valid_top1_frequency.tsv`
- `dataset/setting_a/17_structure_baselines/complex_valid_case_samples.json`