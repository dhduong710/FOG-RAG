from __future__ import annotations

import json
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml


CFG_PATH = Path("configs/week12A/rgcn_ranker_ft.yaml")
OUT_DIR = Path("dataset/setting_a/21_ranker_rescue")
LOG_DIR = Path("results/week12A/ranker_ft_train")


def find_trainer() -> Path:
    candidates = [
        Path("scripts/week7/02_train_rgcn_ranker_v2.py"),
        Path("scripts/week6/02_train_rgcn_ranker.py"),
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(
        "Cannot find an existing R-GCN trainer script. "
        "Expected one of: scripts/week7/02_train_rgcn_ranker_v2.py or scripts/week6/02_train_rgcn_ranker.py"
    )


def load_cfg() -> dict:
    if not CFG_PATH.exists():
        raise FileNotFoundError(f"Missing config: {CFG_PATH}")
    with CFG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_cmd(trainer: Path) -> list[str]:
    # Default assumption:
    # your existing trainer accepts: python trainer.py --config path/to/yaml
    #
    # If your old trainer uses a different CLI, change ONLY this function.
    return [sys.executable, str(trainer), "--config", str(CFG_PATH)]


def main() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    cfg = load_cfg()
    trainer = find_trainer()
    cmd = build_cmd(trainer)

    launch_log = LOG_DIR / "launcher_train.log"
    launch_meta = LOG_DIR / "launch_meta.json"

    meta = {
        "timestamp_start": datetime.now().isoformat(),
        "trainer": str(trainer),
        "config": str(CFG_PATH),
        "command": cmd,
        "cwd": str(Path.cwd()),
        "expected_outputs": {
            "checkpoint": str(OUT_DIR / "rgcn_ranker_v2_checkpoint.pt"),
            "train_log": str(OUT_DIR / "ranker_v2_train_log.jsonl"),
            "meta": str(OUT_DIR / "ranker_v2_meta.json"),
        },
    }

    with launch_meta.open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print("Launching trainer:")
    print(" ".join(shlex.quote(x) for x in cmd))
    print(f"Logging to: {launch_log}")

    with launch_log.open("w", encoding="utf-8") as log_f:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            print(line, end="")
            log_f.write(line)
        ret = proc.wait()

    meta["timestamp_end"] = datetime.now().isoformat()
    meta["return_code"] = ret

    with launch_meta.open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    if ret != 0:
        raise SystemExit(f"Trainer failed with return code {ret}")

    ckpt = OUT_DIR / "rgcn_ranker_v2_checkpoint.pt"
    train_log = OUT_DIR / "ranker_v2_train_log.jsonl"
    out_meta = OUT_DIR / "ranker_v2_meta.json"

    missing = [str(p) for p in [ckpt, train_log, out_meta] if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "Training finished but some expected outputs are missing:\n"
            + "\n".join(missing)
        )

    print("Training finished successfully.")
    print(f"Checkpoint: {ckpt}")
    print(f"Train log : {train_log}")
    print(f"Meta      : {out_meta}")


if __name__ == "__main__":
    main()