from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(".").resolve()

RETRIEVAL_MAIN_PATH = ROOT / "dataset/setting_a/27_n2_fuzzy_retrieval/valid_fuzzy_retrieval_main.json"
PROBE_PATH = ROOT / "dataset/setting_a/28_n2_fuzzy_encoder/valid_fuzzy_encoder_probe_v0.json"

OUT_JSON = ROOT / "results/week17/encoder_case_samples.json"
OUT_MD = ROOT / "reports/week17/day5_case_review.md"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def safe_get_probe_top1_detail(probe_row: dict) -> dict:
    top1_id = probe_row["candidate_entity_ids_probe_ordered"][0]
    top1_name = probe_row["candidate_entities_probe_ordered"][0]

    for r in probe_row["probe_score_rows"]:
        if r["candidate_entity_id"] == top1_id:
            return {
                "top1_candidate": top1_name,
                "top1_candidate_id": top1_id,
                "probe_score": r["probe_score"],
                "incident_norm": r["incident_norm"],
                "bridge_norm": r["bridge_norm"],
                "direct_norm": r["direct_norm"],
                "candidate_incident_mass": r["candidate_incident_mass"],
                "candidate_bridge_mass": r["candidate_bridge_mass"],
                "candidate_direct_mass": r["candidate_direct_mass"],
                "support_band": r["support_band"],
                "contra_flag": r["contra_flag"],
            }
    return {
        "top1_candidate": top1_name,
        "top1_candidate_id": top1_id,
    }


def safe_get_retrieval_top1_detail(ret_row: dict) -> dict:
    top1_id = ret_row["candidate_entity_ids"][0]
    top1_name = ret_row["candidate_entities"][0]
    return {
        "top1_candidate": top1_name,
        "top1_candidate_id": top1_id,
    }


def get_rank(ids: list[int], gold_id: int) -> int:
    return ids.index(gold_id) + 1 if gold_id in ids else len(ids) + 1


def main():
    retrieval_rows = load_json(RETRIEVAL_MAIN_PATH)
    probe_rows = load_json(PROBE_PATH)

    probe_index = {row["row_uid"]: row for row in probe_rows}

    improved = []
    worsened = []
    same_better_graph = []
    redundant = []
    anchor_caution = []

    for ret_row in retrieval_rows:
        uid = ret_row["row_uid"]
        probe_row = probe_index[uid]

        gold_id = ret_row["gold_entity_id"]

        ret_rank = get_rank(ret_row["candidate_entity_ids"], gold_id)
        probe_rank = int(probe_row["probe_summary"]["gold_rank_probe"])

        ret_top1 = safe_get_retrieval_top1_detail(ret_row)
        probe_top1 = safe_get_probe_top1_detail(probe_row)

        top1_changed = ret_top1["top1_candidate_id"] != probe_top1["top1_candidate_id"]

        case = {
            "row_uid": uid,
            "row_index": ret_row["row_index"],
            "query_entity": ret_row["query_entity"],
            "query_entity_id": ret_row["query_entity_id"],
            "gold_entity": ret_row["gold_entity"],
            "gold_entity_id": gold_id,
            "retrieval_rank": ret_rank,
            "probe_rank": probe_rank,
            "rank_delta_probe_minus_retrieval": probe_rank - ret_rank,
            "retrieval_top1": ret_top1,
            "probe_top1": probe_top1,
            "probe_summary": probe_row["probe_summary"],
            "top1_changed": top1_changed,
            "retrieval_top5": ret_row["candidate_entities"][:5],
            "probe_top5": probe_row["candidate_entities_probe_ordered"][:5],
        }

        if probe_rank < ret_rank:
            improved.append(case)

        elif probe_rank > ret_rank:
            worsened.append(case)

        else:
            # same-rank buckets
            if (
                probe_row["probe_summary"]["avg_bridge_norm"] > 0
                or probe_top1.get("candidate_bridge_mass", 0.0) > 0
                or (
                    top1_changed
                    and probe_top1.get("candidate_direct_mass", 999.0)
                    <=  ret_row.get("subgraph_summary", {}).get("direct_shortcut_path_rate", 999.0)
                )
            ):
                same_better_graph.append(case)
            else:
                redundant.append(case)

        if (
            top1_changed
            and probe_rank >= ret_rank
            and probe_top1.get("candidate_bridge_mass", 0.0) == 0.0
            and probe_top1.get("candidate_incident_mass", 0.0) > 0.0
        ):
            anchor_caution.append(case)

    out = {
        "week": 17,
        "day": 5,
        "bucket_counts": {
            "improved_vs_retrieval_main": len(improved),
            "worsened_vs_retrieval_main": len(worsened),
            "same_rank_but_better_graph_signal": len(same_better_graph),
            "probe_redundant_cases": len(redundant),
            "anchor_caution_cases": len(anchor_caution),
        },
        "samples": {
            "improved_vs_retrieval_main": improved[:15],
            "worsened_vs_retrieval_main": worsened[:20],
            "same_rank_but_better_graph_signal": same_better_graph[:20],
            "probe_redundant_cases": redundant[:20],
            "anchor_caution_cases": anchor_caution[:20],
        },
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)

    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    lines = []
    lines.append("# Week 17 Day 5 — Case Review\n")
    lines.append("## Bucket counts")
    for k, v in out["bucket_counts"].items():
        lines.append(f"- **{k}**: `{v}`")
    lines.append("")
    lines.append("## Reading guide")
    lines.append("- improved_vs_retrieval_main: probe helps")
    lines.append("- worsened_vs_retrieval_main: probe harms")
    lines.append("- same_rank_but_better_graph_signal: same rank but maybe graph-side cleaner")
    lines.append("- probe_redundant_cases: probe adds little beyond retrieval main")
    lines.append("- anchor_caution_cases: top1 changed but not for the better")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"[OK] wrote {OUT_JSON}")
    print(f"[OK] wrote {OUT_MD}")
    print(json.dumps(out["bucket_counts"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()