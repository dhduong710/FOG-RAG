from __future__ import annotations

import json
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path


CFG_PATH = Path("configs/week12A/rgcn_ranker_ft.yaml")
OUT_DIR = Path("dataset/setting_a/21_ranker_rescue")
LOG_DIR = Path("results/week12A/build_candidates")


def find_builder() -> Path:
    candidates = [
        Path("scripts/week7/04_build_candidate_json_v2.py"),
        Path("scripts/week6/04_build_real_candidate_json.py"),
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(
        "Cannot find candidate-builder script. Expected week7 or week6 builder."
    )


def build_cmd(builder: Path) -> list[str]:
    return [
        sys.executable, 
        str(builder), 
        "--score-dir", str(OUT_DIR), 
        "--k", "20", 
        "--report-dir", "reports/week12A"
    ]


def main() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    builder = find_builder()
    cmd = build_cmd(builder)

    launch_log = LOG_DIR / "launcher_build.log"
    launch_meta = LOG_DIR / "launch_meta.json"

    meta = {
        "timestamp_start": datetime.now().isoformat(),
        "builder": str(builder),
        "config": str(CFG_PATH),
        "command": cmd,
        "cwd": str(Path.cwd()),
        "expected_outputs": {
            "train_top20_raw": str(OUT_DIR / "train_top20_raw.json"),
            "valid_top20_raw": str(OUT_DIR / "valid_top20_raw.json"),
            "test_top20_raw": str(OUT_DIR / "test_top20_raw.json"),
            "train_top20_drkgc_ready": str(OUT_DIR / "train_top20_drkgc_ready.json"),
            "valid_top20_drkgc_ready": str(OUT_DIR / "valid_top20_drkgc_ready.json"),
            "test_top20_drkgc_ready": str(OUT_DIR / "test_top20_drkgc_ready.json"),
        },
    }

    with launch_meta.open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print("Launching candidate builder:")
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
        raise SystemExit(f"Candidate builder failed with return code {ret}")

    expected = [
        OUT_DIR / "train_top20_raw.json",
        OUT_DIR / "valid_top20_raw.json",
        OUT_DIR / "test_top20_raw.json",
        OUT_DIR / "train_top20_drkgc_ready.json",
        OUT_DIR / "valid_top20_drkgc_ready.json",
        OUT_DIR / "test_top20_drkgc_ready.json",
    ]
    missing = [str(p) for p in expected if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing candidate files:\n" + "\n".join(missing))

    print("Candidate build finished successfully.")
    for p in expected:
        print("-", p)


if __name__ == "__main__":
    main()