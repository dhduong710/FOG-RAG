# Week 28 Closeout — repoDB Clinical External Validation

## 1. Final decision

```text
WEEK28_DECISION = REPODB_EXTERNAL_VALIDATION_COMPLETED
FINAL_DAY_DECISION = DAY8_REPODB_E2E_ALL_ROWS_READY
DATASET_STATUS = COMPLETED_E2E
```

Week 28 completed repoDB as the fifth external validation dataset for SoftFuse-KGC.

repoDB should be framed as a **clinical drug-repositioning external validation benchmark**, not as a large biomedical KG benchmark. Its main value is clinical/translational relevance: the task uses approved drug-indication pairs and failed-like drug-indication pairs from repoDB.

The final repoDB conclusion is:

```text
Soft-support re-ranking did not improve the R-GCN source on repoDB.
Fuzzy retrieval preserved candidate metrics, reduced graph size by 45%, and achieved the best E2E MRR among R-GCN-derived rows.
```

---

## 2. Dataset and task

```text
Dataset: repoDB
Setting: setting_f_repodb
Task: (?, repoDB_approved_indication, disease)
Target relation: repoDB::approved_indication::Compound:Disease
Prediction type: predicted_head
Query entity: Disease / UMLS CUI
Gold entity: Compound / DrugBank ID
Candidate universe: train approved-relation compound heads
Top-k: 20
Gold injection on valid/test: false
Absent-gold rank sentinel: 21
```

Entity format:

```text
Compound: Compound::DBxxxxx
Disease : Disease::UMLS:Cxxxxxxx
```

Paper-safe wording:

```text
repoDB approved drug-indication prediction / clinical drug-repositioning external validation.
```

Do not claim prospective clinical validation.

---

## 3. Raw inventory and normalization

Raw repoDB table:

```text
raw rows = 10,800
columns = 11
```

Canonical normalized fields:

```text
drug_name
drugbank_id
compound_entity
disease_name
umls_cui
disease_entity
sem_type
status
phase
DetailedStatus
```

Raw label counts:

```text
approved = 6,677
failed-like = 4,123
```

Normalized unique pairs:

```text
approved unique pairs = 6,677
failed-like unique pairs before conflict removal = 3,281
failed-like unique pairs after conflict removal = 3,260
conflict pairs = 21
```

Entity coverage:

```text
approved drugs = 1,519
approved diseases = 1,229
failed-like drugs = 458
failed-like diseases = 989
```

Mapping probe to DRKG:

```text
compound exact hit rate in DRKG = 0.7193
approved compound exact hit rate in DRKG = 0.7281
disease CUI exact hit rate in DRKG = 0.0000
```

Interpretation:

```text
repoDB disease nodes are retained as local UMLS disease nodes.
DRKG evidence is reused mainly through mapped DrugBank compounds and compound-gene/gene-gene evidence.
```

---

## 4. Split and graph construction

Final split:

```text
train = 5,677
valid = 500
test  = 500
```

Split policy:

```text
coverage_safe = true
valid/test gold drugs appear in train candidate universe
valid/test query diseases appear in train target relation
valid/test approved target triples removed from train graph
exact leakage = 0
```

Graph summary:

```text
train_enriched_edges = 90,804
num_entities = 8,818
num_relations = 63
graph_num_rels = 63
target_relation_id = 61
failed_relation_id = 62
```

Kept graph edge families:

```text
target_approved = 5,677
failed_diagnostic = 3,222
compound_gene = 39,017
gene_gene = 42,888
```

Graph interpretation:

```text
The repoDB evidence graph combines train approved target edges, failed-like diagnostic edges, DRKG compound-gene evidence for mapped DrugBank compounds, and DRKG gene-gene bridge evidence.
```

---

## 5. Structure baselines

Six structure baselines were run under the reviewer-safe top-20 protocol:

```text
TransE
DistMult
ComplEx
RotatE
R-GCN
HRGAT
```

## 5.1 Baseline table

| Model | Valid Gold@20 | Valid MRR@20 | Valid H@10 | Valid Top1Dom | Test Gold@20 | Test MRR@20 | Test H@10 | Test Top1Dom |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| DistMult | 0.510 | 0.1013 | 0.362 | 0.134 | 0.482 | 0.1041 | 0.320 | 0.146 |
| ComplEx | 0.540 | 0.0876 | 0.350 | 0.106 | 0.502 | 0.0836 | 0.312 | 0.124 |
| TransE | 0.282 | 0.0623 | 0.152 | 0.242 | 0.248 | 0.0530 | 0.130 | 0.218 |
| R-GCN | 0.236 | 0.0570 | 0.144 | 0.528 | 0.214 | 0.0481 | 0.128 | 0.512 |
| HRGAT | 0.240 | 0.0521 | 0.150 | 0.452 | 0.222 | 0.0523 | 0.146 | 0.482 |
| RotatE | 0.198 | 0.0225 | 0.090 | 0.022 | 0.202 | 0.0217 | 0.100 | 0.026 |

Interpretation:

```text
DistMult is the strongest standalone structure-only candidate generator on repoDB.
R-GCN is retained as the main DrKGC/SoftFuse-consistency source.
```

Paper-safe claim:

```text
On repoDB, SoftFuse-KGC should not be claimed to outperform the strongest standalone structure-only baseline. Instead, repoDB is used to test clinical external validation behavior and evidence-efficiency for the R-GCN graph-LLM source.
```

---

## 6. Source package and display patch

Main source:

```text
main_source = R-GCN
source_path = dataset/setting_f_repodb/06_fograg_ready/rgcn
embedding_shape = [8818, 128]
graph_num_rels = 63
```

Diagnostic source:

```text
diagnostic_source = DistMult
```

A display-name patch was required before E2E because generation/evaluation matches text, while graph embeddings require canonical IDs.

Final field policy:

```text
rank_entities = display drug names for infer.py text matching
rank_entities_canonical = Compound::DBxxxxx canonical IDs
rank_entities_id = numeric entity IDs for graph embeddings
output = display gold drug name
```

Final raw-display-control package:

```text
dataset/setting_f_repodb/09_e2e_soft_support_ready/rgcn_raw_display_control
```

Raw-display-control metrics:

| Split | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Rank21 | Top1Dom | Avg graph |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Valid | 0.236 | 0.0570 | 0.026 | 0.048 | 0.144 | 382 | 0.528 | 100 |
| Test | 0.214 | 0.0481 | 0.018 | 0.040 | 0.128 | 393 | 0.512 | 100 |

---

## 7. Soft-support result

Initial and conservative soft-support sweeps did not improve the R-GCN source.

Best conservative selected variant:

```text
variant = soft_support_sweep_beta0.00_raw0.95
beta = 0.00
raw_weight = 0.95
gamma = 0.20
```

Candidate-stage comparison:

| Split | Row | Gold@20 | MRR@20 | H@10 | Top1Dom | Rank21 |
|---|---|---:|---:|---:|---:|---:|
| Valid | R-GCN raw | 0.236 | 0.0570 | 0.144 | 0.528 | 382 |
| Valid | soft_support_sweep | 0.236 | 0.0570 | 0.144 | 0.528 | 382 |
| Test | R-GCN raw | 0.214 | 0.0481 | 0.128 | 0.512 | 393 |
| Test | soft_support_sweep | 0.214 | 0.0481 | 0.128 | 0.512 | 393 |

Interpretation:

```text
Soft-support re-ranking is a diagnostic/negative row on repoDB.
The support features were not sufficiently query-specific because repoDB diseases are local UMLS nodes and there is no disease-gene evidence in the reused graph.
```

Paper-safe conclusion:

```text
Soft-support re-ranking is dataset-dependent and did not improve repoDB.
```

---

## 8. Fuzzy retrieval result

Fuzzy retrieval input:

```text
dataset/setting_f_repodb/09_e2e_soft_support_ready/rgcn_raw_display_control
```

Fuzzy retrieval output:

```text
dataset/setting_f_repodb/11_e2e_fuzzy_retrieval_ready/rgcn
```

Candidate metrics are preserved exactly:

| Split | Raw MRR@20 | Fuzzy MRR@20 | Metrics preserved | Raw graph | Fuzzy graph | Reduction |
|---|---:|---:|---:|---:|---:|---:|
| Train | preserved | preserved | True | 100 | 55 | 45% |
| Valid | 0.0570 | 0.0570 | True | 100 | 55 | 45% |
| Test | 0.0481 | 0.0481 | True | 100 | 55 | 45% |

Fuzzy retrieval audit:

```text
bad_candidate_len = 0
bad_query_placeholder = 0
bad_entity_placeholder = 0
bad_display_rank_entities = 0
valid/test exact subgraph leaks = 0
candidate_order_mismatch = 0
avg_selected_subgraph_size = 55
```

Interpretation:

```text
Fuzzy retrieval is successful on repoDB as an evidence-efficiency module.
It preserves candidate ranking while reducing graph size by 45%.
```

---

## 9. E2E Llama-3.2-3B results

Rows evaluated:

```text
backbone_raw
soft_support_sweep
fuzzy_retrieval_main
```

## 9.1 Valid E2E

| Row | Cand Gold@20 | Cand MRR@20 | E2E MRR@20 | E2E H@1 | E2E H@3 | E2E H@10 | Pred-in-cand | Invalid | Exact match | Top1Dom | Avg graph |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fuzzy_retrieval_main | 0.236 | 0.0570 | 0.0588 | 0.030 | 0.050 | 0.140 | 1.000 | 0.000 | 0.004 | 0.528 | 55 |
| backbone_raw | 0.236 | 0.0570 | 0.0587 | 0.030 | 0.050 | 0.140 | 0.998 | 0.002 | 0.004 | 0.528 | 100 |
| soft_support_sweep | 0.236 | 0.0570 | 0.0584 | 0.030 | 0.050 | 0.140 | 1.000 | 0.000 | 0.004 | 0.528 | 100 |

## 9.2 Test E2E

| Row | Cand Gold@20 | Cand MRR@20 | E2E MRR@20 | E2E H@1 | E2E H@3 | E2E H@10 | Pred-in-cand | Invalid | Exact match | Top1Dom | Avg graph |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fuzzy_retrieval_main | 0.214 | 0.0481 | 0.0529 | 0.024 | 0.046 | 0.134 | 1.000 | 0.000 | 0.006 | 0.512 | 55 |
| soft_support_sweep | 0.214 | 0.0481 | 0.0509 | 0.022 | 0.042 | 0.132 | 1.000 | 0.000 | 0.006 | 0.512 | 100 |
| backbone_raw | 0.214 | 0.0481 | 0.0487 | 0.020 | 0.040 | 0.130 | 1.000 | 0.000 | 0.002 | 0.512 | 100 |

Main E2E conclusion:

```text
fuzzy_retrieval_main is the best repoDB E2E row on both valid and test.
```

Key values:

```text
Valid:
  backbone_raw E2E MRR = 0.0587
  fuzzy_retrieval_main E2E MRR = 0.0588
  graph = 100 → 55

Test:
  backbone_raw E2E MRR = 0.0487
  fuzzy_retrieval_main E2E MRR = 0.0529
  graph = 100 → 55
```

---

## 10. Prediction diagnostics

Sample predictions show that the model often selects frequent candidates such as:

```text
Cortisone acetate
Dexamethasone
Fusidic Acid
Hydrocortisone
Betamethasone
Prednisolone
```

Many early test examples have gold rank 21, meaning the gold drug is absent from the top-20 candidate list. In those cases, E2E adjusted rank remains 21 regardless of generation quality.

Diagnostic interpretation:

```text
repoDB E2E performance is candidate-limited.
Fuzzy retrieval improves graph efficiency and slightly improves E2E behavior, but it does not solve missing-gold candidate coverage.
```

---

## 11. Paper-facing interpretation

Recommended paragraph:

> On repoDB, we evaluated SoftFuse-KGC as a clinical drug-repositioning external validation task using approved drug-indication pairs. DistMult was the strongest standalone structure-only candidate generator, whereas R-GCN was retained as the graph-compatible DrKGC/SoftFuse source for cross-dataset consistency. The R-GCN source was challenging, with Gold@20 of 0.236/0.214 and candidate MRR@20 of 0.0570/0.0481 on validation/test. Soft-support re-ranking did not improve the R-GCN source at the candidate stage, indicating that support calibration is dataset-dependent when disease nodes are local UMLS concepts without disease-gene evidence. However, fuzzy retrieval preserved the R-GCN candidate ranking while reducing the average evidence graph size from 100 to 55 triples. It achieved the best E2E MRR among R-GCN-derived rows on both validation and test, improving test E2E MRR from 0.0487 to 0.0529 with zero invalid generations. Thus, repoDB supports the evidence-efficiency claim of SoftFuse-KGC while highlighting the limits of soft-support re-ranking under clinical benchmark constraints.

---

## 12. Limitations

```text
1. repoDB is not a full biomedical KG; it is a clinical drug-repositioning benchmark.
2. Disease nodes are local UMLS CUI nodes and do not map directly to DRKG disease nodes.
3. DRKG evidence is reused mainly through DrugBank compounds and compound-gene/gene-gene edges.
4. R-GCN is weaker than DistMult on repoDB candidate ranking.
5. Soft-support re-ranking did not improve repoDB candidate metrics.
6. E2E performance remains candidate-limited because many gold drugs are absent from R-GCN top-20.
7. Fuzzy retrieval improves evidence efficiency and E2E slightly, but it does not solve candidate coverage.
```

---

## 13. How to report repoDB in the main paper

Recommended placement:

```text
Main table:
  include repoDB candidate + E2E metrics for backbone_raw, soft_support_sweep, fuzzy_retrieval_main.

Baseline table:
  include all six structure baselines and explicitly mark DistMult as strongest standalone baseline.

Ablation/limitation:
  explain soft-support failure on repoDB.

Efficiency table:
  highlight fuzzy graph reduction 100 → 55 with preserved candidate metrics.
```

Recommended claim level:

```text
Strong claim:
  Fuzzy retrieval preserves ranking and improves evidence efficiency on repoDB.

Moderate claim:
  Fuzzy retrieval achieves the best R-GCN-derived E2E result on repoDB.

Limitation:
  Soft-support re-ranking is dataset-dependent and did not improve repoDB.

Do not claim:
  SoftFuse universally beats all structure baselines on repoDB.
```

---

## 14. Final closeout

```text
WEEK28_REPODB_CLOSEOUT
================================================================================
Dataset:
  repoDB

Task:
  (?, repoDB_approved_indication, disease)

Split:
  train/valid/test = 5677 / 500 / 500

Graph:
  entities = 8,818
  relations = 63
  graph_num_rels = 63
  train_enriched_edges = 90,804
  target_relation_id = 61
  failed_relation_id = 62
  exact leak = 0

Structure baselines:
  all six baselines completed
  strongest standalone baseline = DistMult
  main graph-compatible source = R-GCN

R-GCN source:
  valid Cand MRR = 0.0570
  test  Cand MRR = 0.0481
  valid Gold@20 = 0.236
  test  Gold@20 = 0.214
  Top1Dom = 0.528 / 0.512

Soft support:
  candidate improvement = no
  role = diagnostic/negative row
  interpretation = dataset-dependent limitation

Fuzzy retrieval:
  candidate metrics preserved = true
  graph size = 100 → 55
  graph reduction = 45%
  valid E2E MRR = 0.0588
  test  E2E MRR = 0.0529
  invalid rate = 0.000 / 0.000

Best repoDB R-GCN-derived row:
  fuzzy_retrieval_main

Final decision:
  REPODB_EXTERNAL_VALIDATION_COMPLETED
================================================================================
```

---

## 15. Next step after Week 28

```text
1. Stop adding new datasets.
2. Build 5-dataset cross-dataset summary table:
   PrimeKG, PharmKG, Hetionet, DRKG, repoDB.
3. Update manuscript with:
   - external validation section
   - evidence-efficiency table
   - dataset-dependent limitation of soft support
   - clinical repoDB validation paragraph
4. Prepare appendix:
   - per-dataset baseline tables
   - per-dataset E2E rows
   - sensitivity/robustness
   - failure examples
```
