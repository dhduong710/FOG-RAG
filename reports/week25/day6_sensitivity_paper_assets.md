# Week 25 Day 6 — Sensitivity Paper Assets

- Decision: **WEEK25_SENSITIVITY_PAPER_ASSETS_READY**
- Created at: `2026-05-02T22:03:29`

## Outputs

- `rule_sensitivity_table_latex`: `results/week25/paper_assets/rule_sensitivity_table_latex.tex`
- `template_sensitivity_table_latex`: `results/week25/paper_assets/template_sensitivity_table_latex.tex`
- `noise_robustness_table_latex`: `results/week25/paper_assets/noise_robustness_table_latex.tex`
- `week25_sensitivity_paragraph`: `results/week25/paper_assets/week25_sensitivity_paragraph.md`
- `week25_limitation_paragraph`: `results/week25/paper_assets/week25_limitation_paragraph.md`
- `day6_report`: `reports/week25/day6_sensitivity_paper_assets.md`

## Rule sensitivity test table

| Variant | Gold@20 | CandMRR | E2E MRR | H@10 | Invalid | AvgGraph |
| --- | --- | --- | --- | --- | --- | --- |
| main_rules | 0.24 | 0.125326 | 0.074687 | 0.218 | 0.002 | 32.34 |
| no_rules | 0.24 | 0.125326 | 0.074676 | 0.218 | 0.02 | 59.932 |
| random_rules | 0.24 | 0.125326 | 0.074742 | 0.218 | 0.002 | 32.34 |

## Template sensitivity test table

| Variant | E2E MRR | H@10 | Invalid | PredChange | DeltaMRR |
| --- | --- | --- | --- | --- | --- |
| T0_canonical | 0.074687 | 0.218 | 0.002 | 0.0 | 0.0 |
| T1_treatment | 0.074687 | 0.218 | 0.0 | 0.03 | 0.0 |
| T2_medication | 0.074722 | 0.218 | 0.002 | 0.006 | 3.5e-05 |
| T3_association_neutral | 0.074722 | 0.218 | 0.0 | 0.046 | 3.5e-05 |

## Noise robustness test table

| Variant | MRR@20 | H@10 | SameTop1 | RankChange | AvgGraph | DeltaMRR |
| --- | --- | --- | --- | --- | --- | --- |
| N0_no_noise | 0.125326 | 0.222 | 1.0 | 0.0 | 32.34 | 0.0 |
| N1_support_score_noise_seed1 | 0.077903 | 0.22 | 0.086 | 0.206 | 32.34 | -0.047423 |
| N2_support_score_noise_seed2 | 0.077914 | 0.216 | 0.096 | 0.214 | 32.34 | -0.047412 |
| N3_support_score_noise_seed3 | 0.076251 | 0.22 | 0.086 | 0.214 | 32.34 | -0.049075 |
| N4_subgraph_edge_dropout_5_seed1 | 0.125326 | 0.222 | 1.0 | 0.0 | 30.49 | 0.0 |
| N5_subgraph_edge_dropout_5_seed2 | 0.125326 | 0.222 | 1.0 | 0.0 | 30.49 | 0.0 |
| N6_subgraph_edge_dropout_5_seed3 | 0.125326 | 0.222 | 1.0 | 0.0 | 30.49 | 0.0 |

## Paper paragraph

## Week 25 sensitivity paragraph

We further conducted sensitivity analyses on the locked PrimeKG Setting A evaluation using the frozen Llama-3.2-3B decoding configuration. First, rule-package sensitivity shows that the main confidence-aware retrieval package achieves essentially the same E2E MRR@20 as the larger no-rule/source-graph variant (0.074687 vs. 0.074676), while reducing the average subgraph size from 59.93 to 32.34 triples (46.0\% reduction). The random-rule negative control also produces a nearly identical E2E score (0.074742), suggesting that, under the candidate-constrained setting, the main ranking gain is primarily driven by soft candidate support rather than brittle dependence on a single hand-coded rule package. Second, question-template sensitivity is minimal: canonical, treatment, medication, and association-neutral prompts produce E2E MRR@20 values within 0.000035 of each other on the locked test split. This indicates that the main result is not an artifact of one prompt wording, although the canonical indication prompt remains the main setting because it best matches the PrimeKG task definition. Third, light subgraph-edge dropout preserves candidate-level MRR@20 (0.125326 to 0.125326) while reducing the average graph from 32.34 to 30.49 triples, suggesting that the selected fuzzy evidence package is not fragile to minor edge loss.


## Limitation paragraph

## Week 25 limitation paragraph

The small-noise study also reveals an important limitation. When Gaussian perturbations are added directly to support scores before re-ranking, MRR@20 drops from 0.125326 to an average of 0.077356 across three seeds (average delta -0.047970). The same-top1 rate is only 0.089, with a rank-change rate of 0.211. Therefore, FOG-RAG should not be overclaimed as robust to arbitrary support-score perturbations. Instead, the result suggests that soft-support scoring is effective but remains sensitive near close score ties, motivating future calibration of support-score margins and uncertainty-aware re-ranking. In contrast, the graph package itself is stable under light edge dropout, so the main limitation lies more in support-score calibration than in fuzzy subgraph selection.

