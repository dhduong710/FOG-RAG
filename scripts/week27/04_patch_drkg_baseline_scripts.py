#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from pathlib import Path


ROOT = Path(".")

SRC_KGE = ROOT / "scripts/week26/03a_run_hetionet_kge_baselines.py"
SRC_GNN = ROOT / "scripts/week26/03b_run_hetionet_gnn_baselines_v2.py"

OUT_KGE = ROOT / "scripts/week27/04a_run_drkg_kge_baselines.py"
OUT_GNN = ROOT / "scripts/week27/04b_run_drkg_gnn_baselines.py"


REPLACEMENTS = {
    "setting_d_hetionet": "setting_e_drkg",
    "week26": "week27",
    "hetionet_baseline_reviewer_safe_valid.json": "drkg_baseline_reviewer_safe_valid.json",
    "hetionet_baseline_reviewer_safe_test.json": "drkg_baseline_reviewer_safe_test.json",
    "hetionet_baseline_main_table.json": "drkg_baseline_main_table.json",
    "day3_hetionet_structure_baselines.md": "day4_drkg_structure_baselines.md",
    "Hetionet v1.0": "DRKG",
    "Hetionet": "DRKG",
    "compound_treats_disease": "drugbank_treats",
    "(?, CtD, disease)": "(?, DRUGBANK::treats, disease)",
    "CtD": "DRUGBANK::treats::Compound:Disease",
    "Compound-treats-Disease": "DRUGBANK::treats::Compound:Disease",
    "num_candidate_compounds": "num_candidate_compounds",
}


def patch_text(text: str) -> str:
    for a, b in REPLACEMENTS.items():
        text = text.replace(a, b)

    # Cleaner report title if inherited from Hetionet script.
    text = text.replace(
        "# Week 26 Day 3 — DRKG Structure Baselines",
        "# Week 27 Day 4 — DRKG Structure Baselines",
    )
    text = text.replace(
        "# Week 26 Day 3 — Hetionet Structure Baselines",
        "# Week 27 Day 4 — DRKG Structure Baselines",
    )
    text = text.replace(
        "# Week 27 Day 3 — DRKG Structure Baselines",
        "# Week 27 Day 4 — DRKG Structure Baselines",
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


def main() -> None:
    patch_one(SRC_KGE, OUT_KGE)
    patch_one(SRC_GNN, OUT_GNN)
    print("[DONE] DRKG Day 4 baseline scripts generated")


if __name__ == "__main__":
    main()
