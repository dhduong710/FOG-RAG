import json
from pathlib import Path

base = Path("dataset/toy_debug")

for split in ["train.json", "valid.json", "test.json"]:
    path = base / split
    data = json.load(open(path, "r", encoding="utf-8"))
    print("=" * 60)
    print(split, "num samples =", len(data))

    ex = data[0]
    print("keys:", list(ex.keys()))
    print("input preview:", ex["input"][:250])
    print("output:", ex["output"])
    print("query_entity_id:", ex["query_entity_id"])
    print("num rank_entities_id:", len(ex["rank_entities_id"]))
    print("num subgraph triples:", len(ex["subgraph"]))