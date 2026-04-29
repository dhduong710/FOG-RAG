# Week 22 Day 6 — Build PharmKG FOG-RAG-ready Package

## Decision

`FOGRAG_READY_PACKAGE_BUILT`

## Source selection

- Main FOG-RAG source: `rgcn`
- DrKGC-aligned alternative: `hrgat`

Reason:

R-GCN is selected as the main FOG-RAG transfer source because it is DrKGC-compatible, aligned with the PrimeKG FOG-RAG pipeline, and it has the best locked-test MRR@20 among the available GNN sources.

## Dataset/task

- Dataset: PharmKG-8k
- Setting: `setting_c_pharmkg`
- Task: `(?, T, disease)`
- Relation normalized: `therapeutic_association_proxy`
- Candidate universe: `drug_only_from_train_T_heads`
- Gold injection for evaluation: `false`

## Ready split summary

| Split | Rows | Avg candidates | Gold in list rate | Rank21 | Avg subgraph size |
|---|---:|---:|---:|---:|---:|
| train | 28960 | 20.00 | 1.000 | 0 | 100.00 |
| valid | 500 | 20.00 | 0.070 | 465 | 100.00 |
| test | 500 | 20.00 | 0.092 | 454 | 100.00 |

## Leak sanity

- valid target in train_enriched: `0`
- test target in train_enriched: `0`
- valid/test target overlap: `0`
- decision: `PASS`

## Prompt template

`What drug is therapeutically associated with {disease}?`

## Rule policy

No explicit semantic PharmKG relation-label map is available. Therefore, Day 6 uses:

1. shortest-path retrieval between candidate and query on `train_enriched.tsv`;
2. incident-edge fill around query and candidates;
3. no hand-claimed semantic rule sequence.

## Files written

- `dataset/setting_c_pharmkg/05_backbone_raw_source/valid_top20_raw.json`
- `dataset/setting_c_pharmkg/05_backbone_raw_source/test_top20_raw.json`
- `dataset/setting_c_pharmkg/06_fograg_ready/train.json`
- `dataset/setting_c_pharmkg/06_fograg_ready/valid.json`
- `dataset/setting_c_pharmkg/06_fograg_ready/test.json`
- `dataset/setting_c_pharmkg/06_fograg_ready/prompt_lexicon.json`
- `dataset/setting_c_pharmkg/06_fograg_ready/rules.json`
- `dataset/setting_c_pharmkg/06_fograg_ready/support_schema.json`
- `dataset/setting_c_pharmkg/06_fograg_ready/prep_manifest.json`
- `results/week22/dataset2_source_selection.json`

## Next step: Day 7

Close out Week 22 and decide whether to start Week 23 FOG-RAG transfer.
