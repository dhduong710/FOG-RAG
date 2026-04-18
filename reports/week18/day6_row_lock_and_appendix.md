# Week 18 Day 6 — Row Lock and Appendix Positioning

## Main positioning
- Reference row: `backbone_raw`
- Negative control: `ontology_raw`
- Candidate-stage intermediate: `soft_support_raw`
- Main row after week 17: `soft_support_fuzzy_retrieval_main`

## Appendix positioning
- Appendix row: `soft_support_fuzzy_encoder_probe_v0`
- Decision: `deferred_not_promoted`

## Paper narrative lock
- The paper should present backbone_raw as the reference row.
- The paper should present ontology_raw as a negative control rather than a competitive row.
- The paper should present soft_support_raw as the candidate-stage main intermediate row.
- The paper should present soft_support_fuzzy_retrieval_main as the strongest current frozen row of Novelty 2.
- The paper should present soft_support_fuzzy_encoder_probe_v0 as a supporting deferred direction in the appendix, not as a promoted main stage.

## Current limitations
- The encoder probe does not justify promotion to a main stage.
- The project is not yet ready for official locked test because test-side soft_support_raw and retrieval_main artifacts are still missing.

## Next-step recommendation
- test_readiness_status: `PARTIAL_READY`
- recommended_direction: `keep retrieval main as the main row, keep encoder as appendix/supporting only, and build the missing main test artifacts before official locked test`

## Paper-ready paragraph
After freezing the candidate-stage and retrieval-stage rows, we retained soft_support_fuzzy_retrieval_main as the strongest current row of Novelty 2 under the raw/no-injection valid protocol. We also conducted a controlled encoder-readiness probe, but the probe did not provide sufficient gain over the retrieval main row. Therefore, we position the encoder probe as a supporting deferred direction rather than promoting it to a main stage.
