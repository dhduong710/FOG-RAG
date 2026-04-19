# Day 7 — Week 19 closeout

- status: **GO_PAPER_ASSEMBLY**
- paper_main_row: **`soft_support_fuzzy_retrieval_main`**
- next_step: **`paper_assembly_final_interpretation_figures_tables`**

## 1. Closeout checks
- soft_support_raw_test_built_clean: `True`
- retrieval_main_test_built_clean: `True`
- test_eval_ready_package_clean: `True`
- official_locked_test_main_table_clean: `True`
- test_side_supports_retrieval_main_as_main_row: `True`
- encoder_remains_appendix_only: `True`

## 2. Paper-facing decision
- paper_main_row: `soft_support_fuzzy_retrieval_main`
- reference_row: `backbone_raw`
- negative_control: `ontology_raw`
- candidate_stage_intermediate: `soft_support_raw`
- appendix_only: `['soft_support_fuzzy_encoder_probe_v0']`
- selected_source_variant: `soft_support_fuzzy_retrieval_tight`
- selected_source_variant_set_from_locked_test: `['soft_support_fuzzy_retrieval_tight']`

## 3. Candidate-stage gain vs backbone
- delta_mrr_at20: `0.06076335`
- delta_hits1_at20: `0.048`
- delta_hits3_at20: `0.096`
- delta_hits10_at20: `0.03`
- delta_avg_gold_rank: `-0.848`

## 4. Retrieval-stage gain vs soft
- delta_mrr_at20: `0.0`
- delta_hits1_at20: `0.0`
- delta_hits3_at20: `0.0`
- delta_hits10_at20: `0.0`
- delta_avg_gold_rank: `0.0`

## 5. Ontology vs backbone
- delta_mrr_at20: `-0.06142308`
- delta_hits1_at20: `-0.022`
- delta_hits3_at20: `-0.068`
- delta_hits10_at20: `-0.182`
- delta_avg_gold_rank: `3.188`

## 6. Recommended main-paper cases
### backbone_to_retrieval_improved
- row=348 | query=`lymphosarcoma` | gold=`Vincristine` | backbone_rank=16 | soft_rank=2 | retrieval_rank=2
- row=56 | query=`lymphoma` | gold=`Vincristine` | backbone_rank=17 | soft_rank=3 | retrieval_rank=3
- row=381 | query=`rheumatoid arthritis` | gold=`Methotrexate` | backbone_rank=19 | soft_rank=8 | retrieval_rank=8

### ontology_failure_retrieval_success
- row=22 | query=`seborrheic dermatitis` | gold=`Cortisone acetate` | backbone_rank=1 | soft_rank=1 | retrieval_rank=1
- row=41 | query=`acute lymphoblastic leukemia (disease)` | gold=`Dexamethasone` | backbone_rank=2 | soft_rank=1 | retrieval_rank=1
- row=48 | query=`acquired angioedema` | gold=`Betamethasone` | backbone_rank=5 | soft_rank=1 | retrieval_rank=1

### same_rank_cleaner_graph
- row=282 | query=`chronic tubotympanic suppurative otitis media` | gold=`Norfloxacin` | backbone_rank=4 | soft_rank=4 | retrieval_rank=4
- row=187 | query=`cholera` | gold=`Fusidic acid` | backbone_rank=1 | soft_rank=1 | retrieval_rank=1
- row=68 | query=`botulism` | gold=`Ofloxacin` | backbone_rank=12 | soft_rank=10 | retrieval_rank=10

## 7. Decision note
Locked test confirms the valid-side narrative under reviewer-safe protocol. Keep soft_support_fuzzy_retrieval_main as the paper-facing main row.

## 8. Day-7 conclusion
Week 19 is now closed. Locked test artifacts, eval-ready package, main table, ablation, and shortlist are all assembled into one paper-facing decision package.
