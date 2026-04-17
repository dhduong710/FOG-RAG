# Week 2 - Day 5 Report

## Part A - ID maps
- source train graph: `dataset/setting_a/02_graph/train_enriched.tsv`
- num_entities: 10453
- num_relations: 4
- relation_names: ['associated_with', 'indication', 'ppi', 'target']
- split_entity_coverage_ok: True

## Output files
- `dataset/setting_a/04_drkgc_json/entity2id.pkl`
- `dataset/setting_a/04_drkgc_json/id2entity.pkl`
- `dataset/setting_a/04_drkgc_json/relation2id.pkl`
- `dataset/setting_a/04_drkgc_json/id2relation.pkl`

## Part B - JSON skeleton
- train_skeleton_samples: 8388
- valid_skeleton_samples: 500
- test_skeleton_samples: 500
- sample_type: predicted_head
- query_entity_role: disease
- placeholder_ranking: gold-only list, to be replaced on Day 6

## Output files
- `dataset/setting_a/04_drkgc_json/train_skeleton.json`
- `dataset/setting_a/04_drkgc_json/valid_skeleton.json`
- `dataset/setting_a/04_drkgc_json/test_skeleton.json`
