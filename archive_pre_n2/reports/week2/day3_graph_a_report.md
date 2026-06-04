# Week 2 - Day 3 Graph A Report

## Goal
Enrich Setting A training graph in DrKGC style.

## Inputs
- Raw KG: `dataset/raw/primekg/kg.csv`
- Train split: `dataset/setting_a/01_split/train.tsv`

## Output
- Enriched train graph: `dataset/setting_a/02_graph/train_enriched.tsv`

## Hub cap
- max_gene_degree: 1000

## Triple counts
- train indication: 8388
- target: 6131
- associated_with: 48271
- ppi: 73561
- support triples only: 127963
- total enriched triples: 136351

## Entity counts
- total entities: 10453
- drugs: 1801
- diseases: 1363
- gene/protein: 7289

## Relation types
- ['associated_with', 'indication', 'ppi', 'target']

## Hub filtering
- candidate genes before cap: 7337
- genes removed by hub cap: 48
- genes after cap: 7289

## Notes
- `train_enriched.tsv` includes both the 8388 train indication triples and the added support graph triples.
- `valid.tsv` and `test.tsv` remain unchanged.
- Raw PrimeKG stores symmetric PPI in both directions.
- Official FOG-RAG/DrKGC reproduction graph collapses PPI to one unordered edge per pair.