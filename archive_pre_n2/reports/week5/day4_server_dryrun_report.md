# Week 5 - Day 4 Server Dry Run Report

## Config
- dataset_path: `dataset/setting_a/08_backbone_ready`
- model_name_or_path: `meta-llama/Llama-3.2-3B`
- model_type: `llama`
- kge_embedding_path: `dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt`
- use_quant: `True`
- bits: `4`
- batch_size: `1`
- source_max_len: `768`
- target_max_len: `64`
- adapter_size: `1024`
- gnn_hidden_dim: `128`
- gnn_num_hidden_layers: `1`

## Model / Embedding
- llm_effective_device: `cuda:0`
- llm_hidden_size: `3072`
- llm_hidden_act: `silu`
- kge_embedding_shape: `(10453, 256)`

## Per-step records
```json
[
  {
    "step": 0,
    "actual_batch_size": 1,
    "sequence_length": 382,
    "num_candidates_per_sample": 20,
    "query_ids_shape": [
      1
    ],
    "entity_ids_shape": [
      1,
      20
    ],
    "subgraph_size_min": 65,
    "subgraph_size_max": 65,
    "loss": 2.1253840923309326,
    "loss_is_finite": true,
    "seconds_per_batch": 0.2868,
    "peak_gpu_memory_mb": 3691.56
  },
  {
    "step": 1,
    "actual_batch_size": 1,
    "sequence_length": 391,
    "num_candidates_per_sample": 20,
    "query_ids_shape": [
      1
    ],
    "entity_ids_shape": [
      1,
      20
    ],
    "subgraph_size_min": 66,
    "subgraph_size_max": 66,
    "loss": 2.086371898651123,
    "loss_is_finite": true,
    "seconds_per_batch": 0.1445,
    "peak_gpu_memory_mb": 3691.56
  }
]
```

## Judgment
- DRYRUN_VALID: `True`

## Interpretation
A successful day-4 dry run means full-ready data + real embedding + LLM + graph branch can produce finite loss on server.