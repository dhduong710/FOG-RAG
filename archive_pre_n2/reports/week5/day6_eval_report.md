# Week 5 - Day 6 Eval Report

## Run identity
- model: meta-llama/Llama-3.2-3B
- checkpoint: results/week5/backbone_llama32_3b_rgcn/checkpoint-final
- dataset: dataset/setting_a/08_backbone_ready
- split: valid
- embedding: dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt

## Metrics
- MRR: 1.0
- Hits@1: 1.0
- Hits@3: 1.0
- Hits@10: 1.0

## Artifacts
- prediction_json: results/week5/backbone_llama32_3b_rgcn/eval_valid_prediction.json
- metrics_json: results/week5/backbone_llama32_3b_rgcn/eval_valid_metrics.json
- error_case_md: results/week5/backbone_llama32_3b_rgcn/eval_valid_error_cases.md
- eval_log: results/week5/backbone_llama32_3b_rgcn/logs/eval_valid_20260405_172606.log

## 5 good cases
- summarize from eval_valid_error_cases.md

## 5 bad cases
- summarize from eval_valid_error_cases.md

## Preliminary error groups
1. candidate quality still weak
2. subgraph poor or noisy
3. graph signal not helping enough
4. LLM reranking still weak

## Judgment
- READY_FOR_DAY7: yes / no

## What worked
- full Setting-A backbone-ready package built successfully
- first real R-GCN embedding source exported successfully
- first server dry run passed with finite loss
- first full backbone training run completed successfully
- first valid eval run completed successfully

## What is still provisional
- candidate source is still mock-like
- valid metrics are saturated and not scientifically interpretable
- current backbone eval mainly validates pipeline correctness, not model quality
- real coarse ranker / real candidate ranking is still missing

## Decision
Conditional go to next step