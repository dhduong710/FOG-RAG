# Week 21 Day 3 — Rerun All Structure Baselines

## Decision

**ALL_BASELINES_RERUN_EXPORTED_TOP20_READY_FOR_DAY4_METRIC_RECOMPUTE**

## Protocol reminder

- Baselines are evaluated as upstream top-20 candidate generators.
- This is not a classical full-universe filtered KGC metric.
- Gold injection is forbidden.
- Reviewer-safe metrics will be recomputed on Day 4.

## Data summary

- Train rows path: `dataset/setting_a/29_n2_e2e_infer_ready/backbone_raw/train.json`
- Enriched KG path: `dataset/setting_a/02_graph/train_enriched_deg1000_final.tsv`
- Number of train triples: `136351`
- Number of train indication pairs: `8388`
- Number of entities: `17742`
- Number of relations: `4`
- Drug-only candidate universe size: `1801`
- Valid rows: `500`
- Test rows: `500`

## Model output summary

| Model | Valid rows | Valid Gold@20 raw | Test rows | Test Gold@20 raw | Output dir |
|---|---:|---:|---:|---:|---|
| `transe` | 500 | 0.1040 | 500 | 0.1040 | `results/week21/baseline_outputs/transe` |
| `distmult` | 500 | 0.3540 | 500 | 0.4340 | `results/week21/baseline_outputs/distmult` |
| `complex` | 500 | 0.5600 | 500 | 0.5740 | `results/week21/baseline_outputs/complex` |
| `rotate` | 500 | 0.1380 | 500 | 0.1340 | `results/week21/baseline_outputs/rotate` |
| `rgcn` | 500 | 0.1620 | 500 | 0.2200 | `results/week21/baseline_outputs/rgcn` |
| `hrgat` | 500 | 0.1640 | 500 | 0.2120 | `results/week21/baseline_outputs/hrgat` |

## Files produced

### transe
- `results/week21/baseline_outputs/transe/valid_top20.json`
- `results/week21/baseline_outputs/transe/test_top20.json`
- `results/week21/baseline_outputs/transe/config.json`
- `results/week21/baseline_outputs/transe/train_log.json`
- `results/week21/baseline_outputs/transe/summary.json`
### distmult
- `results/week21/baseline_outputs/distmult/valid_top20.json`
- `results/week21/baseline_outputs/distmult/test_top20.json`
- `results/week21/baseline_outputs/distmult/config.json`
- `results/week21/baseline_outputs/distmult/train_log.json`
- `results/week21/baseline_outputs/distmult/summary.json`
### complex
- `results/week21/baseline_outputs/complex/valid_top20.json`
- `results/week21/baseline_outputs/complex/test_top20.json`
- `results/week21/baseline_outputs/complex/config.json`
- `results/week21/baseline_outputs/complex/train_log.json`
- `results/week21/baseline_outputs/complex/summary.json`
### rotate
- `results/week21/baseline_outputs/rotate/valid_top20.json`
- `results/week21/baseline_outputs/rotate/test_top20.json`
- `results/week21/baseline_outputs/rotate/config.json`
- `results/week21/baseline_outputs/rotate/train_log.json`
- `results/week21/baseline_outputs/rotate/summary.json`
### rgcn
- `results/week21/baseline_outputs/rgcn/valid_top20.json`
- `results/week21/baseline_outputs/rgcn/test_top20.json`
- `results/week21/baseline_outputs/rgcn/config.json`
- `results/week21/baseline_outputs/rgcn/train_log.json`
- `results/week21/baseline_outputs/rgcn/summary.json`
### hrgat
- `results/week21/baseline_outputs/hrgat/valid_top20.json`
- `results/week21/baseline_outputs/hrgat/test_top20.json`
- `results/week21/baseline_outputs/hrgat/config.json`
- `results/week21/baseline_outputs/hrgat/train_log.json`
- `results/week21/baseline_outputs/hrgat/summary.json`

## Next step

Day 4 should recompute reviewer-safe metrics for all baseline outputs and FOG-RAG rows with the frozen rule: RR = 1/rank if rank <= 20 else 0; absent gold has rank 21 and RR 0.
