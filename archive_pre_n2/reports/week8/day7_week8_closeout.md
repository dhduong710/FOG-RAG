# Day 7 Week 8 Closeout

## 1. Scope of the week
This week focused on freezing the Setting-A structural baseline protocol, running 2–4 structure-only baselines, building the first clean Setting-A result table v0, and drafting the corresponding Experimental Setup / Baselines writing.

## 2. What was completed
- Protocol freeze for Setting A structural baseline evaluation
- Clean structure-only evaluation row for R-GCN (provisional)
- Full HRGAT baseline training and valid evaluation
- Full ComplEx baseline training and valid evaluation
- Full TransE baseline training and valid evaluation
- First clean Setting-A table v0
- Separate reference section for candidate-aware reranker rows

## 3. Main result table status
The current structure-only ordering in table v0 is:
1. ComplEx
2. HRGAT
3. TransE
4. R-GCN (provisional)

The candidate-aware reranker rows are kept in a separate supporting section, with week7 3B remaining the main backbone reference.

## 4. Main technical conclusions
- The Setting-A protocol is now frozen cleanly for structural baseline comparison.
- ComplEx is currently the strongest structure-only row in the first table version.
- HRGAT substantially reduces collapse relative to the provisional R-GCN row.
- The reranker backbone path is already frozen enough to serve as a reference, so no further retrieval/backbone changes were needed this week.

## 5. GO decision
**GO (strong)**

Rationale:
- Four structure-only baselines are available.
- The first clean Setting-A table v0 is complete.
- Experimental Setup / Baselines drafts are available.
- The repo now has a cleaner comparison floor before entering the next novelty phase.
