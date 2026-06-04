# Week 17 Day 6 — Freeze or Defer

## Decision
- **DEFER_ENCODER**
- Week-18 recommendation: `do_not_open_full_encoder_stage`

## Main row status
- **keep_retrieval_main_as_current_best_row**: `True`
- **promote_encoder_probe_to_main_row**: `False`
- **treat_probe_as_supporting_readiness_result**: `True`

## Negative reasons
- MRR-like drops from 0.135644 to 0.091707.
- Hits@1-like drops from 0.056 to 0.012.
- Average gold rank worsens from 17.676 to 17.98.
- Worsened cases (70) exceed improved cases (8).
- Average probe-minus-retrieval rank delta is positive (0.304).
- Average bridge_norm is too low (0.0135), suggesting sparse bridge signal.
- Anchor caution cases are high (266).

## Positive signals
- Probe improves 8 cases over retrieval main.
- There are 294 same-rank cases with possibly better graph signal.

## Cautions
- Probe is not redundant with retrieval main (same_top1_rate=0.274).
- There may still be some graph-side value, but it is not enough to justify promotion.

## Next-step recommendations
- Keep soft_support_fuzzy_retrieval_main as the strongest frozen row.
- Do not promote encoder probe v0 to a main row.
- Use week 17 as evidence that encoder readiness was checked in a controlled way.
- If encoder is revisited later, redesign bridge signal first instead of opening full training immediately.
