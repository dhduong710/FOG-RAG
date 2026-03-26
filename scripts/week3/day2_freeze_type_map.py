from __future__ import annotations

import json
from pathlib import Path
from collections import Counter

import pandas as pd


BASE_A = Path("dataset/setting_a")
BASE_B = Path("dataset/setting_b")

SPLIT_DIR = BASE_A / "01_split"
GRAPH_DIR = BASE_A / "02_graph"
CAND_DIR = BASE_A / "03_candidates"

ONTO_DIR = BASE_B / "01_ontology"
ANNOT_DIR = BASE_B / "01_annotations"
ANNOT_DIR.mkdir(parents=True, exist_ok=True)

RAW_TYPE_JSON = ONTO_DIR / "entity_name_to_type.json"
RULES_JSON = ONTO_DIR / "domain_range_rules.json"
NAME_CONFLICT_JSON = ONTO_DIR / "name_type_conflicts.json"
MISSING_SPLIT_JSON = ONTO_DIR / "missing_split_entities.json"

CONTRA_CANONICAL = ANNOT_DIR / "contraindication_pairs.tsv"
CONTRA_FALLBACK = BASE_B / "00_safety_labels" / "contraindication_edges_overlap.tsv"

OUT_TYPE_MAP = ANNOT_DIR / "type_map.tsv"
OUT_OVERRIDES = ANNOT_DIR / "type_map_overrides.tsv"
OUT_REPORT = Path("reports/week3/type_map_report.md")
OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)


RAW_TO_COARSE = {
    "drug": "Drug",
    "disease": "Disease",
    "gene/protein": "Protein_or_Gene",
    "pathway": "Pathway",
    "anatomy": "Anatomy_or_Phenotype",
    "effect/phenotype": "Anatomy_or_Phenotype",
    "biological_process": "Biological_Process",
    "molecular_function": "Biological_Process",
    "cellular_component": "Biological_Process",
    "exposure": "Other",
}

PRIORITY = {
    "candidate_valid_test": 100,
    "indication_or_contra": 90,
    "graph_rule": 70,
}


def norm(x: object) -> str:
    return str(x).strip()


def read_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_tsv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t")


def raw_to_coarse(raw_type: str | None) -> str | None:
    if raw_type is None:
        return None
    return RAW_TO_COARSE.get(norm(raw_type).lower())


def canonicalize_rule_type(x: str) -> str:
    x = norm(x).lower()
    if x == "drug":
        return "Drug"
    if x == "disease":
        return "Disease"
    if x == "gene/protein":
        return "Protein_or_Gene"
    if x == "pathway":
        return "Pathway"
    return "Other"


def add_expected(best: dict, entity: str, exp_type: str, source: str, priority: int):
    prev = best.get(entity)
    if prev is None or priority > prev["priority"]:
        best[entity] = {
            "expected_type": exp_type,
            "expected_source": source,
            "priority": priority,
        }


def collect_from_split(expected_best: dict) -> set[str]:
    universe = set()

    for name in ["train.tsv", "valid.tsv", "test.tsv"]:
        path = SPLIT_DIR / name
        if not path.exists():
            continue

        df = read_tsv(path)
        hcol = "head" if "head" in df.columns else df.columns[0]
        rcol = "relation" if "relation" in df.columns else df.columns[1]
        tcol = "tail" if "tail" in df.columns else df.columns[2]

        for _, row in df.iterrows():
            h = norm(row[hcol])
            r = norm(row[rcol]).lower()
            t = norm(row[tcol])

            universe.update([h, t])

            if r in {"indication", "contraindication"}:
                add_expected(expected_best, h, "Drug", "split_relation_head", PRIORITY["indication_or_contra"])
                add_expected(expected_best, t, "Disease", "split_relation_tail", PRIORITY["indication_or_contra"])

    return universe


def collect_from_graph(expected_best: dict, rules: dict) -> set[str]:
    universe = set()

    for path in sorted(GRAPH_DIR.glob("*.tsv")):
        df = read_tsv(path)
        if not {"head", "relation", "tail"}.issubset(df.columns):
            continue

        for _, row in df.iterrows():
            h = norm(row["head"])
            r = norm(row["relation"]).lower()
            t = norm(row["tail"])

            universe.update([h, t])

            if r in rules:
                head_type = canonicalize_rule_type(rules[r].get("head_type", "Other"))
                tail_type = canonicalize_rule_type(rules[r].get("tail_type", "Other"))

                add_expected(expected_best, h, head_type, f"graph_rule:{r}:head", PRIORITY["graph_rule"])
                add_expected(expected_best, t, tail_type, f"graph_rule:{r}:tail", PRIORITY["graph_rule"])

    return universe


def collect_from_candidates(expected_best: dict) -> tuple[set[str], set[str]]:
    universe = set()
    valid_test_candidates = set()

    for path in sorted(CAND_DIR.glob("*.json")):
        # bỏ qua file metadata
        if path.name == "candidate_meta.json":
            continue

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # chỉ nhận file candidate dạng list[dict]
        if not isinstance(data, list):
            print(f"[skip] {path.name}: top-level is {type(data).__name__}, not list")
            continue

        is_valid_or_test = path.name.startswith("valid") or path.name.startswith("test")

        for ex in data:
            if not isinstance(ex, dict):
                print(f"[skip item] {path.name}: item type = {type(ex).__name__}")
                continue

            query_entity = ex.get("query_entity")
            gold_entity = ex.get("gold_entity")
            cands = ex.get("candidate_entities", [])

            if query_entity:
                universe.add(norm(query_entity))
            if gold_entity:
                universe.add(norm(gold_entity))

            if not isinstance(cands, list):
                continue

            for c in cands:
                c = norm(c)
                if not c:
                    continue

                universe.add(c)

                if is_valid_or_test:
                    valid_test_candidates.add(c)
                    add_expected(
                        expected_best,
                        c,
                        "Drug",
                        "valid_test_candidate",
                        PRIORITY["candidate_valid_test"],
                    )

    return universe, valid_test_candidates


def collect_from_contra(expected_best: dict) -> set[str]:
    universe = set()

    contra_path = CONTRA_CANONICAL if CONTRA_CANONICAL.exists() else CONTRA_FALLBACK
    if not contra_path.exists():
        return universe

    df = read_tsv(contra_path)

    if {"drug", "disease"}.issubset(df.columns):
        for _, row in df.iterrows():
            d = norm(row["drug"])
            dis = norm(row["disease"])
            universe.update([d, dis])
            add_expected(expected_best, d, "Drug", "contra_annotation_drug", PRIORITY["indication_or_contra"])
            add_expected(expected_best, dis, "Disease", "contra_annotation_disease", PRIORITY["indication_or_contra"])
    elif {"head", "tail"}.issubset(df.columns):
        for _, row in df.iterrows():
            d = norm(row["head"])
            dis = norm(row["tail"])
            universe.update([d, dis])
            add_expected(expected_best, d, "Drug", "contra_annotation_head", PRIORITY["indication_or_contra"])
            add_expected(expected_best, dis, "Disease", "contra_annotation_tail", PRIORITY["indication_or_contra"])

    return universe


def main():
    raw_type_map = read_json(RAW_TYPE_JSON)
    rules = read_json(RULES_JSON) if RULES_JSON.exists() else {}
    name_conflicts = read_json(NAME_CONFLICT_JSON) if NAME_CONFLICT_JSON.exists() else {}
    missing_split_entities = read_json(MISSING_SPLIT_JSON) if MISSING_SPLIT_JSON.exists() else []

    expected_best = {}

    split_universe = collect_from_split(expected_best)
    graph_universe = collect_from_graph(expected_best, rules)
    cand_universe, valid_test_candidates = collect_from_candidates(expected_best)
    contra_universe = collect_from_contra(expected_best)

    universe = split_universe | graph_universe | cand_universe | contra_universe

    rows = []
    overrides = []

    for ent in sorted(universe):
        raw_type = raw_type_map.get(ent)
        raw_coarse = raw_to_coarse(raw_type)

        exp = expected_best.get(ent)
        final_type = None
        type_source = None
        notes = ""

        if exp is not None:
            exp_type = exp["expected_type"]
            exp_source = exp["expected_source"]

            if raw_coarse is None:
                final_type = exp_type
                type_source = "context_override_missing_raw"
                notes = f"expected_from={exp_source}"
                overrides.append({
                    "entity": ent,
                    "raw_type": "",
                    "raw_coarse": "",
                    "override_type": exp_type,
                    "override_reason": exp_source,
                })
            elif raw_coarse == exp_type:
                final_type = raw_coarse
                type_source = "raw_json"
                notes = f"context_agree:{exp_source}"
            else:
                final_type = exp_type
                type_source = "context_override_conflict"
                notes = f"raw={raw_type}; expected_from={exp_source}"
                overrides.append({
                    "entity": ent,
                    "raw_type": raw_type,
                    "raw_coarse": raw_coarse,
                    "override_type": exp_type,
                    "override_reason": exp_source,
                })
        else:
            if raw_coarse is not None:
                final_type = raw_coarse
                type_source = "raw_json"
            else:
                final_type = "Other"
                type_source = "fallback_other"
                notes = "missing_in_raw_json_and_no_context"

        rows.append({
            "entity": ent,
            "raw_type": raw_type if raw_type is not None else "",
            "final_type": final_type,
            "type_source": type_source,
            "notes": notes,
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUT_TYPE_MAP, sep="\t", index=False)

    odf = pd.DataFrame(overrides)
    if len(odf) == 0:
        odf = pd.DataFrame(columns=["entity", "raw_type", "raw_coarse", "override_type", "override_reason"])
    odf.to_csv(OUT_OVERRIDES, sep="\t", index=False)

    type_counts = Counter(df["final_type"].tolist())
    raw_missing_count = int((df["raw_type"] == "").sum())

    candidate_df = df[df["entity"].isin(valid_test_candidates)].copy()
    bad_candidates = candidate_df[candidate_df["final_type"] != "Drug"].copy()

    sample_rows = df.sample(min(20, len(df)), random_state=2025)

    report = []
    report.append("# Type Map Report")
    report.append("")
    report.append("## 1. Goal")
    report.append("Freeze a benchmark-relevant coarse type map for Setting B using the existing ontology JSON as the raw source.")
    report.append("")
    report.append("## 2. Inputs")
    report.append(f"- raw ontology source: `{RAW_TYPE_JSON}`")
    report.append(f"- relation rules: `{RULES_JSON}`")
    report.append(f"- name type conflicts: `{NAME_CONFLICT_JSON}`")
    report.append(f"- missing split entities: `{MISSING_SPLIT_JSON}`")
    report.append(f"- split dir: `{SPLIT_DIR}`")
    report.append(f"- graph dir: `{GRAPH_DIR}`")
    report.append(f"- candidate dir: `{CAND_DIR}`")
    report.append("")
    report.append("## 3. Summary")
    report.append(f"- benchmark-relevant entity universe: {len(df)}")
    report.append(f"- entities missing raw type in ontology JSON: {raw_missing_count}")
    report.append(f"- override rows: {len(odf)}")
    report.append(f"- valid/test candidate entities: {len(valid_test_candidates)}")
    report.append(f"- valid/test candidate entities typed as non-Drug: {len(bad_candidates)}")
    report.append(f"- existing name_type_conflicts.json entries: {len(name_conflicts)}")
    report.append(f"- existing missing_split_entities.json entries: {len(missing_split_entities)}")
    report.append("")
    report.append("## 4. Final type counts")
    for k in sorted(type_counts.keys()):
        report.append(f"- {k}: {type_counts[k]}")
    report.append("")
    report.append("## 5. Manual spot-check (20 samples)")
    for _, row in sample_rows.iterrows():
        report.append(f"- {row['entity']} -> {row['final_type']} ({row['type_source']}) {row['notes']}")
    report.append("")
    report.append("## 6. Notes")
    report.append("- `entity_name_to_type.json` is preserved as the raw ontology source.")
    report.append("- `type_map.tsv` is the frozen benchmark-relevant coarse type map for Setting B.")
    report.append("- Any task-critical conflicts are logged in `type_map_overrides.tsv` rather than changed silently.")

    with open(OUT_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    print("Saved:", OUT_TYPE_MAP)
    print("Saved:", OUT_OVERRIDES)
    print("Saved:", OUT_REPORT)
    print("benchmark_entity_universe =", len(df))
    print("raw_missing_count =", raw_missing_count)
    print("override_count =", len(odf))
    print("valid_test_candidate_count =", len(valid_test_candidates))
    print("bad_candidate_count =", len(bad_candidates))
    print("final_type_counts =", dict(type_counts))


if __name__ == "__main__":
    main()