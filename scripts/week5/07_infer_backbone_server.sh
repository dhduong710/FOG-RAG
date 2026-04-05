#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="${HOME}/Documents/2026-dhd/FOG-RAG"
cd "${REPO_DIR}"

source .venv/bin/activate

export TOKENIZERS_PARALLELISM=false
export HF_HOME="${HOME}/Documents/2026-dhd/.cache/huggingface"

OUT_DIR="results/week5/backbone_llama32_3b_rgcn"
LOG_DIR="${OUT_DIR}/logs"
mkdir -p "${LOG_DIR}"

STAMP=$(date +"%Y%m%d_%H%M%S")
LOG_PATH="${LOG_DIR}/eval_valid_${STAMP}.log"

echo "Repo      : ${REPO_DIR}"
echo "Output dir: ${OUT_DIR}"
echo "Log path  : ${LOG_PATH}"
echo "Start time: $(date)"

python scripts/week5/07_eval_backbone_server.py \
  --dataset_path dataset/setting_a/08_backbone_ready \
  --model_name_or_path meta-llama/Llama-3.2-3B \
  --checkpoint_dir results/week5/backbone_llama32_3b_rgcn/checkpoint-final \
  --kge_embedding_path dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt \
  --split valid \
  --output_dir "${OUT_DIR}" \
  --max_new_tokens 64 \
  --min_new_tokens 1 \
  --num_beams 1 \
  --temperature 1.0 \
  --top_k 50 \
  2>&1 | tee "${LOG_PATH}"

python scripts/week5/08_collect_error_cases.py \
  --prediction_path "${OUT_DIR}/eval_valid_prediction.json" \
  --output_md "${OUT_DIR}/eval_valid_error_cases.md"

echo "End time: $(date)"
echo "Eval log saved to: ${LOG_PATH}"