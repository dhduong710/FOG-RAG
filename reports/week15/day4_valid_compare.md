# Week 15 - Day 4 Valid Compare v1

## Main rows
- backbone_raw
- soft_support_raw
- soft_support_fuzzy_retrieval_v1

## backbone_raw
{
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
  "avg_top5_contra_rate": 0.0108
}

## soft_support_raw
{
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
  "avg_top5_contra_rate": 0.0092
}

## soft_support_fuzzy_retrieval_v1
{
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
  "avg_top5_contra_rate": 0.0092
}

## Delta: fuzzy vs backbone
{
  "mrr_like": 0.043841,
  "hits1_like": 0.032,
  "hits3_like": 0.088,
  "hits10_like": 0.024,
  "avg_gold_rank": -0.7,
  "direct_shortcut_path_rate": -0.055262,
  "avg_top5_direct_link_rate": -0.2336
}

## Delta: fuzzy vs soft_support
{
  "mrr_like": 0.0,
  "hits1_like": 0.0,
  "hits3_like": 0.0,
  "hits10_like": 0.0,
  "avg_gold_rank": 0.0,
  "direct_shortcut_path_rate": -0.055262,
  "avg_top5_direct_link_rate": 0.0
}

## Case-level
{
  "improved_vs_backbone": 80,
  "worsened_vs_backbone": 0,
  "improved_vs_soft_support": 0,
  "worsened_vs_soft_support": 0
}