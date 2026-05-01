# Week 24 Extension Day 6C  PharmKG Frozen Model Comparison

## Decision

**PHARMKG_FROZEN_MODEL_COMPARE_READY**

## Ranked test fuzzy_retrieval_main

| Rank | Model | E2E MRR | H@1 | H@3 | H@10 | Pred-in-cand | Invalid | Top1-copy | List-frag |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | llama3_2_3b | 0.020971 | 0.002 | 0.030 | 0.062 | 0.412 | 0.588 | 0.412 | 0.582 |
| 2 | llama3_8b | 0.020275 | 0.002 | 0.026 | 0.064 | 0.274 | 0.726 | 0.274 | 0.096 |
| 3 | medllama3_8b | 0.018583 | 0.000 | 0.024 | 0.060 | 0.022 | 0.978 | 0.022 | 0.598 |

## Full table

| Model | Split | Row | Gold@20 | Cand MRR | E2E MRR | H@1 | H@3 | H@10 | Pred-in-cand | Invalid | Top1-copy | List-frag | Avg graph |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| llama3_2_3b | valid | backbone_raw | 0.070 | 0.017846 | 0.015402 | 0.006 | 0.014 | 0.034 | 0.524 | 0.476 | 0.524 | 0.474 | 100.00 |
| llama3_2_3b | valid | soft_support_raw | 0.070 | 0.021308 | 0.017157 | 0.004 | 0.020 | 0.052 | 0.360 | 0.640 | 0.360 | 0.634 | 100.00 |
| llama3_2_3b | valid | fuzzy_retrieval_main | 0.070 | 0.021308 | 0.017184 | 0.004 | 0.020 | 0.052 | 0.376 | 0.624 | 0.376 | 0.618 | 55.00 |
| llama3_2_3b | test | backbone_raw | 0.092 | 0.020481 | 0.015575 | 0.000 | 0.018 | 0.044 | 0.504 | 0.496 | 0.504 | 0.490 | 100.00 |
| llama3_2_3b | test | soft_support_raw | 0.092 | 0.028159 | 0.020587 | 0.000 | 0.030 | 0.062 | 0.390 | 0.610 | 0.390 | 0.604 | 100.00 |
| llama3_2_3b | test | fuzzy_retrieval_main | 0.092 | 0.028159 | 0.020971 | 0.002 | 0.030 | 0.062 | 0.412 | 0.588 | 0.412 | 0.582 | 55.00 |
| llama3_8b | valid | backbone_raw | 0.070 | 0.017846 | 0.013930 | 0.004 | 0.014 | 0.034 | 0.494 | 0.506 | 0.494 | 0.020 | 100.00 |
| llama3_8b | valid | soft_support_raw | 0.070 | 0.021308 | 0.015342 | 0.002 | 0.020 | 0.050 | 0.254 | 0.746 | 0.254 | 0.084 | 100.00 |
| llama3_8b | valid | fuzzy_retrieval_main | 0.070 | 0.021308 | 0.015367 | 0.002 | 0.020 | 0.052 | 0.300 | 0.700 | 0.300 | 0.094 | 55.00 |
| llama3_8b | test | backbone_raw | 0.092 | 0.020481 | 0.016193 | 0.002 | 0.014 | 0.044 | 0.502 | 0.498 | 0.502 | 0.012 | 100.00 |
| llama3_8b | test | soft_support_raw | 0.092 | 0.028159 | 0.018970 | 0.000 | 0.026 | 0.064 | 0.266 | 0.734 | 0.266 | 0.088 | 100.00 |
| llama3_8b | test | fuzzy_retrieval_main | 0.092 | 0.028159 | 0.020275 | 0.002 | 0.026 | 0.064 | 0.274 | 0.726 | 0.274 | 0.096 | 55.00 |
| medllama3_8b | valid | backbone_raw | 0.070 | 0.017846 | 0.011300 | 0.000 | 0.014 | 0.034 | 0.000 | 1.000 | 0.000 | 0.710 | 100.00 |
| medllama3_8b | valid | soft_support_raw | 0.070 | 0.021308 | 0.013894 | 0.000 | 0.020 | 0.050 | 0.020 | 0.980 | 0.020 | 0.570 | 100.00 |
| medllama3_8b | valid | fuzzy_retrieval_main | 0.070 | 0.021308 | 0.013894 | 0.000 | 0.020 | 0.050 | 0.020 | 0.980 | 0.020 | 0.612 | 55.00 |
| medllama3_8b | test | backbone_raw | 0.092 | 0.020481 | 0.014034 | 0.000 | 0.014 | 0.044 | 0.000 | 1.000 | 0.000 | 0.716 | 100.00 |
| medllama3_8b | test | soft_support_raw | 0.092 | 0.028159 | 0.018583 | 0.000 | 0.024 | 0.060 | 0.022 | 0.978 | 0.022 | 0.560 | 100.00 |
| medllama3_8b | test | fuzzy_retrieval_main | 0.092 | 0.028159 | 0.018583 | 0.000 | 0.024 | 0.060 | 0.022 | 0.978 | 0.022 | 0.598 | 55.00 |

## Trend checks

```json
{
  "llama3_2_3b": {
    "soft_improves_backbone_e2e": true,
    "fuzzy_preserves_or_improves_soft_e2e": true,
    "fuzzy_smaller_than_soft": true,
    "delta_fuzzy_minus_backbone_e2e": 0.00539619,
    "delta_fuzzy_minus_soft_e2e": 0.0003842
  },
  "llama3_8b": {
    "soft_improves_backbone_e2e": true,
    "fuzzy_preserves_or_improves_soft_e2e": true,
    "fuzzy_smaller_than_soft": true,
    "delta_fuzzy_minus_backbone_e2e": 0.00408243,
    "delta_fuzzy_minus_soft_e2e": 0.00130556
  },
  "medllama3_8b": {
    "soft_improves_backbone_e2e": true,
    "fuzzy_preserves_or_improves_soft_e2e": true,
    "fuzzy_smaller_than_soft": true,
    "delta_fuzzy_minus_backbone_e2e": 0.00454935,
    "delta_fuzzy_minus_soft_e2e": 0.0
  }
}
```

## Result paragraph

On the PharmKG therapeutic-association proxy task, soft support improves the locked-test candidate MRR@20 from 0.020481 to 0.028159. In reviewer-safe E2E evaluation with Llama-3.2-3B, the backbone obtains MRR@20=0.015575, while soft support and fuzzy retrieval reach 0.020587 and 0.020971, respectively. Fuzzy retrieval preserves the ranking trend while reducing the evidence subgraph from 100.00 to 55.00 triples.

## Limitation paragraph

PharmKG remains a difficult secondary transfer benchmark. The top-20 candidate bottleneck is strong, and unconstrained generation frequently produces invalid or fragmentary outputs for the Llama-3.2-3B run. Therefore, PharmKG is reported as transfer evidence for the direction of FOG-RAG improvements, not as a full-universe PharmKG KGC superiority claim.
