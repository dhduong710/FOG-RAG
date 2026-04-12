#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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


def maybe_bool_args(cmd: list[str], flag: str, value: bool):
    cmd.extend([flag, "True" if value else "False"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to configs/week8/backbone_valid_posthoc_3b.yaml")
    args = parser.parse_args()

    cfg = load_yaml(Path(args.config))

    output_dir = Path(cfg["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    log_path = Path("reports/week8/day5_train_backbone_posthoc_3b.log")
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
        "--save_strategy", "steps",
        "--logging_strategy", "steps",
        "--evaluation_strategy", "no",
        "--report_to", cfg["report_to"],
        "--seed", str(cfg["seed"]),
    ]

    maybe_bool_args(cmd, "--overwrite_output_dir", bool(cfg.get("overwrite_output_dir", True)))
    maybe_bool_args(cmd, "--remove_unused_columns", False)

    precision = str(cfg.get("precision", "fp16")).lower()
    if precision == "fp16":
        maybe_bool_args(cmd, "--fp16", True)
    elif precision == "bf16":
        maybe_bool_args(cmd, "--bf16", True)

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
            f"Posthoc 3B training failed with return code {proc.returncode}. "
            f"See log: {log_path}"
        )

    print(f"[OK] Training finished. Log: {log_path}")
    print(f"[OK] Config snapshot: {config_snapshot_path}")


if __name__ == "__main__":
    main()