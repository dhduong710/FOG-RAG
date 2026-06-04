# Day 2 — Build infer-ready packages

- status: **BUILT**
- checkpoint_dir: `results/week20/e2e_primary_checkpoint`
- model_name_or_path: `meta-llama/Llama-3.2-3B`
- kge_embedding_path: `dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt`

## 1. Package summaries
### backbone_raw
- path: `/home/anhlq/Documents/2026-dhd/FOG-RAG/dataset/setting_a/29_n2_e2e_infer_ready/backbone_raw`
- valid_summary: `{'num_rows': 500, 'sample_rank': 1, 'sample_num_candidates': 20, 'sample_subgraph_size': 49, 'has_required_fields': True}`
- test_summary: `{'num_rows': 500, 'sample_rank': 21, 'sample_num_candidates': 20, 'sample_subgraph_size': 66, 'has_required_fields': True}`

### soft_support_raw
- path: `/home/anhlq/Documents/2026-dhd/FOG-RAG/dataset/setting_a/29_n2_e2e_infer_ready/soft_support_raw`
- valid_summary: `{'num_rows': 500, 'sample_rank': 1, 'sample_num_candidates': 20, 'sample_subgraph_size': 49, 'has_required_fields': True}`
- test_summary: `{'num_rows': 500, 'sample_rank': 21, 'sample_num_candidates': 20, 'sample_subgraph_size': 66, 'has_required_fields': True}`

### retrieval_main
- path: `/home/anhlq/Documents/2026-dhd/FOG-RAG/dataset/setting_a/29_n2_e2e_infer_ready/retrieval_main`
- valid_summary: `{'num_rows': 500, 'sample_rank': 1, 'sample_num_candidates': 20, 'sample_subgraph_size': 27, 'has_required_fields': True}`
- test_summary: `{'num_rows': 500, 'sample_rank': 21, 'sample_num_candidates': 20, 'sample_subgraph_size': 32, 'has_required_fields': True}`
- selected_source_variant_set_test: `['soft_support_fuzzy_retrieval_tight']`

## 2. Day-2 conclusion
Built infer-ready packages for backbone_raw, soft_support_raw, and retrieval_main. Each package now contains train/valid/test JSONs that satisfy the current infer.py contract.
