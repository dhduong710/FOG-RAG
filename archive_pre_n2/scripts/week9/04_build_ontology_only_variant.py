import argparse
import csv
import json
import pickle
from collections import Counter, defaultdict, deque
from copy import deepcopy
from pathlib import Path

import yaml


def normalize_text(x):
    if x is None:
        return ""
    return str(x).strip()


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def load_pickle(path: Path):
    with path.open("rb") as f:
        return pickle.load(f)


def load_type_map_tsv(path: Path):
    entity_to_type = {}
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        required = {"entity", "final_type"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError(
                f"{path} must contain columns {sorted(required)}; got {reader.fieldnames}"
            )
        for row in reader:
            ent = normalize_text(row.get("entity"))
            typ = normalize_text(row.get("final_type"))
            if ent:
                entity_to_type[ent] = typ
    return entity_to_type


def load_fallback_type_json(path: Path):
    if not path.exists():
        return {}
    data = load_json(path)
    return {normalize_text(k): normalize_text(v) for k, v in data.items()}


def resolve_type(entity_name, main_type_map, fallback_type_map):
    entity_name = normalize_text(entity_name)
    if entity_name in main_type_map:
        return main_type_map[entity_name]
    if entity_name in fallback_type_map:
        return fallback_type_map[entity_name]
    return "UNKNOWN"


def get_candidate_keys(row):
    if "candidate_entities" in row and "candidate_entity_ids" in row:
        return "candidate_entities", "candidate_entity_ids"
    if "rank_entities" in row and "rank_entities_id" in row:
        return "rank_entities", "rank_entities_id"
    raise KeyError(
        "Expected either candidate_entities/candidate_entity_ids "
        "or rank_entities/rank_entities_id."
    )


def normalize_schema_rules(raw_rules):
    normalized = {}
    for rel, obj in raw_rules.items():
        rel = normalize_text(rel)

        if isinstance(obj, list) and len(obj) == 2:
            normalized[rel] = {
                "head_types": {normalize_text(obj[0])},
                "tail_types": {normalize_text(obj[1])},
            }
            continue

        if isinstance(obj, dict):
            head_types = set()
            tail_types = set()

            for hk in ["head_types", "allowed_head_types", "domain", "head"]:
                if hk in obj:
                    val = obj[hk]
                    if isinstance(val, str):
                        head_types.add(normalize_text(val))
                    elif isinstance(val, list):
                        head_types |= {normalize_text(x) for x in val}

            for tk in ["tail_types", "allowed_tail_types", "range", "tail"]:
                if tk in obj:
                    val = obj[tk]
                    if isinstance(val, str):
                        tail_types.add(normalize_text(val))
                    elif isinstance(val, list):
                        tail_types |= {normalize_text(x) for x in val}

            normalized[rel] = {
                "head_types": head_types,
                "tail_types": tail_types,
            }
            continue

        normalized[rel] = {
            "head_types": set(),
            "tail_types": set(),
        }

    return normalized


def schema_allows(relation_name, head_type, tail_type, schema_rules):
    relation_name = normalize_text(relation_name)
    head_type = normalize_text(head_type)
    tail_type = normalize_text(tail_type)

    if relation_name not in schema_rules:
        return False

    rule = schema_rules[relation_name]
    allowed_heads = rule.get("head_types", set())
    allowed_tails = rule.get("tail_types", set())

    if not allowed_heads or not allowed_tails:
        return False

    return head_type in allowed_heads and tail_type in allowed_tails


def load_path_templates(path: Path):
    with path.open("r", encoding="utf-8") as f:
        obj = yaml.safe_load(f)

    valid_sequences = set()

    for item in obj.get("valid_path_templates", []) if isinstance(obj, dict) else []:
        path_steps = item.get("path", [])
        seq = []
        ok = True
        for step in path_steps:
            # expected [head_type, relation, tail_type]
            if not isinstance(step, list) or len(step) != 3:
                ok = False
                break
            seq.append(normalize_text(step[1]))
        if ok and seq:
            valid_sequences.add(tuple(seq))

    return valid_sequences


def build_directed_edges(subgraph):
    """
    Returns list of edges:
      (h_id, r_name, t_id)
    """
    edges = []
    for triple in subgraph:
        if len(triple) != 3:
            continue
        h, r, t = int(triple[0]), int(triple[1]), int(triple[2])
        edges.append((h, r, t))
    return edges


def build_directed_adj(subgraph, id2entity, id2relation, type_map, fallback_type_map, schema_rules):
    """
    Keep only schema-valid directed edges.
    Returns adjacency: node_id -> list[(relation_name, next_node_id)]
    """
    adj = defaultdict(list)

    for triple in subgraph:
        if len(triple) != 3:
            continue
        h_id, r_id, t_id = int(triple[0]), int(triple[1]), int(triple[2])

        h_name = normalize_text(id2entity[h_id])
        r_name = normalize_text(id2relation[r_id])
        t_name = normalize_text(id2entity[t_id])

        h_type = resolve_type(h_name, type_map, fallback_type_map)
        t_type = resolve_type(t_name, type_map, fallback_type_map)

        if schema_allows(r_name, h_type, t_type, schema_rules):
            adj[h_id].append((r_name, t_id))

    return adj


def has_direct_valid_indication_edge(candidate_id, query_id, subgraph, id2entity, id2relation, type_map, fallback_type_map, schema_rules):
    candidate_id = int(candidate_id)
    query_id = int(query_id)

    for triple in subgraph:
        if len(triple) != 3:
            continue
        h_id, r_id, t_id = int(triple[0]), int(triple[1]), int(triple[2])
        if h_id != candidate_id or t_id != query_id:
            continue

        r_name = normalize_text(id2relation[r_id])
        if r_name != "indication":
            continue

        h_name = normalize_text(id2entity[h_id])
        t_name = normalize_text(id2entity[t_id])
        h_type = resolve_type(h_name, type_map, fallback_type_map)
        t_type = resolve_type(t_name, type_map, fallback_type_map)

        if schema_allows(r_name, h_type, t_type, schema_rules):
            return True

    return False


def has_valid_mechanism_path(candidate_id, query_id, directed_adj, valid_path_sequences, max_depth=3, max_paths=50):
    candidate_id = int(candidate_id)
    query_id = int(query_id)

    queue = deque()
    queue.append((candidate_id, [], {candidate_id}))
    found = False
    found_examples = []

    while queue and len(found_examples) < max_paths:
        cur, rel_seq, visited = queue.popleft()

        if cur == query_id and len(rel_seq) > 0:
            seq_tuple = tuple(rel_seq)
            if seq_tuple in valid_path_sequences:
                found = True
                found_examples.append(seq_tuple)
            continue

        if len(rel_seq) >= max_depth:
            continue

        for r_name, nxt in directed_adj.get(cur, []):
            if nxt in visited:
                continue
            queue.append((nxt, rel_seq + [r_name], visited | {nxt}))

    return found, found_examples[:3]


def priority_of_support(support_type):
    if support_type == "direct":
        return 3
    if support_type == "mechanism":
        return 2
    return 1


def build_md_report(report, out_path: Path):
    lines = []
    lines.append("# Day 4 — Ontology Candidate Build")
    lines.append("")
    lines.append("## 1. Goal")
    lines.append("Build the ontology-only candidate artifact using direct valid task edges and valid mechanism paths.")
    lines.append("")
    lines.append("## 2. Inputs")
    lines.append(f"- input_candidates: `{report['inputs']['input_candidates']}`")
    lines.append(f"- input_evidence: `{report['inputs']['input_evidence']}`")
    lines.append(f"- type_map_tsv: `{report['inputs']['type_map_tsv']}`")
    lines.append(f"- schema_rules_json: `{report['inputs']['schema_rules_json']}`")
    lines.append(f"- path_templates_yaml: `{report['inputs']['path_templates_yaml']}`")
    lines.append("")
    lines.append("## 3. Output")
    lines.append(f"- ontology_candidate_artifact: `{report['outputs']['ontology_candidate_artifact']}`")
    lines.append(f"- ontology_filter_report: `{report['outputs']['ontology_filter_report']}`")
    lines.append("")
    lines.append("## 4. Summary")
    for k in [
        "total_queries",
        "total_candidates_before",
        "total_candidates_after",
        "removed_unsupported_candidates",
        "candidates_kept_by_direct_support",
        "candidates_kept_by_mechanism_support",
        "queries_with_any_direct_support",
        "queries_with_any_mechanism_support",
        "fallback_queries",
        "empty_queries_before_fallback",
        "gold_in_ontology_candidates",
        "top1_changed_queries",
        "top5_changed_queries",
    ]:
        lines.append(f"- {k}: {report[k]}")
    lines.append("")
    lines.append("## 5. Sample before/after")
    for item in report["sample_before_after"]:
        lines.append(f"### Query: {item['query_entity']}")
        lines.append(f"- before_top5: {item['before_top5']}")
        lines.append(f"- after_top5: {item['after_top5']}")
        lines.append(f"- support_labels_top5_after: {item['support_labels_top5_after']}")
        lines.append(f"- fallback_used: {item['fallback_used']}")
        lines.append("")
    if not report["sample_before_after"]:
        lines.append("- no samples")
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_candidates",
        default="dataset/setting_a/18_ontology_only/valid_top20_type_filtered.json",
    )
    parser.add_argument(
        "--input_evidence",
        default="dataset/setting_a/12_backbone_ready_ranker_v2/valid.json",
    )
    parser.add_argument(
        "--id2entity_path",
        default="dataset/setting_a/12_backbone_ready_ranker_v2/id2entity.pkl",
    )
    parser.add_argument(
        "--id2relation_path",
        default="dataset/setting_a/12_backbone_ready_ranker_v2/id2relation.pkl",
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
        "--schema_rules_json",
        default="dataset/setting_b/01_annotations/schema_rules.json",
    )
    parser.add_argument(
        "--path_templates_yaml",
        default="dataset/setting_b/01_annotations/path_templates.yaml",
    )
    parser.add_argument(
        "--output_candidates",
        default="dataset/setting_a/18_ontology_only/valid_top20_ontology_only.json",
    )
    parser.add_argument(
        "--output_report_json",
        default="dataset/setting_a/18_ontology_only/ontology_filter_report.json",
    )
    parser.add_argument(
        "--output_report_md",
        default="reports/week9/day4_ontology_candidate_build.md",
    )
    parser.add_argument(
        "--max_path_len",
        type=int,
        default=3,
    )
    parser.add_argument(
        "--sample_limit",
        type=int,
        default=10,
    )
    args = parser.parse_args()

    input_candidates = Path(args.input_candidates)
    input_evidence = Path(args.input_evidence)
    id2entity_path = Path(args.id2entity_path)
    id2relation_path = Path(args.id2relation_path)
    type_map_tsv = Path(args.type_map_tsv)
    fallback_type_json = Path(args.fallback_type_json)
    schema_rules_json = Path(args.schema_rules_json)
    path_templates_yaml = Path(args.path_templates_yaml)
    output_candidates = Path(args.output_candidates)
    output_report_json = Path(args.output_report_json)
    output_report_md = Path(args.output_report_md)

    output_candidates.parent.mkdir(parents=True, exist_ok=True)
    output_report_json.parent.mkdir(parents=True, exist_ok=True)
    output_report_md.parent.mkdir(parents=True, exist_ok=True)

    candidate_rows = load_json(input_candidates)
    evidence_rows = load_json(input_evidence)
    id2entity = load_pickle(id2entity_path)
    id2relation = load_pickle(id2relation_path)
    type_map = load_type_map_tsv(type_map_tsv)
    fallback_type_map = load_fallback_type_json(fallback_type_json)
    schema_rules = normalize_schema_rules(load_json(schema_rules_json))
    valid_path_sequences = load_path_templates(path_templates_yaml)

    evidence_by_query = {}
    for row in evidence_rows:
        qid = row.get("query_entity_id")
        if qid is not None:
            evidence_by_query[int(qid)] = row

    output_rows = []

    total_queries = len(candidate_rows)
    total_candidates_before = 0
    total_candidates_after = 0
    removed_unsupported_candidates = 0
    candidates_kept_by_direct_support = 0
    candidates_kept_by_mechanism_support = 0
    queries_with_any_direct_support = 0
    queries_with_any_mechanism_support = 0
    fallback_queries = 0
    empty_queries_before_fallback = 0
    gold_in_ontology_candidates = 0
    top1_changed_queries = 0
    top5_changed_queries = 0

    sample_before_after = []

    for row in candidate_rows:
        new_row = deepcopy(row)
        cand_name_key, cand_id_key = get_candidate_keys(row)

        qid = int(row["query_entity_id"])
        query_entity = row.get("query_entity", f"query_{qid}")
        gold_entity = row.get("gold_entity")

        cand_names = row[cand_name_key]
        cand_ids = row[cand_id_key]
        total_candidates_before += len(cand_names)

        ev_row = evidence_by_query.get(qid)
        subgraph = ev_row.get("subgraph", []) if ev_row is not None else []

        directed_adj = build_directed_adj(
            subgraph=subgraph,
            id2entity=id2entity,
            id2relation=id2relation,
            type_map=type_map,
            fallback_type_map=fallback_type_map,
            schema_rules=schema_rules,
        )

        scored_candidates = []
        any_direct_for_query = False
        any_mech_for_query = False

        for idx, (cand_name, cand_id) in enumerate(zip(cand_names, cand_ids)):
            direct_ok = has_direct_valid_indication_edge(
                candidate_id=cand_id,
                query_id=qid,
                subgraph=subgraph,
                id2entity=id2entity,
                id2relation=id2relation,
                type_map=type_map,
                fallback_type_map=fallback_type_map,
                schema_rules=schema_rules,
            )

            mech_ok, mech_examples = has_valid_mechanism_path(
                candidate_id=cand_id,
                query_id=qid,
                directed_adj=directed_adj,
                valid_path_sequences=valid_path_sequences,
                max_depth=args.max_path_len,
                max_paths=50,
            )

            if direct_ok:
                support_type = "direct"
                any_direct_for_query = True
                candidates_kept_by_direct_support += 1
            elif mech_ok:
                support_type = "mechanism"
                any_mech_for_query = True
                candidates_kept_by_mechanism_support += 1
            else:
                support_type = "unsupported"

            scored_candidates.append({
                "name": cand_name,
                "id": cand_id,
                "orig_idx": idx,
                "support_type": support_type,
                "mechanism_examples": [" -> ".join(x) for x in mech_examples],
            })

        if any_direct_for_query:
            queries_with_any_direct_support += 1
        if any_mech_for_query:
            queries_with_any_mechanism_support += 1

        kept = [x for x in scored_candidates if x["support_type"] in {"direct", "mechanism"}]
        removed_unsupported_candidates += sum(1 for x in scored_candidates if x["support_type"] == "unsupported")

        # sort kept by support priority, then original order
        kept = sorted(
            kept,
            key=lambda x: (-priority_of_support(x["support_type"]), x["orig_idx"])
        )

        fallback_used = False
        if len(kept) == 0:
            empty_queries_before_fallback += 1
            fallback_queries += 1
            fallback_used = True
            kept = sorted(scored_candidates, key=lambda x: x["orig_idx"])

        out_names = [x["name"] for x in kept]
        out_ids = [x["id"] for x in kept]
        out_support = [x["support_type"] for x in kept]

        total_candidates_after += len(out_names)

        if gold_entity in set(out_names):
            gold_in_ontology_candidates += 1
            gold_rank = out_names.index(gold_entity) + 1
        else:
            gold_rank = None

        before_top5 = cand_names[:5]
        after_top5 = out_names[:5]

        if cand_names[:1] != out_names[:1]:
            top1_changed_queries += 1
        if before_top5 != after_top5:
            top5_changed_queries += 1

        new_row[cand_name_key] = out_names
        new_row[cand_id_key] = out_ids

        new_row["candidate_support_types"] = out_support
        new_row["ontology_filter_applied"] = True
        new_row["ontology_filter_mode"] = "keep_direct_or_mechanism_else_fallback"
        new_row["ontology_fallback_used"] = fallback_used
        new_row["num_candidates_before_ontology_filter"] = len(cand_names)
        new_row["num_candidates_after_ontology_filter"] = len(out_names)
        new_row["num_candidates_removed_by_ontology_filter"] = len(cand_names) - len([x for x in kept if not fallback_used]) if not fallback_used else 0
        new_row["gold_in_topk_ontology"] = gold_rank is not None
        new_row["gold_rank_in_ontology_candidates"] = gold_rank

        output_rows.append(new_row)

        if len(sample_before_after) < args.sample_limit:
            sample_before_after.append({
                "query_entity": query_entity,
                "before_top5": before_top5,
                "after_top5": after_top5,
                "support_labels_top5_after": out_support[:5],
                "fallback_used": fallback_used,
            })

    report = {
        "day": 4,
        "title": "Ontology-only candidate build",
        "inputs": {
            "input_candidates": str(input_candidates),
            "input_evidence": str(input_evidence),
            "type_map_tsv": str(type_map_tsv),
            "schema_rules_json": str(schema_rules_json),
            "path_templates_yaml": str(path_templates_yaml),
        },
        "outputs": {
            "ontology_candidate_artifact": str(output_candidates),
            "ontology_filter_report": str(output_report_json),
        },
        "total_queries": total_queries,
        "total_candidates_before": total_candidates_before,
        "total_candidates_after": total_candidates_after,
        "removed_unsupported_candidates": removed_unsupported_candidates,
        "candidates_kept_by_direct_support": candidates_kept_by_direct_support,
        "candidates_kept_by_mechanism_support": candidates_kept_by_mechanism_support,
        "queries_with_any_direct_support": queries_with_any_direct_support,
        "queries_with_any_mechanism_support": queries_with_any_mechanism_support,
        "fallback_queries": fallback_queries,
        "empty_queries_before_fallback": empty_queries_before_fallback,
        "gold_in_ontology_candidates": gold_in_ontology_candidates,
        "top1_changed_queries": top1_changed_queries,
        "top5_changed_queries": top5_changed_queries,
        "valid_mechanism_templates_loaded": len(valid_path_sequences),
        "sample_before_after": sample_before_after,
    }

    save_json(output_rows, output_candidates)
    save_json(report, output_report_json)
    build_md_report(report, output_report_md)

    print(f"Saved ontology candidates: {output_candidates}")
    print(f"Saved ontology report:     {output_report_json}")
    print(f"Saved markdown report:    {output_report_md}")
    print("Summary:")
    print(f"  total_queries = {report['total_queries']}")
    print(f"  total_candidates_before = {report['total_candidates_before']}")
    print(f"  total_candidates_after = {report['total_candidates_after']}")
    print(f"  removed_unsupported_candidates = {report['removed_unsupported_candidates']}")
    print(f"  candidates_kept_by_direct_support = {report['candidates_kept_by_direct_support']}")
    print(f"  candidates_kept_by_mechanism_support = {report['candidates_kept_by_mechanism_support']}")
    print(f"  queries_with_any_direct_support = {report['queries_with_any_direct_support']}")
    print(f"  queries_with_any_mechanism_support = {report['queries_with_any_mechanism_support']}")
    print(f"  fallback_queries = {report['fallback_queries']}")
    print(f"  empty_queries_before_fallback = {report['empty_queries_before_fallback']}")
    print(f"  gold_in_ontology_candidates = {report['gold_in_ontology_candidates']}")
    print(f"  top1_changed_queries = {report['top1_changed_queries']}")
    print(f"  top5_changed_queries = {report['top5_changed_queries']}")


if __name__ == "__main__":
    main()