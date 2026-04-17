import json
from pathlib import Path

TARGETS = {
    "backbone": Path("results/week11_test/backbone_test"),
    "ontology": Path("results/week11_test/ontology_test"),
    "hard_main": Path("results/week11_test/hard_main_test"),
    "soft_best": Path("results/week11_test/soft_best_test"),
}

for name, base in TARGETS.items():
    print("=" * 100)
    print(name)

    for split in ["valid", "test"]:
        pred_path = base / f"prediction_{split}_rerun.json"
        metric_path = base / f"ranking_metrics_{split}_rerun.json"

        assert pred_path.exists(), f"Missing {pred_path}"
        assert metric_path.exists(), f"Missing {metric_path}"

        pred = json.loads(pred_path.read_text(encoding="utf-8"))
        metrics = json.loads(metric_path.read_text(encoding="utf-8"))

        first_triple = pred["prediction"][0]["triple"] if pred["prediction"] else None

        print(f"[{split}] metrics = {metrics}")
        print(f"[{split}] first triple = {first_triple}")