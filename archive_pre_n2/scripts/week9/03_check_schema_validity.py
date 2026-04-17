import argparse
import csv
import json
import pickle
from collections import Counter, defaultdict, deque
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
        return main_type_map[entity_name], "type_map.tsv"
    if entity_name in fallback_type_map:
        return fallback_type_map[entity_name], "entity_name_to_type.json"
    return "UNKNOWN", "missing"


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
    """
    Support both:
    1) simple format:
       "indication": ["Drug", "Disease"]
    2) richer dict format:
       "indication": {"head_types": [...], "tail_types": [...]}
    """
    normalized = {}

    for rel, obj in raw_rules.items():
        rel = normalize_text(rel)

        # week3 canonical simple format
        if isinstance(obj, list) and len(obj) == 2:
            normalized[rel] = {
                "head_types": {normalize_text(obj[0])},
                "tail_types": {normalize_text(obj[1])},
            }
            continue

        # richer dict fallback
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

        # unknown format
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
        return False, "missing_relation_rule"

    rule = schema_rules[relation_name]
    allowed_heads = rule.get("head_types", set())
    allowed_tails = rule.get("tail_types", set())

    if not allowed_heads or not allowed_tails:
        return False, "incomplete_relation_rule"

    if head_type not in allowed_heads:
        return False, "invalid_head_type"
    if tail_type not in allowed_tails:
        return False, "invalid_tail_type"

    return True, "ok"


def load_path_templates(path: Path):
    """
    Support week3 canonical YAML:
    valid_path_templates:
      - name: ...
        path:
          - [Drug, target, Protein_or_Gene]
          - [Protein_or_Gene, associated_with, Disease]

    invalid_for_treatment_explanation:
      - [Drug, contraindication, Disease]
    """
    with path.open("r", encoding="utf-8") as f:
        obj = yaml.safe_load(f)

    valid_sequences = set()
    invalid_single_relations = set()

    # canonical valid templates
    for item in obj.get("valid_path_templates", []) if isinstance(obj, dict) else []:
        path = item.get("path", [])
        seq = []
        ok = True
        for step in path:
            # step expected: [head_type, relation, tail_type]
            if not isinstance(step, list) or len(step) != 3:
                ok = False
                break
            seq.append(normalize_text(step[1]))
        if ok and seq:
            valid_sequences.add(tuple(seq))

    # canonical invalid explanation relations
    for step in obj.get("invalid_for_treatment_explanation", []) if isinstance(obj, dict) else []:
        # expected [head_type, relation, tail_type]
        if isinstance(step, list) and len(step) == 3:
            invalid_single_relations.add(normalize_text(step[1]))

    return valid_sequences, invalid_single_relations


def build_adjacency(subgraph):
    adj = defaultdict(list)
    undirected = defaultdict(list)

    for h, r, t in subgraph:
        h, r, t = int(h), int(r), int(t)
        adj[h].append((r, t))

        # undirected search to avoid orientation mismatch in subgraph construction
        undirected[h].append((r, t))
        undirected[t].append((r, h))

    return adj, undirected


def bfs_relation_sequences_undirected(subgraph, start_node, target_node, max_depth=3, max_paths=20):
    """
    Return relation sequences on simple paths between candidate and query
    using undirected traversal for connectivity, but preserving relation ids.
    """
    start_node = int(start_node)
    target_node = int(target_node)
    _, undirected = build_adjacency(subgraph)

    results = []
    queue = deque()
    queue.append((start_node, [], {start_node}))

    while queue and len(results) < max_paths:
        cur, rel_seq, visited = queue.popleft()

        if cur == target_node and len(rel_seq) > 0:
            results.append(tuple(rel_seq))
            continue

        if len(rel_seq) >= max_depth:
            continue

        for rel_id, nxt in undirected.get(cur, []):
            if nxt in visited:
                continue
            queue.append((nxt, rel_seq + [rel_id], visited | {nxt}))

    return results


def build_md_report(report, out_path: Path):
    lines = []
    lines.append("# Day 3 — Schema Validity")
    lines.append("")
    lines.append("## 1. Goal")
    lines.append("Check schema validity for candidate / path / evidence on the valid split.")
    lines.append("")
    lines.append("## 2. Candidate validity summary")
    cand = report["candidate_validity"]
    lines.append(f"- total_queries_checked: {cand['total_queries_checked']}")
    lines.append(f"- total_candidates_checked: {cand['total_candidates_checked']}")
    lines.append(f"- candidate_type_violations: {cand['candidate_type_violations']}")
    lines.append(f"- unknown_candidate_types: {cand['unknown_candidate_types']}")
    lines.append("")
    lines.append("## 3. Evidence triple validity summary")
    ev = report["evidence_validity"]
    lines.append(f"- total_queries_checked: {ev['total_queries_checked']}")
    lines.append(f"- total_evidence_triples_checked: {ev['total_evidence_triples_checked']}")
    lines.append(f"- valid_evidence_triples: {ev['valid_evidence_triples']}")
    lines.append(f"- invalid_evidence_triples: {ev['invalid_evidence_triples']}")
    lines.append(f"- missing_relation_rules: {ev['missing_relation_rules']}")
    lines.append(f"- incomplete_relation_rules: {ev['incomplete_relation_rules']}")
    lines.append("")
    lines.append("### Top invalid evidence patterns")
    for k, v in ev["top_invalid_evidence_patterns"]:
        lines.append(f"- {k}: {v}")
    if not ev["top_invalid_evidence_patterns"]:
        lines.append("- none")
    lines.append("")
    lines.append("## 4. Path validity summary")
    pv = report["path_validity"]
    lines.append(f"- valid_mechanism_templates_loaded: {pv['valid_mechanism_templates_loaded']}")
    lines.append(f"- invalid_explanation_relations_loaded: {pv['invalid_explanation_relations_loaded']}")
    lines.append(f"- total_path_sequences_checked: {pv['total_path_sequences_checked']}")
    lines.append(f"- valid_mechanism_path_sequences: {pv['valid_mechanism_path_sequences']}")
    lines.append(f"- direct_task_edge_sequences: {pv['direct_task_edge_sequences']}")
    lines.append(f"- blocked_explanation_sequences: {pv['blocked_explanation_sequences']}")
    lines.append(f"- unsupported_path_sequences: {pv['unsupported_path_sequences']}")
    lines.append(f"- queries_with_no_candidate_to_query_path: {pv['queries_with_no_candidate_to_query_path']}")
    lines.append("")
    lines.append("### Top unsupported path patterns")
    for k, v in pv["top_unsupported_path_patterns"]:
        lines.append(f"- {k}: {v}")
    if not pv["top_unsupported_path_patterns"]:
        lines.append("- none")
    lines.append("")
    lines.append("### Sample unsupported paths")
    for x in pv["sample_unsupported_paths"]:
        lines.append(
            f"- query={x['query_entity']} | candidate={x['candidate_name']} | path={x['relation_sequence']}"
        )
    if not pv["sample_unsupported_paths"]:
        lines.append("- none")
    lines.append("")
    lines.append("## 5. Interpretation")
    lines.append("- Direct indication edge is counted separately from mechanism paths.")
    lines.append("- Contraindication-style relations are blocked as treatment explanation evidence.")
    lines.append("- Unsupported path sequences are not necessarily schema-invalid triples; they are template-unapproved explanation paths.")
    lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--candidate_artifact",
        default="dataset/setting_a/18_ontology_only/valid_top20_type_filtered.json",
    )
    parser.add_argument(
        "--evidence_artifact",
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
        "--output_report_json",
        default="dataset/setting_a/18_ontology_only/schema_validity_report.json",
    )
    parser.add_argument(
        "--output_report_md",
        default="reports/week9/day3_schema_validity.md",
    )
    parser.add_argument(
        "--max_path_len",
        type=int,
        default=3,
    )
    parser.add_argument(
        "--topn_candidates_for_path_check",
        type=int,
        default=5,
    )
    parser.add_argument(
        "--sample_limit",
        type=int,
        default=10,
    )
    args = parser.parse_args()

    candidate_rows = load_json(Path(args.candidate_artifact))
    evidence_rows = load_json(Path(args.evidence_artifact))
    id2entity = load_pickle(Path(args.id2entity_path))
    id2relation = load_pickle(Path(args.id2relation_path))
    main_type_map = load_type_map_tsv(Path(args.type_map_tsv))
    fallback_type_map = load_fallback_type_json(Path(args.fallback_type_json))
    schema_rules = normalize_schema_rules(load_json(Path(args.schema_rules_json)))
    valid_path_sequences, blocked_relations = load_path_templates(Path(args.path_templates_yaml))

    evidence_by_query = {}
    for row in evidence_rows:
        qid = row.get("query_entity_id")
        if qid is not None:
            evidence_by_query[int(qid)] = row

    lookup_source_counter = Counter()

    # candidate validity
    cand_total = 0
    cand_violations = 0
    cand_unknown = 0

    # evidence validity
    ev_total_triples = 0
    ev_valid_triples = 0
    ev_invalid_triples = 0
    ev_missing_relation_rules = 0
    ev_incomplete_relation_rules = 0
    invalid_evidence_pattern_counter = Counter()
    sample_invalid_evidence = []

    # path validity
    path_total_checked = 0
    valid_mechanism_paths = 0
    direct_task_edge_paths = 0
    blocked_explanation_paths = 0
    unsupported_paths = 0
    queries_with_no_path = 0
    unsupported_path_counter = Counter()
    sample_unsupported_paths = []

    for cand_row in candidate_rows:
        cand_name_key, cand_id_key = get_candidate_keys(cand_row)
        qid = int(cand_row["query_entity_id"])
        query_entity = cand_row.get("query_entity", f"query_{qid}")
        cand_names = cand_row[cand_name_key]
        cand_ids = cand_row[cand_id_key]

        # candidate validity
        for name in cand_names:
            cand_total += 1
            typ, src = resolve_type(name, main_type_map, fallback_type_map)
            lookup_source_counter[src] += 1
            if typ == "UNKNOWN":
                cand_unknown += 1
            if typ != "Drug":
                cand_violations += 1

        ev_row = evidence_by_query.get(qid)
        if ev_row is None:
            continue

        subgraph = ev_row.get("subgraph", [])

        # evidence triple validity
        for triple in subgraph:
            if len(triple) != 3:
                continue
            h_id, r_id, t_id = int(triple[0]), int(triple[1]), int(triple[2])

            h_name = normalize_text(id2entity[h_id])
            r_name = normalize_text(id2relation[r_id])
            t_name = normalize_text(id2entity[t_id])

            h_type, src_h = resolve_type(h_name, main_type_map, fallback_type_map)
            t_type, src_t = resolve_type(t_name, main_type_map, fallback_type_map)
            lookup_source_counter[src_h] += 1
            lookup_source_counter[src_t] += 1

            ev_total_triples += 1
            allowed, reason = schema_allows(r_name, h_type, t_type, schema_rules)
            if allowed:
                ev_valid_triples += 1
            else:
                ev_invalid_triples += 1
                if reason == "missing_relation_rule":
                    ev_missing_relation_rules += 1
                elif reason == "incomplete_relation_rule":
                    ev_incomplete_relation_rules += 1

                pattern = f"{h_type} -[{r_name}]-> {t_type}"
                invalid_evidence_pattern_counter[pattern] += 1

                if len(sample_invalid_evidence) < args.sample_limit:
                    sample_invalid_evidence.append({
                        "query_entity": query_entity,
                        "head_name": h_name,
                        "relation_name": r_name,
                        "tail_name": t_name,
                        "head_type": h_type,
                        "tail_type": t_type,
                        "reason": reason,
                    })

        # path validity
        top_candidate_ids = cand_ids[: args.topn_candidates_for_path_check]
        any_path_for_query = False

        for cid in top_candidate_ids:
            rel_seq_ids_list = bfs_relation_sequences_undirected(
                subgraph=subgraph,
                start_node=int(cid),
                target_node=qid,
                max_depth=args.max_path_len,
                max_paths=20,
            )

            candidate_name = normalize_text(id2entity[int(cid)])

            if rel_seq_ids_list:
                any_path_for_query = True

            for rel_seq_ids in rel_seq_ids_list:
                rel_seq_names = tuple(normalize_text(id2relation[int(x)]) for x in rel_seq_ids)
                path_total_checked += 1

                # direct task edge: allow but classify separately
                if rel_seq_names == ("indication",):
                    direct_task_edge_paths += 1
                    continue

                # explicit blocked explanation relation
                if any(rel in blocked_relations for rel in rel_seq_names):
                    blocked_explanation_paths += 1
                    continue

                # valid mechanism template
                if rel_seq_names in valid_path_sequences:
                    valid_mechanism_paths += 1
                    continue

                # otherwise unsupported
                unsupported_paths += 1
                unsupported_path_counter[" -> ".join(rel_seq_names)] += 1
                if len(sample_unsupported_paths) < args.sample_limit:
                    sample_unsupported_paths.append({
                        "query_entity": query_entity,
                        "candidate_name": candidate_name,
                        "relation_sequence": " -> ".join(rel_seq_names),
                    })

        if not any_path_for_query:
            queries_with_no_path += 1

    report = {
        "day": 3,
        "title": "Schema validity check",
        "inputs": {
            "candidate_artifact": args.candidate_artifact,
            "evidence_artifact": args.evidence_artifact,
            "type_map_tsv": args.type_map_tsv,
            "fallback_type_json": args.fallback_type_json,
            "schema_rules_json": args.schema_rules_json,
            "path_templates_yaml": args.path_templates_yaml,
            "id2entity_path": args.id2entity_path,
            "id2relation_path": args.id2relation_path,
        },
        "candidate_validity": {
            "total_queries_checked": len(candidate_rows),
            "total_candidates_checked": cand_total,
            "candidate_type_violations": cand_violations,
            "unknown_candidate_types": cand_unknown,
        },
        "evidence_validity": {
            "total_queries_checked": len(candidate_rows),
            "total_evidence_triples_checked": ev_total_triples,
            "valid_evidence_triples": ev_valid_triples,
            "invalid_evidence_triples": ev_invalid_triples,
            "missing_relation_rules": ev_missing_relation_rules,
            "incomplete_relation_rules": ev_incomplete_relation_rules,
            "top_invalid_evidence_patterns": invalid_evidence_pattern_counter.most_common(10),
            "sample_invalid_evidence": sample_invalid_evidence,
        },
        "path_validity": {
            "valid_mechanism_templates_loaded": len(valid_path_sequences),
            "invalid_explanation_relations_loaded": len(blocked_relations),
            "total_path_sequences_checked": path_total_checked,
            "valid_mechanism_path_sequences": valid_mechanism_paths,
            "direct_task_edge_sequences": direct_task_edge_paths,
            "blocked_explanation_sequences": blocked_explanation_paths,
            "unsupported_path_sequences": unsupported_paths,
            "queries_with_no_candidate_to_query_path": queries_with_no_path,
            "top_unsupported_path_patterns": unsupported_path_counter.most_common(10),
            "sample_unsupported_paths": sample_unsupported_paths,
        },
        "lookup_source_breakdown": dict(lookup_source_counter),
    }

    save_json(report, Path(args.output_report_json))
    build_md_report(report, Path(args.output_report_md))

    print(f"Saved report json: {args.output_report_json}")
    print(f"Saved report md:   {args.output_report_md}")
    print("Summary:")
    print(f"  candidate_type_violations = {report['candidate_validity']['candidate_type_violations']}")
    print(f"  unknown_candidate_types = {report['candidate_validity']['unknown_candidate_types']}")
    print(f"  valid_evidence_triples = {report['evidence_validity']['valid_evidence_triples']}")
    print(f"  invalid_evidence_triples = {report['evidence_validity']['invalid_evidence_triples']}")
    print(f"  missing_relation_rules = {report['evidence_validity']['missing_relation_rules']}")
    print(f"  incomplete_relation_rules = {report['evidence_validity']['incomplete_relation_rules']}")
    print(f"  valid_mechanism_templates_loaded = {report['path_validity']['valid_mechanism_templates_loaded']}")
    print(f"  invalid_explanation_relations_loaded = {report['path_validity']['invalid_explanation_relations_loaded']}")
    print(f"  total_path_sequences_checked = {report['path_validity']['total_path_sequences_checked']}")
    print(f"  valid_mechanism_path_sequences = {report['path_validity']['valid_mechanism_path_sequences']}")
    print(f"  direct_task_edge_sequences = {report['path_validity']['direct_task_edge_sequences']}")
    print(f"  blocked_explanation_sequences = {report['path_validity']['blocked_explanation_sequences']}")
    print(f"  unsupported_path_sequences = {report['path_validity']['unsupported_path_sequences']}")
    print(f"  queries_with_no_candidate_to_query_path = {report['path_validity']['queries_with_no_candidate_to_query_path']}")


if __name__ == "__main__":
    main()