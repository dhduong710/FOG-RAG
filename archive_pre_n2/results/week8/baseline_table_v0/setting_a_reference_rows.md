# Setting A Candidate-aware Reranker Reference Rows

These rows are supporting references and should not be mixed directly with structure-only baselines without explicit protocol notes.

| Method | Protocol | Valid MRR | Hits@1 | Hits@3 | Hits@10 | Notes |
|---|---|---:|---:|---:|---:|---|
| week7 3B | candidate-aware reranker reference | 0.42424878 | 0.368 | 0.39399999 | 0.50999999 | Candidate-aware reranker reference row; main backbone reference package. |
| week7 8B | candidate-aware reranker reference | 0.43187144 | 0.37599999 | 0.40200001 | 0.51800001 | Candidate-aware reranker capacity check; slight gain over week7 3B. |
| week8 posthoc 3B | candidate-aware reranker reference | 0.31621575 | 0.25400001 | 0.28200001 | 0.384 | Supporting retrieval-side analysis only; not the main backbone package. |

## Important note
- week7 3B remains the main backbone reference.
- week8 posthoc 3B remains supporting retrieval-side analysis only.
