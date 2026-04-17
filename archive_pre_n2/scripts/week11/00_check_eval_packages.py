import json
import hashlib
from pathlib import Path

PACKAGES = {
    "backbone": "dataset/setting_a/12_backbone_ready_ranker_v2",
    "ontology": "dataset/setting_a/18_ontology_only_eval_ready",
    "hard_main": "dataset/setting_a/19_contra_aware_eval_ready/hard_main",
    "soft_best": "dataset/setting_a/19_contra_aware_eval_ready/soft_best",
}

def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()

def first_triple(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not data:
        return None
    return data[0].get("triple")

for name, pkg in PACKAGES.items():
    pkg = Path(pkg)
    valid_path = pkg / "valid.json"
    test_path = pkg / "test.json"

    assert valid_path.exists(), f"Missing {valid_path}"
    assert test_path.exists(), f"Missing {test_path}"

    valid_hash = md5(valid_path)
    test_hash = md5(test_path)

    print("=" * 100)
    print(name)
    print("package:", pkg)
    print("valid hash:", valid_hash)
    print("test  hash:", test_hash)
    print("valid == test ?", valid_hash == test_hash)
    print("valid first triple:", first_triple(valid_path))
    print("test  first triple:", first_triple(test_path))