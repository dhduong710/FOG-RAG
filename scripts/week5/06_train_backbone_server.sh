#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="${HOME}/Documents/2026-dhd/FOG-RAG"
cd "${REPO_DIR}"

# activate venv used in day-4 dry run
source .venv/bin/activate

export TOKENIZERS_PARALLELISM=false
export WANDB_DISABLED=true
export HF_HOME="${HOME}/Documents/2026-dhd/.cache/huggingface"
export TRANSFORMERS_CACHE="${HF_HOME}"

OUT_DIR="results/week5/backbone_llama32_3b_rgcn"
LOG_DIR="${OUT_DIR}/logs"
mkdir -p "${LOG_DIR}"

STAMP=$(date +"%Y%m%d_%H%M%S")
LOG_PATH="${LOG_DIR}/train_${STAMP}.log"
SNAPSHOT_PATH="${OUT_DIR}/config_snapshot.json"

echo "Repo      : ${REPO_DIR}"
echo "Output dir: ${OUT_DIR}"
echo "Log path  : ${LOG_PATH}"
echo "Start time: $(date)"

python scripts/week5/06a_launch_main_adaptive.py \
  --model_name_or_path meta-llama/Llama-3.2-3B \
  --dataset_path dataset/setting_a/08_backbone_ready \
  --kge_embedding_path dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt \
  --output_dir "${OUT_DIR}" \
  --run_name week5_llama32_3b_rgcn \
  --source_max_len 768 \
  --target_max_len 64 \
  --per_device_train_batch_size 1 \
  --gradient_accumulation_steps 8 \
  --learning_rate 2e-4 \
  --num_train_epochs 1 \
  --lora_r 32 \
  --lora_alpha 32 \
  --lora_dropout 0.1 \
  --bits 4 \
  --double_quant \
  --seed 2025 \
  --save_steps 200 \
  --logging_steps 10 \
  --save_total_limit 2 \
  --gnn_hidden_dim 128 \
  --gnn_num_hidden_layers 1 \
  --adapter_size 1024 \
  --gradient_checkpointing \
  --prefer_bf16 \
  --snapshot_path "${SNAPSHOT_PATH}" \
  2>&1 | tee "${LOG_PATH}"

echo "End time: $(date)"
echo "Train log saved to: ${LOG_PATH}"