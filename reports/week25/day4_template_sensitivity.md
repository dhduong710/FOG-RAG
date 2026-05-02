# Week 25 Day 4  Question-Template Sensitivity

- Decision: **QUESTION_TEMPLATE_SENSITIVITY_READY**
- Created at: `2026-05-02T04:36:05`
- Main row: **retrieval_main**
- Primary model: **Llama-3.2-3B**
- Frozen decoding: **cfg01_mnt16_rp100_ng0**
- Policy: reviewer-safe RR@20, no test tuning

## Template variants

| Variant | Template |
| --- | --- |
| T0_canonical | What drug is indicated for {query_entity}? |
| T1_treatment | Which drug is used to treat {query_entity}? |
| T2_medication | Which medication is indicated for {query_entity}? |
| T3_association_neutral | What drug is therapeutically associated with {query_entity}? |

## VALID summary

| Variant | Gold@20 | Cand MRR@20 | E2E MRR@20 | E2E H@3 | E2E H@10 | Pred-in-cand | Invalid | List-frag | Top1-copy | Pred change vs T0 | � E2E MRR vs T0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T0_canonical | 0.202 | 0.097644 | 0.058518 | 0.1 | 0.174 | 0.992 | 0.008 | 0.048 | 0.008 | 0.0 | 0.0 |
| T1_treatment | 0.202 | 0.097644 | 0.058518 | 0.1 | 0.174 | 0.986 | 0.014 | 0.05 | 0.01 | 0.04 | 0.0 |
| T2_medication | 0.202 | 0.097644 | 0.058518 | 0.1 | 0.174 | 0.994 | 0.006 | 0.048 | 0.008 | 0.022 | 0.0 |
| T3_association_neutral | 0.202 | 0.097644 | 0.058518 | 0.1 | 0.174 | 0.99 | 0.01 | 0.052 | 0.006 | 0.06 | 0.0 |

## TEST summary

| Variant | Gold@20 | Cand MRR@20 | E2E MRR@20 | E2E H@3 | E2E H@10 | Pred-in-cand | Invalid | List-frag | Top1-copy | Pred change vs T0 | � E2E MRR vs T0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T0_canonical | 0.24 | 0.125326 | 0.074687 | 0.132 | 0.218 | 0.998 | 0.002 | 0.07 | 0.01 | 0.0 | 0.0 |
| T1_treatment | 0.24 | 0.125326 | 0.074687 | 0.132 | 0.218 | 1.0 | 0.0 | 0.074 | 0.012 | 0.03 | 0.0 |
| T2_medication | 0.24 | 0.125326 | 0.074722 | 0.132 | 0.218 | 0.998 | 0.002 | 0.072 | 0.01 | 0.006 | 3.5e-05 |
| T3_association_neutral | 0.24 | 0.125326 | 0.074722 | 0.132 | 0.218 | 1.0 | 0.0 | 0.074 | 0.01 | 0.046 | 3.5e-05 |

## Interpretation guide

- Candidate metrics should remain identical across templates because candidate lists are fixed.
- If E2E MRR and invalid rate vary only slightly, the system is not strongly prompt-template sensitive.
- T0 remains the canonical PrimeKG indication prompt. T3 is robustness-only and should not redefine the task.

## Changed/problematic cases

### valid_T1_treatment
| idx | query | gold | T0 pred | variant pred | T0 rank | variant rank | rank delta | variant invalid |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 116 | migraine disorder | Naproxen | Fluticasone propionate | Migraine disorder | 21 | 21 | 0 | True |
| 136 | migraine disorder | Acetaminophen | Fluticasone propionate | Migraine disorder | 21 | 21 | 0 | True |
| 165 | migraine disorder | Almotriptan | Fluticasone propionate | Migraine disorder | 21 | 21 | 0 | True |
| 176 | migraine disorder | Ergotamine | Fluticasone propionate | Migraine disorder | 21 | 21 | 0 | True |
| 203 | iron deficiency anemia | Ferrous sulfate anhydrous | Iron | Iron | 21 | 21 | 0 | True |
| 288 | acute neonatal citrullinemia type I | Phenylbutyric acid | Citrullinemia type I | Citrullinemia type I | 21 | 21 | 0 | True |
| 311 | iron deficiency anemia | Ferric oxide | Iron | Iron | 21 | 21 | 0 | True |
| 120 | Hodgkin's paragranuloma | Procarbazine | Thiotepa | Cortisone acetate | 21 | 21 | 0 | False |
| 150 | mantle cell lymphoma | Hydrocortisone acetate | Desonide | Dexamethasone | 2 | 2 | 0 | False |
| 158 | mantle cell lymphoma | Mechlorethamine | Desonide | Dexamethasone | 4 | 4 | 0 | False |

### valid_T2_medication
| idx | query | gold | T0 pred | variant pred | T0 rank | variant rank | rank delta | variant invalid |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 116 | migraine disorder | Naproxen | Fluticasone propionate | Migraine disorder | 21 | 21 | 0 | True |
| 288 | acute neonatal citrullinemia type I | Phenylbutyric acid | Citrullinemia type I | Citrullinemia type I | 21 | 21 | 0 | True |
| 446 | Plasmodium vivax malaria | Pyronaridine | Plasmodium vivax malaria | Plasmodium vivax malaria | 21 | 21 | 0 | True |
| 28 | arteriosclerosis disorder | Fluvastatin | Hydroxyurea | Hydrocortisone | 21 | 21 | 0 | False |
| 203 | iron deficiency anemia | Ferrous sulfate anhydrous | Iron | Norfloxacin | 21 | 21 | 0 | False |
| 277 | ovarian carcinosarcoma | Hydroxyurea | Doxorubicin | Testosterone | 17 | 17 | 0 | False |
| 282 | Langerhans cell histiocytosis | Mechlorethamine | Desonide | Dexamethasone | 21 | 21 | 0 | False |
| 309 | Langerhans cell histiocytosis | Bleomycin | Desonide | Dexamethasone | 4 | 4 | 0 | False |
| 311 | iron deficiency anemia | Ferric oxide | Iron | Norfloxacin | 21 | 21 | 0 | False |
| 315 | ascaridiasis | Mebendazole | Cyproheptadine | Alimemazine | 21 | 21 | 0 | False |

### valid_T3_association_neutral
| idx | query | gold | T0 pred | variant pred | T0 rank | variant rank | rank delta | variant invalid |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 116 | migraine disorder | Naproxen | Fluticasone propionate | Migraine disorder | 21 | 21 | 0 | True |
| 136 | migraine disorder | Acetaminophen | Fluticasone propionate | Migraine disorder | 21 | 21 | 0 | True |
| 165 | migraine disorder | Almotriptan | Fluticasone propionate | Migraine disorder | 21 | 21 | 0 | True |
| 176 | migraine disorder | Ergotamine | Fluticasone propionate | Migraine disorder | 21 | 21 | 0 | True |
| 288 | acute neonatal citrullinemia type I | Phenylbutyric acid | Citrullinemia type I | Citrullinemia type I | 21 | 21 | 0 | True |
| 28 | arteriosclerosis disorder | Fluvastatin | Hydroxyurea | Hydrocortisone | 21 | 21 | 0 | False |
| 31 | visual epilepsy | Phenobarbital | Hydrocortisone | Hydroxyurea | 21 | 21 | 0 | False |
| 32 | scleroderma (disease) | Aminobenzoic acid | Hydroxyurea | Hydrocortisone | 21 | 21 | 0 | False |
| 72 | visual epilepsy | Lamotrigine | Hydrocortisone | Hydroxyurea | 21 | 21 | 0 | False |
| 73 | renal cell adenocarcinoma | Sirolimus | Hydroxyurea | Hydrocortisone | 21 | 21 | 0 | False |

### test_T1_treatment
| idx | query | gold | T0 pred | variant pred | T0 rank | variant rank | rank delta | variant invalid |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 60 | Langerhans cell histiocytosis | Doxorubicin | Desonide | Cortisone acetate | 3 | 3 | 0 | False |
| 73 | obsolete familial combined hyperlipidemia | Fenofibric acid | Thiotepa | Tetracycline | 21 | 21 | 0 | False |
| 97 | obsolete familial combined hyperlipidemia | Atorvastatin | Thiotepa | Tetracycline | 21 | 21 | 0 | False |
| 132 | argininosuccinic aciduria | Phenylbutyric acid | Phenylephrine | Doxycycline | 21 | 21 | 0 | False |
| 137 | AIDS | Etravirine | Ofloxacin | Fusidic acid | 21 | 21 | 0 | False |
| 149 | Hodgkin's paragranuloma | Triamcinolone | Thiotepa | Cortisone acetate | 2 | 2 | 0 | False |
| 182 | Hodgkins lymphoma | Prednisone | Desonide | Thiotepa | 2 | 2 | 0 | False |
| 232 | non-histaminic angioedema | Hydrocortisone | Ampicillin | Methylprednisolone | 3 | 3 | 0 | False |
| 265 | Plasmodium vivax malaria | Artesunate | Plasmodium vivax malaria | Methylprednisolone | 21 | 21 | 0 | False |
| 293 | Hodgkins lymphoma | Doxorubicin | Desonide | Thiotepa | 3 | 3 | 0 | False |

### test_T2_medication
| idx | query | gold | T0 pred | variant pred | T0 rank | variant rank | rank delta | variant invalid |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 346 | malignant otitis externa caused by Pseudomonas aeruginosa | Ofloxacin | Hydrocortisone | Hydrocortisone acetate | 8 | 7 | -1 | False |
| 265 | Plasmodium vivax malaria | Artesunate | Plasmodium vivax malaria | Plasmodium vivax malaria | 21 | 21 | 0 | True |
| 60 | Langerhans cell histiocytosis | Doxorubicin | Desonide | Dexamethasone | 3 | 3 | 0 | False |
| 437 | anxiety | Oxazepam | Alimemazine | Phenylephrine | 21 | 21 | 0 | False |

### test_T3_association_neutral
| idx | query | gold | T0 pred | variant pred | T0 rank | variant rank | rank delta | variant invalid |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 346 | malignant otitis externa caused by Pseudomonas aeruginosa | Ofloxacin | Hydrocortisone | Hydrocortisone acetate | 8 | 7 | -1 | False |
| 1 | acquired hyperprolactinemia | Cabergoline | Fusidic acid | Hydrocortisone | 21 | 21 | 0 | False |
| 60 | Langerhans cell histiocytosis | Doxorubicin | Desonide | Cortisone acetate | 3 | 3 | 0 | False |
| 73 | obsolete familial combined hyperlipidemia | Fenofibric acid | Thiotepa | Tetracycline | 21 | 21 | 0 | False |
| 87 | miliary tuberculosis | Prednisolone | Dexamethasone | Cortisone acetate | 4 | 4 | 0 | False |
| 96 | visual epilepsy | Carbamazepine | Hydrocortisone | Hydroxyurea | 21 | 21 | 0 | False |
| 97 | obsolete familial combined hyperlipidemia | Atorvastatin | Thiotepa | Tetracycline | 21 | 21 | 0 | False |
| 103 | classic Hodgkin lymphoma, lymphocyte-rich type | Chlorambucil | Desonide | Thiotepa | 21 | 21 | 0 | False |
| 167 | sympathetic paraganglioma | Phentolamine | Hydroxyurea | Hydrocortisone | 21 | 21 | 0 | False |
| 182 | Hodgkins lymphoma | Prednisone | Desonide | Thiotepa | 2 | 2 | 0 | False |

## Final decision

**QUESTION_TEMPLATE_SENSITIVITY_READY**
