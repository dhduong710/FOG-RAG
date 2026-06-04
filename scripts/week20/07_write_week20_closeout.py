from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(".").resolve()

E2E_MAIN = ROOT / "results/week20/e2e_main_table.json"
E2E_ABL = ROOT / "results/week20/e2e_ablation.json"
TABLES = ROOT / "results/week20/paper_tables_manifest.json"
FIGURES = ROOT / "results/week20/paper_figures_manifest.json"
CASES = ROOT / "results/week20/paper_case_pack.json"

OUT_JSON = ROOT / "results/week20/week20_go_decision.json"
OUT_MD = ROOT / "reports/week20/day7_week20_closeout.md"

def load(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def save(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def main():
    e2e_main = load(E2E_MAIN)
    e2e_abl = load(E2E_ABL)
    tables = load(TABLES)
    figures = load(FIGURES)
    cases = load(CASES)

    checks = {
        "e2e_main_table_built": e2e_main.get("status") == "BUILT_REVIEWER_SAFE",
        "e2e_ablation_built": e2e_abl.get("status") == "BUILT_REVIEWER_SAFE",
        "paper_tables_built": tables.get("status") == "BUILT",
        "paper_figures_manifest_built": figures.get("status") == "BUILT",
        "paper_case_pack_built": cases.get("status") == "BUILT",
        "main_row_is_retrieval": e2e_main.get("provisional_main_row") == "soft_support_fuzzy_retrieval_main",
        "soft_improves_backbone_e2e": e2e_main.get("narrative_checks", {}).get("soft_improves_e2e_mrr_vs_backbone") is True,
        "retrieval_preserves_soft_e2e": e2e_main.get("narrative_checks", {}).get("retrieval_preserves_e2e_mrr_vs_soft") is True,
        "retrieval_smaller_subgraph": e2e_main.get("narrative_checks", {}).get("retrieval_has_smaller_subgraph_than_soft") is True,
    }

    all_pass = all(checks.values())

    decision = {
        "week": 20,
        "stage": "week20_closeout",
        "status": "GO_FULL_PAPER_WRITING_WITH_EXPERIMENT_BACKLOG" if all_pass else "CONDITIONAL_GO_NEEDS_CLEANUP",
        "closeout_checks": checks,
        "paper_facing_decision": {
            "main_row": "soft_support_fuzzy_retrieval_main",
            "reference_row": "backbone_raw",
            "candidate_stage_intermediate": "soft_support_raw",
            "encoder_status": "appendix_only",
            "main_claim": (
                "Soft support provides the main ranking gain over backbone; confidence-aware retrieval "
                "preserves candidate/E2E performance while substantially reducing evidence subgraph size."
            ),
            "known_limitation": e2e_abl.get("interpretation", {}).get("known_limitation"),
        },
        "week20_outputs": {
            "e2e_main_table": str(E2E_MAIN),
            "e2e_ablation": str(E2E_ABL),
            "paper_tables_manifest": str(TABLES),
            "paper_figures_manifest": str(FIGURES),
            "paper_case_pack": str(CASES),
        },
        "recommended_next_weeks": [
            {
                "priority": 1,
                "name": "Week21_baseline_rerun_and_fair_comparison",
                "decision": "DO_NEXT",
                "scope": [
                    "Rerun structure baselines on the exact same drug-only head-prediction task.",
                    "Use reviewer-safe MRR@20 and Hits@1/3/10@20.",
                    "Check whether any baseline beats the current candidate ceiling.",
                    "If a baseline is stronger, consider an appendix branch using that baseline as upstream candidate source."
                ],
            },
            {
                "priority": 2,
                "name": "Week22_second_dataset_feasibility",
                "decision": "DO_AFTER_BASELINES",
                "scope": [
                    "Check PharmKG first for a drug-disease indication/treatment-style relation.",
                    "Verify entity types, relation names, candidate universe, split policy, and no-leak rules.",
                    "Only build full downstream pipeline if the task is clean and comparable."
                ],
            },
            {
                "priority": 3,
                "name": "Week23_optional_dataset2_minimal_pipeline",
                "decision": "CONDITIONAL",
                "scope": [
                    "If PharmKG/DRKG feasibility passes, run a minimal no-injection pipeline.",
                    "Do not add encoder or extra novelty.",
                    "Report as external validation, not replacement of PrimeKG main result."
                ],
            },
            {
                "priority": 4,
                "name": "Week24_optional_robustness",
                "decision": "OPTIONAL",
                "scope": [
                    "Rule sensitivity: hard-coded rules vs no-rules vs random-rule negative control.",
                    "Question-template sensitivity for indication prompts.",
                    "Small noise robustness if time permits.",
                    "One extra LLM only if adapter/fine-tuning budget is available."
                ],
            },
        ],
        "final_note": (
            "Week 20 closes the main experimental package. The next best step is not to change the mainline, "
            "but to run fair baselines under the same reviewer-safe protocol before expanding to another dataset."
        ),
    }

    save(OUT_JSON, decision)

    md = []
    md.append("# Day 7 — Week 20 closeout")
    md.append("")
    md.append(f"- status: **{decision['status']}**")
    md.append(f"- main_row: **`{decision['paper_facing_decision']['main_row']}`**")
    md.append("")
    md.append("## 1. Closeout checks")
    for k, v in checks.items():
        md.append(f"- {k}: `{v}`")
    md.append("")
    md.append("## 2. Paper-facing decision")
    for k, v in decision["paper_facing_decision"].items():
        md.append(f"- {k}: `{v}`")
    md.append("")
    md.append("## 3. Recommended next weeks")
    for item in decision["recommended_next_weeks"]:
        md.append(f"### Priority {item['priority']} — {item['name']}")
        md.append(f"- decision: `{item['decision']}`")
        for s in item["scope"]:
            md.append(f"- {s}")
        md.append("")
    md.append("## 4. Final note")
    md.append(decision["final_note"])
    md.append("")
    md.append("## 5. Day-7 conclusion")
    md.append(
        "Week 20 is closed. The main PrimeKG/FOG-RAG result package is paper-ready, "
        "with a clear experiment backlog for baseline fairness, second-dataset feasibility, and optional robustness."
    )

    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
