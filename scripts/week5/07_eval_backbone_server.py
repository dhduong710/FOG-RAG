#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
import torch
from tqdm import tqdm
from transformers import AutoTokenizer, LlamaForCausalLM, GenerationConfig
from peft import PeftModel

from data import DataModule
from model import GraphEnhancer, DrKGC


def parse_args():
    p = argparse.ArgumentParser(description="Week 5 Day 6 - evaluate backbone checkpoint on valid/test")
    p.add_argument("--dataset_path", default="dataset/setting_a/08_backbone_ready")
    p.add_argument("--model_name_or_path", default="meta-llama/Llama-3.2-3B")
    p.add_argument("--checkpoint_dir", default="results/week5/backbone_llama32_3b_rgcn/checkpoint-final")
    p.add_argument("--kge_embedding_path", default="dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt")
    p.add_argument("--split", default="valid", choices=["valid", "test"])
    p.add_argument("--output_dir", default="results/week5/backbone_llama32_3b_rgcn")

    p.add_argument("--max_new_tokens", type=int, default=64)
    p.add_argument("--min_new_tokens", type=int, default=1)
    p.add_argument("--do_sample", action="store_true")
    p.add_argument("--num_beams", type=int, default=1)
    p.add_argument("--temperature", type=float, default=1.0)
    p.add_argument("--top_k", type=int, default=50)

    p.add_argument("--seed", type=int, default=2025)
    return p.parse_args()


def set_seed(seed: int):
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def normalize_prediction(text: str) -> str:
    """
    Safer post-processing than raw infer.py:
    - strip prompt prefix if Answer: appears
    - keep first non-empty line
    - trim whitespace and trailing punctuation
    """
    pred = (text or "").strip()

    if "Answer:" in pred:
        pred = pred.split("Answer:")[-1].strip()

    lines = [x.strip() for x in pred.splitlines() if x.strip()]
    if lines:
        pred = lines[0]

    pred = pred.strip().strip(".").strip()
    return pred


def build_generation_config(args, tokenizer):
    cfg = GenerationConfig(
        max_new_tokens=args.max_new_tokens,
        min_new_tokens=args.min_new_tokens,
        do_sample=args.do_sample,
        num_beams=args.num_beams,
        temperature=args.temperature,
        top_k=args.top_k,
        use_cache=True,
        num_return_sequences=1,
        output_scores=False,
        return_dict_in_generate=True,
    )
    cfg.bos_token_id = tokenizer.bos_token_id
    cfg.eos_token_id = tokenizer.eos_token_id
    return cfg


@torch.no_grad()
def ranking_metrics(dataset: List[Dict[str, Any]], tokenizer, model, generation_config, split_name: str):
    model.eval()

    ranks = []
    preds = []
    generated_ids = []

    for ex_idx, ex in enumerate(tqdm(dataset, desc=f"Evaluating {split_name}")):
        prompt = ex["input"]
        inputs = tokenizer(prompt, return_tensors="pt")
        input_ids = inputs.input_ids.cuda()

        subgraph = [ex["subgraph"]] if "subgraph" in ex else None

        output = model.generate(
            input_ids=input_ids,
            query_ids=torch.LongTensor([ex["query_entity_id"]]).to(input_ids.device),
            entity_ids=torch.LongTensor([ex["rank_entities_id"]]).to(input_ids.device),
            subgraph=subgraph,
            generation_config=generation_config,
        )

        generated_ids.append(output.sequences[0].detach().cpu().tolist())

    decoded = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

    for ex_idx, ex in enumerate(dataset):
        target = ex["output"]
        original_rank = ex["rank"]
        pred_text = normalize_prediction(decoded[ex_idx])

        topk_names = ex["rank_entities"]

        if target == pred_text:
            pred_rank = 1
        else:
            if pred_text not in set(topk_names) or topk_names.index(pred_text) >= original_rank:
                pred_rank = original_rank + 1
            else:
                pred_rank = topk_names.index(pred_text) + 1

        record = dict(ex)
        record["target"] = target
        record["pred"] = pred_text
        record["pred_rank"] = pred_rank
        record["pred_in_candidate"] = pred_text in set(topk_names)
        record["candidate_size"] = len(topk_names)
        record["subgraph_size"] = len(ex.get("subgraph", []))
        preds.append(record)
        ranks.append(pred_rank)

    ranks = np.array(ranks, dtype=np.float32)
    metrics = {
        "mrr": round(float(np.mean(1.0 / ranks)), 8),
        "hits1": round(float(np.mean(ranks <= 1)), 8),
        "hits3": round(float(np.mean(ranks <= 3)), 8),
        "hits10": round(float(np.mean(ranks <= 10)), 8),
        "num_examples": int(len(preds)),
        "split": split_name,
    }
    return preds, metrics


def main():
    args = parse_args()
    set_seed(args.seed)

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("Week 5 Day 6 - Eval Backbone")
    print("=" * 80)
    print("dataset_path       :", args.dataset_path)
    print("model_name_or_path :", args.model_name_or_path)
    print("checkpoint_dir     :", args.checkpoint_dir)
    print("kge_embedding_path :", args.kge_embedding_path)
    print("split              :", args.split)
    print("=" * 80)

    tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path, use_fast=False)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.add_tokens(["[QUERY]", "[ENTITY]", "[RELATION]"])

    base_model = LlamaForCausalLM.from_pretrained(
        args.model_name_or_path,
        low_cpu_mem_usage=True,
        device_map=None,
        torch_dtype=torch.float16,
    )
    base_model = PeftModel.from_pretrained(base_model, args.checkpoint_dir)
    base_model = base_model.half()

    kge_embedding = torch.load(args.kge_embedding_path, map_location="cpu")
    kge_embedding_dim = kge_embedding.shape[1]

    llm_config = base_model.config
    graph_model = GraphEnhancer(
        kge_embedding,
        kge_embedding_dim,
        4,
        128,
        1,
        1024,
        llm_config.hidden_size,
        llm_config.hidden_act,
    )

    ckpt_dir = Path(args.checkpoint_dir)
    graph_state_path = ckpt_dir / "graph_model.bin"
    state = torch.load(graph_state_path, map_location="cpu")
    graph_model.load_state_dict(state)

    model = DrKGC(tokenizer, base_model, graph_model)
    model = model.half().cuda()
    model.eval()

    data_args = argparse.Namespace(
        dataset_path=args.dataset_path,
        model_name_or_path=args.model_name_or_path,
        model_type="llama",
        kge_embedding_path=args.kge_embedding_path,
        source_max_len=768,
        target_max_len=64,
        checkpoint_dir=args.checkpoint_dir,
    )
    data_module = DataModule(data_args, tokenizer)

    if args.split == "valid":
        dataset = data_module.valid_ds
    else:
        dataset = data_module.test_ds

    generation_config = build_generation_config(args, tokenizer)

    with torch.cuda.amp.autocast():
        preds, metrics = ranking_metrics(dataset, tokenizer, model, generation_config, args.split)

    pred_path = Path(args.output_dir) / f"eval_{args.split}_prediction.json"
    metrics_path = Path(args.output_dir) / f"eval_{args.split}_metrics.json"

    json.dump(
        {
            "args": vars(args),
            "generation_config": generation_config.to_dict(),
            "metrics": metrics,
            "prediction": preds,
        },
        open(pred_path, "w", encoding="utf-8"),
        ensure_ascii=False,
        indent=2,
    )
    json.dump(metrics, open(metrics_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print("Ranking metrics:")
    print(metrics)
    print("Saved:", pred_path)
    print("Saved:", metrics_path)


if __name__ == "__main__":
    main()