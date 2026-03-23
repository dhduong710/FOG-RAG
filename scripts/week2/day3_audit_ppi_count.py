from pathlib import Path
import pandas as pd
import json
import argparse

RAW_KG_PATH = Path("dataset/raw/primekg/kg.csv")
TRAIN_SPLIT_PATH = Path("dataset/setting_a/01_split/train.tsv")
OUT_DIR = Path("dataset/setting_a/02_graph_audit")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def norm_text(x):
    return str(x).strip()


def norm_lower(x):
    return str(x).strip().lower()


def is_gene_type(t: str) -> bool:
    return norm_lower(t) in {"gene/protein", "gene", "protein"}


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

    if is_drug_type(x_type) and is_gene_type(y_type):
        return (x_name, "target", y_name)
    if is_gene_type(x_type) and is_drug_type(y_type):
        return (y_name, "target", x_name)
    return None


def canonical_associated_with(row):
    x_name, y_name = norm_text(row["x_name"]), norm_text(row["y_name"])
    x_type, y_type = norm_lower(row["x_type"]), norm_lower(row["y_type"])

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
    return df.drop_duplicates().reset_index(drop=True)


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


def mutual_only_collapsed(ppi_df: pd.DataFrame) -> pd.DataFrame:
    directed = set(map(tuple, ppi_df[["head", "relation", "tail"]].values.tolist()))
    rows = []
    seen = set()

    for u, _, v in directed:
        if u == v:
            continue
        if (v, "ppi", u) in directed:
            a, b = sorted([u, v])
            key = (a, b)
            if key not in seen:
                seen.add(key)
                rows.append((a, "ppi", b))
    return to_df(rows)


def count_entities(df: pd.DataFrame) -> int:
    return len(set(df["head"].tolist()) | set(df["tail"].tolist()))


def build_variant(train_df, target_df, assoc_df, ppi_df, name):
    out = pd.concat([train_df, target_df, assoc_df, ppi_df], ignore_index=True)
    out = out.drop_duplicates().reset_index(drop=True)
    return {
        "name": name,
        "train_indication": int(len(train_df)),
        "target": int(len(target_df)),
        "associated_with": int(len(assoc_df)),
        "ppi": int(len(ppi_df)),
        "total": int(len(out)),
        "entities": int(count_entities(out)),
        "relations": sorted(out["relation"].unique().tolist()),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max_gene_degree", type=int, default=500)
    args = parser.parse_args()

    raw_df = pd.read_csv(RAW_KG_PATH, low_memory=False)
    train_df = pd.read_csv(TRAIN_SPLIT_PATH, sep="\t").drop_duplicates().reset_index(drop=True)

    train_df["head"] = train_df["head"].astype(str).str.strip()
    train_df["relation"] = train_df["relation"].astype(str).str.strip()
    train_df["tail"] = train_df["tail"].astype(str).str.strip()

    train_drugs = set(train_df["head"].tolist())
    train_diseases = set(train_df["tail"].tolist())

    target_rows = raw_df[rel_match(raw_df, {"target"})].copy()
    assoc_rows = raw_df[rel_match(raw_df, {"associated with", "associated_with"})].copy()
    ppi_rows = raw_df[rel_match(raw_df, {"ppi"})].copy()

    target_triples = []
    for _, row in target_rows.iterrows():
        triple = canonical_target(row)
        if triple and triple[0] in train_drugs:
            target_triples.append(triple)

    assoc_triples = []
    for _, row in assoc_rows.iterrows():
        triple = canonical_associated_with(row)
        if triple and triple[2] in train_diseases:
            assoc_triples.append(triple)

    ppi_triples_all = []
    for _, row in ppi_rows.iterrows():
        triple = canonical_ppi(row)
        if triple:
            ppi_triples_all.append(triple)

    target_df = to_df(target_triples)
    assoc_df = to_df(assoc_triples)
    ppi_all_df = to_df(ppi_triples_all)

    genes_from_target = set(target_df["tail"].tolist())
    genes_from_assoc = set(assoc_df["head"].tolist())
    candidate_genes = genes_from_target | genes_from_assoc

    degree = {}
    for _, row in ppi_all_df.iterrows():
        u, v = row["head"], row["tail"]
        if u == v:
            continue
        degree[u] = degree.get(u, 0) + 1
        degree[v] = degree.get(v, 0) + 1

    allowed_genes = {g for g in candidate_genes if degree.get(g, 0) <= args.max_gene_degree}

    target_df = target_df[target_df["tail"].isin(allowed_genes)].reset_index(drop=True)
    assoc_df = assoc_df[assoc_df["head"].isin(allowed_genes)].reset_index(drop=True)
    ppi_df = ppi_all_df[
        ppi_all_df["head"].isin(allowed_genes) &
        ppi_all_df["tail"].isin(allowed_genes)
    ].copy().reset_index(drop=True)

    raw_directed_unique = len(ppi_df)
    raw_self_loops = int((ppi_df["head"] == ppi_df["tail"]).sum())

    unordered_keys = {
        tuple(sorted([row["head"], row["tail"]]))
        for _, row in ppi_df.iterrows()
        if row["head"] != row["tail"]
    }

    directed_set = set(map(tuple, ppi_df[["head", "relation", "tail"]].values.tolist()))
    reverse_pairs = 0
    seen = set()
    for u, _, v in directed_set:
        if u == v:
            continue
        key = tuple(sorted([u, v]))
        if key in seen:
            continue
        if (v, "ppi", u) in directed_set:
            reverse_pairs += 1
        seen.add(key)

    ppi_collapsed_df = collapse_ppi_unordered(ppi_df)
    ppi_mutual_collapsed_df = mutual_only_collapsed(ppi_df)

    variants = [
        build_variant(train_df, target_df, assoc_df, ppi_df, "A_directed_ppi"),
        build_variant(train_df, target_df, assoc_df, ppi_collapsed_df, "B_collapsed_unordered_ppi"),
        build_variant(train_df, target_df, assoc_df, ppi_mutual_collapsed_df, "C_mutual_collapsed_ppi"),
    ]

    audit = {
        "max_gene_degree": args.max_gene_degree,
        "target_count": int(len(target_df)),
        "associated_with_count": int(len(assoc_df)),
        "ppi_audit": {
            "filtered_ppi_directed_unique": int(raw_directed_unique),
            "filtered_ppi_self_loops": int(raw_self_loops),
            "filtered_ppi_unordered_unique": int(len(unordered_keys)),
            "filtered_ppi_unordered_pairs_with_reverse": int(reverse_pairs),
        },
        "variants": variants,
    }

    out_json = OUT_DIR / "ppi_audit.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2, ensure_ascii=False)

    print(json.dumps(audit, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()