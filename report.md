# Week 1 Report

## 1. What I understood

### 1.1 DrKGC backbone pipeline
After reading the paper, draft, and public codebase, I understand the DrKGC backbone as the following pipeline:

incomplete triple  
-> natural-language question construction  
-> lightweight candidate retriever  
-> dynamic subgraph retriever  
-> graph encoder / graph enhancer  
-> LLM reranking

The backbone is not a pure text-only prompting system. It combines:
- prompt text,
- candidate entities,
- retrieved evidence subgraph,
- graph-aware embeddings injected into placeholder tokens such as [QUERY] and [ENTITY].

### 1.2 What FOG-RAG will modify
FOG-RAG keeps the same overall pipeline structure, but plans to modify four major components:

- Candidate retrieval  
  -> ontology-aware and contraindication-aware candidate handling

- Evidence construction / subgraph retrieval  
  -> fuzzy confidence-aware dynamic subgraph retrieval

- Local graph encoding  
  -> fuzzy graph encoder on retrieved subgraphs

- Final ranking / explanation  
  -> grounded explanation and safety-aware reranking

### 1.3 Core task framing
The main task is still based on the query form:

(?, treats, disease)

The target is to rank candidate drugs for a disease query.

### 1.4 Setting A vs Setting B
I locked two evaluation settings:

- Setting A:
  DrKGC-compatible indication ranking for fair comparison

- Setting B:
  contraindication-aware, schema-aware, and grounding-aware extension setting

This separation is important because Setting A supports fairness against the DrKGC backbone, while Setting B evaluates the extra biomedical value of FOG-RAG.

---

## 2. What is already working

### 2.1 Environment
- A dedicated environment for DrKGC was created
- Core packages were installed
- Import sanity check worked

### 2.2 Repo structure understanding
I inspected the major files:
- main.py
- infer.py
- data/dataset.py
- data/collate.py
- model/drkgc.py
- prompt_subgraph.py

I now understand the role of each major file in the current codebase.

### 2.3 Data format understanding
I locked the minimum JSON fields required by the current DrKGC pipeline:
- input
- output
- query_entity_id
- rank_entities_id
- subgraph

I also separated:
- current backbone-required fields
- possible future FOG-RAG extension fields

### 2.4 Toy dataset for smoke testing
Because the public repo does not provide the preprocessed PrimeKG dataset files, I created a toy dataset under:

`dataset/toy_debug`

This toy dataset contains:
- train.json
- valid.json
- test.json
- entity_id_map.json
- entity_embeddings.pt

### 2.5 Smoke tests
I successfully ran:
- smoke_data.py
- smoke_collator.py
- smoke_graph_input.py

The smoke tests confirmed:
- data loading works
- collator works
- placeholder count matches candidate count
- graph input path works on small toy samples

---

## 3. What is still missing

The following parts are not finished yet and will be addressed in the next stage:

### 3.1 PrimeKG split construction
I still need to build the real dataset pipeline for:
- Setting A
- Setting B

### 3.2 Contraindication source
I still need a reliable source for contraindication edges or contraindication-aware annotations.

### 3.3 Ontology / type map
I still need:
- ontology type definitions
- domain-range rules
- schema-validity logic

### 3.4 Exact safety-aware evaluation script
I still need to define and implement:
- SafetyViolation@K
- Contra@K
- ConstraintViolationRate
- grounded explanation related metrics

### 3.5 Reproducible full training path
Week 1 only confirms smoke-test readiness.
I have not yet reproduced the full DrKGC backbone on the real benchmark.

---

## 4. Decisions locked this week

The following decisions are now locked:

### 4.1 Problem framing
The project is framed as:
contraindication-aware drug repurposing with grounded evidence

It is not framed as a clinical-safe treatment recommendation system.

### 4.2 Setting A
Setting A is kept as fair as possible to DrKGC:
- query form remains (?, treats, disease)
- candidate entities are drugs
- evaluation focuses on ranking metrics

### 4.3 Setting B
Setting B extends the task with:
- contraindication-awareness
- schema validity
- grounded evidence / explanation

### 4.4 Week 1 scope boundary
Week 1 is only for:
- reading the pipeline
- locking the spec
- setting up the environment
- running smoke tests

I should not implement full fuzzy modules or safety modules before the backbone and dataset foundations are stable.

### 4.5 Week 2 focus
Week 2 will focus on:
- building the dataset pipeline
- defining split construction
- making the data compatible with Setting A and Setting B

---

## 5. Mapping from DrKGC to FOG-RAG

| DrKGC Module | FOG-RAG Extension |
|---|---|
| Candidate Retriever | Ontology/Safety-aware Candidate Retriever |
| Subgraph Retriever | Fuzzy Dynamic Subgraph Retriever |
| GCN Adapter / Graph Enhancer | Fuzzy Graph Encoder |
| LLM Reranker | Grounded Explanation + Safety-aware Reranker |

---

## 6. Week 1 checklist

- [x] Read the problem formulation carefully
- [x] Finished week1_problem_lock.md
- [x] Finished environment setup
- [x] Successfully imported torch / transformers / peft / networkx
- [x] Understood the role of main.py, infer.py, dataset.py, collate.py, drkgc.py, prompt_subgraph.py
- [x] Finished week1_repo_map.md
- [x] Know the required JSON fields
- [x] Finished week1_data_spec.md for Setting A / B
- [x] Ran smoke test for data / collator
- [x] Finished week1_report.md

Final status:
10/10 checklist items completed.

---

## 7. Self-evaluation

### Level
Reached: Good

### Reason
I now have:
- a stable understanding of the backbone
- a locked task specification
- a working local environment
- successful toy-data smoke tests
- a clear boundary between benchmark-compatible and extension parts

### Remaining risk
The main risk is not week 1 anymore.
The main risk moves to week 2 and later:
- real dataset construction
- split correctness
- contraindication source quality
- evaluation definition

DrKGC:
query -> candidates -> subgraph -> graph encoder -> LLM reranking

FOG-RAG:
query -> ontology/safety-aware candidates -> fuzzy subgraph -> fuzzy graph encoder -> grounded + safety-aware reranking