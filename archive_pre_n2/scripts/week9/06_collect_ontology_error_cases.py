import argparse
import json
from collections import Counter
from pathlib import Path


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def build_md_report(error_report, out_path: Path):
    s = error_report["summary"]

    lines = []
    lines.append("# Day 6 — Error Review")
    lines.append("")
    lines.append("## 1. Goal")
    lines.append("Review ontology-only errors, classify edge cases, and prepare a clean interpretation before week 10.")
    lines.append("")
    lines.append("## 2. Summary")
    for k in [
        "total_queries",
        "fallback_queries",
        "strict_empty_queries",
        "gold_removed_queries",
        "singleton_queries",
        "direct_only_queries",
        "mechanism_only_queries",
        "mixed_support_queries",
        "all_unsupported_queries",
        "total_supported_candidates",
        "total_unsupported_candidates_final",
    ]:
        lines.append(f"- {k}: {s[k]}")
    lines.append("")
    lines.append("## 3. Ranking / constraint context")
    for k, v in error_report["ranking_metrics"].items():
        lines.append(f"- ranking_{k}: {v}")
    for k, v in error_report["constraint_metrics"].items():
        lines.append(f"- constraint_{k}: {v}")
    lines.append("")
    lines.append("## 4. Main issue tags")
    for k, v in error_report["issue_tag_counts"]:
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## 5. Sample fallback queries")
    if error_report["sample_fallback_queries"]:
        for x in error_report["sample_fallback_queries"]:
            lines.append(
                f"- query={x['query_entity']} | gold={x['gold_entity']} | "
                f"top5={x['top5_candidates']} | support={x['top5_support_types']}"
            )
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## 6. Sample gold-removed queries")
    if error_report["sample_gold_removed_queries"]:
        for x in error_report["sample_gold_removed_queries"]:
            lines.append(
                f"- query={x['query_entity']} | gold={x['gold_entity']} | "
                f"gold_in_topk_ready={x['gold_in_topk_ready']} | gold_in_topk_ontology={x['gold_in_topk_ontology']} | "
                f"fallback={x['ontology_fallback_used']}"
            )
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## 7. Sample mechanism-only queries")
    if error_report["sample_mechanism_only_queries"]:
        for x in error_report["sample_mechanism_only_queries"]:
            lines.append(
                f"- query={x['query_entity']} | gold={x['gold_entity']} | "
                f"top5={x['top5_candidates']} | support={x['top5_support_types']}"
            )
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## 8. Interpretation")
    lines.append("- Day 6 does not introduce new modeling changes.")
    lines.append("- The main purpose is to separate strict ontology behavior from fallback-driven sanity behavior.")
    lines.append("- If fallback dominates the row, week 10 should attach hard/soft safety to the supported subset carefully.")
    lines.append("")
    lines.append("## 9. Day-6 decision")
    if s["fallback_queries"] <= 50 and s["gold_removed_queries"] <= 250:
        lines.append("- Decision: GO")
    elif s["fallback_queries"] <= 150:
        lines.append("- Decision: CONDITIONAL GO")
    else:
        lines.append("- Decision: NO-GO")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--type_filtered_candidates",
        default="dataset/setting_a/18_ontology_only/valid_top20_type_filtered.json",
    )
    parser.add_argument(
        "--ontology_candidates",
        default="dataset/setting_a/18_ontology_only/valid_top20_ontology_only.json",
    )
    parser.add_argument(
        "--schema_report",
        default="dataset/setting_a/18_ontology_only/schema_validity_report.json",
    )
    parser.add_argument(
        "--ontology_filter_report",
        default="dataset/setting_a/18_ontology_only/ontology_filter_report.json",
    )
    parser.add_argument(
        "--ranking_metrics",
        default="results/week9/ontology_only_valid/ranking_metrics.json",
    )
    parser.add_argument(
        "--constraint_metrics",
        default="results/week9/ontology_only_valid/constraint_metrics.json",
    )
    parser.add_argument(
        "--candidate_summary",
        default="results/week9/ontology_only_valid/candidate_summary.json",
    )
    parser.add_argument(
        "--output_error_json",
        default="results/week9/ontology_only_valid/error_cases.json",
    )
    parser.add_argument(
        "--output_md_report",
        default="reports/week9/day6_error_review.md",
    )
    parser.add_argument(
        "--sample_limit",
        type=int,
        default=10,
    )
    args = parser.parse_args()

    type_filtered = load_json(Path(args.type_filtered_candidates))
    ontology_rows = load_json(Path(args.ontology_candidates))
    schema_report = load_json(Path(args.schema_report))
    ontology_filter_report = load_json(Path(args.ontology_filter_report))
    ranking_metrics = load_json(Path(args.ranking_metrics))
    constraint_metrics = load_json(Path(args.constraint_metrics))
    candidate_summary = load_json(Path(args.candidate_summary))

    before_by_qid = {int(r["query_entity_id"]): r for r in type_filtered}

    issue_tag_counter = Counter()

    fallback_queries = []
    gold_removed_queries = []
    singleton_queries = []
    mechanism_only_queries = []
    direct_only_queries = []
    all_unsupported_queries = []

    summary = {
        "total_queries": len(ontology_rows),
        "fallback_queries": 0,
        "strict_empty_queries": 0,
        "gold_removed_queries": 0,
        "singleton_queries": 0,
        "direct_only_queries": 0,
        "mechanism_only_queries": 0,
        "mixed_support_queries": 0,
        "all_unsupported_queries": 0,
        "total_supported_candidates": 0,
        "total_unsupported_candidates_final": 0,
    }

    for row in ontology_rows:
        qid = int(row["query_entity_id"])
        before = before_by_qid[qid]

        cands = row.get("candidate_entities", row.get("rank_entities", []))
        supports = row.get("candidate_support_types", [])
        query_entity = row["query_entity"]
        gold_entity = row["gold_entity"]

        num_direct = sum(1 for s in supports if s == "direct")
        num_mech = sum(1 for s in supports if s == "mechanism")
        num_unsup = sum(1 for s in supports if s == "unsupported")
        num_supported = num_direct + num_mech

        summary["total_supported_candidates"] += num_supported
        summary["total_unsupported_candidates_final"] += num_unsup

        tags = []

        if row.get("ontology_fallback_used", False):
            summary["fallback_queries"] += 1
            tags.append("fallback_query")

        if num_supported == 0:
            summary["strict_empty_queries"] += 1
            tags.append("strict_empty")

        if not row.get("gold_in_topk_ontology", False) and row.get("gold_in_topk_ready", False):
            summary["gold_removed_queries"] += 1
            tags.append("gold_removed_by_ontology")

        if len(cands) == 1:
            summary["singleton_queries"] += 1
            tags.append("singleton_after_ontology")

        if num_direct > 0 and num_mech == 0 and num_unsup == 0:
            summary["direct_only_queries"] += 1
            tags.append("direct_only")

        if num_mech > 0 and num_direct == 0 and num_unsup == 0:
            summary["mechanism_only_queries"] += 1
            tags.append("mechanism_only")

        if num_direct > 0 and num_mech > 0:
            summary["mixed_support_queries"] += 1
            tags.append("mixed_support")

        if num_unsup == len(cands) and len(cands) > 0:
            summary["all_unsupported_queries"] += 1
            tags.append("all_unsupported_after_fallback")

        if len(cands) <= 2:
            tags.append("ranking_risk_small_candidate_set")

        if row.get("ontology_fallback_used", False):
            if len(fallback_queries) < args.sample_limit:
                fallback_queries.append({
                    "query_entity": query_entity,
                    "gold_entity": gold_entity,
                    "top5_candidates": cands[:5],
                    "top5_support_types": supports[:5],
                })

        if not row.get("gold_in_topk_ontology", False) and row.get("gold_in_topk_ready", False):
            if len(gold_removed_queries) < args.sample_limit:
                gold_removed_queries.append({
                    "query_entity": query_entity,
                    "gold_entity": gold_entity,
                    "gold_in_topk_ready": row.get("gold_in_topk_ready", False),
                    "gold_in_topk_ontology": row.get("gold_in_topk_ontology", False),
                    "ontology_fallback_used": row.get("ontology_fallback_used", False),
                    "top5_candidates": cands[:5],
                    "top5_support_types": supports[:5],
                })

        if len(cands) == 1:
            if len(singleton_queries) < args.sample_limit:
                singleton_queries.append({
                    "query_entity": query_entity,
                    "gold_entity": gold_entity,
                    "top5_candidates": cands[:5],
                    "top5_support_types": supports[:5],
                })

        if num_mech > 0 and num_direct == 0 and num_unsup == 0:
            if len(mechanism_only_queries) < args.sample_limit:
                mechanism_only_queries.append({
                    "query_entity": query_entity,
                    "gold_entity": gold_entity,
                    "top5_candidates": cands[:5],
                    "top5_support_types": supports[:5],
                })

        if num_direct > 0 and num_mech == 0 and num_unsup == 0:
            if len(direct_only_queries) < args.sample_limit:
                direct_only_queries.append({
                    "query_entity": query_entity,
                    "gold_entity": gold_entity,
                    "top5_candidates": cands[:5],
                    "top5_support_types": supports[:5],
                })

        if num_unsup == len(cands) and len(cands) > 0:
            if len(all_unsupported_queries) < args.sample_limit:
                all_unsupported_queries.append({
                    "query_entity": query_entity,
                    "gold_entity": gold_entity,
                    "top5_candidates": cands[:5],
                    "top5_support_types": supports[:5],
                })

        for t in tags:
            issue_tag_counter[t] += 1

    error_report = {
        "day": 6,
        "title": "Ontology error review",
        "inputs": {
            "type_filtered_candidates": args.type_filtered_candidates,
            "ontology_candidates": args.ontology_candidates,
            "schema_report": args.schema_report,
            "ontology_filter_report": args.ontology_filter_report,
            "ranking_metrics": args.ranking_metrics,
            "constraint_metrics": args.constraint_metrics,
            "candidate_summary": args.candidate_summary,
        },
        "summary": summary,
        "ranking_metrics": ranking_metrics,
        "constraint_metrics": constraint_metrics,
        "candidate_summary": candidate_summary,
        "schema_report_snapshot": {
            "invalid_evidence_triples": schema_report["evidence_validity"]["invalid_evidence_triples"],
            "unsupported_path_sequences": schema_report["path_validity"]["unsupported_path_sequences"],
        },
        "ontology_filter_snapshot": {
            "removed_unsupported_candidates": ontology_filter_report["removed_unsupported_candidates"],
            "fallback_queries": ontology_filter_report["fallback_queries"],
            "gold_in_ontology_candidates": ontology_filter_report["gold_in_ontology_candidates"],
        },
        "issue_tag_counts": issue_tag_counter.most_common(),
        "sample_fallback_queries": fallback_queries,
        "sample_gold_removed_queries": gold_removed_queries,
        "sample_singleton_queries": singleton_queries,
        "sample_mechanism_only_queries": mechanism_only_queries,
        "sample_direct_only_queries": direct_only_queries,
        "sample_all_unsupported_queries": all_unsupported_queries,
    }

    save_json(error_report, Path(args.output_error_json))
    build_md_report(error_report, Path(args.output_md_report))

    print(f"Saved: {args.output_error_json}")
    print(f"Saved: {args.output_md_report}")
    print("Summary:")
    print("  total_queries =", summary["total_queries"])
    print("  fallback_queries =", summary["fallback_queries"])
    print("  strict_empty_queries =", summary["strict_empty_queries"])
    print("  gold_removed_queries =", summary["gold_removed_queries"])
    print("  singleton_queries =", summary["singleton_queries"])
    print("  direct_only_queries =", summary["direct_only_queries"])
    print("  mechanism_only_queries =", summary["mechanism_only_queries"])
    print("  mixed_support_queries =", summary["mixed_support_queries"])
    print("  all_unsupported_queries =", summary["all_unsupported_queries"])
    print("  total_supported_candidates =", summary["total_supported_candidates"])
    print("  total_unsupported_candidates_final =", summary["total_unsupported_candidates_final"])


if __name__ == "__main__":
    main()