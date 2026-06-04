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
LOG_DIR = Path("results/week12A/score_queries")


def find_scorer() -> Path:
    candidates = [
        Path("scripts/week7/03_score_queries_v2.py"),
        Path("scripts/week6/03_score_queries_with_rgcn.py"),
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(
        "Cannot find query scorer script. Expected week7 or week6 scorer."
    )


def build_cmd(scorer: Path) -> list[str]:
    # Default assumption: scorer.py --config configs/week12A/rgcn_ranker_ft.yaml
    return [sys.executable, str(scorer), "--config", str(CFG_PATH)]


def main() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    scorer = find_scorer()
    cmd = build_cmd(scorer)

    launch_log = LOG_DIR / "launcher_score.log"
    launch_meta = LOG_DIR / "launch_meta.json"

    meta = {
        "timestamp_start": datetime.now().isoformat(),
        "scorer": str(scorer),
        "config": str(CFG_PATH),
        "command": cmd,
        "cwd": str(Path.cwd()),
        "expected_outputs": {
            "train_scores": str(OUT_DIR / "train_scores.pt"),
            "valid_scores": str(OUT_DIR / "valid_scores.pt"),
            "test_scores": str(OUT_DIR / "test_scores.pt"),
        },
    }

    with launch_meta.open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print("Launching scorer:")
    print(" ".join(shlex.quote(x) for x in cmd))

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
        raise SystemExit(f"Scorer failed with return code {ret}")

    expected = [
        OUT_DIR / "train_scores.pt",
        OUT_DIR / "valid_scores.pt",
        OUT_DIR / "test_scores.pt",
    ]
    missing = [str(p) for p in expected if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing score files:\n" + "\n".join(missing))

    print("Scoring finished successfully.")
    for p in expected:
        print("-", p)


if __name__ == "__main__":
    main()