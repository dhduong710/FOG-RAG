# Week 23 Day 6 — Diagnostics, Failure Analysis, and Paper Interpretation

## Decision

`DATASET2_DIAGNOSTICS_READY`

## Main diagnostic conclusion

- Raw candidate bottleneck remains strong.
- Hard support is non-discriminative on PharmKG because binary support/path features are saturated.
- Soft support is the source of ranking gain.
- Fuzzy retrieval is the source of evidence-efficiency gain.

## Raw candidate bottleneck

| Split | Raw bottleneck count | Rate | Raw gold-present count | Rate |
|---|---:|---:|---:|---:|
| valid | 465 | 0.930 | 35 | 0.070 |
| test | 454 | 0.908 | 46 | 0.092 |

Interpretation:

Most PharmKG queries remain raw candidate bottleneck cases, so FOG-RAG cannot improve Gold@20 without changing the candidate generator.

## Hard-support control

| Split | Same-rank rate | Same-candidates rate |
|---|---:|---:|
| valid | 1.000 | 1.000 |
| test | 1.000 | 1.000 |

Interpretation:

Hard binary graph support is non-discriminative on PharmKG because candidate support/path features are saturated.

## Soft-support improvements

| Split | Improved | Worsened | Improved given present | Avg rank delta given present | Avg RR delta |
|---|---:|---:|---:|---:|---:|
| valid | 24 | 0 | 0.686 | 2.800 | 0.003461 |
| test | 33 | 0 | 0.717 | 3.130 | 0.007678 |

Direct-T penalty effect:

| Split | Avg direct-T before | Avg direct-T in top-5 after |
|---|---:|---:|
| valid | 0.000 | 0.000 |
| test | 0.000 | 0.000 |

Interpretation:

Frozen soft support improves many gold-present cases and does not worsen any gold-present case in the current PharmKG run.

## Fuzzy retrieval efficiency

| Split | Same-rank cleaner count | Rate | Avg subgraph reduction | Coverage preserved rate |
|---|---:|---:|---:|---:|
| valid | 500 | 1.000 | 45.0 | 1.000 |
| test | 500 | 1.000 | 45.0 | 1.000 |

Interpretation:

Fuzzy retrieval preserves soft-support ranking while reducing every subgraph from 100 to 55 triples with full candidate/band coverage.

## Baseline position

- valid best structure baseline: `distmult`
- valid FOG-RAG main delta MRR: `0.001759791232`
- test best structure baseline: `rgcn`
- test FOG-RAG main delta MRR: `0.007678248918`

## Recommended paper claim

On PharmKG, frozen soft support transfers beyond PrimeKG by improving R-GCN top-20 ranking without valid/test gold injection, and fuzzy retrieval preserves the gain while reducing the evidence budget by 45%.

## Paper-safe language

- Use 'PharmKG therapeutic-association proxy task', not 'clinical indication'.
- Use 'task-specific reviewer-safe top-20 protocol', not 'full-universe PharmKG KGC'.
- Say FOG-RAG improves MRR/ranking among fixed top-20 candidates, not Gold@20 recall.
- Say fuzzy retrieval compresses evidence with preserved coverage, not that it suppresses shortcut rate.

## Example buckets written

The detailed examples are saved in:

- `results/week23/dataset2_case_buckets.json`

Buckets include:

- raw_bottleneck_failure
- soft_support_improved
- soft_support_worsened
- soft_support_unchanged_present
- hard_support_non_discriminative
- same_rank_cleaner_subgraph

## Files written

- `results/week23/dataset2_failure_analysis.json`
- `results/week23/dataset2_case_buckets.json`
- `results/week23/dataset2_paper_interpretation.json`
- `reports/week23/day6_diagnostics_and_optional_sources.md`

## Next step

Day 7 will close out Week 23 and decide final paper status.
