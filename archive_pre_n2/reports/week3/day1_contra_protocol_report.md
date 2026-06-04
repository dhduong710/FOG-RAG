# Day 1 Contraindication Protocol Report

## Input files
- week2 contraindication overlap: `dataset/setting_b/00_safety_labels/contraindication_edges_overlap.tsv`
- setting A split: `dataset/setting_a/01_split`
- setting A train graph: `dataset/setting_a/02_graph`

## Output files
- canonical contraindication pairs: `dataset/setting_b/01_annotations/contraindication_pairs.tsv`
- conflict-only subset: `dataset/setting_b/01_annotations/contraindication_conflicts.tsv`

## Summary
- total contraindication pairs: 16097
- conflict pairs (also appear in indication): 87

## Policy
Conflict pairs are retained in the raw annotation table and marked with `conflict_flag = 1`.
No pair is silently deleted.
