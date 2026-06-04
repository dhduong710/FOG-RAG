# Week 2 - Day 2 Split A Report

## Goal
Lock a fixed Setting A split for PrimeKG indication benchmark.

## Source
- Raw file: dataset/setting_a/00_raw_triples/primekg_indication_only.tsv

## Split sizes
- train: 8388
- valid: 500
- test: 500

## Coverage rule
- All drugs and diseases appearing in valid/test must also appear in train.

## Seed
- base_seed: 2025
- used_seed: 2025

## Train stats
- unique drugs: 1801
- unique diseases: 1363

## Valid stats
- unique drugs: 346
- unique diseases: 316

## Test stats
- unique drugs: 318
- unique diseases: 319

## Output files
- dataset/setting_a/01_split/train.tsv
- dataset/setting_a/01_split/valid.tsv
- dataset/setting_a/01_split/test.tsv
- dataset/setting_a/01_split/split_meta.json

## SHA256
- train.tsv: 97104e9dc8b3fb250df4ba08f7598bb34f2e8d3714959064221ff6989d8d9558
- valid.tsv: 2d131b40a45b309957d37498b7d97d48d6c39333093b1fd455e399f64b60b7b1
- test.tsv: ee189a2fed6137106123fb28f2a50d9b2ee8e2f54784a8cdb7cd799f996256fd
- split_meta.json: e06bdd2ef151765d459f2cdd22a36b4e54d4ec86979b757f547740e76ab4e9b1

## Notes
- This split is now the locked Setting A split.
- Do not change this split in later weeks.
