from pathlib import Path
import pandas as pd
import json


RAW_KG_PATH = Path("dataset/raw/primekg/kg.csv")
SPLIT_DIR = Path("dataset/setting_a/01_split")

SAFETY_DIR = Path("dataset/setting_b/00_safety_labels")
ONTOLOGY_DIR = Path("dataset/setting_b/01_ontology")
EVAL_META_DIR = Path("dataset/setting_b/02_eval_meta")

DOC_PATH = Path("docs/decisions/setting_b.md")
REPORT_PATH = Path("reports/week2/day4_setting_b_report.md")


def norm_text(x):
    return str(x).strip()


def norm_lower(x):
    return str(x).strip().lower()


def save_json(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def rel_match(df: pd.DataFrame, aliases) -> pd.Series:
    aliases = {a.strip().lower() for a in aliases}
    rel = df["relation"].astype(str).str.strip().str.lower()
    disp = df["display_relation"].astype(str).str.strip().str.lower()
    return rel.isin(aliases) | disp.isin(aliases)


def read_split_entities():
    train_df = pd.read_csv(SPLIT_DIR / "train.tsv", sep="\t")
    valid_df = pd.read_csv(SPLIT_DIR / "valid.tsv", sep="\t")
    test_df = pd.read_csv(SPLIT_DIR / "test.tsv", sep="\t")

    all_df = pd.concat([train_df, valid_df, test_df], ignore_index=True)

    drugs = sorted(all_df["head"].astype(str).str.strip().unique().tolist())
    diseases = sorted(all_df["tail"].astype(str).str.strip().unique().tolist())

    return train_df, valid_df, test_df, drugs, diseases


def build_contraindication_edges(raw_df: pd.DataFrame):
    tmp = raw_df.copy()

    mask = rel_match(tmp, {"contraindication"})

    tmp = tmp.loc[mask].copy()

    tmp["x_type_norm"] = tmp["x_type"].map(norm_lower)
    tmp["y_type_norm"] = tmp["y_type"].map(norm_lower)

    tmp = tmp[
        (tmp["x_type_norm"] == "drug") &
        (tmp["y_type_norm"] == "disease")
    ].copy()

    out = pd.DataFrame({
        "head": tmp["x_name"].map(norm_text),
        "relation": "contraindication",
        "tail": tmp["y_name"].map(norm_text),
    })

    out = out.drop_duplicates().reset_index(drop=True)
    return out


def build_type_map(raw_df: pd.DataFrame):
    left = raw_df[["x_name", "x_type"]].copy()
    left.columns = ["entity_name", "entity_type"]

    right = raw_df[["y_name", "y_type"]].copy()
    right.columns = ["entity_name", "entity_type"]

    ent = pd.concat([left, right], ignore_index=True)
    ent["entity_name"] = ent["entity_name"].map(norm_text)
    ent["entity_type"] = ent["entity_type"].map(norm_lower)

    ent = ent.dropna().drop_duplicates()

    grouped = ent.groupby("entity_name")["entity_type"].apply(lambda s: sorted(set(s.tolist())))

    clean_map = {}
    conflicts = {}

    for name, types in grouped.items():
        if len(types) == 1:
            clean_map[name] = types[0]
        else:
            conflicts[name] = types

    return clean_map, conflicts


def main():
    SAFETY_DIR.mkdir(parents=True, exist_ok=True)
    ONTOLOGY_DIR.mkdir(parents=True, exist_ok=True)
    EVAL_META_DIR.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    raw_df = pd.read_csv(RAW_KG_PATH, low_memory=False)

    train_df, valid_df, test_df, split_drugs, split_diseases = read_split_entities()

    # 1) Contraindication edges
    contra_full_df = build_contraindication_edges(raw_df)

    split_drug_set = set(split_drugs)
    split_disease_set = set(split_diseases)

    contra_overlap_df = contra_full_df[
        contra_full_df["head"].isin(split_drug_set) &
        contra_full_df["tail"].isin(split_disease_set)
    ].copy().reset_index(drop=True)

    contra_full_path = SAFETY_DIR / "contraindication_edges_full.tsv"
    contra_overlap_path = SAFETY_DIR / "contraindication_edges_overlap.tsv"

    contra_full_df.to_csv(contra_full_path, sep="\t", index=False)
    contra_overlap_df.to_csv(contra_overlap_path, sep="\t", index=False)

    # 2) Contra lookups
    contra_by_disease = (
        contra_overlap_df.groupby("tail")["head"]
        .apply(lambda s: sorted(set(s.tolist())))
        .to_dict()
    )

    contra_by_drug = (
        contra_overlap_df.groupby("head")["tail"]
        .apply(lambda s: sorted(set(s.tolist())))
        .to_dict()
    )

    save_json(contra_by_disease, SAFETY_DIR / "contra_by_disease.json")
    save_json(contra_by_drug, SAFETY_DIR / "contra_by_drug.json")

    # 3) Entity type map
    entity_name_to_type, name_type_conflicts = build_type_map(raw_df)

    save_json(entity_name_to_type, ONTOLOGY_DIR / "entity_name_to_type.json")
    save_json(name_type_conflicts, ONTOLOGY_DIR / "name_type_conflicts.json")

    split_entities = sorted(set(split_drugs) | set(split_diseases))
    missing_split_entities = [
        e for e in split_entities
        if (e not in entity_name_to_type) and (e not in name_type_conflicts)
    ]
    save_json(missing_split_entities, ONTOLOGY_DIR / "missing_split_entities.json")

    # 4) Domain-range rules
    domain_range_rules = {
        "indication": {
            "head_type": "drug",
            "tail_type": "disease",
            "role": "setting_a_main_task"
        },
        "contraindication": {
            "head_type": "drug",
            "tail_type": "disease",
            "role": "setting_b_auxiliary_safety"
        },
        "target": {
            "head_type": "drug",
            "tail_type": "gene/protein",
            "role": "train_graph_enrichment"
        },
        "associated_with": {
            "head_type": "gene/protein",
            "tail_type": "disease",
            "role": "train_graph_enrichment"
        },
        "ppi": {
            "head_type": "gene/protein",
            "tail_type": "gene/protein",
            "role": "train_graph_enrichment",
            "symmetric": True,
            "counting_convention": "unordered_collapsed"
        }
    }
    save_json(domain_range_rules, ONTOLOGY_DIR / "domain_range_rules.json")

    # 5) Safety eval config
    safety_eval_config = {
        "base_split_dir": str(SPLIT_DIR),
        "main_task": {
            "query_format": "(?, indication, disease)",
            "candidate_type": "drug",
            "positive_relation": "indication"
        },
        "setting_b_policy": {
            "reuse_setting_a_split": True,
            "change_main_task": False,
            "use_contraindication_as_positive_label": False,
            "allow_hard_filter": True,
            "allow_soft_penalty": True,
            "allow_safety_metrics": True
        },
        "metrics_planned": [
            {
                "name": "Contra@10",
                "meaning": "Number or rate of contraindicated drugs appearing in top-10 predictions."
            },
            {
                "name": "SafetyViolation@10",
                "meaning": "Whether top-10 contains at least one contraindicated drug."
            },
            {
                "name": "ConstraintViolationRate",
                "meaning": "Rate of predictions violating type/safety constraints."
            }
        ]
    }
    save_json(safety_eval_config, EVAL_META_DIR / "safety_eval_config.json")

    # 6) Decision doc
    decision_md = f"""# Setting B Lock

## Core decision
Setting B reuses the exact same split as Setting A and keeps the same main task:

- Query format: `(?, indication, disease)`
- Candidate type: `drug`
- Positive relation of the main benchmark: `indication`

## What contraindication is used for
Contraindication is treated only as an auxiliary safety signal for:

- hard filtering
- soft penalty
- safety metrics
- case-study safety flagging

## What contraindication is NOT used for
Contraindication must not be used to:

- create positive training labels for the main task
- change gold labels of Setting A
- create a new train/valid/test split
- redefine the benchmark task

## Schema rules
- indication: drug -> disease
- contraindication: drug -> disease
- target: drug -> gene/protein
- associated_with: gene/protein -> disease
- ppi: gene/protein -> gene/protein (unordered-collapsed in train graph)

## Day-4 artifacts
- full contraindication edges: `{contra_full_path}`
- overlap contraindication edges: `{contra_overlap_path}`
- type map: `dataset/setting_b/01_ontology/entity_name_to_type.json`
- domain-range rules: `dataset/setting_b/01_ontology/domain_range_rules.json`
- safety config: `dataset/setting_b/02_eval_meta/safety_eval_config.json`

## Notes
This document locks the semantic role of Setting B before any hard-filter / soft-penalty implementation.
"""
    DOC_PATH.write_text(decision_md, encoding="utf-8")

    # 7) Report
    report_md = f"""# Week 2 - Day 4 Report

## Goal
Lock Setting B semantics and generate safety / ontology metadata.

## Inputs
- Raw PrimeKG: `{RAW_KG_PATH}`
- Setting A split: `{SPLIT_DIR}`

## Setting A entity universe
- unique drugs: {len(split_drugs)}
- unique diseases: {len(split_diseases)}

## Contraindication extraction
- full contraindication triples: {len(contra_full_df)}
- overlap contraindication triples: {len(contra_overlap_df)}
- diseases with contraindication labels in overlap set: {len(contra_by_disease)}
- drugs with contraindication labels in overlap set: {len(contra_by_drug)}

## Ontology mapping
- clean entity_name_to_type entries: {len(entity_name_to_type)}
- name/type conflict entries: {len(name_type_conflicts)}
- missing split entities: {len(missing_split_entities)}

## Locked Setting B policy
- reuse Setting A split: True
- main task unchanged: True
- contraindication as positive label: False
- candidate type fixed to drug: True

## Output files
- `{contra_full_path}`
- `{contra_overlap_path}`
- `dataset/setting_b/00_safety_labels/contra_by_disease.json`
- `dataset/setting_b/00_safety_labels/contra_by_drug.json`
- `dataset/setting_b/01_ontology/entity_name_to_type.json`
- `dataset/setting_b/01_ontology/name_type_conflicts.json`
- `dataset/setting_b/01_ontology/missing_split_entities.json`
- `dataset/setting_b/01_ontology/domain_range_rules.json`
- `dataset/setting_b/02_eval_meta/safety_eval_config.json`
- `{DOC_PATH}`

## Notes
Day 4 only locks metadata and semantics.
No filtering, penalty, reranking, or training is implemented today.
"""
    REPORT_PATH.write_text(report_md, encoding="utf-8")

    print("Done.")
    print(f"Saved: {contra_full_path}")
    print(f"Saved: {contra_overlap_path}")
    print(f"Saved: {SAFETY_DIR / 'contra_by_disease.json'}")
    print(f"Saved: {SAFETY_DIR / 'contra_by_drug.json'}")
    print(f"Saved: {ONTOLOGY_DIR / 'entity_name_to_type.json'}")
    print(f"Saved: {ONTOLOGY_DIR / 'name_type_conflicts.json'}")
    print(f"Saved: {ONTOLOGY_DIR / 'missing_split_entities.json'}")
    print(f"Saved: {ONTOLOGY_DIR / 'domain_range_rules.json'}")
    print(f"Saved: {EVAL_META_DIR / 'safety_eval_config.json'}")
    print(f"Saved: {DOC_PATH}")
    print(f"Saved: {REPORT_PATH}")
    print(f"Full contraindication triples   : {len(contra_full_df)}")
    print(f"Overlap contraindication triples: {len(contra_overlap_df)}")
    print(f"Type-map entries               : {len(entity_name_to_type)}")
    print(f"Type conflicts                 : {len(name_type_conflicts)}")
    print(f"Missing split entities         : {len(missing_split_entities)}")


if __name__ == "__main__":
    main()