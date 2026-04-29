# Week 22 Day 1 — Dataset 2 Protocol Freeze

## Decision

`DATASET2_PROTOCOL_FROZEN_RELATION_PENDING`

Dataset 2 is currently treated as: **PharmKG candidate**.

The selected relation is **not fixed today**. It remains:

`therapeutic_relation_candidate`

Relation/schema selection will be done on Day 3 after raw inventory.

## Frozen task frame

- Incomplete triple: `(?, therapeutic_relation_candidate, disease)`
- Missing entity type: `drug`
- Query entity type: `disease`
- Candidate universe: `drug_only`
- Top-K: `20`
- Gold injection: `forbidden`

## Reviewer-safe metric policy

Main metric:

`reviewer_safe_mrr_at20`

RR policy:

`RR = 1/rank if gold is present and rank <= 20 else 0`

Absent-gold policy:

- descriptive rank sentinel = `21`
- RR contribution = `0.0`

Do **not** use 1/21 as reciprocal rank for absent gold.

## Paper framing

Dataset 2 is evaluated under the same top-20 no-injection reviewer-safe protocol as Setting A. The purpose is to test transferability of the FOG-RAG pipeline, not to introduce a different KGC metric.

## PharmKG data acquisition plan for Day 2

Preferred source: **PharmKG-8k**

Sources to try:

1. biomed-AI PharmKG GitHub PharmKG-8k:
   - train.tsv
   - valid.tsv
   - test.tsv
   - entity2vec.txt
   - relation2vec.txt

2. Official PharmKG Zenodo raw archive:
   - raw_PharmKG-180k.zip

3. MindRank-Biotech PharmKG repository:
   - README statistics
   - preprocessing notes
   - links to original/raw resources

## Day 1 checks

- candidate_universe = drug_only
- top_k = 20
- gold_injection = forbidden
- rr_absent_policy = 0
- absent_rank_sentinel = 21
- target relation is not selected yet

## Files written

- `results/week22/dataset2_protocol_freeze.json`
- `dataset/setting_c_pharmkg/00_raw_inventory/download_plan.json`
- `reports/week22/day1_dataset2_protocol_freeze.md`

## Next day

Day 2 will download or locate PharmKG files and run raw inventory:
file list, row counts, columns, sample rows, relation counts, and possible entity/type sources.
