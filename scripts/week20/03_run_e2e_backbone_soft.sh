#!/usr/bin/env bash
set -euo pipefail

export HF_HOME="${HF_HOME:-$HOME/.cache/huggingface}"
export TOKENIZERS_PARALLELISM=false

CKPT="results/week20/e2e_primary_checkpoint"
MODEL="meta-llama/Llama-3.2-3B"
KGE="dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt"

BACKBONE_DS="dataset/setting_a/29_n2_e2e_infer_ready/backbone_raw"
SOFT_DS="dataset/setting_a/29_n2_e2e_infer_ready/soft_support_raw"

mkdir -p results/week20

echo "============================================================"
echo "[1/2] Running backbone_raw E2E infer on test"
echo "============================================================"
python infer.py \
  --model_name_or_path "$MODEL" \
  --model_type llama \
  --dataset_path "$BACKBONE_DS" \
  --kge_embedding_path "$KGE" \
  --checkpoint_dir "$CKPT" \
  --eval_split test \
  --source_max_len 768 \
  --target_max_len 64 \
  --candidate_k 20 \
  --subgraph_tau 100 \
  --max_new_tokens 16 \
  --output_suffix backbone_raw_e2e \
  2>&1 | tee results/week20/day3_backbone_raw_e2e.log

echo "============================================================"
echo "[2/2] Running soft_support_raw E2E infer on test"
echo "============================================================"
python infer.py \
  --model_name_or_path "$MODEL" \
  --model_type llama \
  --dataset_path "$SOFT_DS" \
  --kge_embedding_path "$KGE" \
  --checkpoint_dir "$CKPT" \
  --eval_split test \
  --source_max_len 768 \
  --target_max_len 64 \
  --candidate_k 20 \
  --subgraph_tau 100 \
  --max_new_tokens 16 \
  --output_suffix soft_support_raw_e2e \
  2>&1 | tee results/week20/day3_soft_support_raw_e2e.log

echo "Day 3 infer runs finished."
