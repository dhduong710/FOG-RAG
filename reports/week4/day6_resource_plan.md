# Day 6 Resource Plan

## 1. Current pilot configuration
- model: `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
- kge path: `dataset/setting_a/07_pilot_ready/mock_entity_embeddings.pt`
- sequence length: 768
- per-device train batch size: 1
- gradient accumulation steps: 8
- effective batch size: 8
- device: Current local GPU used in week-4 pilot

## 2. Observed runtime and memory
- day-2 dryrun peak VRAM: 4757.14 MB
- pilot train runtime: 63.36 sec
- pilot train steps/sec: 0.316
- pilot train samples/sec: 2.525
- pilot train sec/step: 3.168
- pilot train loss: 0.070948
- pilot infer runtime on valid+test pilot: 56.59 sec total (0.2830 sec/sample)
- pilot infer max RSS (host memory): 4217580 KB

## 3. Storage snapshot
- pilot-ready dataset folder: 22.18 MB
- pilot train output folder: 81.44 MB
- pilot infer output folder: 205.51 KB

### Checkpoint sizes
- checkpoint-10: 27.14 MB
- checkpoint-20: 27.14 MB
- checkpoint-final: 27.14 MB

## 4. Extrapolation to month 2
Assuming the same debug configuration and similar sequence-length behavior:

- full train samples: 8388
- optimizer steps per epoch on full train: 1049
- estimated full epoch runtime: 55.38 minutes
- estimated 3-epoch runtime: 2.77 hours
- estimated 5-epoch runtime: 4.62 hours
- estimated full valid+test inference runtime (500+500): 4.72 minutes

## 5. Interpretation
- The current debug configuration fits comfortably for week-4 pilot purposes.
- The current pilot confirms system stability, not scientific performance.
- Because the current run still uses TinyLlama + mock entity embeddings, these numbers are conservative engineering estimates only.
- The pilot does **not** justify jumping directly to a large month-2 run without one more cautious reproduction-style smoke run.

## 6. Final plan
### Recommended option: Plan B
**Plan B**: pilot fit is good enough, but month 2 should start with a conservative reproduction configuration before scaling.

### Main month-2 recommendation
- primary month-2 goal: reproduce the DrKGC-style backbone on full Setting A first
- start from an original-style conservative config
- keep batch size small
- keep gradient accumulation enabled
- do not add fuzzy or safety modules before backbone stability is confirmed

### Practical recommendation
- debug model: keep the current TinyLlama-based pipeline for fast debugging
- month-2 main run: move to the intended backbone gradually, not in one jump
- first full-A smoke run in month 2 should be short and checkpoint-safe
- only after that should you launch a longer reproduction run

## 7. Risks to watch
- VRAM may rise substantially when replacing the debug model or mock embeddings
- preprocessing time may become a bottleneck on full data
- checkpoint storage can grow if save frequency is too aggressive
- the current pilot infer is optimistic because the coarse ranker is still mock

## 8. Decision
- Current judgment: **ready to enter month 2 with Plan B**
- Not recommended: jumping directly to a heavy full run today
