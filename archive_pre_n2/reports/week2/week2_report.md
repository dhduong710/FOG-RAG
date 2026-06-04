# Week 2 Report

## Objective
Week 2 focused on **benchmark lock and data-pipeline construction**, not full training or metric chasing.

The Week-2 exit gate required:
- fixed Setting A split
- clear Setting B role
- candidate JSON
- prompt/subgraph-ready JSON
- sanity-checked preprocessing pipeline

---

## Day 1 — PrimeKG extraction and raw Setting A benchmark
Completed:
- downloaded PrimeKG raw `kg.csv`
- extracted the biomedical task subset:
  - `(drug, indication, disease)`
- canonical task framing locked as:
  - query format: `(?, indication, disease)`
  - candidate type: `drug`

Key result:
- raw indication triples: `9388`

Status:
- pass

---

## Day 2 — Fixed split for Setting A
Completed:
- locked split:
  - train: `8388`
  - valid: `500`
  - test: `500`
- fixed seed: `2025`
- ensured entity coverage:
  - valid/test drugs appear in train
  - valid/test diseases appear in train

Status:
- pass

---

## Day 3 — Enriched Setting A train graph
Completed:
- added support relations:
  - `target`
  - `associated_with`
  - `ppi`
- fixed raw alias mismatch:
  - `associated with` normalized to `associated_with`
- audited PPI counting
- discovered that raw PrimeKG PPI is stored in both directions
- switched to unordered-collapsed PPI counting
- selected final hub cap:
  - `max_gene_degree = 1000`

Final graph stats:
- train indication: `8388`
- target: `6131`
- associated_with: `48271`
- ppi: `73561`
- total enriched: `136351`
- entities: `10453`

Status:
- pass

Notes:
- graph size is close enough to paper scale for Week-2 purposes
- entity-count difference vs paper is recorded as a convention difference, not a blocking issue

---

## Day 4 — Setting B semantic lock
Completed:
- Setting B reuses the exact Setting A split
- main task remains unchanged:
  - `(?, indication, disease)`
- candidate type remains:
  - `drug`
- contraindication is treated only as an auxiliary safety signal

Created artifacts:
- `contraindication_edges_full.tsv`
- `contraindication_edges_overlap.tsv`
- `contra_by_disease.json`
- `contra_by_drug.json`
- ontology/type maps
- domain-range rules
- safety-eval config

Key stats:
- full contraindication triples: `30675`
- overlap contraindication triples: `16097`
- type conflicts: `94`
- missing split entities: `0`

Status:
- pass

---

## Day 5 — ID maps and JSON skeleton
Completed:
- built:
  - `entity2id`
  - `id2entity`
  - `relation2id`
  - `id2relation`
- created:
  - `train_skeleton.json`
  - `valid_skeleton.json`
  - `test_skeleton.json`

Key stats:
- num_entities: `10453`
- num_relations: `4`
- relations:
  - `associated_with`
  - `indication`
  - `ppi`
  - `target`

Status:
- pass

---

## Day 6 — Mock coarse ranker
Completed:
- built deterministic mock candidate lists
- candidate type restricted to `drug`
- gold guaranteed in list
- fixed `K = 20`
- exported:
  - candidate JSON
  - DrKGC-ready ranked JSON

Key stats:
- train-drug universe: `1801`
- candidate size: `20`

Status:
- pass

Notes:
- this is a pipeline-locking mock ranker, not a learned coarse ranker

---

## Day 7 — Prompt/subgraph subset smoke test
Completed:
- prepared 20-sample subset
- ran `prompt_subgraph.py`
- verified prompt/subgraph-ready JSON output

Important bug found and fixed:
- original graph construction used `train + valid`
- this caused exact gold triple leakage in validation
- fixed by building retrieval graph from **train only**

Final leakage audit:
- `valid exact leak count = 0`
- `test exact leak count = 0`

Status:
- pass

---

## What is locked at the end of Week 2
1. Setting A benchmark split is locked
2. Setting A graph-construction convention is locked
3. Canonical internal relation names are locked
4. Setting B semantic role is locked
5. ID maps and JSON schema are locked
6. Mock coarse ranker format is locked
7. Prompt/subgraph preprocessing passes subset smoke test
8. Validation/test exact leakage is fixed

---

## What is still temporary
The following parts are intentionally temporary at the end of Week 2:
- mock coarse ranker
- 20-sample prompt/subgraph smoke test only
- no learned retrieval or reranking yet
- no ontology-based filtering yet
- no contraindication hard filter / soft penalty implementation yet
- no full-scale training run yet

---

## Go / No-Go decision for Week 3
Decision: **GO**

Reason:
- all Week-2 exit-gate artifacts are present
- split A is locked
- Setting B role is locked
- candidate JSON exists
- prompt/subgraph-ready preprocessing works
- clean-eval leakage issue has been fixed

---

## Recommended Week-3 starting point
Start Week 3 with:
- finalizing Setting B operational protocol
- building type-safe / ontology-aware candidate logic
- preparing safety-aware evaluation hooks
- keeping Week-2 locked artifacts unchanged unless changes are explicitly versioned