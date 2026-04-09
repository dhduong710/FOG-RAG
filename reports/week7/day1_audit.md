# Day 1 Audit — Week 7

## Scope

- Audit week-6 coarse ranker / candidate source.
- Confirm whether the main bottleneck is retrieval quality rather than backbone path.

## Key numbers

- valid_recall20_raw = 0.020000
- valid_top1_hit_ratio_raw = 0.000000
- valid_inject_ratio_ready = 0.980000
- unique_top1_count = 12
- top1_dominance_ratio = 0.568000
- mean_jaccard_top20_between_queries = 0.418300
- duplicate_candidates_within_query_ratio = 0.000000
- week6_valid_metrics = {"mrr": 0.83680612, "hits1": 0.804, "hits3": 0.808, "hits10": 0.946, "num_examples": 500, "split": "valid"}
- error_breakdown = {"prediction_equals_gold": 401, "gold_not_in_candidate": 90, "prediction_in_candidate_but_not_top": 9}

## Conclusion

- Backbone path is technically clean enough for scientific checking on valid.
- Raw candidate recall is extremely weak; coarse ranker quality is still the main bottleneck.
- Inject dependence is extremely high; reranker still relies heavily on injected gold.
- Top-1 dominance suggests score collapse toward a few generic drugs.
- The dominant failure mode is retrieval miss rather than reranking discrimination.
- Day 2 should prioritize ranker stability and score quality, not complexity expansion.

## Must-fix focus for Day 2

- Keep R-GCN as the main path.
- Improve stability and score discrimination.
- Do not expand many baselines yet.

## Example missing-gold cases

- query=leukemia, lymphocytic, susceptibility to | gold=Cortisone acetate | gold_rank_in_full_universe=556 | gold_injected=True | raw_top5=['Cholestyramine', 'Neratinib', 'Talaporfin', 'Infliximab', 'Levomethadone']
- query=streptococcal infection | gold=Cefixime | gold_rank_in_full_universe=1119 | gold_injected=True | raw_top5=['Azathioprine', 'Adenosine phosphate', 'Bexarotene', 'Tofacitinib', 'Arsenic trioxide']
- query=dyspepsia | gold=Magnesium trisilicate | gold_rank_in_full_universe=845 | gold_injected=True | raw_top5=['Azathioprine', 'Bexarotene', 'Tofacitinib', 'Arsenic trioxide', 'Podofilox']
- query=basal cell carcinoma | gold=Vismodegib | gold_rank_in_full_universe=1261 | gold_injected=True | raw_top5=['Cholestyramine', 'Neratinib', 'Talaporfin', 'Infliximab', 'Levomethadone']
- query=obsessive-compulsive disorder | gold=Fluoxetine | gold_rank_in_full_universe=1055 | gold_injected=True | raw_top5=['Cholestyramine', 'Neratinib', 'Talaporfin', 'Levomethadone', 'Infliximab']
- query=Norwegian scabies | gold=Lindane | gold_rank_in_full_universe=478 | gold_injected=True | raw_top5=['Acenocoumarol', 'Omacetaxine mepesuccinate', 'Beraprost', 'Mebendazole', 'Vinflunine']
- query=hypertension | gold=Amiloride | gold_rank_in_full_universe=1444 | gold_injected=True | raw_top5=['Cholestyramine', 'Neratinib', 'Talaporfin', 'Golimumab', 'Infliximab']
- query=pneumococcal meningitis | gold=Meropenem | gold_rank_in_full_universe=1455 | gold_injected=True | raw_top5=['Acenocoumarol', 'Omacetaxine mepesuccinate', 'Beraprost', 'Albendazole', 'Mebendazole']
- query=obsessive-compulsive disorder | gold=Paroxetine | gold_rank_in_full_universe=1110 | gold_injected=True | raw_top5=['Cholestyramine', 'Neratinib', 'Talaporfin', 'Levomethadone', 'Infliximab']
- query=arthropathy | gold=Diflunisal | gold_rank_in_full_universe=100 | gold_injected=True | raw_top5=['Cholestyramine', 'Neratinib', 'Talaporfin', 'Infliximab', 'Golimumab']

## Example prediction error cases

### prediction_equals_gold
- query=leukemia, lymphocytic, susceptibility to | target=Cortisone acetate | pred=Cortisone acetate | pred_rank=1 | pred_in_candidate=True | gold_in_topk_raw=False | gold_injected=True | top5=['Cholestyramine', 'Neratinib', 'Talaporfin', 'Infliximab', 'Levomethadone']
- query=streptococcal infection | target=Cefixime | pred=Cefixime | pred_rank=1 | pred_in_candidate=True | gold_in_topk_raw=False | gold_injected=True | top5=['Azathioprine', 'Adenosine phosphate', 'Bexarotene', 'Tofacitinib', 'Arsenic trioxide']
- query=dyspepsia | target=Magnesium trisilicate | pred=Magnesium trisilicate | pred_rank=1 | pred_in_candidate=True | gold_in_topk_raw=False | gold_injected=True | top5=['Azathioprine', 'Bexarotene', 'Tofacitinib', 'Arsenic trioxide', 'Podofilox']
- query=basal cell carcinoma | target=Vismodegib | pred=Vismodegib | pred_rank=1 | pred_in_candidate=True | gold_in_topk_raw=False | gold_injected=True | top5=['Cholestyramine', 'Neratinib', 'Talaporfin', 'Infliximab', 'Levomethadone']
- query=obsessive-compulsive disorder | target=Fluoxetine | pred=Fluoxetine | pred_rank=1 | pred_in_candidate=True | gold_in_topk_raw=False | gold_injected=True | top5=['Cholestyramine', 'Neratinib', 'Talaporfin', 'Levomethadone', 'Infliximab']

### gold_not_in_candidate
- query=arteriosclerosis disorder | target=Fluvastatin | pred=Infliximab | pred_rank=4 | pred_in_candidate=True | gold_in_topk_raw=False | gold_injected=True | top5=['Cholestyramine', 'Neratinib', 'Talaporfin', 'Infliximab', 'Levomethadone']
- query=hyperparathyroidism | target=Alfacalcidol | pred=Evocalcet | pred_rank=16 | pred_in_candidate=True | gold_in_topk_raw=False | gold_injected=True | top5=['Cholestyramine', 'Neratinib', 'Talaporfin', 'Infliximab', 'Golimumab']
- query=eye disease | target=Betamethasone | pred=Vincristine | pred_rank=16 | pred_in_candidate=True | gold_in_topk_raw=False | gold_injected=True | top5=['Acenocoumarol', 'Omacetaxine mepesuccinate', 'Vinflunine', 'Mebendazole', 'Tofacitinib']
- query=spondyloarthropathy, susceptibility to | target=Acemetacin | pred=Infliximab | pred_rank=5 | pred_in_candidate=True | gold_in_topk_raw=False | gold_injected=True | top5=['Cholestyramine', 'Neratinib', 'Talaporfin', 'Levomethadone', 'Infliximab']
- query=Zollinger-Ellison syndrome | target=Famotidine | pred=Dihydrotachysterol | pred_rank=8 | pred_in_candidate=True | gold_in_topk_raw=False | gold_injected=True | top5=['Cholestyramine', 'Neratinib', 'Infliximab', 'Talaporfin', 'Golimumab']

### prediction_in_candidate_but_not_top
- query=adenocarcinoma of liver and intrahepatic biliary tract | target=Ramucirumab | pred=Infliximab | pred_rank=4 | pred_in_candidate=True | gold_in_topk_raw=True | gold_injected=False | top5=['Cholestyramine', 'Neratinib', 'Talaporfin', 'Infliximab', 'Levomethadone']
- query=spondyloarthropathy, susceptibility to | target=Adalimumab | pred=Infliximab | pred_rank=5 | pred_in_candidate=True | gold_in_topk_raw=True | gold_injected=False | top5=['Cholestyramine', 'Neratinib', 'Talaporfin', 'Levomethadone', 'Infliximab']
- query=anxiety disorder | target=Mebanazine | pred=Infliximab | pred_rank=4 | pred_in_candidate=True | gold_in_topk_raw=True | gold_injected=False | top5=['Cholestyramine', 'Neratinib', 'Talaporfin', 'Infliximab', 'Levomethadone']
- query=hepatocellular carcinoma | target=Ramucirumab | pred=Infliximab | pred_rank=4 | pred_in_candidate=True | gold_in_topk_raw=True | gold_injected=False | top5=['Cholestyramine', 'Neratinib', 'Talaporfin', 'Infliximab', 'Levomethadone']
- query=ascaridiasis | target=Mebendazole | pred=Albendazole | pred_rank=4 | pred_in_candidate=True | gold_in_topk_raw=True | gold_injected=False | top5=['Acenocoumarol', 'Omacetaxine mepesuccinate', 'Beraprost', 'Albendazole', 'Mebendazole']

