#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(description="Adaptive launcher for week-5 backbone training.")
    p.add_argument("--model_name_or_path", default="meta-llama/Llama-3.2-3B")
    p.add_argument("--dataset_path", default="dataset/setting_a/08_backbone_ready")
    p.add_argument("--kge_embedding_path", default="dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt")
    p.add_argument("--output_dir", default="results/week5/backbone_llama32_3b_rgcn")
    p.add_argument("--run_name", default="week5_llama32_3b_rgcn")

    p.add_argument("--source_max_len", type=int, default=768)
    p.add_argument("--target_max_len", type=int, default=64)
    p.add_argument("--per_device_train_batch_size", type=int, default=1)
    p.add_argument("--gradient_accumulation_steps", type=int, default=8)
    p.add_argument("--learning_rate", type=float, default=2e-4)
    p.add_argument("--num_train_epochs", type=float, default=1.0)

    p.add_argument("--lora_r", type=int, default=32)
    p.add_argument("--lora_alpha", type=int, default=32)
    p.add_argument("--lora_dropout", type=float, default=0.1)

    p.add_argument("--bits", type=int, default=4)
    p.add_argument("--double_quant", action="store_true")
    p.add_argument("--seed", type=int, default=2025)

    p.add_argument("--save_steps", type=int, default=200)
    p.add_argument("--logging_steps", type=int, default=10)
    p.add_argument("--save_total_limit", type=int, default=2)
    p.add_argument("--save_safetensors", default="false")

    p.add_argument("--gnn_hidden_dim", type=int, default=128)
    p.add_argument("--gnn_num_hidden_layers", type=int, default=1)
    p.add_argument("--adapter_size", type=int, default=1024)

    p.add_argument("--prefer_bf16", action="store_true")
    p.add_argument("--gradient_checkpointing", action="store_true")

    p.add_argument("--snapshot_path", default="results/week5/backbone_llama32_3b_rgcn/config_snapshot.json")
    return p.parse_args()


def get_help_text() -> str:
    proc = subprocess.run(
        [sys.executable, "main.py", "--help"],
        capture_output=True,
        text=True,
    )
    return (proc.stdout or "") + "\n" + (proc.stderr or "")


def has_flag(help_text: str, flag: str) -> bool:
    return flag in help_text


def pick_first_supported(help_text: str, aliases: list[str]) -> str | None:
    for a in aliases:
        if has_flag(help_text, a):
            return a
    return None


def add_value_arg(cmd: list[str], help_text: str, aliases: list[str], value):
    flag = pick_first_supported(help_text, aliases)
    if flag is not None and value is not None:
        cmd.extend([flag, str(value)])
        return flag
    return None


def add_bool_arg(cmd: list[str], help_text: str, aliases: list[str], enabled: bool):
    flag = pick_first_supported(help_text, aliases)
    if flag is not None and enabled:
        cmd.append(flag)
        return flag
    return None


def main():
    args = parse_args()
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    Path(args.snapshot_path).parent.mkdir(parents=True, exist_ok=True)

    help_text = get_help_text()

    cmd = [sys.executable, "main.py"]
    used_flags = {}

    # core paths
    used_flags["model_name_or_path"] = add_value_arg(
        cmd, help_text, ["--model_name_or_path"], args.model_name_or_path
    )
    used_flags["dataset_path"] = add_value_arg(
        cmd, help_text, ["--dataset_path"], args.dataset_path
    )
    used_flags["kge_embedding_path"] = add_value_arg(
        cmd, help_text, ["--kge_embedding_path"], args.kge_embedding_path
    )
    used_flags["output_dir"] = add_value_arg(
        cmd, help_text, ["--output_dir"], args.output_dir
    )
    used_flags["run_name"] = add_value_arg(
        cmd, help_text, ["--run_name"], args.run_name
    )

    # training sizes
    used_flags["source_max_len"] = add_value_arg(
        cmd, help_text, ["--source_max_len", "--max_source_length"], args.source_max_len
    )
    used_flags["target_max_len"] = add_value_arg(
        cmd, help_text, ["--target_max_len", "--max_target_length"], args.target_max_len
    )
    used_flags["per_device_train_batch_size"] = add_value_arg(
        cmd, help_text, ["--per_device_train_batch_size"], args.per_device_train_batch_size
    )
    used_flags["gradient_accumulation_steps"] = add_value_arg(
        cmd, help_text, ["--gradient_accumulation_steps"], args.gradient_accumulation_steps
    )
    used_flags["learning_rate"] = add_value_arg(
        cmd, help_text, ["--learning_rate"], args.learning_rate
    )
    used_flags["num_train_epochs"] = add_value_arg(
        cmd, help_text, ["--num_train_epochs"], args.num_train_epochs
    )

    # LoRA / quant
    used_flags["lora_r"] = add_value_arg(
        cmd, help_text, ["--lora_r"], args.lora_r
    )
    used_flags["lora_alpha"] = add_value_arg(
        cmd, help_text, ["--lora_alpha"], args.lora_alpha
    )
    used_flags["lora_dropout"] = add_value_arg(
        cmd, help_text, ["--lora_dropout"], args.lora_dropout
    )
    used_flags["bits"] = add_value_arg(
        cmd, help_text, ["--bits"], args.bits
    )
    used_flags["double_quant"] = add_bool_arg(
        cmd, help_text, ["--double_quant"], args.double_quant
    )

    # graph branch
    used_flags["gnn_hidden_dim"] = add_value_arg(
        cmd, help_text, ["--gnn_hidden_dim"], args.gnn_hidden_dim
    )
    used_flags["gnn_num_hidden_layers"] = add_value_arg(
        cmd, help_text, ["--gnn_num_hidden_layers"], args.gnn_num_hidden_layers
    )
    used_flags["adapter_size"] = add_value_arg(
        cmd, help_text, ["--adapter_size", "--adapter_hidden_size"], args.adapter_size
    )

    # bookkeeping
    used_flags["seed"] = add_value_arg(
        cmd, help_text, ["--seed"], args.seed
    )
    used_flags["save_steps"] = add_value_arg(
        cmd, help_text, ["--save_steps"], args.save_steps
    )
    used_flags["logging_steps"] = add_value_arg(
        cmd, help_text, ["--logging_steps"], args.logging_steps
    )
    used_flags["save_total_limit"] = add_value_arg(
        cmd, help_text, ["--save_total_limit"], args.save_total_limit
    )
    used_flags["save_safetensors"] = add_value_arg(
        cmd, help_text, ["--save_safetensors"], args.save_safetensors
    )
    used_flags["report_to"] = add_value_arg(
        cmd, help_text, ["--report_to"], "none"
    )

    # precision
    if args.prefer_bf16:
        used_flags["bf16"] = add_bool_arg(cmd, help_text, ["--bf16"], True)
        if used_flags["bf16"] is None:
            used_flags["fp16"] = add_bool_arg(cmd, help_text, ["--fp16"], True)
        else:
            used_flags["fp16"] = None
    else:
        used_flags["fp16"] = add_bool_arg(cmd, help_text, ["--fp16"], True)
        if used_flags["fp16"] is None:
            used_flags["bf16"] = add_bool_arg(cmd, help_text, ["--bf16"], True)
        else:
            used_flags["bf16"] = None

    used_flags["gradient_checkpointing"] = add_bool_arg(
        cmd, help_text, ["--gradient_checkpointing"], args.gradient_checkpointing
    )

    # Some repos require these flags explicitly, some do not.
    used_flags["do_train"] = add_bool_arg(cmd, help_text, ["--do_train"], True)

    snapshot = {
        "help_text_head": help_text[:4000],
        "used_flags": used_flags,
        "final_command": cmd,
        "final_command_shell": " ".join(shlex.quote(x) for x in cmd),
        "notes": {
            "adaptive_mode": True,
            "goal": "First full week-5 backbone training run on server.",
        },
    }

    Path(args.snapshot_path).write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("=" * 80)
    print("Adaptive launch command")
    print("=" * 80)
    print(snapshot["final_command_shell"])
    print("=" * 80)
    print("Snapshot saved to:", args.snapshot_path)

    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()