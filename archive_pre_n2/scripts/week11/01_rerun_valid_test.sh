#!/usr/bin/env bash
set -euo pipefail

# ====== EDIT THESE ======
MODEL_NAME="meta-llama/Llama-3.2-3B"
KGE_PATH="dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt"
PYTHON_BIN="python"
# ========================

run_one () {
  local name="$1"
  local dataset_path="$2"
  local checkpoint_dir="$3"
  local split="$4"

  echo "============================================================"
  echo "Running: ${name} | split=${split}"
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
    --eval_split "${split}" \
    --output_suffix rerun
}

# backbone
run_one \
  backbone \
  dataset/setting_a/12_backbone_ready_ranker_v2 \
  results/week11_test/backbone_test/checkpoint-final \
  valid

run_one \
  backbone \
  dataset/setting_a/12_backbone_ready_ranker_v2 \
  results/week11_test/backbone_test/checkpoint-final \
  test

# ontology
run_one \
  ontology \
  dataset/setting_a/18_ontology_only_eval_ready \
  results/week11_test/ontology_test/checkpoint-final \
  valid

run_one \
  ontology \
  dataset/setting_a/18_ontology_only_eval_ready \
  results/week11_test/ontology_test/checkpoint-final \
  test

# hard_main
run_one \
  hard_main \
  dataset/setting_a/19_contra_aware_eval_ready/hard_main \
  results/week11_test/hard_main_test/checkpoint-final \
  valid

run_one \
  hard_main \
  dataset/setting_a/19_contra_aware_eval_ready/hard_main \
  results/week11_test/hard_main_test/checkpoint-final \
  test

# soft_best
run_one \
  soft_best \
  dataset/setting_a/19_contra_aware_eval_ready/soft_best \
  results/week11_test/soft_best_test/checkpoint-final \
  valid

run_one \
  soft_best \
  dataset/setting_a/19_contra_aware_eval_ready/soft_best \
  results/week11_test/soft_best_test/checkpoint-final \
  test

echo "All reruns completed."