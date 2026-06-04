from __future__ import annotations

import json
from pathlib import Path
from collections import Counter, defaultdict

import pandas as pd
import yaml


BASE_A = Path("dataset/setting_a")
BASE_B = Path("dataset/setting_b")

GRAPH_DIR = BASE_A / "02_graph"
SPLIT_DIR = BASE_A / "01_split"

ONTO_DIR = BASE_B / "01_ontology"
ANNOT_DIR = BASE_B / "01_annotations"
ANNOT_DIR.mkdir(parents=True, exist_ok=True)

RAW_RULES_JSON = ONTO_DIR / "domain_range_rules.json"
TYPE_MAP_PATH = ANNOT_DIR / "type_map.tsv"

OUT_SCHEMA = ANNOT_DIR / "schema_rules.json"
OUT_PATHS = ANNOT_DIR / "path_templates.yaml"
OUT_REPORT = Path("reports/week3/schema_validation_report.md")
OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)


CANONICAL_SCHEMA = {
    "indication": ["Drug", "Disease"],
    "contraindication": ["Drug", "Disease"],
    "target": ["Drug", "Protein_or_Gene"],
    "associated_with": ["Protein_or_Gene", "Disease"],
    "ppi": ["Protein_or_Gene", "Protein_or_Gene"],
}


PATH_TEMPLATES = {
    "valid_path_templates": [
        {
            "name": "drug_target_disease",
            "path": [
                ["Drug", "target", "Protein_or_Gene"],
                ["Protein_or_Gene", "associated_with", "Disease"],
            ],
        },
        {
            "name": "drug_target_ppi_disease",
            "path": [
                ["Drug", "target", "Protein_or_Gene"],
                ["Protein_or_Gene", "ppi", "Protein_or_Gene"],
                ["Protein_or_Gene", "associated_with", "Disease"],
            ],
        },
    ],
    "invalid_for_treatment_explanation": [
        {
            "name": "direct_contraindication",
            "path": [
                ["Drug", "contraindication", "Disease"],
            ],
        }
    ],
}


def norm(x):
    return str(x).strip()


def read_tsv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t")


def load_type_map() -> dict[str, str]:
    df = read_tsv(TYPE_MAP_PATH)
    type_col = "final_type" if "final_type" in df.columns else "type"
    return {norm(r["entity"]): norm(r[type_col]) for _, r in df.iterrows()}


def collect_triples() -> list[tuple[str, str, str, str]]:
    triples = []

    for path in sorted(SPLIT_DIR.glob("*.tsv")):
        df = read_tsv(path)
        hcol = "head" if "head" in df.columns else df.columns[0]
        rcol = "relation" if "relation" in df.columns else df.columns[1]
        tcol = "tail" if "tail" in df.columns else df.columns[2]

        for _, row in df.iterrows():
            triples.append((norm(row[hcol]), norm(row[rcol]), norm(row[tcol]), path.name))

    for path in sorted(GRAPH_DIR.glob("*.tsv")):
        df = read_tsv(path)
        if not {"head", "relation", "tail"}.issubset(df.columns):
            continue

        for _, row in df.iterrows():
            triples.append((norm(row["head"]), norm(row["relation"]), norm(row["tail"]), path.name))

    return triples


def main():
    with open(OUT_SCHEMA, "w", encoding="utf-8") as f:
        json.dump(CANONICAL_SCHEMA, f, ensure_ascii=False, indent=2)

    with open(OUT_PATHS, "w", encoding="utf-8") as f:
        yaml.safe_dump(PATH_TEMPLATES, f, allow_unicode=True, sort_keys=False)

    type_map = load_type_map()
    triples = collect_triples()

    relation_counts = Counter()
    checked_counts = Counter()
    violations = []

    for h, r, t, src in triples:
        relation_counts[r] += 1

        if r not in CANONICAL_SCHEMA:
            continue

        ht = type_map.get(h, "Other")
        tt = type_map.get(t, "Other")
        allowed_h, allowed_t = CANONICAL_SCHEMA[r]

        checked_counts[r] += 1

        if not (ht == allowed_h and tt == allowed_t):
            violations.append({
                "head": h,
                "head_type": ht,
                "relation": r,
                "tail": t,
                "tail_type": tt,
                "allowed": f"{allowed_h}->{allowed_t}",
                "source_file": src,
            })

    vdf = pd.DataFrame(violations)
    violation_path = ANNOT_DIR / "schema_violations.tsv"
    if len(vdf) == 0:
        vdf = pd.DataFrame(columns=[
            "head", "head_type", "relation", "tail", "tail_type", "allowed", "source_file"
        ])
    vdf.to_csv(violation_path, sep="\t", index=False)

    report = []
    report.append("# Schema Validation Report")
    report.append("")
    report.append("## 1. Frozen schema rules")
    for rel, pair in CANONICAL_SCHEMA.items():
        report.append(f"- {rel}: {pair[0]} -> {pair[1]}")
    report.append("")
    report.append("## 2. Relation counts observed")
    for rel, c in sorted(relation_counts.items()):
        report.append(f"- {rel}: {c}")
    report.append("")
    report.append("## 3. Checked relation counts")
    for rel, c in sorted(checked_counts.items()):
        report.append(f"- {rel}: {c}")
    report.append("")
    report.append("## 4. Violation summary")
    report.append(f"- total checked triples: {sum(checked_counts.values())}")
    report.append(f"- total schema violations: {len(vdf)}")
    report.append("")
    report.append("## 5. Path policy")
    report.append("- valid treatment evidence paths include target/associated_with and target/ppi/associated_with")
    report.append("- contraindication is retained for safety lookup but is invalid as supportive treatment explanation")
    report.append("")
    report.append("## 6. Output files")
    report.append(f"- schema rules: `{OUT_SCHEMA}`")
    report.append(f"- path templates: `{OUT_PATHS}`")
    report.append(f"- violations: `{violation_path}`")

    with open(OUT_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    print("Saved:", OUT_SCHEMA)
    print("Saved:", OUT_PATHS)
    print("Saved:", violation_path)
    print("Saved:", OUT_REPORT)
    print("relation_counts =", dict(relation_counts))
    print("checked_triples =", sum(checked_counts.values()))
    print("schema_violations =", len(vdf))


if __name__ == "__main__":
    main()