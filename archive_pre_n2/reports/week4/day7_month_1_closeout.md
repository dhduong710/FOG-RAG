# Day 7 Month 1 Closeout

## 1. What is locked from week 1–4

### Week 1 foundations
- DrKGC-style pipeline scope was clarified for the FOG-RAG project.
- The main task was fixed as head prediction for `(? , indication, disease)`.
- Setting A and Setting B were separated conceptually and technically.
- Core repo files and required JSON fields were mapped and validated.
- Smoke tests for data loading, collator, and graph-input plumbing were completed.

### Week 2 benchmark and data pipeline
- Setting A benchmark split was fixed with seed 2025 and the 8388 / 500 / 500 protocol.
- Train graph enrichment for Setting A was built and audited.
- Entity/relation ID maps were frozen.
- DrKGC-style JSON skeleton and mock-ranked candidate JSON were built.
- Candidate size was fixed at K = 20 for the current pipeline stage.
- Prompt/subgraph preprocessing was successfully connected on a subset.
- Retrieval leakage in validation was detected and fixed by keeping retrieval train-only.

### Week 3 Setting B formalization
- Contraindication was locked as auxiliary safety information rather than a main-task positive label.
- Type map, schema rules, and path templates were frozen.
- Dataset card v0 was written.
- Evaluator skeletons for safety and constraint metrics were implemented.
- Valid/test annotation-ready Setting B JSON files were prepared.

### Week 4 pilot backbone and infrastructure
- A reproducible pilot subset was created from Setting A.
- Pilot-ready prompt/subgraph JSON was generated.
- Dry run succeeded end-to-end with finite loss.
- Pilot training succeeded, checkpoints were saved, and trainer outputs were generated.
- Pilot inference succeeded on valid/test.
- Resource plan for month 2 was produced.
- Month 1 artifacts are now frozen.

## 2. What worked

- Dry run succeeded:
  - one pilot batch passed data -> collate -> forward -> loss
  - loss was finite
  - no OOM / no NaN in the dry run

- Pilot train succeeded:
  - 20 optimizer steps completed
  - checkpoints were saved at step 10, step 20, and final
  - train loop was stable
  - no OOM / no NaN during pilot training

- Pilot infer succeeded:
  - valid/test prediction files were generated
  - metric script ran successfully
  - checkpoint loading and graph-model loading worked

- Resource estimation is available:
  - day-2 dry-run peak VRAM reference: 4757.14 MB
  - pilot train runtime: 63.3561 sec
  - pilot train sec/step: 3.168
  - pilot infer runtime: 56.59 sec for 200 pilot samples
  - estimated full debug-config 1 epoch runtime: about 55.38 minutes
  - estimated full debug-config valid+test inference: about 4.72 minutes

## 3. What is still provisional

- The current pipeline still uses a mock coarse ranker with gold forced into the candidate list.
- The current week-4 pilot still uses mock entity embeddings for plumbing/debug purposes.
- The current pilot metrics are not scientific results and must not be used in the paper.
- Full backbone metrics on full Setting A are not available yet.
- Safety-aware candidate handling is formalized in protocol/evaluation, but not yet turned on as the main backbone extension.
- Fuzzy retrieval and fuzzy graph encoding have not started yet.
- If the exact hub-cap choice is not considered fully final for the paper, it should still be treated as provisional.

## 4. Month 2 entry conditions

Month 2 must begin with conservative backbone reproduction on full Setting A.

### Required entry conditions
- Reproduce the DrKGC-style backbone on full Setting A first.
- Use an original-style conservative config first.
- Build baseline table v0 before any novelty extension.
- Keep batch size small and gradient accumulation enabled if needed.
- Use the week-4 debug path only for debugging, not as the scientific month-2 setup.
- Do **not** add fuzzy retrieval, fuzzy graph encoding, or safety-aware modeling before backbone stability is confirmed.

### Main month-2 objective
- obtain a stable reproducible backbone run on full Setting A
- produce baseline ranking results
- establish the evaluation script and result table format
- only after that move into month-3 novelty work

## 5. Risks

### Engineering risks
- GPU memory may rise substantially when replacing the week-4 debug model or mock embeddings.
- Full training memory will be higher than the day-2 dry-run forward memory.
- Preprocessing and prompt/subgraph generation may become a bottleneck on full data.
- Checkpoint storage can grow if saving is too frequent.

### Data/pipeline risks
- Candidate quality is still limited by the current mock coarse ranker.
- Subgraph quality on pilot is not enough to judge full-run evidence quality.
- Pilot infer is optimistic because the current mock setup is easy.
- Runtime estimates from week 4 are debug-config estimates, not final full-backbone guarantees.

## 6. Final month-1 judgment

Month 1 is considered successfully closed.

### Why
- Setting A benchmark is locked.
- Setting B protocol is formalized.
- The pilot pipeline runs end-to-end.
- Resource planning is available.
- The repo is in a state where month 2 can begin with a conservative reproduction-first plan.

### Current decision
**Ready to enter month 2 with Plan B.**

This means:
- do not jump directly to a heavy final run,
- begin month 2 with a conservative backbone reproduction on full Setting A,
- keep debugging and scientific claims clearly separated.

## 7. Frozen artifacts checklist

- [x] Setting A split locked
- [x] Setting B protocol locked
- [x] Candidate JSON available
- [x] Prompt/subgraph-ready pilot JSON available
- [x] Dataset card v0 available
- [x] Evaluator skeleton available
- [x] Pilot subset fixed with seed
- [x] Dry run completed
- [x] Pilot train completed
- [x] Pilot infer completed
- [x] Resource plan completed
- [x] Month 1 closeout completed

## 8. Next action

Proceed to day 7 week-4 review and confirm go / no-go for month 2.

### Note on pilot error analysis
The week-4 pilot did not surface rich failure cases because the current mock setup remained too easy
(coarse ranker and pilot configuration were optimistic). Therefore, week-4 error analysis is useful
mainly for pipeline sanity, not for scientific interpretation.