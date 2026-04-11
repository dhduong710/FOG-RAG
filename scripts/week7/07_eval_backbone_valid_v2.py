#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Week 7 - Day 6
Evaluate the short rerun checkpoint on valid split only.

Outputs:
- results/week7/backbone_valid_v2_short/valid_eval_v2/eval_valid_v2_metrics.json
- results/week7/backbone_valid_v2_short/valid_eval_v2/eval_valid_v2_prediction.json
- results/week7/backbone_valid_v2_short/valid_eval_v2/eval_valid_v2_error_cases.md
- reports/week7/day6_valid_eval_v2.md
"""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict, Counter
from pathlib import Path
from typing import Any, Dict, List

import torch
from transformers import (
    AutoTokenizer,
    GenerationConfig,
    HfArgumentParser,
    LlamaForCausalLM,
)
from peft import PeftModel

from arguments import Arguments, GenerationArguments
from data.dataset import DataModule
from model.gnn import GraphEnhancer
from model.drkgc import DrKGC


def load_yaml(path: Path) -> Dict[str, Any]:
    import yaml
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def classify_error(ex: Dict[str, Any]) -> str:
    if ex["pred"] == ex["target"]:
        return "prediction_equals_gold"
    if not ex.get("gold_in_topk_raw", False):
        return "gold_not_in_candidate"
    if not ex.get("pred_in_candidate", False):
        return "prediction_not_in_candidate"
    return "prediction_in_candidate_but_not_top"


@torch.no_grad()
def run_valid_eval(
    model: DrKGC,
    tokenizer,
    dataset: List[Dict[str, Any]],
    generation_config: GenerationConfig,
    device: torch.device,
) -> tuple[Dict[str, Any], List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
    model.eval()

    generated_token_ids = []
    original_examples = []

    for ex in dataset:
        original_examples.append(dict(ex))

        prompt = ex["input"]
        inputs = tokenizer(prompt, return_tensors="pt")
        input_ids = inputs.input_ids.to(device)

        generation_config.eos_token_id = tokenizer.eos_token_id
        subgraph = [ex["subgraph"]] if "subgraph" in ex else None

        output = model.generate(
            input_ids=input_ids,
            query_ids=torch.LongTensor([ex["query_entity_id"]]).to(device),
            entity_ids=torch.LongTensor([ex["rank_entities_id"]]).to(device),
            subgraph=subgraph,
            generation_config=generation_config,
        )
        generated_token_ids.append(output[0].detach().cpu().tolist())

    decoded_preds = tokenizer.batch_decode(generated_token_ids, skip_special_tokens=True)

    preds = []
    ranks = []
    error_buckets = defaultdict(list)

    for ex, pred_text in zip(original_examples, decoded_preds):
        pred = str(pred_text).strip()
        target = ex["output"]
        topk_names = ex["rank_entities"]
        pred_in_candidate = pred in set(topk_names)

        rank = ex["rank"]
        if pred == target:
            rank = 1
        else:
            if (pred not in set(topk_names)) or (topk_names.index(pred) >= rank):
                rank += 1

        row = dict(ex)
        row["target"] = target
        row["pred"] = pred
        row["pred_rank"] = rank
        row["pred_in_candidate"] = pred_in_candidate
        row["candidate_size"] = len(ex["rank_entities"])
        row["subgraph_size"] = len(ex.get("subgraph", []))

        bucket = classify_error(row)
        error_buckets[bucket].append(row)

        preds.append(row)
        ranks.append(rank)

    ranks_t = torch.tensor(ranks, dtype=torch.float32)
    metrics = {
        "mrr": round(float((1.0 / ranks_t).mean().item()), 8),
        "hits1": round(float((ranks_t <= 1).float().mean().item()), 8),
        "hits3": round(float((ranks_t <= 3).float().mean().item()), 8),
        "hits10": round(float((ranks_t <= 10).float().mean().item()), 8),
        "num_examples": len(preds),
        "split": "valid",
    }

    return metrics, preds, error_buckets


def write_error_cases_md(path: Path, error_buckets: Dict[str, List[Dict[str, Any]]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("# Valid eval v2 error cases\n\n")
        for bucket in [
            "prediction_equals_gold",
            "gold_not_in_candidate",
            "prediction_in_candidate_but_not_top",
            "prediction_not_in_candidate",
        ]:
            rows = error_buckets.get(bucket, [])
            f.write(f"## {bucket} ({len(rows)})\n\n")
            for ex in rows[:20]:
                f.write(
                    f"- query={ex['query_entity']} | target={ex['target']} | pred={ex['pred']} "
                    f"| pred_rank={ex['pred_rank']} | gold_in_topk_raw={ex.get('gold_in_topk_raw')} "
                    f"| gold_injected={ex.get('gold_injected')} | pred_in_candidate={ex.get('pred_in_candidate')} "
                    f"| top5={ex.get('rank_entities', [])[:5]}\n"
                )
            f.write("\n")


def write_day6_markdown(
    path: Path,
    metrics_v2: Dict[str, Any],
    metrics_week6: Dict[str, Any] | None,
    candidate_report_week7: Dict[str, Any] | None,
    error_buckets: Dict[str, List[Dict[str, Any]]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("# Day 6 — valid rerun with backbone-ready v2")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Run a short backbone rerun on week7 candidate package.")
    lines.append("- Evaluate valid only.")
    lines.append("- Check whether better candidate retrieval transfers to reranker behavior.")
    lines.append("")

    lines.append("## Current valid metrics (week7 v2 rerun)")
    lines.append("")
    lines.append(f"- mrr = `{metrics_v2['mrr']}`")
    lines.append(f"- hits1 = `{metrics_v2['hits1']}`")
    lines.append(f"- hits3 = `{metrics_v2['hits3']}`")
    lines.append(f"- hits10 = `{metrics_v2['hits10']}`")
    lines.append(f"- num_examples = `{metrics_v2['num_examples']}`")
    lines.append("")

    if metrics_week6 is not None:
        lines.append("## Comparison against week6 valid reranker")
        lines.append("")
        lines.append(f"- week6_mrr = `{metrics_week6.get('mrr')}`")
        lines.append(f"- week7_v2_mrr = `{metrics_v2.get('mrr')}`")
        lines.append(f"- delta_mrr = `{round(metrics_v2['mrr'] - metrics_week6.get('mrr', 0.0), 8)}`")
        lines.append("")
        lines.append(f"- week6_hits1 = `{metrics_week6.get('hits1')}`")
        lines.append(f"- week7_v2_hits1 = `{metrics_v2.get('hits1')}`")
        lines.append(f"- delta_hits1 = `{round(metrics_v2['hits1'] - metrics_week6.get('hits1', 0.0), 8)}`")
        lines.append("")
        lines.append(f"- week6_hits3 = `{metrics_week6.get('hits3')}`")
        lines.append(f"- week7_v2_hits3 = `{metrics_v2.get('hits3')}`")
        lines.append(f"- delta_hits3 = `{round(metrics_v2['hits3'] - metrics_week6.get('hits3', 0.0), 8)}`")
        lines.append("")
        lines.append(f"- week6_hits10 = `{metrics_week6.get('hits10')}`")
        lines.append(f"- week7_v2_hits10 = `{metrics_v2.get('hits10')}`")
        lines.append(f"- delta_hits10 = `{round(metrics_v2['hits10'] - metrics_week6.get('hits10', 0.0), 8)}`")
        lines.append("")

    if candidate_report_week7 is not None:
        v = candidate_report_week7["splits"]["valid"]
        lines.append("## Candidate context from Day 3")
        lines.append("")
        lines.append(f"- valid_recall@20_raw = `{v['recall_at_k_raw']}`")
        lines.append(f"- valid_inject_ratio_ready = `{v['inject_ratio_ready']}`")
        lines.append(f"- valid_top1_hit_ratio_raw = `{v['top1_hit_ratio_raw']}`")
        lines.append("")

    lines.append("## Error bucket counts")
    lines.append("")
    for bucket in [
        "prediction_equals_gold",
        "gold_not_in_candidate",
        "prediction_in_candidate_but_not_top",
        "prediction_not_in_candidate",
    ]:
        lines.append(f"- {bucket} = `{len(error_buckets.get(bucket, []))}`")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("- If week7 v2 valid metrics hold or improve versus week6, the candidate improvement is transferring into reranker behavior.")
    lines.append("- If metrics drop sharply despite much better candidate retrieval, the new candidate distribution may be exposing reranker weakness.")
    lines.append("- Day 7 should close out with GO / CONDITIONAL GO / NO-GO based on both candidate quality and reranker validity.")
    lines.append("")

    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to configs/week7/backbone_valid_v2.yaml")
    args = parser.parse_args()

    cfg = load_yaml(Path(args.config))

    output_dir = Path(cfg["output_dir"])
    checkpoint_dir = Path(cfg["checkpoint_dir"])
    if not checkpoint_dir.exists():
        raise FileNotFoundError(
            f"Checkpoint dir not found: {checkpoint_dir}. "
            f"Run training first and confirm checkpoint-final exists."
        )

    valid_eval_dir = output_dir / "valid_eval_v2"
    valid_eval_dir.mkdir(parents=True, exist_ok=True)

    metrics_out = valid_eval_dir / "eval_valid_v2_metrics.json"
    preds_out = valid_eval_dir / "eval_valid_v2_prediction.json"
    error_md_out = valid_eval_dir / "eval_valid_v2_error_cases.md"
    day6_md = Path("reports/week7/day6_valid_eval_v2.md")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load tokenizer/base LLM + adapter
    tokenizer = AutoTokenizer.from_pretrained(cfg["model_name_or_path"], use_fast=False)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.add_tokens(["[QUERY]", "[ENTITY]", "[RELATION]"])

    base_model = LlamaForCausalLM.from_pretrained(
        cfg["model_name_or_path"],
        low_cpu_mem_usage=True,
        torch_dtype=torch.float16,
    )
    base_model = PeftModel.from_pretrained(base_model, str(checkpoint_dir))
    base_model = base_model.half().to(device)
    base_model.eval()

    # Build graph model
    kge_embedding = torch.load(cfg["kge_embedding_path"], map_location="cpu")
    kge_embedding_dim = int(kge_embedding.shape[1])
    llm_config = base_model.config

    graph_model = GraphEnhancer(
        kge_embedding=kge_embedding,
        input_size=kge_embedding_dim,
        num_rels=4,
        gnn_hidden_dim=128,
        gnn_num_hidden_layers=1,
        adapter_size=1024,
        output_size=llm_config.hidden_size,
        hidden_act=llm_config.hidden_act,
    )
    state = torch.load(checkpoint_dir / "graph_model.bin", map_location="cpu")
    graph_model.load_state_dict(state)
    graph_model = graph_model.half().to(device)
    graph_model.eval()

    model = DrKGC(tokenizer, base_model, graph_model)
    model = model.half().to(device)
    model.eval()

    # Use repo DataModule to read valid.json
    data_args = argparse.Namespace(
        dataset_path=cfg["dataset_path"],
        model_name_or_path=cfg["model_name_or_path"],
        model_type=cfg["model_type"],
        kge_embedding_path=cfg["kge_embedding_path"],
        source_max_len=cfg["source_max_len"],
        target_max_len=cfg["target_max_len"],
        checkpoint_dir=str(checkpoint_dir),
    )
    data_module = DataModule(data_args, tokenizer)
    valid_dataset = data_module.eval_ds

    gen_cfg = GenerationConfig(**cfg["generation"])
    gen_cfg.bos_token_id = tokenizer.bos_token_id
    gen_cfg.eos_token_id = tokenizer.eos_token_id

    metrics_v2, preds, error_buckets = run_valid_eval(
        model=model,
        tokenizer=tokenizer,
        dataset=valid_dataset,
        generation_config=gen_cfg,
        device=device,
    )

    save_json(metrics_out, metrics_v2)
    save_json(
        preds_out,
        {
            "args": {
                "dataset_path": cfg["dataset_path"],
                "model_name_or_path": cfg["model_name_or_path"],
                "checkpoint_dir": str(checkpoint_dir),
                "kge_embedding_path": cfg["kge_embedding_path"],
            },
            "generation_config": cfg["generation"],
            "metrics": metrics_v2,
            "prediction": preds,
        },
    )
    write_error_cases_md(error_md_out, error_buckets)

    metrics_week6 = None
    compare_cfg = cfg.get("compare_against", {})
    week6_path = compare_cfg.get("week6_valid_metrics")
    if week6_path and Path(week6_path).exists():
        metrics_week6 = load_json(Path(week6_path))

    candidate_report_week7 = None
    cand_path = compare_cfg.get("week7_candidate_report")
    if cand_path and Path(cand_path).exists():
        candidate_report_week7 = load_json(Path(cand_path))

    write_day6_markdown(
        path=day6_md,
        metrics_v2=metrics_v2,
        metrics_week6=metrics_week6,
        candidate_report_week7=candidate_report_week7,
        error_buckets=error_buckets,
    )

    print("Saved:")
    print(f"- {metrics_out}")
    print(f"- {preds_out}")
    print(f"- {error_md_out}")
    print(f"- {day6_md}")


if __name__ == "__main__":
    main()