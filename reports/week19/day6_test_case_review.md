# Day 6 — Test case review shortlist

- status: **BUILT**

## 1. Bucket counts
- backbone_to_retrieval_improved_available: `100`
- ontology_failure_retrieval_success_available: `114`
- same_rank_cleaner_graph_available: `298`
- encoder_appendix_deferred_available: `1`

## 2. backbone_to_retrieval_improved
- row=348 | query=`lymphosarcoma` | gold=`Vincristine` | backbone_rank=16 -> retrieval_rank=2
- row=56 | query=`lymphoma` | gold=`Vincristine` | backbone_rank=17 -> retrieval_rank=3
- row=381 | query=`rheumatoid arthritis` | gold=`Methotrexate` | backbone_rank=19 -> retrieval_rank=8
- row=223 | query=`autoimmune disease` | gold=`Prednisone` | backbone_rank=14 -> retrieval_rank=4
- row=476 | query=`autoimmune hemolytic anemia` | gold=`Prednisone` | backbone_rank=14 -> retrieval_rank=4

## 3. ontology_failure_retrieval_success
- row=22 | query=`seborrheic dermatitis` | gold=`Cortisone acetate` | ontology_rank=21 -> retrieval_rank=1
- row=41 | query=`acute lymphoblastic leukemia (disease)` | gold=`Dexamethasone` | ontology_rank=21 -> retrieval_rank=1
- row=48 | query=`acquired angioedema` | gold=`Betamethasone` | ontology_rank=21 -> retrieval_rank=1
- row=50 | query=`primary cutaneous T-cell lymphoma` | gold=`Hydrocortisone` | ontology_rank=21 -> retrieval_rank=1
- row=102 | query=`allergic asthma` | gold=`Cortisone acetate` | ontology_rank=21 -> retrieval_rank=1

## 4. same_rank_cleaner_graph
- row=282 | query=`chronic tubotympanic suppurative otitis media` | gold=`Norfloxacin` | soft_rank=4 = retrieval_rank=4 | subgraph_shrink=38 | shortcut_reduction=19
- row=0 | query=`lung abscess (disease)` | gold=`Ticarcillin` | soft_rank=21 = retrieval_rank=21 | subgraph_shrink=34 | shortcut_reduction=19
- row=192 | query=`lung abscess (disease)` | gold=`Cefoxitin` | soft_rank=21 = retrieval_rank=21 | subgraph_shrink=34 | shortcut_reduction=19
- row=12 | query=`rat-bite fever` | gold=`Procaine benzylpenicillin` | soft_rank=21 = retrieval_rank=21 | subgraph_shrink=33 | shortcut_reduction=19
- row=187 | query=`cholera` | gold=`Fusidic acid` | soft_rank=1 = retrieval_rank=1 | subgraph_shrink=33 | shortcut_reduction=9

## 5. encoder_appendix_deferred
- Encoder remains appendix-only on locked test; no promoted encoder row is shortlisted.

## 6. Day-6 conclusion
Built test-side shortlist for main-paper interpretation and appendix. The shortlist now separates ranking improvement cases, ontology failure recovery cases, and same-rank cleaner-graph cases.
