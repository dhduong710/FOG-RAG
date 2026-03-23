from pathlib import Path
import pandas as pd

path = Path("data_raw/primekg/kg.csv")
assert path.exists(), f"Not found: {path}"

df = pd.read_csv(path, low_memory=False)
print("shape:", df.shape)
print("columns:", df.columns.tolist())
print(df.head(3).to_string())