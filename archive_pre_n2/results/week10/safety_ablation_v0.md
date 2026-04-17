# Week 10 Safety Ablation v0

| Row | MRR | Hits@1 | Hits@3 | Hits@10 | ContraFinal | QueryHasContraRate | GoldInTopKRate | FallbackAfterHard | SoftDemotedContra |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Backbone (week7-v2) | 0.424249 | 0.368000 | 0.394000 | 0.510000 | - | - | - | - | - |
| + Ontology (week9) | 0.313018 | 0.244000 | 0.278000 | 0.434000 | 73 | 0.076000 | 0.292000 | 0 | 0 |
| + Ontology + Hard | 0.393101 | 0.330000 | 0.358000 | 0.524000 | 0 | 0.000000 | 0.312000 | 13 | 0 |
| + Ontology + Soft | 0.393101 | 0.330000 | 0.358000 | 0.524000 | 73 | 0.076000 | 0.292000 | 0 | 52 |

## Main takeaway
- main_row: `hard_main`
- supporting_row: `soft_best`
- reason: Ranking metrics are identical, while hard_main fully removes contraindicated final candidates.
