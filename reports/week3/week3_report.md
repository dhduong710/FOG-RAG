# Week 3 Report

## 1. What was locked this week

### 1.1 Contraindication role
- Contraindication is NOT used as positive training triples for the main task.
- Contraindication is stored as auxiliary safety labels.
- Setting A remains unchanged for fair DrKGC-compatible comparison.
- Setting B uses contraindication for safety analysis, hard-filter / soft-penalty variants, and case-study flagging.

### 1.2 Type map
- A benchmark-relevant coarse type map was frozen from the ontology JSON.
- Final benchmark entity universe: 10453
- Missing raw ontology types resolved by context override: 39
- Valid/test candidate entities typed as non-Drug: 0

### 1.3 Schema rules and path templates
- schema_rules.json was frozen for:
  - indication: Drug -> Disease
  - contraindication: Drug -> Disease
  - target: Drug -> Protein_or_Gene
  - associated_with: Protein_or_Gene -> Disease
  - ppi: Protein_or_Gene -> Protein_or_Gene
- path_templates.yaml was created.
- Contraindication is retained for safety lookup but not allowed as supportive treatment evidence.

### 1.4 Setting B eval-ready annotations
- valid_b_annotations.json and test_b_annotations.json were created.
- valid stats:
  - num_samples: 500
  - all_candidates_have_type: True
  - non_drug_candidates: 0
  - gold_missing_annotation: 0
  - contra_positive_samples: 71
- test stats:
  - num_samples: 500
  - all_candidates_have_type: True
  - non_drug_candidates: 0
  - gold_missing_annotation: 0
  - contra_positive_samples: 75

### 1.5 Dataset card
- dataset_card_v0.md was completed.
- Setting A and Setting B are now described as separate but connected protocols.

### 1.6 Evaluator skeleton
- eval_safety_metrics.py implemented:
  - SafetyViolation@K
  - Contra@K
- eval_constraint_metrics.py implemented:
  - ConstraintViolationRate
  - QueryHasConstraintViolation@K
- Mock tests passed.
- Real valid/test files run without error.

## 2. What remains uncertain
- learned confidence is not implemented
- fuzzy confidence weighting is not implemented
- full logical rule mining / path mining is not implemented
- explanation metrics are defined but not yet operational

## 3. What is ready for Month 2
- Setting A split and graph pipeline are fixed
- Setting B is formalized as an evaluation protocol
- candidate/type/schema/annotation files are ready
- metric code skeleton is ready
- the project can move to Month 2 backbone reproduction without protocol ambiguity

## 4. Go / No-Go decision
Go.

Reason:
- type map is clean enough
- schema rules are validated
- dataset card v0 is available
- eval skeleton runs correctly
- Setting B is now formalized rather than vaguely described

## 5. Final conclusion
Week 3 successfully formalized Setting B into a clear evaluation protocol.
Contraindication is treated as auxiliary safety labels rather than main-task positives.
Ontology/schema constraints are sufficiently defined for candidate and path validation.
Dataset card v0 and evaluator skeleton are ready for Month 2 backbone reproduction.