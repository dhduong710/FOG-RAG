# Week 26 Closeout — Hetionet External Validation

## 1. Final decision

```text
WEEK26_DECISION = HETIONET_EXTERNAL_VALIDATION_READY
DATASET_STATUS = COMPLETED
```

Hetionet is used as an external validation setting for SoftFuse-KGC. Its role is not to replace PrimeKG as the primary benchmark, but to test whether SoftFuse-KGC can handle a collapsed R-GCN candidate source and still provide evidence-calibrated re-ranking and compact retrieval.

## 2. Dataset and task

```text
Dataset: Hetionet v1.0
Setting: setting_d_hetionet
Task: (?, CtD, disease)
Target relation: CtD = Compound-treats-Disease
Prediction type: predicted_head
Query entity: Disease
Gold/candidate entity: Compound
Top-k: 20
Gold injection on valid/test: false
Absent rank sentinel: 21
```

Raw inventory:

```text
nodes = 47,031
relations = 24
compound nodes = 1,552
disease nodes = 137
CtD target edges = 755
CtD unique compounds = 387
CtD unique diseases = 77
```

Split and graph:

```text
train/valid/test = 555 / 100 / 100
train_enriched_edges = 2,249,997
num_entities = 47,031
num_relations = 24
graph_num_rels = 24
CtD relation_id = 8
coverage_pass = true
exact_leak_count = 0
```

## 3. Protocol

Reviewer-safe evaluation:

```text
RR = 1 / rank if gold rank <= 20 else 0
Absent-gold rank = 21
No valid/test gold injection
Fixed top-20 candidate list
```

Coverage-safe split:

```text
valid/test gold compounds appear in train target relation
valid/test query diseases appear in train target relation
valid/test CtD triples removed from train graph
exact leakage = 0
```

## 4. Structure baseline results

| Model | Valid Gold@20 | Valid MRR@20 | Valid Top1Dom | Test Gold@20 | Test MRR@20 | Test Top1Dom |
|---|---:|---:|---:|---:|---:|---:|
| ComplEx | 0.400 | 0.0754 | 0.220 | 0.440 | 0.0903 | 0.130 |
| TransE | 0.370 | 0.0750 | 0.220 | 0.270 | 0.0456 | 0.290 |
| DistMult | 0.270 | 0.0679 | 0.560 | 0.390 | 0.0719 | 0.550 |
| HRGAT | 0.400 | 0.0605 | 1.000 | 0.410 | 0.1013 | 1.000 |
| R-GCN | 0.430 | 0.0575 | 1.000 | 0.440 | 0.0994 | 1.000 |
| RotatE | 0.190 | 0.0402 | 0.170 | 0.200 | 0.0426 | 0.170 |

Interpretation:

```text
ComplEx is the strongest non-degenerate validation baseline.
R-GCN/HRGAT have useful Gold@20 but severe top-1 collapse.
R-GCN is retained as the graph-compatible DrKGC/SoftFuse source.
```

## 5. Backbone R-GCN package

```text
source_model = R-GCN
entity_embeddings_rgcn.pt shape = [47031, 128]
graph_num_rels = 24
avg_subgraph_size = 80
valid/test exact leak = 0
prompt placeholders = 1 [QUERY] + 20 [ENTITY]
```

| Split | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Rank21 | Top1Dom | Avg graph |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Train | 1.000 | 0.0916 | 0.0216 | 0.0486 | 0.1315 | 0 | 1.000 | 80 |
| Valid | 0.430 | 0.0575 | 0.0100 | 0.0400 | 0.1900 | 57 | 1.000 | 80 |
| Test | 0.440 | 0.0994 | 0.0400 | 0.1100 | 0.2200 | 56 | 1.000 | 80 |

## 6. Soft-support result

Variant:

```text
soft_support_b050_hetionet_main
support_score = evidence_positive - 0.50 * direct_shortcut_penalty - 0.10 * contradiction_penalty
```

| Split | Row | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Rank21 | Top1Dom | Avg graph |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Valid | backbone_raw | 0.430 | 0.0575 | 0.010 | 0.040 | 0.190 | 57 | 1.000 | 80 |
| Valid | soft_support_raw | 0.430 | 0.1034 | 0.050 | 0.090 | 0.240 | 57 | 0.430 | 80 |
| Test | backbone_raw | 0.440 | 0.0994 | 0.040 | 0.110 | 0.220 | 56 | 1.000 | 80 |
| Test | soft_support_raw | 0.440 | 0.0954 | 0.010 | 0.110 | 0.280 | 56 | 0.370 | 80 |

Main finding:

```text
Soft support strongly reduces R-GCN top-1 collapse.
Valid MRR improves from 0.0575 to 0.1034.
Test Hits@10 improves from 0.220 to 0.280.
Test MRR slightly decreases from 0.0994 to 0.0954.
```

## 7. Fuzzy retrieval result

Variant:

```text
fuzzy_retrieval_main_hetionet
```

| Split | Soft MRR@20 | Fuzzy MRR@20 | Metrics preserved | Soft graph | Fuzzy graph | Reduction | Coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| Train | 0.0982 | 0.0982 | True | 80 | 44 | 45% | 1.000 |
| Valid | 0.1034 | 0.1034 | True | 80 | 44 | 45% | 1.000 |
| Test | 0.0954 | 0.0954 | True | 80 | 44 | 45% | 1.000 |

Interpretation:

```text
Fuzzy retrieval successfully preserves candidate metrics while reducing the evidence graph by 45%.
```

## 8. E2E Llama-3.2-3B result

| Split | Row | Cand MRR@20 | E2E MRR@20 | E2E H@1 | E2E H@3 | E2E H@10 | Pred-in-cand | Invalid | Avg graph |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Valid | backbone_raw | 0.0575 | 0.0720 | 0.030 | 0.060 | 0.190 | 1.000 | 0.000 | 80 |
| Valid | soft_support_raw | 0.1034 | 0.1200 | 0.070 | 0.110 | 0.250 | 1.000 | 0.000 | 80 |
| Valid | fuzzy_retrieval_main | 0.1034 | 0.1309 | 0.080 | 0.120 | 0.270 | 1.000 | 0.000 | 44 |
| Test | backbone_raw | 0.0994 | 0.1045 | 0.050 | 0.120 | 0.210 | 0.980 | 0.020 | 80 |
| Test | soft_support_raw | 0.0954 | 0.1109 | 0.030 | 0.130 | 0.280 | 1.000 | 0.000 | 80 |
| Test | fuzzy_retrieval_main | 0.0954 | 0.0991 | 0.020 | 0.110 | 0.280 | 1.000 | 0.000 | 44 |

## 9. Paper-facing interpretation

Hetionet is a collapse-stress external validation. The R-GCN source has severe top-1 dominance. Soft support substantially reduces this collapse and improves validation ranking/E2E performance. Fuzzy retrieval preserves the soft-support ranking and reduces the graph from 80 to 44 triples. On test, soft support is the best E2E row, while fuzzy retrieval provides the strongest evidence-efficiency trade-off.

## 10. Limitations

```text
1. Hetionet CtD has only 755 target edges.
2. R-GCN and HRGAT have severe top-1 dominance.
3. Soft support improves validation strongly but test candidate MRR decreases slightly.
4. Fuzzy retrieval reduces graph size but is not the best test E2E row.
5. Strict exact-match remains limited; adjusted E2E rank and validity diagnostics should both be reported.
```

## 11. Final closeout

```text
WEEK26_HETIONET_CLOSEOUT
================================================================================
Dataset: Hetionet v1.0
Task: (?, CtD, disease)
Split: 555 / 100 / 100
Graph: 47,031 entities, 24 relations, 2,249,997 enriched edges
Main source: R-GCN
Best non-degenerate structure baseline: ComplEx

Soft support:
  valid Cand MRR = 0.1034
  test  Cand MRR = 0.0954
  valid E2E MRR = 0.1200
  test  E2E MRR = 0.1109

Fuzzy retrieval:
  graph size = 80 → 44
  graph reduction = 45%
  valid E2E MRR = 0.1309
  test  E2E MRR = 0.0991

Final decision:
  HETIONET_EXTERNAL_VALIDATION_READY
================================================================================
```
