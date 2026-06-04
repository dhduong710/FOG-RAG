# Week 27 Closeout — DRKG External Validation

## 1. Final decision

```text
WEEK27_DECISION = DRKG_EXTERNAL_VALIDATION_COMPLETED
DAY8_DECISION = DAY8_DRKG_E2E_RGCN_ALL_ROWS_READY
```

DRKG is used as a difficult large biomedical KG external validation setting. The goal is not to show universal superiority over all structure-only baselines, but to test whether the R-GCN-based DrKGC/SoftFuse pipeline can still produce modest gains and evidence-efficiency in a large noisy graph.

## 2. Dataset and task

```text
Dataset: DRKG
Setting: setting_e_drkg
Task: (?, DRUGBANK::treats, disease)
Target relation: DRUGBANK::treats::Compound:Disease
Prediction type: predicted_head
Query entity: Disease
Gold/candidate entity: Compound
Candidate universe: train target relation compound heads
Top-k: 20
Gold injection on valid/test: false
Absent rank sentinel: 21
```

Raw DRKG inventory:

```text
triples = 5,874,261
relations = 107
entity types = 13
Compound entities = 24,313
Disease entities = 5,103
```

Target relation:

```text
unique target edges = 4,968
unique compounds = 1,542
unique diseases = 1,182
```

Split:

```text
train = 3,968
valid = 500
test  = 500
coverage_pass = true
exact_leak_count = 0
```

## 3. Filtered graph construction

The full DRKG graph was not used blindly. A filtered graph was constructed using:

```text
1. train DRUGBANK::treats target edges
2. Compound-Gene relations around candidate compounds
3. Disease-Gene relations around target/query diseases
4. selected auxiliary Compound-Disease GNBR relations
5. Gene-Gene bridges around touched genes
```

Filtered graph summary:

```text
train_enriched_edges = 187,962
num_entities = 13,918
num_relations = 85
graph_num_rels = 85
target_relation_id = 16
exact_leak_count = 0
```

Kept edge families:

```text
target_treats = 3,968
compound_gene = 44,197
disease_gene = 23,235
aux_compound_disease = 14,333
gene_gene = 102,229
```

## 4. Structure baselines

| Model | Valid Gold@20 | Valid MRR@20 | Valid Top1Dom | Test Gold@20 | Test MRR@20 | Test Top1Dom |
|---|---:|---:|---:|---:|---:|---:|
| DistMult | 0.444 | 0.1027 | 0.070 | 0.432 | 0.0997 | 0.074 |
| ComplEx | 0.460 | 0.0815 | 0.086 | 0.406 | 0.0863 | 0.066 |
| HRGAT | 0.228 | 0.0663 | 0.844 | 0.204 | 0.0422 | 0.872 |
| TransE | 0.296 | 0.0617 | 0.166 | 0.270 | 0.0548 | 0.154 |
| R-GCN | 0.218 | 0.0614 | 1.000 | 0.200 | 0.0432 | 1.000 |
| RotatE | 0.226 | 0.0276 | 0.052 | 0.182 | 0.0236 | 0.048 |

Interpretation:

```text
DistMult is the strongest standalone structure-only candidate generator on DRKG.
R-GCN is retained as the graph-compatible DrKGC/SoftFuse source for protocol consistency.
R-GCN is not the best DRKG baseline and has severe top-1 collapse.
```

## 5. FOG-RAG-ready packages

Two packages were built:

```text
R-GCN:
  main DrKGC/SoftFuse consistency source

DistMult:
  strongest structure-only comparator / backup source
```

R-GCN package:

```text
train rows = 3,968
valid rows = 500
test rows = 500
avg graph = 100
bad_candidate_len = 0
bad_prompt_placeholders = 0
bad_subgraph = 0
embedding_shape = [13918, 128]
graph_num_rels = 85
```

## 6. Initial b050 soft-support result

The original b050 formula reduced top-1 collapse but harmed MRR.

| Split | Row | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Rank21 | Top1Dom |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Valid | R-GCN raw | 0.218 | 0.0614 | 0.026 | 0.054 | 0.164 | 391 | 1.000 |
| Valid | b050 soft | 0.218 | 0.0419 | 0.012 | 0.040 | 0.130 | 391 | 0.320 |
| Test | R-GCN raw | 0.200 | 0.0432 | 0.010 | 0.042 | 0.120 | 400 | 1.000 |
| Test | b050 soft | 0.200 | 0.0398 | 0.016 | 0.028 | 0.120 | 400 | 0.324 |

Decision:

```text
DAY6_PACKAGE_STATUS = READY
DAY6_METHOD_RESULT = NEEDS_SWEEP
```

## 7. Rank-prior-aware soft-support sweep

Formula:

```text
support = E - beta * D - 0.10 * X
final_score = raw_weight * raw_rank_prior + (1 - raw_weight) * normalized_support
```

Selected variant:

```text
variant = sweep_beta0.10_raw0.80
selection_reason = best_valid_mrr_no_balanced_variant_met_constraints
```

| Split | Row | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Rank21 | Top1Dom |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Valid | R-GCN raw | 0.218 | 0.0614 | 0.026 | 0.054 | 0.164 | 391 | 1.000 |
| Valid | soft_support_sweep | 0.218 | 0.0652 | 0.030 | 0.066 | 0.168 | 391 | 0.886 |
| Test | R-GCN raw | 0.200 | 0.0432 | 0.010 | 0.042 | 0.120 | 400 | 1.000 |
| Test | soft_support_sweep | 0.200 | 0.0466 | 0.014 | 0.044 | 0.142 | 400 | 0.878 |

Interpretation:

```text
Rank-prior-aware soft support gives modest but consistent improvements over the R-GCN source.
```

## 8. Fuzzy retrieval

Variant:

```text
fuzzy_retrieval_main_drkg_rgcn
```

| Split | Soft MRR@20 | Fuzzy MRR@20 | Metrics preserved | Soft graph | Fuzzy graph | Reduction | Coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| Valid | 0.0652 | 0.0652 | True | 100 | 55 | 45% | 1.000 |
| Test | 0.0466 | 0.0466 | True | 100 | 55 | 45% | 1.000 |

Additional retrieval diagnostics:

```text
valid direct edges: 2.954 → 2.130
test direct edges: 2.514 → 1.824
schema_pass = true
candidate_order_mismatch = 0
exact_subgraph_leak = 0
```

## 9. E2E Llama-3.2-3B results

| Split | Row | Cand Gold@20 | Cand MRR@20 | E2E MRR@20 | E2E H@1 | E2E H@3 | E2E H@10 | Pred-in-cand | Invalid | Top1Dom | Avg graph |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Valid | backbone_raw | 0.218 | 0.0614 | 0.0633 | 0.028 | 0.056 | 0.166 | 1.000 | 0.000 | 1.000 | 100 |
| Valid | soft_support_sweep | 0.218 | 0.0652 | 0.0797 | 0.050 | 0.080 | 0.172 | 0.998 | 0.002 | 0.886 | 100 |
| Valid | fuzzy_retrieval_main | 0.218 | 0.0652 | 0.0717 | 0.038 | 0.074 | 0.170 | 1.000 | 0.000 | 0.886 | 55 |
| Test | backbone_raw | 0.200 | 0.0432 | 0.0527 | 0.020 | 0.052 | 0.130 | 1.000 | 0.000 | 1.000 | 100 |
| Test | soft_support_sweep | 0.200 | 0.0466 | 0.0514 | 0.022 | 0.052 | 0.134 | 0.998 | 0.002 | 0.878 | 100 |
| Test | fuzzy_retrieval_main | 0.200 | 0.0466 | 0.0549 | 0.024 | 0.054 | 0.140 | 1.000 | 0.000 | 0.878 | 55 |

Interpretation:

```text
soft_support_sweep gives the strongest valid E2E result.
fuzzy_retrieval_main gives the strongest test E2E result and reduces graph size by 45%.
```

## 10. Paper-facing interpretation

DRKG is a difficult external validation case. R-GCN has low Gold@20 and severe top-1 collapse. Rank-prior-aware soft support modestly improves the R-GCN source. Fuzzy retrieval preserves candidate metrics, reduces graph size from 100 to 55, and gives the best test E2E result. DistMult remains the strongest standalone structure-only candidate generator; therefore, DRKG supports a claim of R-GCN-source improvement and evidence-efficiency rather than universal superiority.

## 11. Limitations

```text
1. DRKG is difficult because R-GCN Gold@20 is only 0.218/0.200.
2. DistMult remains stronger than the R-GCN/SoftFuse source at candidate stage.
3. Initial b050 over-corrected the R-GCN ranking and required rank-prior-aware sweep.
4. Top1Dom remains high after soft support, although lower than raw R-GCN.
5. Candidate coverage limits E2E performance because absent-gold cases remain rank 21.
```

## 12. Final closeout

```text
WEEK27_DRKG_CLOSEOUT
================================================================================
Dataset: DRKG
Task: (?, DRUGBANK::treats, disease)
Split: 3968 / 500 / 500
Filtered graph: 13,918 entities, 85 relations, 187,962 edges
Main consistency source: R-GCN
Strongest structure-only baseline: DistMult

R-GCN backbone:
  valid Cand MRR = 0.0614
  test  Cand MRR = 0.0432
  Top1Dom = 1.000 / 1.000

Soft support:
  selected variant = sweep_beta0.10_raw0.80
  valid Cand MRR = 0.0652
  test  Cand MRR = 0.0466
  valid E2E MRR = 0.0797
  test  E2E MRR = 0.0514

Fuzzy retrieval:
  candidate metrics preserved = true
  graph size = 100 → 55
  graph reduction = 45%
  valid E2E MRR = 0.0717
  test  E2E MRR = 0.0549

Final interpretation:
  modest R-GCN-source gains
  strong evidence-efficiency result
  DistMult remains strongest standalone structure-only baseline
================================================================================
```
