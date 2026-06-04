# Week 11 - Day 1 Protocol Freeze

## 1. Goal
Evaluate Novelty 1 on Setting B using valid-first protocol, compare backbone / ontology / hard_main / soft_best, and choose the main paper variant before moving to month 4.

## 2. References
- Backbone reference: `week7-v2`
- Ontology reference: `week9_ontology_only`
- Safety main candidate: `week10_hard_main`
- Safety supporting candidate: `week10_soft_best`

## 3. Rows to compare
- `backbone` (reference): Backbone reference row evaluated under Setting B protocol [source=week7-v2]
- `ontology` (reference): Ontology-only supporting row [source=week9_ontology_only]
- `hard_main` (main_candidate): Ontology + contraindication-aware hard filtering row [source=week10_hard_main]
- `soft_best` (supporting_candidate): Ontology + contraindication-aware soft penalty row [source=week10_soft_best]

## 4. Evaluation scope
- Setting: `Setting B`
- Decision split: `valid`
- Test policy: `run_only_after_valid_protocol_is_clean`
- Novelty injection point: `candidate_stage_only`
- Retrain backbone: `False`

## 5. Main metrics
### Ranking
- MRR
- Hits@1
- Hits@3
- Hits@10

### Safety
- SafetyViolation@10
- Contra@10

### Constraint
- ConstraintViolationRate
- QueryHasConstraintViolationRate

## 6. Non-goals
- no_new_fuzzy_module
- no_hard_soft_logic_rewrite
- no_backbone_retraining
- no_new_structure_baseline
- no_final_acceptance_claim

## 7. Decision rule
- Default main variant: `hard_main`
- Supporting variant: `soft_best`
- Main selection rule: Prefer the row that keeps ranking stable while improving Setting B safety and constraint metrics most clearly.
- Override condition: Only replace hard_main if soft_best produces clearly better end-to-end Setting B trade-off or hard_main shows unacceptable fallback artifacts.

## 8. Expected outputs
### Results directories
- `results/week11/backbone_valid`
- `results/week11/ontology_valid`
- `results/week11/hard_main_valid`
- `results/week11/soft_best_valid`

### Comparison files
- `results/week11/variant_comparison.json`
- `results/week11/ablation_novelty1_v1.json`
- `results/week11/ablation_novelty1_v1.md`

## 9. End-of-week target
- Have a clean Setting B valid comparison table.
- Choose the main paper variant.
- Produce ablation v1 for Novelty 1.
