# Setting A Graph Lock

## Goal
Lock the final Week-2 reproduction choice for the Setting A train graph before moving to Week 3.

## Benchmark lock
- Raw indication triples extracted from PrimeKG: `9388`
- Fixed split:
  - train: `8388`
  - valid: `500`
  - test: `500`
- Split seed: `2025`
- Coverage rule:
  - all drugs in valid/test must appear in train
  - all diseases in valid/test must appear in train

## Canonical internal relation names
The project uses the following canonical internal relation names:
- `indication`
- `target`
- `associated_with`
- `ppi`

### Alias handling
Accepted raw aliases are normalized into canonical internal names:
- `associated with` -> `associated_with`
- `associated_with` -> `associated_with`

## Setting A train graph construction
The final Setting A train graph is built from:
- train indication triples
- target edges
- associated_with edges
- ppi edges

### Direction convention
- `target`: `drug -> gene/protein`
- `associated_with`: `gene/protein -> disease`
- `ppi`: `gene/protein <-> gene/protein` conceptually symmetric

## PPI counting convention
PrimeKG stores symmetric PPI edges in both directions.

Audit result:
- filtered directed PPI edges: `104328`
- filtered unordered unique PPI pairs: `52164`
- reverse-pair count: `52164`

Therefore, the final internal counting convention is:

- **PPI is stored as one unordered collapsed edge per gene/protein pair**

## Final hub cap choice
Final selected value:
- `max_gene_degree = 1000`

Reason:
- it gives a train graph size close to the DrKGC paper statistics
- it avoids the clear double-counting problem from directed PPI storage
- it preserves a broad but still bounded biomedical support graph

## Final Week-2 graph stats
Using:
- unordered-collapsed PPI
- `max_gene_degree = 1000`

the final graph stats are:
- `num_train_indication_triples = 8388`
- `num_target_triples = 6131`
- `num_associated_with_triples = 48271`
- `num_ppi_triples = 73561`
- `num_support_triples_only = 127963`
- `num_total_enriched_triples = 136351`
- `num_entities = 10453`
- `num_drugs = 1801`
- `num_diseases = 1363`
- `num_gene_protein = 7289`
- `num_genes_removed_by_hub_cap = 48`

## Interpretation
The final graph is considered a valid Week-2 reproduction choice:
- relation schema is correct
- associated_with alias issue is fixed
- PPI double-counting is fixed
- graph size is reasonably close to paper-level scale

The entity count does not exactly match the paper and is treated as a difference in graph-construction/counting convention rather than a blocking issue at Week 2.

## Candidate-stage lock
The Week-2 candidate stage is currently a deterministic mock coarse ranker:
- candidate type: `drug`
- `K = 20`
- gold always included
- gold placed at rank 1
- deterministic negative selection from train-drug universe

This is a temporary Week-2 pipeline-locking choice, not a learned ranker.

## Prompt-subgraph clean-eval lock
The retrieval graph for prompt/subgraph preprocessing must be built from **train graph only**.

Reason:
- building retrieval graph from `train + valid` causes exact gold triple leakage in validation

Final Week-2 leakage audit:
- `valid exact leak count = 0`
- `test exact leak count = 0`

## Locked status
Setting A graph is now considered **locked for the end of Week 2**.
Any later changes must be treated as explicit experimental variants, not silent replacements.