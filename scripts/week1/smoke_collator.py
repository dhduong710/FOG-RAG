import json
from pathlib import Path
from transformers import AutoTokenizer
from data.collate import QueryCollator

base = Path("dataset/toy_debug")
data = json.load(open(base / "train.json", "r", encoding="utf-8"))[:2]

# Dùng tokenizer public, nhẹ hơn cho smoke test.
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

query_tok_id = tokenizer.convert_tokens_to_ids('[QUERY]')
entity_tok_id = tokenizer.convert_tokens_to_ids('[ENTITY]')

print("=== batch keys / shapes ===")
for k, v in batch.items():
    if hasattr(v, "shape"):
        print(k, v.shape)
    else:
        print(k, type(v), len(v))

print("\n=== placeholder count check ===")
num_query_tokens = (batch["input_ids"] == query_tok_id).sum().item()
num_entity_tokens = (batch["input_ids"] == entity_tok_id).sum().item()

batch_size = len(data)
K = len(data[0]["rank_entities_id"])

print("num [QUERY] tokens in batch:", num_query_tokens)
print("expected [QUERY] tokens:", batch_size)

print("num [ENTITY] tokens in batch:", num_entity_tokens)
print("expected [ENTITY] tokens:", batch_size * K)

print("\n=== tensor content check ===")
print("query_ids:", batch["query_ids"])
print("entity_ids:", batch["entity_ids"])
print("subgraph[0]:", batch["subgraph"][0])