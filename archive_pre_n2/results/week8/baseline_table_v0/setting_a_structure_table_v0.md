# Setting A Structure-only Baselines (v0)

## Protocol
- Task: head prediction `(?, indication, disease)`
- Universe: drug-only
- Decision split: valid
- Main metrics: MRR, Hits@1, Hits@3, Hits@10

| Method | Category | Valid MRR | Hits@1 | Hits@3 | Hits@10 | Notes |
|---|---:|---:|---:|---:|---:|---|
| R-GCN | structure-only | 0.05388868 | 0.018 | 0.044 | 0.152 | Provisional row from week7 ranker_v2 score dump; clean structure-only eval, not yet paper-faithful reproduction. |
| HRGAT | structure-only | 0.09550672 | 0.016 | 0.066 | 0.29 | Minimal structure-only HRGAT baseline under the same clean valid-first protocol. |
| ComplEx | structure-only | 0.13171101 | 0.028 | 0.102 | 0.41 | Preferred third baseline; strongest structure-only row in current table v0. |
| TransE | structure-only | 0.08074941 | 0.014 | 0.056 | 0.244 | Bonus fourth baseline; fallback/simple translational reference. |

## Current takeaway
- ComplEx is currently the strongest structure-only row in table v0.
- HRGAT clearly improves over the provisional R-GCN row.
- TransE is a useful bonus baseline but weaker than ComplEx and HRGAT.
