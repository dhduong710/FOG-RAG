# Week 24 Day 5  PrimeKG Model Comparison Evaluation and Selection

## Decision

**PRIMEKG_E2E_MODEL_SELECTION_READY**

## Best model on test retrieval_main

```json
{
  "model_tag": "llama3_8b",
  "split": "test",
  "row_name": "retrieval_main",
  "prediction_path": "/home/anhlq/Documents/2026-dhd/FOG-RAG/results/week24/model_compare/llama3_8b/predictions/prediction_test_retrieval_main.json",
  "num_examples": 500,
  "gold_at20": 0.24,
  "candidate_mrr_at20": 0.12532618,
  "candidate_hits1_at20": 0.072,
  "candidate_hits3_at20": 0.166,
  "candidate_hits10_at20": 0.222,
  "candidate_rank21_count": 380,
  "reviewer_safe_e2e_mrr_at20": 0.12532618,
  "reviewer_safe_e2e_hits1_at20": 0.072,
  "reviewer_safe_e2e_hits3_at20": 0.166,
  "reviewer_safe_e2e_hits10_at20": 0.222,
  "e2e_rank21_count": 380,
  "exact_target_match_rate": 0.072,
  "pred_in_candidate_rate": 1.0,
  "invalid_prediction_rate": 0.0,
  "top1_copy_rate": 1.0,
  "candidate_list_fragment_rate": 0.0,
  "empty_prediction_rate": 0.0,
  "prediction_category_counts": {
    "top1_copy": 464,
    "exact_target": 36
  },
  "rr_rule": "1/adjusted_rank if adjusted_rank <= 20 else 0",
  "absent_gold_policy": "RR@20 = 0",
  "avg_subgraph_size": 32.34,
  "min_subgraph_size": 24,
  "max_subgraph_size": 51,
  "avg_candidate_coverage_preserved_rate": 1.0,
  "selected_source_variant_set": [
    "soft_support_fuzzy_retrieval_tight"
  ]
}
```

## Ranked test retrieval_main models

| Rank | Model | E2E MRR | H@1 | H@3 | H@10 | Pred-in-cand | Invalid | Top1-copy | List-frag |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | llama3_8b | 0.125326 | 0.072 | 0.166 | 0.222 | 1.000 | 0.000 | 1.000 | 0.000 |
| 2 | medllama3_8b | 0.125326 | 0.072 | 0.166 | 0.222 | 1.000 | 0.000 | 1.000 | 0.000 |
| 3 | llama3_2_3b | 0.074687 | 0.000 | 0.132 | 0.218 | 0.998 | 0.002 | 0.010 | 0.010 |

## Full model comparison table

| Model | Split | Row | Gold@20 | Cand MRR | E2E MRR | H@1 | H@3 | H@10 | Pred-in-cand | Invalid | Top1-copy | List-frag | Avg subgraph |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| llama3_2_3b | valid | backbone_raw | 0.202 | 0.053803 | 0.048118 | 0.012 | 0.048 | 0.150 | 0.974 | 0.026 | 0.022 | 0.024 | 60.450 |
| llama3_2_3b | valid | soft_support_raw | 0.202 | 0.097644 | 0.059944 | 0.002 | 0.102 | 0.172 | 0.964 | 0.036 | 0.002 | 0.012 | 60.450 |
| llama3_2_3b | valid | retrieval_main | 0.202 | 0.097644 | 0.058518 | 0.000 | 0.100 | 0.174 | 0.992 | 0.008 | 0.008 | 0.010 | 32.556 |
| llama3_2_3b | test | backbone_raw | 0.240 | 0.064563 | 0.047636 | 0.002 | 0.048 | 0.178 | 0.980 | 0.020 | 0.038 | 0.046 | 59.932 |
| llama3_2_3b | test | soft_support_raw | 0.240 | 0.125326 | 0.074676 | 0.000 | 0.132 | 0.218 | 0.980 | 0.020 | 0.008 | 0.010 | 59.932 |
| llama3_2_3b | test | retrieval_main | 0.240 | 0.125326 | 0.074687 | 0.000 | 0.132 | 0.218 | 0.998 | 0.002 | 0.010 | 0.010 | 32.340 |
| llama3_8b | valid | backbone_raw | 0.202 | 0.053803 | 0.053803 | 0.024 | 0.046 | 0.158 | 0.992 | 0.008 | 0.992 | 0.000 | 60.450 |
| llama3_8b | valid | soft_support_raw | 0.202 | 0.097644 | 0.097644 | 0.056 | 0.134 | 0.182 | 0.992 | 0.008 | 0.992 | 0.008 | 60.450 |
| llama3_8b | valid | retrieval_main | 0.202 | 0.097644 | 0.097644 | 0.056 | 0.134 | 0.182 | 1.000 | 0.000 | 1.000 | 0.008 | 32.556 |
| llama3_8b | test | backbone_raw | 0.240 | 0.064563 | 0.064563 | 0.024 | 0.070 | 0.192 | 0.984 | 0.016 | 0.984 | 0.000 | 59.932 |
| llama3_8b | test | soft_support_raw | 0.240 | 0.125326 | 0.125326 | 0.072 | 0.166 | 0.222 | 0.984 | 0.016 | 0.984 | 0.000 | 59.932 |
| llama3_8b | test | retrieval_main | 0.240 | 0.125326 | 0.125326 | 0.072 | 0.166 | 0.222 | 1.000 | 0.000 | 1.000 | 0.000 | 32.340 |
| medllama3_8b | valid | backbone_raw | 0.202 | 0.053803 | 0.053803 | 0.024 | 0.046 | 0.158 | 0.992 | 0.008 | 0.992 | 0.000 | 60.450 |
| medllama3_8b | valid | soft_support_raw | 0.202 | 0.097644 | 0.097644 | 0.056 | 0.134 | 0.182 | 0.992 | 0.008 | 0.992 | 0.008 | 60.450 |
| medllama3_8b | valid | retrieval_main | 0.202 | 0.097644 | 0.097644 | 0.056 | 0.134 | 0.182 | 1.000 | 0.000 | 1.000 | 0.008 | 32.556 |
| medllama3_8b | test | backbone_raw | 0.240 | 0.064563 | 0.064563 | 0.024 | 0.070 | 0.192 | 0.986 | 0.014 | 0.986 | 0.000 | 59.932 |
| medllama3_8b | test | soft_support_raw | 0.240 | 0.125326 | 0.125326 | 0.072 | 0.166 | 0.222 | 0.986 | 0.014 | 0.986 | 0.000 | 59.932 |
| medllama3_8b | test | retrieval_main | 0.240 | 0.125326 | 0.125326 | 0.072 | 0.166 | 0.222 | 1.000 | 0.000 | 1.000 | 0.000 | 32.340 |

## Test trend checks by model

```json
{
  "llama3_2_3b": {
    "soft_improves_backbone_e2e": true,
    "retrieval_preserves_or_improves_soft_e2e": true,
    "retrieval_smaller_than_soft": true,
    "test_delta_retrieval_minus_backbone_e2e": 0.0270508,
    "test_delta_retrieval_minus_soft_e2e": 1.099e-05
  },
  "llama3_8b": {
    "soft_improves_backbone_e2e": true,
    "retrieval_preserves_or_improves_soft_e2e": true,
    "retrieval_smaller_than_soft": true,
    "test_delta_retrieval_minus_backbone_e2e": 0.06076335,
    "test_delta_retrieval_minus_soft_e2e": 0.0
  },
  "medllama3_8b": {
    "soft_improves_backbone_e2e": true,
    "retrieval_preserves_or_improves_soft_e2e": true,
    "retrieval_smaller_than_soft": true,
    "test_delta_retrieval_minus_backbone_e2e": 0.06076335,
    "test_delta_retrieval_minus_soft_e2e": 0.0
  }
}
```

## Interpretation notes

- Candidate metrics are identical across models for the same row; model differences come from generation.
- `soft_support_raw` should improve over `backbone_raw`; `retrieval_main` should preserve soft-support ranking while using smaller subgraphs.
- High `top1_copy_rate` means the model often copies the first candidate rather than using graph-conditioned reasoning.
- Raw `infer.py` metrics remain audit-only; this report uses reviewer-safe recomputation from prediction rows.