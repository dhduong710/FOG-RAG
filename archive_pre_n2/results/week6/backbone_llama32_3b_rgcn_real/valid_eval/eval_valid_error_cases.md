# Week 5 - Day 6 Error Case Report

## Overall metrics
- mrr: `0.83680612`
- hits1: `0.804`
- hits3: `0.808`
- hits10: `0.946`
- num_examples: `500`
- split: `valid`

## Category counts
- hit@1: `402`
- prediction_in_candidate_but_not_top: `97`
- prediction_not_in_candidate: `1`

## 5 best cases
```json
[
  {
    "query_entity": "leukemia, lymphocytic, susceptibility to",
    "target": "Cortisone acetate",
    "pred": "Cortisone acetate",
    "pred_rank": 1,
    "gold_rank_before_llm": 20,
    "candidate_size": 20,
    "subgraph_size": 68,
    "top5_candidates": [
      "Cholestyramine",
      "Neratinib",
      "Talaporfin",
      "Infliximab",
      "Levomethadone"
    ],
    "category": "hit@1"
  },
  {
    "query_entity": "streptococcal infection",
    "target": "Cefixime",
    "pred": "Cefixime",
    "pred_rank": 1,
    "gold_rank_before_llm": 20,
    "candidate_size": 20,
    "subgraph_size": 88,
    "top5_candidates": [
      "Azathioprine",
      "Adenosine phosphate",
      "Bexarotene",
      "Tofacitinib",
      "Arsenic trioxide"
    ],
    "category": "hit@1"
  },
  {
    "query_entity": "dyspepsia",
    "target": "Magnesium trisilicate",
    "pred": "Magnesium trisilicate",
    "pred_rank": 1,
    "gold_rank_before_llm": 20,
    "candidate_size": 20,
    "subgraph_size": 89,
    "top5_candidates": [
      "Azathioprine",
      "Bexarotene",
      "Tofacitinib",
      "Arsenic trioxide",
      "Podofilox"
    ],
    "category": "hit@1"
  },
  {
    "query_entity": "basal cell carcinoma",
    "target": "Vismodegib",
    "pred": "Vismodegib",
    "pred_rank": 1,
    "gold_rank_before_llm": 20,
    "candidate_size": 20,
    "subgraph_size": 64,
    "top5_candidates": [
      "Cholestyramine",
      "Neratinib",
      "Talaporfin",
      "Infliximab",
      "Levomethadone"
    ],
    "category": "hit@1"
  },
  {
    "query_entity": "obsessive-compulsive disorder",
    "target": "Fluoxetine",
    "pred": "Fluoxetine",
    "pred_rank": 1,
    "gold_rank_before_llm": 20,
    "candidate_size": 20,
    "subgraph_size": 81,
    "top5_candidates": [
      "Cholestyramine",
      "Neratinib",
      "Talaporfin",
      "Levomethadone",
      "Infliximab"
    ],
    "category": "hit@1"
  }
]
```

## 5 worst cases
```json
[
  {
    "query_entity": "folic acid deficiency anemia",
    "target": "Hematin",
    "pred": "folic acid",
    "pred_rank": 21,
    "gold_rank_before_llm": 20,
    "candidate_size": 20,
    "subgraph_size": 89,
    "top5_candidates": [
      "Acenocoumarol",
      "Omacetaxine mepesuccinate",
      "Mebendazole",
      "Azathioprine",
      "Oseltamivir"
    ],
    "category": "prediction_not_in_candidate"
  },
  {
    "query_entity": "mycosis fungoides and variants",
    "target": "Methotrexate",
    "pred": "Ingenol mebutate",
    "pred_rank": 19,
    "gold_rank_before_llm": 20,
    "candidate_size": 20,
    "subgraph_size": 73,
    "top5_candidates": [
      "Acenocoumarol",
      "Omacetaxine mepesuccinate",
      "Mebendazole",
      "Azathioprine",
      "Oseltamivir"
    ],
    "category": "prediction_in_candidate_but_not_top"
  },
  {
    "query_entity": "superficial multifocal basal cell carcinoma",
    "target": "Fluorouracil",
    "pred": "Podofilox",
    "pred_rank": 19,
    "gold_rank_before_llm": 20,
    "candidate_size": 20,
    "subgraph_size": 99,
    "top5_candidates": [
      "Acenocoumarol",
      "Omacetaxine mepesuccinate",
      "Beraprost",
      "Albendazole",
      "Oseltamivir"
    ],
    "category": "prediction_in_candidate_but_not_top"
  },
  {
    "query_entity": "mycosis fungoides and variants",
    "target": "Cyclophosphamide",
    "pred": "Ingenol mebutate",
    "pred_rank": 19,
    "gold_rank_before_llm": 20,
    "candidate_size": 20,
    "subgraph_size": 73,
    "top5_candidates": [
      "Acenocoumarol",
      "Omacetaxine mepesuccinate",
      "Mebendazole",
      "Azathioprine",
      "Oseltamivir"
    ],
    "category": "prediction_in_candidate_but_not_top"
  },
  {
    "query_entity": "acute myeloid leukemia with CEBPA somatic mutations",
    "target": "Gemtuzumab ozogamicin",
    "pred": "Gemcitabine",
    "pred_rank": 19,
    "gold_rank_before_llm": 20,
    "candidate_size": 20,
    "subgraph_size": 65,
    "top5_candidates": [
      "Cholestyramine",
      "Neratinib",
      "Talaporfin",
      "Infliximab",
      "Levomethadone"
    ],
    "category": "prediction_in_candidate_but_not_top"
  }
]
```

## Notes
- `prediction_not_in_candidate` often suggests reranking/generation drift.
- `prediction_in_candidate_but_not_top` often suggests candidate quality or graph signal may be insufficient.
- This report is mechanical; final interpretation should still be read manually.