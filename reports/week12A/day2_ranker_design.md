# Week 12A Day 2 — R-GCN Retriever Finetune Design

## 1. Goal
Design a bounded finetuning plan for an R-GCN coarse retriever under the same Setting-A protocol, in order to determine whether candidate quality can improve enough to justify resetting the base before Novelty 2.

## 2. Frozen protocol
- Task: head prediction (? , indication, disease)
- Candidate universe: drug_only
- K: 20
- Primary decision split: valid
- top20_raw and top20_drkgc_ready remain separated
- gold injection remains explicit and logged in the ready layer only

## 3. Current reference
Current reference retriever lineage:
- dataset/setting_a/11_ranker_v2
- config baseline: configs/week7/rgcn_ranker_v2.yaml

Current valid reference metrics:
- recall@20_raw = 0.192
- inject_ratio_ready = 0.808
- top1_hit_ratio_raw = 0.018

## 4. Why keep R-GCN
R-GCN is already integrated into the current project pipeline, compatible with the current graph artifacts, and gives the fairest retriever-only comparison without changing the rest of the stack.

## 5. Main optimization target
Primary target:
- increase recall@20_raw
- reduce inject_ratio_ready

Secondary target:
- improve top1_hit_ratio_raw
- reduce collapse / repeated top1 behavior

## 6. Main finetuning plan
Main config:
- target_relation = indication
- candidate_universe = drug_only
- num_layers = 2
- embedding_dim = 128
- hidden_dim = 128
- learning_rate = 5e-5
- weight_decay = 1e-4
- epochs = 40
- early_stop = 8
- batch_size = 512
- negatives_per_query = 32

## 7. Optional backup config
Backup config differs only slightly:
- learning_rate = 3e-5 or 2e-5
- negatives_per_query = 48
- batch_size = 256 if needed

## 8. What is NOT changed
- Setting A split
- target relation
- candidate universe
- K
- evaluator logic
- downstream reranker protocol
- Novelty-1 ontology / hard-soft logic

## 9. Checkpoint selection rule
Best retriever checkpoint should be selected using valid-side retrieval metrics, prioritizing:
1. recall@20_raw
2. inject_ratio_ready
3. top1_hit_ratio_raw
4. collapse/diversity diagnostics

## 10. Stop conditions
Stop or mark NO-GO early if:
- loss is unstable or degenerate
- valid recall fails to improve meaningfully
- inject ratio remains near the current reference
- score distribution is highly collapsed

## 11. Day-3 training outputs expected
- trained R-GCN retriever checkpoint
- training log
- score dump meta
- candidate build inputs for day 4