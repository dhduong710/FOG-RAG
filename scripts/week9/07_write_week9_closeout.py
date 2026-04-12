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


def load_baseline_metrics(path: Path):
    """
    Supports:
    - JSON metrics file with keys: mrr, hits1, hits3, hits10
    - text metrics file containing a line like:
      ranking metrics: {'mrr': ..., 'hits1': ..., 'hits3': ..., 'hits10': ...}
    """
    if not path.exists():
        raise FileNotFoundError(f"Baseline metrics file not found: {path}")

    if path.suffix.lower() == ".json":
        obj = load_json(path)
        required = ["mrr", "hits1", "hits3", "hits10"]
        missing = [k for k in required if k not in obj]
        if missing:
            raise KeyError(
                f"Baseline JSON missing keys {missing}: {path}"
            )
        return {
            "mrr": float(obj["mrr"]),
            "hits1": float(obj["hits1"]),
            "hits3": float(obj["hits3"]),
            "hits10": float(obj["hits10"]),
        }

    lines = path.read_text(encoding="utf-8").strip().splitlines()
    metrics = None
    for line in lines:
        if "ranking metrics:" in line:
            payload = line.split("ranking metrics:", 1)[1].strip()
            metrics = ast.literal_eval(payload)

    if metrics is None:
        raise ValueError(f"Cannot parse ranking metrics from {path}")

    return {
        "mrr": float(metrics["mrr"]),
        "hits1": float(metrics["hits1"]),
        "hits3": float(metrics["hits3"]),
        "hits10": float(metrics["hits10"]),
    }


def build_ablation_md(ablation, out_path: Path):
    b = ablation["backbone_reference"]
    o = ablation["ontology_only"]
    d = ablation["delta"]

    lines = []
    lines.append("# Ontology-only Ablation v0")
    lines.append("")
    lines.append("| Row | MRR | Hits@1 | Hits@3 | Hits@10 | Notes |")
    lines.append("|---|---:|---:|---:|---:|---|")
    lines.append(
        f"| backbone_reference | {b['mrr']:.8f} | {b['hits1']:.8f} | {b['hits3']:.8f} | {b['hits10']:.8f} | week7-v2 main reference |"
    )
    lines.append(
        f"| backbone_plus_ontology | {o['mrr']:.8f} | {o['hits1']:.8f} | {o['hits3']:.8f} | {o['hits10']:.8f} | week9 ontology-only sanity row |"
    )
    lines.append("")
    lines.append("## Delta (ontology - backbone)")
    lines.append(f"- ΔMRR: {d['mrr']:.8f}")
    lines.append(f"- ΔHits@1: {d['hits1']:.8f}")
    lines.append(f"- ΔHits@3: {d['hits3']:.8f}")
    lines.append(f"- ΔHits@10: {d['hits10']:.8f}")
    lines.append("")
    lines.append("## Constraint-side context")
    for k, v in ablation["constraint_context"].items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("- ontology-only branch is traceable and runnable.")
    lines.append("- current row is conservative and affected by strict-empty queries plus fallback.")
    lines.append("- use this row as groundwork/supporting evidence, not as the final winning novelty row.")
    lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def build_closeout_md(closeout, out_path: Path):
    s = closeout["week9_summary"]
    b = closeout["backbone_reference"]
    o = closeout["ontology_only"]
    d = closeout["delta"]
    e = closeout["error_review"]

    lines = []
    lines.append("# Day 7 — Week 9 Closeout")
    lines.append("")
    lines.append("## 1. Goal of Week 9")
    lines.append("Lock ontology-aware retrieval groundwork before adding contraindication-aware hard/soft handling in week 10.")
    lines.append("")
    lines.append("## 2. What was completed")
    for item in closeout["completed_items"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## 3. Backbone vs +ontology")
    lines.append(f"- backbone MRR: {b['mrr']:.8f}")
    lines.append(f"- backbone Hits@1: {b['hits1']:.8f}")
    lines.append(f"- backbone Hits@3: {b['hits3']:.8f}")
    lines.append(f"- backbone Hits@10: {b['hits10']:.8f}")
    lines.append("")
    lines.append(f"- +ontology MRR: {o['mrr']:.8f}")
    lines.append(f"- +ontology Hits@1: {o['hits1']:.8f}")
    lines.append(f"- +ontology Hits@3: {o['hits3']:.8f}")
    lines.append(f"- +ontology Hits@10: {o['hits10']:.8f}")
    lines.append("")
    lines.append("### Delta (+ontology - backbone)")
    lines.append(f"- ΔMRR: {d['mrr']:.8f}")
    lines.append(f"- ΔHits@1: {d['hits1']:.8f}")
    lines.append(f"- ΔHits@3: {d['hits3']:.8f}")
    lines.append(f"- ΔHits@10: {d['hits10']:.8f}")
    lines.append("")
    lines.append("## 4. Ontology-only branch summary")
    for k in [
        "removed_unsupported_candidates",
        "fallback_queries",
        "gold_in_ontology_candidates",
        "ConstraintViolationRate",
        "QueryHasConstraintViolationRate",
    ]:
        lines.append(f"- {k}: {s[k]}")
    lines.append("")
    lines.append("## 5. Main error-review findings")
    for k in [
        "strict_empty_queries",
        "gold_removed_queries",
        "singleton_queries",
        "direct_only_queries",
        "mechanism_only_queries",
        "mixed_support_queries",
        "all_unsupported_queries",
    ]:
        lines.append(f"- {k}: {e[k]}")
    lines.append("")
    lines.append("## 6. Main interpretation")
    for item in closeout["main_interpretation"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## 7. Decision for end of week 9")
    lines.append(f"- Decision: {closeout['decision']}")
    lines.append("")
    lines.append("## 8. Week 10 handoff")
    for item in closeout["week10_handoff"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## 9. What not to overclaim")
    for item in closeout["do_not_overclaim"]:
        lines.append(f"- {item}")
    lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--protocol_json",
        default="results/week9/novelty1_protocol.json",
    )
    parser.add_argument(
        "--baseline_metrics_path",
        default="results/week7/backbone_valid_v2_short/valid_eval_v2/eval_valid_v2_metrics.json",
    )
    parser.add_argument(
        "--ranking_metrics_json",
        default="results/week9/ontology_only_valid/ranking_metrics.json",
    )
    parser.add_argument(
        "--constraint_metrics_json",
        default="results/week9/ontology_only_valid/constraint_metrics.json",
    )
    parser.add_argument(
        "--candidate_summary_json",
        default="results/week9/ontology_only_valid/candidate_summary.json",
    )
    parser.add_argument(
        "--ontology_filter_report_json",
        default="dataset/setting_a/18_ontology_only/ontology_filter_report.json",
    )
    parser.add_argument(
        "--error_cases_json",
        default="results/week9/ontology_only_valid/error_cases.json",
    )
    parser.add_argument(
        "--output_ablation_json",
        default="results/week9/ontology_only_ablation_v0.json",
    )
    parser.add_argument(
        "--output_ablation_md",
        default="results/week9/ontology_only_ablation_v0.md",
    )
    parser.add_argument(
        "--output_closeout_md",
        default="reports/week9/day7_week9_closeout.md",
    )
    args = parser.parse_args()

    protocol = load_json(Path(args.protocol_json))
    baseline = load_baseline_metrics(Path(args.baseline_metrics_path))
    ranking = load_json(Path(args.ranking_metrics_json))
    constraint = load_json(Path(args.constraint_metrics_json))
    candidate_summary = load_json(Path(args.candidate_summary_json))
    ontology_filter = load_json(Path(args.ontology_filter_report_json))
    error_cases = load_json(Path(args.error_cases_json))

    delta = {
        "mrr": round(ranking["mrr"] - baseline["mrr"], 8),
        "hits1": round(ranking["hits1"] - baseline["hits1"], 8),
        "hits3": round(ranking["hits3"] - baseline["hits3"], 8),
        "hits10": round(ranking["hits10"] - baseline["hits10"], 8),
    }

    ablation = {
        "title": "week9 ontology-only ablation v0",
        "backbone_reference": baseline,
        "ontology_only": ranking,
        "delta": delta,
        "constraint_context": {
            "ConstraintViolationRate": constraint["ConstraintViolationRate"],
            "QueryHasConstraintViolationRate": constraint["QueryHasConstraintViolationRate"],
            "fallback_queries": constraint["fallback_queries"],
            "gold_in_topk_ontology": constraint["gold_in_topk_ontology"],
            "unsupported_final_candidates": constraint["unsupported_final_candidates"],
        },
    }

    decision = "CONDITIONAL GO"

    closeout = {
        "week": 9,
        "title": "Type filtering + schema validity groundwork for Novelty 1",
        "protocol_title": protocol["title"],
        "backbone_reference": baseline,
        "ontology_only": ranking,
        "delta": delta,
        "week9_summary": {
            "removed_unsupported_candidates": ontology_filter["removed_unsupported_candidates"],
            "fallback_queries": ontology_filter["fallback_queries"],
            "gold_in_ontology_candidates": ontology_filter["gold_in_ontology_candidates"],
            "ConstraintViolationRate": constraint["ConstraintViolationRate"],
            "QueryHasConstraintViolationRate": constraint["QueryHasConstraintViolationRate"],
        },
        "error_review": {
            "strict_empty_queries": error_cases["summary"]["strict_empty_queries"],
            "gold_removed_queries": error_cases["summary"]["gold_removed_queries"],
            "singleton_queries": error_cases["summary"]["singleton_queries"],
            "direct_only_queries": error_cases["summary"]["direct_only_queries"],
            "mechanism_only_queries": error_cases["summary"]["mechanism_only_queries"],
            "mixed_support_queries": error_cases["summary"]["mixed_support_queries"],
            "all_unsupported_queries": error_cases["summary"]["all_unsupported_queries"],
        },
        "completed_items": [
            "Protocol for Novelty 1 was frozen with week7-v2 kept as the fairness anchor.",
            "Candidate type filtering confirmed the candidate list was Drug-only.",
            "Schema validity checker for candidate/path/evidence became traceable after parser fixes.",
            "Ontology-only candidate artifact was built and evaluated on valid.",
            "Error review separated strict-empty behavior from fallback-driven behavior.",
        ],
        "main_interpretation": [
            "Week 9 succeeded as ontology-aware retrieval groundwork, not as a final winning novelty row.",
            "The ontology-only branch is clean and traceable, but still too conservative.",
            "The main trade-off is between cleanliness and ranking usability.",
            "Strict ontology support is real, but fallback reintroduces unsupported candidates for 100 queries.",
            "Direct support currently dominates mechanism support, so the branch is not yet a strong mechanism-grounded main path.",
        ],
        "decision": decision,
        "week10_handoff": [
            "Keep week7-v2 as the main backbone reference.",
            "Treat week9 ontology-only as a supporting / groundwork row, not the final main variant.",
            "Apply hard-filter and soft-penalty safety handling first on the ontology-supported subset.",
            "Do not use the fallback-heavy row as the main safety row without an explicit note.",
            "Use valid as the decision split again in week 10.",
        ],
        "do_not_overclaim": [
            "Do not claim ontology-only already improves ranking over the backbone.",
            "Do not claim current ontology-only row is the final novelty winner.",
            "Do not hide that 100 queries required fallback and 354 queries lost the gold candidate.",
            "Do not present the fallback-heavy row as a purely clean ontology-constrained row.",
        ],
    }

    save_json(ablation, Path(args.output_ablation_json))
    build_ablation_md(ablation, Path(args.output_ablation_md))
    build_closeout_md(closeout, Path(args.output_closeout_md))

    print(f"Saved: {args.output_ablation_json}")
    print(f"Saved: {args.output_ablation_md}")
    print(f"Saved: {args.output_closeout_md}")
    print("Summary:")
    print("  baseline =", baseline)
    print("  ontology_only =", ranking)
    print("  delta =", delta)
    print("  decision =", decision)


if __name__ == "__main__":
    main()