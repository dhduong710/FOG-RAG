from __future__ import annotations

import json
from pathlib import Path
from statistics import mean


ROOT = Path(".").resolve()

SOFT_SUPPORT_PATH = ROOT / "dataset/setting_a/26_n2_soft_support/valid_top20_soft_support_main.json"
RETRIEVAL_MAIN_PATH = ROOT / "dataset/setting_a/27_n2_fuzzy_retrieval/valid_fuzzy_retrieval_main.json"
ENCODER_PROBE_PATH = ROOT / "dataset/setting_a/28_n2_fuzzy_encoder/valid_fuzzy_encoder_probe_v0.json"

OUT_JSON = ROOT / "results/week17/encoder_probe_compare.json"
OUT_MD = ROOT / "reports/week17/day4_probe_compare.md"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def safe_mean(xs):
    return 0.0 if not xs else float(mean(xs))

def get_row_uid(row: dict, default_index: int | None = None) -> str:
    if "row_uid" in row and row["row_uid"] not in (None, ""):
        return str(row["row_uid"])

    if "row_index" in row and row["row_index"] is not None:
        return f"row_index::{row['row_index']}"

    query = row.get("query_entity", "UNK_QUERY")
    gold = row.get("gold_entity", "UNK_GOLD")

    if default_index is not None:
        return f"fallback::{default_index}::{query}::{gold}"

    return f"fallback::{query}::{gold}"


def rank_metrics_from_ranks(ranks: list[int]) -> dict:
    n = len(ranks)
    if n == 0:
        return {
            "num_rows": 0,
            "gold_present_rate": 0.0,
            "mrr_like": 0.0,
            "hits1_like": 0.0,
            "hits3_like": 0.0,
            "hits10_like": 0.0,
            "avg_gold_rank": 0.0,
        }

    present = [1 if r <= 20 else 0 for r in ranks]
    return {
        "num_rows": n,
        "gold_present_rate": round(sum(present) / n, 6),
        "mrr_like": round(sum(1.0 / r for r in ranks) / n, 6),
        "hits1_like": round(sum(1 for r in ranks if r <= 1) / n, 6),
        "hits3_like": round(sum(1 for r in ranks if r <= 3) / n, 6),
        "hits10_like": round(sum(1 for r in ranks if r <= 10) / n, 6),
        "avg_gold_rank": round(sum(ranks) / n, 6),
    }


def candidate_debug_direct_flag(d: dict) -> bool:
    return bool(
        d.get("candidate_query_edge_count", 0) > 0
        or d.get("direct_link_flag", False)
        or d.get("candidate_query_direct_flag", False)
    )


def candidate_debug_evidence_flag(d: dict) -> bool:
    return bool(
        d.get("evidence_edge_touch_count", 0) > 0
        or d.get("evidence_touch_count", 0) > 0
        or d.get("candidate_in_aligned_evidence", False)
    )


def candidate_debug_contra_flag(d: dict) -> bool:
    return bool(
        d.get("contra_flag", False)
        or d.get("contra_penalty", 0) > 0
    )


def extract_soft_support_metrics(rows: list[dict]) -> tuple[dict, list[dict]]:
    ranks = []
    top5_direct_rates = []
    top5_evidence_rates = []
    top5_contra_rates = []
    case_rows = []

    for i, row in enumerate(rows):
        cand_ids = row["candidate_entity_ids"]
        gold_id = row["gold_entity_id"]

        if gold_id in cand_ids:
            rank = cand_ids.index(gold_id) + 1
        else:
            rank = len(cand_ids) + 1
        ranks.append(rank)

        debug_rows = row.get("candidate_debug_rows", [])
        direct_rate = None
        evidence_rate = None
        contra_rate = None

        if debug_rows and len(debug_rows) == len(cand_ids):
            top5_debug = debug_rows[:5]
            direct_rate = sum(1 for d in top5_debug if candidate_debug_direct_flag(d)) / max(len(top5_debug), 1)
            evidence_rate = sum(1 for d in top5_debug if candidate_debug_evidence_flag(d)) / max(len(top5_debug), 1)
            contra_rate = sum(1 for d in top5_debug if candidate_debug_contra_flag(d)) / max(len(top5_debug), 1)

            top5_direct_rates.append(direct_rate)
            top5_evidence_rates.append(evidence_rate)
            top5_contra_rates.append(contra_rate)

        case_rows.append({
            "row_uid": get_row_uid(row, i),
            "row_index": row.get("row_index", i),
            "query_entity": row["query_entity"],
            "gold_entity": row["gold_entity"],
            "gold_rank": rank,
            "top1_candidate": row["candidate_entities"][0],
            "top5_direct_rate": direct_rate,
            "top5_evidence_rate": evidence_rate,
            "top5_contra_rate": contra_rate,
        })

    metrics = rank_metrics_from_ranks(ranks)
    metrics.update({
        "avg_top5_direct_link_rate": round(safe_mean(top5_direct_rates), 6),
        "avg_top5_evidence_positive_rate": round(safe_mean(top5_evidence_rates), 6),
        "avg_top5_contra_rate": round(safe_mean(top5_contra_rates), 6),
    })
    return metrics, case_rows


def extract_retrieval_main_metrics(rows: list[dict]) -> tuple[dict, list[dict]]:
    ranks = []
    subgraph_sizes = []
    triple_scores = []
    direct_rates = []
    contra_rates = []
    cov_rates = []
    case_rows = []

    for i, row in enumerate(rows):
        cand_ids = row["candidate_entity_ids"]
        gold_id = row["gold_entity_id"]
        if gold_id in cand_ids:
            rank = cand_ids.index(gold_id) + 1
        else:
            rank = len(cand_ids) + 1
        ranks.append(rank)

        sg_summary = row.get("subgraph_summary", {}) or {}
        subgraph_sizes.append(
            sg_summary.get("num_selected_triples", len(row.get("selected_subgraph", [])))
        )

        ts_rows = row.get("triple_score_rows", [])
        if ts_rows:
            triple_scores.append(mean([float(t.get("triple_score", 0.0)) for t in ts_rows]))

        direct_rates.append(float(sg_summary.get("direct_shortcut_path_rate", 0.0)))
        contra_rates.append(float(sg_summary.get("contradiction_path_rate", 0.0)))
        cov_rates.append(float(sg_summary.get("candidate_coverage_preserved_rate", 1.0)))

        case_rows.append({
            "row_uid": get_row_uid(row, i),
            "row_index": row.get("row_index", i),
            "query_entity": row["query_entity"],
            "gold_entity": row["gold_entity"],
            "gold_rank": rank,
            "top1_candidate": row["candidate_entities"][0],
            "subgraph_size": sg_summary.get("num_selected_triples", len(row.get("selected_subgraph", []))),
            "direct_shortcut_path_rate": float(sg_summary.get("direct_shortcut_path_rate", 0.0)),
            "contradiction_path_rate": float(sg_summary.get("contradiction_path_rate", 0.0)),
        })

    metrics = rank_metrics_from_ranks(ranks)
    metrics.update({
        "avg_subgraph_size": round(safe_mean(subgraph_sizes), 6),
        "avg_triple_score": round(safe_mean(triple_scores), 6),
        "avg_direct_shortcut_path_rate": round(safe_mean(direct_rates), 6),
        "avg_contradiction_path_rate": round(safe_mean(contra_rates), 6),
        "candidate_coverage_preserved_rate": round(safe_mean(cov_rates), 6),
    })
    return metrics, case_rows


def extract_encoder_probe_metrics(rows: list[dict]) -> tuple[dict, list[dict]]:
    ranks = []
    top5_direct_rates = []
    avg_probe_scores = []
    avg_incident_norms = []
    avg_bridge_norms = []
    avg_direct_norms = []
    edge_counts = []
    high_conf_rates = []
    case_rows = []

    for i, row in enumerate(rows):
        ps = row["probe_summary"]
        ranks.append(int(ps["gold_rank_probe"]))
        top5_direct_rates.append(float(ps["top5_direct_candidate_rate"]))
        avg_probe_scores.append(float(ps["avg_probe_score"]))
        avg_incident_norms.append(float(ps["avg_incident_norm"]))
        avg_bridge_norms.append(float(ps["avg_bridge_norm"]))
        avg_direct_norms.append(float(ps["avg_direct_norm"]))
        edge_counts.append(int(ps["num_edges"]))

        edge_weights = row.get("edge_weights", [])
        if edge_weights:
            high_conf_rates.append(
                sum(1 for e in edge_weights if e.get("edge_confidence_band") == "high") / len(edge_weights)
            )

        case_rows.append({
            "row_uid": get_row_uid(row, i),
            "row_index": row.get("row_index", i),
            "query_entity": row["query_entity"],
            "gold_entity": row["gold_entity"],
            "gold_rank": int(ps["gold_rank_probe"]),
            "top1_candidate": row["candidate_entities_probe_ordered"][0],
            "avg_probe_score": float(ps["avg_probe_score"]),
            "avg_incident_norm": float(ps["avg_incident_norm"]),
            "avg_bridge_norm": float(ps["avg_bridge_norm"]),
            "avg_direct_norm": float(ps["avg_direct_norm"]),
            "top5_direct_candidate_rate": float(ps["top5_direct_candidate_rate"]),
        })

    metrics = rank_metrics_from_ranks(ranks)
    metrics.update({
        "avg_probe_top5_direct_candidate_rate": round(safe_mean(top5_direct_rates), 6),
        "avg_probe_score": round(safe_mean(avg_probe_scores), 6),
        "avg_incident_norm": round(safe_mean(avg_incident_norms), 6),
        "avg_bridge_norm": round(safe_mean(avg_bridge_norms), 6),
        "avg_direct_norm": round(safe_mean(avg_direct_norms), 6),
        "avg_weighted_edge_count": round(safe_mean(edge_counts), 6),
        "avg_high_confidence_edge_rate": round(safe_mean(high_conf_rates), 6),
    })
    return metrics, case_rows


def compare_probe_vs_retrieval(retrieval_rows: list[dict], probe_rows: list[dict]) -> dict:
    improved = 0
    worsened = 0
    same = 0
    same_top1 = 0
    same_top5_exact = 0
    rank_deltas = []

    probe_index = {row["row_uid"]: row for row in probe_rows}

    for rrow in retrieval_rows:
        uid = rrow["row_uid"]
        prow = probe_index[uid]

        gold_id = rrow["gold_entity_id"]
        ret_ids = rrow["candidate_entity_ids"]
        pro_ids = prow["candidate_entity_ids_probe_ordered"]

        ret_rank = ret_ids.index(gold_id) + 1 if gold_id in ret_ids else len(ret_ids) + 1
        pro_rank = pro_ids.index(gold_id) + 1 if gold_id in pro_ids else len(pro_ids) + 1

        delta = pro_rank - ret_rank
        rank_deltas.append(delta)

        if pro_rank < ret_rank:
            improved += 1
        elif pro_rank > ret_rank:
            worsened += 1
        else:
            same += 1

        if ret_ids[0] == pro_ids[0]:
            same_top1 += 1
        if ret_ids[:5] == pro_ids[:5]:
            same_top5_exact += 1

    n = len(retrieval_rows)
    return {
        "num_rows": n,
        "improved_vs_retrieval_main": improved,
        "worsened_vs_retrieval_main": worsened,
        "same_rank_vs_retrieval_main": same,
        "same_top1_rate_vs_retrieval_main": round(same_top1 / n, 6),
        "same_top5_exact_rate_vs_retrieval_main": round(same_top5_exact / n, 6),
        "avg_rank_delta_probe_minus_retrieval": round(safe_mean(rank_deltas), 6),
    }


def main():
    soft_rows = load_json(SOFT_SUPPORT_PATH)
    retrieval_rows = load_json(RETRIEVAL_MAIN_PATH)
    probe_rows = load_json(ENCODER_PROBE_PATH)

    soft_metrics, soft_cases = extract_soft_support_metrics(soft_rows)
    retrieval_metrics, retrieval_cases = extract_retrieval_main_metrics(retrieval_rows)
    probe_metrics, probe_cases = extract_encoder_probe_metrics(probe_rows)
    comp = compare_probe_vs_retrieval(retrieval_rows, probe_rows)

    out = {
        "week": 17,
        "day": 4,
        "rows_compared": [
            "soft_support_raw",
            "soft_support_fuzzy_retrieval_main",
            "soft_support_fuzzy_encoder_probe_v0",
        ],
        "metrics": {
            "soft_support_raw": soft_metrics,
            "soft_support_fuzzy_retrieval_main": retrieval_metrics,
            "soft_support_fuzzy_encoder_probe_v0": probe_metrics,
        },
        "probe_vs_retrieval_main": comp,
        "case_samples_preview": {
            "soft_support_raw": soft_cases[:3],
            "soft_support_fuzzy_retrieval_main": retrieval_cases[:3],
            "soft_support_fuzzy_encoder_probe_v0": probe_cases[:3],
        },
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)

    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    lines = []
    lines.append("# Week 17 Day 4 — Probe Compare\n")
    lines.append("## Rows compared")
    for r in out["rows_compared"]:
        lines.append(f"- `{r}`")
    lines.append("")
    lines.append("## Metrics")
    for row_name, metrics in out["metrics"].items():
        lines.append(f"### {row_name}")
        for k, v in metrics.items():
            lines.append(f"- **{k}**: `{v}`")
        lines.append("")
    lines.append("## Probe vs retrieval main")
    for k, v in comp.items():
        lines.append(f"- **{k}**: `{v}`")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"[OK] wrote {OUT_JSON}")
    print(f"[OK] wrote {OUT_MD}")
    print(json.dumps(out["metrics"], indent=2, ensure_ascii=False))
    print(json.dumps(comp, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()