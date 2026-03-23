# Setting B Lock

## Core decision
Setting B reuses the exact same split as Setting A and keeps the same main task:

- Query format: `(?, indication, disease)`
- Candidate type: `drug`
- Positive relation of the main benchmark: `indication`

## What contraindication is used for
Contraindication is treated only as an auxiliary safety signal for:

- hard filtering
- soft penalty
- safety metrics
- case-study safety flagging

## What contraindication is NOT used for
Contraindication must not be used to:

- create positive training labels for the main task
- change gold labels of Setting A
- create a new train/valid/test split
- redefine the benchmark task

## Schema rules
- indication: drug -> disease
- contraindication: drug -> disease
- target: drug -> gene/protein
- associated_with: gene/protein -> disease
- ppi: gene/protein -> gene/protein (unordered-collapsed in train graph)

## Day-4 artifacts
- full contraindication edges: `dataset/setting_b/00_safety_labels/contraindication_edges_full.tsv`
- overlap contraindication edges: `dataset/setting_b/00_safety_labels/contraindication_edges_overlap.tsv`
- type map: `dataset/setting_b/01_ontology/entity_name_to_type.json`
- domain-range rules: `dataset/setting_b/01_ontology/domain_range_rules.json`
- safety config: `dataset/setting_b/02_eval_meta/safety_eval_config.json`

## Notes
This document locks the semantic role of Setting B before any hard-filter / soft-penalty implementation.

## Type-conflict note
- `name_type_conflicts.json` currently contains 94 entries.
- These conflicts are retained for transparency and are NOT forced into strict ontology assumptions unless explicitly resolved later.
- `missing_split_entities.json = 0`, so all Setting A split entities are covered by the current type layer.