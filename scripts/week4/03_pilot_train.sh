#!/usr/bin/env bash
set -euo pipefail

export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

DATASET_PATH="dataset/setting_a/07_pilot_ready"
KGE_PATH="dataset/setting_a/07_pilot_ready/mock_entity_embeddings.pt"
MODEL_NAME="TinyLlama/TinyLlama-1.1B-Chat-v1.0"
OUTPUT_DIR="results/week4/pilot_train_tinyllama_mock"
LOG_DIR="runs/week4_pilot"
LOG_PATH="${LOG_DIR}/day3_pilot_train.log"

mkdir -p "${OUTPUT_DIR}"
mkdir -p "${LOG_DIR}"

echo "============================================================"
echo "Week 4 Day 3 Pilot Train"
echo "DATASET_PATH=${DATASET_PATH}"
echo "KGE_PATH=${KGE_PATH}"
echo "MODEL_NAME=${MODEL_NAME}"
echo "OUTPUT_DIR=${OUTPUT_DIR}"
echo "LOG_PATH=${LOG_PATH}"
echo "============================================================"

python main.py \
  --dataset_path "${DATASET_PATH}" \
  --kge_embedding_path "${KGE_PATH}" \
  --model_name_or_path "${MODEL_NAME}" \
  --model_type llama \
  --use_quant True \
  --bits 4 \
  --bf16 \
  --output_dir "${OUTPUT_DIR}" \
  --seed 2025 \
  --source_max_len 768 \
  --target_max_len 32 \
  --num_train_epochs 1 \
  --max_steps 20 \
  --per_device_train_batch_size 1 \
  --gradient_accumulation_steps 8 \
  --learning_rate 2e-4 \
  --lr_scheduler_type constant \
  --warmup_ratio 0.0 \
  --lora_r 32 \
  --lora_alpha 32 \
  --lora_dropout 0.1 \
  --dataloader_num_workers 4 \
  --logging_strategy steps \
  --logging_steps 1 \
  --save_strategy steps \
  --save_steps 10 \
  --save_total_limit 2 \
  --evaluation_strategy no \
  --report_to none \
  --remove_unused_columns False \
  --overwrite_output_dir \
  2>&1 | tee "${LOG_PATH}"

echo
echo "Pilot training finished."
echo "Check output directory: ${OUTPUT_DIR}"
echo "Check log file: ${LOG_PATH}"