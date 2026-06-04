# Week 13 Day 2 — Soft prune report

## 1. Goal
Clean the working tree for Novelty 2 while preserving legacy artifacts in archive_pre_n2.

## 2. Branch
- branch: week_13

## 3. Kept in working tree
- DrKGC / FOG-RAG base code
- week12 / week12A / week12B protocol and rescue files
- raw/no-injection source: 23_noinj_source
- negative control: 24_noinj_ontology
- evidence bridge: 24b_noinj_evidence
- ontology/safety lookup from setting_b
- reference rows copied to results/reference_rows

## 4. Archived
- old configs: week4, week5, week7, week8
- old scripts: week1–week11
- old reports: week1–week11
- old results: week4–week11*
- legacy setting_a branches before 23_noinj_source and novelty1 injected/hard-soft branches

## 5. Why this is needed
This reduces confusion and prevents Novelty 2 from accidentally reading legacy novelty1/injected artifacts.

## 6. Manual check summary
- key N2 input files still exist
- reference rows copied successfully
- archive_pre_n2 created successfully

## 7. Next step
Week 13 Day 3 will build support-feature artifacts on valid raw/no-injection candidates.