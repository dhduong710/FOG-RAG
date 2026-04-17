# Week 13 Day 1 — Novelty 2 protocol freeze

## 1. Main truth
Novelty 2 uses raw / no-injection evaluation as the main scientific truth.
Injected results are supporting diagnostics only and must not appear as the main results table.

## 2. Main input source
The main candidate source for Novelty 2 is:
- dataset/setting_a/23_noinj_source/valid_top20_raw.json
- dataset/setting_a/23_noinj_source/test_top20_raw.json

This source is frozen and must not be replaced casually during Novelty 2.

## 3. Negative control
The negative control for Novelty 2 is:
- ontology_raw from dataset/setting_a/24_noinj_ontology/

This branch is kept to show that hard/binary ontology support is brittle on raw retrieval.

## 4. Evidence bridge
Novelty 2 retrieval/evidence work must build from:
- dataset/setting_a/24b_noinj_evidence/

This is the aligned evidence bridge for path/subgraph-level work.

## 5. Ontology and safety lookup
Novelty 2 is allowed to read ontology/safety metadata only from:
- dataset/setting_b/01_annotations/
- dataset/setting_b/01_ontology/
- dataset/setting_b/04_contra_checked/

These files provide type, schema, path templates, and contraindication lookup.

## 6. Legacy branch policy
The following are legacy/supporting only:
- dataset/setting_a/18_ontology_only*
- dataset/setting_a/19_contra_aware*
- dataset/setting_a/20_test_rerun_eval_ready*
- injected novelty-1 rows such as hard_main / soft_best in old branches

They may be cited in appendix/diagnostic discussion, but they are forbidden as the main input path for Novelty 2.

## 7. Scope of Week 13
Week 13 does not train fuzzy encoder or run final test.
Week 13 only:
1. freezes the Novelty 2 workspace,
2. freezes the allowed file registry,
3. audits support features on valid raw/no-injection candidates,
4. probes simple support scoring formulas.

## 8. Decision split
Valid is the only decision split in Week 13.
Test is untouched this week.

## 9. Expected output of Week 13
By the end of Week 13, the project should have:
- a clean week_13 branch,
- a frozen file registry,
- a valid support-feature artifact,
- a support-feature audit summary,
- a go / no-go decision for Week 14.

## 10. Scientific framing
Novelty 2 is framed as:
soft / fuzzy / confidence-aware support,
not harder ontology gating.