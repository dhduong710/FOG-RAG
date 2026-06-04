# Day 6 Table v0

## 1. Scope
- Gather all clean structure-only baseline rows
- Gather candidate-aware reranker reference rows
- Build the first Setting A result table v0

## 2. Structure-only baselines included
- R-GCN: MRR=0.05388868, Hits@10=0.152
- HRGAT: MRR=0.09550672, Hits@10=0.29
- ComplEx: MRR=0.13171101, Hits@10=0.41
- TransE: MRR=0.08074941, Hits@10=0.244

## 3. Reference rows included
- week7 3B: MRR=0.42424878, Hits@10=0.50999999
- week7 8B: MRR=0.43187144, Hits@10=0.51800001
- week8 posthoc 3B: MRR=0.31621575, Hits@10=0.384

## 4. Current conclusion
- Table v0 is clean and traceable.
- Structure-only baselines and candidate-aware references are separated.
- ComplEx is currently the best structure-only row.
- week7 3B remains the main reranker reference row.

## 5. Output files
- `results/week8/baseline_table_v0/setting_a_structure_table_v0.csv`
- `results/week8/baseline_table_v0/setting_a_structure_table_v0.md`
- `results/week8/baseline_table_v0/setting_a_reference_rows.md`
- `results/week8/baseline_table_v0/table_sources.json`
