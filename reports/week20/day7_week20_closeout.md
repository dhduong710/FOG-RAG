# Day 7 — Week 20 closeout

- status: **GO_FULL_PAPER_WRITING_WITH_EXPERIMENT_BACKLOG**
- main_row: **`soft_support_fuzzy_retrieval_main`**

## 1. Closeout checks
- e2e_main_table_built: `True`
- e2e_ablation_built: `True`
- paper_tables_built: `True`
- paper_figures_manifest_built: `True`
- paper_case_pack_built: `True`
- main_row_is_retrieval: `True`
- soft_improves_backbone_e2e: `True`
- retrieval_preserves_soft_e2e: `True`
- retrieval_smaller_subgraph: `True`

## 2. Paper-facing decision
- main_row: `soft_support_fuzzy_retrieval_main`
- reference_row: `backbone_raw`
- candidate_stage_intermediate: `soft_support_raw`
- encoder_status: `appendix_only`
- main_claim: `Soft support provides the main ranking gain over backbone; confidence-aware retrieval preserves candidate/E2E performance while substantially reducing evidence subgraph size.`
- known_limitation: `E2E Hits@1 remains weak because the frozen LLM often generates a plausible candidate instead of the exact gold string even when gold is ranked first.`

## 3. Recommended next weeks
### Priority 1 — Week21_baseline_rerun_and_fair_comparison
- decision: `DO_NEXT`
- Rerun structure baselines on the exact same drug-only head-prediction task.
- Use reviewer-safe MRR@20 and Hits@1/3/10@20.
- Check whether any baseline beats the current candidate ceiling.
- If a baseline is stronger, consider an appendix branch using that baseline as upstream candidate source.

### Priority 2 — Week22_second_dataset_feasibility
- decision: `DO_AFTER_BASELINES`
- Check PharmKG first for a drug-disease indication/treatment-style relation.
- Verify entity types, relation names, candidate universe, split policy, and no-leak rules.
- Only build full downstream pipeline if the task is clean and comparable.

### Priority 3 — Week23_optional_dataset2_minimal_pipeline
- decision: `CONDITIONAL`
- If PharmKG/DRKG feasibility passes, run a minimal no-injection pipeline.
- Do not add encoder or extra novelty.
- Report as external validation, not replacement of PrimeKG main result.

### Priority 4 — Week24_optional_robustness
- decision: `OPTIONAL`
- Rule sensitivity: hard-coded rules vs no-rules vs random-rule negative control.
- Question-template sensitivity for indication prompts.
- Small noise robustness if time permits.
- One extra LLM only if adapter/fine-tuning budget is available.

## 4. Final note
Week 20 closes the main experimental package. The next best step is not to change the mainline, but to run fair baselines under the same reviewer-safe protocol before expanding to another dataset.

## 5. Day-7 conclusion
Week 20 is closed. The main PrimeKG/FOG-RAG result package is paper-ready, with a clear experiment backlog for baseline fairness, second-dataset feasibility, and optional robustness.
