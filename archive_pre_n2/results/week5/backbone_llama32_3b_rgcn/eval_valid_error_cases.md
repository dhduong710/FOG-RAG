# Week 5 - Day 6 Error Case Report

## Overall metrics
- mrr: `1.0`
- hits1: `1.0`
- hits3: `1.0`
- hits10: `1.0`
- num_examples: `500`
- split: `valid`

## Category counts
- hit@1: `500`

## 5 best cases
```json
[
  {
    "query_entity": "leukemia, lymphocytic, susceptibility to",
    "target": "Cortisone acetate",
    "pred": "Cortisone acetate",
    "pred_rank": 1,
    "gold_rank_before_llm": 1,
    "candidate_size": 20,
    "subgraph_size": 63,
    "top5_candidates": [
      "Cortisone acetate",
      "Pitavastatin",
      "Cenegermin",
      "Metharbital",
      "Sulindac"
    ],
    "category": "hit@1"
  },
  {
    "query_entity": "streptococcal infection",
    "target": "Cefixime",
    "pred": "Cefixime",
    "pred_rank": 1,
    "gold_rank_before_llm": 1,
    "candidate_size": 20,
    "subgraph_size": 84,
    "top5_candidates": [
      "Cefixime",
      "Aurothioglucose",
      "Megestrol acetate",
      "Cetilistat",
      "Selegiline"
    ],
    "category": "hit@1"
  },
  {
    "query_entity": "dyspepsia",
    "target": "Magnesium trisilicate",
    "pred": "Magnesium trisilicate",
    "pred_rank": 1,
    "gold_rank_before_llm": 1,
    "candidate_size": 20,
    "subgraph_size": 86,
    "top5_candidates": [
      "Magnesium trisilicate",
      "Vinorelbine",
      "Deutetrabenazine",
      "Radotinib",
      "Fluocinolone acetonide"
    ],
    "category": "hit@1"
  },
  {
    "query_entity": "basal cell carcinoma",
    "target": "Vismodegib",
    "pred": "Vismodegib",
    "pred_rank": 1,
    "gold_rank_before_llm": 1,
    "candidate_size": 20,
    "subgraph_size": 72,
    "top5_candidates": [
      "Vismodegib",
      "Doxylamine",
      "Vaniprevir",
      "Prucalopride",
      "Natalizumab"
    ],
    "category": "hit@1"
  },
  {
    "query_entity": "obsessive-compulsive disorder",
    "target": "Fluoxetine",
    "pred": "Fluoxetine",
    "pred_rank": 1,
    "gold_rank_before_llm": 1,
    "candidate_size": 20,
    "subgraph_size": 73,
    "top5_candidates": [
      "Fluoxetine",
      "Ropeginterferon alfa-2b",
      "Maprotiline",
      "Erenumab",
      "Plicamycin"
    ],
    "category": "hit@1"
  }
]
```

## 5 worst cases
```json
[
  {
    "query_entity": "leukemia, lymphocytic, susceptibility to",
    "target": "Cortisone acetate",
    "pred": "Cortisone acetate",
    "pred_rank": 1,
    "gold_rank_before_llm": 1,
    "candidate_size": 20,
    "subgraph_size": 63,
    "top5_candidates": [
      "Cortisone acetate",
      "Pitavastatin",
      "Cenegermin",
      "Metharbital",
      "Sulindac"
    ],
    "category": "hit@1"
  },
  {
    "query_entity": "streptococcal infection",
    "target": "Cefixime",
    "pred": "Cefixime",
    "pred_rank": 1,
    "gold_rank_before_llm": 1,
    "candidate_size": 20,
    "subgraph_size": 84,
    "top5_candidates": [
      "Cefixime",
      "Aurothioglucose",
      "Megestrol acetate",
      "Cetilistat",
      "Selegiline"
    ],
    "category": "hit@1"
  },
  {
    "query_entity": "dyspepsia",
    "target": "Magnesium trisilicate",
    "pred": "Magnesium trisilicate",
    "pred_rank": 1,
    "gold_rank_before_llm": 1,
    "candidate_size": 20,
    "subgraph_size": 86,
    "top5_candidates": [
      "Magnesium trisilicate",
      "Vinorelbine",
      "Deutetrabenazine",
      "Radotinib",
      "Fluocinolone acetonide"
    ],
    "category": "hit@1"
  },
  {
    "query_entity": "basal cell carcinoma",
    "target": "Vismodegib",
    "pred": "Vismodegib",
    "pred_rank": 1,
    "gold_rank_before_llm": 1,
    "candidate_size": 20,
    "subgraph_size": 72,
    "top5_candidates": [
      "Vismodegib",
      "Doxylamine",
      "Vaniprevir",
      "Prucalopride",
      "Natalizumab"
    ],
    "category": "hit@1"
  },
  {
    "query_entity": "obsessive-compulsive disorder",
    "target": "Fluoxetine",
    "pred": "Fluoxetine",
    "pred_rank": 1,
    "gold_rank_before_llm": 1,
    "candidate_size": 20,
    "subgraph_size": 73,
    "top5_candidates": [
      "Fluoxetine",
      "Ropeginterferon alfa-2b",
      "Maprotiline",
      "Erenumab",
      "Plicamycin"
    ],
    "category": "hit@1"
  }
]
```

## Notes
- `prediction_not_in_candidate` often suggests reranking/generation drift.
- `prediction_in_candidate_but_not_top` often suggests candidate quality or graph signal may be insufficient.
- This report is mechanical; final interpretation should still be read manually.