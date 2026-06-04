# Week 23 Closeout — PharmKG Transfer and E2E Evaluation

## 1. Decision

**WEEK23_PHARMKG_TRANSFER_CLOSEOUT_COMPLETE**

Week 23 successfully completed the PharmKG transfer study for FOG-RAG. The dataset is used as a secondary transfer benchmark, not as the primary dataset. The relation `T` is reported as `therapeutic_association_proxy`, not as clinical indication.

## 2. Protocol

- Task: `(? , T, disease)` head prediction.
- Missing entity: drug/chemical.
- Relation name for paper: `therapeutic_association_proxy`.
- Candidate size: top-20.
- Valid/test gold injection: **false**.
- Reviewer-safe metric: `RR = 1/rank` if `rank <= 20`, otherwise `0`.
- Rank-absent sentinel: `21`.

## 3. Candidate-level transfer results

| Row | Valid Gold@20 | Valid MRR@20 | Valid H@10 | Test Gold@20 | Test MRR@20 | Test H@10 | Avg subgraph | Note |
|---|---|---|---|---|---|---|---|---|
| backbone_raw | 0.070 | 0.017846 | 0.034 | 0.092 | 0.020481 | 0.046 | 100 | R-GCN raw top-20 source. |
| hard_support_raw | 0.070 | 0.017846 | 0.034 | 0.092 | 0.020481 | 0.046 | 100 | Negative control; support features saturated and same as backbone. |
| soft_support_raw | 0.070 | 0.021308 | 0.054 | 0.092 | 0.028159 | 0.068 | 100 | Soft support b050; no pruning and no gold injection. |
| fuzzy_retrieval_main | 0.070 | 0.021308 | 0.054 | 0.092 | 0.028159 | 0.068 | 55 | Preserves soft ranking and compresses evidence subgraph. |

**Interpretation.** `soft_support_raw` improves MRR@20 over `backbone_raw` on both valid and test without changing Gold@20. `fuzzy_retrieval_main` preserves the soft-support ranking and reduces the evidence subgraph from 100 to 55 triples.

## 4. Llama-3.2-3B E2E reviewer-safe results

| Split | Row | Gold@20 | Cand MRR | E2E MRR | H@1 | H@3 | H@10 | Pred-in-cand | Invalid | Rank21 |
|---|---|---|---|---|---|---|---|---|---|---|
| valid | backbone_raw | 0.070 | 0.017846 | 0.015410 | 0.006 | 0.014 | 0.034 | 0.526 | 0.474 | 465 |
| valid | soft_support_raw | 0.070 | 0.021308 | 0.017157 | 0.004 | 0.020 | 0.052 | 0.360 | 0.640 | 465 |
| valid | fuzzy_retrieval_main | 0.070 | 0.021308 | 0.017184 | 0.004 | 0.020 | 0.052 | 0.376 | 0.624 | 465 |
| test | backbone_raw | 0.092 | 0.020481 | 0.015575 | 0.000 | 0.018 | 0.044 | 0.510 | 0.490 | 454 |
| test | soft_support_raw | 0.092 | 0.028159 | 0.020587 | 0.000 | 0.030 | 0.062 | 0.390 | 0.610 | 454 |
| test | fuzzy_retrieval_main | 0.092 | 0.028159 | 0.020971 | 0.002 | 0.030 | 0.062 | 0.412 | 0.588 | 454 |

**Interpretation.** On the locked test split, Llama-3.2-3B improves from `0.015575` E2E MRR@20 on `backbone_raw` to `0.020587` on `soft_support_raw` and `0.020971` on `fuzzy_retrieval_main`.

## 5. Base LLM model comparison

| Model | Split | Row | Gold@20 | Cand MRR | E2E MRR | H@1 | H@3 | H@10 | Pred-in-cand | Invalid |
|---|---|---|---|---|---|---|---|---|---|---|
| llama3_2_3b | valid | backbone_raw | 0.070 | 0.017846 | 0.015410 | 0.006 | 0.014 | 0.034 | 0.526 | 0.474 |
| llama3_2_3b | valid | soft_support_raw | 0.070 | 0.021308 | 0.017157 | 0.004 | 0.020 | 0.052 | 0.360 | 0.640 |
| llama3_2_3b | valid | fuzzy_retrieval_main | 0.070 | 0.021308 | 0.017184 | 0.004 | 0.020 | 0.052 | 0.376 | 0.624 |
| llama3_2_3b | test | backbone_raw | 0.092 | 0.020481 | 0.015575 | 0.000 | 0.018 | 0.044 | 0.510 | 0.490 |
| llama3_2_3b | test | soft_support_raw | 0.092 | 0.028159 | 0.020587 | 0.000 | 0.030 | 0.062 | 0.390 | 0.610 |
| llama3_2_3b | test | fuzzy_retrieval_main | 0.092 | 0.028159 | 0.020971 | 0.002 | 0.030 | 0.062 | 0.412 | 0.588 |
| llama3_8b | valid | backbone_raw | 0.070 | 0.017846 | 0.013936 | 0.004 | 0.014 | 0.034 | 0.522 | 0.478 |
| llama3_8b | valid | soft_support_raw | 0.070 | 0.021308 | 0.015676 | 0.002 | 0.020 | 0.050 | 0.290 | 0.710 |
| llama3_8b | valid | fuzzy_retrieval_main | 0.070 | 0.021308 | 0.016767 | 0.004 | 0.020 | 0.052 | 0.364 | 0.636 |
| llama3_8b | test | backbone_raw | 0.092 | 0.020481 | 0.016193 | 0.002 | 0.014 | 0.044 | 0.510 | 0.490 |
| llama3_8b | test | soft_support_raw | 0.092 | 0.028159 | 0.019072 | 0.000 | 0.026 | 0.064 | 0.304 | 0.696 |
| llama3_8b | test | fuzzy_retrieval_main | 0.092 | 0.028159 | 0.020413 | 0.002 | 0.026 | 0.064 | 0.350 | 0.650 |
| medllama3_8b | valid | backbone_raw | 0.070 | 0.017846 | 0.011300 | 0.000 | 0.014 | 0.034 | 0.000 | 1.000 |
| medllama3_8b | valid | soft_support_raw | 0.070 | 0.021308 | 0.013894 | 0.000 | 0.020 | 0.050 | 0.020 | 0.980 |
| medllama3_8b | valid | fuzzy_retrieval_main | 0.070 | 0.021308 | 0.013894 | 0.000 | 0.020 | 0.050 | 0.020 | 0.980 |
| medllama3_8b | test | backbone_raw | 0.092 | 0.020481 | 0.014034 | 0.000 | 0.014 | 0.044 | 0.000 | 1.000 |
| medllama3_8b | test | soft_support_raw | 0.092 | 0.028159 | 0.018583 | 0.000 | 0.024 | 0.060 | 0.022 | 0.978 |
| medllama3_8b | test | fuzzy_retrieval_main | 0.092 | 0.028159 | 0.018583 | 0.000 | 0.024 | 0.060 | 0.022 | 0.978 |
| mistral_7b | valid | backbone_raw | 0.070 | 0.017846 | 0.011300 | 0.000 | 0.014 | 0.034 | 0.000 | 1.000 |
| mistral_7b | valid | soft_support_raw | 0.070 | 0.021308 | 0.013836 | 0.000 | 0.020 | 0.050 | 0.020 | 0.980 |
| mistral_7b | valid | fuzzy_retrieval_main | 0.070 | 0.021308 | 0.013836 | 0.000 | 0.020 | 0.050 | 0.018 | 0.982 |
| mistral_7b | test | backbone_raw | 0.092 | 0.020481 | 0.014034 | 0.000 | 0.014 | 0.044 | 0.000 | 1.000 |
| mistral_7b | test | soft_support_raw | 0.092 | 0.028159 | 0.018650 | 0.000 | 0.024 | 0.060 | 0.014 | 0.986 |
| mistral_7b | test | fuzzy_retrieval_main | 0.092 | 0.028159 | 0.018650 | 0.000 | 0.024 | 0.060 | 0.014 | 0.986 |

**Best test fuzzy model:** `llama3_2_3b` with E2E MRR@20 = `0.020971`.

**Interpretation.** Larger or biomedical-specific base LLMs did not necessarily improve E2E generation. Several 7B/8B base models produced repeated strings or candidate-list fragments, resulting in high invalid prediction rates. This supports reporting Llama-3.2-3B as the primary PharmKG E2E model and treating the other base models as diagnostic comparisons.

## 6. Paper-ready statement

> On the PharmKG therapeutic-association proxy task, soft support improves reviewer-safe top-20 ranking without valid/test gold injection. On the locked test split, candidate-level MRR@20 improves from 0.0205 to 0.0282, while fuzzy retrieval preserves this gain and reduces the retrieved evidence subgraph from 100 to 55 triples. In E2E LLM evaluation with Llama-3.2-3B, FOG-RAG improves reviewer-safe MRR@20 from 0.0156 to 0.0210. Additional base LLM comparisons show the same direction of improvement but also reveal a generation-format limitation: larger or biomedical-specific base LLMs often produce invalid candidate-list fragments rather than a single entity.

## 7. What not to claim

- Do **not** call PharmKG relation `T` a clinical indication relation.
- Do **not** claim Gold@20 or candidate recall improvement.
- Do **not** claim full-universe PharmKG KGC superiority.
- Do **not** claim fuzzy retrieval reduces shortcut rate on PharmKG.
- Do **not** use raw `infer.py` MRR as paper metric; use reviewer-safe MRR only.

## 8. Final Week 23 status

Week 23 is closed. PharmKG is ready to be used as a secondary transfer dataset in the paper. The main paper story remains PrimeKG Setting A, while PharmKG supports transferability and highlights remaining E2E generation limitations.