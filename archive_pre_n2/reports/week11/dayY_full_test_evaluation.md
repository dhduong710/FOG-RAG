# Week 11 - Full Test Evaluation for Novelty 1

## 1. Goal
Finalize the full test-side evaluation of Novelty 1 and prepare the final closeout.

## 2. Final decision
- main_row: `hard_main`
- supporting_row: `soft_best`
- reason: hard_main is at least as safe as soft_best on final-list test metrics and is not worse on ranking.

## 3. Test rows
- backbone: MRR=0.393101, Hits@10=0.524000, SafetyViolation@10=0.006000, Contra@10=0.006000, SafetyViolation@final=0.014000, Contra@final=0.014000
- ontology: MRR=0.435489, Hits@10=0.936000, SafetyViolation@10=0.006000, Contra@10=0.006000, SafetyViolation@final=0.012000, Contra@final=0.012000
- hard_main: MRR=0.448904, Hits@10=0.932000, SafetyViolation@10=0.002000, Contra@10=0.002000, SafetyViolation@final=0.002000, Contra@final=0.002000
- soft_best: MRR=0.417195, Hits@10=0.918000, SafetyViolation@10=0.002000, Contra@10=0.002000, SafetyViolation@final=0.012000, Contra@final=0.012000

## 4. Main interpretation
- The test results confirm the valid-side decision.
- hard_main remains the best overall trade-off row for Novelty 1.
- soft_best remains useful as a supporting ablation but is not stronger than hard_main.

## 5. Paper policy
- Use test results as the official main table for Novelty 1.
- Use valid results to explain how the row was selected.

## 6. Output files
- results/week11_test/ablation_novelty1_test_v1.json
- results/week11_test/ablation_novelty1_test_v1.md
- results/week11_test/novelty1_test_support_table.md
