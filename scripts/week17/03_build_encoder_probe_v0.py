from __future__ import annotations

import json
import math
import argparse
from pathlib import Path
from collections import defaultdict
from statistics import mean


ROOT = Path(".").resolve()

IN_PATH = ROOT / "dataset/setting_a/28_n2_fuzzy_encoder/valid_encoder_inputs.json"
OUT_FULL_PATH = ROOT / "dataset/setting_a/28_n2_fuzzy_encoder/valid_fuzzy_encoder_probe_v0.json"
OUT_MANIFEST_PATH = ROOT / "dataset/setting_a/28_n2_fuzzy_encoder/encoder_probe_manifest.json"
OUT_REPORT_PATH = ROOT / "reports/week17/day3_probe_design.md"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def max_norm(values: list[float]) -> list[float]:
    if not values:
        return []
    vmax = max(values)
    if vmax <= 1e-12:
        return [0.0 for _ in values]
    return [v / vmax for v in values]


def band_bonus(band: str) -> float:
    if band == "high":
        return 1.0
    if band == "medium":
        return 0.5
    return 0.0


def other_endpoint(edge: dict, node_id: int):
    h = edge["head_id"]
    t = edge["tail_id"]
    if h == node_id:
        return t
    if t == node_id:
        return h
    return None


def build_all_node_incident_mass(edge_rows: list[dict]) -> dict[int, float]:
    node_mass = defaultdict(float)
    for er in edge_rows:
        w = float(er["triple_weight"])
        node_mass[int(er["head_id"])] += w
        node_mass[int(er["tail_id"])] += w
    return dict(node_mass)


def build_query_neighbor_best_weight(edge_rows: list[dict], query_id: int) -> dict[int, float]:
    best = defaultdict(float)
    for er in edge_rows:
        if not er.get("touches_query", False):
            continue
        nb = other_endpoint(er, query_id)
        if nb is None:
            continue
        w = float(er["triple_weight"])
        if w > best[int(nb)]:
            best[int(nb)] = w
    return dict(best)


def build_candidate_probe_rows(row: dict) -> tuple[list[dict], dict, dict, list[float]]:
    query_id = int(row["query_entity_id"])
    gold_id = int(row["gold_entity_id"])
    candidate_entities = row["candidate_entities"]
    candidate_ids = [int(x) for x in row["candidate_entity_ids"]]
    support_bands = row["candidate_support_bands"]
    contra_flags = row["contra_flags_retrieval"]
    edge_rows = row["edge_rows"]

    all_node_mass = build_all_node_incident_mass(edge_rows)
    query_neighbor_best = build_query_neighbor_best_weight(edge_rows, query_id)

    incident_list = []
    bridge_list = []
    direct_list = []

    raw_feature_rows = []

    for idx, (cand_name, cand_id, band, contra) in enumerate(zip(candidate_entities, candidate_ids, support_bands, contra_flags)):
        candidate_incident_mass = float(all_node_mass.get(cand_id, 0.0))
        candidate_bridge_mass = 0.0
        candidate_direct_mass = 0.0
        candidate_edge_count = 0
        candidate_non_direct_edge_count = 0

        for er in edge_rows:
            touched_ids = [int(x) for x in er.get("touched_candidate_ids", [])]
            if cand_id not in touched_ids:
                continue

            nb = other_endpoint(er, cand_id)
            if nb is None:
                continue

            w = float(er["triple_weight"])
            candidate_edge_count += 1

            if er.get("direct_candidate_query_flag", False):
                candidate_direct_mass += w
            else:
                candidate_non_direct_edge_count += 1
                q_nb_w = float(query_neighbor_best.get(int(nb), 0.0))
                if q_nb_w > 0:
                    candidate_bridge_mass += min(w, q_nb_w)

        raw_feature_rows.append({
            "candidate_index_before_probe": idx,
            "candidate_entity": cand_name,
            "candidate_entity_id": cand_id,
            "support_band": band,
            "contra_flag": bool(contra),
            "band_bonus": band_bonus(band),
            "candidate_incident_mass": round(candidate_incident_mass, 6),
            "candidate_bridge_mass": round(candidate_bridge_mass, 6),
            "candidate_direct_mass": round(candidate_direct_mass, 6),
            "candidate_edge_count": candidate_edge_count,
            "candidate_non_direct_edge_count": candidate_non_direct_edge_count,
            "is_gold": cand_id == gold_id,
        })

        incident_list.append(candidate_incident_mass)
        bridge_list.append(candidate_bridge_mass)
        direct_list.append(candidate_direct_mass)

    incident_norm = max_norm(incident_list)
    bridge_norm = max_norm(bridge_list)
    direct_norm = max_norm(direct_list)

    probe_rows = []
    for base, inc_n, br_n, dir_n in zip(raw_feature_rows, incident_norm, bridge_norm, direct_norm):
        score = (
            0.45 * inc_n
            + 0.45 * br_n
            + 0.15 * base["band_bonus"]
            - 0.30 * dir_n
            - 0.10 * (1.0 if base["contra_flag"] else 0.0)
        )
        out = dict(base)
        out["incident_norm"] = round(float(inc_n), 6)
        out["bridge_norm"] = round(float(br_n), 6)
        out["direct_norm"] = round(float(dir_n), 6)
        out["probe_score"] = round(float(score), 6)
        probe_rows.append(out)

    # stable sort by probe score desc, then old index asc
    sorted_idx = sorted(
        range(len(probe_rows)),
        key=lambda i: (-probe_rows[i]["probe_score"], probe_rows[i]["candidate_index_before_probe"])
    )

    candidate_entities_probe = [candidate_entities[i] for i in sorted_idx]
    candidate_ids_probe = [candidate_ids[i] for i in sorted_idx]
    support_bands_probe = [support_bands[i] for i in sorted_idx]
    contra_flags_probe = [contra_flags[i] for i in sorted_idx]
    probe_scores_ordered = [probe_rows[i]["probe_score"] for i in sorted_idx]

    gold_rank_probe = len(candidate_ids_probe) + 1
    if gold_id in candidate_ids_probe:
        gold_rank_probe = candidate_ids_probe.index(gold_id) + 1

    top5_ids = set(candidate_ids_probe[:5])
    top5_rows = [r for r in probe_rows if r["candidate_entity_id"] in top5_ids]
    top5_direct_candidate_rate = sum(1 for r in top5_rows if r["candidate_direct_mass"] > 0) / max(len(top5_rows), 1)

    node_weights = {
        "query_node_id": query_id,
        "query_node_mass": round(float(all_node_mass.get(query_id, 0.0)), 6),
        "all_node_incident_mass": {str(k): round(float(v), 6) for k, v in sorted(all_node_mass.items())},
        "query_neighbor_best_weight": {str(k): round(float(v), 6) for k, v in sorted(query_neighbor_best.items())},
        "candidate_node_mass_by_id": {
            str(cid): round(float(all_node_mass.get(cid, 0.0)), 6) for cid in candidate_ids
        },
    }

    probe_summary = {
        "num_candidates": len(candidate_ids),
        "num_edges": len(edge_rows),
        "gold_rank_probe": gold_rank_probe,
        "avg_probe_score": round(mean([r["probe_score"] for r in probe_rows]), 6) if probe_rows else 0.0,
        "avg_incident_norm": round(mean([r["incident_norm"] for r in probe_rows]), 6) if probe_rows else 0.0,
        "avg_bridge_norm": round(mean([r["bridge_norm"] for r in probe_rows]), 6) if probe_rows else 0.0,
        "avg_direct_norm": round(mean([r["direct_norm"] for r in probe_rows]), 6) if probe_rows else 0.0,
        "top5_direct_candidate_rate": round(float(top5_direct_candidate_rate), 6),
    }

    weighted_subgraph = []
    for er in edge_rows:
        weighted_subgraph.append({
            "head_id": er["head_id"],
            "relation_id": er["relation_id"],
            "relation_name": er["relation_name"],
            "tail_id": er["tail_id"],
            "triple_weight": er["triple_weight"],
            "edge_confidence_band": er["edge_confidence_band"],
            "touches_query": er["touches_query"],
            "touches_candidate": er["touches_candidate"],
            "direct_candidate_query_flag": er["direct_candidate_query_flag"],
            "contra_flag": er["contra_flag"],
        })

    edge_weights = [
        {
            "triple_index": er["triple_index"],
            "triple_weight": er["triple_weight"],
            "edge_confidence_band": er["edge_confidence_band"],
            "direct_candidate_query_flag": er["direct_candidate_query_flag"],
            "contra_flag": er["contra_flag"],
        }
        for er in edge_rows
    ]

    return (
        probe_rows,
        node_weights,
        probe_summary,
        sorted_idx,
        candidate_entities_probe,
        candidate_ids_probe,
        support_bands_probe,
        contra_flags_probe,
        probe_scores_ordered,
        weighted_subgraph,
        edge_weights,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="subset dryrun rows")
    parser.add_argument("--tag", type=str, default="", help="optional tag, e.g. dryrun")
    args = parser.parse_args()

    rows = load_json(IN_PATH)
    if args.limit is not None:
        rows = rows[:args.limit]

    tag_suffix = f"_{args.tag}" if args.tag else ""
    out_probe_path = ROOT / f"dataset/setting_a/28_n2_fuzzy_encoder/valid_fuzzy_encoder_probe_v0{tag_suffix}.json"
    out_manifest_path = ROOT / f"dataset/setting_a/28_n2_fuzzy_encoder/encoder_probe_manifest{tag_suffix}.json"

    out_probe_path.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    probe_rows_all = []
    gold_ranks = []
    top5_direct_rates = []
    avg_probe_scores = []

    for row in rows:
        (
            probe_score_rows,
            node_weights,
            probe_summary,
            sorted_idx,
            candidate_entities_probe,
            candidate_ids_probe,
            support_bands_probe,
            contra_flags_probe,
            probe_scores_ordered,
            weighted_subgraph,
            edge_weights,
        ) = build_candidate_probe_rows(row)

        out_row = {
            "row_index": row["row_index"],
            "row_uid": row["row_uid"],
            "split": row["split"],
            "query_entity": row["query_entity"],
            "query_entity_id": row["query_entity_id"],
            "gold_entity": row["gold_entity"],
            "gold_entity_id": row["gold_entity_id"],
            "variant_name": "soft_support_fuzzy_encoder_probe_v0",
            "source_variant_name": row["source_variant_name"],
            "selected_source_variant": row.get("selected_source_variant"),
            "candidate_entities_before_probe": row["candidate_entities"],
            "candidate_entity_ids_before_probe": row["candidate_entity_ids"],
            "candidate_entities_probe_ordered": candidate_entities_probe,
            "candidate_entity_ids_probe_ordered": candidate_ids_probe,
            "candidate_support_bands_probe_ordered": support_bands_probe,
            "contra_flags_probe_ordered": contra_flags_probe,
            "probe_scores_ordered": probe_scores_ordered,
            "weighted_subgraph": weighted_subgraph,
            "edge_weights": edge_weights,
            "node_weights": node_weights,
            "probe_score_rows": probe_score_rows,
            "probe_summary": probe_summary,
        }

        probe_rows_all.append(out_row)
        gold_ranks.append(probe_summary["gold_rank_probe"])
        top5_direct_rates.append(probe_summary["top5_direct_candidate_rate"])
        avg_probe_scores.append(probe_summary["avg_probe_score"])

    manifest = {
        "week": 17,
        "day": 3,
        "mode": "encoder_probe_v0",
        "input_path": str(IN_PATH.relative_to(ROOT)),
        "output_path": str(out_probe_path.relative_to(ROOT)),
        "num_rows": len(probe_rows_all),
        "limit": args.limit,
        "tag": args.tag,
        "main_input_row": "encoder_inputs_from_retrieval_main",
        "main_output_row": "soft_support_fuzzy_encoder_probe_v0",
        "formula": {
            "incident_norm": 0.45,
            "bridge_norm": 0.45,
            "band_bonus": 0.15,
            "direct_norm_penalty": -0.30,
            "contra_penalty": -0.10,
        },
        "summary": {
            "avg_gold_rank_probe": round(mean(gold_ranks), 6) if gold_ranks else 0.0,
            "avg_top5_direct_candidate_rate": round(mean(top5_direct_rates), 6) if top5_direct_rates else 0.0,
            "avg_probe_score": round(mean(avg_probe_scores), 6) if avg_probe_scores else 0.0,
        },
        "notes": [
            "No end-to-end training is performed.",
            "This is a minimal encoder probe only.",
            "Subset dryrun is recommended before full valid.",
        ],
    }

    write_json(out_probe_path, probe_rows_all)
    write_json(out_manifest_path, manifest)

    md_lines = []
    md_lines.append("# Week 17 Day 3 — Probe Design\n")
    md_lines.append("## Theme")
    md_lines.append("- Frozen retrieval main → one minimal fuzzy encoder probe v0")
    md_lines.append("")
    md_lines.append("## Probe formula")
    md_lines.append("- 0.45 * incident_norm")
    md_lines.append("- 0.45 * bridge_norm")
    md_lines.append("- 0.15 * band_bonus")
    md_lines.append("- 0.30 * direct_norm")
    md_lines.append("- 0.10 * contra_penalty")
    md_lines.append("")
    md_lines.append("## Manifest summary")
    for k, v in manifest["summary"].items():
        md_lines.append(f"- **{k}**: `{v}`")
    md_lines.append("")
    md_lines.append("## Notes")
    md_lines.append("- Day 3 builds the probe artifact only.")
    md_lines.append("- Official compare is deferred to Day 4.")
    md_lines.append("")

    OUT_REPORT_PATH.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"[OK] wrote {out_probe_path}")
    print(f"[OK] wrote {out_manifest_path}")
    print(f"[OK] wrote {OUT_REPORT_PATH}")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()