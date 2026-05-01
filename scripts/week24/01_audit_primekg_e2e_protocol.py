from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Tuple

import torch


ROOT = Path(".").resolve()

READY_ROOT = ROOT / "dataset/setting_a/29_n2_e2e_infer_ready"
KGE_PATH = ROOT / "dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt"

ROWS = ["backbone_raw", "soft_support_raw", "retrieval_main"]
SPLITS = ["train", "valid", "test"]

EXPECTED = {
    "graph_num_rels": 4,
    "top_k": 20,
    "valid_rows": 500,
    "test_rows": 500,
    "entity_count": 10453,
    # PrimeKG embedding dim is read dynamically from kge_embedding.shape[1].
    # Do not hard-code 128 here because gnn_hidden_dim=128 is not the same as input embedding dim.
    "embedding_dim": None,
}

OUT_FREEZE = ROOT / "results/week24/primekg_e2e_protocol_freeze.json"
OUT_AUDIT = ROOT / "results/week24/primekg_e2e_ready_audit.json"
OUT_REPORT = ROOT / "reports/week24/day1_primekg_e2e_protocol_audit.md"


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def compute_rank(gold: str, candidates: List[str], k: int = 20) -> int:
    if gold in candidates[:k]:
        return candidates[:k].index(gold) + 1
    return k + 1


def rr_from_rank(rank: int, k: int = 20) -> float:
    return 1.0 / rank if rank <= k else 0.0


def basic_metric(rows: List[Dict[str, Any]], k: int = 20) -> Dict[str, Any]:
    ranks = [int(r["rank"]) for r in rows]
    rrs = [rr_from_rank(r, k=k) for r in ranks]

    return {
        "num_rows": len(rows),
        "gold_present_at20": round(sum(1 for r in ranks if r <= k) / len(rows), 8),
        "mrr_at20": round(sum(rrs) / len(rows), 8),
        "hits1_at20": round(sum(1 for r in ranks if r <= 1) / len(rows), 8),
        "hits3_at20": round(sum(1 for r in ranks if r <= 3) / len(rows), 8),
        "hits10_at20": round(sum(1 for r in ranks if r <= 10) / len(rows), 8),
        "rank21_count": int(sum(1 for r in ranks if r == k + 1)),
        "rr_rule": "1/rank if rank <= 20 else 0",
    }


def check_row(
    row: Dict[str, Any],
    row_name: str,
    split: str,
    index: int,
    entity_count: int,
    graph_num_rels: int,
    k: int,
) -> List[str]:
    errors = []
    prefix = f"{row_name}/{split}/idx={index}"

    required = [
        "input",
        "output",
        "query_entity",
        "query_entity_id",
        "rank_entities",
        "rank_entities_id",
        "rank",
        "subgraph",
    ]

    for field in required:
        if field not in row:
            errors.append(f"{prefix}: missing required field {field}")

    if errors:
        return errors

    candidates = row["rank_entities"]
    candidate_ids = row["rank_entities_id"]
    output = row["output"]
    rank = int(row["rank"])

    if len(candidates) != k:
        errors.append(f"{prefix}: rank_entities length {len(candidates)} != {k}")

    if len(candidate_ids) != k:
        errors.append(f"{prefix}: rank_entities_id length {len(candidate_ids)} != {k}")

    expected_rank = compute_rank(output, candidates, k=k)
    if rank != expected_rank:
        errors.append(f"{prefix}: rank={rank}, expected_rank={expected_rank}")

    input_text = row["input"]
    if "[QUERY]" not in input_text:
        errors.append(f"{prefix}: missing [QUERY] token in input")

    num_entity_tokens = input_text.count("[ENTITY]")
    if num_entity_tokens != k:
        errors.append(f"{prefix}: [ENTITY] count {num_entity_tokens} != {k}")

    ids_to_check = [int(row["query_entity_id"])] + [int(x) for x in candidate_ids]
    for ent_id in ids_to_check:
        if ent_id < 0 or ent_id >= entity_count:
            errors.append(f"{prefix}: entity id out of range: {ent_id}")

    subgraph = row.get("subgraph", [])
    if not isinstance(subgraph, list):
        errors.append(f"{prefix}: subgraph is not list")
        return errors

    for e_i, edge in enumerate(subgraph):
        if not isinstance(edge, list) or len(edge) != 3:
            errors.append(f"{prefix}: bad edge format at edge {e_i}: {edge}")
            continue

        h, rel, t = int(edge[0]), int(edge[1]), int(edge[2])

        if h < 0 or h >= entity_count:
            errors.append(f"{prefix}: head entity out of range at edge {e_i}: {h}")
        if t < 0 or t >= entity_count:
            errors.append(f"{prefix}: tail entity out of range at edge {e_i}: {t}")
        if rel < 0 or rel >= graph_num_rels:
            errors.append(f"{prefix}: relation id out of range at edge {e_i}: {rel}")

    # Row-specific diagnostic fields are required only for valid/test.
    # train.json is intentionally copied from the shared DrKGC/FOG-RAG train placeholder,
    # so it may not contain soft/retrieval-specific fields.
    if split != "train" and row_name == "soft_support_raw":
        for field in ["support_scores", "support_rank_order", "candidate_debug_rows"]:
            if field not in row:
                errors.append(f"{prefix}: soft row missing {field}")

    if split != "train" and row_name == "retrieval_main":
        for field in ["selected_subgraph", "triple_score_rows", "subgraph_summary"]:
            if field not in row:
                errors.append(f"{prefix}: retrieval row missing {field}")

    return errors


def summarize_split(
    row_name: str,
    split: str,
    rows: List[Dict[str, Any]],
    entity_count: int,
) -> Dict[str, Any]:
    errors = []
    subgraph_sizes = []
    max_rel = -1
    max_ent = -1

    for i, row in enumerate(rows):
        row_errors = check_row(
            row=row,
            row_name=row_name,
            split=split,
            index=i,
            entity_count=entity_count,
            graph_num_rels=EXPECTED["graph_num_rels"],
            k=EXPECTED["top_k"],
        )
        errors.extend(row_errors)

        sg = row.get("subgraph", [])
        subgraph_sizes.append(len(sg))

        for ent_id in [row.get("query_entity_id", -1)] + row.get("rank_entities_id", []):
            max_ent = max(max_ent, int(ent_id))

        for edge in sg:
            if isinstance(edge, list) and len(edge) == 3:
                max_ent = max(max_ent, int(edge[0]), int(edge[2]))
                max_rel = max(max_rel, int(edge[1]))

    metric = None
    if split in {"valid", "test"}:
        metric = basic_metric(rows, k=EXPECTED["top_k"])

    return {
        "num_rows": len(rows),
        "avg_subgraph_size": round(mean(subgraph_sizes), 8) if subgraph_sizes else 0.0,
        "min_subgraph_size": min(subgraph_sizes) if subgraph_sizes else 0,
        "max_subgraph_size": max(subgraph_sizes) if subgraph_sizes else 0,
        "max_relation_id_seen": int(max_rel),
        "max_entity_id_seen": int(max_ent),
        "metric": metric,
        "sample_keys": sorted(list(rows[0].keys())) if rows else [],
        "sample_query": rows[0].get("query_entity") if rows else None,
        "sample_output": rows[0].get("output") if rows else None,
        "sample_rank": rows[0].get("rank") if rows else None,
        "sample_top5": rows[0].get("rank_entities", [])[:5] if rows else [],
        "num_errors": len(errors),
        "errors": errors[:50],
    }


def compare_candidate_order(row_a: List[Dict[str, Any]], row_b: List[Dict[str, Any]]) -> Dict[str, Any]:
    n = min(len(row_a), len(row_b))
    same = 0
    same_ids = 0

    for i in range(n):
        if row_a[i].get("rank_entities") == row_b[i].get("rank_entities"):
            same += 1
        if row_a[i].get("rank_entities_id") == row_b[i].get("rank_entities_id"):
            same_ids += 1

    return {
        "num_compared": n,
        "same_candidate_names_rate": round(same / n, 8) if n else None,
        "same_candidate_ids_rate": round(same_ids / n, 8) if n else None,
    }


def main() -> None:
    if not READY_ROOT.exists():
        raise FileNotFoundError(f"Missing ready root: {READY_ROOT}")

    if not KGE_PATH.exists():
        raise FileNotFoundError(f"Missing KGE embedding: {KGE_PATH}")

    kge = torch.load(KGE_PATH, map_location="cpu")
    embedding_shape = list(kge.shape)
    entity_count = int(kge.shape[0])
    embedding_dim = int(kge.shape[1])

    if entity_count != EXPECTED["entity_count"]:
        raise RuntimeError(f"Unexpected entity_count={entity_count}, expected={EXPECTED['entity_count']}")
    if EXPECTED["embedding_dim"] is not None and embedding_dim != EXPECTED["embedding_dim"]:
        raise RuntimeError(f"Unexpected embedding_dim={embedding_dim}, expected={EXPECTED['embedding_dim']}")

    protocol = {
        "decision": "PRIMEKG_E2E_PROTOCOL_FREEZED_FOR_WEEK24_DAY1",
        "dataset": "PrimeKG-derived Setting A",
        "task": "(? , indication, disease) head prediction",
        "candidate_universe": "drug_only",
        "rows": ROWS,
        "splits": ["valid", "test"],
        "top_k": EXPECTED["top_k"],
        "graph_num_rels": EXPECTED["graph_num_rels"],
        "rank_absent_sentinel": EXPECTED["top_k"] + 1,
        "reviewer_safe_rr_rule": "1/rank if rank <= 20 else 0",
        "do_not_use": [
            "raw infer.py MRR for paper",
            "test split for decoding selection",
            "instruct model as main protocol",
            "PharmKG graph_num_rels=28",
        ],
        "kge_embedding_path": str(KGE_PATH),
        "kge_embedding_shape": embedding_shape,
        "ready_root": str(READY_ROOT),
    }

    save_json(OUT_FREEZE, protocol)

    all_rows: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    audit = {
        "decision": None,
        "protocol": protocol,
        "row_summaries": {},
        "cross_row_checks": {},
    }

    total_errors = 0

    for row_name in ROWS:
        row_dir = READY_ROOT / row_name
        if not row_dir.exists():
            raise FileNotFoundError(f"Missing row dir: {row_dir}")

        all_rows[row_name] = {}
        audit["row_summaries"][row_name] = {}

        for split in SPLITS:
            path = row_dir / f"{split}.json"
            rows = load_json(path)
            all_rows[row_name][split] = rows

            summary = summarize_split(
                row_name=row_name,
                split=split,
                rows=rows,
                entity_count=entity_count,
            )
            audit["row_summaries"][row_name][split] = summary
            total_errors += summary["num_errors"]

    # Cross-row checks
    for split in ["valid", "test"]:
        audit["cross_row_checks"][f"soft_vs_retrieval_candidate_order_{split}"] = compare_candidate_order(
            all_rows["soft_support_raw"][split],
            all_rows["retrieval_main"][split],
        )

        audit["cross_row_checks"][f"backbone_vs_soft_candidate_order_{split}"] = compare_candidate_order(
            all_rows["backbone_raw"][split],
            all_rows["soft_support_raw"][split],
        )

    # Expected row counts
    for row_name in ROWS:
        if len(all_rows[row_name]["valid"]) != EXPECTED["valid_rows"]:
            total_errors += 1
            audit["row_summaries"][row_name]["valid"]["errors"].append("valid row count != 500")
        if len(all_rows[row_name]["test"]) != EXPECTED["test_rows"]:
            total_errors += 1
            audit["row_summaries"][row_name]["test"]["errors"].append("test row count != 500")

    # Decision
    if total_errors == 0:
        audit["decision"] = "PRIMEKG_E2E_PROTOCOL_READY"
    else:
        audit["decision"] = "PRIMEKG_E2E_PROTOCOL_NEEDS_FIX"

    save_json(OUT_AUDIT, audit)

    # Markdown report
    lines = []
    lines.append("# Week 24 Day 1 — PrimeKG E2E Protocol Audit")
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append(f"**{audit['decision']}**")
    lines.append("")
    lines.append("## Frozen protocol")
    lines.append("")
    lines.append(f"- Dataset: `{protocol['dataset']}`")
    lines.append(f"- Task: `{protocol['task']}`")
    lines.append(f"- Candidate universe: `{protocol['candidate_universe']}`")
    lines.append(f"- Rows: `{', '.join(ROWS)}`")
    lines.append(f"- Top-k: `{EXPECTED['top_k']}`")
    lines.append(f"- Graph num relations: `{EXPECTED['graph_num_rels']}`")
    lines.append(f"- KGE embedding: `{KGE_PATH}`")
    lines.append(f"- KGE shape: `{embedding_shape}`")
    lines.append(f"- Reviewer-safe RR: `{protocol['reviewer_safe_rr_rule']}`")
    lines.append("")
    lines.append("## Row summaries")
    lines.append("")

    for row_name in ROWS:
        lines.append(f"### {row_name}")
        lines.append("")
        lines.append("| Split | Rows | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Rank21 | Avg subgraph | Max rel | Max ent | Errors |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

        for split in SPLITS:
            s = audit["row_summaries"][row_name][split]
            m = s.get("metric") or {}
            lines.append(
                f"| {split} | {s['num_rows']} | "
                f"{m.get('gold_present_at20', '')} | "
                f"{m.get('mrr_at20', '')} | "
                f"{m.get('hits1_at20', '')} | "
                f"{m.get('hits3_at20', '')} | "
                f"{m.get('hits10_at20', '')} | "
                f"{m.get('rank21_count', '')} | "
                f"{s['avg_subgraph_size']} | "
                f"{s['max_relation_id_seen']} | "
                f"{s['max_entity_id_seen']} | "
                f"{s['num_errors']} |"
            )

        lines.append("")

    lines.append("## Cross-row checks")
    lines.append("")
    for name, val in audit["cross_row_checks"].items():
        lines.append(f"- `{name}`: `{val}`")
    lines.append("")

    lines.append("## Important notes for Week 24")
    lines.append("")
    lines.append("- Use `--graph_num_rels 4` for PrimeKG.")
    lines.append("- Do not use raw `infer.py` MRR as paper metric.")
    lines.append("- Day 2 decoding sweep must use valid only.")
    lines.append("- `retrieval_main` is paper-facing main row if it preserves soft-support E2E while reducing subgraph size.")
    lines.append("- Larger base LLMs are diagnostic unless they improve E2E and keep invalid rate reasonable.")

    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")

    print(f"decision = {audit['decision']}")
    print(f"wrote protocol = {OUT_FREEZE}")
    print(f"wrote audit = {OUT_AUDIT}")
    print(f"wrote report = {OUT_REPORT}")

    for row_name in ROWS:
        print("=" * 100)
        print(row_name)
        for split in ["valid", "test"]:
            s = audit["row_summaries"][row_name][split]
            m = s["metric"]
            print(
                split,
                "rows =", s["num_rows"],
                "Gold@20 =", m["gold_present_at20"],
                "MRR@20 =", m["mrr_at20"],
                "H@10 =", m["hits10_at20"],
                "Rank21 =", m["rank21_count"],
                "avg_subgraph =", s["avg_subgraph_size"],
                "max_rel =", s["max_relation_id_seen"],
                "errors =", s["num_errors"],
            )

    print("=" * 100)
    print("cross-row checks")
    for k, v in audit["cross_row_checks"].items():
        print(k, "=", v)


if __name__ == "__main__":
    main()