# Week 25 Day 2  Rule Sensitivity Valid Analysis

- Decision: **RULE_SENSITIVITY_VALID_READY**
- Created at: `2026-05-02T03:47:17`
- Split: **valid**
- Main row: **main_rules / retrieval_main**

## Main valid table

| Variant | Gold@20 | Cand MRR@20 | H@1 | H@3 | H@10 | Rank21 | Avg graph | Cand coverage | Query coverage | Same cand order | Graph Jaccard vs main |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| main_rules | 0.202 | 0.097644 | 0.056 | 0.134 | 0.182 | 399 | 32.556 | 0.7845 | 1.0 | 1.0 | 1.0 |
| no_rules | 0.202 | 0.097644 | 0.056 | 0.134 | 0.182 | 399 | 60.45 | 0.7845 | 1.0 | 1.0 | 0.860085 |
| random_rules | 0.202 | 0.097644 | 0.056 | 0.134 | 0.182 | 399 | 32.556 | 0.7845 | 1.0 | 1.0 | 0.788629 |

## Interpretation

- If candidate MRR is identical across variants, this is expected because Day 2 keeps candidate ordering fixed or nearly fixed and mainly changes the graph evidence package.
- `no_rules` measures the effect of removing the Week15/16 confidence-aware fuzzy rule-selection layer and falling back to the soft-support source graph.
- `random_rules` is a negative control: it preserves query/candidate coverage as much as possible but breaks confidence-aware edge selection.
- Day 3 E2E inference will test whether these graph-package changes affect LLM predictions.

## Case samples with strongest graph differences

### no_rules
| idx | query | gold | rank main | rank var | graph main | graph var | Jaccard | top3 variant |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 488 | non-Hodgkin lymphoma | Hydrocortisone | 1 | 1 | 24 | 44 | 0.571429 | Hydrocortisone, Propranolol, Cortisone acetate |
| 120 | Hodgkin's paragranuloma | Procarbazine | 21 | 21 | 26 | 48 | 0.604651 | Triamcinolone, Prednisolone, Methotrexate |
| 147 | classic Hodgkin lymphoma, lymphocyte-rich type | Methylprednisolone | 1 | 1 | 26 | 48 | 0.604651 | Methylprednisolone, Doxorubicin, Fusidic acid |
| 170 | mantle cell lymphoma | Uracil mustard | 21 | 21 | 25 | 45 | 0.609756 | Hydrocortisone acetate, Propranolol, Mechlorethamine |
| 470 | Hodgkin's paragranuloma | Prednisolone | 2 | 2 | 26 | 48 | 0.619048 | Triamcinolone, Prednisolone, Methotrexate |
| 282 | Langerhans cell histiocytosis | Mechlorethamine | 21 | 21 | 25 | 46 | 0.625 | Fusidic acid, Doxorubicin, Bleomycin |
| 309 | Langerhans cell histiocytosis | Bleomycin | 3 | 3 | 25 | 46 | 0.625 | Fusidic acid, Doxorubicin, Bleomycin |
| 150 | mantle cell lymphoma | Hydrocortisone acetate | 1 | 1 | 25 | 45 | 0.625 | Hydrocortisone acetate, Propranolol, Mechlorethamine |
| 158 | mantle cell lymphoma | Mechlorethamine | 3 | 3 | 25 | 45 | 0.625 | Hydrocortisone acetate, Propranolol, Mechlorethamine |
| 42 | angioedema | Dexbrompheniramine | 21 | 21 | 29 | 53 | 0.630435 | Fusidic acid, Ofloxacin, Ciprofloxacin |

### random_rules
| idx | query | gold | rank main | rank var | graph main | graph var | Jaccard | top3 variant |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 120 | Hodgkin's paragranuloma | Procarbazine | 21 | 21 | 26 | 26 | 0.405405 | Triamcinolone, Prednisolone, Methotrexate |
| 309 | Langerhans cell histiocytosis | Bleomycin | 3 | 3 | 25 | 25 | 0.428571 | Fusidic acid, Doxorubicin, Bleomycin |
| 147 | classic Hodgkin lymphoma, lymphocyte-rich type | Methylprednisolone | 1 | 1 | 26 | 26 | 0.444444 | Methylprednisolone, Doxorubicin, Fusidic acid |
| 158 | mantle cell lymphoma | Mechlorethamine | 3 | 3 | 25 | 25 | 0.470588 | Hydrocortisone acetate, Propranolol, Mechlorethamine |
| 258 | seborrheic dermatitis | Chloroxine | 21 | 21 | 31 | 31 | 0.47619 | Cortisone acetate, Hydrocortisone acetate, Prednisone |
| 11 | obsolete Hodgkin's granuloma | Betamethasone | 2 | 2 | 27 | 27 | 0.5 | Triamcinolone, Betamethasone, Prednisolone |
| 317 | classic Hodgkin lymphoma | Methylprednisolone | 1 | 1 | 27 | 27 | 0.5 | Methylprednisolone, Doxorubicin, Methotrexate |
| 488 | non-Hodgkin lymphoma | Hydrocortisone | 1 | 1 | 24 | 24 | 0.5 | Hydrocortisone, Propranolol, Cortisone acetate |
| 149 | seborrheic keratosis | Sulfacetamide | 21 | 21 | 31 | 31 | 0.512195 | Fusidic acid, Hydrocortisone acetate, Ofloxacin |
| 44 | granulomatous slack skin disease | Prednisone | 2 | 2 | 28 | 28 | 0.513514 | Dexamethasone, Prednisone, Doxorubicin |

## Final decision

**RULE_SENSITIVITY_VALID_READY**
