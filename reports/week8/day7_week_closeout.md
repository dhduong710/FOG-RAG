# Week Closeout — Candidate Retrieval Strengthening, Reranker Validation, and Final Decision

## 1. Scope of this week

This week focused on repairing the main bottleneck observed in the previous stage: **candidate retrieval quality was too weak and too dependent on gold injection**, which made backbone valid results scientifically hard to interpret.

The intended goals were:

- improve coarse candidate retrieval quality on Setting A,
- reduce dependence on gold injection,
- compare week6 vs week7 retrieval directly on the same valid queries,
- rebuild a clean backbone-ready package,
- rerun valid backbone evaluation,
- check whether stronger backbone capacity (8B) helps,
- and decide whether further retrieval refinement is worthwhile.

---

## 2. Starting point

At the beginning of the week, the main retrieval failure mode was already clear:

- week6 valid `recall@20_raw = 0.02`
- week6 valid `inject_ratio_ready = 0.98`

This meant that the reranker was still heavily relying on injected gold rather than a genuinely useful raw candidate list.

The main concern was not whether the backbone could train, but whether the retrieval pipeline could produce a scientifically meaningful candidate source.

---

## 3. What was done this week

### 3.1 Retrieval audit and diagnosis
We first audited the week6 retrieval behavior and confirmed that the main bottleneck was **candidate source quality**, not the backbone path itself.

### 3.2 Train `ranker_v2`
We trained a more stable R-GCN-based coarse ranker with a stability-first configuration and rebuilt candidate artifacts for train/valid/test.

### 3.3 Build candidate artifacts and compare week6 vs week7
We scored full train/valid/test, rebuilt:

- `top20_raw`
- `top20_drkgc_ready`

and then compared week6 vs week7 directly on the same valid queries.

### 3.4 Rebuild backbone-ready package
Using the improved candidate artifacts, we rebuilt a clean `backbone_ready` package and re-ran the 3B backbone on valid.

### 3.5 Capacity sanity check with 8B
We then ran a larger 8B backbone to test whether the main bottleneck was simply insufficient LLM capacity.

### 3.6 Retrieval-v3 refinement attempts
We explored a retrieval-v3 direction with hard negatives and collapse-aware training, but those retraining attempts did not produce a clear Pareto improvement over week7-v2.

### 3.7 Post-hoc debias sweep
Finally, instead of retraining again, we applied a lightweight post-hoc score debias sweep on top of week7-v2 scores and selected the best valid lambda.

---

## 4. Main retrieval results

The main retrieval improvement of the week came from **week7-v2**.

### Week6 valid retrieval
- `recall@20_raw = 0.02`
- `top1_hit_ratio_raw = 0.0`
- `inject_ratio_ready = 0.98`

### Week7-v2 valid retrieval
- `recall@20_raw = 0.192`
- `top1_hit_ratio_raw = 0.018`
- `inject_ratio_ready = 0.808`

This was a real improvement, not just noise.

At the per-query level:

- `improved_to_top20 = 96`
- `worsened_out_of_top20 = 10`

So retrieval quality improved **systematically**.

However, retrieval collapse remained significant in week7-v2 valid:

- `unique_top1_count_raw = 3`
- `top1_dominance_ratio_raw = 0.482`

The dominant top-1 drugs were still heavily concentrated in a very small set of generic drugs.

---

## 5. Backbone valid results

### Week7 3B rerun
Using the improved week7-v2 candidate package, the 3B reranker produced:

- `MRR = 0.42424878`
- `Hits@1 = 0.368`
- `Hits@3 = 0.39399999`
- `Hits@10 = 0.50999999`

### Week7 8B rerun
The 8B rerun improved only slightly:

- `MRR = 0.43187144`
- `Hits@1 = 0.37599999`
- `Hits@3 = 0.40200001`
- `Hits@10 = 0.51800001`

This was an important finding.

**Increasing backbone capacity from 3B to 8B did not solve the main problem.**

That means the current bottleneck is **not primarily LLM capacity**. The harder candidate package is still exposing a retrieval-side weakness.

---

## 6. Retrieval-v3 retraining attempts

We attempted a retrieval-v3 refinement direction with collapse-aware hard negatives.

### Scratch retrieval-v3
This reduced collapse, but retrieval signal fell too much.

### Warm-start retrieval-v3 (day2b)
Warm-starting from `ranker_v2` recovered some probe retrieval signal:

- probe `recall20 = 0.21`

but collapse effectively returned:

- `unique_top1_count = 3`
- `top1_dominance_ratio = 0.48`

In addition, the best checkpoint still showed weak score separation at the score-stat level.

### Conclusion from retrieval-v3 retraining
The retrieval-v3 retraining path **did not produce a clearly better Pareto point than week7-v2**.

So it was not adopted as the new main retrieval path.

---

## 7. Post-hoc debias sweep

Since retraining did not clearly win, we tested a cheaper and cleaner option: **post-hoc score debias** on week7-v2.

We swept several lambda values on valid and selected the best one under the rule:

- do not meaningfully hurt recall,
- reduce collapse,
- or increase top-1 diversity.

### Best lambda
The best choice was:

- `lambda = 0.05`

### Baseline week7-v2 valid
- `recall@20_raw = 0.192`
- `top1_hit_ratio_raw = 0.018`
- `inject_ratio_ready = 0.808`
- `unique_top1_count_raw = 3`
- `top1_dominance_ratio_raw = 0.482`

### Post-hoc debias valid with `lambda = 0.05`
- `recall@20_raw = 0.192`
- `top1_hit_ratio_raw = 0.018`
- `inject_ratio_ready = 0.808`
- `unique_top1_count_raw = 9`
- `top1_dominance_ratio_raw = 0.416`

This was the cleanest retrieval-side improvement of the whole refinement stage:

- no recall drop,
- no injection penalty,
- but clearly reduced collapse.

---

## 8. Final reranker check on the debiased package

To verify whether the post-hoc debias should become the new final package, we rebuilt a backbone-ready package from the best-lambda artifacts and re-ran the 3B reranker.

### Post-hoc debias 3B valid rerun
- `MRR = 0.31621575`
- `Hits@1 = 0.25400001`
- `Hits@3 = 0.28200001`
- `Hits@10 = 0.384`

Compared with week7 3B:

- `delta MRR = -0.10803303`
- `delta Hits@1 = -0.11399999`
- `delta Hits@3 = -0.11199998`
- `delta Hits@10 = -0.12599999`

So although post-hoc debias **improved retrieval-side collapse**, it **did not improve end-to-end reranker performance**. In fact, it made the final valid reranker results worse.

---

## 9. Final decision

## Final week decision: **CONDITIONAL GO**

### Why GO
Because the week successfully improved retrieval quality over week6 in a real and systematic way.

Week7-v2 is a better and more scientifically meaningful retrieval package than week6.

### Why CONDITIONAL
Because the retrieval improvement did **not transfer cleanly** into better end-to-end reranker valid performance.

That means the week solved the retrieval foundation **partially**, but not fully.

---

## 10. What should be kept as the final outputs

### Main backbone package to carry forward
Use **week7-v2** as the main package for end-to-end backbone experiments.

### Supporting retrieval-side result
Keep **post-hoc debias with `lambda = 0.05`** as a retrieval-side analysis / ablation result.

This is important because it shows that collapse can be reduced by a lightweight bias correction without hurting raw retrieval metrics, even though this did not translate into better reranker valid.

---

## 11. What should *not* be done next

At this point, we should **not**:

- continue training more retrieval-v3 variants,
- scale to even larger backbones,
- or keep tuning more collapse heuristics.

The current evidence already tells a coherent story, and additional tuning is likely to give diminishing returns.

---

## 12. Scientific interpretation of the week

This week successfully shifted the project from a weak and highly injected candidate setup toward a stronger and more realistic retrieval setting.

The strongest scientific conclusions are:

1. **Candidate retrieval can be improved substantially over week6.**
2. **The main bottleneck is still retrieval quality / collapse, not simply LLM size.**
3. **Increasing backbone size from 3B to 8B gives only small gains.**
4. **Collapse can be reduced by a lightweight post-hoc debias, but that does not automatically improve end-to-end reranking.**

This makes the final story much stronger and more honest than simply reporting one backbone score.

---

## 13. Final frozen outputs

### Freeze as main path
- `week7-v2` retrieval artifacts
- `week7-v2` backbone valid results

### Freeze as supporting analysis
- post-hoc debias `lambda = 0.05`
- retrieval-v3 retraining notes showing why retraining did not beat week7-v2

---

## 14. Short final summary

This week produced a meaningful retrieval improvement over week6, but that improvement did not fully transfer into end-to-end reranker gains. The best main package remains **week7-v2**. A lightweight **post-hoc debias (`lambda = 0.05`)** is worth keeping as a retrieval-side analysis because it reduces collapse without hurting raw retrieval metrics, but it should **not** replace week7-v2 as the final backbone package.