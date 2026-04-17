from pathlib import Path
import pandas as pd

IN_PATH = Path("dataset/raw/primekg/kg.csv")
OUT_PATH = Path("dataset/setting_a/00_raw_triples/primekg_indication_only.tsv")
REPORT_PATH = Path("reports/week2/day1_extract_report.md")

REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(IN_PATH, low_memory=False)

print("Columns:")
print(df.columns.tolist())

# Tìm tên cột an toàn hơn giữa các version
def pick_col(candidates, columns):
    for c in candidates:
        if c in columns:
            return c
    return None

head_name_col = pick_col(["x_name", "source", "head", "x_id"], df.columns)
tail_name_col = pick_col(["y_name", "target", "tail", "y_id"], df.columns)
head_type_col = pick_col(["x_type", "source_type", "head_type"], df.columns)
tail_type_col = pick_col(["y_type", "target_type", "tail_type"], df.columns)
relation_col = pick_col(["relation", "display_relation"], df.columns)
display_relation_col = pick_col(["display_relation", "relation"], df.columns)

assert head_name_col is not None, "Cannot find head entity column"
assert tail_name_col is not None, "Cannot find tail entity column"
assert head_type_col is not None, "Cannot find head type column"
assert tail_type_col is not None, "Cannot find tail type column"
assert relation_col is not None, "Cannot find relation column"

# Chuẩn hóa string để lọc an toàn hơn
tmp = df.copy()
for c in [head_type_col, tail_type_col, relation_col]:
    tmp[c] = tmp[c].astype(str).str.strip().str.lower()

if display_relation_col in tmp.columns:
    tmp[display_relation_col] = tmp[display_relation_col].astype(str).str.strip().str.lower()

# Ưu tiên lọc theo relation/display_relation = indication
rel_mask = (tmp[relation_col] == "indication")
if display_relation_col in tmp.columns:
    rel_mask = rel_mask | (tmp[display_relation_col] == "indication")

subset = tmp[
    (tmp[head_type_col] == "drug") &
    (tmp[tail_type_col] == "disease") &
    rel_mask
].copy()

# Xuất đúng 3 cột chuẩn cho bước tuần 2
out = pd.DataFrame({
    "head": subset[head_name_col].astype(str),
    "relation": "indication",
    "tail": subset[tail_name_col].astype(str),
})

out = out.drop_duplicates().reset_index(drop=True)
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
out.to_csv(OUT_PATH, sep="\t", index=False)

num_triples = len(out)
num_drugs = out["head"].nunique()
num_diseases = out["tail"].nunique()
rel_names = sorted(out["relation"].unique().tolist())

report = f"""# Extract Report

## Input
- Source file: {IN_PATH}

## Output
- Output file: {OUT_PATH}

## Stats
- indication triples: {num_triples}
- unique drugs: {num_drugs}
- unique diseases: {num_diseases}
- relation names: {rel_names}

## Notes
- Goal for DrKGC-compatible extraction: around 9388 triples
- If this number is far away from 9388, inspect column mapping and filtering logic immediately.
"""

REPORT_PATH.write_text(report, encoding="utf-8")

print(f"Saved: {OUT_PATH}")
print(f"Saved: {REPORT_PATH}")
print("triples:", num_triples)
print("unique drugs:", num_drugs)
print("unique diseases:", num_diseases)
print("relation names:", rel_names)