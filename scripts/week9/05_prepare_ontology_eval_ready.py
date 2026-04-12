import argparse
import json
import pickle
import shutil
from copy import deepcopy
from pathlib import Path


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


def get_candidate_keys(row):
    if "candidate_entities" in row and "candidate_entity_ids" in row:
        return "candidate_entities", "candidate_entity_ids"
    if "rank_entities" in row and "rank_entities_id" in row:
        return "rank_entities", "rank_entities_id"
    raise KeyError(
        "Expected either candidate_entities/candidate_entity_ids "
        "or rank_entities/rank_entities_id."
    )


def add_prompt(raw, relation_questions_A_to_B, relation_questions_B_to_A, bkg=True):
    rel = raw["triple"][1]
    query_entity = raw["query_entity"]
    rank_entities = raw["rank_entities"]
    pred_type = raw["type"]

    answer_options = "(" + ", ".join([f"'{name}'" for name in rank_entities]) + ")"
    refer_parts = [f"'{query_entity}': [QUERY]"]
    for name in rank_entities:
        refer_parts.append(f"'{name}': [ENTITY]")
    refer_str = ", ".join(refer_parts)

    if pred_type == "predicted_tail":
        question_template = relation_questions_A_to_B.get(rel, "What is related to {}?")
    else:
        question_template = relation_questions_B_to_A.get(rel, "What is related to {}?")

    question = question_template.format(query_entity)

    if bkg:
        prompt = (
            "You are a biomedical scientist. "
            "The task is to predict the answer based on the given question, "
            "and you only need to answer one entity. "
            f"The answer must be in {answer_options}.\n"
            f"You can refer to the entity embeddings: {refer_str}.\n\n"
            f"Question: {question}\n"
            "Answer: "
        )
    else:
        prompt = (
            "You are an excellent linguist. "
            "The task is to predict the answer based on the given question, "
            "and you only need to answer one entity. "
            f"The answer must be in {answer_options}.\n"
            f"You can refer to the entity embeddings: {refer_str}.\n\n"
            f"Question: {question}\n"
            "Answer: "
        )

    if pred_type == "predicted_tail":
        answer = raw["triple"][2]
    else:
        answer = raw["triple"][0]

    raw["input"] = prompt
    raw["output"] = answer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ontology_candidates",
        default="dataset/setting_a/18_ontology_only/valid_top20_ontology_only.json",
    )
    parser.add_argument(
        "--base_package_dir",
        default="dataset/setting_a/12_backbone_ready_ranker_v2",
    )
    parser.add_argument(
        "--head_pred_lex",
        default="dataset/setting_a/05_prompt_subgraph_subset/head_prediction_lexicon.json",
    )
    parser.add_argument(
        "--tail_pred_lex",
        default="dataset/setting_a/05_prompt_subgraph_subset/tail_prediction_lexicon.json",
    )
    parser.add_argument(
        "--output_package_dir",
        default="dataset/setting_a/18_ontology_only_eval_ready",
    )
    args = parser.parse_args()

    ontology_candidates = load_json(Path(args.ontology_candidates))
    base_package_dir = Path(args.base_package_dir)
    output_package_dir = Path(args.output_package_dir)
    output_package_dir.mkdir(parents=True, exist_ok=True)

    head_lex = load_json(Path(args.head_pred_lex))
    tail_lex = load_json(Path(args.tail_pred_lex))

    base_valid = load_json(base_package_dir / "valid.json")
    base_train = base_package_dir / "train.json"
    base_test = base_package_dir / "test.json"

    # copy train/test and maps unchanged
    for fn in [
        "train.json",
        "test.json",
        "entity2id.pkl",
        "id2entity.pkl",
        "relation2id.pkl",
        "id2relation.pkl",
    ]:
        src = base_package_dir / fn
        dst = output_package_dir / fn
        shutil.copy2(src, dst)

    # map ontology candidate row by query_entity_id
    ont_by_qid = {}
    for row in ontology_candidates:
        ont_by_qid[int(row["query_entity_id"])] = row

    rebuilt_valid = []
    num_missing_match = 0
    num_gold_in_topk_ontology = 0
    num_fallback = 0

    for row in base_valid:
        qid = int(row["query_entity_id"])
        new_row = deepcopy(row)

        ont_row = ont_by_qid.get(qid)
        if ont_row is None:
            num_missing_match += 1
            rebuilt_valid.append(new_row)
            continue

        cand_names_key, cand_ids_key = get_candidate_keys(ont_row)
        cand_names = ont_row[cand_names_key]
        cand_ids = ont_row[cand_ids_key]

        new_row["rank_entities"] = cand_names
        new_row["rank_entities_id"] = cand_ids

        gold_entity = ont_row.get("gold_entity", new_row.get("gold_entity", new_row["output"]))
        gold_rank = ont_row.get("gold_rank_in_ontology_candidates", None)
        gold_in_topk = bool(ont_row.get("gold_in_topk_ontology", False))

        if gold_in_topk:
            num_gold_in_topk_ontology += 1

        if ont_row.get("ontology_fallback_used", False):
            num_fallback += 1

        # infer.py expects rank
        if gold_rank is None:
            new_row["rank"] = len(cand_names) + 1
        else:
            new_row["rank"] = int(gold_rank)

        # carry traceable week9 fields
        new_row["candidate_support_types"] = ont_row.get("candidate_support_types", [])
        new_row["ontology_filter_applied"] = ont_row.get("ontology_filter_applied", True)
        new_row["ontology_filter_mode"] = ont_row.get("ontology_filter_mode", "ontology_only")
        new_row["ontology_fallback_used"] = ont_row.get("ontology_fallback_used", False)
        new_row["gold_in_topk_ontology"] = gold_in_topk
        new_row["gold_rank_in_ontology_candidates"] = gold_rank

        # rebuild prompt with ontology candidates
        add_prompt(
            new_row,
            relation_questions_A_to_B=tail_lex,
            relation_questions_B_to_A=head_lex,
            bkg=True,
        )

        rebuilt_valid.append(new_row)

    save_json(rebuilt_valid, output_package_dir / "valid.json")

    manifest = {
        "base_package_dir": str(base_package_dir),
        "ontology_candidates": args.ontology_candidates,
        "output_package_dir": str(output_package_dir),
        "num_valid_rows": len(rebuilt_valid),
        "num_missing_match": num_missing_match,
        "num_gold_in_topk_ontology": num_gold_in_topk_ontology,
        "num_fallback_queries": num_fallback,
    }
    save_json(manifest, output_package_dir / "prep_manifest.json")

    print(f"Saved: {output_package_dir / 'valid.json'}")
    print(f"Saved: {output_package_dir / 'prep_manifest.json'}")
    print("Summary:")
    print("  num_valid_rows =", len(rebuilt_valid))
    print("  num_missing_match =", num_missing_match)
    print("  num_gold_in_topk_ontology =", num_gold_in_topk_ontology)
    print("  num_fallback_queries =", num_fallback)


if __name__ == "__main__":
    main()