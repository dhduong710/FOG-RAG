# Week 5 - Day 5 Train Report

## Run identity
- model: meta-llama/Llama-3.2-3B
- dataset: dataset/setting_a/08_backbone_ready
- embedding: dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt
- output_dir: results/week5/backbone_llama32_3b_rgcn

## Config
- source_max_len: 768
- target_max_len: 64
- per_device_train_batch_size: 1
- gradient_accumulation_steps: 8
- learning_rate: 2e-4
- LoRA: 32 / 32 / 0.1
- quantization: 4-bit

## What happened
- train completed or not: completed
- checkpoint-final saved or not: saved
- OOM / NaN / crash:
- log path: results/week5/backbone_llama32_3b_rgcn/logs/train_20260405_160037.log

## Quick observations
- first visible loss: 0.4873
- last visible loss: 0.004715721041406182
- approximate runtime: 0:14:39.50
- major warnings: dataloader: 32 workers, bitsandbytes < 0.41.1

## Judgment
- READY_FOR_DAY6: yes