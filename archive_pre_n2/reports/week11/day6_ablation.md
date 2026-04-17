# Week 11 - Day 6 Ablation

## Goal
Build the first clean ablation table for Novelty 1 and prepare the week11 closeout.

## Rows included
- backbone: reference
- ontology: intermediate_ablation
- hard_main: main_variant
- soft_best: supporting_ablation

## Decision reused from Day 5
- main_row: `hard_main`
- supporting_row: `soft_best`
- reason: hard_main and soft_best tie on Setting B @10 safety/constraint metrics, but hard_main has higher GoldInTopKRate and cleaner week10 candidate-stage safety proxies.

## Interpretation
- backbone is the high-coverage reference row.
- ontology is the conservative intermediate row that demonstrates the cost of ontology-only filtering.
- hard_main is the main safety-aware row because it stays clean on Setting B while recovering ranking relative to ontology.
- soft_best remains useful as a supporting ablation but does not beat hard_main.

## Output files
- results/week11/ablation_novelty1_v1.json
- results/week11/ablation_novelty1_v1.md
