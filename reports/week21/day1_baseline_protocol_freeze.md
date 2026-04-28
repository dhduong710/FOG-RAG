# Week 21 Day 1 — Baseline Protocol Freeze

## Decision

**PROTOCOL_FROZEN_READY_FOR_INVENTORY**

## Theme

Fair comparison of structure baselines as top-20 candidate generators

## Main question

If TransE / ComplEx / R-GCN / HRGAT are used as upstream top-20 candidate generators for the same (? drug, indication, disease) task, how strong are they compared with backbone_raw, soft_support_raw, and soft_support_fuzzy_retrieval_main?

## Required framing statement

> Structure baselines are evaluated as upstream candidate generators for the downstream DrKGC/FOG-RAG top-20 prompting pipeline. This is not a classical full-universe filtered KGC metric.

## Frozen task protocol

| Field | Value |
|---|---|
| Task | Setting A head prediction |
| Query form | `(?, indication, disease)` |
| Missing entity type | `drug` |
| Target relation | `indication` |
| Query entity type | `disease` |
| Candidate universe | `drug_only` |
| Top-k | `20` |
| Gold injection | `forbidden` |

## Frozen metric protocol

| Field | Value |
|---|---|
| Main metric | `reviewer_safe_mrr_at20` |
| RR rule | `RR = 1/rank if rank <= 20 else 0` |
| Gold absent policy | `gold_absent_from_top20_has_rr_0` |
| Absent rank sentinel | `21` |
| RR for absent gold | `0` |

## Required metrics

- `gold_present_at20`
- `reviewer_safe_mrr_at20`
- `hits1_at20`
- `hits3_at20`
- `hits10_at20`
- `avg_gold_rank_absent_as_21`
- `gold_rank_21_count`

## Diagnostics to collect

- `num_rows`
- `candidate_size`
- `candidate_universe_size`
- `same_query_set`
- `unique_top1_count`
- `top1_dominance`

## Baselines in scope

Minimum baselines:

- `TransE`
- `ComplEx`
- `R-GCN`
- `HRGAT`

Optional baselines if already available:

- `DistMult`
- `RotatE`

## FOG-RAG rows for comparison

- `backbone_raw`
- `soft_support_raw`
- `soft_support_fuzzy_retrieval_main`

## Explicitly out of scope in Week 21

- `classical_full_ranking_KGC_table`
- `Bordes_filtered_metric_claim`
- `dataset_2`
- `Mistral_or_extra_LLM`
- `fuzzy_encoder_promotion`
- `gold_injection`
- `main_row_change_before_clean_baseline_table`

## Forbidden interpretations

- Do not call this Bordes et al. filtered metric.
- Do not call this DrKGC classical full-ranking metric.
- Do not use 1/21 for absent gold.
- Do not report gold-injected candidate metrics as reviewer-safe results.

## Paper-positioning scenarios prepared

### Scenario A — FOG-RAG strongest

FOG-RAG improves the DrKGC-compatible backbone and outperforms structure-only candidate generators under the downstream top-20 protocol.

### Scenario B — One baseline slightly higher

FOG-RAG is not necessarily the strongest pure candidate generator, but it improves the DrKGC-compatible source and provides evidence-aware retrieval with E2E confirmation.

### Scenario C — Baseline clearly higher

Consider a stronger-upstream branch using the strongest baseline as candidate source before opening Dataset 2.

## Next step

Proceed to **Day 2 — Baseline inventory audit**.

Day 2 should identify which baseline artifacts already exist, which ones can be recollected, and which ones must be rerun.
