from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(".").resolve()

INPUTS = {
    "week17_go_decision": ROOT / "results/week17/week17_go_decision.json",
    "valid_main_table": ROOT / "results/week18/novelty2_valid_main_table.json",
    "valid_ablation": ROOT / "results/week18/novelty2_valid_ablation.json",
    "test_readiness": ROOT / "results/week18/test_readiness_manifest.json",
}

OUT_JSON = ROOT / "results/week18/encoder_probe_appendix_note.json"
OUT_MD = ROOT / "reports/week18/day6_row_lock_and_appendix.md"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_row(main_table: dict, canonical_row_name: str) -> dict:
    for row in main_table["rows"]:
        if row["canonical_row_name"] == canonical_row_name:
            return row
    raise KeyError(f"Cannot find row: {canonical_row_name}")


def main():
    week17 = load_json(INPUTS["week17_go_decision"])
    main_table = load_json(INPUTS["valid_main_table"])
    ablation = load_json(INPUTS["valid_ablation"])
    readiness = load_json(INPUTS["test_readiness"])

    backbone = find_row(main_table, "backbone_raw")
    ontology = find_row(main_table, "ontology_raw")
    soft = find_row(main_table, "soft_support_raw")
    retrieval = find_row(main_table, "soft_support_fuzzy_retrieval_main")
    appendix_probe = ablation["appendix_probe_summary"]

    result = {
        "week": 18,
        "day": 6,
        "mode": "row_lock_and_appendix_positioning",
        "row_positioning": {
            "reference_row": {
                "row_name": "backbone_raw",
                "role": "reference",
                "ranking_metrics": backbone["ranking_metrics"],
            },
            "negative_control_row": {
                "row_name": "ontology_raw",
                "role": "negative_control",
                "ranking_metrics": ontology["ranking_metrics"],
                "reason": "binary/hard ontology support is brittle under raw/no-injection",
            },
            "candidate_stage_main_intermediate": {
                "row_name": "soft_support_raw",
                "role": "candidate_stage_main_intermediate",
                "ranking_metrics": soft["ranking_metrics"],
            },
            "main_row_after_week17": {
                "row_name": "soft_support_fuzzy_retrieval_main",
                "role": "main_row_after_week17",
                "ranking_metrics": retrieval["ranking_metrics"],
                "graph_diagnostics": retrieval["row_specific_diagnostics"],
                "reason": "preserves reviewer-safe ranking metrics over soft_support_raw while improving graph/evidence packaging",
            },
        },
        "appendix_positioning": {
            "row_name": "soft_support_fuzzy_encoder_probe_v0",
            "role": "supporting_appendix_only",
            "decision": appendix_probe["decision"],
            "probe_summary": appendix_probe,
            "reason": "controlled encoder-readiness probe was conducted, but not promoted due to weak bridge signal and worse ranking outcomes than retrieval main",
        },
        "paper_narrative_lock": [
            "The paper should present backbone_raw as the reference row.",
            "The paper should present ontology_raw as a negative control rather than a competitive row.",
            "The paper should present soft_support_raw as the candidate-stage main intermediate row.",
            "The paper should present soft_support_fuzzy_retrieval_main as the strongest current frozen row of Novelty 2.",
            "The paper should present soft_support_fuzzy_encoder_probe_v0 as a supporting deferred direction in the appendix, not as a promoted main stage.",
        ],
        "current_limitations": [
            "The encoder probe does not justify promotion to a main stage.",
            "The project is not yet ready for official locked test because test-side soft_support_raw and retrieval_main artifacts are still missing.",
        ],
        "next_step_recommendation": {
            "week17_dependency_ok": (
                week17["final_decision"] == "NO_GO_FOR_FULL_ENCODER_STAGE"
                and week17["main_row_after_week17"] == "soft_support_fuzzy_retrieval_main"
            ),
            "test_readiness_status": readiness["decision"],
            "recommended_direction": (
                "keep retrieval main as the main row, keep encoder as appendix/supporting only, and build the missing main test artifacts before official locked test"
            ),
        },
        "paper_ready_paragraph": (
            "After freezing the candidate-stage and retrieval-stage rows, we retained "
            "soft_support_fuzzy_retrieval_main as the strongest current row of Novelty 2 "
            "under the raw/no-injection valid protocol. We also conducted a controlled "
            "encoder-readiness probe, but the probe did not provide sufficient gain over "
            "the retrieval main row. Therefore, we position the encoder probe as a "
            "supporting deferred direction rather than promoting it to a main stage."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)

    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    lines = []
    lines.append("# Week 18 Day 6 — Row Lock and Appendix Positioning\n")
    lines.append("## Main positioning")
    lines.append(f"- Reference row: `backbone_raw`")
    lines.append(f"- Negative control: `ontology_raw`")
    lines.append(f"- Candidate-stage intermediate: `soft_support_raw`")
    lines.append(f"- Main row after week 17: `soft_support_fuzzy_retrieval_main`")
    lines.append("")
    lines.append("## Appendix positioning")
    lines.append(f"- Appendix row: `soft_support_fuzzy_encoder_probe_v0`")
    lines.append(f"- Decision: `{appendix_probe['decision']}`")
    lines.append("")
    lines.append("## Paper narrative lock")
    for item in result["paper_narrative_lock"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Current limitations")
    for item in result["current_limitations"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Next-step recommendation")
    lines.append(f"- test_readiness_status: `{readiness['decision']}`")
    lines.append(f"- recommended_direction: `{result['next_step_recommendation']['recommended_direction']}`")
    lines.append("")
    lines.append("## Paper-ready paragraph")
    lines.append(result["paper_ready_paragraph"])
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"[OK] wrote {OUT_JSON}")
    print(f"[OK] wrote {OUT_MD}")
    print(json.dumps({
        "main_row_after_week17": result["row_positioning"]["main_row_after_week17"]["row_name"],
        "appendix_row": result["appendix_positioning"]["row_name"],
        "test_readiness_status": result["next_step_recommendation"]["test_readiness_status"],
        "recommended_direction": result["next_step_recommendation"]["recommended_direction"],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()