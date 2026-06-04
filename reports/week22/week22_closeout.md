# Week 22 Closeout — PharmKG Dataset 2 Feasibility and FOG-RAG Transfer Setup

## Final decision

`GO_WEEK23_FOGRAG_TRANSFER`

## Decision notes

- Dataset 2 protocol is frozen.
- PharmKG task/schema selected with relation T as therapeutic_association_proxy.
- Coverage-safe split and train_enriched graph are ready.
- Leak checks passed.
- All six baselines are available.
- FOG-RAG-ready package is built with R-GCN as main source.

## Dataset 2 selected task

- Dataset: `PharmKG-8k`
- Setting: `setting_c_pharmkg`
- Task: `(?, T, disease)`
- Prediction type: `predicted_head`
- Direction: `drug_or_chemical -> disease`
- Raw relation code: `T`
- Normalized relation name: `therapeutic_association_proxy`
- Candidate universe: `drug_only_from_T_heads`

Important paper wording:

`relation T = therapeutic association proxy`

Do **not** call relation T clinical indication.

## Split and graph

- Split decision: `SPLIT_GRAPH_READY`
- Leak decision: `PASS`

Final split sizes:

- train: `28960`
- valid: `500`
- test: `500`

Entity/graph stats:

- num entities: `7247`
- num relations: `28`
- candidate drugs: `1342`
- query diseases: `803`
- train enriched triples: `386768`

Exact leak checks:

- valid positive in train: `0`
- test positive in train: `0`
- valid/test overlap: `0`
- selected valid/test target in train_enriched: `0`

## Baseline table — validation

| Model | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | H@20 | Rank21 |
|---|---:|---:|---:|---:|---:|---:|---:|
| distmult | 0.104 | 0.019548 | 0.008 | 0.018 | 0.038 | 0.104 | 448 |
| rgcn | 0.070 | 0.017846 | 0.010 | 0.014 | 0.034 | 0.070 | 465 |
| hrgat | 0.060 | 0.013963 | 0.006 | 0.016 | 0.032 | 0.060 | 470 |
| complex | 0.050 | 0.005814 | 0.000 | 0.004 | 0.018 | 0.050 | 475 |
| transe | 0.042 | 0.005302 | 0.000 | 0.000 | 0.022 | 0.042 | 479 |
| rotate | 0.022 | 0.002318 | 0.000 | 0.000 | 0.006 | 0.022 | 489 |

## Baseline table — test

| Model | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | H@20 | Rank21 |
|---|---:|---:|---:|---:|---:|---:|---:|
| rgcn | 0.092 | 0.020481 | 0.008 | 0.020 | 0.046 | 0.092 | 454 |
| hrgat | 0.094 | 0.018783 | 0.010 | 0.014 | 0.044 | 0.094 | 453 |
| distmult | 0.102 | 0.016576 | 0.006 | 0.012 | 0.038 | 0.102 | 449 |
| transe | 0.060 | 0.009319 | 0.002 | 0.008 | 0.028 | 0.060 | 470 |
| complex | 0.066 | 0.009066 | 0.000 | 0.008 | 0.036 | 0.066 | 467 |
| rotate | 0.024 | 0.001900 | 0.000 | 0.000 | 0.004 | 0.024 | 488 |

## Source selection

- Main FOG-RAG source: `rgcn`
- DrKGC-aligned alternative: `hrgat`
- Best valid baseline: `distmult` with MRR@20 `0.019548`
- Best test baseline: `rgcn` with MRR@20 `0.020481`

R-GCN is selected as the main FOG-RAG source because it is aligned with the PrimeKG FOG-RAG pipeline and has the strongest test MRR@20 among GNN-style sources.

## FOG-RAG-ready package

- Package ready: `True`
- Manifest decision: `FOGRAG_READY_PACKAGE_BUILT`
- Leak sanity: `PASS`

Ready split summary:

| Split | Rows | Avg candidates | Gold in list | Rank21 | Avg subgraph |
|---|---:|---:|---:|---:|---:|
| train | 28960 | 20.00 | 1.000 | 0 | 100.00 |
| valid | 500 | 20.00 | 0.070 | 465 | 100.00 |
| test | 500 | 20.00 | 0.092 | 454 | 100.00 |

## Answers to alignment questions

### 1. Did PrimeKG use gold in train candidates?

Yes. DrKGC-style supervised training requires the gold answer to be present in the answer options. The reviewer-sensitive issue is valid/test gold injection, not train supervision.

For PharmKG, `train_top20_supervised.json` is gold-first for train only. Valid/test are raw no-injection.

### 2. Did PharmKG use hard-coded rules?

PharmKG uses a fixed/manual retrieval policy, but does not claim semantic hard-coded rule sequences because PharmKG-8k only exposes compact relation codes. This is reviewer-safe.

PrimeKG used manual biomedical rules because relation semantics were explicit. PharmKG uses a fixed no-rule fallback: shortest paths plus incident-edge fill. Both avoid rule mining.

### 3. Did PharmKG use a question lexicon?

Yes. PharmKG has `prompt_lexicon.json`.

Prompt:

`What drug is therapeutically associated with {}?`

## Known limitations

- PharmKG relation T is treated as a therapeutic association proxy, not a confirmed clinical indication relation.
- Entity type map is task-specific: T heads are Drug/Chemical candidates and T tails are Disease queries.
- Current valid/test R-GCN Gold@20 is low, so Week 23 should treat raw candidate bottleneck as central.
- Day 6 subgraphs are fixed at graph_size=100; fuzzy retrieval in Week 23 should test whether smaller weighted evidence can preserve performance.
- HRGAT is retained as a DrKGC-aligned alternative, but R-GCN is selected as main source for pipeline continuity and stronger test MRR@20.

## Week 23 recommendation

Start FOG-RAG transfer with:

1. `backbone_raw`
2. `ontology_raw_negative_control`
3. `soft_support_raw`
4. `fuzzy_retrieval_main`

Optional:

- `hrgat_source_alternative`
- `fuzzy_encoder_probe_appendix_only`

## Files written

- `results/week22/week22_closeout.json`
- `results/week22/week22_go_decision.json`
- `reports/week22/day7_week22_closeout.md`
- `reports/week22/week22_closeout.md`
