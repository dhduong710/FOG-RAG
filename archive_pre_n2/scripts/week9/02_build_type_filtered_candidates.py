import argparse
import json
import csv
from collections import Counter
from copy import deepcopy
from pathlib import Path


def normalize_text(x: str) -> str:
    if x is None:
        return ""
    return str(x).strip()


def load_type_map_tsv(path: Path):
    entity_to_type = {}
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        required = {"entity", "final_type"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError(
                f"{path} must contain at least columns: {sorted(required)}; got {reader.fieldnames}"
            )
        for row in reader:
            entity = normalize_text(row.get("entity"))
            final_type = normalize_text(row.get("final_type"))
            if entity:
                entity_to_type[entity] = final_type
    return entity_to_type


def load_fallback_json(path: Path):
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    # expected: {entity_name: type}
    return {normalize_text(k): normalize_text(v) for k, v in data.items()}


def resolve_type(name, main_type_map, fallback_type_map):
    name = normalize_text(name)
    if name in main_type_map:
        return main_type_map[name], "type_map.tsv"
    if name in fallback_type_map:
        return fallback_type_map[name], "entity_name_to_type.json"
    return "UNKNOWN", "missing"


def get_candidate_keys(row):
    """
    Support both schemas:
    - candidate_entities / candidate_entity_ids
    - rank_entities / rank_entities_id
    """
    if "candidate_entities" in row and "candidate_entity_ids" in row:
        return "candidate_entities", "candidate_entity_ids"
    if "rank_entities" in row and "rank_entities_id" in row:
        return "rank_entities", "rank_entities_id"
    raise KeyError(
        "Cannot find candidate keys. Expected either "
        "('candidate_entities','candidate_entity_ids') or "
        "('rank_entities','rank_entities_id')."
    )


def build_md_report(report, md_path: Path):
    lines = []
    lines.append("# Day 2 — Type Filtering")
    lines.append("")
    lines.append("## 1. Goal")
    lines.append("Filter candidates so that every remaining candidate is of type `Drug`.")
    lines.append("")
    lines.append("## 2. Inputs")
    lines.append(f"- input_candidates: `{report['input_candidates']}`")
    lines.append(f"- type_map_tsv: `{report['type_map_tsv']}`")
    lines.append(f"- fallback_type_json: `{report['fallback_type_json']}`")
    lines.append("")
    lines.append("## 3. Outputs")
    lines.append(f"- filtered_candidates: `{report['output_filtered_candidates']}`")
    lines.append(f"- filter_report_json: `{report['output_filter_report']}`")
    lines.append("")
    lines.append("## 4. Summary")
    lines.append(f"- total_queries: {report['total_queries']}")
    lines.append(f"- total_candidates_before: {report['total_candidates_before']}")
    lines.append(f"- total_candidates_after: {report['total_candidates_after']}")
    lines.append(f"- total_removed: {report['total_removed']}")
    lines.append(f"- empty_queries_after_filter: {report['empty_queries_after_filter']}")
    lines.append(f"- remaining_non_drug_candidates: {report['remaining_non_drug_candidates']}")
    lines.append(f"- top1_changed_queries: {report['top1_changed_queries']}")
    lines.append(f"- top5_changed_queries: {report['top5_changed_queries']}")
    lines.append("")
    lines.append("## 5. Removal breakdown by type")
    for k, v in report["removed_type_breakdown"].items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## 6. Type lookup source breakdown")
    for k, v in report["type_lookup_source_breakdown"].items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## 7. Empty-query examples")
    if report["empty_query_examples"]:
        for x in report["empty_query_examples"]:
            lines.append(f"- {x}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## 8. Before/after samples")
    if report["sample_before_after"]:
        for item in report["sample_before_after"]:
            lines.append(f"### Query: {item['query_entity']}")
            lines.append(f"- before_top5: {item['before_top5']}")
            lines.append(f"- after_top5: {item['after_top5']}")
            lines.append(f"- removed_types: {item['removed_types']}")
            lines.append("")
    else:
        lines.append("- no samples")
        lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_candidates",
        default="dataset/setting_a/11_ranker_v2/valid_top20_drkgc_ready.json",
    )
    parser.add_argument(
        "--type_map_tsv",
        default="dataset/setting_b/01_annotations/type_map.tsv",
    )
    parser.add_argument(
        "--fallback_type_json",
        default="dataset/setting_b/01_ontology/entity_name_to_type.json",
    )
    parser.add_argument(
        "--output_filtered_candidates",
        default="dataset/setting_a/18_ontology_only/valid_top20_type_filtered.json",
    )
    parser.add_argument(
        "--output_filter_report",
        default="dataset/setting_a/18_ontology_only/ontology_filter_report.json",
    )
    parser.add_argument(
        "--output_md_report",
        default="reports/week9/day2_type_filtering.md",
    )
    parser.add_argument(
        "--target_type",
        default="Drug",
    )
    parser.add_argument(
        "--sample_limit",
        type=int,
        default=10,
    )
    args = parser.parse_args()

    input_candidates = Path(args.input_candidates)
    type_map_tsv = Path(args.type_map_tsv)
    fallback_type_json = Path(args.fallback_type_json)
    output_filtered_candidates = Path(args.output_filtered_candidates)
    output_filter_report = Path(args.output_filter_report)
    output_md_report = Path(args.output_md_report)

    output_filtered_candidates.parent.mkdir(parents=True, exist_ok=True)
    output_filter_report.parent.mkdir(parents=True, exist_ok=True)
    output_md_report.parent.mkdir(parents=True, exist_ok=True)

    main_type_map = load_type_map_tsv(type_map_tsv)
    fallback_type_map = load_fallback_json(fallback_type_json)

    with input_candidates.open("r", encoding="utf-8") as f:
        data = json.load(f)

    filtered_rows = []
    removed_type_counter = Counter()
    lookup_source_counter = Counter()

    total_candidates_before = 0
    total_candidates_after = 0
    total_removed = 0
    empty_queries_after_filter = 0
    remaining_non_drug_candidates = 0
    top1_changed_queries = 0
    top5_changed_queries = 0

    empty_query_examples = []
    sample_before_after = []

    for row in data:
        new_row = deepcopy(row)
        cand_name_key, cand_id_key = get_candidate_keys(row)

        cand_names = row[cand_name_key]
        cand_ids = row[cand_id_key]

        if len(cand_names) != len(cand_ids):
            raise ValueError(
                f"Length mismatch in row for query={row.get('query_entity')}: "
                f"{cand_name_key} has {len(cand_names)} but {cand_id_key} has {len(cand_ids)}"
            )

        total_candidates_before += len(cand_names)

        kept_names = []
        kept_ids = []
        removed_names = []
        removed_types = []

        for name, cid in zip(cand_names, cand_ids):
            etype, source = resolve_type(name, main_type_map, fallback_type_map)
            lookup_source_counter[source] += 1

            if etype == args.target_type:
                kept_names.append(name)
                kept_ids.append(cid)
            else:
                removed_names.append(name)
                removed_types.append(etype)
                removed_type_counter[etype] += 1

        total_candidates_after += len(kept_names)
        total_removed += len(removed_names)

        before_top1 = cand_names[0] if cand_names else None
        after_top1 = kept_names[0] if kept_names else None
        if before_top1 != after_top1:
            top1_changed_queries += 1

        before_top5 = cand_names[:5]
        after_top5 = kept_names[:5]
        if before_top5 != after_top5:
            top5_changed_queries += 1

        if len(kept_names) == 0:
            empty_queries_after_filter += 1
            if len(empty_query_examples) < args.sample_limit:
                empty_query_examples.append(row.get("query_entity", "UNKNOWN_QUERY"))

        # sanity: count any remaining non-Drug
        for n in kept_names:
            t, _ = resolve_type(n, main_type_map, fallback_type_map)
            if t != args.target_type:
                remaining_non_drug_candidates += 1

        new_row[cand_name_key] = kept_names
        new_row[cand_id_key] = kept_ids

        # keep traceable metadata for week9 intermediate artifact
        new_row["type_filter_target_type"] = args.target_type
        new_row["num_candidates_before_type_filter"] = len(cand_names)
        new_row["num_candidates_after_type_filter"] = len(kept_names)
        new_row["num_candidates_removed_by_type_filter"] = len(removed_names)
        new_row["empty_after_type_filter"] = len(kept_names) == 0

        filtered_rows.append(new_row)

        if len(sample_before_after) < args.sample_limit:
            sample_before_after.append({
                "query_entity": row.get("query_entity", "UNKNOWN_QUERY"),
                "before_top5": before_top5,
                "after_top5": after_top5,
                "removed_types": dict(Counter(removed_types)),
            })

    report = {
        "day": 2,
        "title": "Type filtering",
        "target_type": args.target_type,
        "input_candidates": str(input_candidates),
        "type_map_tsv": str(type_map_tsv),
        "fallback_type_json": str(fallback_type_json),
        "output_filtered_candidates": str(output_filtered_candidates),
        "output_filter_report": str(output_filter_report),
        "total_queries": len(data),
        "total_candidates_before": total_candidates_before,
        "total_candidates_after": total_candidates_after,
        "total_removed": total_removed,
        "empty_queries_after_filter": empty_queries_after_filter,
        "remaining_non_drug_candidates": remaining_non_drug_candidates,
        "top1_changed_queries": top1_changed_queries,
        "top5_changed_queries": top5_changed_queries,
        "removed_type_breakdown": dict(removed_type_counter),
        "type_lookup_source_breakdown": dict(lookup_source_counter),
        "empty_query_examples": empty_query_examples,
        "sample_before_after": sample_before_after,
    }

    with output_filtered_candidates.open("w", encoding="utf-8") as f:
        json.dump(filtered_rows, f, indent=2, ensure_ascii=False)

    with output_filter_report.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    build_md_report(report, output_md_report)

    print(f"Saved filtered candidates: {output_filtered_candidates}")
    print(f"Saved filter report json: {output_filter_report}")
    print(f"Saved markdown report: {output_md_report}")
    print("Summary:")
    print(f"  total_queries = {report['total_queries']}")
    print(f"  total_candidates_before = {report['total_candidates_before']}")
    print(f"  total_candidates_after = {report['total_candidates_after']}")
    print(f"  total_removed = {report['total_removed']}")
    print(f"  empty_queries_after_filter = {report['empty_queries_after_filter']}")
    print(f"  remaining_non_drug_candidates = {report['remaining_non_drug_candidates']}")
    print(f"  top1_changed_queries = {report['top1_changed_queries']}")
    print(f"  top5_changed_queries = {report['top5_changed_queries']}")


if __name__ == "__main__":
    main()