# Week 21 Day 6 — Interpretation and Paper Positioning

## Decision

**INTERPRETATION_ASSETS_READY_FOR_WEEK21_CLOSEOUT**

## Headline

FOG-RAG main slightly leads locked-test MRR@20 while ComplEx leads Gold@20.

## Key findings

- FOG-RAG main is the best locked-test MRR@20 row, slightly above ComplEx.
- ComplEx is the strongest structure-only candidate generator by Gold@20.
- FOG-RAG does not beat ComplEx on coverage; it beats ComplEx slightly on locked-test MRR@20.
- Soft support is responsible for ranking improvement.
- Retrieval main preserves the soft-support ranking and improves graph efficiency.
- The correct paper stance is balanced: FOG-RAG improves the DrKGC-compatible pipeline and remains competitive with strong structure baselines.

## Recommended claims

- FOG-RAG main achieves the highest locked-test reviewer-safe MRR@20.
- FOG-RAG substantially improves the DrKGC-compatible raw backbone.
- ComplEx demonstrates that stronger pure structure retrievers can provide higher coverage.
- Coverage and ranking quality are complementary.
- FOG-RAG's retrieval module improves graph compactness and evidence quality while preserving the ranking gain.

## Forbidden claims

- Do not claim FOG-RAG universally outperforms all structure baselines.
- Do not claim FOG-RAG has better Gold@20 than ComplEx.
- Do not claim fuzzy retrieval improves ranking beyond soft support.
- Do not hide the fact that ComplEx is better on validation MRR@20.
- Do not call the metric a classical full-ranking filtered KGC metric.

## Generated files

- `results/week21/baseline_interpretation_assets.json`
- `results/week21/paper_snippet_results_week21.md`
- `results/week21/paper_snippet_discussion_week21.md`
- `results/week21/paper_snippet_reviewer_defense_week21.md`
- `results/week21/paper_snippet_table_caption_week21.tex`
- `results/week21/week21_paper_positioning_summary.md`

## Next step

Day 7 should close out Week 21 by freezing the baseline table, paper positioning, and remaining open questions before moving to Dataset 2.
