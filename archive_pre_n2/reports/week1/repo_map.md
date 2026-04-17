# Week 1 Repo Map

## Overall understanding
DrKGC backbone pipeline:
incomplete triple
-> question generator
-> lightweight candidate retriever
-> dynamic subgraph retriever
-> graph enhancer / GCN adapter
-> LLM reranking

## File map

### 1. main.py
Role: training entry.
What it does:
- loads tokenizer
- adds special tokens [QUERY], [ENTITY], [RELATION]
- loads KGE embeddings
- builds graph enhancer
- trains LoRA on top of the LLM

Key takeaway:
This backbone does not use only text prompts. It injects graph-aware embeddings into placeholder positions inside the prompt.

### 2. model/drkgc.py
Role: bridge between KG structure and LLM.
What it does:
- reads placeholder tokens [QUERY] and [ENTITY]
- uses graph model to produce query embedding and entity embeddings
- replaces text-token embeddings at placeholder positions with graph embeddings

Key takeaway:
This is the core integration point between structural graph information and the language model.

### 3. data/dataset.py
Role: dataset loader.
What it does:
- loads train.json
- loads valid.json
- loads test.json

Key takeaway:
The repo assumes the JSON files already exist in the correct format. It does not build the dataset for you.

### 4. data/collate.py
Role: collator / batch builder.
What it does:
- reads required fields from each sample
- tokenizes input and output
- builds input_ids, attention_mask, labels
- packs query_ids, entity_ids, and subgraph into the batch

Required fields per sample:
- input
- output
- query_entity_id
- rank_entities_id
- subgraph

Key takeaway:
If one of these required fields is missing or has the wrong type, the pipeline will fail.

### 5. infer.py
Role: evaluation entry.
What it does:
- computes ranking metrics
- reports MRR
- reports Hits@1
- reports Hits@3
- reports Hits@10

Key takeaway:
If I later add SafetyViolation@K, Contra@K, or other safety-aware evaluation, this is one of the first files I will need to modify.

### 6. prompt_subgraph.py
Role: prompt construction + subgraph retrieval.
What it does:
- constructs the natural-language prompt
- prepares candidate-related prompt content
- builds subgraphs
- uses shortest-path and rule-based paths

Key takeaway:
This file is important because it shows how evidence is prepared before being consumed by the model.

## Answers I must remember

### Q1. Where does the candidate list come from?
From the lightweight candidate retriever stage before LLM reranking. In the data pipeline this candidate list is represented through rank_entities / rank_entities_id and is then used in prompt construction and model input.

### Q2. What fields are required in each JSON sample?
- input
- output
- query_entity_id
- rank_entities_id
- subgraph

### Q3. At what step is the subgraph fed into the model?
The subgraph is prepared before model input, passed through the batch/collator, and then used by the graph side of the model when creating graph-aware embeddings for placeholder injection.

### Q4. If I want to add safety metrics later, which file will I likely modify?
infer.py