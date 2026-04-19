from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(".").resolve()

BACKBONE_METRICS = ROOT / "results/week20/ranking_metrics_test_backbone_raw_e2e.json"
SOFT_METRICS = ROOT / "results/week20/ranking_metrics_test_soft_support_raw_e2e.json"

BACKBONE_PRED = ROOT / "results/week20/prediction_test_backbone_raw_e2e.json"
SOFT_PRED = ROOT / "results/week20/prediction_test_soft_support_raw_e2e.json"

OUT_JSON = ROOT / "results/week20/e2e_backbone_soft_summary.json"
OUT_MD = ROOT / "reports/week20/day3_run_backbone_and_soft.md"

def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def main():
    backbone_metrics = load_json(BACKBONE_METRICS)
    soft_metrics = load_json(SOFT_METRICS)

    backbone_pred = load_json(BACKBONE_PRED)
    soft_pred = load_json(SOFT_PRED)

    summary = {
        "week": 20,
        "stage": "run_e2e_backbone_and_soft",
        "status": "BUILT",
        "backbone_raw": {
            "metrics": backbone_metrics,
            "num_prediction_rows": len(backbone_pred["prediction"]),
            "sample0": {
                "target": backbone_pred["prediction"][0]["target"],
                "pred": backbone_pred["prediction"][0]["pred"],
                "pred_rank": backbone_pred["prediction"][0]["pred_rank"],
            },
        },
        "soft_support_raw": {
            "metrics": soft_metrics,
            "num_prediction_rows": len(soft_pred["prediction"]),
            "sample0": {
                "target": soft_pred["prediction"][0]["target"],
                "pred": soft_pred["prediction"][0]["pred"],
                "pred_rank": soft_pred["prediction"][0]["pred_rank"],
            },
        },
        "delta_soft_minus_backbone": {
            "delta_mrr": round(float(soft_metrics["mrr"]) - float(backbone_metrics["mrr"]), 8),
            "delta_hits1": round(float(soft_metrics["hits1"]) - float(backbone_metrics["hits1"]), 8),
            "delta_hits3": round(float(soft_metrics["hits3"]) - float(backbone_metrics["hits3"]), 8),
            "delta_hits10": round(float(soft_metrics["hits10"]) - float(backbone_metrics["hits10"]), 8),
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    md = []
    md.append("# Day 3 — E2E infer for backbone_raw and soft_support_raw")
    md.append("")
    md.append(f"- status: **{summary['status']}**")
    md.append("")
    md.append("## 1. backbone_raw")
    for k, v in summary["backbone_raw"]["metrics"].items():
        md.append(f"- {k}: `{v}`")
    md.append(f"- num_prediction_rows: `{summary['backbone_raw']['num_prediction_rows']}`")
    md.append("")
    md.append("## 2. soft_support_raw")
    for k, v in summary["soft_support_raw"]["metrics"].items():
        md.append(f"- {k}: `{v}`")
    md.append(f"- num_prediction_rows: `{summary['soft_support_raw']['num_prediction_rows']}`")
    md.append("")
    md.append("## 3. delta_soft_minus_backbone")
    for k, v in summary["delta_soft_minus_backbone"].items():
        md.append(f"- {k}: `{v}`")
    md.append("")
    md.append("## 4. Day-3 conclusion")
    md.append(
        "Ran frozen end-to-end test inference for backbone_raw and soft_support_raw "
        "using the recovered week20 primary checkpoint."
    )

    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
