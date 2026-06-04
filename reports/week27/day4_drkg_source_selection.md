# Week 27 Day 4 — DRKG source selection

- Decision: `DAY4_DRKG_SOURCE_RGCN_READY`
- Recommended primary source: `rgcn`
- Source path: `dataset/setting_e_drkg/04_baseline_outputs/rgcn`
- Embedding path: `dataset/setting_e_drkg/04_baseline_outputs/rgcn/entity_embeddings_rgcn.pt`

## Best validation model

```json
{
  "model_name": "distmult",
  "split": "valid",
  "gold_present_at20": 0.444,
  "mrr_at20": 0.10271677325082898,
  "hits1_at20": 0.02,
  "hits3_at20": 0.108,
  "hits10_at20": 0.324,
  "gold_rank_21_count": 278,
  "top1_dominance": 0.07
}
```

## Best test model

```json
{
  "model_name": "distmult",
  "split": "test",
  "gold_present_at20": 0.432,
  "mrr_at20": 0.0996747976138069,
  "hits1_at20": 0.034,
  "hits3_at20": 0.092,
  "hits10_at20": 0.276,
  "gold_rank_21_count": 284,
  "top1_dominance": 0.074
}
```

## R-GCN metrics

```json
{
  "valid": {
    "model_name": "rgcn",
    "split": "valid",
    "gold_present_at20": 0.218,
    "mrr_at20": 0.06140422852001799,
    "hits1_at20": 0.026,
    "hits3_at20": 0.054,
    "hits10_at20": 0.164,
    "gold_rank_21_count": 391,
    "top1_dominance": 1.0
  },
  "test": {
    "model_name": "rgcn",
    "split": "test",
    "gold_present_at20": 0.2,
    "mrr_at20": 0.0432420445911158,
    "hits1_at20": 0.01,
    "hits3_at20": 0.042,
    "hits10_at20": 0.12,
    "gold_rank_21_count": 400,
    "top1_dominance": 1.0
  }
}
```

## Missing models

```json
[]
```
