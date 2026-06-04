# Ontology-only Ablation v0

| Row | MRR | Hits@1 | Hits@3 | Hits@10 | Notes |
|---|---:|---:|---:|---:|---|
| backbone_reference | 0.42424878 | 0.36800000 | 0.39399999 | 0.50999999 | week7-v2 main reference |
| backbone_plus_ontology | 0.31301793 | 0.24400000 | 0.27800000 | 0.43400000 | week9 ontology-only sanity row |

## Delta (ontology - backbone)
- ΔMRR: -0.11123085
- ΔHits@1: -0.12400000
- ΔHits@3: -0.11599999
- ΔHits@10: -0.07599999

## Constraint-side context
- ConstraintViolationRate: 0.51046452
- QueryHasConstraintViolationRate: 0.2
- fallback_queries: 100
- gold_in_topk_ontology: 146
- unsupported_final_candidates: 2000

## Interpretation
- ontology-only branch is traceable and runnable.
- current row is conservative and affected by strict-empty queries plus fallback.
- use this row as groundwork/supporting evidence, not as the final winning novelty row.
