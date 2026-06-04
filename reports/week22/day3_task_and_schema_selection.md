# Week 22 Day 3 — Task, Relation, Schema, and Entity-Type Selection

## Decision

`GO_TASK_SELECTED_PROXY_SCHEMA`

## Decision notes

- No explicit relation-label map was available in PharmKG-8k files; relation T is selected as a therapeutic association proxy, not clinical indication.
- Preliminary type map is task-specific: T heads are Drug/Chemical candidates and T tails are Disease queries.

## Selected task

- Task template: `(?, T, disease)`
- Prediction type: `predicted_head`
- Missing entity type: `Drug_or_Chemical`
- Query entity type: `Disease`
- Candidate universe: `drug_only_from_T_heads`
- Raw relation code: `T`
- Normalized relation name: `therapeutic_association_proxy`
- Direction: `drug_or_chemical -> disease`

## Important paper wording

Use:

`therapeutic association proxy`

Do **not** call this relation:

- clinical indication
- PrimeKG indication
- confirmed treatment label

unless an explicit PharmKG relation-label map is later found.

## Target relation T counts

| Split | # T triples |
|---|---:|
| train | 33411 |
| valid | 4082 |
| test | 4177 |
| all | 41670 |

## Inferred entity types from T direction

- Candidate drug/chemical entities from T heads: **1370**
- Disease query entities from T tails: **812**
- Ambiguous T head/tail entities: **0**
- Unknown/other entities: **5080**

## Coverage of valid/test T entities in train T

| Split | Drug-head coverage | Disease-tail coverage | Unseen heads | Unseen tails |
|---|---:|---:|---:|---:|
| valid | 0.9804 | 0.9912 | 19 | 5 |
| test | 0.9863 | 0.9899 | 13 | 6 |

## Sample T rows

- `colchicine    T    anemia`
- `neomycin    T    pain`
- `vinorelbine    T    esophagitis`
- `methocarbamol    T    pain`
- `orlistat    T    body weight changes`
- `goserelin    T    neoplasm metastasis`
- `carbamazepine    T    sensation disorders`
- `testosterone    T    hiv infections`
- `oxcarbazepine    T    tuberous sclerosis`
- `danazol    T    neoplasm metastasis`
- `amrinone    T    intracranial hemorrhages`
- `vitamin a    T    hyperthyroidism`

## Relation role analysis

| Relation | # triples | Head drug-like rate | Tail disease-like rate | Proposed role |
|---|---:|---:|---:|---|
| T | 41670 | 1.000 | 1.000 | target_relation |
| GG | 83402 | 0.000 | 0.000 | unknown_or_other_support_candidate |
| ML | 45402 | 0.000 | 0.000 | support_relation_candidate |
| Rg | 43857 | 0.000 | 0.000 | unknown_or_other_support_candidate |
| E | 39743 | 0.284 | 0.000 | support_relation_candidate |
| Ra | 38089 | 0.000 | 0.000 | unknown_or_other_support_candidate |
| P | 35878 | 0.000 | 0.997 | support_relation_candidate |
| Q | 32589 | 0.000 | 0.000 | unknown_or_other_support_candidate |
| CC | 32032 | 0.979 | 0.000 | support_relation_candidate |
| B | 18984 | 0.046 | 0.000 | unknown_or_other_support_candidate |
| I | 18040 | 0.404 | 0.325 | support_relation_candidate |
| U | 16143 | 0.000 | 0.985 | support_relation_candidate |
| Sa | 14263 | 0.997 | 0.998 | support_relation_candidate |
| Te | 6424 | 0.000 | 0.995 | support_relation_candidate |
| Pr | 6345 | 0.998 | 0.999 | support_relation_candidate |
| Iw | 6153 | 0.130 | 0.402 | support_relation_candidate |
| N | 4089 | 0.997 | 0.000 | support_relation_candidate |
| X | 3558 | 0.000 | 0.000 | support_relation_candidate |
| J | 3368 | 0.998 | 0.997 | support_relation_candidate |
| K | 2700 | 0.000 | 0.000 | support_relation_candidate |
| D | 2501 | 0.000 | 0.994 | support_relation_candidate |
| C | 2232 | 0.999 | 0.999 | support_relation_candidate |
| O | 854 | 0.000 | 0.000 | support_relation_candidate |
| An | 676 | 0.000 | 0.960 | support_relation_candidate |
| Z | 482 | 0.000 | 0.000 | support_relation_candidate |
| Mp | 447 | 0.000 | 0.000 | support_relation_candidate |
| A | 403 | 1.000 | 0.000 | support_relation_candidate |
| As | 36 | 0.000 | 0.944 | support_relation_candidate |

## Day 4 recommendation

Use official PharmKG-8k split as base, select T triples, then apply Setting-A-style coverage filtering/subsampling with seed 2025.

Recommended Day 4 policy:

- valid/test size = 500/500 if coverage permits
- candidate universe = T-head drug/chemical entities
- query universe = T-tail disease entities
- train_enriched.tsv = train T target triples + support relation candidates
- do not include valid/test T target triples in train_enriched.tsv

## Files written

- `results/week22/dataset2_task_spec.json`
- `dataset/setting_c_pharmkg/01_task_spec/task_spec.json`
- `dataset/setting_c_pharmkg/01_task_spec/relation_role_analysis.json`
- `dataset/setting_c_pharmkg/01_task_spec/entity_type_summary.json`
- `dataset/setting_c_pharmkg/01_task_spec/type_map_preliminary.json`
- `dataset/setting_c_pharmkg/01_task_spec/target_relation_rows_summary.json`
- `reports/week22/day3_task_and_schema_selection.md`

## Next step

Day 4 should build:

- train/valid/test task rows
- entity2id/relation2id
- type_map
- train_enriched.tsv
- split_summary
- leak_check
