# Week 24 Day 1 — PrimeKG E2E Protocol Audit

## Decision

**PRIMEKG_E2E_PROTOCOL_READY**

## Frozen protocol

- Dataset: `PrimeKG-derived Setting A`
- Task: `(? , indication, disease) head prediction`
- Candidate universe: `drug_only`
- Rows: `backbone_raw, soft_support_raw, retrieval_main`
- Top-k: `20`
- Graph num relations: `4`
- KGE embedding: `/home/anhlq/Documents/2026-dhd/FOG-RAG/dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt`
- KGE shape: `[10453, 256]`
- Reviewer-safe RR: `1/rank if rank <= 20 else 0`

## Row summaries

### backbone_raw

| Split | Rows | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Rank21 | Avg subgraph | Max rel | Max ent | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train | 8388 |  |  |  |  |  |  | 73.63340486 | 3 | 10452 | 0 |
| valid | 500 | 0.202 | 0.05380338 | 0.024 | 0.046 | 0.158 | 399 | 60.45 | 3 | 10452 | 0 |
| test | 500 | 0.24 | 0.06456283 | 0.024 | 0.07 | 0.192 | 380 | 59.932 | 3 | 10452 | 0 |

### soft_support_raw

| Split | Rows | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Rank21 | Avg subgraph | Max rel | Max ent | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train | 8388 |  |  |  |  |  |  | 73.63340486 | 3 | 10452 | 0 |
| valid | 500 | 0.202 | 0.09764372 | 0.056 | 0.134 | 0.182 | 399 | 60.45 | 3 | 10452 | 0 |
| test | 500 | 0.24 | 0.12532618 | 0.072 | 0.166 | 0.222 | 380 | 59.932 | 3 | 10452 | 0 |

### retrieval_main

| Split | Rows | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Rank21 | Avg subgraph | Max rel | Max ent | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train | 8388 |  |  |  |  |  |  | 73.63340486 | 3 | 10452 | 0 |
| valid | 500 | 0.202 | 0.09764372 | 0.056 | 0.134 | 0.182 | 399 | 32.556 | 3 | 10452 | 0 |
| test | 500 | 0.24 | 0.12532618 | 0.072 | 0.166 | 0.222 | 380 | 32.34 | 3 | 10452 | 0 |

## Cross-row checks

- `soft_vs_retrieval_candidate_order_valid`: `{'num_compared': 500, 'same_candidate_names_rate': 1.0, 'same_candidate_ids_rate': 1.0}`
- `backbone_vs_soft_candidate_order_valid`: `{'num_compared': 500, 'same_candidate_names_rate': 0.09, 'same_candidate_ids_rate': 0.09}`
- `soft_vs_retrieval_candidate_order_test`: `{'num_compared': 500, 'same_candidate_names_rate': 1.0, 'same_candidate_ids_rate': 1.0}`
- `backbone_vs_soft_candidate_order_test`: `{'num_compared': 500, 'same_candidate_names_rate': 0.1, 'same_candidate_ids_rate': 0.1}`

## Important notes for Week 24

- Use `--graph_num_rels 4` for PrimeKG.
- Do not use raw `infer.py` MRR as paper metric.
- Day 2 decoding sweep must use valid only.
- `retrieval_main` is paper-facing main row if it preserves soft-support E2E while reducing subgraph size.
- Larger base LLMs are diagnostic unless they improve E2E and keep invalid rate reasonable.