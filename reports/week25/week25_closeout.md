# Week 25 Closeout — Sensitivity and Robustness for FOG-RAG

- Decision: **GO_WEEK25_SENSITIVITY_APPENDIX_READY**
- Created at: `2026-05-02T22:06:31`
- Role: **appendix sensitivity / robustness evidence**
- Main result status: **Week 24 remains frozen**
- Primary model: **Llama-3.2-3B**
- Frozen decoding: **cfg01_mnt16_rp100_ng0**
- Metric: **reviewer-safe RR@20**

## 1. What Week 25 answered

Week 25 addressed three reviewer-facing questions:

1. Does FOG-RAG depend too strongly on a single rule package?
2. Is the E2E result sensitive to question wording?
3. Is the retrieval/ranking stage robust to small support-score or graph perturbations?

## 2. Rule sensitivity

| Variant | Gold@20 | Cand MRR | E2E MRR | H@10 | Invalid | Avg graph |
| --- | --- | --- | --- | --- | --- | --- |
| main_rules | 0.24 | 0.125326 | 0.074687 | 0.218 | 0.002 | 32.34 |
| no_rules | 0.24 | 0.125326 | 0.074676 | 0.218 | 0.02 | 59.932 |
| random_rules | 0.24 | 0.125326 | 0.074742 | 0.218 | 0.002 | 32.34 |

**Conclusion:** rule variants are almost tied in E2E MRR under fixed candidate ordering. This means the paper should not overclaim rule superiority. The useful claim is that the main fuzzy retrieval package preserves E2E behavior while using a much smaller graph than the no-rule/source-graph variant and keeping invalid output lower.

## 3. Question-template sensitivity

| Template | E2E MRR | Invalid | Prediction change vs T0 |
| --- | --- | --- | --- |
| T0_canonical | 0.074687 | 0.002 | 0.0 |
| T1_treatment | 0.074687 | 0.0 | 0.03 |
| T2_medication | 0.074722 | 0.002 | 0.006 |
| T3_association_neutral | 0.074722 | 0.0 | 0.046 |

**Conclusion:** template sensitivity is minimal. Test E2E MRR range is only `0.000035`. The canonical indication prompt remains the main prompt because it matches the PrimeKG relation definition.

## 4. Small-noise robustness

### 4.1 Support-score noise

| Variant | MRR@20 | Same top1 | Interpretation |
| --- | --- | --- | --- |
| N0_no_noise | 0.125326 | 1.0 | main retrieval ranking |
| Score noise s1 | 0.077903 | 0.086 | ranking drops |
| Score noise s2 | 0.077914 | 0.096 | ranking drops |
| Score noise s3 | 0.076251 | 0.086 | ranking drops |

**Conclusion:** support-score noise is a real limitation. The model should not be described as robust to arbitrary score perturbations.

### 4.2 Edge dropout

| Variant | MRR@20 | Avg graph | Candidate coverage | Interpretation |
| --- | --- | --- | --- | --- |
| N0_no_noise | 0.125326 | 32.34 | 0.7831 | main graph |
| Edge drop s1 | 0.125326 | 30.49 | 0.7831 | stable |
| Edge drop s2 | 0.125326 | 30.49 | 0.7831 | stable |
| Edge drop s3 | 0.125326 | 30.49 | 0.7831 | stable |

**Conclusion:** light edge dropout preserves ranking and coverage. This supports the claim that fuzzy retrieval is not fragile to minor edge loss.

## 5. Paper-ready stance

Use Week 25 as:

- An appendix table set.
- A sensitivity/robustness paragraph.
- A limitation paragraph.

Do **not** use Week 25 as:

- A third novelty.
- A replacement for Week 24 main results.
- Evidence that FOG-RAG is robust to support-score noise.

## 6. Recommended paragraph for paper

FOG-RAG is not sensitive to prompt wording under the frozen candidate-constrained setting, and its fuzzy evidence package is stable under light subgraph edge dropout. However, support-score perturbation substantially changes candidate ordering, indicating that the soft-support score remains sensitive near close score ties. Therefore, the final paper should present Week 25 as robustness and limitation evidence rather than a new method contribution.

## 7. Final decision

**GO_WEEK25_SENSITIVITY_APPENDIX_READY**
