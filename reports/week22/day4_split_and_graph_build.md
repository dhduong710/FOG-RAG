# Week 22 Day 4 — Build PharmKG Splits, Enriched Graph, and Leak Checks

## Decision

`SPLIT_GRAPH_READY`

Leak-check decision:

`PASS`

## Task

- Dataset: PharmKG-8k
- Setting: `setting_c_pharmkg`
- Task: `(?, T, disease)`
- Target relation raw: `T`
- Target relation normalized: `therapeutic_association_proxy`
- Prediction type: `predicted_head`
- Missing entity type: `Drug_or_Chemical`
- Query entity type: `Disease`
- Candidate universe: `drug_only_from_train_T_heads`
- Query universe: `disease_only_from_train_T_tails`
- Gold injection: `false`

## Raw target relation counts

| Split | # T triples |
|---|---:|
| train | 33411 |
| valid | 4082 |
| test | 4177 |

## Filtering and sampling

| Split | Before | After coverage | After train overlap removal | After extra forbidden removal | After dedup | Final |
|---|---:|---:|---:|---:|---:|---:|
| valid | 4082 | 4058 | 3173 | 3173 | 3141 | 500 |
| test | 4177 | 4157 | 3235 | 3227 | 3200 | 500 |

Train positives:

- train = **28960**

## Entity and graph stats

- Num entities: **7247**
- Num relations: **28**
- Num candidate drugs: **1342**
- Num query diseases: **803**
- Train enriched triples: **386768**

## Train enriched relation counts

- `GG`: 66774
- `Rg`: 35103
- `E`: 31741
- `ML`: 31529
- `Ra`: 30540
- `T`: 28960
- `P`: 26472
- `Q`: 26070
- `CC`: 25658
- `B`: 15259
- `I`: 14247
- `U`: 12281
- `Sa`: 10843
- `Pr`: 4949
- `Te`: 4870
- `Iw`: 4809
- `N`: 3281
- `X`: 2783
- `J`: 2567
- `K`: 2157
- `D`: 1934
- `C`: 1713
- `O`: 688
- `An`: 443
- `Z`: 384
- `Mp`: 362
- `A`: 323
- `As`: 28

## Exact leak checks

| Check | Value |
|---|---:|
| valid positive in train | 0 |
| test positive in train | 0 |
| valid/test positive overlap | 0 |
| selected valid/test target in train_enriched | 0 |

## Coverage checks

| Check | Value |
|---|---:|
| valid gold drug coverage | 1.000000 |
| test gold drug coverage | 1.000000 |
| valid query disease coverage | 1.000000 |
| test query disease coverage | 1.000000 |

## Type checks

- Candidate non-drug count: **0**
- Query non-disease count: **0**

Type counts JSON:

    {
      "Disease_from_train_T_tail": 803,
      "Unknown_or_Other": 5102,
      "Drug_or_Chemical_from_train_T_head": 1342
    }

## Files written

- `dataset/setting_c_pharmkg/02_splits/train.json`
- `dataset/setting_c_pharmkg/02_splits/valid.json`
- `dataset/setting_c_pharmkg/02_splits/test.json`
- `dataset/setting_c_pharmkg/03_graph/entity2id.json`
- `dataset/setting_c_pharmkg/03_graph/relation2id.json`
- `dataset/setting_c_pharmkg/03_graph/type_map.json`
- `dataset/setting_c_pharmkg/03_graph/train_enriched.tsv`
- `results/week22/dataset2_split_summary.json`
- `results/week22/dataset2_leak_check.json`
- `reports/week22/day4_split_and_graph_build.md`

## Next step: Day 5

Rerun six structure baselines as top-20 candidate generators:

- TransE
- DistMult
- ComplEx
- RotatE
- R-GCN
- HRGAT

All baselines must use:

- candidate universe = `drug_only_from_train_T_heads`
- top_k = 20
- gold_injection = false
- reviewer-safe RR@20
