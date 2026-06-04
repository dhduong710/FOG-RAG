# Week 5 - Day 3 Embedding Report

## Input
- embedding_path: `dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt`
- entity2id_path: `dataset/setting_a/08_backbone_ready/entity2id.pkl`
- reference_embedding_path: `dataset/setting_a/07_pilot_ready/mock_entity_embeddings.pt`

## Validation summary
- embedding_type: `<class 'torch.Tensor'>`
- embedding_shape: `(10453, 256)`
- num_entities_from_entity2id: `10453`
- entity_count_match: `True`
- nan_count: `0`
- inf_count: `0`
- all_zero_like: `False`
- mean_abs: `6.16453695`
- std: `63.08946991`

## Reference comparison
- reference_note: `reference_embedding_loaded`
- reference_shape: `(10453, 200)`
- embedding_dim_match_reference: `False`

## Judgment
- VALID_FOR_DAY4: `True`

## Interpretation
This report checks only whether the exported entity embedding matrix is structurally valid
for week-5 day-4 server dry run. It does not claim that the embedding is already optimal.

## Note
- embedding_dim = 256
- reference_mock_dim = 200
- This is acceptable because GraphEnhancer reads kge_embedding.shape[1] dynamically
