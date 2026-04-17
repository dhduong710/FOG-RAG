# Week 5 Closeout — First Full Setting-A Backbone Run

## 1. Week-5 goal
Week 5 was defined as the first real **DrKGC-style backbone reproduction week** on **full Setting A**, with:
- local machine = debug/pilot only,
- server = full run only,
- primary LLM = `meta-llama/Llama-3.2-3B`,
- primary structural embedding source = `R-GCN`,
- no fuzzy module,
- no safety module in the main training path,
- no second LLM branch.

This week was **not** intended for metric chasing or novelty expansion.  
Its purpose was to prove that the full backbone path can run cleanly on server with real data and real graph embeddings.

---

## 2. What is locked at the end of week 5

### 2.1 Full Setting-A backbone-ready package
A clean full package was built at:

`dataset/setting_a/08_backbone_ready/`

with:
- `train.json` = 8388
- `valid.json` = 500
- `test.json` = 500
- `entity2id.pkl`
- `id2entity.pkl`
- `relation2id.pkl`
- `id2relation.pkl`
- `backbone_ready_manifest.json`

Sanity checks passed:
- full split counts are correct,
- required fields are present,
- exact leakage on valid/test = 0.

### 2.2 First real embedding source
A real R-GCN embedding file was exported to:

`dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt`

Validation summary:
- shape = `(10453, 256)`
- entity count matches `entity2id`
- `nan_count = 0`
- `inf_count = 0`
- structurally valid for backbone dry run

### 2.3 Local / server role separation
This week kept compute roles clean:
- **local**: debugging and quick checks only
- **server**: dry run, full train, full valid eval

This separation should be preserved in week 6.

---

## 3. What worked

### 3.1 Server dry run succeeded
A full-ready server dry run passed with real embeddings.

Observed dry-run examples:
- step 0 loss = `2.125384`
- step 1 loss = `2.086372`
- both losses were finite
- candidate count per sample = 20
- subgraph sizes were normal (65–66)
- peak GPU memory was about `3691.56 MB`

Interpretation:
- tokenizer / placeholder path works,
- graph branch works,
- data format works,
- full-ready package can pass through the backbone without NaN/OOM.

### 3.2 First full backbone training run succeeded
The first full Setting-A backbone run completed successfully on server.

Training summary:
- model: `meta-llama/Llama-3.2-3B`
- dataset: `dataset/setting_a/08_backbone_ready`
- graph embedding: `entity_embeddings_rgcn.pt`
- train runtime: `879.5064 sec` (~14m39s)
- train loss: `0.0047157`
- train samples/sec: `9.537`
- train steps/sec: `1.192`

Checkpoints saved:
- `checkpoint-1000`
- `checkpoint-1048`
- `checkpoint-final`

Interpretation:
- the week-5 server training path is alive,
- the environment is usable,
- the first real checkpoint has been produced.

### 3.3 First valid eval run succeeded
A valid inference/evaluation run completed successfully and produced:
- prediction JSON
- metrics JSON
- error-case report

This confirms that the full train → checkpoint → eval path is operational.

---

## 4. What did **not** become scientifically valid yet

### 4.1 Valid metrics are saturated and not interpretable
The first valid evaluation produced:

- `MRR = 1.0`
- `Hits@1 = 1.0`
- `Hits@3 = 1.0`
- `Hits@10 = 1.0`

However, this is **not** evidence that the backbone has solved Setting A.

Follow-up checks showed:

- `rank_distribution = {1: 500}`
- `rank1_ratio = 1.0`
- `pred_equals_top1 = 500 / 500 = 1.0`
- `pred_equals_target = 500 / 500 = 1.0`
- a trivial baseline that always picks candidate #1 also gets perfect ranking metrics on valid

Interpretation:
- the current candidate source remains **mock-like / saturated**
- gold is already top-ranked in all valid samples
- therefore current valid metrics are **engineering-valid but scientifically non-informative**

### 4.2 Current `08_backbone_ready` is final in format, but not final in ranking quality
The current full-ready JSON is:
- final enough for pipeline execution,
- but not final enough for scientific evaluation of the backbone,
because it still inherits candidate ordering from the old mock-style ranked JSON.

This is now the main bottleneck.

---

## 5. Minor warnings observed this week

These did not block progress, but should be remembered:

1. `DataLoader` warning about 32 workers vs suggested 24  
   - not fatal this week
   - may need cleanup later if instability appears

2. `bitsandbytes` version warning  
   - not fatal this week
   - may be worth upgrading later if optimizer issues appear

3. `TRANSFORMERS_CACHE` deprecation warning  
   - cosmetic for now
   - low priority

---

## 6. Main conclusion of week 5

Week 5 is a success in the **engineering / systems** sense:

- full Setting-A backbone-ready package exists,
- first real graph embedding source exists,
- first full backbone server run succeeded,
- first full valid eval run succeeded.

But week 5 is **not yet a scientific backbone result** for Setting A, because:
- the candidate source is still mock-like,
- the valid set is saturated,
- the perfect valid metrics are not meaningful.

The most important outcome of week 5 is therefore:

> The bottleneck is no longer environment, server setup, JSON format, graph branch integration, or checkpointing.  
> The bottleneck is now the **candidate ranking source** for Setting A.

---

## 7. Week-6 entry conditions

Week 6 should **not** open fuzzy or safety modules yet.

Week 6 should keep the same backbone path:
- same server environment
- same Llama-3.2-3B path
- same graph branch path
- same full-ready packaging logic

But week 6 must replace the current mock-like candidate source with a **real coarse ranker for Setting A**, preferably using R-GCN-based scoring.

Required week-6 entry tasks:
1. build real candidate ranking for Setting A
2. generate new ranked JSON for train/valid/test
3. rebuild backbone-ready JSON from real ranked inputs
4. retrain backbone on the new candidate source
5. re-evaluate valid before touching test
6. still keep fuzzy/safety disabled in the main path

---

## 8. Decision

**Decision: CONDITIONAL GO**

Reason:
- Go, because the first full server backbone path is alive and reproducible.
- Conditional, because the current valid metrics cannot be trusted scientifically until the candidate source is rebuilt with a real coarse ranker.

In short:

> Week 5 successfully established the full backbone execution path.  
> Week 6 must replace the mock-like candidate ranking with a real R-GCN-based coarse ranker before any further metric interpretation.
