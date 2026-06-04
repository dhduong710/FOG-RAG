# Paper Snippet — Results Section

## Baseline comparison paragraph

Table~\ref{tab:week21-baseline-main} reports the locked-test reviewer-safe comparison between six structure-only candidate generators and the DrKGC-compatible FOG-RAG rows. Among the structure baselines, ComplEx is the strongest candidate generator, reaching Gold@20 of 0.574 and MRR@20 of 0.124731. However, the selected FOG-RAG main row obtains the highest locked-test MRR@20, 0.125326, slightly above ComplEx by 0.000595. This result is notable because FOG-RAG main has substantially lower Gold@20 (0.240) than ComplEx, but achieves better early-rank placement with Hits@1 of 0.072 versus 0.032, and Hits@3 of 0.166 versus 0.118. Compared with the DrKGC-style raw backbone, FOG-RAG improves MRR@20 by 0.060763, Hits@1 by 0.048, and Hits@3 by 0.096.

## Graph-efficiency paragraph

The ranking gain is driven by the soft-support stage, while the confidence-aware retrieval stage preserves the same candidate ordering and improves the graph package. On the locked test set, retrieval main reduces the average retrieved subgraph size from 59.93 to 32.34 triples, a reduction of 27.59 triples per query, while preserving candidate coverage. Thus, retrieval main should be interpreted as an evidence-efficiency and interpretability improvement rather than an additional candidate-ranking improvement over soft support.
