# Week 2 - Day 4 Report

## Goal
Lock Setting B semantics and generate safety / ontology metadata.

## Inputs
- Raw PrimeKG: `dataset/raw/primekg/kg.csv`
- Setting A split: `dataset/setting_a/01_split`

## Setting A entity universe
- unique drugs: 1801
- unique diseases: 1363

## Contraindication extraction
- full contraindication triples: 30675
- overlap contraindication triples: 16097
- diseases with contraindication labels in overlap set: 606
- drugs with contraindication labels in overlap set: 944

## Ontology mapping
- clean entity_name_to_type entries: 129168
- name/type conflict entries: 94
- missing split entities: 0

## Locked Setting B policy
- reuse Setting A split: True
- main task unchanged: True
- contraindication as positive label: False
- candidate type fixed to drug: True

## Output files
- `dataset/setting_b/00_safety_labels/contraindication_edges_full.tsv`
- `dataset/setting_b/00_safety_labels/contraindication_edges_overlap.tsv`
- `dataset/setting_b/00_safety_labels/contra_by_disease.json`
- `dataset/setting_b/00_safety_labels/contra_by_drug.json`
- `dataset/setting_b/01_ontology/entity_name_to_type.json`
- `dataset/setting_b/01_ontology/name_type_conflicts.json`
- `dataset/setting_b/01_ontology/missing_split_entities.json`
- `dataset/setting_b/01_ontology/domain_range_rules.json`
- `dataset/setting_b/02_eval_meta/safety_eval_config.json`
- `docs/decisions/setting_b.md`

## Notes
Day 4 only locks metadata and semantics.
No filtering, penalty, reranking, or training is implemented today.
name_type_conflicts = 94 are retained for transparency and excluded from strict ontology assumptions unless explicitly resolved later.
