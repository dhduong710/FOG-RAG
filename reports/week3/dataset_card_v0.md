# Dataset Card v0
## 1. Dataset name
PrimeKG-derived drug repurposing benchmark for FOG-RAG

## 2. Overview
This dataset card describes a PrimeKG-derived benchmark for contraindication-aware drug repurposing built on top of a DrKGC-compatible knowledge graph completion setup.

The benchmark is designed with two complementary evaluation settings:
- Setting A: DrKGC-compatible indication ranking for fair backbone comparison
- Setting B: extended contraindication-aware ranking with safety, constraint, and explanation analysis

## 3. Task definition
### Main task
Given an incomplete triple of the form:

(? , indication, disease)

predict and rank candidate drug entities.

This is a head-prediction / indication-ranking task.

### Extended task
In addition to ranking plausible indication drugs, the extended protocol analyzes:
- contraindication-aware safety
- ontology/schema validity
- explanation readiness

The benchmark does not claim clinical decision making. It is intended for research on safer biomedical KG completion and grounded drug repurposing support.

## 4. Query form
Each query is represented as an incomplete triple:

(? , indication, disease)

Operationally:
- query entity = disease
- target entity = drug
- prediction type = predicted_head

## 5. Data source
The benchmark is derived from PrimeKG relation subsets relevant to drug repurposing.

The current protocol uses:
- indication pairs for the main task
- contraindication pairs as auxiliary safety annotations
- graph enrichment relations for evidence structure:
  - target
  - associated_with
  - ppi

## 6. Setting A
Setting A is the fairness-oriented benchmark aligned as closely as possible with the DrKGC backbone protocol.

Purpose:
- preserve the original indication-ranking task
- support direct comparison against the DrKGC backbone
- avoid benchmark changes being mistaken for model improvements

Current Setting A status:
- fixed split already locked
- mock coarse candidates prepared
- prompt/subgraph preprocessing subset already tested

Metrics intended for Setting A:
- MRR
- Hits@1
- Hits@3
- Hits@10

## 7. Setting B
Setting B extends Setting A with contraindication-aware and ontology-aware analysis.

Setting B keeps the same main query/gold structure as Setting A, but adds:
- contraindication safety labels
- coarse entity type constraints
- schema/domain-range checks
- explanation-oriented path policy

Purpose:
- measure biomedical usefulness beyond ranking alone
- distinguish safe and unsafe ranked outputs
- support future grounded explanation analysis

## 8. Entity types
The current coarse type system is:

- Drug
- Disease
- Protein_or_Gene
- Pathway
- Anatomy_or_Phenotype
- Biological_Process
- Other

These coarse types are used for:
- candidate sanity checks
- schema/domain-range validation
- path template validation

## 9. Relation set
The current benchmark protocol uses the following main relations:

- indication
- contraindication
- target
- associated_with
- ppi

Their intended roles are:
- indication: main ranking relation
- contraindication: auxiliary safety annotation
- target / associated_with / ppi: evidence-structure relations

## 10. Annotation policy
### Contraindication policy
Contraindication is NOT used as a positive training relation for the main task.

Instead, contraindication is used as:
- auxiliary safety label
- hard-filter reference in future Setting B variants
- soft-penalty reference in future Setting B variants
- safety metric reference
- case-study safety flag

### Conflict policy
If a (drug, disease) pair appears in both indication and contraindication sources:
- keep the raw pair
- mark it with a conflict flag
- do not silently remove it

## 11. Splits and candidate protocol
### Setting A split
The benchmark uses a fixed split:
- train: 8388
- valid: 500
- test: 500

### Candidate protocol
Current candidate lists are mock coarse candidates prepared to unblock the pipeline.

Current constraints:
- candidate entities are drug-only
- gold drug is forced into the candidate list if needed
- valid/test candidate annotation is available for Setting B

### Leakage policy
Retrieval/preprocessing must not leak exact validation/test facts into the retrieval graph.
The current protocol uses train-only graph construction for leakage-safe retrieval preparation.

## 12. Current Setting B artifacts
The current Setting B protocol already includes:
- contraindication_pairs.tsv
- type_map.tsv
- schema_rules.json
- path_templates.yaml
- valid_b_annotations.json
- test_b_annotations.json

These files formalize Setting B as an evaluation-ready protocol rather than a draft-only idea.

## 13. Metrics
### Ranking metrics
- MRR
- Hits@1
- Hits@3
- Hits@10

### Safety metrics
- SafetyViolation@K
- Contra@K

### Constraint metrics
- ConstraintViolationRate

### Explanation metrics (planned / when feasible)
- Grounding Rate
- Path Faithfulness
- Evidence Density

### Efficiency metrics (planned)
- inference time per query
- average subgraph size
- average number of retrieved paths
- GPU memory usage

## 14. Intended use
This benchmark is intended for:
- backbone reproduction against DrKGC in Setting A
- safety/schema-aware extension studies in Setting B
- ablation studies for ontology-aware retrieval and fuzzy evidence modeling

It is NOT intended to support direct clinical recommendation.

## 15. Known limitations
- current candidate lists are still mock coarse candidates, not final learned retrieval outputs
- contraindication labels are currently used as auxiliary protocol annotations
- fuzzy confidence weighting is not yet implemented at this stage
- explanation metrics are protocol-defined but not yet fully operationalized

## 16. Summary
Setting A preserves benchmark fairness with DrKGC.
Setting B adds contraindication-aware safety and ontology-aware evaluation without changing the main task definition.
This dataset card v0 documents the protocol clearly enough for Month 2 backbone reproduction and later Setting B evaluation.