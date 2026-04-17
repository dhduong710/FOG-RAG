#!/usr/bin/env python3
import csv
import json
from pathlib import Path


ROOT = Path(".")
OUT_DIR = ROOT / "results" / "week8" / "baseline_table_v0"
REPORT_DIR = ROOT / "reports" / "week8"

STRUCTURE_METRICS = {
    "R-GCN": ROOT / "dataset" / "setting_a" / "17_structure_baselines" / "rgcn_valid_metrics.json",
    "HRGAT": ROOT / "dataset" / "setting_a" / "17_structure_baselines" / "hrgat_valid_metrics.json",
    "ComplEx": ROOT / "dataset" / "setting_a" / "17_structure_baselines" / "complex_valid_metrics.json",
    "TransE": ROOT / "dataset" / "setting_a" / "17_structure_baselines" / "transe_valid_metrics.json",
}

REFERENCE_METRICS = {
    "week7 3B": ROOT / "results" / "week7" / "backbone_valid_v2_short" / "valid_eval_v2" / "eval_valid_v2_metrics.json",
    "week7 8B": ROOT / "results" / "week7" / "backbone_valid_v2_8b_full" / "valid_eval_8b" / "eval_valid_8b_metrics.json",
    "week8 posthoc 3B": ROOT / "results" / "week8" / "backbone_valid_posthoc_3b" / "valid_eval_posthoc_3b" / "eval_valid_posthoc_3b_metrics.json",
}

STRUCTURE_NOTES = {
    "R-GCN": "Provisional row from week7 ranker_v2 score dump; clean structure-only eval, not yet paper-faithful reproduction.",
    "HRGAT": "Minimal structure-only HRGAT baseline under the same clean valid-first protocol.",
    "ComplEx": "Preferred third baseline; strongest structure-only row in current table v0.",
    "TransE": "Bonus fourth baseline; fallback/simple translational reference.",
}

REFERENCE_NOTES = {
    "week7 3B": "Candidate-aware reranker reference row; main backbone reference package.",
    "week7 8B": "Candidate-aware reranker capacity check; slight gain over week7 3B.",
    "week8 posthoc 3B": "Supporting retrieval-side analysis only; not the main backbone package.",
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def fmt(x):
    if isinstance(x, float):
        return f"{x:.8f}".rstrip("0").rstrip(".")
    return str(x)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    missing = []
    for path in list(STRUCTURE_METRICS.values()) + list(REFERENCE_METRICS.values()):
        if not path.exists():
            missing.append(str(path))
    if missing:
        print("Missing metric files:")
        for p in missing:
            print("-", p)
        raise SystemExit(1)

    structure_rows = []
    reference_rows = []
    source_manifest = {
        "structure_only": {},
        "reference_rows": {},
    }

    for method, path in STRUCTURE_METRICS.items():
        x = load_json(path)
        source_manifest["structure_only"][method] = str(path)
        structure_rows.append({
            "Method": method,
            "Category": "structure-only",
            "Valid MRR": x["mrr"],
            "Hits@1": x["hits1"],
            "Hits@3": x["hits3"],
            "Hits@10": x["hits10"],
            "Notes": STRUCTURE_NOTES[method],
        })

    for method, path in REFERENCE_METRICS.items():
        x = load_json(path)
        source_manifest["reference_rows"][method] = str(path)
        reference_rows.append({
            "Method": method,
            "Protocol": "candidate-aware reranker reference",
            "Valid MRR": x["mrr"],
            "Hits@1": x["hits1"],
            "Hits@3": x["hits3"],
            "Hits@10": x["hits10"],
            "Notes": REFERENCE_NOTES[method],
        })

    # save source manifest
    with (OUT_DIR / "table_sources.json").open("w", encoding="utf-8") as f:
        json.dump(source_manifest, f, ensure_ascii=False, indent=2)

    # save structure csv
    csv_path = OUT_DIR / "setting_a_structure_table_v0.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["Method", "Category", "Valid MRR", "Hits@1", "Hits@3", "Hits@10", "Notes"]
        )
        writer.writeheader()
        for row in structure_rows:
            writer.writerow({
                "Method": row["Method"],
                "Category": row["Category"],
                "Valid MRR": fmt(row["Valid MRR"]),
                "Hits@1": fmt(row["Hits@1"]),
                "Hits@3": fmt(row["Hits@3"]),
                "Hits@10": fmt(row["Hits@10"]),
                "Notes": row["Notes"],
            })

    # save structure markdown
    md_lines = []
    md_lines.append("# Setting A Structure-only Baselines (v0)")
    md_lines.append("")
    md_lines.append("## Protocol")
    md_lines.append("- Task: head prediction `(?, indication, disease)`")
    md_lines.append("- Universe: drug-only")
    md_lines.append("- Decision split: valid")
    md_lines.append("- Main metrics: MRR, Hits@1, Hits@3, Hits@10")
    md_lines.append("")
    md_lines.append("| Method | Category | Valid MRR | Hits@1 | Hits@3 | Hits@10 | Notes |")
    md_lines.append("|---|---:|---:|---:|---:|---:|---|")
    for row in structure_rows:
        md_lines.append(
            f"| {row['Method']} | {row['Category']} | {fmt(row['Valid MRR'])} | {fmt(row['Hits@1'])} | {fmt(row['Hits@3'])} | {fmt(row['Hits@10'])} | {row['Notes']} |"
        )
    md_lines.append("")
    md_lines.append("## Current takeaway")
    md_lines.append("- ComplEx is currently the strongest structure-only row in table v0.")
    md_lines.append("- HRGAT clearly improves over the provisional R-GCN row.")
    md_lines.append("- TransE is a useful bonus baseline but weaker than ComplEx and HRGAT.")
    md_lines.append("")
    (OUT_DIR / "setting_a_structure_table_v0.md").write_text("\n".join(md_lines), encoding="utf-8")

    # save reference markdown
    ref_lines = []
    ref_lines.append("# Setting A Candidate-aware Reranker Reference Rows")
    ref_lines.append("")
    ref_lines.append("These rows are supporting references and should not be mixed directly with structure-only baselines without explicit protocol notes.")
    ref_lines.append("")
    ref_lines.append("| Method | Protocol | Valid MRR | Hits@1 | Hits@3 | Hits@10 | Notes |")
    ref_lines.append("|---|---|---:|---:|---:|---:|---|")
    for row in reference_rows:
        ref_lines.append(
            f"| {row['Method']} | {row['Protocol']} | {fmt(row['Valid MRR'])} | {fmt(row['Hits@1'])} | {fmt(row['Hits@3'])} | {fmt(row['Hits@10'])} | {row['Notes']} |"
        )
    ref_lines.append("")
    ref_lines.append("## Important note")
    ref_lines.append("- week7 3B remains the main backbone reference.")
    ref_lines.append("- week8 posthoc 3B remains supporting retrieval-side analysis only.")
    ref_lines.append("")
    (OUT_DIR / "setting_a_reference_rows.md").write_text("\n".join(ref_lines), encoding="utf-8")

    # optional preview
    preview_lines = []
    preview_lines.append("Structure-only ordering by MRR:")
    for row in sorted(structure_rows, key=lambda x: x["Valid MRR"], reverse=True):
        preview_lines.append(
            f"{row['Method']}: MRR={fmt(row['Valid MRR'])}, Hits@10={fmt(row['Hits@10'])}"
        )
    (OUT_DIR / "setting_a_structure_table_v0_preview.txt").write_text("\n".join(preview_lines), encoding="utf-8")

    # day6 report
    report_lines = []
    report_lines.append("# Day 6 Table v0")
    report_lines.append("")
    report_lines.append("## 1. Scope")
    report_lines.append("- Gather all clean structure-only baseline rows")
    report_lines.append("- Gather candidate-aware reranker reference rows")
    report_lines.append("- Build the first Setting A result table v0")
    report_lines.append("")
    report_lines.append("## 2. Structure-only baselines included")
    for row in structure_rows:
        report_lines.append(
            f"- {row['Method']}: MRR={fmt(row['Valid MRR'])}, Hits@10={fmt(row['Hits@10'])}"
        )
    report_lines.append("")
    report_lines.append("## 3. Reference rows included")
    for row in reference_rows:
        report_lines.append(
            f"- {row['Method']}: MRR={fmt(row['Valid MRR'])}, Hits@10={fmt(row['Hits@10'])}"
        )
    report_lines.append("")
    report_lines.append("## 4. Current conclusion")
    report_lines.append("- Table v0 is clean and traceable.")
    report_lines.append("- Structure-only baselines and candidate-aware references are separated.")
    report_lines.append("- ComplEx is currently the best structure-only row.")
    report_lines.append("- week7 3B remains the main reranker reference row.")
    report_lines.append("")
    report_lines.append("## 5. Output files")
    report_lines.append(f"- `{OUT_DIR / 'setting_a_structure_table_v0.csv'}`")
    report_lines.append(f"- `{OUT_DIR / 'setting_a_structure_table_v0.md'}`")
    report_lines.append(f"- `{OUT_DIR / 'setting_a_reference_rows.md'}`")
    report_lines.append(f"- `{OUT_DIR / 'table_sources.json'}`")
    report_lines.append("")
    (REPORT_DIR / "day6_table_v0.md").write_text("\n".join(report_lines), encoding="utf-8")

    print("Saved:")
    print(f"- {OUT_DIR / 'setting_a_structure_table_v0.csv'}")
    print(f"- {OUT_DIR / 'setting_a_structure_table_v0.md'}")
    print(f"- {OUT_DIR / 'setting_a_reference_rows.md'}")
    print(f"- {OUT_DIR / 'table_sources.json'}")
    print(f"- {OUT_DIR / 'setting_a_structure_table_v0_preview.txt'}")
    print(f"- {REPORT_DIR / 'day6_table_v0.md'}")


if __name__ == "__main__":
    main()