# Experimental Setup for Setting A

## 1. Task formulation
We evaluate Setting A as a head-prediction task of the form `(?, indication, disease)`, where the goal is to rank candidate drugs for a given disease query.

## 2. Candidate universe and split policy
For the structure-only baselines, the evaluation universe is restricted to the drug-only entity set. We use the valid split as the primary decision split in this week, and report standard ranking metrics including MRR, Hits@1, Hits@3, and Hits@10.

## 3. Graph and evaluation protocol
All structure-only baselines are evaluated under the same clean valid-first protocol on the PrimeKG-based Setting A benchmark. The training graph is the enriched Setting-A graph, while validation is performed on the fixed valid split. This week focuses on establishing a clean comparison floor rather than introducing new novelty modules.

## 4. Table policy
We intentionally separate the main structure-only baseline table from the candidate-aware reranker reference rows. The latter are included only as supporting references and should not be interpreted as directly comparable under the exact same evaluation protocol without explicit caveats.
