# Week 25 Day 5  Small-Noise Robustness

- Decision: **NOISE_ROBUSTNESS_READY**
- Created at: `2026-05-02T04:45:22`
- Main row: **retrieval_main / N0_no_noise**
- Evaluation: candidate/retrieval-level robustness, no LLM E2E required
- Policy: reviewer-safe RR@20

## VALID summary

| Variant | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Same top1 | Rank-change | Avg rank shift | Avg graph | Cand coverage | Graph Jaccard | � MRR vs N0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| N0_no_noise | 0.202 | 0.097644 | 0.056 | 0.134 | 0.182 | 1.0 | 0.0 | 0.0 | 32.556 | 0.7845 | 1.0 | 0.0 |
| N1_support_score_noise_seed1 | 0.202 | 0.058922 | 0.02 | 0.066 | 0.174 | 0.084 | 0.182 | 0.728 | 32.556 | 0.7845 | 1.0 | -0.038722 |
| N2_support_score_noise_seed2 | 0.202 | 0.064638 | 0.022 | 0.066 | 0.19 | 0.08 | 0.182 | 0.748 | 32.556 | 0.7845 | 1.0 | -0.033006 |
| N3_support_score_noise_seed3 | 0.202 | 0.065056 | 0.026 | 0.07 | 0.182 | 0.076 | 0.184 | 0.788 | 32.556 | 0.7845 | 1.0 | -0.032588 |
| N4_subgraph_edge_dropout_5_seed1 | 0.202 | 0.097644 | 0.056 | 0.134 | 0.182 | 1.0 | 0.0 | 0.0 | 30.734 | 0.7845 | 0.944181 | 0.0 |
| N5_subgraph_edge_dropout_5_seed2 | 0.202 | 0.097644 | 0.056 | 0.134 | 0.182 | 1.0 | 0.0 | 0.0 | 30.734 | 0.7845 | 0.944181 | 0.0 |
| N6_subgraph_edge_dropout_5_seed3 | 0.202 | 0.097644 | 0.056 | 0.134 | 0.182 | 1.0 | 0.0 | 0.0 | 30.734 | 0.7845 | 0.944181 | 0.0 |

## TEST summary

| Variant | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Same top1 | Rank-change | Avg rank shift | Avg graph | Cand coverage | Graph Jaccard | � MRR vs N0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| N0_no_noise | 0.24 | 0.125326 | 0.072 | 0.166 | 0.222 | 1.0 | 0.0 | 0.0 | 32.34 | 0.7831 | 1.0 | 0.0 |
| N1_support_score_noise_seed1 | 0.24 | 0.077903 | 0.03 | 0.092 | 0.22 | 0.086 | 0.206 | 0.83 | 32.34 | 0.7831 | 1.0 | -0.047423 |
| N2_support_score_noise_seed2 | 0.24 | 0.077914 | 0.032 | 0.088 | 0.216 | 0.096 | 0.214 | 0.748 | 32.34 | 0.7831 | 1.0 | -0.047412 |
| N3_support_score_noise_seed3 | 0.24 | 0.076251 | 0.026 | 0.092 | 0.22 | 0.086 | 0.214 | 0.816 | 32.34 | 0.7831 | 1.0 | -0.049075 |
| N4_subgraph_edge_dropout_5_seed1 | 0.24 | 0.125326 | 0.072 | 0.166 | 0.222 | 1.0 | 0.0 | 0.0 | 30.49 | 0.7831 | 0.942933 | 0.0 |
| N5_subgraph_edge_dropout_5_seed2 | 0.24 | 0.125326 | 0.072 | 0.166 | 0.222 | 1.0 | 0.0 | 0.0 | 30.49 | 0.7831 | 0.942933 | 0.0 |
| N6_subgraph_edge_dropout_5_seed3 | 0.24 | 0.125326 | 0.072 | 0.166 | 0.222 | 1.0 | 0.0 | 0.0 | 30.49 | 0.7831 | 0.942933 | 0.0 |

## Interpretation guide

- Support-score noise tests whether small perturbations in soft evidence scores destabilize candidate ordering.
- Subgraph dropout tests whether the selected evidence package remains structurally usable under light edge loss.
- If MRR@20 changes only slightly and coverage remains stable, FOG-RAG can be described as robust to small perturbations.
- These results are appendix robustness evidence and must not replace the frozen Week 24 main result.

## Case samples

### valid_N1_support_score_noise_seed1
| idx | query | gold | rank N0 | rank var | rank delta | top1 N0 | top1 var | graph N0 | graph var | Jaccard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 350 | primary non-gestational choriocarcinoma of ovary | Hydroxyurea | 16 | 2 | -14 | Cortisone acetate | Hydrocortisone acetate | 32 | 32 | 1.0 |
| 435 | urinary bladder neoplasm | Thiotepa | 16 | 6 | -10 | Cortisone acetate | Bleomycin | 34 | 34 | 1.0 |
| 393 | punctate epithelial keratoconjunctivitis | Dexamethasone | 3 | 13 | 10 | Fusidic acid | Fusidic acid | 28 | 28 | 1.0 |
| 110 | Klebsiella pneumonia | Norfloxacin | 3 | 12 | 9 | Fusidic acid | Methylprednisolone | 29 | 29 | 1.0 |
| 117 | Crohn's colitis | Prednisolone | 1 | 10 | 9 | Prednisolone | Prednisone | 31 | 31 | 1.0 |
| 123 | urinary bladder carcinoma | Thiotepa | 16 | 7 | -9 | Dexamethasone | Hydrocortisone acetate | 34 | 34 | 1.0 |
| 151 | therapy related acute myeloid leukemia and myelodysplastic syndrome | Doxorubicin | 10 | 1 | -9 | Cortisone acetate | Doxorubicin | 32 | 32 | 1.0 |
| 221 | Crohn's colitis | Prednisone | 2 | 11 | 9 | Prednisolone | Doxorubicin | 31 | 31 | 1.0 |

### valid_N2_support_score_noise_seed2
| idx | query | gold | rank N0 | rank var | rank delta | top1 N0 | top1 var | graph N0 | graph var | Jaccard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 277 | ovarian carcinosarcoma | Hydroxyurea | 16 | 1 | -15 | Cortisone acetate | Hydroxyurea | 32 | 32 | 1.0 |
| 483 | ovarian clear cell adenocarcinoma | Hydroxyurea | 16 | 1 | -15 | Cortisone acetate | Hydroxyurea | 32 | 32 | 1.0 |
| 350 | primary non-gestational choriocarcinoma of ovary | Hydroxyurea | 16 | 2 | -14 | Cortisone acetate | Prednisone | 32 | 32 | 1.0 |
| 406 | latent syphilis | Benzylpenicillin | 15 | 1 | -14 | Fusidic acid | Benzylpenicillin | 34 | 34 | 1.0 |
| 123 | urinary bladder carcinoma | Thiotepa | 16 | 3 | -13 | Dexamethasone | Triamcinolone | 34 | 34 | 1.0 |
| 30 | ovarian mucinous adenocarcinoma | Hydroxyurea | 16 | 5 | -11 | Cortisone acetate | Prednisolone | 32 | 32 | 1.0 |
| 264 | sickle cell anemia | Hydroxyurea | 18 | 7 | -11 | Cortisone acetate | Hydrocortisone | 36 | 36 | 1.0 |
| 77 | intrinsic asthma | Hydrocortisone | 1 | 11 | 10 | Hydrocortisone | Doxorubicin | 30 | 30 | 1.0 |

### valid_N3_support_score_noise_seed3
| idx | query | gold | rank N0 | rank var | rank delta | top1 N0 | top1 var | graph N0 | graph var | Jaccard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 30 | ovarian mucinous adenocarcinoma | Hydroxyurea | 16 | 1 | -15 | Cortisone acetate | Hydroxyurea | 32 | 32 | 1.0 |
| 156 | theca steroid-producing cell malignant tumor of ovary, not further specified | Thiotepa | 14 | 1 | -13 | Cortisone acetate | Thiotepa | 32 | 32 | 1.0 |
| 305 | primary central nervous system lymphoma | Dexamethasone | 1 | 12 | 11 | Dexamethasone | Vinblastine | 35 | 35 | 1.0 |
| 123 | urinary bladder carcinoma | Thiotepa | 16 | 6 | -10 | Dexamethasone | Prednisolone | 34 | 34 | 1.0 |
| 483 | ovarian clear cell adenocarcinoma | Hydroxyurea | 16 | 6 | -10 | Cortisone acetate | Mechlorethamine | 32 | 32 | 1.0 |
| 25 | aspiration pneumonia (disease) | Cortisone acetate | 1 | 9 | 8 | Cortisone acetate | Fusidic acid | 32 | 32 | 1.0 |
| 38 | dysentery | Norfloxacin | 3 | 11 | 8 | Fusidic acid | Hydrocortisone acetate | 35 | 35 | 1.0 |
| 77 | intrinsic asthma | Hydrocortisone | 1 | 9 | 8 | Hydrocortisone | Doxorubicin | 30 | 30 | 1.0 |

### valid_N4_subgraph_edge_dropout_5_seed1
| idx | query | gold | rank N0 | rank var | rank delta | top1 N0 | top1 var | graph N0 | graph var | Jaccard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 17 | acquired thrombocytopenia | Cortisone acetate | 1 | 1 | 0 | Cortisone acetate | Cortisone acetate | 30 | 28 | 0.933333 |
| 19 | prostate cancer | Estramustine | 21 | 21 | 0 | Cortisone acetate | Cortisone acetate | 30 | 28 | 0.933333 |
| 26 | autoimmune thrombocytopenic | Romiplostim | 21 | 21 | 0 | Fusidic acid | Fusidic acid | 30 | 28 | 0.933333 |
| 39 | acute myeloid leukemia with minimal differentiation | Gilteritinib | 21 | 21 | 0 | Cortisone acetate | Cortisone acetate | 30 | 28 | 0.933333 |
| 48 | brain edema | Mannitol | 21 | 21 | 0 | Fusidic acid | Fusidic acid | 30 | 28 | 0.933333 |
| 59 | discoid lupus erythematosus | Amcinonide | 21 | 21 | 0 | Triamcinolone | Triamcinolone | 30 | 28 | 0.933333 |
| 62 | eye disease | Betamethasone | 2 | 2 | 0 | Fusidic acid | Fusidic acid | 30 | 28 | 0.933333 |
| 63 | spondyloarthropathy, susceptibility to | Acemetacin | 21 | 21 | 0 | Cortisone acetate | Cortisone acetate | 30 | 28 | 0.933333 |

### valid_N5_subgraph_edge_dropout_5_seed2
| idx | query | gold | rank N0 | rank var | rank delta | top1 N0 | top1 var | graph N0 | graph var | Jaccard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 17 | acquired thrombocytopenia | Cortisone acetate | 1 | 1 | 0 | Cortisone acetate | Cortisone acetate | 30 | 28 | 0.933333 |
| 19 | prostate cancer | Estramustine | 21 | 21 | 0 | Cortisone acetate | Cortisone acetate | 30 | 28 | 0.933333 |
| 26 | autoimmune thrombocytopenic | Romiplostim | 21 | 21 | 0 | Fusidic acid | Fusidic acid | 30 | 28 | 0.933333 |
| 39 | acute myeloid leukemia with minimal differentiation | Gilteritinib | 21 | 21 | 0 | Cortisone acetate | Cortisone acetate | 30 | 28 | 0.933333 |
| 48 | brain edema | Mannitol | 21 | 21 | 0 | Fusidic acid | Fusidic acid | 30 | 28 | 0.933333 |
| 59 | discoid lupus erythematosus | Amcinonide | 21 | 21 | 0 | Triamcinolone | Triamcinolone | 30 | 28 | 0.933333 |
| 62 | eye disease | Betamethasone | 2 | 2 | 0 | Fusidic acid | Fusidic acid | 30 | 28 | 0.933333 |
| 63 | spondyloarthropathy, susceptibility to | Acemetacin | 21 | 21 | 0 | Cortisone acetate | Cortisone acetate | 30 | 28 | 0.933333 |

### valid_N6_subgraph_edge_dropout_5_seed3
| idx | query | gold | rank N0 | rank var | rank delta | top1 N0 | top1 var | graph N0 | graph var | Jaccard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 17 | acquired thrombocytopenia | Cortisone acetate | 1 | 1 | 0 | Cortisone acetate | Cortisone acetate | 30 | 28 | 0.933333 |
| 19 | prostate cancer | Estramustine | 21 | 21 | 0 | Cortisone acetate | Cortisone acetate | 30 | 28 | 0.933333 |
| 26 | autoimmune thrombocytopenic | Romiplostim | 21 | 21 | 0 | Fusidic acid | Fusidic acid | 30 | 28 | 0.933333 |
| 39 | acute myeloid leukemia with minimal differentiation | Gilteritinib | 21 | 21 | 0 | Cortisone acetate | Cortisone acetate | 30 | 28 | 0.933333 |
| 48 | brain edema | Mannitol | 21 | 21 | 0 | Fusidic acid | Fusidic acid | 30 | 28 | 0.933333 |
| 59 | discoid lupus erythematosus | Amcinonide | 21 | 21 | 0 | Triamcinolone | Triamcinolone | 30 | 28 | 0.933333 |
| 62 | eye disease | Betamethasone | 2 | 2 | 0 | Fusidic acid | Fusidic acid | 30 | 28 | 0.933333 |
| 63 | spondyloarthropathy, susceptibility to | Acemetacin | 21 | 21 | 0 | Cortisone acetate | Cortisone acetate | 30 | 28 | 0.933333 |

### test_N1_support_score_noise_seed1
| idx | query | gold | rank N0 | rank var | rank delta | top1 N0 | top1 var | graph N0 | graph var | Jaccard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 187 | cholera | Fusidic acid | 1 | 11 | 10 | Fusidic acid | Triamcinolone | 35 | 35 | 1.0 |
| 238 | inherited aplastic anemia | Prednisolone | 1 | 11 | 10 | Prednisolone | Hydrocortisone acetate | 31 | 31 | 1.0 |
| 239 | ovarian endometrioid adenocarcinoma | Thiotepa | 14 | 4 | -10 | Cortisone acetate | Hydrocortisone | 32 | 32 | 1.0 |
| 288 | streptococcal pneumonia | Norfloxacin | 11 | 1 | -10 | Cortisone acetate | Norfloxacin | 31 | 31 | 1.0 |
| 9 | spondyloarthropathy | Methylprednisolone | 2 | 11 | 9 | Dexamethasone | Thiotepa | 30 | 30 | 1.0 |
| 459 | iritis (disease) | Dexamethasone | 2 | 11 | 9 | Fusidic acid | Methdilazine | 32 | 32 | 1.0 |
| 80 | allergic asthma | Dexamethasone | 2 | 10 | 8 | Cortisone acetate | Methotrexate | 30 | 30 | 1.0 |
| 148 | idiopathic uveitis | Prednisolone | 4 | 12 | 8 | Fusidic acid | Tetracycline | 31 | 31 | 1.0 |

### test_N2_support_score_noise_seed2
| idx | query | gold | rank N0 | rank var | rank delta | top1 N0 | top1 var | graph N0 | graph var | Jaccard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 102 | allergic asthma | Cortisone acetate | 1 | 13 | 12 | Cortisone acetate | Dexamethasone | 30 | 30 | 1.0 |
| 238 | inherited aplastic anemia | Prednisolone | 1 | 11 | 10 | Prednisolone | Carmustine | 31 | 31 | 1.0 |
| 432 | diffuse large B-cell lymphoma | Vincristine | 13 | 3 | -10 | Cortisone acetate | Hydrocortisone acetate | 35 | 35 | 1.0 |
| 16 | intrinsic asthma | Prednisolone | 3 | 12 | 9 | Hydrocortisone | Carmustine | 30 | 30 | 1.0 |
| 459 | iritis (disease) | Dexamethasone | 2 | 11 | 9 | Fusidic acid | Benzylpenicillin | 32 | 32 | 1.0 |
| 80 | allergic asthma | Dexamethasone | 2 | 10 | 8 | Cortisone acetate | Methotrexate | 30 | 30 | 1.0 |
| 355 | corneal ulcer | Cortisone acetate | 1 | 9 | 8 | Cortisone acetate | Ciprofloxacin | 33 | 33 | 1.0 |
| 455 | Kaposi's sarcoma (disease) | Vinblastine | 13 | 5 | -8 | Cortisone acetate | Fluticasone propionate | 34 | 34 | 1.0 |

### test_N3_support_score_noise_seed3
| idx | query | gold | rank N0 | rank var | rank delta | top1 N0 | top1 var | graph N0 | graph var | Jaccard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 80 | allergic asthma | Dexamethasone | 2 | 13 | 11 | Cortisone acetate | Bleomycin | 30 | 30 | 1.0 |
| 355 | corneal ulcer | Cortisone acetate | 1 | 12 | 11 | Cortisone acetate | Prednisone | 33 | 33 | 1.0 |
| 282 | chronic tubotympanic suppurative otitis media | Norfloxacin | 4 | 14 | 10 | Fusidic acid | Oxytetracycline | 35 | 35 | 1.0 |
| 236 | systemic lupus erythematosus (disease) | Dexamethasone | 1 | 10 | 9 | Dexamethasone | Doxorubicin | 30 | 30 | 1.0 |
| 459 | iritis (disease) | Dexamethasone | 2 | 11 | 9 | Fusidic acid | Methdilazine | 32 | 32 | 1.0 |
| 135 | skin disease | Cortisone acetate | 1 | 9 | 8 | Cortisone acetate | Prednisolone | 35 | 35 | 1.0 |
| 302 | chronic cutaneous lupus erythematosus | Hydrocortisone | 1 | 9 | 8 | Hydrocortisone | Ofloxacin | 31 | 31 | 1.0 |
| 493 | proctitis | Cortisone acetate | 2 | 10 | 8 | Fusidic acid | Betamethasone | 30 | 30 | 1.0 |

### test_N4_subgraph_edge_dropout_5_seed1
| idx | query | gold | rank N0 | rank var | rank delta | top1 N0 | top1 var | graph N0 | graph var | Jaccard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | allergic rhinitis | Hydrocortisone | 3 | 3 | 0 | Fusidic acid | Fusidic acid | 30 | 28 | 0.933333 |
| 3 | blepharoconjunctivitis | Hydrocortisone acetate | 4 | 4 | 0 | Betamethasone | Betamethasone | 30 | 28 | 0.933333 |
| 9 | spondyloarthropathy | Methylprednisolone | 2 | 2 | 0 | Dexamethasone | Dexamethasone | 30 | 28 | 0.933333 |
| 16 | intrinsic asthma | Prednisolone | 3 | 3 | 0 | Hydrocortisone | Hydrocortisone | 30 | 28 | 0.933333 |
| 26 | acute gonococcal endometritis | Cefoxitin | 21 | 21 | 0 | Cortisone acetate | Cortisone acetate | 30 | 28 | 0.933333 |
| 29 | acute gonococcal cervicitis | Alatrofloxacin | 21 | 21 | 0 | Cortisone acetate | Cortisone acetate | 30 | 28 | 0.933333 |
| 48 | acquired angioedema | Betamethasone | 1 | 1 | 0 | Betamethasone | Betamethasone | 30 | 28 | 0.933333 |
| 55 | discoid lupus erythematosus | Chloroquine | 21 | 21 | 0 | Triamcinolone | Triamcinolone | 30 | 28 | 0.933333 |

### test_N5_subgraph_edge_dropout_5_seed2
| idx | query | gold | rank N0 | rank var | rank delta | top1 N0 | top1 var | graph N0 | graph var | Jaccard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | allergic rhinitis | Hydrocortisone | 3 | 3 | 0 | Fusidic acid | Fusidic acid | 30 | 28 | 0.933333 |
| 3 | blepharoconjunctivitis | Hydrocortisone acetate | 4 | 4 | 0 | Betamethasone | Betamethasone | 30 | 28 | 0.933333 |
| 9 | spondyloarthropathy | Methylprednisolone | 2 | 2 | 0 | Dexamethasone | Dexamethasone | 30 | 28 | 0.933333 |
| 16 | intrinsic asthma | Prednisolone | 3 | 3 | 0 | Hydrocortisone | Hydrocortisone | 30 | 28 | 0.933333 |
| 26 | acute gonococcal endometritis | Cefoxitin | 21 | 21 | 0 | Cortisone acetate | Cortisone acetate | 30 | 28 | 0.933333 |
| 29 | acute gonococcal cervicitis | Alatrofloxacin | 21 | 21 | 0 | Cortisone acetate | Cortisone acetate | 30 | 28 | 0.933333 |
| 48 | acquired angioedema | Betamethasone | 1 | 1 | 0 | Betamethasone | Betamethasone | 30 | 28 | 0.933333 |
| 55 | discoid lupus erythematosus | Chloroquine | 21 | 21 | 0 | Triamcinolone | Triamcinolone | 30 | 28 | 0.933333 |

### test_N6_subgraph_edge_dropout_5_seed3
| idx | query | gold | rank N0 | rank var | rank delta | top1 N0 | top1 var | graph N0 | graph var | Jaccard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | allergic rhinitis | Hydrocortisone | 3 | 3 | 0 | Fusidic acid | Fusidic acid | 30 | 28 | 0.933333 |
| 3 | blepharoconjunctivitis | Hydrocortisone acetate | 4 | 4 | 0 | Betamethasone | Betamethasone | 30 | 28 | 0.933333 |
| 9 | spondyloarthropathy | Methylprednisolone | 2 | 2 | 0 | Dexamethasone | Dexamethasone | 30 | 28 | 0.933333 |
| 16 | intrinsic asthma | Prednisolone | 3 | 3 | 0 | Hydrocortisone | Hydrocortisone | 30 | 28 | 0.933333 |
| 26 | acute gonococcal endometritis | Cefoxitin | 21 | 21 | 0 | Cortisone acetate | Cortisone acetate | 30 | 28 | 0.933333 |
| 29 | acute gonococcal cervicitis | Alatrofloxacin | 21 | 21 | 0 | Cortisone acetate | Cortisone acetate | 30 | 28 | 0.933333 |
| 48 | acquired angioedema | Betamethasone | 1 | 1 | 0 | Betamethasone | Betamethasone | 30 | 28 | 0.933333 |
| 55 | discoid lupus erythematosus | Chloroquine | 21 | 21 | 0 | Triamcinolone | Triamcinolone | 30 | 28 | 0.933333 |

## Final decision

**NOISE_ROBUSTNESS_READY**
