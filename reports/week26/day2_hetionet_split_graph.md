# Week 26 Day 2 — Hetionet split + graph + mappings

- Created at: `2026-05-11T13:19:18.472333+00:00`
- Decision: `DAY2_HETIONET_SPLIT_GRAPH_READY`

## Split summary

- target_relation: `CtD`
- num_target_edges_total: `755`
- train_size: `555`
- valid_size: `100`
- test_size: `100`
- num_train_compounds: `387`
- num_valid_compounds: `63`
- num_test_compounds: `58`
- num_train_diseases: `77`
- num_valid_diseases: `37`
- num_test_diseases: `44`

## Graph summary

- train_enriched_num_edges: `2249997`
- num_entities: `47031`
- num_relations: `24`
- target_train_edges_in_graph: `555`
- heldout_target_edges_removed: `200`

## Checks

- coverage_pass: `True`
- exact_leak_count: `0`
- relation_id_range_pass: `True`
- entity_id_range_pass: `True`

## Notes

- Target task is `(? , CtD, disease)`, predicted head.
- Valid/test target CtD triples are removed from the train enriched graph.
- CpD and other non-CtD edges remain as auxiliary graph evidence.