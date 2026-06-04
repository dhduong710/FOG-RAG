from __future__ import annotations

import json
from pathlib import Path

import yaml


def main() -> None:
    cfg_path = Path("configs/week12A/rgcn_ranker_ft.yaml")
    if not cfg_path.exists():
        raise FileNotFoundError(f"Missing config: {cfg_path}")

    with cfg_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    required_paths = [
        cfg["split_dir"],
        cfg["graph_path"],
    ]

    missing = [p for p in required_paths if not Path(p).exists()]
    if missing:
        print("Missing required inputs:")
        for p in missing:
            print(" -", p)
        raise SystemExit(1)

    checks = {
        "target_relation": cfg["target_relation"],
        "candidate_universe": cfg["candidate_universe"],
        "k": cfg["k"],
        "embedding_dim": cfg["model"]["embedding_dim"],
        "hidden_dim": cfg["model"]["hidden_dim"],
        "num_layers": cfg["model"]["num_layers"],
        "learning_rate": cfg["training"]["learning_rate"],
        "negatives_per_query": cfg["training"]["negatives_per_query"],
        "decision_split": cfg["decision_split"],
        "output_dir": cfg["output"]["out_dir"],
    }

    assert checks["target_relation"] == "indication"
    assert checks["candidate_universe"] == "drug_only"
    assert checks["k"] == 20
    assert checks["decision_split"] == "valid"

    out_dir = Path("results/week12A/ranker_design")
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / "config_snapshot.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(checks, f, indent=2, ensure_ascii=False)

    print("Config validation passed.")
    print(json.dumps(checks, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()