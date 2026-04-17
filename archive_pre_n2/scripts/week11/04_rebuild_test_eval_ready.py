import json
import shutil
import hashlib
from pathlib import Path

SRC = {
    "backbone": Path("dataset/setting_a/19_contra_aware_eval_ready_test/backbone"),
    "ontology": Path("dataset/setting_a/19_contra_aware_eval_ready_test/ontology"),
    "hard_main": Path("dataset/setting_a/19_contra_aware_eval_ready_test/hard_main"),
    "soft_best": Path("dataset/setting_a/19_contra_aware_eval_ready_test/soft_best"),
}

DST_ROOT = Path("dataset/setting_a/20_test_rerun_eval_ready")


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def first_info(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not data:
        return None, None, 0
    first_triple = data[0].get("triple")
    first_top5 = data[0].get("rank_entities", [])[:5]
    return first_triple, first_top5, len(data)


def main():
    DST_ROOT.mkdir(parents=True, exist_ok=True)

    for name, src in SRC.items():
        if not src.exists():
            raise FileNotFoundError(f"Missing source package: {src}")

        dst = DST_ROOT / name
        if dst.exists():
            shutil.rmtree(dst)

        shutil.copytree(src, dst)

        test_json = dst / "test.json"
        valid_json = dst / "valid.json"
        train_json = dst / "train.json"

        assert train_json.exists(), f"Missing {train_json}"
        assert valid_json.exists(), f"Missing {valid_json}"
        assert test_json.exists(), f"Missing {test_json}"

        first_triple, first_top5, n = first_info(test_json)

        print("=" * 100)
        print(name)
        print("src:", src)
        print("dst:", dst)
        print("num_rows:", n)
        print("test hash:", md5(test_json))
        print("first triple:", first_triple)
        print("first top5:", first_top5)

    print("\nDone. Clean rerun packages created at:")
    print(DST_ROOT)


if __name__ == "__main__":
    main()