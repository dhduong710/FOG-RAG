# Week 28 Day 4 — repoDB source selection

- Decision: `DAY4_REPODB_SOURCE_RGCN_READY`
- Recommended primary source: `rgcn`
- Source path: `dataset/setting_f_repodb/04_baseline_outputs/rgcn`
- Embedding path: `dataset/setting_f_repodb/04_baseline_outputs/rgcn/entity_embeddings_rgcn.pt`

## Best validation model

```json
{
  "model_name": "distmult",
  "split": "valid",
  "gold_present_at20": 0.51,
  "mrr_at20": 0.1012765240435519,
  "hits1_at20": 0.016,
  "hits3_at20": 0.094,
  "hits10_at20": 0.362,
  "gold_rank_21_count": 245,
  "top1_dominance": 0.134
}
```

## Best test model

```json
{
  "model_name": "distmult",
  "split": "test",
  "gold_present_at20": 0.482,
  "mrr_at20": 0.10413942877727705,
  "hits1_at20": 0.026,
  "hits3_at20": 0.094,
  "hits10_at20": 0.32,
  "gold_rank_21_count": 259,
  "top1_dominance": 0.146
}
```

## R-GCN metrics

```json
{
  "valid": {
    "model_name": "rgcn",
    "split": "valid",
    "gold_present_at20": 0.236,
    "mrr_at20": 0.05702382453288026,
    "hits1_at20": 0.026,
    "hits3_at20": 0.048,
    "hits10_at20": 0.144,
    "gold_rank_21_count": 382,
    "top1_dominance": 0.528
  },
  "test": {
    "model_name": "rgcn",
    "split": "test",
    "gold_present_at20": 0.214,
    "mrr_at20": 0.04813962250339959,
    "hits1_at20": 0.018,
    "hits3_at20": 0.04,
    "hits10_at20": 0.128,
    "gold_rank_21_count": 393,
    "top1_dominance": 0.512
  }
}
```

## Source policy

Prefer R-GCN as the graph-compatible DrKGC/SoftFuse source if it has non-trivial Gold@20. Report all six structure baselines. If another model is best by validation MRR, describe it as the strongest structure-only candidate generator. For repoDB, clinical validation value is more important than claiming universal baseline superiority.
