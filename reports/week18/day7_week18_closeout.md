# Week 18 Closeout

## Final decision
- **GO_TO_BUILD_TEST_ARTIFACTS**
- official_locked_test_now: `False`
- week19_recommendation: `build missing soft_support_raw_test and retrieval_main_test artifacts, then run official locked test`

## Row lock summary
- **reference_row**: `backbone_raw`
- **negative_control_row**: `ontology_raw`
- **candidate_stage_main_intermediate**: `soft_support_raw`
- **main_row_after_week18**: `soft_support_fuzzy_retrieval_main`
- **appendix_row**: `soft_support_fuzzy_encoder_probe_v0`

## Week-18 status
- **row_lock_completed**: `True`
- **reviewer_safe_valid_main_table_completed**: `True`
- **reviewer_safe_valid_ablation_completed**: `True`
- **case_shortlist_completed**: `True`
- **test_readiness_checked**: `True`
- **appendix_positioning_completed**: `True`

## Core findings
- **backbone_raw_mrr_at20**: `0.053803`
- **ontology_raw_mrr_at20**: `0.003917`
- **soft_support_raw_mrr_at20**: `0.097644`
- **retrieval_main_mrr_at20**: `0.097644`
- **retrieval_main_hits1_at20**: `0.056`
- **retrieval_main_avg_gold_rank**: `17.676`
- **retrieval_main_avg_subgraph_size**: `32.556`
- **retrieval_main_avg_direct_shortcut_path_rate**: `0.105536`
- **retrieval_main_avg_contradiction_path_rate**: `0.006804`
- **retrieval_main_candidate_coverage_preserved_rate**: `1.0`
- **encoder_probe_mrr_at20**: `0.053707`
- **encoder_probe_avg_bridge_norm**: `0.0135`

## Test readiness summary
- decision: `PARTIAL_READY`
- note: Missing required test sources: ['soft_support_raw_test', 'retrieval_main_test']
- note: Main locked-test sources still missing: ['soft_support_raw_test', 'retrieval_main_test']
- missing_required_sources: `['soft_support_raw_test', 'retrieval_main_test']`

## Paper narrative lock
- Use reviewer-safe metrics with RR@20 = 1/rank if rank <= 20 else 0.
- Treat gold_rank = 21 only as a descriptive sentinel for out-of-top20 cases.
- Present backbone_raw as the reference row.
- Present ontology_raw as a brittle negative control.
- Present soft_support_raw as the candidate-stage main intermediate row.
- Present soft_support_fuzzy_retrieval_main as the strongest current frozen row.
- Present soft_support_fuzzy_encoder_probe_v0 as a supporting deferred appendix direction.

## Successes of week 18
- The retrieval main row was locked as the main row after week 17.
- A reviewer-safe valid main table was built.
- A reviewer-safe ablation export was built.
- Ontology was correctly repositioned as a negative control under the reviewer-safe metric policy.
- A case-study shortlist was built for main-paper interpretation and appendix positioning.

## Remaining limits
- Official locked test should not be run yet because the main test artifacts for soft_support_raw and retrieval_main are still missing.
- Encoder remains deferred and should not be reopened as the default main path.

## Paper-ready paragraph
By the end of week 18, we locked soft_support_fuzzy_retrieval_main as the strongest current frozen row of Novelty 2 under a reviewer-safe valid protocol. The valid main table now clearly separates backbone_raw as the reference row, ontology_raw as a brittle negative control, soft_support_raw as the candidate-stage main intermediate row, and retrieval_main as the final main row at the current stage. The encoder probe remains a supporting deferred direction rather than a promoted stage. However, official locked test is deferred until the missing main test-side artifacts are built.
