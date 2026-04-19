# Day 1 — Week 20 Protocol Freeze

- status: **READY_FOR_E2E_CONFIRMATION**
- theme: **Frozen end-to-end LLaMA confirmation + paper-ready assets**

## 1. Frozen paper-facing rows
- paper_main_row: `soft_support_fuzzy_retrieval_main`
- reference_row: `backbone_raw`
- negative_control: `ontology_raw`
- candidate_stage_intermediate: `soft_support_raw`
- appendix_only: `['soft_support_fuzzy_encoder_probe_v0']`
- selected_source_variant: `soft_support_fuzzy_retrieval_tight`

## 2. End-to-end confirmation rows
- `backbone_raw`
- `soft_support_raw`
- `soft_support_fuzzy_retrieval_main`

## 3. Infer contract
- required_dataset_files: `['train.json', 'valid.json', 'test.json']`
- required_sample_fields: `['input', 'output', 'query_entity_id', 'rank_entities_id', 'subgraph']`
- eval_split: `test`
- main_e2e_rows: `['backbone_raw', 'soft_support_raw', 'soft_support_fuzzy_retrieval_main']`

## 4. Checkpoint inventory
- num_candidates: `0`
- primary_candidate: `None`

## 5. Model hints
- `/home/anhlq/Documents/2026-dhd/FOG-RAG/configs/reference_backbone/setting_a_server_3b.yaml` | `model_name_or_path` = `meta-llama/Llama-3.2-3B`
- `/home/anhlq/Documents/2026-dhd/FOG-RAG/configs/reference_backbone/backbone_valid_v2.yaml` | `model_name_or_path` = `meta-llama/Llama-3.2-3B`

## 6. Preferred KGE path
- `/home/anhlq/Documents/2026-dhd/FOG-RAG/dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt`

## 7. Day-1 conclusion
Week 20 is ready for frozen end-to-end confirmation. Day 2 should build infer-ready packages for backbone_raw, soft_support_raw, and soft_support_fuzzy_retrieval_main.
