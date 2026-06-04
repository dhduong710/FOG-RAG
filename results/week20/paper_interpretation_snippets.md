# Paper interpretation snippets

## Main result wording

Soft-support re-ranking provides the main candidate-level improvement over the raw backbone. On the reviewer-safe E2E evaluation, soft_support_raw improves MRR@20 from 0.04763573 to 0.07467554, with Hits@3 increasing from 0.048 to 0.132 and Hits@10 from 0.178 to 0.218.

The confidence-aware retrieval stage preserves the soft-support ranking and E2E behavior while producing a substantially smaller evidence package. The retrieval-main row obtains E2E MRR@20=0.07468653 and reduces the average subgraph size to 32.34 triples, with candidate coverage preserved at 1.0.

## Ablation wording

Compared with the raw backbone, soft support improves candidate-ceiling MRR@20 by 0.06076335 and E2E MRR@20 by 0.02703981.

Compared with soft support, retrieval main changes candidate-ceiling MRR@20 by 0.0 and E2E MRR@20 by 1.099e-05, while reducing average subgraph size by -27.592 triples.

## Limitation wording

The E2E Hits@1 remains weak because the frozen LLM adapter often generates a plausible candidate rather than the exact gold entity string, even when the gold entity is ranked first in the candidate list. We therefore report both candidate-ceiling and generation-adjusted reviewer-safe metrics.

## Recommended main-paper case buckets

### backbone_to_retrieval_improved
- row=348 | query=lymphosarcoma | gold=Vincristine | backbone_rank=16 | soft_rank=2 | retrieval_rank=2 | subgraph_shrink=20 | shortcut_reduction=15
- row=56 | query=lymphoma | gold=Vincristine | backbone_rank=17 | soft_rank=3 | retrieval_rank=3 | subgraph_shrink=20 | shortcut_reduction=15
- row=381 | query=rheumatoid arthritis | gold=Methotrexate | backbone_rank=19 | soft_rank=8 | retrieval_rank=8 | subgraph_shrink=23 | shortcut_reduction=16

### ontology_failure_retrieval_success
- row=22 | query=seborrheic dermatitis | gold=Cortisone acetate | backbone_rank=1 | soft_rank=1 | retrieval_rank=1 | subgraph_shrink=26 | shortcut_reduction=11
- row=41 | query=acute lymphoblastic leukemia (disease) | gold=Dexamethasone | backbone_rank=2 | soft_rank=1 | retrieval_rank=1 | subgraph_shrink=22 | shortcut_reduction=14
- row=48 | query=acquired angioedema | gold=Betamethasone | backbone_rank=5 | soft_rank=1 | retrieval_rank=1 | subgraph_shrink=24 | shortcut_reduction=18

### same_rank_cleaner_graph
- row=282 | query=chronic tubotympanic suppurative otitis media | gold=Norfloxacin | backbone_rank=4 | soft_rank=4 | retrieval_rank=4 | subgraph_shrink=38 | shortcut_reduction=19
- row=187 | query=cholera | gold=Fusidic acid | backbone_rank=1 | soft_rank=1 | retrieval_rank=1 | subgraph_shrink=33 | shortcut_reduction=9
- row=68 | query=botulism | gold=Ofloxacin | backbone_rank=12 | soft_rank=10 | retrieval_rank=10 | subgraph_shrink=30 | shortcut_reduction=18

