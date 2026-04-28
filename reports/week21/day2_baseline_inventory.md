# Week 21 Day 2 — Baseline Inventory Audit

## Decision

**INVENTORY_NEEDS_RERUN_FOR_CORE_BASELINES**

## Scope

Inventory old structure baseline artifacts for `TransE`, `ComplEx`, `R-GCN`, `HRGAT`, and optional `DistMult` / `RotatE`. Baselines are treated only as upstream top-20 candidate generators, not as classical full-ranking KGC rows.

## Scan summary

- Files scanned: `1156`
- Scan roots: `results, dataset, reports, scripts, archive_pre_n2`

## FOG-RAG reference files

- `raw_valid`: **OK** — `dataset/setting_a/23_noinj_source/valid_top20_raw.json`
- `raw_test`: **OK** — `dataset/setting_a/23_noinj_source/test_top20_raw.json`
- `eval_valid_backbone`: **OK** — `dataset/setting_b/07_n2_eval_valid/valid_backbone_raw_eval.json`
- `eval_valid_soft`: **OK** — `dataset/setting_b/07_n2_eval_valid/valid_soft_support_raw_eval.json`
- `eval_valid_retrieval`: **OK** — `dataset/setting_b/07_n2_eval_valid/valid_retrieval_main_eval.json`
- `eval_test_backbone`: **OK** — `dataset/setting_b/08_n2_eval_test/test_backbone_raw_eval.json`
- `eval_test_soft`: **OK** — `dataset/setting_b/08_n2_eval_test/test_soft_support_raw_eval.json`
- `eval_test_retrieval`: **OK** — `dataset/setting_b/08_n2_eval_test/test_retrieval_main_eval.json`

## Baseline recommendations

### TransE (core)
- Artifacts found: `30`
- Useful for recompute: `0`
- Splits detected all: `['train', 'unknown', 'valid']`
- Splits detected useful: `[]`
- Recommendation: **CHECKPOINT_FOUND_NEEDS_TOP20_EXPORT**
- Artifact type counts: `{'baseline_related': 7, 'metrics_or_report': 20, 'checkpoint_or_embedding': 2, 'unknown': 1}`

Top artifact candidates:
- `archive_pre_n2/dataset/setting_a/17_structure_baselines/transe_valid_case_samples.json`
  - type: `baseline_related` | split: `valid` | size_mb: `0.0027` | score: `11`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/dataset/setting_a/17_structure_baselines/transe_valid_metrics.json`
  - type: `metrics_or_report` | split: `valid` | size_mb: `0.0005` | score: `11`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/scripts/week8/08_eval_transe_structure_baseline.py`
  - type: `metrics_or_report` | split: `unknown` | size_mb: `0.0087` | score: `11`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/dataset/setting_a/17_structure_baselines/transe_valid_scores.pt`
  - type: `checkpoint_or_embedding` | split: `valid` | size_mb: `3.4363` | score: `10`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/dataset/setting_a/17_structure_baselines/transe_valid_top1_frequency.tsv`
  - type: `baseline_related` | split: `valid` | size_mb: `0.005` | score: `10`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/results/week8/transe_baseline_full_v1/transe_train_log.jsonl`
  - type: `metrics_or_report` | split: `train` | size_mb: `0.0046` | score: `9`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/scripts/week8/07_train_transe_baseline.py`
  - type: `metrics_or_report` | split: `train` | size_mb: `0.0117` | score: `9`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/results/week8/transe_baseline_full_v1/transe_meta.json`
  - type: `baseline_related` | split: `unknown` | size_mb: `0.001` | score: `8`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/reports/week8/day5_complex_or_transe.md`
  - type: `metrics_or_report` | split: `unknown` | size_mb: `0.0003` | score: `7`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/results/week8/baseline_table_v0/setting_a_structure_table_v0.csv`
  - type: `metrics_or_report` | split: `unknown` | size_mb: `0.0006` | score: `7`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`

### ComplEx (core)
- Artifacts found: `33`
- Useful for recompute: `0`
- Splits detected all: `['train', 'unknown', 'valid']`
- Splits detected useful: `[]`
- Recommendation: **CHECKPOINT_FOUND_NEEDS_TOP20_EXPORT**
- Artifact type counts: `{'baseline_related': 7, 'metrics_or_report': 23, 'checkpoint_or_embedding': 2, 'unknown': 1}`

Top artifact candidates:
- `archive_pre_n2/dataset/setting_a/17_structure_baselines/complex_valid_case_samples.json`
  - type: `baseline_related` | split: `valid` | size_mb: `0.0027` | score: `11`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/dataset/setting_a/17_structure_baselines/complex_valid_metrics.json`
  - type: `metrics_or_report` | split: `valid` | size_mb: `0.0005` | score: `11`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/scripts/week8/06_eval_complex_structure_baseline.py`
  - type: `metrics_or_report` | split: `unknown` | size_mb: `0.01` | score: `11`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/dataset/setting_a/17_structure_baselines/complex_valid_scores.pt`
  - type: `checkpoint_or_embedding` | split: `valid` | size_mb: `3.4363` | score: `10`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/dataset/setting_a/17_structure_baselines/complex_valid_top1_frequency.tsv`
  - type: `baseline_related` | split: `valid` | size_mb: `0.0039` | score: `10`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/results/week8/complex_baseline_full_v1/complex_train_log.jsonl`
  - type: `metrics_or_report` | split: `train` | size_mb: `0.0046` | score: `9`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/scripts/week8/05_train_complex_baseline.py`
  - type: `metrics_or_report` | split: `train` | size_mb: `0.0134` | score: `9`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/results/week8/complex_baseline_full_v1/complex_meta.json`
  - type: `baseline_related` | split: `unknown` | size_mb: `0.001` | score: `8`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/reports/week8/day5_complex_or_transe.md`
  - type: `metrics_or_report` | split: `unknown` | size_mb: `0.0003` | score: `7`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/results/week8/baseline_table_v0/setting_a_structure_table_v0.csv`
  - type: `metrics_or_report` | split: `unknown` | size_mb: `0.0006` | score: `7`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`

### R-GCN (core)
- Artifacts found: `161`
- Useful for recompute: `0`
- Splits detected all: `['test', 'train', 'unknown', 'valid']`
- Splits detected useful: `[]`
- Recommendation: **NEEDS_SCHEMA_INSPECTION_OR_STANDARDIZATION**
- Artifact type counts: `{'baseline_related': 6, 'metrics_or_report': 51, 'checkpoint_or_embedding': 7, 'candidate_rows_with_metrics': 5, 'candidate_or_ranking_rows': 23, 'unknown': 47, 'script': 12, 'score_file': 8, 'candidate_related_unknown_schema': 2}`

Top artifact candidates:
- `archive_pre_n2/dataset/setting_a/17_structure_baselines/rgcn_valid_case_samples.json`
  - type: `baseline_related` | split: `valid` | size_mb: `0.0029` | score: `11`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/dataset/setting_a/17_structure_baselines/rgcn_valid_metrics.json`
  - type: `metrics_or_report` | split: `valid` | size_mb: `0.0006` | score: `11`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/scripts/week8/02_eval_rgcn_structure_baseline.py`
  - type: `metrics_or_report` | split: `unknown` | size_mb: `0.0122` | score: `11`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/dataset/setting_a/17_structure_baselines/rgcn_valid_scores.pt`
  - type: `checkpoint_or_embedding` | split: `valid` | size_mb: `3.4363` | score: `10`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/dataset/setting_a/17_structure_baselines/rgcn_valid_top1_frequency.tsv`
  - type: `baseline_related` | split: `valid` | size_mb: `0.0001` | score: `10`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/reports/week8/day2_rgcn_baseline.md`
  - type: `metrics_or_report` | split: `unknown` | size_mb: `0.0011` | score: `9`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/results/week5/backbone_llama32_3b_rgcn/eval_valid_prediction.json`
  - type: `candidate_rows_with_metrics` | split: `valid` | size_mb: `3.4888` | score: `8`
  - can_recompute: `False` | candidate_fields: `['prediction']` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/results/week6/backbone_llama32_3b_rgcn_real/valid_eval/eval_valid_prediction.json`
  - type: `candidate_rows_with_metrics` | split: `valid` | size_mb: `3.5455` | score: `8`
  - can_recompute: `False` | candidate_fields: `['prediction']` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/results/week8/baseline_table_v0/setting_a_structure_table_v0.csv`
  - type: `metrics_or_report` | split: `unknown` | size_mb: `0.0006` | score: `7`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/results/week8/baseline_table_v0/setting_a_structure_table_v0.md`
  - type: `metrics_or_report` | split: `unknown` | size_mb: `0.0011` | score: `7`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`

### HRGAT (core)
- Artifacts found: `33`
- Useful for recompute: `0`
- Splits detected all: `['train', 'unknown', 'valid']`
- Splits detected useful: `[]`
- Recommendation: **CHECKPOINT_FOUND_NEEDS_TOP20_EXPORT**
- Artifact type counts: `{'baseline_related': 9, 'metrics_or_report': 19, 'checkpoint_or_embedding': 4, 'unknown': 1}`

Top artifact candidates:
- `archive_pre_n2/dataset/setting_a/17_structure_baselines/hrgat_valid_case_samples.json`
  - type: `baseline_related` | split: `valid` | size_mb: `0.0028` | score: `11`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/dataset/setting_a/17_structure_baselines/hrgat_valid_metrics.json`
  - type: `metrics_or_report` | split: `valid` | size_mb: `0.0006` | score: `11`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/scripts/week8/04_eval_hrgat_structure_baseline.py`
  - type: `metrics_or_report` | split: `unknown` | size_mb: `0.0134` | score: `11`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/dataset/setting_a/17_structure_baselines/hrgat_valid_scores.pt`
  - type: `checkpoint_or_embedding` | split: `valid` | size_mb: `3.4363` | score: `10`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/dataset/setting_a/17_structure_baselines/hrgat_valid_top1_frequency.tsv`
  - type: `baseline_related` | split: `valid` | size_mb: `0.004` | score: `10`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/results/week8/hrgat_baseline/hrgat_train_log.jsonl`
  - type: `metrics_or_report` | split: `train` | size_mb: `0.0026` | score: `9`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/results/week8/hrgat_baseline_full_v1/hrgat_train_log.jsonl`
  - type: `metrics_or_report` | split: `train` | size_mb: `0.0026` | score: `9`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/results/week8/hrgat_baseline_smoke/hrgat_train_log.jsonl`
  - type: `metrics_or_report` | split: `train` | size_mb: `0.0003` | score: `9`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/scripts/week8/03_train_hrgat_baseline.py`
  - type: `metrics_or_report` | split: `train` | size_mb: `0.0148` | score: `9`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/results/week8/hrgat_baseline/hrgat_meta.json`
  - type: `baseline_related` | split: `unknown` | size_mb: `0.001` | score: `8`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`

### DistMult (optional)
- Artifacts found: `6`
- Useful for recompute: `0`
- Splits detected all: `['train', 'unknown']`
- Splits detected useful: `[]`
- Recommendation: **NEEDS_SCHEMA_INSPECTION_OR_STANDARDIZATION**
- Artifact type counts: `{'metrics_or_report': 5, 'score_file': 1}`

Top artifact candidates:
- `reports/week21/day1_baseline_protocol_freeze.md`
  - type: `metrics_or_report` | split: `unknown` | size_mb: `0.003` | score: `3`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `True`
- `results/week21/baseline_protocol_freeze.json`
  - type: `metrics_or_report` | split: `unknown` | size_mb: `0.005` | score: `3`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `scripts/week21/01_freeze_baseline_protocol.py`
  - type: `metrics_or_report` | split: `unknown` | size_mb: `0.0119` | score: `3`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `True`
- `scripts/week21/02_inventory_baselines.py`
  - type: `metrics_or_report` | split: `unknown` | size_mb: `0.0285` | score: `3`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `True`
- `archive_pre_n2/scripts/week7/02_train_rgcn_ranker_v2.py`
  - type: `metrics_or_report` | split: `train` | size_mb: `0.0281` | score: `1`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `archive_pre_n2/scripts/week7/03_score_queries_v2.py`
  - type: `score_file` | split: `unknown` | size_mb: `0.0148` | score: `0`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`

### RotatE (optional)
- Artifacts found: `4`
- Useful for recompute: `0`
- Splits detected all: `['unknown']`
- Splits detected useful: `[]`
- Recommendation: **METRICS_ONLY_NEEDS_RERUN_OR_RAW_OUTPUT**
- Artifact type counts: `{'metrics_or_report': 4}`

Top artifact candidates:
- `reports/week21/day1_baseline_protocol_freeze.md`
  - type: `metrics_or_report` | split: `unknown` | size_mb: `0.003` | score: `3`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `True`
- `results/week21/baseline_protocol_freeze.json`
  - type: `metrics_or_report` | split: `unknown` | size_mb: `0.005` | score: `3`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `False`
- `scripts/week21/01_freeze_baseline_protocol.py`
  - type: `metrics_or_report` | split: `unknown` | size_mb: `0.0119` | score: `3`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `True`
- `scripts/week21/02_inventory_baselines.py`
  - type: `metrics_or_report` | split: `unknown` | size_mb: `0.0285` | score: `3`
  - can_recompute: `False` | candidate_fields: `[]` | score_fields: `[]` | injection_hint: `True`

## Possible MRR around 0.13 hits

- `scripts/week21/02_inventory_baselines.py`
  - models_detected: `['ComplEx', 'DistMult', 'HRGAT', 'R-GCN', 'RotatE', 'TransE']`
  - split_detected: `unknown`
  - line: `# MRR around 0.13 search`
  - numeric_values: `[0.13]`
- `scripts/week21/02_inventory_baselines.py`
  - models_detected: `['ComplEx', 'DistMult', 'HRGAT', 'R-GCN', 'RotatE', 'TransE']`
  - split_detected: `unknown`
  - line: `lines.append("## Possible MRR around 0.13 hits\n")`
  - numeric_values: `[0.13]`
- `scripts/week21/02_inventory_baselines.py`
  - models_detected: `['ComplEx', 'DistMult', 'HRGAT', 'R-GCN', 'RotatE', 'TransE']`
  - split_detected: `unknown`
  - line: `lines.append("No automatic MRR≈0.13 hit was found. Manual check may still be needed.\n")`
  - numeric_values: `[0.13]`
- `scripts/week21/02_inventory_baselines.py`
  - models_detected: `['ComplEx', 'DistMult', 'HRGAT', 'R-GCN', 'RotatE', 'TransE']`
  - split_detected: `unknown`
  - line: `lines.append("1. Baseline MRR khoảng 0.13 trước đây là model nào?")`
  - numeric_values: `[0.13]`
- `scripts/week21/02_inventory_baselines.py`
  - models_detected: `['ComplEx', 'DistMult', 'HRGAT', 'R-GCN', 'RotatE', 'TransE']`
  - split_detected: `unknown`
  - line: `print(f"Possible MRR≈0.13 hits: {len(inventory['possible_mrr_around_0_13_hits'])}")`
  - numeric_values: `[0.13]`
- `archive_pre_n2/reports/week8/day6_table_v0.md`
  - models_detected: `['ComplEx', 'HRGAT', 'R-GCN', 'TransE']`
  - split_detected: `unknown`
  - line: `- ComplEx: MRR=0.13171101, Hits@10=0.41`
  - numeric_values: `[0.13171101, 0.41]`
- `archive_pre_n2/results/week8/complex_baseline_full_v1/complex_train_log.jsonl`
  - models_detected: `['ComplEx']`
  - split_detected: `train`
  - key/value: `[2].probe_mrr` = `0.1217542`
- `archive_pre_n2/results/week8/baseline_table_v0/setting_a_structure_table_v0_preview.txt`
  - models_detected: `['ComplEx', 'HRGAT', 'R-GCN', 'TransE']`
  - split_detected: `unknown`
  - line: `ComplEx: MRR=0.13171101, Hits@10=0.41`
  - numeric_values: `[0.13171101, 0.41]`
- `archive_pre_n2/dataset/setting_a/17_structure_baselines/complex_valid_metrics.json`
  - models_detected: `['ComplEx']`
  - split_detected: `valid`
  - key/value: `mrr` = `0.13171101`

## End-of-day questions

Answer these manually after inspecting the artifacts above:

1. Baseline MRR khoảng 0.13 trước đây là model nào?
2. Nó là valid hay test?
3. Task có đúng `(? drug, indication, disease)` không?
4. Candidate universe có phải `drug_only` không?
5. Metric có phải reviewer-safe top-20 không, hay chỉ là old/full-ranking/proxy metric?
6. Core baselines nào có thể recollect, baseline nào phải rerun?

## Next step

Day 3 should use this inventory to either recollect existing top-20 rows or rerun/export missing baseline outputs into `results/week21/baseline_outputs/{model_name}/{split}_top20.json`.
