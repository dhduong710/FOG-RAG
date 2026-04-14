#!/usr/bin/env bash
set -euo pipefail

# =========================
# EDIT THESE IF NEEDED
# =========================
MODEL_NAME="meta-llama/Llama-3.2-3B-Instruct"
KGE_PATH="dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt"
PYTHON_BIN="python"
PKG_ROOT="dataset/setting_a/20_test_rerun_eval_ready"
# =========================

run_one () {
  local name="$1"
  local dataset_path="$2"
  local checkpoint_dir="$3"

  echo "============================================================"
  echo "Running TEST rerun for: ${name}"
  echo "dataset_path=${dataset_path}"
  echo "checkpoint_dir=${checkpoint_dir}"
  echo "============================================================"

  ${PYTHON_BIN} infer.py \
    --dataset_path "${dataset_path}" \
    --model_name_or_path "${MODEL_NAME}" \
    --model_type llama \
    --kge_embedding_path "${KGE_PATH}" \
    --checkpoint_dir "${checkpoint_dir}" \
    --source_max_len 768 \
    --target_max_len 64 \
    --eval_split test \
    --output_suffix rerun_clean
}

run_one \
  backbone \
  ${PKG_ROOT}/backbone \
  results/week11_test/backbone_test/checkpoint-final

run_one \
  ontology \
  ${PKG_ROOT}/ontology \
  results/week11_test/ontology_test/checkpoint-final

run_one \
  hard_main \
  ${PKG_ROOT}/hard_main \
  results/week11_test/hard_main_test/checkpoint-final

run_one \
  soft_best \
  ${PKG_ROOT}/soft_best \
  results/week11_test/soft_best_test/checkpoint-final

echo "All TEST reruns completed."