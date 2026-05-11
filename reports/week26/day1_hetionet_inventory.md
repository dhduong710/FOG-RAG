# Week 26 Day 1 — Hetionet raw inventory

- Created at: `2026-05-11T13:03:27.838674+00:00`
- Setting: `setting_d_hetionet`
- Download source: Zenodo Hetionet v1.0.0

## Raw files detected

- Nodes found: `True`
- Edges found: `True`
- Metaedges found: `True`
- Metanodes found: `True`

## Node inventory

- Number of node rows: `47031`
- Node type counts:
  - `Gene`: 20945
  - `Biological Process`: 11381
  - `Side Effect`: 5734
  - `Molecular Function`: 2884
  - `Pathway`: 1822
  - `Compound`: 1552
  - `Cellular Component`: 1391
  - `Symptom`: 438
  - `Anatomy`: 402
  - `Pharmacologic Class`: 345
  - `Disease`: 137

## Edge inventory

- Number of edge rows: `2250197`
- Top metaedge counts:
  - `GpBP`: 559504
  - `AeG`: 526407
  - `Gr>G`: 265672
  - `GiG`: 147164
  - `CcSE`: 138944
  - `AdG`: 102240
  - `AuG`: 97848
  - `GpMF`: 97222
  - `GpPW`: 84372
  - `GpCC`: 73566
  - `GcG`: 61690
  - `CdG`: 21102
  - `CuG`: 18756
  - `DaG`: 12623
  - `CbG`: 11571
  - `DuG`: 7731
  - `DdG`: 7623
  - `CrC`: 6486
  - `DlA`: 3602
  - `DpS`: 3357
  - `PCiC`: 1029
  - `CtD`: 755
  - `DrD`: 543
  - `CpD`: 390

## Candidate task summary

### `CtD` — Compound-treats-Disease
- Edges: `755`
- Unique compounds: `387`
- Unique diseases: `77`

### `CpD` — Compound-palliates-Disease
- Edges: `390`
- Unique compounds: `221`
- Unique diseases: `50`

## Draft task decision

```json
{
  "task_name": "hetionet_compound_treats_disease_head_prediction",
  "task_form": "(?, CtD, disease)",
  "prediction_type": "predicted_head",
  "target_relation_code": "CtD",
  "target_relation_name": "Compound-treats-Disease",
  "query_entity_type": "Disease",
  "missing_entity_type": "Compound",
  "candidate_universe": "Compound nodes; final universe to be frozen on Day 2 after coverage checks.",
  "top_k": 20,
  "gold_injection": false,
  "absent_gold_rank_sentinel": 21,
  "paper_claim_level": "Classic drug-repurposing / compound-disease treatment external validation, not clinical validation."
}
```
