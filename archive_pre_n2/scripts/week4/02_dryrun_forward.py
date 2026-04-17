import json
import math
from pathlib import Path
import argparse

import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModelForCausalLM

from data.dataset import DataModule
from data.collate import QueryCollator
from model.gnn import GraphEnhancer
from model.drkgc import DrKGC


def get_args():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset_path", required=True)
    p.add_argument("--model_name_or_path", default="TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    p.add_argument("--kge_embedding_path", required=True)
    p.add_argument("--source_max_len", type=int, default=768)
    p.add_argument("--target_max_len", type=int, default=32)
    p.add_argument("--batch_size", type=int, default=2)
    p.add_argument("--num_rels", type=int, default=4)
    p.add_argument("--gnn_hidden_dim", type=int, default=128)
    p.add_argument("--gnn_num_hidden_layers", type=int, default=1)
    p.add_argument("--steps", type=int, default=2)
    return p.parse_args()


def main():
    args = get_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print("device:", device)
    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()

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

    llm = AutoModelForCausalLM.from_pretrained(args.model_name_or_path)
    llm.resize_token_embeddings(len(tokenizer))
    llm.to(device)
    llm.eval()

    kge_embedding = torch.load(args.kge_embedding_path, map_location="cpu")
    kge_embedding_dim = kge_embedding.shape[1]

    graph_model = GraphEnhancer(
        kge_embedding=kge_embedding,
        input_size=kge_embedding_dim,
        num_rels=args.num_rels,
        gnn_hidden_dim=args.gnn_hidden_dim,
        gnn_num_hidden_layers=args.gnn_num_hidden_layers,
        adapter_size=1024,
        output_size=llm.config.hidden_size,
    ).to(device)

    model = DrKGC(tokenizer, llm, graph_model).to(device)
    model.eval()

    for step, batch in enumerate(train_loader):
        if step >= args.steps:
            break

        batch = {
            k: (v.to(device) if hasattr(v, "to") else v)
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

        loss = out.loss.item()
        finite = math.isfinite(loss)

        print("=" * 80)
        print("step:", step)
        print("actual_batch_size:", batch["input_ids"].shape[0])
        print("sequence_length:", batch["input_ids"].shape[1])
        print("num_candidates_per_sample:", batch["entity_ids"].shape[1])
        print("query_ids_shape:", tuple(batch["query_ids"].shape))
        print("entity_ids_shape:", tuple(batch["entity_ids"].shape))
        print("loss:", loss)
        print("loss_is_finite:", finite)

        if device == "cuda":
            peak_mb = torch.cuda.max_memory_allocated() / (1024 ** 2)
            print("peak_gpu_memory_mb:", round(peak_mb, 2))

        assert finite, "Loss is not finite."

    print("Dry run finished successfully.")


if __name__ == "__main__":
    main()