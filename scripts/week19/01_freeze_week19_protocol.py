from pathlib import Path
import json
import sys
from datetime import datetime

ROOT = Path(".").resolve()

def meta(path_str: str):
    p = ROOT / path_str
    return {
        "path": path_str,
        "exists": p.exists(),
        "is_file": p.is_file(),
        "size_bytes": p.stat().st_size if p.exists() and p.is_file() else None,
    }

def try_load_json(path_str: str):
    p = ROOT / path_str
    if not p.exists():
        return {"path": path_str, "loaded": False, "error": "missing"}
    try:
        with p.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        summary = {
            "path": path_str,
            "loaded": True,
            "json_kind": type(obj).__name__,
        }
        if isinstance(obj, dict):
            summary["top_keys"] = list(obj.keys())[:20]
        elif isinstance(obj, list):
            summary["num_rows"] = len(obj)
            if len(obj) > 0 and isinstance(obj[0], dict):
                summary["top_keys"] = list(obj[0].keys())[:20]
        return summary
    except Exception as e:
        return {"path": path_str, "loaded": False, "error": repr(e)}

required_week18 = [
    "results/week18/retrieval_main_lock_report.json",
    "results/week18/novelty2_valid_main_table.json",
    "results/week18/novelty2_valid_ablation.json",
    "results/week18/encoder_probe_appendix_note.json",
    "results/week18/test_readiness_manifest.json",
    "results/week18/week18_go_decision.json",
]

required_valid_eval = [
    "dataset/setting_b/07_n2_eval_valid/valid_backbone_raw_eval.json",
    "dataset/setting_b/07_n2_eval_valid/valid_ontology_raw_eval.json",
    "dataset/setting_b/07_n2_eval_valid/valid_soft_support_raw_eval.json",
    "dataset/setting_b/07_n2_eval_valid/valid_retrieval_main_eval.json",
]

missing_test_artifacts = [
    "dataset/setting_a/26_n2_soft_support/test_top20_soft_support_main.json",
    "dataset/setting_a/27_n2_fuzzy_retrieval/test_fuzzy_retrieval_main.json",
]

future_eval_ready_outputs = [
    "dataset/setting_b/08_n2_eval_test/test_backbone_raw_eval.json",
    "dataset/setting_b/08_n2_eval_test/test_ontology_raw_eval.json",
    "dataset/setting_b/08_n2_eval_test/test_soft_support_raw_eval.json",
    "dataset/setting_b/08_n2_eval_test/test_retrieval_main_eval.json",
]

all_required = required_week18 + required_valid_eval
checks = [meta(p) for p in all_required]
missing_required = [x["path"] for x in checks if not x["exists"]]

status = "READY_FOR_LOCKED_TEST_WEEK" if not missing_required else "BLOCKED_MISSING_WEEK18_INPUTS"

protocol = {
    "week": 19,
    "generated_at_utc": datetime.utcnow().isoformat() + "Z",
    "status": status,
    "theme": "Build missing main test artifacts then run official locked test",
    "week_type": "official_locked_test_week",
    "main_success_criterion": (
        "Under the locked reviewer-safe test protocol, "
        "the frozen retrieval main row remains the strongest current row of Novelty 2."
    ),
    "row_roles": {
        "reference_row": "backbone_raw",
        "negative_control": "ontology_raw",
        "candidate_stage_intermediate": "soft_support_raw",
        "main_row": "soft_support_fuzzy_retrieval_main",
        "appendix_only": ["soft_support_fuzzy_encoder_probe_v0"],
    },
    "frozen_logic": {
        "candidate_formula_change_allowed": False,
        "retrieval_variant_change_allowed": False,
        "encoder_promotion_allowed": False,
        "new_novelty_allowed": False,
        "row_role_change_allowed": False,
    },
    "metric_policy": {
        "main_metric": "mrr_at20",
        "rr_rule": "1/rank if rank <= 20 else 0",
        "gold_rank_out_of_top20": 21,
        "secondary_metrics": [
            "gold_present_rate",
            "mrr_present_only",
            "hits1_at20",
            "hits3_at20",
            "hits10_at20",
            "avg_gold_rank",
        ],
    },
    "decision_split": "test",
    "week18_prerequisite_checks": checks,
    "week18_json_summaries": [try_load_json(p) for p in required_week18 + required_valid_eval],
    "missing_test_artifacts_to_build": missing_test_artifacts,
    "future_eval_ready_outputs": future_eval_ready_outputs,
    "allowed_actions_week19": [
        "build soft_support_raw_test",
        "build retrieval_main_test",
        "build test eval-ready package",
        "run official locked test",
        "build test main table",
        "build test ablation",
        "review test cases",
        "freeze paper-facing row",
    ],
    "forbidden_actions_week19": [
        "reopen candidate-stage",
        "change soft_support_raw formula",
        "change retrieval main variant",
        "promote encoder to main path",
        "add new novelty",
        "change reviewer-safe metric policy",
        "change row roles frozen on valid",
    ],
    "expected_day1_outputs": [
        "results/week19/test_protocol_freeze.json",
        "reports/week19/day1_protocol_freeze.md",
    ],
}

results_dir = ROOT / "results/week19"
reports_dir = ROOT / "reports/week19"
results_dir.mkdir(parents=True, exist_ok=True)
reports_dir.mkdir(parents=True, exist_ok=True)

json_path = results_dir / "test_protocol_freeze.json"
with json_path.open("w", encoding="utf-8") as f:
    json.dump(protocol, f, ensure_ascii=False, indent=2)

md_lines = []
md_lines.append("# Day 1 Protocol Freeze — Week 19")
md_lines.append("")
md_lines.append(f"- status: **{protocol['status']}**")
md_lines.append(f"- theme: **{protocol['theme']}**")
md_lines.append(f"- decision split: **{protocol['decision_split']}**")
md_lines.append("")
md_lines.append("## 1. Locked row roles")
for k, v in protocol["row_roles"].items():
    md_lines.append(f"- {k}: `{v}`")
md_lines.append("")
md_lines.append("## 2. Metric policy")
md_lines.append(f"- main_metric: `{protocol['metric_policy']['main_metric']}`")
md_lines.append(f"- rr_rule: `{protocol['metric_policy']['rr_rule']}`")
md_lines.append(f"- gold_rank_out_of_top20: `{protocol['metric_policy']['gold_rank_out_of_top20']}`")
md_lines.append("- secondary_metrics:")
for m in protocol["metric_policy"]["secondary_metrics"]:
    md_lines.append(f"  - `{m}`")
md_lines.append("")
md_lines.append("## 3. Required week18 prerequisites")
for item in protocol["week18_prerequisite_checks"]:
    mark = "OK" if item["exists"] else "MISSING"
    md_lines.append(f"- [{mark}] `{item['path']}`")
md_lines.append("")
md_lines.append("## 4. Missing test artifacts to build next")
for p in protocol["missing_test_artifacts_to_build"]:
    md_lines.append(f"- `{p}`")
md_lines.append("")
md_lines.append("## 5. Forbidden changes this week")
for x in protocol["forbidden_actions_week19"]:
    md_lines.append(f"- {x}")
md_lines.append("")
md_lines.append("## 6. Day-1 conclusion")
if not missing_required:
    md_lines.append(
        "Week 19 is officially frozen as a locked-test week. "
        "Next steps are to build `soft_support_raw_test` and `retrieval_main_test` "
        "without changing formula, retrieval variant, or row roles."
    )
else:
    md_lines.append(
        "Week 19 is currently BLOCKED because required week18 inputs are missing. "
        "Fix the missing files below before running any locked test."
    )
    for p in missing_required:
        md_lines.append(f"- missing: `{p}`")

report_path = reports_dir / "day1_protocol_freeze.md"
report_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

print("=" * 80)
print("Wrote:", json_path)
print("Wrote:", report_path)
print("status =", status)

if missing_required:
    print("missing_required_inputs:")
    for p in missing_required:
        print(" -", p)
    sys.exit(1)

print("All required week18 prerequisites exist.")
