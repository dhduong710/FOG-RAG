#!/usr/bin/env bash
set -euo pipefail

export HF_HOME="${HF_HOME:-$HOME/.cache/huggingface}"
export TOKENIZERS_PARALLELISM=false

CKPT="results/week20/e2e_primary_checkpoint"
MODEL="meta-llama/Llama-3.2-3B"
KGE="dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt"
RETR_DS="dataset/setting_a/29_n2_e2e_infer_ready/retrieval_main"

mkdir -p results/week20

echo "============================================================"
echo "Running retrieval_main E2E infer on test"
echo "============================================================"

python infer.py \
  --model_name_or_path "$MODEL" \
  --model_type llama \
  --dataset_path "$RETR_DS" \
  --kge_embedding_path "$KGE" \
  --checkpoint_dir "$CKPT" \
  --eval_split test \
  --source_max_len 768 \
  --target_max_len 64 \
  --candidate_k 20 \
  --subgraph_tau 100 \
  --max_new_tokens 16 \
  --output_suffix retrieval_main_e2e \
  2>&1 | tee results/week20/day4_retrieval_main_e2e.log

echo "Day 4 retrieval_main infer finished."
