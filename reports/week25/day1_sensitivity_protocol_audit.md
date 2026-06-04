# Week 25 Day 1  Sensitivity Protocol Audit

- Decision: **WEEK25_SENSITIVITY_PROTOCOL_READY**
- Created at: `2026-05-02T03:39:45`
- Primary dataset: **PrimeKG Setting A**
- Primary model: **Llama-3.2-3B**
- Main row: **retrieval_main**
- Frozen decoding config: **cfg01_mnt16_rp100_ng0**

## Frozen decoding

```json
{
  "config_name": "cfg01_mnt16_rp100_ng0",
  "selected_on": "valid_only",
  "max_new_tokens": 16,
  "min_new_tokens": 1,
  "do_sample": false,
  "num_beams": 1,
  "temperature": 1.0,
  "repetition_penalty": 1.0,
  "no_repeat_ngram_size": 0
}
```

## Week 24 reference table

| Row | Gold@20 | Cand MRR@20 | E2E MRR@20 | H@3 | H@10 | Pred-in-cand | Invalid | Top1-copy | Avg graph |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| backbone_raw | 0.24 | 0.064563 | 0.047636 | 0.048 | 0.178 | 0.98 | 0.02 | 0.038 | 59.93 |
| soft_support_raw | 0.24 | 0.125326 | 0.074676 | 0.132 | 0.218 | 0.98 | 0.02 | 0.008 | 59.93 |
| retrieval_main | 0.24 | 0.125326 | 0.074687 | 0.132 | 0.218 | 0.998 | 0.002 | 0.01 | 32.34 |

## E2E-ready row audit

| Row | Split | Exists | Rows | Avg cand len | Avg subgraph | Missing field rows | Bad cand len rows | Bad subgraph rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| backbone_raw | train | True | 8388 | 20.0 | 73.633405 | 0 | 0 | 0 |
| backbone_raw | valid | True | 500 | 20.0 | 60.45 | 0 | 0 | 0 |
| backbone_raw | test | True | 500 | 20.0 | 59.932 | 0 | 0 | 0 |
| soft_support_raw | train | True | 8388 | 20.0 | 73.633405 | 0 | 0 | 0 |
| soft_support_raw | valid | True | 500 | 20.0 | 60.45 | 0 | 0 | 0 |
| soft_support_raw | test | True | 500 | 20.0 | 59.932 | 0 | 0 | 0 |
| retrieval_main | train | True | 8388 | 20.0 | 73.633405 | 0 | 0 | 0 |
| retrieval_main | valid | True | 500 | 20.0 | 32.556 | 0 | 0 | 0 |
| retrieval_main | test | True | 500 | 20.0 | 32.34 | 0 | 0 | 0 |

## Sample questions

| Row | Split | Sample question | Sample output |
| --- | --- | --- | --- |
| backbone_raw | valid | What drug is indicated for leukemia, lymphocytic, susceptibility to? | Cortisone acetate |
| backbone_raw | test | What drug is indicated for lung abscess (disease)? | Ticarcillin |
| soft_support_raw | valid | What drug is indicated for leukemia, lymphocytic, susceptibility to? | Cortisone acetate |
| soft_support_raw | test | What drug is indicated for lung abscess (disease)? | Ticarcillin |
| retrieval_main | valid | What drug is indicated for leukemia, lymphocytic, susceptibility to? | Cortisone acetate |
| retrieval_main | test | What drug is indicated for lung abscess (disease)? | Ticarcillin |

## Checkpoint audit

- Selected checkpoint: `results/week20/e2e_primary_checkpoint`

| Path | Exists | Adapter config | Adapter weights | Graph model | Valid |
| --- | --- | --- | --- | --- | --- |
| results/week20/e2e_primary_checkpoint/checkpoint-final | False | False | False | False | False |
| results/week20/e2e_primary_checkpoint | True | True | True | True | True |
| results/week24/e2e_primary_checkpoint/checkpoint-final | False | False | False | False | False |
| results/week24/e2e_primary_checkpoint | False | False | False | False | False |

## Week 24 artifact audit

| Name | Path | Exists | Kind |
| --- | --- | --- | --- |
| primekg_e2e_protocol_freeze | results/week24/primekg_e2e_protocol_freeze.json | True | file |
| week24_go_decision | results/week24/week24_go_decision.json | True | file |
| frozen_decode_test_dir | results/week24/frozen_decode_test | True | dir |
| model_compare_dir | results/week24/model_compare | True | dir |
| diagnostics_dir | results/week24/diagnostics | True | dir |

## Sensitivity groups frozen for Week 25

### rule_sensitivity
- Role: appendix sensitivity / negative-control analysis
- Main row: `retrieval_main`
- Variants: main_rules, no_rules, random_rules

### template_sensitivity
- Role: appendix prompt wording sensitivity
- Main row: `retrieval_main`
- Variants: T0_canonical, T1_treatment, T2_medication, T3_association_neutral

### small_noise_robustness
- Role: appendix robustness under small perturbations
- Main row: `retrieval_main`
- Variants: N0_no_noise, N1_support_score_noise_seed1, N2_support_score_noise_seed2, N3_support_score_noise_seed3, N4_subgraph_edge_dropout_5_seed1_optional, N5_subgraph_edge_dropout_5_seed2_optional, N6_subgraph_edge_dropout_5_seed3_optional

## Fatal errors

- None

## Warnings

- None

## Final rule

Week 25 sensitivity outputs are appendix/supporting evidence only. They must not replace the Week 24 locked main result, and no test-based tuning is allowed.
