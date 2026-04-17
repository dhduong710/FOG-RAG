from __future__ import annotations

import argparse
import json
import math
import os
import re
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Build week-4 resource plan from pilot artifacts.")
    parser.add_argument(
        "--train_results",
        type=Path,
        default=Path("results/week4/pilot_train_tinyllama_mock/train_results.json"),
    )
    parser.add_argument(
        "--trainer_state",
        type=Path,
        default=Path("results/week4/pilot_train_tinyllama_mock/trainer_state.json"),
    )
    parser.add_argument(
        "--infer_metrics",
        type=Path,
        default=Path("results/week4/pilot_infer_tinyllama_mock/metrics.json"),
    )
    parser.add_argument(
        "--timed_infer_log",
        type=Path,
        default=Path("runs/week4_pilot/day5_timed_infer.log"),
    )
    parser.add_argument(
        "--pilot_ready_dir",
        type=Path,
        default=Path("dataset/setting_a/07_pilot_ready"),
    )
    parser.add_argument(
        "--train_output_dir",
        type=Path,
        default=Path("results/week4/pilot_train_tinyllama_mock"),
    )
    parser.add_argument(
        "--infer_output_dir",
        type=Path,
        default=Path("results/week4/pilot_infer_tinyllama_mock"),
    )
    parser.add_argument(
        "--report_path",
        type=Path,
        default=Path("reports/week4/day6_resource_plan.md"),
    )
    parser.add_argument(
        "--dryrun_peak_vram_mb",
        type=float,
        default=4757.14,
        help="Peak GPU memory from day-2 dry run.",
    )
    parser.add_argument(
        "--full_train_samples",
        type=int,
        default=8388,
    )
    parser.add_argument(
        "--full_valid_samples",
        type=int,
        default=500,
    )
    parser.add_argument(
        "--full_test_samples",
        type=int,
        default=500,
    )
    parser.add_argument(
        "--per_device_train_batch_size",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--gradient_accumulation_steps",
        type=int,
        default=8,
    )
    parser.add_argument(
        "--seq_len",
        type=int,
        default=768,
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    )
    parser.add_argument(
        "--kge_path",
        type=str,
        default="dataset/setting_a/07_pilot_ready/mock_entity_embeddings.pt",
    )
    parser.add_argument(
        "--device_note",
        type=str,
        default="Current local GPU used in week-4 pilot",
    )
    return parser.parse_args()


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def sizeof_path(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    total = 0
    for root, _, files in os.walk(path):
        root = Path(root)
        for name in files:
            fp = root / name
            if fp.exists():
                total += fp.stat().st_size
    return total


def human_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024


def parse_time_to_seconds(text: str):
    """
    Handle forms like:
    - 0:48.56
    - 1:02:03
    - 12.34
    """
    text = text.strip()
    if not text:
        return None

    parts = text.split(":")
    try:
        if len(parts) == 3:
            h = float(parts[0])
            m = float(parts[1])
            s = float(parts[2])
            return h * 3600 + m * 60 + s
        if len(parts) == 2:
            m = float(parts[0])
            s = float(parts[1])
            return m * 60 + s
        if len(parts) == 1:
            return float(parts[0])
    except ValueError:
        return None
    return None


def parse_timed_infer_log(path: Path):
    if not path.exists():
        return {
            "elapsed_seconds": None,
            "max_rss_kb": None,
            "raw_elapsed_str": None,
        }

    text = path.read_text(encoding="utf-8", errors="ignore")

    elapsed_match = re.search(
        r"Elapsed \(wall clock\) time .*?:\s*([0-9:\.]+)",
        text
    )
    rss_match = re.search(
        r"Maximum resident set size \(kbytes\):\s*(\d+)",
        text
    )

    elapsed_str = elapsed_match.group(1) if elapsed_match else None
    elapsed_seconds = parse_time_to_seconds(elapsed_str) if elapsed_str else None
    max_rss_kb = int(rss_match.group(1)) if rss_match else None

    return {
        "elapsed_seconds": elapsed_seconds,
        "max_rss_kb": max_rss_kb,
        "raw_elapsed_str": elapsed_str,
    }


def main():
    args = parse_args()

    train_results = load_json(args.train_results)
    trainer_state = load_json(args.trainer_state)
    infer_metrics = load_json(args.infer_metrics)
    infer_timing = parse_timed_infer_log(args.timed_infer_log)

    global_step = trainer_state.get("global_step", None)
    train_runtime = train_results.get("train_runtime", None)
    train_steps_per_second = train_results.get("train_steps_per_second", None)
    train_samples_per_second = train_results.get("train_samples_per_second", None)
    train_loss = train_results.get("train_loss", None)

    sec_per_step = None
    if train_runtime is not None and global_step:
        sec_per_step = train_runtime / global_step
    elif train_steps_per_second:
        sec_per_step = 1.0 / train_steps_per_second

    effective_batch = args.per_device_train_batch_size * args.gradient_accumulation_steps
    full_epoch_steps = math.ceil(args.full_train_samples / effective_batch)

    full_epoch_seconds = None
    if sec_per_step is not None:
        full_epoch_seconds = full_epoch_steps * sec_per_step

    full_3epoch_seconds = full_epoch_seconds * 3 if full_epoch_seconds is not None else None
    full_5epoch_seconds = full_epoch_seconds * 5 if full_epoch_seconds is not None else None

    pilot_valid_n = infer_metrics["valid"]["num_samples"]
    pilot_test_n = infer_metrics["test"]["num_samples"]
    pilot_infer_n = pilot_valid_n + pilot_test_n
    full_infer_n = args.full_valid_samples + args.full_test_samples

    infer_seconds_total = infer_timing["elapsed_seconds"]
    infer_seconds_per_sample = (
        infer_seconds_total / pilot_infer_n
        if infer_seconds_total is not None and pilot_infer_n > 0
        else None
    )
    full_eval_seconds = (
        infer_seconds_per_sample * full_infer_n
        if infer_seconds_per_sample is not None
        else None
    )

    pilot_ready_size = sizeof_path(args.pilot_ready_dir)
    train_output_size = sizeof_path(args.train_output_dir)
    infer_output_size = sizeof_path(args.infer_output_dir)

    checkpoint_dirs = sorted(
        [p for p in args.train_output_dir.iterdir() if p.is_dir() and p.name.startswith("checkpoint-")]
    ) if args.train_output_dir.exists() else []
    checkpoint_sizes = [
        {"name": p.name, "bytes": sizeof_path(p), "human": human_size(sizeof_path(p))}
        for p in checkpoint_dirs
    ]

    # Choose final plan
    # Conservative because current pilot still uses TinyLlama + mock embeddings
    final_plan = "B"

    summary = {
        "current_pilot_config": {
            "model_name": args.model_name,
            "kge_path": args.kge_path,
            "seq_len": args.seq_len,
            "per_device_train_batch_size": args.per_device_train_batch_size,
            "gradient_accumulation_steps": args.gradient_accumulation_steps,
            "effective_batch": effective_batch,
            "device_note": args.device_note,
        },
        "observed_runtime_memory": {
            "dryrun_peak_vram_mb": args.dryrun_peak_vram_mb,
            "train_runtime_seconds": train_runtime,
            "train_steps_per_second": train_steps_per_second,
            "train_samples_per_second": train_samples_per_second,
            "sec_per_step": sec_per_step,
            "infer_elapsed_seconds_pilot_valid_test": infer_seconds_total,
            "infer_seconds_per_sample": infer_seconds_per_sample,
            "infer_max_rss_kb": infer_timing["max_rss_kb"],
        },
        "storage": {
            "pilot_ready_size": human_size(pilot_ready_size),
            "train_output_size": human_size(train_output_size),
            "infer_output_size": human_size(infer_output_size),
            "checkpoints": checkpoint_sizes,
        },
        "extrapolation_to_month2": {
            "full_train_samples": args.full_train_samples,
            "full_epoch_optimizer_steps": full_epoch_steps,
            "estimated_full_epoch_seconds": full_epoch_seconds,
            "estimated_full_epoch_minutes": (full_epoch_seconds / 60.0) if full_epoch_seconds is not None else None,
            "estimated_3epoch_hours": (full_3epoch_seconds / 3600.0) if full_3epoch_seconds is not None else None,
            "estimated_5epoch_hours": (full_5epoch_seconds / 3600.0) if full_5epoch_seconds is not None else None,
            "estimated_full_valid_test_seconds": full_eval_seconds,
            "estimated_full_valid_test_minutes": (full_eval_seconds / 60.0) if full_eval_seconds is not None else None,
        },
        "final_plan": final_plan,
        "note": (
            "These estimates are based on the week-4 debug setup "
            "(TinyLlama + mock entity embeddings + pilot-ready JSON), "
            "so they are engineering estimates, not final month-2 scientific run estimates."
        ),
    }

    args.report_path.parent.mkdir(parents=True, exist_ok=True)

    def fmt_num(x, digits=2):
        if x is None:
            return "N/A"
        return f"{x:.{digits}f}"

    checkpoint_lines = "\n".join(
        [f"- {x['name']}: {x['human']}" for x in checkpoint_sizes]
    ) if checkpoint_sizes else "- none"

    infer_time_note = (
        f"{fmt_num(infer_seconds_total)} sec total "
        f"({fmt_num(infer_seconds_per_sample, 4)} sec/sample)"
        if infer_seconds_total is not None
        else "N/A (run timed infer first)"
    )

    report = f"""# Day 6 Resource Plan

## 1. Current pilot configuration
- model: `{args.model_name}`
- kge path: `{args.kge_path}`
- sequence length: {args.seq_len}
- per-device train batch size: {args.per_device_train_batch_size}
- gradient accumulation steps: {args.gradient_accumulation_steps}
- effective batch size: {effective_batch}
- device: {args.device_note}

## 2. Observed runtime and memory
- day-2 dryrun peak VRAM: {fmt_num(args.dryrun_peak_vram_mb)} MB
- pilot train runtime: {fmt_num(train_runtime)} sec
- pilot train steps/sec: {fmt_num(train_steps_per_second, 3)}
- pilot train samples/sec: {fmt_num(train_samples_per_second, 3)}
- pilot train sec/step: {fmt_num(sec_per_step, 3)}
- pilot train loss: {fmt_num(train_loss, 6)}
- pilot infer runtime on valid+test pilot: {infer_time_note}
- pilot infer max RSS (host memory): {infer_timing["max_rss_kb"] if infer_timing["max_rss_kb"] is not None else "N/A"} KB

## 3. Storage snapshot
- pilot-ready dataset folder: {human_size(pilot_ready_size)}
- pilot train output folder: {human_size(train_output_size)}
- pilot infer output folder: {human_size(infer_output_size)}

### Checkpoint sizes
{checkpoint_lines}

## 4. Extrapolation to month 2
Assuming the same debug configuration and similar sequence-length behavior:

- full train samples: {args.full_train_samples}
- optimizer steps per epoch on full train: {full_epoch_steps}
- estimated full epoch runtime: {fmt_num((full_epoch_seconds / 60.0) if full_epoch_seconds is not None else None)} minutes
- estimated 3-epoch runtime: {fmt_num((full_3epoch_seconds / 3600.0) if full_3epoch_seconds is not None else None)} hours
- estimated 5-epoch runtime: {fmt_num((full_5epoch_seconds / 3600.0) if full_5epoch_seconds is not None else None)} hours
- estimated full valid+test inference runtime (500+500): {fmt_num((full_eval_seconds / 60.0) if full_eval_seconds is not None else None)} minutes

## 5. Interpretation
- The current debug configuration fits comfortably for week-4 pilot purposes.
- The current pilot confirms system stability, not scientific performance.
- Because the current run still uses TinyLlama + mock entity embeddings, these numbers are conservative engineering estimates only.
- The pilot does **not** justify jumping directly to a large month-2 run without one more cautious reproduction-style smoke run.

## 6. Final plan
### Recommended option: Plan {final_plan}
**Plan B**: pilot fit is good enough, but month 2 should start with a conservative reproduction configuration before scaling.

### Main month-2 recommendation
- primary month-2 goal: reproduce the DrKGC-style backbone on full Setting A first
- start from an original-style conservative config
- keep batch size small
- keep gradient accumulation enabled
- do not add fuzzy or safety modules before backbone stability is confirmed

### Practical recommendation
- debug model: keep the current TinyLlama-based pipeline for fast debugging
- month-2 main run: move to the intended backbone gradually, not in one jump
- first full-A smoke run in month 2 should be short and checkpoint-safe
- only after that should you launch a longer reproduction run

## 7. Risks to watch
- VRAM may rise substantially when replacing the debug model or mock embeddings
- preprocessing time may become a bottleneck on full data
- checkpoint storage can grow if save frequency is too aggressive
- the current pilot infer is optimistic because the coarse ranker is still mock

## 8. Decision
- Current judgment: **ready to enter month 2 with Plan B**
- Not recommended: jumping directly to a heavy full run today
"""

    args.report_path.write_text(report, encoding="utf-8")

    summary_path = args.report_path.with_suffix(".json")
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    infer_summary_path = args.infer_output_dir / "infer_timing_summary.json"
    with infer_summary_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "pilot_valid_test_total_samples": pilot_infer_n,
                "elapsed_seconds": infer_seconds_total,
                "seconds_per_sample": infer_seconds_per_sample,
                "max_rss_kb": infer_timing["max_rss_kb"],
                "raw_elapsed_str": infer_timing["raw_elapsed_str"],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Saved report: {args.report_path}")
    print(f"Saved summary json: {summary_path}")
    print(f"Saved infer timing json: {infer_summary_path}")


if __name__ == "__main__":
    main()