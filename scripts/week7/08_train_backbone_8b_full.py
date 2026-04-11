#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Week 7 / capacity check
Train 8B full rerun on:
  dataset/setting_a/12_backbone_ready_ranker_v2

This keeps the same backbone path as earlier weeks and only scales the LLM.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict

import yaml


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def add_bool_arg(cmd: list[str], flag: str, value: bool):
    cmd.extend([flag, "True" if value else "False"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to configs/week7/backbone_valid_v2_8b.yaml")
    args = parser.parse_args()

    cfg = load_yaml(Path(args.config))

    output_dir = Path(cfg["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    log_path = Path("reports/week7/day6_8b_train.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)

    config_snapshot_path = output_dir / "config_snapshot.json"
    with config_snapshot_path.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

    cmd = [
        "python", "main.py",
        "--dataset_path", cfg["dataset_path"],
        "--model_name_or_path", cfg["model_name_or_path"],
        "--model_type", cfg["model_type"],
        "--kge_embedding_path", cfg["kge_embedding_path"],
        "--source_max_len", str(cfg["source_max_len"]),
        "--target_max_len", str(cfg["target_max_len"]),
        "--output_dir", cfg["output_dir"],
        "--num_train_epochs", str(cfg["num_train_epochs"]),
        "--per_device_train_batch_size", str(cfg["per_device_train_batch_size"]),
        "--gradient_accumulation_steps", str(cfg["gradient_accumulation_steps"]),
        "--dataloader_num_workers", str(cfg["dataloader_num_workers"]),
        "--learning_rate", str(cfg["learning_rate"]),
        "--lora_r", str(cfg["lora_r"]),
        "--lora_alpha", str(cfg["lora_alpha"]),
        "--lora_dropout", str(cfg["lora_dropout"]),
        "--optim", cfg["optim"],
        "--lr_scheduler_type", cfg["lr_scheduler_type"],
        "--warmup_ratio", str(cfg["warmup_ratio"]),
        "--logging_steps", str(cfg["logging_steps"]),
        "--save_steps", str(cfg["save_steps"]),
        "--save_total_limit", str(cfg["save_total_limit"]),
        "--save_safetensors", "False",
        "--gradient_checkpointing", "True",
        "--save_strategy", "steps",
        "--logging_strategy", "steps",
        "--evaluation_strategy", "no",
        "--report_to", cfg["report_to"],
        "--seed", str(cfg["seed"]),
    ]

    # overwrite / trainer behavior
    add_bool_arg(cmd, "--overwrite_output_dir", bool(cfg.get("overwrite_output_dir", True)))
    add_bool_arg(cmd, "--remove_unused_columns", False)

    # quantization
    if bool(cfg.get("use_quant", False)):
        add_bool_arg(cmd, "--use_quant", True)
        cmd.extend(["--bits", str(cfg.get("bits", 4))])
        add_bool_arg(cmd, "--double_quant", bool(cfg.get("double_quant", True)))
        cmd.extend(["--quant_type", str(cfg.get("quant_type", "nf4"))])

    # precision
    precision = str(cfg.get("precision", "bf16")).lower()
    if precision == "bf16":
        add_bool_arg(cmd, "--bf16", True)
    elif precision == "fp16":
        add_bool_arg(cmd, "--fp16", True)

    env = os.environ.copy()
    env["TOKENIZERS_PARALLELISM"] = "false"

    with log_path.open("w", encoding="utf-8") as f:
        f.write("# Command\n")
        f.write(" ".join(shlex.quote(x) for x in cmd) + "\n\n")
        f.write("# Output\n")
        f.flush()

        proc = subprocess.run(
            cmd,
            stdout=f,
            stderr=subprocess.STDOUT,
            env=env,
            text=True,
            check=False,
        )

    if proc.returncode != 0:
        raise RuntimeError(
            f"8B training failed with return code {proc.returncode}. "
            f"See log: {log_path}"
        )

    print(f"[OK] 8B training finished. Log: {log_path}")
    print(f"[OK] Config snapshot: {config_snapshot_path}")


if __name__ == "__main__":
    main()