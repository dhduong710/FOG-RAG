# Week 12B Closeout — No-injection Rerun for Novelty 1

## 1. Objective of the week

Week 12B was opened to answer one very specific question: **Without gold injection, what can Novelty 1 still achieve on raw R-GCN retrieval?**

The goal of this week was not to make the results look better, but to:

* promote **no-injection** to the role of **main scientific check**,
* demote **injected reranker-ready results** to the role of **supporting / diagnostic evidence**,
* and verify whether the ontology / hard / soft branches of Novelty 1 still hold up under true raw retrieval.

The raw source of truth was frozen from `dataset/setting_a/21_ranker_rescue` into `dataset/setting_a/23_noinj_source`, with valid `recall@20_raw = 0.202` and test `recall@20_raw = 0.24`.

## 2. What was done during the week

### Day 1 — Freeze the no-injection protocol

The week was finalized under the following protocol:

* **main truth** = no-injection,
* **supporting truth** = injected reranker-ready,
* 4 target rows = `backbone_raw`, `ontology_raw`, `hard_main_raw`, `soft_best_raw`,
* valid is the decision split,
* test is used only after valid is clean.

The raw source was successfully frozen while preserving the raw candidate lists for valid/test. The raw source manifest confirmed valid `recall@20_raw = 0.202` and test `recall@20_raw = 0.24`.

### Day 2 — Build `ontology_raw`

The `type_filtered_raw` branch behaved correctly and did not change the candidate list, because the raw source was already `drug_only`:

* valid: `avg_candidate_size = 20.0`, `gold_in_topk_rate = 0.202`
* test: `avg_candidate_size = 20.0`, `gold_in_topk_rate = 0.24`

However, after ontology filtering, `ontology_raw` dropped sharply:

* valid: `avg_candidate_size = 8.796`, `gold_in_topk_rate = 0.014`
* test: `avg_candidate_size = 8.042`, `gold_in_topk_rate = 0.012`

This was the first signal that the ontology-only policy was too strict under raw retrieval. Sample cases showed that some gold entities were present in the raw top-20 but were removed by ontology filtering.

### Day 3 — Audit alignment and rebuild raw-aligned evidence

An important issue was discovered: the original evidence sidecar had been taken from the wrong source, causing the valid/test candidate rows to be misaligned with the evidence rows. After scanning all `valid.json` files, the correct source was identified as `dataset/setting_a/12_backbone_ready_ranker_v2/*.json`, and the evidence package was rebuilt.

After the fix, the alignment manifest showed:

* valid: `num_rebuilt_rows = 500`, `same_query_rate_zip = 1.0`, `same_gold_rate_zip = 1.0`, `same_candidate_list_rate_zip = 1.0`, `exact_leak_count = 0`
* test: `num_rebuilt_rows = 500`, `same_query_rate_zip = 1.0`, `same_gold_rate_zip = 1.0`, `same_candidate_list_rate_zip = 1.0`, `exact_leak_count = 0`

This means the valid/test alignment issue was fully fixed. Train was also rebuilt successfully, but it had `exact_leak_count = 8388`, so train cannot be used for any scientific conclusion in this week.

### Day 4 — Ontology pruning / gold removal audit

After rerunning `ontology_raw` with correctly aligned evidence, the results remained almost equally poor. This means the problem no longer came from evidence mismatch, but from the **ontology policy itself**.

The gold-loss audit showed:

**Valid**

* `num_raw_gold_cases = 101`
* `num_pruning_cases = 94`
* `pruning_rate_given_raw_gold = 0.930693`

**Test**

* `num_raw_gold_cases = 120`
* `num_pruning_cases = 114`
* `pruning_rate_given_raw_gold = 0.95`

Most importantly, all pruning cases shared the same dominant reason:

* `gold_no_ontology_support`

There was no evidence that the issue came from the type map or from incorrectly typed gold entities. Sample cases confirmed that the gold entities were all typed as `Drug` in the `type_map`, yet they were still removed because they did not satisfy the current ontology-support policy.

## 3. Scientific conclusion of Week 12B

The strongest conclusion of this week is:

> **The ontology-only raw branch is a NO-GO under the current no-injection raw retrieval setting.**

More specifically:

* the current ontology policy removes around **93%** of raw-gold cases on valid,
* and around **95%** of raw-gold cases on test,
* and the dominant reason is not a type error, but **lack of ontology support**.

This means:

* **Novelty 1 in the form of hard ontology-supported retrieval does not hold up under true raw retrieval**
* the current policy is **too brittle / too aggressive**
* it only appears more acceptable when the candidate artifacts are prepared more favorably in the reranker-ready setting

This is a **negative finding**, but it is a **high-value negative finding**:

* it is transparent,
* it clearly explains what is not working,
* and it points directly to the issue that Novelty 2 needs to solve.

## 4. Was Week 12B successful?

**Yes.**

But not in the sense that “Novelty 1 looks better.” It was successful because:

* the protocol was made more transparent,
* injected vs no-injection were clearly separated into different roles,
* the alignment bug was found and fixed,
* and most importantly, it became clear that **the real issue is not evidence mismatch or the type map, but the hard ontology-support policy itself**.

In other words, Week 12B turned a vague suspicion into a clear conclusion:

* **hard ontology gating is too rigid under raw retrieval**
* therefore, it should not be pushed further as `ontology_raw -> hard_main_raw / soft_best_raw` under the current policy

## 5. Decisions after closeout

### Decision 1

**Stop the current `ontology_raw -> hard/soft_raw` branch.**

It is not worth continuing to build `hard_main_raw` and `soft_best_raw` from the current ontology policy, because that would almost certainly produce more poor results in a predictable way.

### Decision 2

**Keep no-injection results as the main scientific check.**  
**Keep injected results as supporting / diagnostic evidence.**

This is a better framing for a Q2-journal-oriented paper:

* more transparent,
* more honest,
* easier to defend in front of reviewers.

### Decision 3

**Use this negative finding itself to justify Novelty 2.**

Novelty 2 now has a very clear motivation:

* hard binary ontology support is too strict,
* so a **softer / fuzzier / confidence-aware mechanism** is needed,
* that is, instead of asking whether a candidate is supported or not, the model should represent the **degree of support** and the **confidence of the evidence**.

## 6. Implications for the paper

If the paper is written for a Q2 venue, I recommend the following framing:

### Main truth

* No-injection evaluation better reflects real retrieval quality and the true robustness of the candidate-stage policy.

### Supporting diagnostic

* Injected reranker-ready results can still be kept to answer a secondary question:
  * if the coarse retriever already contains the gold entity in the candidate set, how well does the reranker / downstream pipeline handle it?

### A more reviewer-safe narrative

You can state clearly that:

* Novelty 1 hard ontology gating looks reasonable on reranker-ready artifacts,
* but when moved to raw no-injection evaluation, it removes most raw-gold cases because of lack of ontology support,
* therefore, the correct next step is not stronger hard gating, but **soft/fuzzy support modeling**.

This creates a very natural transition into Novelty 2.

## 7. Final conclusion of the week

### Week 12B has demonstrated that:

* no-injection evaluation is necessary
* the current hard ontology support is too brittle
* this negative finding is real, not a type-map issue
* the valid/test alignment issue has been fixed
* Novelty 2 should be built in the direction of **soft / fuzzy / confidence-aware support**, not by continuing hard binary ontology pruning

### Final Week 12B status

* **Protocol status**: clean
* **Scientific status**: informative negative finding
* **Novelty 1 no-injection hard ontology branch**: NO-GO
* **Next step**: open Novelty 2 with a new framing based on soft/fuzzy support