# Day 6 — Error Review

## 1. Goal
Review ontology-only errors, classify edge cases, and prepare a clean interpretation before week 10.

## 2. Summary
- total_queries: 500
- fallback_queries: 100
- strict_empty_queries: 100
- gold_removed_queries: 354
- singleton_queries: 104
- direct_only_queries: 221
- mechanism_only_queries: 118
- mixed_support_queries: 61
- all_unsupported_queries: 100
- total_supported_candidates: 1918
- total_unsupported_candidates_final: 2000

## 3. Ranking / constraint context
- ranking_mrr: 0.31301793
- ranking_hits1: 0.244
- ranking_hits3: 0.278
- ranking_hits10: 0.434
- constraint_ConstraintViolationRate: 0.51046452
- constraint_QueryHasConstraintViolationRate: 0.2
- constraint_remaining_non_drug_candidates: 0
- constraint_unsupported_final_candidates: 2000
- constraint_fallback_queries: 100
- constraint_gold_in_topk_ontology: 146
- constraint_invalid_evidence_triples_day3: 10858
- constraint_unsupported_path_sequences_day3: 28306

## 4. Main issue tags
- gold_removed_by_ontology: 354
- direct_only: 221
- ranking_risk_small_candidate_set: 157
- mechanism_only: 118
- singleton_after_ontology: 104
- fallback_query: 100
- strict_empty: 100
- all_unsupported_after_fallback: 100
- mixed_support: 61

## 5. Sample fallback queries
- query=dyspepsia | gold=Magnesium trisilicate | top5=['Fusidic acid', 'Oxytetracycline', 'Dexamethasone', 'Methylprednisolone', 'Methdilazine'] | support=['unsupported', 'unsupported', 'unsupported', 'unsupported', 'unsupported']
- query=Norwegian scabies | gold=Lindane | top5=['Fusidic acid', 'Oxytetracycline', 'Tetracycline', 'Tobramycin', 'Dexamethasone'] | support=['unsupported', 'unsupported', 'unsupported', 'unsupported', 'unsupported']
- query=migraine with or without aura, susceptibility to | gold=Acetylsalicylic acid | top5=['Fusidic acid', 'Methylprednisolone', 'Dexamethasone', 'Prednisolone', 'Cortisone acetate'] | support=['unsupported', 'unsupported', 'unsupported', 'unsupported', 'unsupported']
- query=chromomycosis | gold=Ketoconazole | top5=['Fusidic acid', 'Prednisolone', 'Dexamethasone', 'Methylprednisolone', 'Cortisone acetate'] | support=['unsupported', 'unsupported', 'unsupported', 'unsupported', 'unsupported']
- query=pulmonary emphysema | gold=Ipratropium | top5=['Betamethasone', 'Hydrocortisone', 'Methylprednisolone', 'Triamcinolone', 'Cortisone acetate'] | support=['unsupported', 'unsupported', 'unsupported', 'unsupported', 'unsupported']
- query=respiratory tract infectious disease | gold=Loracarbef | top5=['Fusidic acid', 'Oxytetracycline', 'Dexamethasone', 'Methylprednisolone', 'Methdilazine'] | support=['unsupported', 'unsupported', 'unsupported', 'unsupported', 'unsupported']
- query=hemiparkinsonism-hemiatrophy syndrome | gold=Biperiden | top5=['Betamethasone', 'Hydrocortisone', 'Cortisone acetate', 'Triamcinolone', 'Methylprednisolone'] | support=['unsupported', 'unsupported', 'unsupported', 'unsupported', 'unsupported']
- query=cerebral infarction | gold=Telmisartan | top5=['Betamethasone', 'Methylprednisolone', 'Hydrocortisone', 'Cortisone acetate', 'Triamcinolone'] | support=['unsupported', 'unsupported', 'unsupported', 'unsupported', 'unsupported']
- query=hereditary angioedema with C1Inh deficiency | gold=Icatibant | top5=['Methylprednisolone', 'Betamethasone', 'Hydrocortisone', 'Triamcinolone', 'Cortisone acetate'] | support=['unsupported', 'unsupported', 'unsupported', 'unsupported', 'unsupported']
- query=gastroesophageal reflux disease | gold=Magnesium carbonate | top5=['Fusidic acid', 'Methylprednisolone', 'Dexamethasone', 'Cortisone acetate', 'Prednisolone'] | support=['unsupported', 'unsupported', 'unsupported', 'unsupported', 'unsupported']

## 6. Sample gold-removed queries
- query=leukemia, lymphocytic, susceptibility to | gold=Cortisone acetate | gold_in_topk_ready=True | gold_in_topk_ontology=False | fallback=False
- query=streptococcal infection | gold=Cefixime | gold_in_topk_ready=True | gold_in_topk_ontology=False | fallback=False
- query=obsessive-compulsive disorder | gold=Fluoxetine | gold_in_topk_ready=True | gold_in_topk_ontology=False | fallback=False
- query=hypertension | gold=Amiloride | gold_in_topk_ready=True | gold_in_topk_ontology=False | fallback=False
- query=pneumococcal meningitis | gold=Meropenem | gold_in_topk_ready=True | gold_in_topk_ontology=False | fallback=False
- query=arthropathy | gold=Diflunisal | gold_in_topk_ready=True | gold_in_topk_ontology=False | fallback=False
- query=diffuse large B-cell lymphoma | gold=Doxorubicin | gold_in_topk_ready=True | gold_in_topk_ontology=False | fallback=False
- query=obsolete Hodgkin's granuloma | gold=Betamethasone | gold_in_topk_ready=True | gold_in_topk_ontology=False | fallback=False
- query=infectious anterior uveitis | gold=Dexamethasone | gold_in_topk_ready=True | gold_in_topk_ontology=False | fallback=False
- query=proctitis | gold=Pramocaine | gold_in_topk_ready=True | gold_in_topk_ontology=False | fallback=False

## 7. Sample mechanism-only queries
- query=basal cell carcinoma | gold=Vismodegib | top5=['Vismodegib'] | support=['mechanism']
- query=obsessive-compulsive disorder | gold=Fluoxetine | top5=['Propranolol'] | support=['mechanism']
- query=hypertension | gold=Amiloride | top5=['Dexamethasone'] | support=['mechanism']
- query=obsessive-compulsive disorder | gold=Paroxetine | top5=['Propranolol', 'Paroxetine'] | support=['mechanism', 'mechanism']
- query=hemoglobinopathy | gold=Phenprocoumon | top5=['Dexamethasone', 'Hydrocortisone acetate'] | support=['mechanism', 'mechanism']
- query=prostate cancer | gold=Estramustine | top5=['Hydrocortisone', 'Methylprednisolone', 'Dexamethasone', 'Hydrocortisone acetate', 'Doxorubicin'] | support=['mechanism', 'mechanism', 'mechanism', 'mechanism', 'mechanism']
- query=mental disorder | gold=Paliperidone | top5=['Propranolol'] | support=['mechanism']
- query=arteriosclerosis disorder | gold=Fluvastatin | top5=['Dexamethasone'] | support=['mechanism']
- query=visual epilepsy | gold=Phenobarbital | top5=['Dexamethasone', 'Propranolol', 'Vinblastine'] | support=['mechanism', 'mechanism', 'mechanism']
- query=scleroderma (disease) | gold=Aminobenzoic acid | top5=['Propranolol'] | support=['mechanism']

## 8. Interpretation
- Day 6 does not introduce new modeling changes.
- The main purpose is to separate strict ontology behavior from fallback-driven sanity behavior.
- If fallback dominates the row, week 10 should attach hard/soft safety to the supported subset carefully.

## 9. Day-6 decision
- Decision: CONDITIONAL GO
