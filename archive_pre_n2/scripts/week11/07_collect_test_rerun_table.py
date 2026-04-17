import json
from pathlib import Path

ROWS = {
    "Backbone": Path("results/week11_test/backbone_test"),
    "+ Ontology": Path("results/week11_test/ontology_test"),
    "+ Ontology + Hard": Path("results/week11_test/hard_main_test"),
    "+ Ontology + Soft": Path("results/week11_test/soft_best_test"),
}

print("=" * 120)
print("FINAL TEST RERUN SUMMARY")
print("=" * 120)
print(f"{'Variant':30s} {'MRR':>10s} {'Hits@1':>10s} {'Hits@3':>10s} {'Hits@10':>10s}")

for name, folder in ROWS.items():
    path = folder / "ranking_metrics_test_rerun_clean.json"
    metrics = json.loads(path.read_text(encoding="utf-8"))
    print(
        f"{name:30s} "
        f"{metrics['mrr']:10.4f} "
        f"{metrics['hits1']:10.4f} "
        f"{metrics['hits3']:10.4f} "
        f"{metrics['hits10']:10.4f}"
    )