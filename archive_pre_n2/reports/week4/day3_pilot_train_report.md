# Day 3 Pilot Train Report

## 1. Goal
Run one short pilot training loop to verify end-to-end training stability on the week-4 pilot subset.

## 2. Setup
- dataset_path: `dataset/setting_a/07_pilot_ready`
- model_name_or_path: `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
- kge_embedding_path: `dataset/setting_a/07_pilot_ready/mock_entity_embeddings.pt`
- quantization: 4-bit
- batch_size: 1
- gradient_accumulation_steps: 8
- max_steps: 20
- save_steps: 10
- learning_rate: 2e-4
- seed: 2025

## 3. Output Directory
`results/week4/pilot_train_tinyllama_mock`

## 4. Training Log Summary
- checkpoint saved at step 10: yes
- checkpoint saved at step 20: yes
- final checkpoint saved: yes
- training finished successfully: yes
- NaN observed: no
- OOM observed: no

## 5. Main Metrics
- epoch: 0.19
- train_loss: 0.07094827135151718
- train_runtime: 63.3561
- train_samples_per_second: 2.525
- train_steps_per_second: 0.316

## 6. Loss Behavior
Observed training loss decreased rapidly from early steps (e.g., 0.6501) to very small values on later steps. This is acceptable for a short pilot run on a small subset and indicates that the training loop, gradient flow, checkpoint saving, and optimizer updates are functioning correctly.

## 7. Interpretation
This run confirms:
- the pilot-ready JSON can be used in the real training loop;
- the tokenizer, collator, DrKGC model, graph branch, and trainer work together end-to-end;
- checkpointing and result saving function correctly.

This run does **not** constitute scientific evidence of model quality, because it uses:
- a week-4 pilot subset,
- a short 20-step run,
- TinyLlama instead of the planned month-2 backbone setting,
- mock entity embeddings instead of final structural embeddings.

## 8. Files Confirmed
The output directory contains:
- `checkpoint-10/`
- `checkpoint-20/`
- `checkpoint-final/`
- `train_results.json`
- `trainer_state.json`

## 9. Decision
**Ready for Day 4 pilot inference.**