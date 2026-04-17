from __future__ import annotations

import json
import math
import pickle
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import torch


ROOT = Path(".")


def load_pickle(path: Path):
    with path.open("rb") as f:
        return pickle.load(f)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_exists(paths: List[Path]) -> List[Path]:
    return [p for p in paths if not p.exists()]


def split_unique_drugs(split_train_path: Path) -> List[str]:
    df = pd.read_csv(split_train_path, sep="\t")
    df["head"] = df["head"].astype(str).str.strip()
    return sorted(df["head"].drop_duplicates().tolist())


def summarize_score_tensor(scores: torch.Tensor) -> Dict:
    scores = scores.float()
    finite = torch.isfinite(scores)
    summary = {
        "shape": list(scores.shape),
        "all_finite": bool(finite.all().item()),
        "min": float(scores.min().item()) if finite.any() else None,
        "max": float(scores.max().item()) if finite.any() else None,
        "mean": float(scores.mean().item()) if finite.any() else None,
        "std": float(scores.std().item()) if finite.any() else None,
    }
    return summary


def compute_top1_ratio(score_obj: Dict) -> float:
    scores = score_obj["scores"]
    gold_ids = score_obj["gold_entity_ids"]
    cand_ids = score_obj["candidate_entity_ids"]
    top1_idx = scores.argmax(dim=1)
    pred_ids = cand_ids[top1_idx]
    return float((pred_ids == gold_ids).float().mean().item())


def inspect_checkpoint(ckpt_path: Path, entity2id_path: Path, relation2id_path: Path) -> Tuple[List[str], Dict]:
    errors = []
    ckpt = torch.load(ckpt_path, map_location="cpu")

    required_keys = [
        "node_embeddings",
        "relation_embeddings",
        "drug_universe_names",
        "drug_universe_ids",
    ]
    for k in required_keys:
        if k not in ckpt:
            errors.append(f"checkpoint missing key: {k}")

    entity2id = load_pickle(entity2id_path)
    relation2id = load_pickle(relation2id_path)

    meta = {
        "checkpoint_keys": sorted(list(ckpt.keys())),
        "num_entities_expected": len(entity2id),
        "num_relations_expected": len(relation2id),
    }

    if "node_embeddings" in ckpt:
        node_emb = ckpt["node_embeddings"]
        meta["node_embeddings_shape"] = list(node_emb.shape)
        if node_emb.shape[0] != len(entity2id):
            errors.append(
                f"node_embeddings first dim mismatch: got {node_emb.shape[0]}, expected {len(entity2id)}"
            )

    if "relation_embeddings" in ckpt:
        rel_emb = ckpt["relation_embeddings"]
        meta["relation_embeddings_shape"] = list(rel_emb.shape)
        if rel_emb.shape[0] != len(relation2id):
            errors.append(
                f"relation_embeddings first dim mismatch: got {rel_emb.shape[0]}, expected {len(relation2id)}"
            )

    if "drug_universe_names" in ckpt and "drug_universe_ids" in ckpt:
        if len(ckpt["drug_universe_names"]) != len(ckpt["drug_universe_ids"]):
            errors.append("drug_universe_names and drug_universe_ids length mismatch")
        meta["drug_universe_size_in_checkpoint"] = len(ckpt["drug_universe_names"])

    return errors, meta


def inspect_score_file(
    score_path: Path,
    split_path: Path,
    expected_drug_names: List[str],
    relation_name_expected: str = "indication",
) -> Tuple[List[str], List[str], Dict]:
    errors = []
    warnings = []

    obj = torch.load(score_path, map_location="cpu")

    required_keys = [
        "split",
        "relation_name",
        "query_entity_names",
        "query_entity_ids",
        "gold_entity_names",
        "gold_entity_ids",
        "candidate_entity_names",
        "candidate_entity_ids",
        "scores",
    ]
    for k in required_keys:
        if k not in obj:
            errors.append(f"{score_path.name} missing key: {k}")

    if errors:
        return errors, warnings, {"path": str(score_path)}

    split_df = pd.read_csv(split_path, sep="\t")
    expected_num_queries = len(split_df)
    actual_num_queries = len(obj["query_entity_names"])
    actual_num_candidates = len(obj["candidate_entity_names"])
    expected_num_candidates = len(expected_drug_names)

    scores = obj["scores"]
    score_summary = summarize_score_tensor(scores)

    if obj["relation_name"] != relation_name_expected:
        errors.append(
            f"{score_path.name} relation_name mismatch: got {obj['relation_name']}, expected {relation_name_expected}"
        )

    if actual_num_queries != expected_num_queries:
        errors.append(
            f"{score_path.name} num_queries mismatch: got {actual_num_queries}, expected {expected_num_queries}"
        )

    if actual_num_candidates != expected_num_candidates:
        errors.append(
            f"{score_path.name} num_candidates mismatch: got {actual_num_candidates}, expected {expected_num_candidates}"
        )

    if list(scores.shape) != [expected_num_queries, expected_num_candidates]:
        errors.append(
            f"{score_path.name} score tensor shape mismatch: got {list(scores.shape)}, expected {[expected_num_queries, expected_num_candidates]}"
        )

    if not score_summary["all_finite"]:
        errors.append(f"{score_path.name} contains non-finite scores")

    if score_summary["std"] is not None and score_summary["std"] == 0.0:
        errors.append(f"{score_path.name} scores are constant (std = 0.0)")

    # candidate universe should match train split head universe exactly
    cand_names = list(obj["candidate_entity_names"])
    if set(cand_names) != set(expected_drug_names):
        warnings.append(
            f"{score_path.name} candidate universe differs from train split unique head set"
        )

    top1_ratio = compute_top1_ratio(obj)
    if score_path.name == "valid_scores.pt" and top1_ratio >= 0.999:
        warnings.append(
            f"{score_path.name} raw top1 ratio is suspiciously high: {top1_ratio:.6f}"
        )

    meta = {
        "path": str(score_path),
        "split_name": obj["split"],
        "expected_num_queries": expected_num_queries,
        "actual_num_queries": actual_num_queries,
        "expected_num_candidates": expected_num_candidates,
        "actual_num_candidates": actual_num_candidates,
        "score_summary": score_summary,
        "raw_top1_ratio": round(top1_ratio, 6),
    }
    return errors, warnings, meta


def build_markdown(report: Dict) -> str:
    status = report["final_decision"]
    overall = report["overall"]
    checkpoint = report["checkpoint"]
    input_readiness = report["input_readiness"]
    score_files = report["score_files"]

    def join_lines(xs):
        return "\n".join(xs) if xs else "- none"

    lines = []
    lines.append("# Week 6 - Day 2 Completion Check")
    lines.append("")
    lines.append(f"## Final decision: **{status}**")
    lines.append("")
    lines.append("## 1. Overall summary")
    lines.append(f"- passed_checks: {overall['passed_checks']}")
    lines.append(f"- failed_checks: {overall['failed_checks']}")
    lines.append(f"- warnings: {overall['warnings_count']}")
    lines.append("")
    lines.append("## 2. Required input readiness")
    lines.append(f"- ready: {input_readiness['ready']}")
    if input_readiness["missing"]:
        lines.append("- missing inputs:")
        for x in input_readiness["missing"]:
            lines.append(f"  - `{x}`")
    else:
        lines.append("- missing inputs: none")
    lines.append("")
    lines.append("## 3. Checkpoint inspection")
    lines.append(f"- checkpoint path: `{checkpoint['path']}`")
    for k, v in checkpoint["meta"].items():
        lines.append(f"- {k}: {v}")
    if checkpoint["errors"]:
        lines.append("- checkpoint errors:")
        for x in checkpoint["errors"]:
            lines.append(f"  - {x}")
    else:
        lines.append("- checkpoint errors: none")
    lines.append("")
    lines.append("## 4. Score file inspection")
    for split_name, obj in score_files.items():
        lines.append(f"### {split_name}")
        lines.append(f"- path: `{obj['meta']['path']}`")
        for k, v in obj["meta"].items():
            if k == "path":
                continue
            lines.append(f"- {k}: {v}")
        if obj["errors"]:
            lines.append("- errors:")
            for x in obj["errors"]:
                lines.append(f"  - {x}")
        else:
            lines.append("- errors: none")
        if obj["warnings"]:
            lines.append("- warnings:")
            for x in obj["warnings"]:
                lines.append(f"  - {x}")
        else:
            lines.append("- warnings: none")
        lines.append("")
    lines.append("## 5. End-of-day interpretation")
    lines.append(join_lines([f"- {x}" for x in report["interpretation"]]))
    lines.append("")
    lines.append("## 6. Next step")
    lines.append("- If GO: move to day 3 and build `top20_raw` / `top20_drkgc_ready`.")
    lines.append("- If CONDITIONAL GO: fix warnings first if they affect scientific interpretation.")
    lines.append("- If NO-GO: do not move to day 3 before fixing checkpoint/score dump issues.")
    lines.append("")
    return "\n".join(lines)


def main():
    train_graph = ROOT / "dataset/setting_a/02_graph/train_enriched_deg1000_final.tsv"
    split_train = ROOT / "dataset/setting_a/01_split/train.tsv"
    split_valid = ROOT / "dataset/setting_a/01_split/valid.tsv"
    split_test = ROOT / "dataset/setting_a/01_split/test.tsv"
    entity2id_path = ROOT / "dataset/setting_a/04_drkgc_json/entity2id.pkl"
    id2entity_path = ROOT / "dataset/setting_a/04_drkgc_json/id2entity.pkl"
    relation2id_path = ROOT / "dataset/setting_a/04_drkgc_json/relation2id.pkl"
    id2relation_path = ROOT / "dataset/setting_a/04_drkgc_json/id2relation.pkl"

    ckpt_path = ROOT / "dataset/setting_a/09_real_coarse_ranker/rgcn_ranker_checkpoint.pt"
    scorer_meta_path = ROOT / "dataset/setting_a/09_real_coarse_ranker/scorer_meta.json"
    train_scores_path = ROOT / "dataset/setting_a/09_real_coarse_ranker/train_scores.pt"
    valid_scores_path = ROOT / "dataset/setting_a/09_real_coarse_ranker/valid_scores.pt"
    test_scores_path = ROOT / "dataset/setting_a/09_real_coarse_ranker/test_scores.pt"
    score_dump_meta_path = ROOT / "dataset/setting_a/09_real_coarse_ranker/score_dump_meta.json"

    report_path = ROOT / "reports/week6/day2_check_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    required_inputs = [
        train_graph,
        split_train,
        split_valid,
        split_test,
        entity2id_path,
        id2entity_path,
        relation2id_path,
        id2relation_path,
    ]
    missing_inputs = ensure_exists(required_inputs)

    required_outputs = [
        ckpt_path,
        scorer_meta_path,
        train_scores_path,
        valid_scores_path,
        test_scores_path,
        score_dump_meta_path,
    ]
    missing_outputs = ensure_exists(required_outputs)

    report = {
        "input_readiness": {
            "ready": len(missing_inputs) == 0,
            "missing": [str(x) for x in missing_inputs],
        },
        "checkpoint": {
            "path": str(ckpt_path),
            "errors": [],
            "meta": {},
        },
        "score_files": {},
        "overall": {
            "passed_checks": 0,
            "failed_checks": 0,
            "warnings_count": 0,
        },
        "interpretation": [],
        "final_decision": "NO-GO",
    }

    if missing_inputs:
        report["interpretation"].append("Input readiness chưa đạt: thiếu file nền từ các tuần trước.")
    if missing_outputs:
        report["interpretation"].append("Output ngày 2 chưa đủ: bạn chưa thể coi ngày 2 là hoàn thành.")

    if not missing_inputs and not missing_outputs:
        ckpt_errors, ckpt_meta = inspect_checkpoint(ckpt_path, entity2id_path, relation2id_path)
        report["checkpoint"]["errors"] = ckpt_errors
        report["checkpoint"]["meta"] = ckpt_meta

        expected_drugs = split_unique_drugs(split_train)

        score_specs = {
            "train": (train_scores_path, split_train),
            "valid": (valid_scores_path, split_valid),
            "test": (test_scores_path, split_test),
        }

        total_errors = list(ckpt_errors)
        total_warnings = []

        for split_name, (score_path, split_path) in score_specs.items():
            errs, warns, meta = inspect_score_file(score_path, split_path, expected_drugs)
            report["score_files"][split_name] = {
                "errors": errs,
                "warnings": warns,
                "meta": meta,
            }
            total_errors.extend(errs)
            total_warnings.extend(warns)

        report["overall"]["failed_checks"] = len(total_errors)
        report["overall"]["warnings_count"] = len(total_warnings)

        if len(total_errors) == 0:
            report["overall"]["passed_checks"] = 1
            if len(total_warnings) == 0:
                report["final_decision"] = "GO"
                report["interpretation"].append(
                    "Ngày 2 đạt: scorer thật đã train/export được và score dump cho train/valid/test dùng được."
                )
                report["interpretation"].append(
                    "Bạn có thể sang ngày 3 để build top20_raw và top20_drkgc_ready."
                )
            else:
                report["final_decision"] = "CONDITIONAL GO"
                report["interpretation"].append(
                    "Ngày 2 về mặt kỹ thuật đạt, nhưng còn warning cần lưu ý trước khi diễn giải khoa học."
                )
                report["interpretation"].append(
                    "Bạn vẫn có thể sang ngày 3, nhưng phải đọc kỹ candidate recall/top1 ratio/rank distribution."
                )
        else:
            report["final_decision"] = "NO-GO"
            report["interpretation"].append(
                "Ngày 2 chưa đạt: checkpoint hoặc score dump còn lỗi cấu trúc / shape / finite / candidate universe."
            )
            report["interpretation"].append(
                "Chưa nên sang ngày 3 trước khi sửa các lỗi cứng này."
            )

    md = build_markdown(report)
    report_path.write_text(md, encoding="utf-8")

    print("=" * 80)
    print("WEEK 6 - DAY 2 COMPLETION CHECK")
    print("=" * 80)
    print("Final decision:", report["final_decision"])
    print("Report saved to:", report_path)
    print("=" * 80)

    if report["input_readiness"]["missing"]:
        print("Missing inputs:")
        for x in report["input_readiness"]["missing"]:
            print(" -", x)

    if missing_outputs:
        print("Missing outputs:")
        for x in missing_outputs:
            print(" -", x)

    if report["checkpoint"]["errors"]:
        print("Checkpoint errors:")
        for x in report["checkpoint"]["errors"]:
            print(" -", x)

    for split_name, obj in report["score_files"].items():
        if obj["errors"]:
            print(f"{split_name} errors:")
            for x in obj["errors"]:
                print(" -", x)
        if obj["warnings"]:
            print(f"{split_name} warnings:")
            for x in obj["warnings"]:
                print(" -", x)

    print("=" * 80)
    for line in report["interpretation"]:
        print("-", line)
    print("=" * 80)


if __name__ == "__main__":
    main()