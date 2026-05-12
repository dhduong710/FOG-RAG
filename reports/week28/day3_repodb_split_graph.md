# Week 28 Day 3  repoDB split and evidence graph

- Decision: `DAY3_REPODB_SPLIT_GRAPH_READY`
- Dataset: `repoDB`
- Task: `(?, repoDB_approved_indication, disease)`

## Split summary

- Train: `5677`
- Valid: `500`
- Test: `500`
- Candidate compounds: `1519`
- Query diseases: `1229`
- Coverage pass: `True`

## Graph summary

- Train enriched edges: `90804`
- Entities: `8818`
- Relations: `63`
- graph_num_rels: `63`
- Exact leak count: `0`

## Kept edges by family

- `target_approved`: 5677
- `failed_diagnostic`: 3222
- `compound_gene`: 39017
- `gene_gene`: 42888

## Interpretation

- repoDB diseases are retained as local UMLS disease nodes.
- DRKG evidence is reused mainly through mapped DrugBank compounds and compound-gene/gene-gene evidence.
- Failed-like repoDB pairs are kept as diagnostic evidence after conflict removal.
- Valid/test approved target triples are removed from the train graph.

## Next step

Day 4 should run structure baselines on this graph and export fixed top-20 candidate rows.
