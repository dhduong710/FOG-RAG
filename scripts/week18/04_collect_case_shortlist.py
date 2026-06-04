from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(".").resolve()

INPUTS = {
    "backbone_raw": ROOT / "dataset/setting_b/07_n2_eval_valid/valid_backbone_raw_eval.json",
    "ontology_raw": ROOT / "dataset/setting_b/07_n2_eval_valid/valid_ontology_raw_eval.json",
    "soft_support_raw": ROOT / "dataset/setting_b/07_n2_eval_valid/valid_soft_support_raw_eval.json",
    "retrieval_main": ROOT / "dataset/setting_b/07_n2_eval_valid/valid_retrieval_main_eval.json",
    "encoder_cases": ROOT / "results/week17/encoder_case_samples.json",
    "main_table": ROOT / "results/week18/novelty2_valid_main_table.json",
}

OUT_JSON = ROOT / "results/week18/novelty2_case_shortlist.json"
OUT_MD = ROOT / "reports/week18/day4_case_shortlist.md"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_index(rows: list[dict]) -> dict:
    idx = {}
    for row in rows:
        key = (row["query_entity"], row["gold_entity"])
        idx[key] = row
    return idx


def base_case(back: dict, ont: dict, soft: dict, ret: dict) -> dict:
    rs = ret["stage_specific"]
    return {
        "row_index": ret["row_index"],
        "query_entity": ret["query_entity"],
        "query_entity_id": ret["query_entity_id"],
        "gold_entity": ret["gold_entity"],
        "gold_entity_id": ret["gold_entity_id"],
        "backbone_rank": back["gold_rank"],
        "ontology_rank": ont["gold_rank"],
        "soft_support_rank": soft["gold_rank"],
        "retrieval_rank": ret["gold_rank"],
        "backbone_top1": back["top1_candidate"],
        "ontology_top1": ont["top1_candidate"],
        "soft_support_top1": soft["top1_candidate"],
        "retrieval_top1": ret["top1_candidate"],
        "retrieval_subgraph_size": rs.get("num_selected_triples"),
        "retrieval_avg_triple_score": rs.get("avg_triple_score_row_value"),
        "retrieval_direct_shortcut_path_rate": rs.get("direct_shortcut_path_rate"),
        "retrieval_contradiction_path_rate": rs.get("contradiction_path_rate"),
        "retrieval_candidate_coverage_preserved_rate": rs.get("candidate_coverage_preserved_rate"),
        "ontology_gold_present": ont["gold_present"],
        "retrieval_gold_present": ret["gold_present"],
    }


def pick_top(cases: list[dict], n: int) -> list[dict]:
    return cases[:n]


def main():
    backbone_rows = load_json(INPUTS["backbone_raw"])
    ontology_rows = load_json(INPUTS["ontology_raw"])
    soft_rows = load_json(INPUTS["soft_support_raw"])
    retrieval_rows = load_json(INPUTS["retrieval_main"])
    encoder_cases = load_json(INPUTS["encoder_cases"])
    main_table = load_json(INPUTS["main_table"])

    back_idx = build_index(backbone_rows)
    ont_idx = build_index(ontology_rows)
    soft_idx = build_index(soft_rows)
    ret_idx = build_index(retrieval_rows)

    joined = []
    for key, ret in ret_idx.items():
        back = back_idx[key]
        ont = ont_idx[key]
        soft = soft_idx[key]
        joined.append(base_case(back, ont, soft, ret))

    # Bucket A: retrieval beats backbone
    bucket_a = []
    for c in joined:
        if c["retrieval_rank"] < c["backbone_rank"]:
            item = dict(c)
            item["improvement_vs_backbone"] = c["backbone_rank"] - c["retrieval_rank"]
            bucket_a.append(item)

    bucket_a.sort(key=lambda x: (-x["improvement_vs_backbone"], x["retrieval_rank"], x["backbone_rank"]))

    # Bucket B: ontology fails, retrieval succeeds
    bucket_b = []
    for c in joined:
        if (c["ontology_gold_present"] is False) and (c["retrieval_gold_present"] is True):
            item = dict(c)
            item["ontology_failure_gap"] = c["ontology_rank"] - c["retrieval_rank"]
            bucket_b.append(item)

    bucket_b.sort(key=lambda x: (x["retrieval_rank"], -x["ontology_failure_gap"], x["backbone_rank"]))

    # Bucket C: same rank as soft support but cleaner graph-ready story
    bucket_c = []
    for c in joined:
        if (
            c["soft_support_rank"] == c["retrieval_rank"]
            and c["retrieval_gold_present"] is True
            and c["retrieval_candidate_coverage_preserved_rate"] == 1.0
        ):
            item = dict(c)
            item["graph_story_score"] = (
                10.0 * (1.0 - float(c["retrieval_direct_shortcut_path_rate"] or 0.0))
                + 5.0 * (1.0 - float(c["retrieval_contradiction_path_rate"] or 0.0))
                + 2.0 * (1.0 / max(int(c["retrieval_rank"]), 1))
            )
            bucket_c.append(item)

    bucket_c.sort(
        key=lambda x: (
            -x["graph_story_score"],
            x["retrieval_rank"],
            x["retrieval_subgraph_size"] if x["retrieval_subgraph_size"] is not None else 9999
        )
    )

    # Bucket D: appendix encoder-deferred cases
    worsened_cases = encoder_cases["samples"]["worsened_vs_retrieval_main"]
    anchor_cases = encoder_cases["samples"]["anchor_caution_cases"]

    appendix_d = []
    seen = set()

    for row in worsened_cases[:10]:
        key = (row["query_entity"], row["gold_entity"])
        if key not in seen:
            item = dict(row)
            item["appendix_reason"] = "worsened_vs_retrieval_main"
            appendix_d.append(item)
            seen.add(key)

    for row in anchor_cases[:10]:
        key = (row["query_entity"], row["gold_entity"])
        if key not in seen:
            item = dict(row)
            item["appendix_reason"] = "anchor_caution"
            appendix_d.append(item)
            seen.add(key)

    shortlist = {
        "week": 18,
        "day": 4,
        "main_row_after_week17": main_table["main_row_after_week17"],
        "appendix_row": main_table["appendix_row"],
        "bucket_counts": {
            "backbone_to_retrieval_improved_total": len(bucket_a),
            "ontology_failure_retrieval_success_total": len(bucket_b),
            "same_rank_cleaner_graph_total": len(bucket_c),
            "encoder_appendix_cases_total": len(appendix_d),
        },
        "selected_cases": {
            "backbone_to_retrieval_improved": pick_top(bucket_a, 5),
            "ontology_failure_retrieval_success": pick_top(bucket_b, 5),
            "same_rank_cleaner_graph": pick_top(bucket_c, 5),
            "encoder_appendix_deferred": pick_top(appendix_d, 5),
        },
        "selection_notes": [
            "Bucket A highlights cases where the frozen retrieval main row improves over backbone_raw.",
            "Bucket B highlights ontology-negative-control failure cases rescued by retrieval main.",
            "Bucket C highlights same-rank cases where retrieval main supports a cleaner graph/evidence narrative.",
            "Bucket D highlights appendix cases explaining why encoder was deferred after week 17.",
        ],
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)

    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(shortlist, f, indent=2, ensure_ascii=False)

    lines = []
    lines.append("# Week 18 Day 4 — Case-study Shortlist\n")
    lines.append("## Bucket counts")
    for k, v in shortlist["bucket_counts"].items():
        lines.append(f"- **{k}**: `{v}`")
    lines.append("")
    lines.append("## Selected shortlist")
    for bucket_name, items in shortlist["selected_cases"].items():
        lines.append(f"### {bucket_name}")
        for item in items:
            lines.append(
                f"- `{item['query_entity']}` | gold=`{item['gold_entity']}` | "
                f"backbone={item.get('backbone_rank', 'NA')}, "
                f"ontology={item.get('ontology_rank', 'NA')}, "
                f"soft={item.get('soft_support_rank', item.get('retrieval_rank', 'NA'))}, "
                f"retrieval={item.get('retrieval_rank', 'NA')}"
            )
        lines.append("")
    lines.append("## Notes")
    for note in shortlist["selection_notes"]:
        lines.append(f"- {note}")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"[OK] wrote {OUT_JSON}")
    print(f"[OK] wrote {OUT_MD}")
    print(json.dumps(shortlist["bucket_counts"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()