# Week 27 Day 3  DRKG split + filtered graph

- Decision: `DAY3_DRKG_SPLIT_GRAPH_READY`
- Target relation: `DRUGBANK::treats::Compound:Disease`
- Task: `(? , DRUGBANK::treats, disease)`

## Split summary

- Train: `3968`
- Valid: `500`
- Test: `500`
- Candidate compounds: `1542`
- Query diseases: `1182`
- Coverage pass: `True`

## Graph summary

- Train enriched edges: `187962`
- Entities: `13918`
- Relations: `85`
- graph_num_rels: `85`
- Exact leak count: `0`

## Kept edges by family

- `compound_gene`: 44197
- `target_treats`: 3968
- `aux_compound_disease`: 14333
- `disease_gene`: 23235
- `gene_gene`: 102229

## Notes

- Full DRKG graph is not used blindly.
- Valid/test target DRUGBANK::treats triples are removed.
- Hetionet CtD/CpD auxiliary relations are not included by default in this Day 3 graph.
- Day 4 should run structure baselines using this filtered graph and fixed top-20 reviewer-safe protocol.
