# Week 22 Day 2 — Raw Inventory for PharmKG / Dataset 2

## Decision

`PARTIAL_READY_NEEDS_ENTITY_TYPE_MAP`

## Decision notes

- No explicit entity type map was found. Day 3 may need raw Zenodo archive or heuristic type mapping.
- No obvious therapeutic relation keyword found in visible relation strings. Relation IDs may need mapping.

## Download status

See:

- `dataset/setting_c_pharmkg/00_raw_inventory/download_status.json`

## Raw files found

Number of files: **7**

Manifest:

- `dataset/setting_c_pharmkg/00_raw_inventory/file_manifest.json`

## Triple file candidates

- `PharmKG-8k/test.tsv` (lines=50036, cols=3)
- `PharmKG-8k/train.tsv` (lines=400788, cols=3)
- `PharmKG-8k/valid.tsv` (lines=49536, cols=3)


## Entity file candidates

- `PharmKG-8k/entity2vec.txt` (lines=7601, cols=NA)


## Relation file candidates

- `PharmKG-8k/relation2vec.txt` (lines=28, cols=NA)


## Entity/type file candidates

- None found


## Top relation values seen in triple-like files

- `GG`: 83402
- `ML`: 45402
- `Rg`: 43857
- `T`: 41670
- `E`: 39743
- `Ra`: 38089
- `P`: 35878
- `Q`: 32589
- `CC`: 32032
- `B`: 18984
- `I`: 18040
- `U`: 16143
- `Sa`: 14263
- `Te`: 6424
- `Pr`: 6345
- `Iw`: 6153
- `N`: 4089
- `X`: 3558
- `J`: 3368
- `K`: 2700

## Therapeutic relation keyword hints

- None

## Day 2 answers

1. Dataset has files? **yes**
2. Candidate triple files? **yes**
3. Candidate entity files? **yes**
4. Candidate relation files? **yes**
5. Explicit entity type map? **not confirmed**
6. Relation like indication/treatment/therapeutic association? **not confirmed**
7. Enough Drug/Disease entities? **not confirmed on Day 2**
8. Enough drug-disease triples for split? **not confirmed until Day 3 relation/type selection**

## Important warning

Day 2 only inventories the raw files. It does **not** select the final target relation.
Do not write in the paper that PharmKG has an indication relation unless Day 3 confirms the semantics.

## Files written

- `results/week22/dataset2_raw_inventory.json`
- `dataset/setting_c_pharmkg/00_raw_inventory/file_manifest.json`
- `dataset/setting_c_pharmkg/00_raw_inventory/triple_file_candidates.json`
- `dataset/setting_c_pharmkg/00_raw_inventory/relation_hint_candidates.json`
- `reports/week22/day2_raw_inventory.md`

## Next step: Day 3

Select:

- target relation
- relation direction
- drug entity type
- disease entity type
- support relations
- excluded relations

Expected Day 3 decision:

`GO_TASK_SELECTED` or `PARTIAL_READY_NEEDS_MANUAL_SCHEMA_CHECK`
