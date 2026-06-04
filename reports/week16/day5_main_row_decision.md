# Week 16 - Day 5 Main Row Decision

## Decision
- selected_main_row: `soft_support_fuzzy_retrieval_main`
- selected_source_variant: `soft_support_fuzzy_retrieval_tight`

## Why selected
- ranking-like proxy is preserved relative to soft_support_raw
- direct shortcut evidence is reduced more than in v1
- candidate coverage stays preserved
- this variant provides the cleanest overall trade-off on valid

## Ranked candidates
[
  {
    "variant_name": "soft_support_fuzzy_retrieval_tight",
    "eligible": true,
    "metrics": {
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
      "avg_query_touch_count": 8.174,
      "avg_non_direct_query_touch_count": 5.122,
      "worsened_vs_soft_support": 0,
      "improved_vs_soft_support": 0,
      "selected_subgraph_identical_to_v1_rate": 0.176
    },
    "selection_features": {
      "shortcut_gain_vs_soft_support": 0.079239,
      "subgraph_size_gain_vs_soft_support": 27.894,
      "mrr_delta_vs_soft_support": 0.0,
      "redundancy_count": 0,
      "anchor_caution_count": 13
    }
  },
  {
    "variant_name": "soft_support_fuzzy_retrieval_directplus",
    "eligible": true,
    "metrics": {
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
      "avg_query_touch_count": 9.73,
      "avg_non_direct_query_touch_count": 5.162,
      "worsened_vs_soft_support": 0,
      "improved_vs_soft_support": 0,
      "selected_subgraph_identical_to_v1_rate": 0.746
    },
    "selection_features": {
      "shortcut_gain_vs_soft_support": 0.055262,
      "subgraph_size_gain_vs_soft_support": 23.736,
      "mrr_delta_vs_soft_support": 0.0,
      "redundancy_count": 373,
      "anchor_caution_count": 0
    }
  },
  {
    "variant_name": "soft_support_fuzzy_retrieval_v1",
    "eligible": true,
    "metrics": {
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
      "avg_query_touch_count": 9.73,
      "avg_non_direct_query_touch_count": 5.162,
      "worsened_vs_soft_support": 0,
      "improved_vs_soft_support": 0,
      "selected_subgraph_identical_to_v1_rate": 1.0
    },
    "selection_features": {
      "shortcut_gain_vs_soft_support": 0.055262,
      "subgraph_size_gain_vs_soft_support": 23.736,
      "mrr_delta_vs_soft_support": 0.0,
      "redundancy_count": 0,
      "anchor_caution_count": 0
    }
  }
]

## Selected metrics
{
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
}

## Delta vs soft_support_raw
{
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
}

## Case review support
{
  "tight_same_rank_cleaner_than_v1": 217,
  "tight_preserved_backbone_gain": 80,
  "tight_anchor_caution_same_rank": 13,
  "directplus_redundant_vs_v1": 373,
  "raw_bottleneck_failure": 399
}