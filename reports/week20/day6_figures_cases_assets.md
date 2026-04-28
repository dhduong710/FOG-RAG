# Day 6 — Paper-ready tables, figures, and case assets

- status: **BUILT**

## 1. Tables
- locked_test_main: CSV=`/home/duong/code/FOG-RAG/results/week20/paper_assets/table1_locked_test_main.csv`, LaTeX=`/home/duong/code/FOG-RAG/results/week20/paper_assets/table1_locked_test_main.tex`
- e2e_confirmation: CSV=`/home/duong/code/FOG-RAG/results/week20/paper_assets/table2_e2e_confirmation.csv`, LaTeX=`/home/duong/code/FOG-RAG/results/week20/paper_assets/table2_e2e_confirmation.tex`
- e2e_ablation: CSV=`/home/duong/code/FOG-RAG/results/week20/paper_assets/table3_e2e_ablation.csv`, LaTeX=`/home/duong/code/FOG-RAG/results/week20/paper_assets/table3_e2e_ablation.tex`
- graph_package: CSV=`/home/duong/code/FOG-RAG/results/week20/paper_assets/table4_graph_package.csv`, LaTeX=`/home/duong/code/FOG-RAG/results/week20/paper_assets/table4_graph_package.tex`

## 2. Figures
- fig1_pipeline: FOG-RAG / Novelty 2 pipeline overview | type=`diagram`
- fig2_candidate_vs_e2e_mrr: Candidate-ceiling versus E2E reviewer-safe MRR@20 | type=`bar_chart`
- fig3_subgraph_size_reduction: Evidence subgraph size reduction | type=`bar_chart`
- fig4_case_study: Representative case study | type=`case_study_panel`

## 3. Case pack
- main_paper/backbone_to_retrieval_improved: `3` cases
- main_paper/ontology_failure_retrieval_success: `3` cases
- main_paper/same_rank_cleaner_graph: `3` cases
- appendix/same_rank_cleaner_graph_extra: `5` cases
- appendix/encoder_appendix_deferred: `1` cases

## 4. Paper-facing decision
- main_row: `soft_support_fuzzy_retrieval_main`
- decision_note: Keep retrieval_main as the paper-facing main row: soft support provides the main ranking gain over backbone, while retrieval_main preserves candidate/E2E performance and substantially reduces the evidence subgraph.

## 5. Day-6 conclusion
Paper-ready tables, figure manifest, case pack, and interpretation snippets have been generated. Day 7 should close Week 20 and decide whether to move to full paper writing or run a small robustness package.
