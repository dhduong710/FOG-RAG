from __future__ import annotations

import argparse
import json
from copy import deepcopy
from contextlib import nullcontext
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch
from tqdm import tqdm
from transformers import AutoTokenizer, GenerationConfig, LlamaForCausalLM, set_seed
from peft import PeftModel

from data import DataModule
from model import GraphEnhancer, DrKGC


def parse_args():
    parser = argparse.ArgumentParser(description="Week 4 Day 4 pilot inference for valid/test.")

    parser.add_argument(
        "--dataset_path",
        type=str,
        default="dataset/setting_a/07_pilot_ready",
        help="Path containing train.json / valid.json / test.json",
    )
    parser.add_argument(
        "--model_name_or_path",
        type=str,
        default="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        help="Base HF model",
    )
    parser.add_argument(
        "--checkpoint_dir",
        type=str,
        default="results/week4/pilot_train_tinyllama_mock/checkpoint-final",
        help="Checkpoint directory containing LoRA adapter + graph_model.bin",
    )
    parser.add_argument(
        "--kge_embedding_path",
        type=str,
        default="dataset/setting_a/07_pilot_ready/mock_entity_embeddings.pt",
        help="Path to mock entity embeddings",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="results/week4/pilot_infer_tinyllama_mock",
        help="Where to save predictions and reports",
    )
    parser.add_argument(
        "--source_max_len",
        type=int,
        default=768,
        help="Only needed because DataModule expects full args namespace consistency",
    )
    parser.add_argument(
        "--target_max_len",
        type=int,
        default=32,
        help="Only needed because DataModule expects full args namespace consistency",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=2025,
        help="Random seed",
    )
    parser.add_argument(
        "--max_new_tokens",
        type=int,
        default=16,
        help="Short generation is enough because target is a drug name",
    )
    return parser.parse_args()


def build_generation_config(args) -> GenerationConfig:
    return GenerationConfig(
        max_new_tokens=args.max_new_tokens,
        min_new_tokens=1,
        do_sample=False,
        num_beams=1,
        num_return_sequences=1,
        use_cache=True,
        temperature=1.0,
        top_k=50,
        repetition_penalty=1.0,
        length_penalty=1.0,
        no_repeat_ngram_size=0,
        return_dict_in_generate=True,
        output_scores=False,
    )


def load_model_and_tokenizer(args):
    print(f"Loading tokenizer from: {args.model_name_or_path}")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path, use_fast=False)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.add_tokens(["[QUERY]", "[ENTITY]", "[RELATION]"])

    print(f"Loading base model from: {args.model_name_or_path}")
    base_model = LlamaForCausalLM.from_pretrained(
        args.model_name_or_path,
        low_cpu_mem_usage=True,
        device_map="auto",
        torch_dtype=torch.float16,
    )

    print(f"Loading LoRA checkpoint from: {args.checkpoint_dir}")
    base_model = PeftModel.from_pretrained(base_model, args.checkpoint_dir)
    base_model = base_model.half()

    print(f"Loading graph embeddings from: {args.kge_embedding_path}")
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

    graph_ckpt_path = Path(args.checkpoint_dir) / "graph_model.bin"
    if not graph_ckpt_path.exists():
        raise FileNotFoundError(f"Missing graph checkpoint: {graph_ckpt_path}")

    graph_state = torch.load(graph_ckpt_path, map_location="cpu")
    graph_model.load_state_dict(graph_state)

    model = DrKGC(tokenizer, base_model, graph_model)
    model = model.half()
    model.cuda()
    model.eval()

    return tokenizer, model


def decode_prediction(tokenizer, sequences: torch.Tensor, input_len: int) -> str:
    """
    Robust decoding:
    - try to decode only generated tail if available
    - fallback to full decode otherwise
    """
    seq = sequences[0].detach().cpu()
    full_text = tokenizer.decode(seq, skip_special_tokens=True).strip()

    if seq.shape[0] > input_len:
        gen_only = tokenizer.decode(seq[input_len:], skip_special_tokens=True).strip()
        if gen_only:
            return gen_only

    return full_text


def compute_rank_like_repo(target: str, pred: str, coarse_rank: int, rank_entities: List[str]) -> int:
    """
    Keep the same ranking logic as repo/infer.py for consistency.
    """
    if target == pred:
        return 1

    if pred not in set(rank_entities):
        return coarse_rank + 1

    pred_pos = rank_entities.index(pred)  # 0-based index
    if pred_pos >= coarse_rank:
        return coarse_rank + 1

    return coarse_rank


def run_split(
    split_name: str,
    dataset,
    tokenizer,
    model,
    generation_config: GenerationConfig,
) -> Tuple[List[Dict], Dict]:
    model.eval()

    preds = []
    ranks = []
    exact_matches = []
    coarse_ranks = []

    amp_ctx = torch.cuda.amp.autocast() if torch.cuda.is_available() else nullcontext()

    for ex in tqdm(dataset, desc=f"Infer {split_name}"):
        item = deepcopy(ex)

        prompt = item["input"]
        target = str(item["output"]).strip()
        coarse_rank = int(item["rank"])
        coarse_ranks.append(coarse_rank)

        inputs = tokenizer(prompt, return_tensors="pt")
        input_ids = inputs.input_ids.cuda()

        generation_config.eos_token_id = tokenizer.eos_token_id
        generation_config.bos_token_id = tokenizer.bos_token_id
        generation_config.pad_token_id = tokenizer.pad_token_id

        subgraph = [item["subgraph"]] if "subgraph" in item else None

        with torch.no_grad():
            with amp_ctx:
                output = model.generate(
                    input_ids=input_ids,
                    query_ids=torch.LongTensor([item["query_entity_id"]]).to(input_ids.device),
                    entity_ids=torch.LongTensor([item["rank_entities_id"]]).to(input_ids.device),
                    subgraph=subgraph,
                    generation_config=generation_config,
                )

        pred = decode_prediction(tokenizer, output.sequences, input_len=input_ids.shape[1]).strip()
        pred_rank = compute_rank_like_repo(target, pred, coarse_rank, item["rank_entities"])

        exact = int(pred == target)
        exact_matches.append(exact)
        ranks.append(pred_rank)

        out_item = {
            "triple": item["triple"],
            "triple_id": item["triple_id"],
            "type": item["type"],
            "query_entity": item["query_entity"],
            "query_entity_id": item["query_entity_id"],
            "target": target,
            "pred": pred,
            "coarse_rank": coarse_rank,
            "pred_rank": pred_rank,
            "exact_match": exact,
            "candidate_top5": item["rank_entities"][:5],
            "num_candidates": len(item["rank_entities"]),
            "subgraph_size": len(item.get("subgraph", [])),
            "input_preview": prompt[:400],
        }
        preds.append(out_item)

    ranks = np.array(ranks, dtype=np.float64)
    exact_matches = np.array(exact_matches, dtype=np.float64)
    coarse_ranks = np.array(coarse_ranks, dtype=np.float64)

    metrics = {
        "num_samples": int(len(preds)),
        "exact_match": float(np.mean(exact_matches)) if len(exact_matches) else 0.0,
        "mrr": float(np.mean(1.0 / ranks)) if len(ranks) else 0.0,
        "hits1": float(np.mean(ranks <= 1)) if len(ranks) else 0.0,
        "hits3": float(np.mean(ranks <= 3)) if len(ranks) else 0.0,
        "hits10": float(np.mean(ranks <= 10)) if len(ranks) else 0.0,
        "avg_subgraph_size": float(np.mean([p["subgraph_size"] for p in preds])) if preds else 0.0,
        "all_coarse_rank_is_one": bool(np.all(coarse_ranks == 1)) if len(coarse_ranks) else False,
    }

    metrics = {
        k: (round(v, 8) if isinstance(v, float) else v)
        for k, v in metrics.items()
    }

    return preds, metrics


def make_case_review_markdown(valid_preds: List[Dict], test_preds: List[Dict], metrics: Dict) -> str:
    def pick_cases(preds, exact_value: int, limit: int = 5):
        out = []
        for x in preds:
            if x["exact_match"] == exact_value:
                out.append(x)
            if len(out) >= limit:
                break
        return out

    def render_cases(title: str, cases: List[Dict]) -> str:
        lines = [f"## {title}"]
        if not cases:
            lines.append("- none")
            return "\n".join(lines)

        for i, x in enumerate(cases, 1):
            lines.extend(
                [
                    f"### {i}. Query: {x['query_entity']}",
                    f"- target: {x['target']}",
                    f"- pred: {x['pred']}",
                    f"- coarse_rank: {x['coarse_rank']}",
                    f"- pred_rank: {x['pred_rank']}",
                    f"- subgraph_size: {x['subgraph_size']}",
                    f"- candidate_top5: {x['candidate_top5']}",
                    f"- input_preview: `{x['input_preview']}`",
                    "",
                ]
            )
        return "\n".join(lines)

    valid_correct = pick_cases(valid_preds, exact_value=1, limit=5)
    valid_wrong = pick_cases(valid_preds, exact_value=0, limit=5)
    test_correct = pick_cases(test_preds, exact_value=1, limit=5)
    test_wrong = pick_cases(test_preds, exact_value=0, limit=5)

    note = ""
    if metrics["valid"]["all_coarse_rank_is_one"] and metrics["test"]["all_coarse_rank_is_one"]:
        note = (
            "Because the week-4 pilot still uses the week-2 mock coarse ranker "
            "(gold fixed at rank 1), MRR / Hits@K here are sanity-only and not scientific."
        )

    parts = [
        "# Day 4 Pilot Inference Case Review",
        "",
        "## Key Note",
        f"- {note or 'Ranking metrics should still be interpreted cautiously on the pilot subset.'}",
        "",
        "## Valid Metrics",
        f"- {metrics['valid']}",
        "",
        "## Test Metrics",
        f"- {metrics['test']}",
        "",
        render_cases("Valid - Correct Cases", valid_correct),
        "",
        render_cases("Valid - Wrong Cases", valid_wrong),
        "",
        render_cases("Test - Correct Cases", test_correct),
        "",
        render_cases("Test - Wrong Cases", test_wrong),
        "",
    ]
    return "\n".join(parts)


def main():
    args = parse_args()
    set_seed(args.seed)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    tokenizer, model = load_model_and_tokenizer(args)
    generation_config = build_generation_config(args)

    data_args = argparse.Namespace(
        dataset_path=args.dataset_path,
        source_max_len=args.source_max_len,
        target_max_len=args.target_max_len,
    )
    data_module = DataModule(data_args, tokenizer)

    valid_preds, valid_metrics = run_split(
        split_name="valid",
        dataset=data_module.eval_ds,
        tokenizer=tokenizer,
        model=model,
        generation_config=generation_config,
    )

    test_preds, test_metrics = run_split(
        split_name="test",
        dataset=data_module.test_ds,
        tokenizer=tokenizer,
        model=model,
        generation_config=generation_config,
    )

    all_metrics = {
        "args": vars(args),
        "valid": valid_metrics,
        "test": test_metrics,
    }

    with (output_dir / "valid_predictions.json").open("w", encoding="utf-8") as f:
        json.dump(valid_preds, f, ensure_ascii=False, indent=2)

    with (output_dir / "test_predictions.json").open("w", encoding="utf-8") as f:
        json.dump(test_preds, f, ensure_ascii=False, indent=2)

    with (output_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(all_metrics, f, ensure_ascii=False, indent=2)

    case_review = make_case_review_markdown(valid_preds, test_preds, all_metrics)
    (output_dir / "case_review.md").write_text(case_review, encoding="utf-8")

    print("=" * 80)
    print("VALID METRICS")
    print(valid_metrics)
    print("=" * 80)
    print("TEST METRICS")
    print(test_metrics)
    print("=" * 80)
    print(f"Saved: {output_dir / 'valid_predictions.json'}")
    print(f"Saved: {output_dir / 'test_predictions.json'}")
    print(f"Saved: {output_dir / 'metrics.json'}")
    print(f"Saved: {output_dir / 'case_review.md'}")


if __name__ == "__main__":
    main()