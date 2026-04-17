# Baselines for Setting A

## 1. Structure-only baselines
We include four structure-only baselines in the first clean comparison table:
- **R-GCN**: currently a provisional row derived from the existing week7 ranker_v2 score dump under the clean structure-only evaluator.
- **HRGAT**: a minimal relation-aware graph attention baseline evaluated under the same valid-first protocol.
- **ComplEx**: the preferred third baseline and currently the strongest structure-only row in table v0.
- **TransE**: a bonus fourth baseline providing a simple translational reference.

## 2. Candidate-aware reranker reference rows
We additionally keep three reranker-based reference rows:
- **week7 3B**: the main backbone reference package.
- **week7 8B**: a capacity-check reference row.
- **week8 posthoc 3B**: supporting retrieval-side analysis only, not the main backbone package.

## 3. Current interpretation
At the current stage, ComplEx provides the strongest structure-only result, while HRGAT clearly improves over the provisional R-GCN row. The candidate-aware reranker rows remain useful references for the main backbone path, but are intentionally kept separate from the structure-only baseline section.
