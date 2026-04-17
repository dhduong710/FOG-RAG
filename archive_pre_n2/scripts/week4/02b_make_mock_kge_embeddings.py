import pickle
from pathlib import Path
import torch

ENTITY2ID_PATH = Path("dataset/setting_a/04_drkgc_json/entity2id.pkl")
OUT_PATH = Path("dataset/setting_a/07_pilot_ready/mock_entity_embeddings.pt")
DIM = 200
SEED = 2025

def main():
    torch.manual_seed(SEED)
    with open(ENTITY2ID_PATH, "rb") as f:
        entity2id = pickle.load(f)

    num_entities = len(entity2id)
    emb = torch.randn(num_entities, DIM) * 0.02

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    torch.save(emb, OUT_PATH)

    print("num_entities:", num_entities)
    print("dim:", DIM)
    print("saved:", OUT_PATH)

if __name__ == "__main__":
    main()