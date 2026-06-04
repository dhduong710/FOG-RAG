# Type Map Report

## 1. Goal
Freeze a benchmark-relevant coarse type map for Setting B using the existing ontology JSON as the raw source.

## 2. Inputs
- raw ontology source: `dataset/setting_b/01_ontology/entity_name_to_type.json`
- relation rules: `dataset/setting_b/01_ontology/domain_range_rules.json`
- name type conflicts: `dataset/setting_b/01_ontology/name_type_conflicts.json`
- missing split entities: `dataset/setting_b/01_ontology/missing_split_entities.json`
- split dir: `dataset/setting_a/01_split`
- graph dir: `dataset/setting_a/02_graph`
- candidate dir: `dataset/setting_a/03_candidates`

## 3. Summary
- benchmark-relevant entity universe: 10453
- entities missing raw type in ontology JSON: 39
- override rows: 39
- valid/test candidate entities: 1801
- valid/test candidate entities typed as non-Drug: 0
- existing name_type_conflicts.json entries: 94
- existing missing_split_entities.json entries: 0

## 4. Final type counts
- Disease: 1363
- Drug: 1801
- Protein_or_Gene: 7289

## 5. Manual spot-check (20 samples)
- CXCR1 -> Protein_or_Gene (raw_json) context_agree:graph_rule:target:tail
- Pentobarbital -> Drug (raw_json) context_agree:valid_test_candidate
- UNC80 -> Protein_or_Gene (raw_json) context_agree:graph_rule:associated_with:head
- GBA -> Protein_or_Gene (raw_json) context_agree:graph_rule:target:tail
- Amphetamine -> Drug (raw_json) context_agree:valid_test_candidate
- UBE2E1 -> Protein_or_Gene (raw_json) context_agree:graph_rule:associated_with:head
- SYP -> Protein_or_Gene (raw_json) context_agree:graph_rule:associated_with:head
- PROP1 -> Protein_or_Gene (raw_json) context_agree:graph_rule:associated_with:head
- Piperaquine -> Drug (raw_json) context_agree:valid_test_candidate
- ATXN8OS -> Protein_or_Gene (raw_json) context_agree:graph_rule:associated_with:head
- RIOX2 -> Protein_or_Gene (raw_json) context_agree:graph_rule:associated_with:head
- Methadyl acetate -> Drug (raw_json) context_agree:valid_test_candidate
- CMTR2 -> Protein_or_Gene (raw_json) context_agree:graph_rule:associated_with:head
- SMAD5 -> Protein_or_Gene (raw_json) context_agree:graph_rule:associated_with:head
- H3C2 -> Protein_or_Gene (raw_json) context_agree:graph_rule:associated_with:head
- CLEC10A -> Protein_or_Gene (raw_json) context_agree:graph_rule:associated_with:head
- GRM2 -> Protein_or_Gene (raw_json) context_agree:graph_rule:associated_with:head
- SLC22A2 -> Protein_or_Gene (raw_json) context_agree:graph_rule:associated_with:head
- DDX60 -> Protein_or_Gene (raw_json) context_agree:graph_rule:associated_with:head
- cutaneous neuroendocrine carcinoma -> Disease (raw_json) context_agree:split_relation_tail

## 6. Notes
- `entity_name_to_type.json` is preserved as the raw ontology source.
- `type_map.tsv` is the frozen benchmark-relevant coarse type map for Setting B.
- Any task-critical conflicts are logged in `type_map_overrides.tsv` rather than changed silently.