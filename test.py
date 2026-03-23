import json
from pathlib import Path

for name in ["valid_20_prompt.json", "test_20_prompt.json"]:
    path = Path("dataset/setting_a/05_prompt_subgraph_subset") / name
    data = json.loads(path.read_text(encoding="utf-8"))

    leak = 0
    for x in data:
        gold = x["triple_id"]
        if gold in x["subgraph"]:
            leak += 1

    print(name, "leak_count =", leak, "out of", len(data))