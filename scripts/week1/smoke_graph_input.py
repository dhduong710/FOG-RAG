import json
from pathlib import Path
import torch
from transformers import AutoTokenizer
from data.collate import QueryCollator
from model.gnn import GraphEnhancer

base = Path("dataset/toy_debug")
data = json.load(open(base / "train.json", "r", encoding="utf-8"))[:2]

tokenizer = AutoTokenizer.from_pretrained(
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    use_fast=False
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

tokenizer.add_tokens(['[QUERY]', '[ENTITY]', '[RELATION]'])

collator = QueryCollator(
    args=None,
    tokenizer=tokenizer,
    source_max_len=512,
    target_max_len=32
)

batch = collator(data)

entity_embeddings = torch.load(base / "entity_embeddings.pt")

graph_model = GraphEnhancer(
    kge_embedding=entity_embeddings,
    input_size=entity_embeddings.size(1),
    num_rels=8,
    gnn_hidden_dim=entity_embeddings.size(1),
    gnn_num_hidden_layers=1,
    adapter_size=32,
    output_size=64
)

query_embeds, entity_embeds = graph_model(
    batch["query_ids"],
    batch["entity_ids"],
    batch["subgraph"]
)

print("query_embeds shape:", query_embeds.shape)
print("entity_embeds shape:", entity_embeds.shape)