# Week 24 Day 6  PrimeKG E2E Diagnostics and Paper Assets

## Decision

**PRIMEKG_E2E_PAPER_ASSETS_READY**

## Model-selection interpretation

```json
{
  "metric_best_model": "llama3_8b",
  "metric_best_e2e_mrr_at20": 0.12532618,
  "primary_e2e_model": "llama3_2_3b",
  "primary_e2e_mrr_at20": 0.07468653,
  "diagnostic_top1_copy_models": [
    "llama3_8b",
    "medllama3_8b"
  ],
  "selection_rationale": "Llama-3-8B and MedLlama-3-8B reach candidate-ceiling MRR by copying the top-ranked candidate almost always. Llama-3.2-3B is kept as the primary E2E model because it avoids this degenerate top-1-copy behavior while preserving the FOG-RAG improvement trend."
}
```

## Primary E2E result

| Row | Gold@20 | Cand MRR | E2E MRR | H@3 | H@10 | Pred-in-cand | Invalid | Top1-copy | Avg graph |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| backbone_raw | 0.240 | 0.064563 | 0.047636 | 0.048 | 0.178 | 0.980 | 0.020 | 0.038 | 59.93 |
| soft_support_raw | 0.240 | 0.125326 | 0.074676 | 0.132 | 0.218 | 0.980 | 0.020 | 0.008 | 59.93 |
| retrieval_main | 0.240 | 0.125326 | 0.074687 | 0.132 | 0.218 | 0.998 | 0.002 | 0.010 | 32.34 |

## Retrieval cleaner-graph diagnostics

```json
{
  "valid": {
    "split": "valid",
    "num_rows": 500,
    "same_candidate_order_rate": 1.0,
    "same_rank_rate": 1.0,
    "retrieval_smaller_graph_rate": 1.0,
    "same_rank_cleaner_graph_count": 500,
    "same_rank_cleaner_graph_rate": 1.0,
    "avg_subgraph_reduction": 27.894,
    "min_subgraph_reduction": 20,
    "max_subgraph_reduction": 78,
    "cases": [
      {
        "row_index": 0,
        "query_entity": "leukemia, lymphocytic, susceptibility to",
        "gold_entity": "Cortisone acetate",
        "rank": 1,
        "soft_subgraph_size": 49,
        "retrieval_subgraph_size": 27,
        "subgraph_reduction": 22,
        "top5": [
          "Cortisone acetate",
          "Carmustine",
          "Vinblastine",
          "Bleomycin",
          "Propranolol"
        ]
      },
      {
        "row_index": 1,
        "query_entity": "streptococcal infection",
        "gold_entity": "Cefixime",
        "rank": 21,
        "soft_subgraph_size": 56,
        "retrieval_subgraph_size": 31,
        "subgraph_reduction": 25,
        "top5": [
          "Cortisone acetate",
          "Hydrocortisone",
          "Dexamethasone",
          "Triamcinolone",
          "Prednisolone"
        ]
      },
      {
        "row_index": 2,
        "query_entity": "dyspepsia",
        "gold_entity": "Magnesium trisilicate",
        "rank": 21,
        "soft_subgraph_size": 70,
        "retrieval_subgraph_size": 36,
        "subgraph_reduction": 34,
        "top5": [
          "Fusidic acid",
          "Cortisone acetate",
          "Hydrocortisone",
          "Dexamethasone",
          "Tetracycline"
        ]
      },
      {
        "row_index": 3,
        "query_entity": "basal cell carcinoma",
        "gold_entity": "Vismodegib",
        "rank": 21,
        "soft_subgraph_size": 59,
        "retrieval_subgraph_size": 32,
        "subgraph_reduction": 27,
        "top5": [
          "Cortisone acetate",
          "Dexamethasone",
          "Methylprednisolone",
          "Betamethasone",
          "Hydrocortisone"
        ]
      },
      {
        "row_index": 4,
        "query_entity": "obsessive-compulsive disorder",
        "gold_entity": "Fluoxetine",
        "rank": 21,
        "soft_subgraph_size": 77,
        "retrieval_subgraph_size": 39,
        "subgraph_reduction": 38,
        "top5": [
          "Cortisone acetate",
          "Dexamethasone",
          "Methylprednisolone",
          "Triamcinolone",
          "Hydrocortisone"
        ]
      },
      {
        "row_index": 5,
        "query_entity": "Norwegian scabies",
        "gold_entity": "Lindane",
        "rank": 21,
        "soft_subgraph_size": 94,
        "retrieval_subgraph_size": 39,
        "subgraph_reduction": 55,
        "top5": [
          "Fusidic acid",
          "Cortisone acetate",
          "Hydrocortisone",
          "Dexamethasone",
          "Tetracycline"
        ]
      },
      {
        "row_index": 6,
        "query_entity": "hypertension",
        "gold_entity": "Amiloride",
        "rank": 21,
        "soft_subgraph_size": 61,
        "retrieval_subgraph_size": 34,
        "subgraph_reduction": 27,
        "top5": [
          "Fusidic acid",
          "Cortisone acetate",
          "Hydrocortisone",
          "Dexamethasone",
          "Betamethasone"
        ]
      },
      {
        "row_index": 7,
        "query_entity": "pneumococcal meningitis",
        "gold_entity": "Meropenem",
        "rank": 21,
        "soft_subgraph_size": 64,
        "retrieval_subgraph_size": 33,
        "subgraph_reduction": 31,
        "top5": [
          "Fusidic acid",
          "Cortisone acetate",
          "Dexamethasone",
          "Hydrocortisone",
          "Betamethasone"
        ]
      },
      {
        "row_index": 8,
        "query_entity": "obsessive-compulsive disorder",
        "gold_entity": "Paroxetine",
        "rank": 21,
        "soft_subgraph_size": 77,
        "retrieval_subgraph_size": 39,
        "subgraph_reduction": 38,
        "top5": [
          "Cortisone acetate",
          "Dexamethasone",
          "Methylprednisolone",
          "Triamcinolone",
          "Hydrocortisone"
        ]
      },
      {
        "row_index": 9,
        "query_entity": "arthropathy",
        "gold_entity": "Diflunisal",
        "rank": 21,
        "soft_subgraph_size": 59,
        "retrieval_subgraph_size": 32,
        "subgraph_reduction": 27,
        "top5": [
          "Cortisone acetate",
          "Dexamethasone",
          "Methylprednisolone",
          "Hydrocortisone",
          "Betamethasone"
        ]
      }
    ]
  },
  "test": {
    "split": "test",
    "num_rows": 500,
    "same_candidate_order_rate": 1.0,
    "same_rank_rate": 1.0,
    "retrieval_smaller_graph_rate": 1.0,
    "same_rank_cleaner_graph_count": 500,
    "same_rank_cleaner_graph_rate": 1.0,
    "avg_subgraph_reduction": 27.592,
    "min_subgraph_reduction": 19,
    "max_subgraph_reduction": 76,
    "cases": [
      {
        "row_index": 0,
        "query_entity": "lung abscess (disease)",
        "gold_entity": "Ticarcillin",
        "rank": 21,
        "soft_subgraph_size": 66,
        "retrieval_subgraph_size": 32,
        "subgraph_reduction": 34,
        "top5": [
          "Cortisone acetate",
          "Fusidic acid",
          "Dexamethasone",
          "Betamethasone",
          "Triamcinolone"
        ]
      },
      {
        "row_index": 1,
        "query_entity": "acquired hyperprolactinemia",
        "gold_entity": "Cabergoline",
        "rank": 21,
        "soft_subgraph_size": 68,
        "retrieval_subgraph_size": 37,
        "subgraph_reduction": 31,
        "top5": [
          "Cortisone acetate",
          "Dexamethasone",
          "Methylprednisolone",
          "Triamcinolone",
          "Hydrocortisone"
        ]
      },
      {
        "row_index": 2,
        "query_entity": "allergic rhinitis",
        "gold_entity": "Hydrocortisone",
        "rank": 3,
        "soft_subgraph_size": 55,
        "retrieval_subgraph_size": 30,
        "subgraph_reduction": 25,
        "top5": [
          "Fusidic acid",
          "Cortisone acetate",
          "Hydrocortisone",
          "Betamethasone",
          "Tetracycline"
        ]
      },
      {
        "row_index": 3,
        "query_entity": "blepharoconjunctivitis",
        "gold_entity": "Hydrocortisone acetate",
        "rank": 4,
        "soft_subgraph_size": 54,
        "retrieval_subgraph_size": 30,
        "subgraph_reduction": 24,
        "top5": [
          "Betamethasone",
          "Triamcinolone",
          "Methylprednisolone",
          "Hydrocortisone acetate",
          "Ofloxacin"
        ]
      },
      {
        "row_index": 4,
        "query_entity": "parkinsonian-pyramidal syndrome",
        "gold_entity": "Procyclidine",
        "rank": 21,
        "soft_subgraph_size": 60,
        "retrieval_subgraph_size": 33,
        "subgraph_reduction": 27,
        "top5": [
          "Cortisone acetate",
          "Dexamethasone",
          "Methylprednisolone",
          "Triamcinolone",
          "Hydrocortisone"
        ]
      },
      {
        "row_index": 5,
        "query_entity": "pharyngitis",
        "gold_entity": "Dirithromycin",
        "rank": 21,
        "soft_subgraph_size": 52,
        "retrieval_subgraph_size": 29,
        "subgraph_reduction": 23,
        "top5": [
          "Cortisone acetate",
          "Hydrocortisone",
          "Dexamethasone",
          "Triamcinolone",
          "Prednisolone"
        ]
      },
      {
        "row_index": 6,
        "query_entity": "diabetes mellitus (disease)",
        "gold_entity": "Voglibose",
        "rank": 21,
        "soft_subgraph_size": 61,
        "retrieval_subgraph_size": 34,
        "subgraph_reduction": 27,
        "top5": [
          "Cortisone acetate",
          "Dexamethasone",
          "Methylprednisolone",
          "Triamcinolone",
          "Betamethasone"
        ]
      },
      {
        "row_index": 7,
        "query_entity": "Trichinella spiralis infectious disease",
        "gold_entity": "Methylprednisolone",
        "rank": 5,
        "soft_subgraph_size": 60,
        "retrieval_subgraph_size": 33,
        "subgraph_reduction": 27,
        "top5": [
          "Fusidic acid",
          "Dexamethasone",
          "Triamcinolone",
          "Prednisolone",
          "Methylprednisolone"
        ]
      },
      {
        "row_index": 8,
        "query_entity": "type 2 diabetes mellitus",
        "gold_entity": "Gliclazide",
        "rank": 21,
        "soft_subgraph_size": 60,
        "retrieval_subgraph_size": 33,
        "subgraph_reduction": 27,
        "top5": [
          "Cortisone acetate",
          "Dexamethasone",
          "Methylprednisolone",
          "Triamcinolone",
          "Betamethasone"
        ]
      },
      {
        "row_index": 9,
        "query_entity": "spondyloarthropathy",
        "gold_entity": "Methylprednisolone",
        "rank": 2,
        "soft_subgraph_size": 54,
        "retrieval_subgraph_size": 30,
        "subgraph_reduction": 24,
        "top5": [
          "Dexamethasone",
          "Methylprednisolone",
          "Hydrocortisone",
          "Hydrocortisone acetate",
          "Doxorubicin"
        ]
      }
    ]
  }
}
```

## Failure bucket summary

```json
{
  "counts": {
    "raw_bottleneck_failure": 380,
    "candidate_present_but_generation_fail": 118,
    "exact_target_success": 0,
    "top1_copy": 5,
    "other_candidate": 494,
    "invalid_generation": 1,
    "candidate_list_fragment": 0
  },
  "rates": {
    "raw_bottleneck_failure_rate": 0.76,
    "candidate_present_but_generation_fail_rate": 0.236,
    "exact_target_success_rate": 0.0,
    "top1_copy_rate": 0.01,
    "other_candidate_rate": 0.988,
    "invalid_generation_rate": 0.002,
    "candidate_list_fragment_rate": 0.0
  }
}
```

## Paper result paragraph

On the locked PrimeKG test split, soft-support re-ranking improves the reviewer-safe candidate MRR@20 from 0.064563 to 0.125326. In end-to-end generation with Llama-3.2-3B, the raw backbone obtains MRR@20=0.047636, while soft support reaches 0.074676. The FOG-RAG retrieval row preserves this E2E performance (0.074687) while reducing the average evidence subgraph from 59.93 to 32.34 triples.

## Limitation paragraph

The main remaining limitation is not the fuzzy retrieval stage but the upstream candidate and generation bottleneck. Gold entities are absent from the top-20 list in many queries, and even when the gold is present, the base LLM may generate a plausible but incorrect candidate. In model comparison, Llama-3-8B and MedLlama-3-8B reach candidate-ceiling MRR by copying the top-ranked candidate almost always, which motivates reporting top1-copy diagnostics alongside reviewer-safe E2E metrics.

## Model comparison paragraph

Model comparison shows that larger base LLMs do not necessarily provide better biomedical reasoning in this constrained generation setup. Llama-3-8B and MedLlama-3-8B obtain the highest test retrieval-main adjusted MRR@20 (0.125326), but their top1-copy rate is 1.0 on the main row. Therefore, we treat them as diagnostic candidate-order-following runs and keep Llama-3.2-3B as the primary E2E model.

## Outputs

- `/home/anhlq/Documents/2026-dhd/FOG-RAG/results/week24/diagnostics/primekg_e2e_failure_analysis.json`
- `/home/anhlq/Documents/2026-dhd/FOG-RAG/results/week24/diagnostics/primekg_generation_error_buckets.json`
- `/home/anhlq/Documents/2026-dhd/FOG-RAG/results/week24/diagnostics/primekg_case_samples.json`
- `/home/anhlq/Documents/2026-dhd/FOG-RAG/results/week24/diagnostics/primekg_e2e_paper_interpretation.json`
- `/home/anhlq/Documents/2026-dhd/FOG-RAG/results/week24/paper_assets/primekg_e2e_table_latex.tex`
- `/home/anhlq/Documents/2026-dhd/FOG-RAG/results/week24/paper_assets/primekg_model_compare_table_latex.tex`
- `/home/anhlq/Documents/2026-dhd/FOG-RAG/results/week24/paper_assets/primekg_e2e_result_paragraph.md`
- `/home/anhlq/Documents/2026-dhd/FOG-RAG/results/week24/paper_assets/primekg_e2e_limitation_paragraph.md`
- `/home/anhlq/Documents/2026-dhd/FOG-RAG/results/week24/paper_assets/primekg_model_compare_paragraph.md`
