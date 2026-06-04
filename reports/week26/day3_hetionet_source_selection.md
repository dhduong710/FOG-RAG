# Week 26 Day 3 — Hetionet source selection

## Decision

`DAY3_HETIONET_SOURCE_RGCN_READY`

## Recommended source

- Primary source: `rgcn`
- Source folder: `dataset/setting_d_hetionet/04_baseline_outputs/rgcn`
- Valid top20: `dataset/setting_d_hetionet/04_baseline_outputs/rgcn/valid_top20.json`
- Test top20: `dataset/setting_d_hetionet/04_baseline_outputs/rgcn/test_top20.json`
- Embedding: `dataset/setting_d_hetionet/04_baseline_outputs/rgcn/entity_embeddings_rgcn.pt`

## Rationale

R-GCN is selected as the primary FOG-RAG/DrKGC-ready source for consistency with PrimeKG, PharmKG, and the graph-adapter setting. All six baselines remain in the structure-only comparison table.

## Best validation model by MRR

```json
{
  "model_name": "complex",
  "split": "valid",
  "gold_present_at20": 0.4,
  "mrr_at20": 0.07536615955424004,
  "hits1_at20": 0.02,
  "hits3_at20": 0.07,
  "hits10_at20": 0.21,
  "gold_rank_21_count": 60,
  "top1_dominance": 0.22
}
```

## Best test model by MRR

```json
{
  "model_name": "hrgat",
  "split": "test",
  "gold_present_at20": 0.41,
  "mrr_at20": 0.10130366752270778,
  "hits1_at20": 0.04,
  "hits3_at20": 0.08,
  "hits10_at20": 0.29,
  "gold_rank_21_count": 59,
  "top1_dominance": 1.0
}
```

## R-GCN validation/test

```json
{
  "valid": {
    "model_name": "rgcn",
    "split": "valid",
    "gold_present_at20": 0.43,
    "mrr_at20": 0.057457932375502035,
    "hits1_at20": 0.01,
    "hits3_at20": 0.04,
    "hits10_at20": 0.19,
    "gold_rank_21_count": 57,
    "top1_dominance": 1.0
  },
  "test": {
    "model_name": "rgcn",
    "split": "test",
    "gold_present_at20": 0.44,
    "mrr_at20": 0.09944529326882268,
    "hits1_at20": 0.04,
    "hits3_at20": 0.11,
    "hits10_at20": 0.22,
    "gold_rank_21_count": 56,
    "top1_dominance": 1.0
  },
  "files_ready": {
    "valid_top20": true,
    "test_top20": true,
    "entity_embeddings_rgcn": true
  }
}
```

## Missing models

```json
[]
```
