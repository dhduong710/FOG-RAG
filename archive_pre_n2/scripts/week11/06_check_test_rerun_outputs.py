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

    pred_path = base / "prediction_test_rerun_clean.json"
    metric_path = base / "ranking_metrics_test_rerun_clean.json"

    assert pred_path.exists(), f"Missing {pred_path}"
    assert metric_path.exists(), f"Missing {metric_path}"

    pred = json.loads(pred_path.read_text(encoding="utf-8"))
    metrics = json.loads(metric_path.read_text(encoding="utf-8"))

    first_triple = pred["prediction"][0]["triple"] if pred["prediction"] else None
    first_pred = pred["prediction"][0]["pred"] if pred["prediction"] else None
    first_top5 = pred["prediction"][0]["rank_entities"][:5] if pred["prediction"] else None

    print("metrics =", metrics)
    print("first triple =", first_triple)
    print("first pred   =", first_pred)
    print("first top5   =", first_top5)