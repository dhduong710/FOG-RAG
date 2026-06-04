from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from collections import Counter, defaultdict


ROOT = Path(".").resolve()

RETRIEVAL_MAIN_PATH = ROOT / "dataset/setting_a/27_n2_fuzzy_retrieval/valid_fuzzy_retrieval_main.json"
VALID_B_PATH = ROOT / "dataset/setting_b/04_contra_checked/valid_b_annotations_contra_checked.json"

OUT_DATA_PATH = ROOT / "dataset/setting_a/28_n2_fuzzy_encoder/valid_encoder_inputs.json"
OUT_SUMMARY_PATH = ROOT / "results/week17/encoder_input_summary.json"
OUT_REPORT_PATH = ROOT / "reports/week17/day2_encoder_input_build.md"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def safe_div(a: float, b: float) -> float:
    return 0.0 if b == 0 else a / b


def normalize_nonnegative(values: list[float]) -> list[float]:
    if not values:
        return []
    vmin = min(values)
    vmax = max(values)
    if vmax - vmin < 1e-12:
        # Nếu mọi edge gần như bằng nhau, giữ tất cả là 1.0 nếu >0, ngược lại 0.0
        base = 1.0 if vmax > 0 else 0.0
        return [base for _ in values]
    return [(v - vmin) / (vmax - vmin) for v in values]


def to_band(w: float) -> str:
    if w >= 0.67:
        return "high"
    if w >= 0.34:
        return "medium"
    return "low"


def build_valid_b_index(valid_b_rows: list[dict]) -> dict:
    idx = {}
    for row in valid_b_rows:
        key = (row["query_disease"], row["gold_drug"])
        idx[key] = row
    return idx


def build_edge_row(tr: dict) -> dict:
    score_debug = tr.get("score_debug", {}) or {}

    raw_triple_score = float(tr.get("triple_score", 0.0))
    direct_term = float(score_debug.get("direct_shortcut_term", 0.0))
    contra_term = float(score_debug.get("contra_term", 0.0))

    # Khôi phục pre-penalty score để có các field giải thích được
    pre_penalty_score = raw_triple_score - direct_term - contra_term

    shortcut_penalized_weight = max(pre_penalty_score + direct_term, 0.0)
    contra_penalized_weight = max(shortcut_penalized_weight + contra_term, 0.0)

    return {
        "triple_index": tr.get("triple_index"),
        "head_id": tr.get("head_id"),
        "relation_id": tr.get("relation_id"),
        "relation_name": tr.get("relation_name"),
        "tail_id": tr.get("tail_id"),
        "touches_query": bool(tr.get("touches_query", False)),
        "touches_candidate": bool(tr.get("touches_candidate", False)),
        "touched_candidate_positions": tr.get("touched_candidate_positions", []),
        "touched_candidate_ids": tr.get("touched_candidate_ids", []),
        "touched_candidate_names": tr.get("touched_candidate_names", []),
        "touches_top_band_candidate": bool(tr.get("touches_top_band_candidate", False)),
        "direct_candidate_query_flag": bool(tr.get("direct_candidate_query_flag", False)),
        "contra_flag": bool(tr.get("contra_flag", False)),
        "ontology_consistency_flag": tr.get("ontology_consistency_flag"),
        "triple_frequency_in_subgraph": tr.get("triple_frequency_in_subgraph"),
        "local_density_hint": tr.get("local_density_hint"),
        "raw_triple_score": raw_triple_score,
        "pre_penalty_score": pre_penalty_score,
        "shortcut_penalized_weight": shortcut_penalized_weight,
        "contra_penalized_weight": contra_penalized_weight,
        "score_debug": score_debug,
    }


def main():
    retrieval_rows = load_json(RETRIEVAL_MAIN_PATH)
    valid_b_rows = load_json(VALID_B_PATH)
    valid_b_index = build_valid_b_index(valid_b_rows)

    OUT_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    encoder_rows = []

    num_rows = 0
    edge_count_list = []
    avg_edge_weight_list = []
    high_conf_rate_list = []
    weighted_shortcut_rate_list = []
    query_weight_mass_list = []
    candidate_weight_mass_mean_list = []
    candidate_weight_mass_max_list = []
    contra_alignment_ok = 0
    missing_valid_b = 0
    band_counter = Counter()

    for row in retrieval_rows:
        num_rows += 1

        query_entity = row["query_entity"]
        gold_entity = row["gold_entity"]
        key = (query_entity, gold_entity)

        valid_b = valid_b_index.get(key)
        if valid_b is None:
            missing_valid_b += 1

        candidate_entities = row["candidate_entities"]
        candidate_entity_ids = row["candidate_entity_ids"]
        candidate_support_bands = row.get("candidate_support_bands", [])
        contra_flags_retrieval = [bool(x) for x in row.get("contra_flags", [])]

        if valid_b is not None:
            contra_flags_lookup = [bool(x) for x in valid_b.get("contra_flags_lookup_checked", [])]
            if len(contra_flags_lookup) == len(contra_flags_retrieval):
                if contra_flags_lookup == contra_flags_retrieval:
                    contra_alignment_ok += 1
        else:
            contra_flags_lookup = None

        triple_rows = row.get("triple_score_rows", [])
        edge_rows = [build_edge_row(tr) for tr in triple_rows]

        raw_weights = [er["contra_penalized_weight"] for er in edge_rows]
        norm_weights = normalize_nonnegative(raw_weights)

        for er, w in zip(edge_rows, norm_weights):
            er["triple_weight"] = round(float(w), 6)
            er["edge_confidence_band"] = to_band(w)
            band_counter[er["edge_confidence_band"]] += 1

        query_incident_weight_mass = 0.0
        candidate_mass_by_position = defaultdict(float)
        candidate_mass_by_id = defaultdict(float)
        shortcut_weight_mass = 0.0
        total_weight_mass = sum(er["triple_weight"] for er in edge_rows)

        for er in edge_rows:
            w = er["triple_weight"]

            if er["touches_query"]:
                query_incident_weight_mass += w

            if er["direct_candidate_query_flag"]:
                shortcut_weight_mass += w

            touched_positions = er.get("touched_candidate_positions", []) or []
            touched_ids = er.get("touched_candidate_ids", []) or []

            for pos in touched_positions:
                candidate_mass_by_position[int(pos)] += w
            for cid in touched_ids:
                candidate_mass_by_id[int(cid)] += w

        # Pad candidate masses to length K
        K = len(candidate_entity_ids)
        candidate_mass_list = [round(float(candidate_mass_by_position.get(i, 0.0)), 6) for i in range(K)]

        avg_edge_weight = safe_div(total_weight_mass, len(edge_rows))
        high_confidence_edge_rate = safe_div(
            sum(1 for er in edge_rows if er["edge_confidence_band"] == "high"),
            len(edge_rows),
        )
        weighted_shortcut_rate = safe_div(shortcut_weight_mass, total_weight_mass)

        edge_weight_values = [er["triple_weight"] for er in edge_rows]
        edge_weight_range = {
            "min": round(min(edge_weight_values), 6) if edge_weight_values else 0.0,
            "max": round(max(edge_weight_values), 6) if edge_weight_values else 0.0,
            "mean": round(avg_edge_weight, 6),
        }

        encoder_row = {
            "row_index": row["row_index"],
            "row_uid": row["row_uid"],
            "split": row["split"],
            "query_entity": query_entity,
            "query_entity_id": row["query_entity_id"],
            "gold_entity": gold_entity,
            "gold_entity_id": row["gold_entity_id"],
            "variant_name": "encoder_inputs_from_retrieval_main",
            "source_variant_name": row.get("variant_name"),
            "selected_source_variant": row.get("selected_source_variant"),
            "candidate_entities": candidate_entities,
            "candidate_entity_ids": candidate_entity_ids,
            "candidate_support_bands": candidate_support_bands,
            "contra_flags_retrieval": contra_flags_retrieval,
            "contra_flags_lookup_checked": contra_flags_lookup,
            "selected_subgraph": row.get("selected_subgraph", []),
            "edge_rows": edge_rows,
            "node_weight_summary": {
                "query_incident_weight_mass": round(float(query_incident_weight_mass), 6),
                "candidate_incident_weight_mass_by_position": candidate_mass_list,
                "candidate_incident_weight_mass_by_id": {
                    str(k): round(float(v), 6) for k, v in sorted(candidate_mass_by_id.items())
                },
                "candidate_incident_weight_mass_mean": round(mean(candidate_mass_list), 6) if candidate_mass_list else 0.0,
                "candidate_incident_weight_mass_max": round(max(candidate_mass_list), 6) if candidate_mass_list else 0.0,
            },
            "encoder_input_summary": {
                "num_edges": len(edge_rows),
                "avg_edge_weight": round(float(avg_edge_weight), 6),
                "high_confidence_edge_rate": round(float(high_confidence_edge_rate), 6),
                "weighted_shortcut_rate": round(float(weighted_shortcut_rate), 6),
                "edge_weight_range": edge_weight_range,
            },
            "subgraph_summary_from_retrieval": row.get("subgraph_summary", {}),
            "encoder_ready": True,
        }

        encoder_rows.append(encoder_row)

        edge_count_list.append(len(edge_rows))
        avg_edge_weight_list.append(avg_edge_weight)
        high_conf_rate_list.append(high_confidence_edge_rate)
        weighted_shortcut_rate_list.append(weighted_shortcut_rate)
        query_weight_mass_list.append(query_incident_weight_mass)
        candidate_weight_mass_mean_list.append(
            encoder_row["node_weight_summary"]["candidate_incident_weight_mass_mean"]
        )
        candidate_weight_mass_max_list.append(
            encoder_row["node_weight_summary"]["candidate_incident_weight_mass_max"]
        )

    summary = {
        "week": 17,
        "day": 2,
        "source_row": "soft_support_fuzzy_retrieval_main",
        "output_row": "encoder_inputs_from_retrieval_main",
        "num_rows": num_rows,
        "num_missing_valid_b_rows": missing_valid_b,
        "contra_alignment_exact_row_count": contra_alignment_ok,
        "avg_num_edges": round(mean(edge_count_list), 6) if edge_count_list else 0.0,
        "avg_edge_weight": round(mean(avg_edge_weight_list), 6) if avg_edge_weight_list else 0.0,
        "avg_high_confidence_edge_rate": round(mean(high_conf_rate_list), 6) if high_conf_rate_list else 0.0,
        "avg_weighted_shortcut_rate": round(mean(weighted_shortcut_rate_list), 6) if weighted_shortcut_rate_list else 0.0,
        "avg_query_incident_weight_mass": round(mean(query_weight_mass_list), 6) if query_weight_mass_list else 0.0,
        "avg_candidate_incident_weight_mass_mean": round(mean(candidate_weight_mass_mean_list), 6) if candidate_weight_mass_mean_list else 0.0,
        "avg_candidate_incident_weight_mass_max": round(mean(candidate_weight_mass_max_list), 6) if candidate_weight_mass_max_list else 0.0,
        "edge_confidence_band_counts": dict(band_counter),
    }

    with OUT_DATA_PATH.open("w", encoding="utf-8") as f:
        json.dump(encoder_rows, f, indent=2, ensure_ascii=False)

    with OUT_SUMMARY_PATH.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    md_lines = []
    md_lines.append("# Week 17 Day 2 — Encoder Input Build\n")
    md_lines.append("## Goal")
    md_lines.append("- Build `valid_encoder_inputs.json` from retrieval main row.")
    md_lines.append("- Convert retrieval triple scores into normalized edge weights for encoder probe.")
    md_lines.append("")
    md_lines.append("## Source")
    md_lines.append("- input row: `soft_support_fuzzy_retrieval_main`")
    md_lines.append("- output row: `encoder_inputs_from_retrieval_main`")
    md_lines.append("")
    md_lines.append("## Summary")
    for k, v in summary.items():
        md_lines.append(f"- **{k}**: `{v}`")
    md_lines.append("")
    md_lines.append("## Notes")
    md_lines.append("- No reranking was performed on day 2.")
    md_lines.append("- No probe message passing was run on day 2.")
    md_lines.append("- The output is intended for day-3 encoder probe only.")
    md_lines.append("")

    OUT_REPORT_PATH.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"[OK] wrote {OUT_DATA_PATH}")
    print(f"[OK] wrote {OUT_SUMMARY_PATH}")
    print(f"[OK] wrote {OUT_REPORT_PATH}")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()