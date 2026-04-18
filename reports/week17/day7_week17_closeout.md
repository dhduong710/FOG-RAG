# Week 17 Closeout

## Final decision
- **NO_GO_FOR_FULL_ENCODER_STAGE**
- Week-18 recommendation: `keep_retrieval_main_as_final_row_or_only_redesign_encoder_as_side_probe`
- Main row after week 17: `soft_support_fuzzy_retrieval_main`
- Promote encoder probe: `False`

## Week-17 status
- **readiness_check_completed**: `True`
- **encoder_input_package_built**: `True`
- **encoder_probe_built**: `True`
- **probe_compare_completed**: `True`
- **probe_case_review_completed**: `True`

## Core findings
- **retrieval_main_mrr_like**: `0.135644`
- **retrieval_main_hits1_like**: `0.056`
- **retrieval_main_avg_gold_rank**: `17.676`
- **encoder_probe_mrr_like**: `0.091707`
- **encoder_probe_hits1_like**: `0.012`
- **encoder_probe_avg_gold_rank**: `17.98`
- **encoder_probe_avg_bridge_norm**: `0.0135`
- **improved_vs_retrieval_main**: `8`
- **worsened_vs_retrieval_main**: `70`
- **avg_rank_delta_probe_minus_retrieval**: `0.304`
- **anchor_caution_cases**: `266`

## Successes of week 17
- Encoder readiness was checked in a controlled, valid-only setting.
- Encoder inputs were built cleanly from the frozen retrieval main row.
- A minimal fuzzy encoder probe v0 was successfully constructed and compared.
- The project avoided prematurely committing to a full encoder stage.

## Failures / limits of encoder probe
- Probe v0 underperforms retrieval main on ranking-like proxy metrics.
- Bridge signal is too sparse to support promotion of encoder stage now.
- Probe changes ordering in many cases without reliable gains.
- Anchor caution cases are too frequent.

## Paper narrative lock
- Candidate-stage freeze: soft_support_raw.
- Retrieval-stage freeze: soft_support_fuzzy_retrieval_main.
- Week 17 checks encoder readiness instead of jumping directly to full encoder training.
- Encoder probe v0 is reported as a controlled but not-yet-successful probe.
- Retrieval main remains the strongest frozen row after week 17.

## Next-step options
- Option A: keep retrieval main as the final N2 row and move toward locked evaluation / interpretation.
- Option B: revisit encoder only as an explicitly redesigned side experiment, not as the default week-18 main path.
