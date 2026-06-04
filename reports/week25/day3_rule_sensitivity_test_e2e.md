# Week 25 Day 3  Rule Sensitivity Locked Test + E2E

- Decision: **RULE_SENSITIVITY_TEST_E2E_READY**
- Created at: `2026-05-02T04:05:16`
- Primary model: **Llama-3.2-3B**
- Frozen decoding: **cfg01_mnt16_rp100_ng0**
- Policy: reviewer-safe RR@20, no test tuning

## VALID summary

| Variant | Gold@20 | Cand MRR@20 | E2E MRR@20 | E2E H@3 | E2E H@10 | Pred-in-cand | Invalid | Top1-copy | Avg graph | � E2E MRR vs main |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| main_rules | 0.202 | 0.097644 | 0.058518 | 0.1 | 0.174 | 0.992 | 0.008 | 0.008 | 32.556 | 0.0 |
| no_rules | 0.202 | 0.097644 | 0.059944 | 0.102 | 0.172 | 0.964 | 0.036 | 0.002 | 60.45 | 0.001426 |
| random_rules | 0.202 | 0.097644 | 0.05999 | 0.102 | 0.174 | 0.992 | 0.008 | 0.002 | 32.556 | 0.001472 |

## TEST summary

| Variant | Gold@20 | Cand MRR@20 | E2E MRR@20 | E2E H@3 | E2E H@10 | Pred-in-cand | Invalid | Top1-copy | Avg graph | � E2E MRR vs main |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| main_rules | 0.24 | 0.125326 | 0.074687 | 0.132 | 0.218 | 0.998 | 0.002 | 0.01 | 32.34 | 0.0 |
| no_rules | 0.24 | 0.125326 | 0.074676 | 0.132 | 0.218 | 0.98 | 0.02 | 0.008 | 59.932 | -1.1e-05 |
| random_rules | 0.24 | 0.125326 | 0.074742 | 0.132 | 0.218 | 0.998 | 0.002 | 0.01 | 32.34 | 5.5e-05 |

## Interpretation guide

- `main_rules` remains the frozen Week 24 main graph package.
- `no_rules` uses the larger soft-support source graph. If its E2E score is close to main, FOG-RAG is not overly dependent on a single hard-coded rule package.
- `random_rules` is the negative control. If it is worse or less stable, that supports the value of confidence-aware evidence selection. If it is close, report it honestly as evidence that candidate ordering dominates E2E behavior.
- These rows are appendix sensitivity evidence and do not replace the Week 24 main result.

## Changed / problematic cases

### valid_no_rules
| idx | query | gold | main pred | variant pred | main rank | variant rank | rank delta | variant invalid |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20 | chronic cutaneous lupus erythematosus | Prednisolone | Cortisone acetate | Prednisolone | 4 | 1 | -3 | False |
| 10 | diffuse large B-cell lymphoma | Doxorubicin | Prednisolone | Dexamethasone | 8 | 9 | 1 | False |
| 162 | diffuse large B-cell lymphoma of the central nervous system | Doxorubicin | Prednisolone | Dexamethasone | 8 | 9 | 1 | False |
| 478 | acute myeloid leukemia with t(6;9)(p23;q34) | Doxorubicin | Hydrocortisone | Testosterone | 10 | 11 | 1 | False |
| 56 | hyperparathyroidism | Alfacalcidol | Desonide | !!!!!!!!!!!!!!!! | 21 | 21 | 0 | True |
| 64 | Zollinger-Ellison syndrome | Famotidine | Desonide | !!!!!!!!!!!!!!!! | 21 | 21 | 0 | True |
| 116 | migraine disorder | Naproxen | Fluticasone propionate | Migraine disorder | 21 | 21 | 0 | True |
| 136 | migraine disorder | Acetaminophen | Fluticasone propionate | Migraine disorder | 21 | 21 | 0 | True |
| 165 | migraine disorder | Almotriptan | Fluticasone propionate | Migraine disorder | 21 | 21 | 0 | True |
| 176 | migraine disorder | Ergotamine | Fluticasone propionate | Migraine disorder | 21 | 21 | 0 | True |

### valid_random_rules
| idx | query | gold | main pred | variant pred | main rank | variant rank | rank delta | variant invalid |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20 | chronic cutaneous lupus erythematosus | Prednisolone | Cortisone acetate | Prednisolone | 4 | 1 | -3 | False |
| 10 | diffuse large B-cell lymphoma | Doxorubicin | Prednisolone | Dexamethasone | 8 | 9 | 1 | False |
| 203 | iron deficiency anemia | Ferrous sulfate anhydrous | Iron | Iron | 21 | 21 | 0 | True |
| 288 | acute neonatal citrullinemia type I | Phenylbutyric acid | Citrullinemia type I | Citrullinemia type I | 21 | 21 | 0 | True |
| 311 | iron deficiency anemia | Ferric oxide | Iron | Iron | 21 | 21 | 0 | True |
| 446 | Plasmodium vivax malaria | Pyronaridine | Plasmodium vivax malaria | Plasmodium vivax malaria | 21 | 21 | 0 | True |
| 0 | leukemia, lymphocytic, susceptibility to | Cortisone acetate | Dexamethasone | Desonide | 2 | 2 | 0 | False |
| 9 | arthropathy | Diflunisal | Desonide | Fusidic acid | 21 | 21 | 0 | False |
| 22 | common cold | Cefprozil | Fluorometholone | Methdilazine | 21 | 21 | 0 | False |
| 23 | classic Hodgkin lymphoma | Mechlorethamine | Thiotepa | Carmustine | 21 | 21 | 0 | False |

### test_no_rules
| idx | query | gold | main pred | variant pred | main rank | variant rank | rank delta | variant invalid |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 432 | diffuse large B-cell lymphoma | Vincristine | Prednisolone | Dexamethasone | 13 | 14 | 1 | False |
| 65 | hyperinsulinism (disease) | Ranitidine | Desonide | !!!!!!!!!!!!!!!! | 21 | 21 | 0 | True |
| 99 | visceral leishmaniasis | Amphotericin B | Fusidic acid | !!!!!!!!!!!!!!!! | 21 | 21 | 0 | True |
| 132 | argininosuccinic aciduria | Phenylbutyric acid | Phenylephrine | !!!!!!!!!!!!!!!! | 21 | 21 | 0 | True |
| 220 | glaucoma | Bupranolol | Desonide | !!!!!!!!!!!!!!!! | 21 | 21 | 0 | True |
| 301 | pancreatic adenocarcinoma | Erlotinib | Prednisolone | !!!!!!!!!!!!!!!! | 21 | 21 | 0 | True |
| 442 | fallopian tube cancer | Paclitaxel | Alimemazine | !!!!!!!!!!!!!!!! | 21 | 21 | 0 | True |
| 453 | osteomalacia (disease) | Ergocalciferol | Desonide | !!!!!!!!!!!!!!!! | 21 | 21 | 0 | True |
| 490 | pancreatic adenocarcinoma | Gemcitabine | Prednisolone | !!!!!!!!!!!!!!!! | 21 | 21 | 0 | True |
| 491 | Graves disease | Carbimazole | Hydroxyurea | !!!!!!!!!!!!!!!! | 21 | 21 | 0 | True |

### test_random_rules
| idx | query | gold | main pred | variant pred | main rank | variant rank | rank delta | variant invalid |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 177 | pulmonary eosinophilia | Prednisone | Cortisone acetate | Prednisolone | 6 | 5 | -1 | False |
| 432 | diffuse large B-cell lymphoma | Vincristine | Prednisolone | Dexamethasone | 13 | 14 | 1 | False |
| 265 | Plasmodium vivax malaria | Artesunate | Plasmodium vivax malaria | Plasmodium vivax malaria | 21 | 21 | 0 | True |
| 2 | allergic rhinitis | Hydrocortisone | Dexamethasone | Phenylephrine | 4 | 4 | 0 | False |
| 15 | common cold | Ipratropium | Fluorometholone | Methdilazine | 21 | 21 | 0 | False |
| 16 | intrinsic asthma | Prednisolone | Methylprednisolone | Norfloxacin | 4 | 4 | 0 | False |
| 17 | classic Hodgkin lymphoma | Doxorubicin | Thiotepa | Carmustine | 3 | 3 | 0 | False |
| 20 | trichinosis | Prednisone | Methylprednisolone | Cortisone acetate | 6 | 6 | 0 | False |
| 22 | seborrheic dermatitis | Cortisone acetate | Methylprednisolone | Alimemazine | 2 | 2 | 0 | False |
| 23 | rheumatoid arthritis | Celecoxib | Cortisone acetate | Desonide | 21 | 21 | 0 | False |

## Final decision

**RULE_SENSITIVITY_TEST_E2E_READY**
