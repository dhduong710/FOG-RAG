#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from transformers import (
    AutoConfig,
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)
from transformers import LlamaForCausalLM

from peft import prepare_model_for_kbit_training, LoraConfig, get_peft_model
from peft.tuners.lora import LoraLayer

from data.dataset import DataModule
from data.collate import QueryCollator
from model.gnn import GraphEnhancer
from model.drkgc import DrKGC


def parse_args():
    p = argparse.ArgumentParser(description="Week 5 Day 4 - server dry run with full-ready data + real embeddings")

    p.add_argument("--dataset_path", default="dataset/setting_a/08_backbone_ready")
    p.add_argument("--model_name_or_path", default="meta-llama/Llama-3.2-3B")
    p.add_argument("--model_type", default="llama", choices=["llama", "mistral"])
    p.add_argument("--kge_embedding_path", default="dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt")

    p.add_argument("--source_max_len", type=int, default=768)
    p.add_argument("--target_max_len", type=int, default=64)
    p.add_argument("--batch_size", type=int, default=1)
    p.add_argument("--steps", type=int, default=2)

    p.add_argument("--num_rels", type=int, default=4)
    p.add_argument("--gnn_hidden_dim", type=int, default=128)
    p.add_argument("--gnn_num_hidden_layers", type=int, default=1)
    p.add_argument("--adapter_size", type=int, default=1024)

    p.add_argument("--use_quant", action="store_true")
    p.add_argument("--bits", type=int, default=4, choices=[4, 8])
    p.add_argument("--double_quant", action="store_true")
    p.add_argument("--quant_type", default="nf4")

    p.add_argument("--lora_r", type=int, default=32)
    p.add_argument("--lora_alpha", type=int, default=32)
    p.add_argument("--lora_dropout", type=float, default=0.1)

    p.add_argument("--seed", type=int, default=2025)
    p.add_argument("--report_path", default="reports/week5/day4_server_dryrun_report.md")

    return p.parse_args()


def set_seed(seed: int):
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_llm_with_optional_quant_and_lora(args):
    model_config = AutoConfig.from_pretrained(args.model_name_or_path)

    if args.use_quant:
        compute_dtype = torch.bfloat16
        quant_config = BitsAndBytesConfig(
            load_in_4bit=(args.bits == 4),
            load_in_8bit=(args.bits == 8),
            llm_int8_threshold=6.0,
            llm_int8_has_fp16_weight=False,
            bnb_4bit_compute_dtype=compute_dtype,
            bnb_4bit_use_double_quant=args.double_quant,
            bnb_4bit_quant_type=args.quant_type,
        )

        if args.model_type == "llama":
            model = LlamaForCausalLM.from_pretrained(
                args.model_name_or_path,
                config=model_config,
                device_map="auto",
                quantization_config=quant_config,
                torch_dtype=torch.bfloat16,
            )
        else:
            model = AutoModelForCausalLM.from_pretrained(
                args.model_name_or_path,
                config=model_config,
                device_map="auto",
                quantization_config=quant_config,
                torch_dtype=torch.bfloat16,
            )

        model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    else:
        if args.model_type == "llama":
            model = LlamaForCausalLM.from_pretrained(
                args.model_name_or_path,
                config=model_config,
                low_cpu_mem_usage=True,
            )
        else:
            model = AutoModelForCausalLM.from_pretrained(
                args.model_name_or_path,
                config=model_config,
                low_cpu_mem_usage=True,
            )

    if args.model_type == "llama":
        lora_cfg = LoraConfig(
            r=args.lora_r,
            lora_alpha=args.lora_alpha,
            lora_dropout=args.lora_dropout,
            bias="none",
            task_type="CAUSAL_LM",
        )
    else:
        lora_cfg = LoraConfig(
            r=args.lora_r,
            lora_alpha=args.lora_alpha,
            lora_dropout=args.lora_dropout,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=[
                "q_proj",
                "k_proj",
                "v_proj",
                "o_proj",
                "gate_proj",
                "up_proj",
                "down_proj",
                "lm_head",
            ],
        )

    model = get_peft_model(model, lora_cfg)

    for name, module in model.named_modules():
        if isinstance(module, LoraLayer):
            module.to(torch.bfloat16)
        if "norm" in name:
            module.to(torch.float32)
        if "lm_head" in name or "embed_tokens" in name:
            if hasattr(module, "weight") and module.weight.dtype == torch.float32:
                module.to(torch.bfloat16)

    model.config.use_cache = False
    return model


def get_effective_device(model):
    # For quantized / device_map="auto" models, parameters may live on first CUDA device.
    try:
        return next(model.parameters()).device
    except StopIteration:
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def main():
    args = parse_args()
    set_seed(args.seed)

    local_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if local_device.type == "cuda":
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.empty_cache()

    print("=" * 80)
    print("Week 5 Day 4 - Server Dry Run")
    print("=" * 80)
    print("dataset_path       :", args.dataset_path)
    print("model_name_or_path :", args.model_name_or_path)
    print("kge_embedding_path :", args.kge_embedding_path)
    print("use_quant          :", args.use_quant)
    print("bits               :", args.bits)
    print("source_max_len     :", args.source_max_len)
    print("target_max_len     :", args.target_max_len)
    print("batch_size         :", args.batch_size)
    print("steps              :", args.steps)
    print("=" * 80)

    tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path, use_fast=False)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.add_tokens(["[QUERY]", "[ENTITY]", "[RELATION]"])

    data_args = argparse.Namespace(
        dataset_path=args.dataset_path,
        source_max_len=args.source_max_len,
        target_max_len=args.target_max_len,
    )

    data_module = DataModule(data_args, tokenizer)
    collator = QueryCollator(
        args=None,
        tokenizer=tokenizer,
        source_max_len=args.source_max_len,
        target_max_len=args.target_max_len,
    )

    train_loader = DataLoader(
        data_module.train_ds,
        batch_size=args.batch_size,
        shuffle=False,
        collate_fn=collator,
    )

    llm = load_llm_with_optional_quant_and_lora(args)
    llm.resize_token_embeddings(len(tokenizer))

    llm_device = get_effective_device(llm)
    print("llm_effective_device:", llm_device)
    print("llm_hidden_size     :", llm.config.hidden_size)
    print("llm_hidden_act      :", getattr(llm.config, "hidden_act", "silu"))

    kge_embedding = torch.load(args.kge_embedding_path, map_location="cpu")
    assert isinstance(kge_embedding, torch.Tensor), f"Expected tensor embedding, got {type(kge_embedding)}"
    assert kge_embedding.ndim == 2, f"Expected 2D embedding, got shape {tuple(kge_embedding.shape)}"
    kge_embedding_dim = kge_embedding.shape[1]

    print("kge_embedding_shape :", tuple(kge_embedding.shape))

    graph_model = GraphEnhancer(
        kge_embedding=kge_embedding,
        input_size=kge_embedding_dim,
        num_rels=args.num_rels,
        gnn_hidden_dim=args.gnn_hidden_dim,
        gnn_num_hidden_layers=args.gnn_num_hidden_layers,
        adapter_size=args.adapter_size,
        output_size=llm.config.hidden_size,
        hidden_act=getattr(llm.config, "hidden_act", "silu"),
    ).to(llm_device)

    model = DrKGC(tokenizer, llm, graph_model).to(llm_device)
    model.eval()

    records = []
    for step, batch in enumerate(train_loader):
        if step >= args.steps:
            break

        start_t = time.time()

        batch = {
            k: (v.to(llm_device) if hasattr(v, "to") else v)
            for k, v in batch.items()
        }

        with torch.no_grad():
            out = model(
                input_ids=batch["input_ids"],
                attention_mask=batch["attention_mask"],
                labels=batch["labels"],
                query_ids=batch["query_ids"],
                entity_ids=batch["entity_ids"],
                subgraph=batch["subgraph"],
            )

        loss = float(out.loss.item())
        finite = math.isfinite(loss)
        elapsed = time.time() - start_t

        subgraph_sizes = [len(x) for x in batch["subgraph"]]
        rec = {
            "step": step,
            "actual_batch_size": int(batch["input_ids"].shape[0]),
            "sequence_length": int(batch["input_ids"].shape[1]),
            "num_candidates_per_sample": int(batch["entity_ids"].shape[1]),
            "query_ids_shape": tuple(batch["query_ids"].shape),
            "entity_ids_shape": tuple(batch["entity_ids"].shape),
            "subgraph_size_min": min(subgraph_sizes) if subgraph_sizes else None,
            "subgraph_size_max": max(subgraph_sizes) if subgraph_sizes else None,
            "loss": loss,
            "loss_is_finite": finite,
            "seconds_per_batch": round(elapsed, 4),
        }

        if local_device.type == "cuda":
            rec["peak_gpu_memory_mb"] = round(torch.cuda.max_memory_allocated() / (1024 ** 2), 2)

        records.append(rec)

        print("=" * 80)
        for k, v in rec.items():
            print(f"{k}: {v}")

        assert finite, "Loss is not finite."

    overall_ok = len(records) > 0 and all(x["loss_is_finite"] for x in records)

    report_lines = [
        "# Week 5 - Day 4 Server Dry Run Report",
        "",
        "## Config",
        f"- dataset_path: `{args.dataset_path}`",
        f"- model_name_or_path: `{args.model_name_or_path}`",
        f"- model_type: `{args.model_type}`",
        f"- kge_embedding_path: `{args.kge_embedding_path}`",
        f"- use_quant: `{args.use_quant}`",
        f"- bits: `{args.bits}`",
        f"- batch_size: `{args.batch_size}`",
        f"- source_max_len: `{args.source_max_len}`",
        f"- target_max_len: `{args.target_max_len}`",
        f"- adapter_size: `{args.adapter_size}`",
        f"- gnn_hidden_dim: `{args.gnn_hidden_dim}`",
        f"- gnn_num_hidden_layers: `{args.gnn_num_hidden_layers}`",
        "",
        "## Model / Embedding",
        f"- llm_effective_device: `{llm_device}`",
        f"- llm_hidden_size: `{llm.config.hidden_size}`",
        f"- llm_hidden_act: `{getattr(llm.config, 'hidden_act', 'silu')}`",
        f"- kge_embedding_shape: `{tuple(kge_embedding.shape)}`",
        "",
        "## Per-step records",
        "```json",
        json.dumps(records, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Judgment",
        f"- DRYRUN_VALID: `{overall_ok}`",
        "",
        "## Interpretation",
        "A successful day-4 dry run means full-ready data + real embedding + LLM + graph branch can produce finite loss on server.",
    ]

    Path(args.report_path).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report_path).write_text("\n".join(report_lines), encoding="utf-8")

    print("\nSaved report:", args.report_path)
    if overall_ok:
        print("[OK] Day-4 server dry run passed.")
    else:
        print("[WARN] Day-4 server dry run did not pass cleanly.")


if __name__ == "__main__":
    main()