# Paper Snippet — Discussion Section

## Interpretation

The baseline comparison reveals an important distinction between candidate coverage and rank quality. ComplEx retrieves the gold drug in the top-20 list much more often than FOG-RAG main (0.574 vs. 0.240 Gold@20), yet FOG-RAG main slightly outperforms ComplEx on locked-test MRR@20. This indicates that simply increasing top-20 coverage is insufficient when the downstream graph-augmented LLM pipeline relies on a short candidate list: the position of the gold entity within the list also matters. FOG-RAG improves the DrKGC-compatible raw source by using soft support signals to move evidence-supported drugs earlier in the candidate list, while the retrieval module makes the graph evidence smaller and less shortcut-heavy. We therefore position FOG-RAG not as a replacement for all structure-only retrievers, but as an evidence-aware extension of the DrKGC-style graph-augmented LLM pipeline.

## Limitation / future work

The comparison also exposes a limitation of the current FOG-RAG implementation: its DrKGC-compatible raw candidate source has lower Gold@20 than the strongest pure structure-only generator. This limits the maximum achievable recall of the downstream LLM prompt. Future work should evaluate a hybrid system in which a stronger upstream candidate generator, such as ComplEx, is combined with the proposed soft-support and confidence-aware retrieval modules.
