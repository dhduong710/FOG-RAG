from pathlib import Path
import pandas as pd
import json
import argparse


RAW_KG_PATH = Path("dataset/raw/primekg/kg.csv")
TRAIN_SPLIT_PATH = Path("dataset/setting_a/01_split/train.tsv")

OUT_DIR = Path("dataset/setting_a/02_graph")
OUT_GRAPH_PATH = OUT_DIR / "train_enriched.tsv"
OUT_STATS_PATH = OUT_DIR / "graph_stats.json"
OUT_HUBS_PATH = OUT_DIR / "hub_filtered_genes.txt"

REPORT_PATH = Path("reports/week2/day3_graph_a_report.md")


def norm_text(x):
    return str(x).strip()


def norm_lower(x):
    return str(x).strip().lower()


def is_gene_type(t: str) -> bool:
    t = norm_lower(t)
    return t in {"gene/protein", "gene", "protein"}


def is_drug_type(t: str) -> bool:
    return norm_lower(t) == "drug"


def is_disease_type(t: str) -> bool:
    return norm_lower(t) == "disease"


def rel_match(df: pd.DataFrame, aliases) -> pd.Series:
    aliases = {a.strip().lower() for a in aliases}
    rel = df["relation"].astype(str).str.strip().str.lower()
    disp = df["display_relation"].astype(str).str.strip().str.lower()
    return rel.isin(aliases) | disp.isin(aliases)


def canonical_target(row):
    x_name, y_name = norm_text(row["x_name"]), norm_text(row["y_name"])
    x_type, y_type = norm_lower(row["x_type"]), norm_lower(row["y_type"])

    # Chuẩn hóa về drug -> gene/protein
    if is_drug_type(x_type) and is_gene_type(y_type):
        return (x_name, "target", y_name)
    if is_gene_type(x_type) and is_drug_type(y_type):
        return (y_name, "target", x_name)
    return None


def canonical_associated_with(row):
    x_name, y_name = norm_text(row["x_name"]), norm_text(row["y_name"])
    x_type, y_type = norm_lower(row["x_type"]), norm_lower(row["y_type"])

    # Chuẩn hóa về gene/protein -> disease
    if is_gene_type(x_type) and is_disease_type(y_type):
        return (x_name, "associated_with", y_name)
    if is_disease_type(x_type) and is_gene_type(y_type):
        return (y_name, "associated_with", x_name)
    return None


def canonical_ppi(row):
    x_name, y_name = norm_text(row["x_name"]), norm_text(row["y_name"])
    x_type, y_type = norm_lower(row["x_type"]), norm_lower(row["y_type"])

    if is_gene_type(x_type) and is_gene_type(y_type):
        return (x_name, "ppi", y_name)
    return None


def to_df(triples):
    if not triples:
        return pd.DataFrame(columns=["head", "relation", "tail"])
    df = pd.DataFrame(triples, columns=["head", "relation", "tail"])
    df = df.drop_duplicates().reset_index(drop=True)
    return df


def collapse_ppi_unordered(ppi_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    seen = set()

    for _, row in ppi_df.iterrows():
        u, v = row["head"], row["tail"]
        if u == v:
            continue
        a, b = sorted([u, v])
        key = (a, b)
        if key in seen:
            continue
        seen.add(key)
        rows.append((a, "ppi", b))

    return to_df(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max_gene_degree", type=int, default=500)
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    raw_df = pd.read_csv(RAW_KG_PATH, low_memory=False)
    train_df = pd.read_csv(TRAIN_SPLIT_PATH, sep="\t")

    # Chuẩn hóa train split
    train_df["head"] = train_df["head"].astype(str).str.strip()
    train_df["relation"] = train_df["relation"].astype(str).str.strip()
    train_df["tail"] = train_df["tail"].astype(str).str.strip()
    train_df = train_df.drop_duplicates().reset_index(drop=True)

    train_drugs = set(train_df["head"].tolist())
    train_diseases = set(train_df["tail"].tolist())

    # 1) TARGET edges connected to train drugs
    target_rows = raw_df[rel_match(raw_df, {"target"})].copy()

    target_triples = []
    for _, row in target_rows.iterrows():
        triple = canonical_target(row)
        if triple is None:
            continue
        h, _, _ = triple
        if h in train_drugs:
            target_triples.append(triple)

    target_df = to_df(target_triples)

    # 2) ASSOCIATED WITH edges connected to train diseases
    assoc_rows = raw_df[rel_match(raw_df, {"associated with", "associated_with"})].copy()

    assoc_triples = []
    for _, row in assoc_rows.iterrows():
        triple = canonical_associated_with(row)
        if triple is None:
            continue
        _, _, t = triple
        if t in train_diseases:
            assoc_triples.append(triple)

    assoc_df = to_df(assoc_triples)

    # 3) Candidate genes from target + associated_with
    genes_from_target = set(target_df["tail"].tolist()) if len(target_df) > 0 else set()
    genes_from_assoc = set(assoc_df["head"].tolist()) if len(assoc_df) > 0 else set()
    candidate_genes = genes_from_target | genes_from_assoc

    # 4) Full PPI rows
    ppi_rows = raw_df[rel_match(raw_df, {"ppi"})].copy()

    ppi_triples_all = []
    for _, row in ppi_rows.iterrows():
        triple = canonical_ppi(row)
        if triple is not None:
            ppi_triples_all.append(triple)

    ppi_all_df = to_df(ppi_triples_all)

    # 5) Compute gene degree on full PPI graph
    degree = {}
    for _, row in ppi_all_df.iterrows():
        u = row["head"]
        v = row["tail"]
        if u == v:
            continue
        degree[u] = degree.get(u, 0) + 1
        degree[v] = degree.get(v, 0) + 1

    filtered_hubs = sorted([g for g in candidate_genes if degree.get(g, 0) > args.max_gene_degree])
    allowed_genes = {g for g in candidate_genes if degree.get(g, 0) <= args.max_gene_degree}

    # 6) Filter target/assoc by allowed genes
    target_df = target_df[target_df["tail"].isin(allowed_genes)].reset_index(drop=True)
    assoc_df = assoc_df[assoc_df["head"].isin(allowed_genes)].reset_index(drop=True)

    # 7) PPI only within allowed genes
    ppi_df = ppi_all_df[
        ppi_all_df["head"].isin(allowed_genes) &
        ppi_all_df["tail"].isin(allowed_genes)
    ].copy().reset_index(drop=True)

    ppi_df = collapse_ppi_unordered(ppi_df)

    # 8) Final enriched train graph
    # Bao gồm luôn 8388 train indication triples
    support_df = pd.concat([target_df, assoc_df, ppi_df], ignore_index=True)
    support_df = support_df.drop_duplicates().reset_index(drop=True)

    enriched_df = pd.concat([train_df, support_df], ignore_index=True)
    enriched_df = enriched_df.drop_duplicates().reset_index(drop=True)
    enriched_df.to_csv(OUT_GRAPH_PATH, sep="\t", index=False)

    with open(OUT_HUBS_PATH, "w", encoding="utf-8") as f:
        for g in filtered_hubs:
            f.write(g + "\n")

    # 9) Stats
    entities = set(enriched_df["head"].tolist()) | set(enriched_df["tail"].tolist())
    relation_types = sorted(enriched_df["relation"].unique().tolist())

    drugs = set(train_df["head"].tolist()) | set(target_df["head"].tolist())
    diseases = set(train_df["tail"].tolist()) | set(assoc_df["tail"].tolist())
    genes = (
        set(target_df["tail"].tolist()) |
        set(assoc_df["head"].tolist()) |
        set(ppi_df["head"].tolist()) |
        set(ppi_df["tail"].tolist())
    )

    stats = {
        "source_train_split": str(TRAIN_SPLIT_PATH),
        "source_raw_kg": str(RAW_KG_PATH),
        "max_gene_degree": args.max_gene_degree,
        "num_train_indication_triples": int(len(train_df)),
        "num_target_triples": int(len(target_df)),
        "num_associated_with_triples": int(len(assoc_df)),
        "num_ppi_triples": int(len(ppi_df)),
        "num_support_triples_only": int(len(support_df)),
        "num_total_enriched_triples": int(len(enriched_df)),
        "num_relation_types": int(len(relation_types)),
        "relation_types": relation_types,
        "num_entities": int(len(entities)),
        "num_drugs": int(len(drugs)),
        "num_diseases": int(len(diseases)),
        "num_gene_protein": int(len(genes)),
        "num_candidate_genes_before_hub_cap": int(len(candidate_genes)),
        "num_genes_removed_by_hub_cap": int(len(filtered_hubs)),
        "num_genes_after_hub_cap": int(len(allowed_genes)),
    }

    with open(OUT_STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    report = f"""# Week 2 - Day 3 Graph A Report

## Goal
Enrich Setting A training graph in DrKGC style.

## Inputs
- Raw KG: `{RAW_KG_PATH}`
- Train split: `{TRAIN_SPLIT_PATH}`

## Output
- Enriched train graph: `{OUT_GRAPH_PATH}`

## Hub cap
- max_gene_degree: {args.max_gene_degree}

## Triple counts
- train indication: {len(train_df)}
- target: {len(target_df)}
- associated_with: {len(assoc_df)}
- ppi: {len(ppi_df)}
- support triples only: {len(support_df)}
- total enriched triples: {len(enriched_df)}

## Entity counts
- total entities: {len(entities)}
- drugs: {len(drugs)}
- diseases: {len(diseases)}
- gene/protein: {len(genes)}

## Relation types
- {relation_types}

## Hub filtering
- candidate genes before cap: {len(candidate_genes)}
- genes removed by hub cap: {len(filtered_hubs)}
- genes after cap: {len(allowed_genes)}

## Notes
- `train_enriched.tsv` includes both the 8388 train indication triples and the added support graph triples.
- `valid.tsv` and `test.tsv` remain unchanged.
"""

    REPORT_PATH.write_text(report, encoding="utf-8")

    print("Done.")
    print(f"Saved: {OUT_GRAPH_PATH}")
    print(f"Saved: {OUT_STATS_PATH}")
    print(f"Saved: {OUT_HUBS_PATH}")
    print(f"Saved: {REPORT_PATH}")
    print(f"train indication: {len(train_df)}")
    print(f"target: {len(target_df)}")
    print(f"associated_with: {len(assoc_df)}")
    print(f"ppi: {len(ppi_df)}")
    print(f"support only: {len(support_df)}")
    print(f"total enriched: {len(enriched_df)}")
    print(f"genes removed by hub cap: {len(filtered_hubs)}")


if __name__ == "__main__":
    main()