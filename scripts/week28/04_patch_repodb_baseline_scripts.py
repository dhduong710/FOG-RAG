#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

ROOT = Path(".")

SRC_KGE = ROOT / "scripts/week27/04a_run_drkg_kge_baselines.py"
SRC_GNN = ROOT / "scripts/week27/04b_run_drkg_gnn_baselines.py"

OUT_KGE = ROOT / "scripts/week28/04a_run_repodb_kge_baselines.py"
OUT_GNN = ROOT / "scripts/week28/04b_run_repodb_gnn_baselines.py"


REPLACEMENTS = {
    "setting_e_drkg": "setting_f_repodb",
    "week27": "week28",

    "drkg_baseline_reviewer_safe_valid.json": "repodb_baseline_reviewer_safe_valid.json",
    "drkg_baseline_reviewer_safe_test.json": "repodb_baseline_reviewer_safe_test.json",
    "drkg_baseline_main_table.json": "repodb_baseline_main_table.json",

    "day4_drkg_structure_baselines.md": "day4_repodb_structure_baselines.md",

    "DRKG": "repoDB",
    "drugbank_treats": "repodb_approved_indication",
    "(?, DRUGBANK::treats, disease)": "(?, repoDB_approved_indication, disease)",
    "DRUGBANK::treats::Compound:Disease": "repoDB::approved_indication::Compound:Disease",
    "drugbank_treats": "repodb_approved_indication",
    "train_target_relation_compound_heads": "train_approved_relation_compound_heads",
}


def patch_text(text: str) -> str:
    for a, b in REPLACEMENTS.items():
        text = text.replace(a, b)

    text = text.replace(
        "# Week 27 Day 4 — repoDB Structure Baselines",
        "# Week 28 Day 4 — repoDB Structure Baselines",
    )
    text = text.replace(
        "# Week 27 Day 4 — DRKG Structure Baselines",
        "# Week 28 Day 4 — repoDB Structure Baselines",
    )
    return text


def patch_one(src: Path, dst: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(f"Missing source script: {src}")

    text = src.read_text(encoding="utf-8")
    text = patch_text(text)

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")
    dst.chmod(0o755)
    print(f"[write] {dst}")


def main():
    patch_one(SRC_KGE, OUT_KGE)
    patch_one(SRC_GNN, OUT_GNN)
    print("[DONE] repoDB Day 4 baseline scripts generated")


if __name__ == "__main__":
    main()
