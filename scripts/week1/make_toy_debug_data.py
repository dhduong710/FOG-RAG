import json
from pathlib import Path
import torch

base = Path("dataset/toy_debug")
base.mkdir(parents=True, exist_ok=True)

entity_id_map = {
    "Losartan": 1,
    "Metformin": 2,
    "Aspirin": 3,
    "Lisinopril": 4,
    "Hypertension": 10,
    "Type 2 Diabetes": 11,
    "AGTR1": 20,
    "ACE": 21,
    "INSR": 22,
}

sample1 = {
    "input": (
        "You are a biomedical scientist. The task is to predict the answer based on the given question, "
        "and you only need to answer one entity. The answer must be in "
        "('Losartan', 'Metformin', 'Aspirin').\n"
        "You can refer to the entity embeddings: "
        "'Hypertension': [QUERY], "
        "'Losartan': [ENTITY], "
        "'Metformin': [ENTITY], "
        "'Aspirin': [ENTITY].\n\n"
        "Question: What drug can be used to treat hypertension?\n"
        "Answer: "
    ),
    "output": "Losartan",
    "query_entity_id": 10,
    "rank_entities_id": [1, 2, 3],
    "subgraph": [
        [1, 0, 20],
        [20, 1, 10],
        [3, 2, 10]
    ]
}

sample2 = {
    "input": (
        "You are a biomedical scientist. The task is to predict the answer based on the given question, "
        "and you only need to answer one entity. The answer must be in "
        "('Losartan', 'Metformin', 'Lisinopril').\n"
        "You can refer to the entity embeddings: "
        "'Type 2 Diabetes': [QUERY], "
        "'Losartan': [ENTITY], "
        "'Metformin': [ENTITY], "
        "'Lisinopril': [ENTITY].\n\n"
        "Question: What drug can be used to treat type 2 diabetes?\n"
        "Answer: "
    ),
    "output": "Metformin",
    "query_entity_id": 11,
    "rank_entities_id": [1, 2, 4],
    "subgraph": [
        [2, 3, 22],
        [22, 1, 11],
        [4, 2, 11]
    ]
}

train_data = [sample1, sample2]
valid_data = [sample1]
test_data = [sample2]

with open(base / "train.json", "w", encoding="utf-8") as f:
    json.dump(train_data, f, ensure_ascii=False, indent=2)

with open(base / "valid.json", "w", encoding="utf-8") as f:
    json.dump(valid_data, f, ensure_ascii=False, indent=2)

with open(base / "test.json", "w", encoding="utf-8") as f:
    json.dump(test_data, f, ensure_ascii=False, indent=2)

with open(base / "entity_id_map.json", "w", encoding="utf-8") as f:
    json.dump(entity_id_map, f, ensure_ascii=False, indent=2)

# random toy embeddings: 100 entities, dim 16
torch.manual_seed(42)
entity_embeddings = torch.randn(100, 16)
torch.save(entity_embeddings, base / "entity_embeddings.pt")

print("Toy dataset created at:", base)
print("Files:")
print("-", base / "train.json")
print("-", base / "valid.json")
print("-", base / "test.json")
print("-", base / "entity_embeddings.pt")
print("-", base / "entity_id_map.json")