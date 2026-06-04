# Week 16 - Day 3 Valid Sweep Compare

## Baselines
{
  "backbone_raw": {
    "mrr_like": 0.053803,
    "hits1_like": 0.024,
    "hits3_like": 0.046,
    "hits10_like": 0.158,
    "avg_gold_rank": 18.376,
    "avg_subgraph_size": 60.45,
    "avg_triple_score": null,
    "direct_shortcut_path_rate": 0.184775,
    "contradiction_path_rate": 0.005681,
    "candidate_coverage_preserved_rate": 1.0,
    "avg_top5_direct_link_rate": 0.2408,
    "avg_top5_evidence_positive_rate": 0.9396,
    "avg_top5_contra_rate": 0.0108,
    "avg_query_touch_count": 23.854,
    "avg_non_direct_query_touch_count": 13.85
  },
  "soft_support_raw": {
    "mrr_like": 0.097644,
    "hits1_like": 0.056,
    "hits3_like": 0.134,
    "hits10_like": 0.182,
    "avg_gold_rank": 17.676,
    "avg_subgraph_size": 60.45,
    "avg_triple_score": null,
    "direct_shortcut_path_rate": 0.184775,
    "contradiction_path_rate": 0.005681,
    "candidate_coverage_preserved_rate": 1.0,
    "avg_top5_direct_link_rate": 0.0072,
    "avg_top5_evidence_positive_rate": 1.0,
    "avg_top5_contra_rate": 0.0092,
    "avg_query_touch_count": 23.854,
    "avg_non_direct_query_touch_count": 13.85
  }
}

## Retrieval variants
{
  "soft_support_fuzzy_retrieval_v1": {
    "mrr_like": 0.097644,
    "hits1_like": 0.056,
    "hits3_like": 0.134,
    "hits10_like": 0.182,
    "avg_gold_rank": 17.676,
    "avg_subgraph_size": 36.714,
    "avg_triple_score": 0.440709,
    "direct_shortcut_path_rate": 0.129513,
    "contradiction_path_rate": 0.006121,
    "candidate_coverage_preserved_rate": 1.0,
    "avg_top5_direct_link_rate": 0.0072,
    "avg_top5_evidence_positive_rate": 1.0,
    "avg_top5_contra_rate": 0.0092,
    "avg_query_touch_count": 9.73,
    "avg_non_direct_query_touch_count": 5.162,
    "improved_vs_backbone": 80,
    "worsened_vs_backbone": 0,
    "improved_vs_soft_support": 0,
    "worsened_vs_soft_support": 0,
    "selected_subgraph_identical_to_v1_rate": 1.0
  },
  "soft_support_fuzzy_retrieval_tight": {
    "mrr_like": 0.097644,
    "hits1_like": 0.056,
    "hits3_like": 0.134,
    "hits10_like": 0.182,
    "avg_gold_rank": 17.676,
    "avg_subgraph_size": 32.556,
    "avg_triple_score": 0.499203,
    "direct_shortcut_path_rate": 0.105536,
    "contradiction_path_rate": 0.006804,
    "candidate_coverage_preserved_rate": 1.0,
    "avg_top5_direct_link_rate": 0.0072,
    "avg_top5_evidence_positive_rate": 1.0,
    "avg_top5_contra_rate": 0.0092,
    "avg_query_touch_count": 8.174,
    "avg_non_direct_query_touch_count": 5.122,
    "improved_vs_backbone": 80,
    "worsened_vs_backbone": 0,
    "improved_vs_soft_support": 0,
    "worsened_vs_soft_support": 0,
    "selected_subgraph_identical_to_v1_rate": 0.176
  },
  "soft_support_fuzzy_retrieval_directplus": {
    "mrr_like": 0.097644,
    "hits1_like": 0.056,
    "hits3_like": 0.134,
    "hits10_like": 0.182,
    "avg_gold_rank": 17.676,
    "avg_subgraph_size": 36.714,
    "avg_triple_score": 0.414807,
    "direct_shortcut_path_rate": 0.129513,
    "contradiction_path_rate": 0.006121,
    "candidate_coverage_preserved_rate": 1.0,
    "avg_top5_direct_link_rate": 0.0072,
    "avg_top5_evidence_positive_rate": 1.0,
    "avg_top5_contra_rate": 0.0092,
    "avg_query_touch_count": 9.73,
    "avg_non_direct_query_touch_count": 5.162,
    "improved_vs_backbone": 80,
    "worsened_vs_backbone": 0,
    "improved_vs_soft_support": 0,
    "worsened_vs_soft_support": 0,
    "selected_subgraph_identical_to_v1_rate": 0.746
  }
}

## Delta vs soft_support_raw
{
  "soft_support_fuzzy_retrieval_v1": {
    "mrr_like": 0.0,
    "hits1_like": 0.0,
    "hits3_like": 0.0,
    "hits10_like": 0.0,
    "avg_gold_rank": 0.0,
    "avg_subgraph_size": -23.736,
    "direct_shortcut_path_rate": -0.055262,
    "avg_top5_direct_link_rate": 0.0,
    "avg_query_touch_count": -14.124,
    "avg_non_direct_query_touch_count": -8.688
  },
  "soft_support_fuzzy_retrieval_tight": {
    "mrr_like": 0.0,
    "hits1_like": 0.0,
    "hits3_like": 0.0,
    "hits10_like": 0.0,
    "avg_gold_rank": 0.0,
    "avg_subgraph_size": -27.894,
    "direct_shortcut_path_rate": -0.079239,
    "avg_top5_direct_link_rate": 0.0,
    "avg_query_touch_count": -15.68,
    "avg_non_direct_query_touch_count": -8.728
  },
  "soft_support_fuzzy_retrieval_directplus": {
    "mrr_like": 0.0,
    "hits1_like": 0.0,
    "hits3_like": 0.0,
    "hits10_like": 0.0,
    "avg_gold_rank": 0.0,
    "avg_subgraph_size": -23.736,
    "direct_shortcut_path_rate": -0.055262,
    "avg_top5_direct_link_rate": 0.0,
    "avg_query_touch_count": -14.124,
    "avg_non_direct_query_touch_count": -8.688
  }
}

## Delta vs v1
{
  "soft_support_fuzzy_retrieval_tight": {
    "mrr_like": 0.0,
    "hits1_like": 0.0,
    "hits3_like": 0.0,
    "hits10_like": 0.0,
    "avg_gold_rank": 0.0,
    "avg_subgraph_size": -4.158,
    "direct_shortcut_path_rate": -0.023977,
    "avg_top5_direct_link_rate": 0.0,
    "avg_query_touch_count": -1.556,
    "avg_non_direct_query_touch_count": -0.04
  },
  "soft_support_fuzzy_retrieval_directplus": {
    "mrr_like": 0.0,
    "hits1_like": 0.0,
    "hits3_like": 0.0,
    "hits10_like": 0.0,
    "avg_gold_rank": 0.0,
    "avg_subgraph_size": 0.0,
    "direct_shortcut_path_rate": 0.0,
    "avg_top5_direct_link_rate": 0.0,
    "avg_query_touch_count": 0.0,
    "avg_non_direct_query_touch_count": 0.0
  }
}

## Sweep summary
{
  "week": 16,
  "day": 3,
  "retrieval_variants": [
    "soft_support_fuzzy_retrieval_v1",
    "soft_support_fuzzy_retrieval_tight",
    "soft_support_fuzzy_retrieval_directplus"
  ],
  "evidence_cleanliness_order": [
    {
      "variant_name": "soft_support_fuzzy_retrieval_tight",
      "direct_shortcut_path_rate": 0.105536,
      "avg_subgraph_size": 32.556,
      "candidate_coverage_preserved_rate": 1.0
    },
    {
      "variant_name": "soft_support_fuzzy_retrieval_v1",
      "direct_shortcut_path_rate": 0.129513,
      "avg_subgraph_size": 36.714,
      "candidate_coverage_preserved_rate": 1.0
    },
    {
      "variant_name": "soft_support_fuzzy_retrieval_directplus",
      "direct_shortcut_path_rate": 0.129513,
      "avg_subgraph_size": 36.714,
      "candidate_coverage_preserved_rate": 1.0
    }
  ],
  "ranking_proxy_order": [
    {
      "variant_name": "soft_support_fuzzy_retrieval_v1",
      "mrr_like": 0.097644,
      "avg_gold_rank": 17.676,
      "worsened_vs_soft_support": 0
    },
    {
      "variant_name": "soft_support_fuzzy_retrieval_tight",
      "mrr_like": 0.097644,
      "avg_gold_rank": 17.676,
      "worsened_vs_soft_support": 0
    },
    {
      "variant_name": "soft_support_fuzzy_retrieval_directplus",
      "mrr_like": 0.097644,
      "avg_gold_rank": 17.676,
      "worsened_vs_soft_support": 0
    }
  ],
  "redundancy_check": {
    "soft_support_fuzzy_retrieval_v1": 1.0,
    "soft_support_fuzzy_retrieval_tight": 0.176,
    "soft_support_fuzzy_retrieval_directplus": 0.746
  },
  "provisional_read": [
    "A strong main-row candidate should reduce shortcut-heavy evidence more than v1 without introducing worsened_vs_soft_support.",
    "If a variant is nearly identical to v1, it should not be kept as a distinct candidate.",
    "If tight wins on evidence cleanliness but clearly hurts ranking proxy, it may remain a supporting row rather than the main row."
  ]
}