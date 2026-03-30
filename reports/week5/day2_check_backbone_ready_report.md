# Day 2 Backbone-Ready Report

## 1. Goal
Check if a **full Setting-A backbone-ready package** is properly prepared for week-5 reproduction,
without mixing it with pilot-only artifacts.

## 2. Source files
- train: `dataset/setting_a/08_backbone_ready/train.json`
- valid: `dataset/setting_a/08_backbone_ready/valid.json`
- test: `dataset/setting_a/08_backbone_ready/test.json`
- entity2id: `dataset/setting_a/04_drkgc_json/entity2id.pkl`
- id2entity: `dataset/setting_a/04_drkgc_json/id2entity.pkl`
- relation2id: `dataset/setting_a/04_drkgc_json/relation2id.pkl`
- id2relation: `dataset/setting_a/04_drkgc_json/id2relation.pkl`
- split_meta: `dataset/setting_a/01_split/split_meta.json`
- type_map: `dataset/setting_b/01_annotations/type_map.tsv`

## 3. Destination
- `dataset/setting_a/08_check_backbone_ready`

## 4. Global checks
- [x] train_size_ok
- [x] valid_size_ok
- [x] test_size_ok
- [x] entity2id_nonempty
- [x] id2entity_nonempty
- [x] relation2id_nonempty
- [x] id2relation_nonempty
- [x] entity_map_size_match
- [x] relation_map_size_match
- [x] train_missing_field_zero
- [x] valid_missing_field_zero
- [x] test_missing_field_zero
- [x] train_gold_in_candidate_all
- [x] valid_gold_in_candidate_all
- [x] test_gold_in_candidate_all
- [x] train_id_mismatch_zero
- [x] valid_id_mismatch_zero
- [x] test_id_mismatch_zero
- [x] train_candidates_all_drug
- [x] valid_candidates_all_drug
- [x] test_candidates_all_drug

## 5. Split summaries

### Train
- num_samples: 8388
- candidate_len_min/max: 20 / 20
- subgraph_len_min/max: 2 / 149
- required_field_missing_count: 0
- subgraph_empty_count: 0
- gold_in_candidate_count: 8388
- id_mismatch_count: 0
- candidate_type_checkable_count: 8388
- all_candidates_are_drug_count: 8388

### Valid
- num_samples: 500
- candidate_len_min/max: 20 / 20
- subgraph_len_min/max: 50 / 128
- required_field_missing_count: 0
- subgraph_empty_count: 0
- gold_in_candidate_count: 500
- id_mismatch_count: 0
- candidate_type_checkable_count: 500
- all_candidates_are_drug_count: 500

### Test
- num_samples: 500
- candidate_len_min/max: 20 / 20
- subgraph_len_min/max: 49 / 126
- required_field_missing_count: 0
- subgraph_empty_count: 0
- gold_in_candidate_count: 500
- id_mismatch_count: 0
- candidate_type_checkable_count: 500
- all_candidates_are_drug_count: 500

## 6. Example samples
### Train examples
[
  {
    "index": 0,
    "output": "Fosinopril",
    "query_entity_id": 9772,
    "num_rank_entities_id": 20,
    "num_subgraph_triples": 65
  },
  {
    "index": 1,
    "output": "Fosinopril",
    "query_entity_id": 9771,
    "num_rank_entities_id": 20,
    "num_subgraph_triples": 66
  },
  {
    "index": 2,
    "output": "Imidapril",
    "query_entity_id": 9772,
    "num_rank_entities_id": 20,
    "num_subgraph_triples": 70
  }
]

### Valid examples
[
  {
    "index": 0,
    "output": "Cortisone acetate",
    "query_entity_id": 9871,
    "num_rank_entities_id": 20,
    "num_subgraph_triples": 63
  },
  {
    "index": 1,
    "output": "Cefixime",
    "query_entity_id": 10317,
    "num_rank_entities_id": 20,
    "num_subgraph_triples": 84
  },
  {
    "index": 2,
    "output": "Magnesium trisilicate",
    "query_entity_id": 9557,
    "num_rank_entities_id": 20,
    "num_subgraph_triples": 86
  }
]

### Test examples
[
  {
    "index": 0,
    "output": "Ticarcillin",
    "query_entity_id": 9885,
    "num_rank_entities_id": 20,
    "num_subgraph_triples": 94
  },
  {
    "index": 1,
    "output": "Cabergoline",
    "query_entity_id": 9223,
    "num_rank_entities_id": 20,
    "num_subgraph_triples": 78
  },
  {
    "index": 2,
    "output": "Hydrocortisone",
    "query_entity_id": 9279,
    "num_rank_entities_id": 20,
    "num_subgraph_triples": 62
  }
]

## 7. Warning examples
### Missing fields
{
  "train": [],
  "valid": [],
  "test": []
}

### Candidate non-drug examples
{
  "train": [],
  "valid": [],
  "test": []
}

### Rank-name mismatch examples
{
  "train": [],
  "valid": [],
  "test": []
}

## 8. Judgment
**READY** for day-3 real embedding export.

## 9. Next step
Day 3 will export the first real embedding source:
`dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt`
