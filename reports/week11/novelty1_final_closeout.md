# Novelty 1 Final Closeout

## 1. Goal of Novelty 1

Novelty 1 was designed to add **ontology-aware** and **contraindication-aware** candidate handling on top of the **DrKGC backbone** without retraining a new backbone. The intervention point stayed at the **candidate stage**:

- **Week 9** established the ontology-supported branch.
- **Week 10** added the `hard_main` and `soft_best` variants.
- **Week 11** evaluated them under the **Setting B** protocol.

---

## 2. Evaluated Variants

The final four rows used for Novelty 1 evaluation are:

- `backbone`: DrKGC reference row
- `ontology`: ontology-only intermediate row
- `hard_main`: main Novelty 1 row
- `soft_best`: supporting ablation row

On **valid**, `hard_main` was selected as the **main row** because it matched `soft_best` on ranking while remaining cleaner at the candidate/final-list stage. Therefore, `soft_best` was kept only as a **supporting ablation**.

---

## 3. Valid-Side Result Used for Variant Selection

The valid-side patched evaluation showed the following pattern:

| Row | MRR | Hits@10 | SafetyViolation@final | Contra@final |
|---|---:|---:|---:|---:|
| backbone | 0.424249 | 0.510000 | 0.014000 | 0.014000 |
| ontology | 0.313018 | 0.434000 | 0.010000 | 0.010000 |
| hard_main | 0.393101 | 0.524000 | 0.000000 | 0.000000 |
| soft_best | 0.393101 | 0.524000 | 0.010000 | 0.010000 |

The valid-side support table also confirmed that `hard_main` was the cleanest final-list row:

| Metric | backbone | ontology | hard_main | soft_best |
|---|---:|---:|---:|---:|
| RowsWithContraFinal | 7 | 5 | 0 | 5 |
| AvgCandidateSize | 20.0 | 7.65 | 8.184 | 7.836 |

### Interpretation of valid-side results

- `ontology` alone was too conservative and substantially reduced ranking quality.
- `hard_main` recovered ranking relative to `ontology` while fully removing contraindicated final candidates.
- `soft_best` did not outperform `hard_main`, so it remained a supporting rather than primary row.

---

## 4. Official Test-Side Results for the Paper

After rebuilding the true ontology test source and rerunning the clean test pipeline, the **official test results** are:

| Row | MRR | Hits@1 | Hits@3 | Hits@10 | SafetyViolation@10 | Contra@10 | SafetyViolation@final | Contra@final |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| backbone | 0.393101 | 0.330000 | 0.358000 | 0.524000 | 0.006000 | 0.006000 | 0.014000 | 0.014000 |
| ontology | 0.435489 | 0.260000 | 0.486000 | 0.936000 | 0.006000 | 0.006000 | 0.012000 | 0.012000 |
| hard_main | 0.448904 | 0.290000 | 0.480000 | 0.932000 | 0.002000 | 0.002000 | 0.002000 | 0.002000 |
| soft_best | 0.417195 | 0.240000 | 0.468000 | 0.918000 | 0.002000 | 0.002000 | 0.012000 | 0.012000 |

### Final test decision

- **main_row** = `hard_main`
- **supporting_row** = `soft_best`

**Reason:** `hard_main` is at least as safe as `soft_best` on final-list metrics and is not worse on ranking.

---

## 5. Scientific Conclusion of Novelty 1

The correct and defensible conclusion is:

> Novelty 1 should **not** be presented as “beating the backbone on every axis”.  
> Novelty 1 should be presented as: **`hard_main` provides the best overall trade-off between ranking and safety under the current protocol.**

More specifically:

- Compared with `ontology`, `hard_main` clearly improves ranking on both **valid** and **test**.
- Compared with `soft_best`, `hard_main` is cleaner at the **final-list stage** on both **valid** and **test**.
- Compared with `backbone`, `hard_main` gives a stronger result under the **safety-aware evaluation protocol** on **test**, but the backbone still has higher final-list coverage, so the paper should avoid claiming a universal or unconditional win.

---

## 6. Role of Each Row in the Paper

Recommended roles in the paper:

- `backbone`: reference row
- `ontology`: intermediate ablation row
- `hard_main`: main row of Novelty 1
- `soft_best`: supporting ablation row

This assignment is consistent across:

- valid-side selection,
- week 10 decision logic,
- final test-side confirmation.

---

## 7. What Should Be Reported in the Paper

Use **test** as the official results split for Novelty 1, and use **valid** to explain:

- how the variant was selected,
- why `hard_main` was kept as the main row,
- why `soft_best` was retained only as a supporting ablation.

### Main test table should keep

- MRR
- Hits@1
- Hits@3
- Hits@10
- SafetyViolation@10
- Contra@10
- SafetyViolation@final
- Contra@final

### Support table should keep

- AvgCandidateSize
- GoldInFinalListRate
- RowsWithContraFinal
- SafetyViolation@final
- Contra@final

---

## 8. Limitations of Novelty 1

The limitations that should be stated transparently are:

- The gains of Novelty 1 are most visible at the **candidate/final-list stage**; at `@10`, the benchmark is already relatively clean, so several safety metrics saturate easily.
- `soft_best` does not provide a better trade-off than `hard_main`, so the soft-penalty path remains a **supporting ablation** rather than a competitive final choice.
- Novelty 1 is a **candidate-stage safety control mechanism**, not a clinical safety guarantee, and should not be written as a clinical decision system. This remains consistent with the week 10 framing of contraindication-aware candidate handling.

---

## 9. Final Decision

The final decision for Novelty 1 is:

- **Main row:** `hard_main`
- **Supporting row:** `soft_best`
- **Official paper results:** use **test**
- **Role of valid:** variant selection and protocol freeze
- **Status:** **GO to Novelty 2**

---

## 10. Handoff to Novelty 2

Novelty 2 should start under the following frozen assumptions:

- Novelty 1 is complete.
- The Setting B evaluation protocol is available.
- `hard_main` is the row that should be used as the main comparison base.
- `soft_best` should remain available as a supporting ablation when discussing safety trade-offs.

---

## Final Summary

**Novelty 1 is strong enough to close and include in the paper.**