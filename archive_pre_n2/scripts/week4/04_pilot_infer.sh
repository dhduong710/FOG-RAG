#!/usr/bin/env bash
set -euo pipefail

export TOKENIZERS_PARALLELISM=false

DATASET_PATH="dataset/setting_a/07_pilot_ready"
MODEL_NAME="TinyLlama/TinyLlama-1.1B-Chat-v1.0"
CHECKPOINT_DIR="results/week4/pilot_train_tinyllama_mock/checkpoint-final"
KGE_PATH="dataset/setting_a/07_pilot_ready/mock_entity_embeddings.pt"
OUTPUT_DIR="results/week4/pilot_infer_tinyllama_mock"
LOG_DIR="runs/week4_pilot"
LOG_PATH="${LOG_DIR}/day4_pilot_infer.log"

mkdir -p "${OUTPUT_DIR}"
mkdir -p "${LOG_DIR}"

echo "============================================================"
echo "Week 4 Day 4 Pilot Inference"
echo "DATASET_PATH=${DATASET_PATH}"
echo "MODEL_NAME=${MODEL_NAME}"
echo "CHECKPOINT_DIR=${CHECKPOINT_DIR}"
echo "KGE_PATH=${KGE_PATH}"
echo "OUTPUT_DIR=${OUTPUT_DIR}"
echo "LOG_PATH=${LOG_PATH}"
echo "============================================================"

PYTHONPATH=. python scripts/week4/04_pilot_infer.py \
  --dataset_path "${DATASET_PATH}" \
  --model_name_or_path "${MODEL_NAME}" \
  --checkpoint_dir "${CHECKPOINT_DIR}" \
  --kge_embedding_path "${KGE_PATH}" \
  --output_dir "${OUTPUT_DIR}" \
  --source_max_len 768 \
  --target_max_len 32 \
  --seed 2025 \
  --max_new_tokens 16 \
  2>&1 | tee "${LOG_PATH}"

echo
echo "Pilot inference finished."
echo "Check output directory: ${OUTPUT_DIR}"
echo "Check log file: ${LOG_PATH}"