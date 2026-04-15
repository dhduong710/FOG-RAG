# Week 12A Day 1 — Retriever Rescue Protocol Freeze

## 1. Goal
Week 12A is a bounded retriever-rescue sprint before Novelty 2.
The goal is to determine whether a finetuned R-GCN coarse retriever can reduce gold-injection dependence enough to justify resetting the base candidate source.

## 2. Scope
This week only revisits the coarse retriever / candidate source.
It does NOT:
- change Setting A task
- change candidate universe
- change K
- change ontology/hard/soft logic
- change LLM backbone
- start Novelty 2

## 3. Frozen protocol
- Task: head prediction (? , indication, disease)
- Candidate universe: drug_only
- K: 20
- Primary decision split: valid
- Test is not used for scientific decision until valid clearly improves

## 4. Two-layer artifact rule
Retriever evaluation must keep two separate artifact layers:
1. top20_raw = true retrieval quality
2. top20_drkgc_ready = reranker-ready artifact with explicit gold injection logging if needed

Gold injection is allowed only in the ready layer and must be logged explicitly.

## 5. Current reference
### Current retriever reference
- dataset/setting_a/11_ranker_v2
- dataset/setting_a/12_backbone_ready_ranker_v2

### Current reference retrieval metrics (valid)
- recall@20_raw = 0.192
- inject_ratio_ready = 0.808
- top1_hit_ratio_raw = 0.018

## 6. Decision gate
### NO-GO
- recall@20_raw < 0.25
- or inject_ratio_ready > 0.75

### CONDITIONAL GO
- recall@20_raw in [0.25, 0.35)
- inject_ratio_ready in [0.65, 0.75]
- plus clear top1 / diversity / collapse improvement

### STRONG GO
- recall@20_raw >= 0.35
- inject_ratio_ready <= 0.65
- and short valid rerun does not collapse

## 7. Allowed next actions
Only if valid-side retriever metrics pass the GO gate:
- build new top20_raw / top20_drkgc_ready artifacts
- build a new backbone-ready package
- run short valid rerun of the backbone

## 8. Frozen references for later comparison
- backbone reference row: current backbone
- Novelty-1 main row: +Ontology+Hard
These are not rerun unless the retriever clearly wins.

## 9. Success condition of week 12A
Week 12A is successful if one of the following happens:
1. GO: the finetuned retriever clearly improves enough to justify resetting the base
2. clean NO-GO: the finetuned retriever does not improve enough, and we stop immediately and move to Novelty 2

## 10. Failure condition
Week 12A fails if:
- protocol changes mid-week
- valid and test are mixed
- retriever and reranker metrics are confused
- raw and ready artifact layers are merged
- gold injection is not logged explicitly