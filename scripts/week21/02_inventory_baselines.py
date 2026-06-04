#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Week 21 Day 2
Baseline inventory audit.

Goal:
- Find old artifacts for TransE / ComplEx / R-GCN / HRGAT / optional DistMult / RotatE.
- Determine whether each baseline can be recollected or must be rerun.
- Do NOT recompute reviewer-safe metrics today.
- Do NOT change the main row.
"""

from __future__ import annotations

import csv
import json
import math
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(".")
RESULTS_DIR = ROOT / "results" / "week21"
REPORTS_DIR = ROOT / "reports" / "week21"

OUT_JSON = RESULTS_DIR / "baseline_inventory.json"
OUT_MD = REPORTS_DIR / "day2_baseline_inventory.md"

SCAN_ROOTS = [
    ROOT / "results",
    ROOT / "dataset",
    ROOT / "reports",
    ROOT / "scripts",
    ROOT / "archive_pre_n2",
]

IGNORE_DIR_PARTS = {
    ".git",
    "__pycache__",
    ".ipynb_checkpoints",
    "node_modules",
    ".venv",
    "venv",
    "env",
    "wandb",
    "runs",
    "cache",
    ".cache",
}

TEXT_SUFFIXES = {".txt", ".md", ".log"}
TABLE_SUFFIXES = {".csv", ".tsv"}
JSON_SUFFIXES = {".json", ".jsonl"}
MODEL_SUFFIXES = {".pt", ".pth", ".bin", ".ckpt", ".safetensors"}
PY_SUFFIXES = {".py"}
SUPPORTED_SUFFIXES = TEXT_SUFFIXES | TABLE_SUFFIXES | JSON_SUFFIXES | MODEL_SUFFIXES | PY_SUFFIXES

MAX_JSON_LOAD_MB = 200
MAX_TEXT_READ_MB = 20
MAX_CONTENT_CHARS = 200_000

MODEL_ALIASES = {
    "TransE": ["transe", "trans-e", "trans_e"],
    "ComplEx": ["complex", "compl-ex", "compl_ex"],
    "R-GCN": ["r-gcn", "rgcn", "r_gcn", "relgraphconv"],
    "HRGAT": ["hrgat", "h-rgat", "h_rgat"],
    "DistMult": ["distmult", "dist-mult", "dist_mult"],
    "RotatE": ["rotate", "rotat-e", "rotat_e"],
}

CORE_MODELS = ["TransE", "ComplEx", "R-GCN", "HRGAT"]
OPTIONAL_MODELS = ["DistMult", "RotatE"]
ALL_MODELS = CORE_MODELS + OPTIONAL_MODELS

CANDIDATE_FIELDS = [
    "candidate_entities",
    "candidate_entity_ids",
    "candidate_entities_top20",
    "candidate_entity_ids_top20",
    "rank_entities",
    "rank_entities_id",
    "rank_entities_ids",
    "rank_entities_name",
    "rank_entities_names",
    "candidates",
    "candidate_ids",
    "top20",
    "top20_entities",
    "top20_entity_ids",
    "prediction",
    "predictions",
]

SCORE_FIELDS = [
    "scores",
    "scores_top20",
    "candidate_scores",
    "top20_scores",
    "score",
    "rank_scores",
    "full_scores",
    "drug_scores",
]

GOLD_FIELDS = [
    "gold_entity",
    "gold_entity_id",
    "target",
    "target_id",
    "answer",
    "answer_id",
    "gold",
    "gold_id",
]

QUERY_FIELDS = [
    "query_entity",
    "query_entity_id",
    "disease",
    "disease_id",
    "tail",
    "tail_id",
    "triple",
    "triple_id",
]

RANK_FIELDS = [
    "gold_rank",
    "gold_rank_in_top20",
    "gold_rank_in_top20_or_21",
    "gold_rank_in_full_universe",
    "rank",
    "rank_ready",
    "rank_raw",
]

INJECTION_HINT_FIELDS = [
    "gold_injected",
    "inject_ratio",
    "injected",
    "gold_in_topk_ready",
    "gold_in_topk_raw",
]

FOGRAG_REFERENCE_PATHS = {
    "raw_valid": "dataset/setting_a/23_noinj_source/valid_top20_raw.json",
    "raw_test": "dataset/setting_a/23_noinj_source/test_top20_raw.json",
    "eval_valid_backbone": "dataset/setting_b/07_n2_eval_valid/valid_backbone_raw_eval.json",
    "eval_valid_soft": "dataset/setting_b/07_n2_eval_valid/valid_soft_support_raw_eval.json",
    "eval_valid_retrieval": "dataset/setting_b/07_n2_eval_valid/valid_retrieval_main_eval.json",
    "eval_test_backbone": "dataset/setting_b/08_n2_eval_test/test_backbone_raw_eval.json",
    "eval_test_soft": "dataset/setting_b/08_n2_eval_test/test_soft_support_raw_eval.json",
    "eval_test_retrieval": "dataset/setting_b/08_n2_eval_test/test_retrieval_main_eval.json",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def norm_text(s: str) -> str:
    return s.lower().replace("\\", "/")


def file_size_mb(path: Path) -> float:
    try:
        return path.stat().st_size / (1024 * 1024)
    except OSError:
        return 0.0


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts & IGNORE_DIR_PARTS:
        return True
    if path.is_dir():
        return True
    if path.suffix.lower() not in SUPPORTED_SUFFIXES:
        return True
    return False


def safe_read_text(path: Path, max_mb: int = MAX_TEXT_READ_MB) -> str:
    if file_size_mb(path) > max_mb:
        return ""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return text[:MAX_CONTENT_CHARS]
    except Exception:
        return ""


def detect_models(path: Path, content_preview: str = "") -> list[str]:
    haystack = norm_text(str(path)) + "\n" + norm_text(content_preview[:20_000])
    models = []
    for model, aliases in MODEL_ALIASES.items():
        for alias in aliases:
            if alias in haystack:
                models.append(model)
                break
    return sorted(set(models))


def detect_split(path: Path, row_sample: dict[str, Any] | None = None) -> str:
    text = norm_text(str(path))
    if row_sample and isinstance(row_sample.get("split"), str):
        return str(row_sample["split"]).lower()
    for split in ["valid", "validation", "test", "train"]:
        if re.search(rf"(^|[/_.-]){split}($|[/_.-])", text):
            return "valid" if split == "validation" else split
    return "unknown"


def flatten_dict_keys(obj: Any, prefix: str = "", max_depth: int = 3) -> list[str]:
    keys = []
    if max_depth <= 0:
        return keys
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            keys.append(key)
            keys.extend(flatten_dict_keys(v, key, max_depth - 1))
    return keys


def get_first_rows_from_json(obj: Any, max_rows: int = 3) -> tuple[str, int | None, list[dict[str, Any]]]:
    if isinstance(obj, list):
        rows = [x for x in obj[:max_rows] if isinstance(x, dict)]
        return "list", len(obj), rows
    if isinstance(obj, dict):
        for key in ["rows", "data", "predictions", "results", "items", "examples"]:
            if isinstance(obj.get(key), list):
                rows = [x for x in obj[key][:max_rows] if isinstance(x, dict)]
                return f"dict_with_{key}", len(obj[key]), rows
        return "dict", None, [obj]
    return type(obj).__name__, None, []


def inspect_json(path: Path) -> dict[str, Any]:
    info: dict[str, Any] = {
        "json_loadable": False,
        "json_kind": None,
        "num_rows": None,
        "top_keys": [],
        "nested_keys": [],
        "candidate_fields_found": [],
        "score_fields_found": [],
        "gold_fields_found": [],
        "query_fields_found": [],
        "rank_fields_found": [],
        "injection_fields_found": [],
        "candidate_lengths_in_sample": [],
        "split_detected": "unknown",
        "row_sample_preview": [],
        "metric_values_found": [],
    }

    if file_size_mb(path) > MAX_JSON_LOAD_MB:
        info["json_error"] = f"too_large_to_load>{MAX_JSON_LOAD_MB}MB"
        return info

    try:
        if path.suffix.lower() == ".jsonl":
            rows = []
            with path.open("r", encoding="utf-8", errors="ignore") as f:
                for i, line in enumerate(f):
                    if i >= 3:
                        break
                    try:
                        rows.append(json.loads(line))
                    except Exception:
                        pass
            obj = rows
        else:
            obj = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception as e:
        info["json_error"] = repr(e)
        return info

    kind, num_rows, rows = get_first_rows_from_json(obj)
    info["json_loadable"] = True
    info["json_kind"] = kind
    info["num_rows"] = num_rows

    if rows:
        first = rows[0]
        info["top_keys"] = list(first.keys())[:80]
        nested_keys = flatten_dict_keys(first)
        info["nested_keys"] = nested_keys[:120]
        all_keys = set(info["top_keys"]) | set(k.split(".")[-1] for k in nested_keys)

        def found(fields: list[str]) -> list[str]:
            return sorted([f for f in fields if f in all_keys])

        info["candidate_fields_found"] = found(CANDIDATE_FIELDS)
        info["score_fields_found"] = found(SCORE_FIELDS)
        info["gold_fields_found"] = found(GOLD_FIELDS)
        info["query_fields_found"] = found(QUERY_FIELDS)
        info["rank_fields_found"] = found(RANK_FIELDS)
        info["injection_fields_found"] = found(INJECTION_HINT_FIELDS)
        info["split_detected"] = detect_split(path, first)

        previews = []
        lengths = []
        for row in rows:
            preview = {}
            for key in list(row.keys())[:20]:
                val = row.get(key)
                if isinstance(val, list):
                    preview[key] = f"list_len={len(val)}"
                    if key in CANDIDATE_FIELDS or "candidate" in key.lower() or "rank_entities" in key.lower():
                        lengths.append(len(val))
                elif isinstance(val, dict):
                    preview[key] = f"dict_keys={list(val.keys())[:8]}"
                else:
                    preview[key] = val
            previews.append(preview)
        info["row_sample_preview"] = previews
        info["candidate_lengths_in_sample"] = lengths

    metrics = extract_metrics_from_obj(obj)
    info["metric_values_found"] = metrics[:30]
    return info


def extract_metrics_from_obj(obj: Any) -> list[dict[str, Any]]:
    hits = []

    def rec(x: Any, path: str = "") -> None:
        if isinstance(x, dict):
            for k, v in x.items():
                kk = str(k).lower()
                new_path = f"{path}.{k}" if path else str(k)
                if any(term in kk for term in ["mrr", "hits", "hit@", "recall", "gold_present"]):
                    if isinstance(v, (int, float, str)):
                        hits.append({"key": new_path, "value": v})
                rec(v, new_path)
        elif isinstance(x, list):
            for i, item in enumerate(x[:20]):
                rec(item, f"{path}[{i}]")

    rec(obj)
    return hits


def inspect_table(path: Path) -> dict[str, Any]:
    info: dict[str, Any] = {
        "table_loadable": False,
        "num_rows_estimate": None,
        "columns": [],
        "candidate_fields_found": [],
        "score_fields_found": [],
        "gold_fields_found": [],
        "query_fields_found": [],
        "rank_fields_found": [],
        "injection_fields_found": [],
        "split_detected": detect_split(path),
        "metric_lines_found": [],
    }

    try:
        delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
        with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            columns = reader.fieldnames or []
            rows_sample = []
            count = 0
            for row in reader:
                count += 1
                if len(rows_sample) < 3:
                    rows_sample.append(row)
        info["table_loadable"] = True
        info["num_rows_estimate"] = count
        info["columns"] = columns[:100]
        low_cols = {c.lower() for c in columns}

        def found(fields: list[str]) -> list[str]:
            return sorted([f for f in fields if f.lower() in low_cols])

        info["candidate_fields_found"] = found(CANDIDATE_FIELDS)
        info["score_fields_found"] = found(SCORE_FIELDS)
        info["gold_fields_found"] = found(GOLD_FIELDS)
        info["query_fields_found"] = found(QUERY_FIELDS)
        info["rank_fields_found"] = found(RANK_FIELDS)
        info["injection_fields_found"] = found(INJECTION_HINT_FIELDS)
    except Exception as e:
        info["table_error"] = repr(e)

    text = safe_read_text(path)
    info["metric_lines_found"] = extract_metric_lines(text)[:20]
    return info


def extract_metric_lines(text: str) -> list[str]:
    lines = []
    for line in text.splitlines():
        low = line.lower()
        if any(term in low for term in ["mrr", "hits", "hit@", "recall", "gold_present", "gold present"]):
            clean = re.sub(r"\s+", " ", line).strip()
            if clean:
                lines.append(clean[:500])
    return lines


def inspect_text(path: Path) -> dict[str, Any]:
    text = safe_read_text(path)
    return {
        "text_read": bool(text),
        "split_detected": detect_split(path),
        "metric_lines_found": extract_metric_lines(text)[:50],
        "contains_gold_injection_hint": bool(re.search(r"gold[_ -]?inject|inject_ratio|gold_injected", text, flags=re.I)),
        "contains_top20_hint": bool(re.search(r"top[_ -]?20|top20|candidate", text, flags=re.I)),
        "contains_drug_only_hint": bool(re.search(r"drug[_ -]?only|drug universe", text, flags=re.I)),
    }


def inspect_model_file(path: Path) -> dict[str, Any]:
    return {
        "model_file": True,
        "split_detected": detect_split(path),
        "note": "Binary/checkpoint-like artifact; not read. Useful only if Day 3 rerun/export is needed.",
    }


def inspect_file(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    base = {
        "path": str(path),
        "suffix": suffix,
        "size_bytes": path.stat().st_size if path.exists() else None,
        "size_mb": round(file_size_mb(path), 4),
    }

    if suffix in JSON_SUFFIXES:
        base.update(inspect_json(path))
    elif suffix in TABLE_SUFFIXES:
        base.update(inspect_table(path))
    elif suffix in TEXT_SUFFIXES or suffix in PY_SUFFIXES:
        base.update(inspect_text(path))
    elif suffix in MODEL_SUFFIXES:
        base.update(inspect_model_file(path))
    else:
        base["unsupported"] = True

    base["artifact_type"] = classify_artifact(base)
    base["has_candidate_rows_hint"] = bool(base.get("candidate_fields_found"))
    base["has_scores_hint"] = bool(base.get("score_fields_found"))
    base["has_gold_hint"] = bool(base.get("gold_fields_found"))
    base["has_query_hint"] = bool(base.get("query_fields_found"))
    base["has_rank_hint"] = bool(base.get("rank_fields_found"))
    base["has_injection_hint"] = bool(base.get("injection_fields_found")) or bool(base.get("contains_gold_injection_hint"))
    base["can_help_reviewer_safe_recompute"] = can_help_recompute(base)
    return base


def classify_artifact(info: dict[str, Any]) -> str:
    path = norm_text(info["path"])

    if info["suffix"] in MODEL_SUFFIXES:
        return "checkpoint_or_embedding"

    if "metric" in path or info.get("metric_lines_found") or info.get("metric_values_found"):
        if info.get("candidate_fields_found"):
            return "candidate_rows_with_metrics"
        return "metrics_or_report"

    if any(k in path for k in ["top20", "candidate", "ranking", "prediction", "pred"]):
        if info.get("candidate_fields_found"):
            return "candidate_or_ranking_rows"
        return "candidate_related_unknown_schema"

    if "score" in path or info.get("score_fields_found"):
        return "score_file"

    if "baseline" in path or "structure" in path:
        return "baseline_related"

    if info["suffix"] == ".py":
        return "script"

    return "unknown"


def can_help_recompute(info: dict[str, Any]) -> bool:
    if info.get("has_injection_hint"):
        return False

    candidate_fields = info.get("candidate_fields_found") or []
    gold_fields = info.get("gold_fields_found") or []
    query_fields = info.get("query_fields_found") or []
    rank_fields = info.get("rank_fields_found") or []
    score_fields = info.get("score_fields_found") or []

    if candidate_fields and gold_fields and query_fields:
        return True
    if candidate_fields and rank_fields:
        return True
    if score_fields and gold_fields and query_fields:
        return True
    return False


def relevance_score(info: dict[str, Any], model: str) -> int:
    path = norm_text(info["path"])
    score = 0

    for alias in MODEL_ALIASES[model]:
        if alias in path:
            score += 4

    if "baseline" in path:
        score += 2
    if "structure" in path:
        score += 2
    if "week8" in path or "17_structure" in path:
        score += 2
    if info.get("has_candidate_rows_hint"):
        score += 4
    if info.get("has_scores_hint"):
        score += 2
    if info.get("has_gold_hint"):
        score += 1
    if info.get("has_query_hint"):
        score += 1
    if info.get("has_rank_hint"):
        score += 1
    if info.get("can_help_reviewer_safe_recompute"):
        score += 3
    if info["artifact_type"] == "metrics_or_report":
        score += 1
    if "entity_embeddings" in path:
        score -= 3
    if "e2e" in path:
        score -= 1
    if "checkpoint" in path:
        score -= 1
    return score


def recommendation_for_model(artifacts: list[dict[str, Any]]) -> str:
    if not artifacts:
        return "NEEDS_RERUN_NO_ARTIFACT_FOUND"

    useful = [a for a in artifacts if a.get("can_help_reviewer_safe_recompute")]
    if useful:
        has_valid = any(a.get("split_detected") == "valid" for a in useful)
        has_test = any(a.get("split_detected") == "test" for a in useful)
        if has_valid and has_test:
            return "RECOLLECT_READY_VALID_AND_TEST"
        if has_valid or has_test:
            return "PARTIAL_RECOLLECT_READY_MISSING_ONE_SPLIT"
        return "RECOLLECT_POSSIBLE_BUT_SPLIT_UNKNOWN"

    candidate_like = [
        a for a in artifacts
        if a["artifact_type"] in {"candidate_or_ranking_rows", "candidate_related_unknown_schema", "score_file"}
    ]
    if candidate_like:
        return "NEEDS_SCHEMA_INSPECTION_OR_STANDARDIZATION"

    metrics_only = [a for a in artifacts if a["artifact_type"] == "metrics_or_report"]
    checkpoint_only = [a for a in artifacts if a["artifact_type"] == "checkpoint_or_embedding"]

    if metrics_only and not checkpoint_only:
        return "METRICS_ONLY_NEEDS_RERUN_OR_RAW_OUTPUT"
    if checkpoint_only:
        return "CHECKPOINT_FOUND_NEEDS_TOP20_EXPORT"

    return "NEEDS_RERUN_OR_MANUAL_SEARCH"


def is_mrr_around_013(value: Any) -> bool:
    try:
        v = float(value)
    except Exception:
        return False
    return 0.12 <= v <= 0.145


def extract_numeric_values_from_line(line: str) -> list[float]:
    vals = []
    for m in re.finditer(r"(?<!\d)(0\.\d+|1\.0+|[1-9]\d*\.\d+)(?!\d)", line):
        try:
            vals.append(float(m.group(1)))
        except Exception:
            pass
    return vals


def scan_repo() -> dict[str, Any]:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    all_files: list[Path] = []
    for root in SCAN_ROOTS:
        if root.exists():
            for path in root.rglob("*"):
                if not should_skip(path):
                    all_files.append(path)

    inventory: dict[str, Any] = {
        "week": 21,
        "day": 2,
        "artifact_name": "baseline_inventory",
        "created_at_utc": now_utc(),
        "scope": "Inventory old structure baseline artifacts for top-20 candidate-generator evaluation.",
        "models": {},
        "general_baseline_files": [],
        "reference_fograg_files": {},
        "possible_mrr_around_0_13_hits": [],
        "scan_summary": {
            "scan_roots": [str(p) for p in SCAN_ROOTS],
            "num_files_scanned": len(all_files),
            "supported_suffixes": sorted(SUPPORTED_SUFFIXES),
        },
        "day2_decision": None,
    }

    for key, rel in FOGRAG_REFERENCE_PATHS.items():
        p = ROOT / rel
        inventory["reference_fograg_files"][key] = {
            "path": rel,
            "exists": p.exists(),
            "size_bytes": p.stat().st_size if p.exists() else None,
        }

    model_to_artifacts: dict[str, list[dict[str, Any]]] = defaultdict(list)
    general_baseline_files = []

    for path in all_files:
        content_preview = ""
        if path.suffix.lower() in TEXT_SUFFIXES | PY_SUFFIXES | TABLE_SUFFIXES:
            content_preview = safe_read_text(path, max_mb=5)
        elif path.suffix.lower() in JSON_SUFFIXES and file_size_mb(path) <= 5:
            content_preview = safe_read_text(path, max_mb=5)

        models = detect_models(path, content_preview)
        baselineish = any(term in norm_text(str(path)) for term in ["baseline", "structure", "transe", "complex", "rgcn", "r-gcn", "hrgat", "distmult", "rotate"])

        if not models and not baselineish:
            continue

        try:
            info = inspect_file(path)
        except Exception as e:
            info = {
                "path": str(path),
                "suffix": path.suffix.lower(),
                "size_mb": round(file_size_mb(path), 4),
                "inspect_error": repr(e),
                "artifact_type": "inspect_error",
            }

        if not models and baselineish:
            general_baseline_files.append(info)
            continue

        for model in models:
            info_for_model = dict(info)
            info_for_model["relevance_score"] = relevance_score(info, model)
            model_to_artifacts[model].append(info_for_model)

        # MRR around 0.13 search
        metric_values = info.get("metric_values_found") or []
        for mv in metric_values:
            if "mrr" in str(mv.get("key", "")).lower() and is_mrr_around_013(mv.get("value")):
                inventory["possible_mrr_around_0_13_hits"].append({
                    "path": str(path),
                    "models_detected": models,
                    "source": "json_metric_key",
                    "key": mv.get("key"),
                    "value": mv.get("value"),
                    "split_detected": info.get("split_detected"),
                })

        metric_lines = info.get("metric_lines_found") or []
        for line in metric_lines:
            low = line.lower()
            if "mrr" in low:
                vals = extract_numeric_values_from_line(line)
                if any(0.12 <= v <= 0.145 for v in vals):
                    inventory["possible_mrr_around_0_13_hits"].append({
                        "path": str(path),
                        "models_detected": models,
                        "source": "metric_line",
                        "line": line,
                        "numeric_values": vals,
                        "split_detected": info.get("split_detected"),
                    })

    for info in general_baseline_files:
        info["relevance_score"] = 0
    inventory["general_baseline_files"] = sorted(
        general_baseline_files,
        key=lambda x: (x.get("artifact_type", ""), x.get("path", "")),
    )[:200]

    for model in ALL_MODELS:
        artifacts = sorted(
            model_to_artifacts.get(model, []),
            key=lambda x: (-int(x.get("relevance_score", 0)), x.get("path", "")),
        )
        top_artifacts = artifacts[:80]
        useful = [a for a in artifacts if a.get("can_help_reviewer_safe_recompute")]
        inventory["models"][model] = {
            "model_name": model,
            "is_core_baseline": model in CORE_MODELS,
            "num_artifacts_found": len(artifacts),
            "num_useful_for_recompute": len(useful),
            "recommendation": recommendation_for_model(artifacts),
            "splits_detected_all": sorted(set(a.get("split_detected", "unknown") for a in artifacts)),
            "splits_detected_useful": sorted(set(a.get("split_detected", "unknown") for a in useful)),
            "artifact_type_counts": dict(count_by_key(artifacts, "artifact_type")),
            "top_artifacts": top_artifacts,
        }

    core_recs = {m: inventory["models"][m]["recommendation"] for m in CORE_MODELS}
    if all("RECOLLECT_READY" in rec for rec in core_recs.values()):
        decision = "INVENTORY_PASS_ALL_CORE_BASELINES_RECOLLECT_READY"
    elif any("RECOLLECT" in rec for rec in core_recs.values()):
        decision = "INVENTORY_PARTIAL_RECOLLECT_SOME_BASELINES_NEED_RERUN"
    else:
        decision = "INVENTORY_NEEDS_RERUN_FOR_CORE_BASELINES"

    inventory["day2_decision"] = decision
    inventory["core_recommendations"] = core_recs
    return inventory


def count_by_key(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    d: dict[str, int] = defaultdict(int)
    for x in items:
        d[str(x.get(key, "missing"))] += 1
    return d


def write_inventory_json(inventory: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def format_artifact_short(a: dict[str, Any]) -> str:
    return (
        f"- `{a.get('path')}`\n"
        f"  - type: `{a.get('artifact_type')}` | split: `{a.get('split_detected')}` | "
        f"size_mb: `{a.get('size_mb')}` | score: `{a.get('relevance_score', '')}`\n"
        f"  - can_recompute: `{a.get('can_help_reviewer_safe_recompute')}` | "
        f"candidate_fields: `{a.get('candidate_fields_found', [])}` | "
        f"score_fields: `{a.get('score_fields_found', [])}` | "
        f"injection_hint: `{a.get('has_injection_hint')}`"
    )


def write_report(inventory: dict[str, Any]) -> None:
    lines = []
    lines.append("# Week 21 Day 2 — Baseline Inventory Audit\n")
    lines.append(f"## Decision\n\n**{inventory['day2_decision']}**\n")
    lines.append("## Scope\n")
    lines.append(
        "Inventory old structure baseline artifacts for `TransE`, `ComplEx`, `R-GCN`, "
        "`HRGAT`, and optional `DistMult` / `RotatE`. Baselines are treated only as "
        "upstream top-20 candidate generators, not as classical full-ranking KGC rows.\n"
    )

    lines.append("## Scan summary\n")
    ss = inventory["scan_summary"]
    lines.append(f"- Files scanned: `{ss['num_files_scanned']}`")
    lines.append(f"- Scan roots: `{', '.join(ss['scan_roots'])}`")
    lines.append("")

    lines.append("## FOG-RAG reference files\n")
    for key, x in inventory["reference_fograg_files"].items():
        status = "OK" if x["exists"] else "MISSING"
        lines.append(f"- `{key}`: **{status}** — `{x['path']}`")
    lines.append("")

    lines.append("## Baseline recommendations\n")
    for model in ALL_MODELS:
        m = inventory["models"][model]
        core = "core" if m["is_core_baseline"] else "optional"
        lines.append(f"### {model} ({core})")
        lines.append(f"- Artifacts found: `{m['num_artifacts_found']}`")
        lines.append(f"- Useful for recompute: `{m['num_useful_for_recompute']}`")
        lines.append(f"- Splits detected all: `{m['splits_detected_all']}`")
        lines.append(f"- Splits detected useful: `{m['splits_detected_useful']}`")
        lines.append(f"- Recommendation: **{m['recommendation']}**")
        lines.append(f"- Artifact type counts: `{m['artifact_type_counts']}`")
        lines.append("")
        if m["top_artifacts"]:
            lines.append("Top artifact candidates:")
            for a in m["top_artifacts"][:10]:
                lines.append(format_artifact_short(a))
            lines.append("")
        else:
            lines.append("No artifact found.\n")

    lines.append("## Possible MRR around 0.13 hits\n")
    hits = inventory["possible_mrr_around_0_13_hits"]
    if not hits:
        lines.append("No automatic MRR≈0.13 hit was found. Manual check may still be needed.\n")
    else:
        for h in hits[:30]:
            lines.append(f"- `{h.get('path')}`")
            lines.append(f"  - models_detected: `{h.get('models_detected')}`")
            lines.append(f"  - split_detected: `{h.get('split_detected')}`")
            if h.get("source") == "json_metric_key":
                lines.append(f"  - key/value: `{h.get('key')}` = `{h.get('value')}`")
            else:
                lines.append(f"  - line: `{h.get('line')}`")
                lines.append(f"  - numeric_values: `{h.get('numeric_values')}`")
        lines.append("")

    lines.append("## End-of-day questions\n")
    lines.append("Answer these manually after inspecting the artifacts above:\n")
    lines.append("1. Baseline MRR khoảng 0.13 trước đây là model nào?")
    lines.append("2. Nó là valid hay test?")
    lines.append("3. Task có đúng `(? drug, indication, disease)` không?")
    lines.append("4. Candidate universe có phải `drug_only` không?")
    lines.append("5. Metric có phải reviewer-safe top-20 không, hay chỉ là old/full-ranking/proxy metric?")
    lines.append("6. Core baselines nào có thể recollect, baseline nào phải rerun?")
    lines.append("")

    lines.append("## Next step\n")
    lines.append(
        "Day 3 should use this inventory to either recollect existing top-20 rows or rerun/export "
        "missing baseline outputs into `results/week21/baseline_outputs/{model_name}/{split}_top20.json`."
    )

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    inventory = scan_repo()
    write_inventory_json(inventory)
    write_report(inventory)

    print("=" * 100)
    print("WEEK 21 DAY 2 — BASELINE INVENTORY AUDIT")
    print("=" * 100)
    print(f"JSON written:   {OUT_JSON}")
    print(f"Report written: {OUT_MD}")
    print()
    print("Core baseline recommendations:")
    for model in CORE_MODELS:
        m = inventory["models"][model]
        print(
            f"  {model:8s} | artifacts={m['num_artifacts_found']:4d} | "
            f"useful={m['num_useful_for_recompute']:3d} | {m['recommendation']}"
        )
    print()
    print(f"Possible MRR≈0.13 hits: {len(inventory['possible_mrr_around_0_13_hits'])}")
    print("Decision:", inventory["day2_decision"])
    print("=" * 100)


if __name__ == "__main__":
    main()