import argparse
import ast
import json
from pathlib import Path


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def parse_metrics_file(path: Path):
    """
    Expect a line like:
    ranking metrics: {'mrr': 0.1, 'hits1': 0.2, 'hits3': 0.3, 'hits10': 0.4}
    """
    text = path.read_text(encoding="utf-8").strip().splitlines()
    metrics = None
    for line in text:
        if "ranking metrics:" in line:
            payload = line.split("ranking metrics:", 1)[1].strip()
            payload = payload.replace("np.float64(", "").replace("np.float32(", "").replace(")", "")
            metrics = ast.literal_eval(payload)
    if metrics is None:
        raise ValueError(f"Cannot parse ranking metrics from {path}")
    return metrics


def parse_optional_baseline(path: Path):
    if not path.exists():
        return None

    if path.suffix.lower() == ".json":
        return load_json(path)

    return parse_metrics_file(path)


def build_md_report(
    ranking_metrics,
    baseline_metrics,
    constraint_metrics,
    candidate_summary,
    out_path: Path,
):
    lines = []
    lines.append("# Day 5 — Valid Sanity Evaluation")
    lines.append("")
    lines.append("## 1. Goal")
    lines.append("Run valid-side sanity evaluation for the ontology-only branch using the frozen backbone reference checkpoint.")
    lines.append("")
    lines.append("## 2. Ranking metrics (`backbone + ontology`)")
    for k, v in ranking_metrics.items():
        lines.append(f"- {k}: {v}")
    lines.append("")

    if baseline_metrics is not None:
        lines.append("## 3. Comparison vs backbone reference")
        for k in ["mrr", "hits1", "hits3", "hits10"]:
            if k in baseline_metrics and k in ranking_metrics:
                delta = ranking_metrics[k] - baseline_metrics[k]
                lines.append(
                    f"- Δ{k}: {delta:.8f} "
                    f"(ontology={ranking_metrics[k]:.8f}, backbone={baseline_metrics[k]:.8f})"
                )
        lines.append("")
    else:
        lines.append("## 3. Comparison vs backbone reference")
        lines.append("- baseline metrics file not found; comparison skipped")
        lines.append("")

    lines.append("## 4. Constraint metrics")
    for k, v in constraint_metrics.items():
        lines.append(f"- {k}: {v}")
    lines.append("")

    lines.append("## 5. Candidate summary")
    for k, v in candidate_summary.items():
        if k == "sample_support_distribution":
            continue
        lines.append(f"- {k}: {v}")
    lines.append("")

    lines.append("## 6. Interpretation")
    lines.append("- This is a sanity evaluation, not a final paper result.")
    lines.append("- If ranking drops but constraint cleanliness improves clearly, the row can still be useful as ontology-only groundwork.")
    lines.append("- High fallback and low gold coverage indicate the ontology-only branch is still conservative.")
    lines.append("")

    if baseline_metrics is not None:
        delta_mrr = ranking_metrics["mrr"] - baseline_metrics["mrr"]
        lines.append("## 7. Day-5 decision")
        if constraint_metrics["ConstraintViolationRate"] < 0.25 and delta_mrr > -0.15:
            lines.append("- Decision: GO")
        elif constraint_metrics["ConstraintViolationRate"] < 0.50:
            lines.append("- Decision: CONDITIONAL GO")
        else:
            lines.append("- Decision: NO-GO")
    else:
        lines.append("## 7. Day-5 decision")
        lines.append("- Decision: CONDITIONAL GO (baseline comparison unavailable)")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ontology_candidates",
        default="dataset/setting_a/18_ontology_only/valid_top20_ontology_only.json",
    )
    parser.add_argument(
        "--day3_schema_report",
        default="dataset/setting_a/18_ontology_only/schema_validity_report.json",
    )
    parser.add_argument(
        "--day4_ontology_report",
        default="dataset/setting_a/18_ontology_only/ontology_filter_report.json",
    )
    parser.add_argument(
        "--metrics_txt",
        default="results/week9/ontology_only_valid/metrics.txt",
    )
    parser.add_argument(
        "--baseline_metrics_path",
        default="results/week7/backbone_valid_v2_short/metrics.txt",
    )
    parser.add_argument(
        "--output_ranking_metrics",
        default="results/week9/ontology_only_valid/ranking_metrics.json",
    )
    parser.add_argument(
        "--output_constraint_metrics",
        default="results/week9/ontology_only_valid/constraint_metrics.json",
    )
    parser.add_argument(
        "--output_candidate_summary",
        default="results/week9/ontology_only_valid/candidate_summary.json",
    )
    parser.add_argument(
        "--output_md_report",
        default="reports/week9/day5_valid_sanity_eval.md",
    )
    args = parser.parse_args()

    ontology_candidates = load_json(Path(args.ontology_candidates))
    day3 = load_json(Path(args.day3_schema_report))
    day4 = load_json(Path(args.day4_ontology_report))
    ranking_metrics = parse_metrics_file(Path(args.metrics_txt))
    baseline_metrics = parse_optional_baseline(Path(args.baseline_metrics_path))

    total_queries = len(ontology_candidates)
    total_final_candidates = 0
    remaining_non_drug_candidates = 0
    unsupported_final_candidates = 0
    queries_with_any_constraint_violation = 0
    direct_final_candidates = 0
    mechanism_final_candidates = 0
    fallback_queries = 0
    gold_in_topk_ontology = 0

    for row in ontology_candidates:
        cands = row.get("candidate_entities", row.get("rank_entities", []))
        supports = row.get("candidate_support_types", [])
        total_final_candidates += len(cands)

        row_violation = False
        for s in supports:
            if s == "unsupported":
                unsupported_final_candidates += 1
                row_violation = True
            elif s == "direct":
                direct_final_candidates += 1
            elif s == "mechanism":
                mechanism_final_candidates += 1

        if row.get("ontology_fallback_used", False):
            fallback_queries += 1
            row_violation = True

        if row.get("gold_in_topk_ontology", False):
            gold_in_topk_ontology += 1

        # by construction of day2/day4 this should stay zero, but keep explicit field
        # if you later add candidate types directly into artifact, update here
        # remaining_non_drug_candidates remains 0 for now

        if row_violation:
            queries_with_any_constraint_violation += 1

    constraint_violation_rate = 0.0
    if total_final_candidates > 0:
        constraint_violation_rate = (
            remaining_non_drug_candidates + unsupported_final_candidates
        ) / total_final_candidates

    query_violation_rate = 0.0
    if total_queries > 0:
        query_violation_rate = queries_with_any_constraint_violation / total_queries

    constraint_metrics = {
        "ConstraintViolationRate": round(constraint_violation_rate, 8),
        "QueryHasConstraintViolationRate": round(query_violation_rate, 8),
        "remaining_non_drug_candidates": remaining_non_drug_candidates,
        "unsupported_final_candidates": unsupported_final_candidates,
        "fallback_queries": fallback_queries,
        "gold_in_topk_ontology": gold_in_topk_ontology,
        "invalid_evidence_triples_day3": day3["evidence_validity"]["invalid_evidence_triples"],
        "unsupported_path_sequences_day3": day3["path_validity"]["unsupported_path_sequences"],
    }

    candidate_summary = {
        "total_queries": total_queries,
        "total_final_candidates": total_final_candidates,
        "direct_final_candidates": direct_final_candidates,
        "mechanism_final_candidates": mechanism_final_candidates,
        "unsupported_final_candidates": unsupported_final_candidates,
        "fallback_queries": fallback_queries,
        "gold_in_topk_ontology": gold_in_topk_ontology,
        "removed_unsupported_candidates_day4": day4["removed_unsupported_candidates"],
        "queries_with_any_direct_support_day4": day4["queries_with_any_direct_support"],
        "queries_with_any_mechanism_support_day4": day4["queries_with_any_mechanism_support"],
        "sample_support_distribution": {
            "direct": direct_final_candidates,
            "mechanism": mechanism_final_candidates,
            "unsupported": unsupported_final_candidates,
        },
    }

    save_json(ranking_metrics, Path(args.output_ranking_metrics))
    save_json(constraint_metrics, Path(args.output_constraint_metrics))
    save_json(candidate_summary, Path(args.output_candidate_summary))
    build_md_report(
        ranking_metrics=ranking_metrics,
        baseline_metrics=baseline_metrics,
        constraint_metrics=constraint_metrics,
        candidate_summary=candidate_summary,
        out_path=Path(args.output_md_report),
    )

    print(f"Saved: {args.output_ranking_metrics}")
    print(f"Saved: {args.output_constraint_metrics}")
    print(f"Saved: {args.output_candidate_summary}")
    print(f"Saved: {args.output_md_report}")
    print("Summary:")
    print("  ranking_metrics =", ranking_metrics)
    print("  constraint_metrics =", constraint_metrics)
    print("  candidate_summary =", candidate_summary)


if __name__ == "__main__":
    main()