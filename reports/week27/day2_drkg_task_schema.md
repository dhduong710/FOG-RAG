# Week 27 Day 2  DRKG task schema freeze

- Decision: `DAY2_DRKG_TASK_SCHEMA_READY`
- Target relation: `DRUGBANK::treats::Compound:Disease`
- Task: `(?, DRUGBANK::treats, disease)`
- Candidate universe policy: `train_target_relation_compound_heads`

## Target relation feasibility

- Unique target edges: `4968`
- Unique compounds: `1542`
- Unique diseases: `1182`
- Singleton compounds: `753`
- Singleton diseases: `450`

## Recommended split

- Decision: `SPLIT_SIZE_FEASIBLE`
- Train: `3968`
- Valid: `500`
- Test: `500`

## Relation semantics

- Data source: `DRUGBANK`
- Claim level: `DrugBank treatment-relation prediction within DRKG; not clinical validation.`
- Wording: `treatment-like drugdisease prediction / DrugBank treats relation`

## DRKG large-graph policy

- `do_not_use_full_graph_blindly`: True
- `reason`: DRKG has 5.87M triples; full graph is too large/noisy for fast baseline and subgraph retrieval.
- `target_relation_handling`: Include only train target DRUGBANK::treats edges; remove valid/test target edges.
- `candidate_universe`: Compounds from train target heads.
- `initial_train_graph_relation_families`: ['target train DRUGBANK::treats edges', 'Compound-Gene relations', 'Disease-Gene relations', 'Gene-Gene relations', 'selected auxiliary Compound-Disease evidence relations with shortcut penalties']
- `degree_cap_policy_day3`: {'cap_high_degree_genes': True, 'max_edges_target_for_graph': 'Prefer <= 1.5M edges for initial DRKG Setting E graph.', 'keep_all_target_train_edges': True, 'keep_all_candidate_query_target_nodes': True, 'apply_relation_and_node_degree_filtering': True}
- `leakage_policy`: Exact valid/test target triples must be removed from train graph and subgraphs.

## Auxiliary CompoundDisease relations

| Relation | Count | Source | Role | Caution |
|---|---:|---|---|---|
| `GNBR::T::Compound:Disease` | 54020 | `GNBR` | `direct_cd_auxiliary` | `very_large_relation_use_degree_cap_or_penalty` |
| `GNBR::Sa::Compound:Disease` | 16923 | `GNBR` | `direct_cd_auxiliary` | `` |
| `GNBR::Pa::Compound:Disease` | 2619 | `GNBR` | `direct_cd_auxiliary` | `` |
| `GNBR::C::Compound:Disease` | 1739 | `GNBR` | `direct_cd_auxiliary` | `` |
| `GNBR::J::Compound:Disease` | 1020 | `GNBR` | `direct_cd_auxiliary` | `` |
| `GNBR::Pr::Compound:Disease` | 966 | `GNBR` | `direct_cd_auxiliary` | `` |
| `Hetionet::CtD::Compound:Disease` | 755 | `Hetionet` | `direct_cd_auxiliary` | `overlaps_with_week26_hetionet_source` |
| `GNBR::Mp::Compound:Disease` | 495 | `GNBR` | `direct_cd_auxiliary` | `` |
| `Hetionet::CpD::Compound:Disease` | 390 | `Hetionet` | `direct_cd_auxiliary` | `overlaps_with_week26_hetionet_source` |

## Day 3 next step

Build the actual coverage-safe split and train graph using this frozen protocol.
The train graph should not blindly include all 5.87M DRKG triples; use relation filtering and degree caps.
