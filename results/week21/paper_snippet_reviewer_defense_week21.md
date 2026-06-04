# Paper Snippet — Reviewer Defense

## Concern

ComplEx has much higher Gold@20 than FOG-RAG main. Does this weaken the FOG-RAG claim?

## Response

A reviewer may note that ComplEx achieves substantially higher Gold@20 than FOG-RAG main. We agree and report this explicitly. Our conclusion is not that FOG-RAG has better candidate coverage than ComplEx; it does not. Instead, under the frozen reviewer-safe top-20 protocol, FOG-RAG main achieves slightly higher locked-test MRR@20 because it places the gold drug earlier when it is present, as reflected by H@1=0.072 and H@3=0.166, compared with ComplEx H@1=0.032 and H@3=0.118. The result should therefore be interpreted as evidence that coverage and ordering are complementary. A stronger upstream generator such as ComplEx is a promising future candidate source for FOG-RAG, while the current contribution focuses on soft evidence modeling and confidence-aware retrieval within the DrKGC-compatible pipeline.

## Claims to avoid

- Do not claim FOG-RAG universally outperforms all structure baselines.
- Do not claim FOG-RAG has better Gold@20 than ComplEx.
- Do not claim fuzzy retrieval improves ranking beyond soft support.
- Do not hide the fact that ComplEx is better on validation MRR@20.
- Do not call the metric a classical full-ranking filtered KGC metric.

## Safe claims

- FOG-RAG main achieves the highest locked-test reviewer-safe MRR@20.
- FOG-RAG substantially improves the DrKGC-compatible raw backbone.
- ComplEx demonstrates that stronger pure structure retrievers can provide higher coverage.
- Coverage and ranking quality are complementary.
- FOG-RAG's retrieval module improves graph compactness and evidence quality while preserving the ranking gain.
