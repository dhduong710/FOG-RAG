import json
from pathlib import Path

OUTPUT_DIR = Path("results/week4/pilot_train_tinyllama_mock")
REPORT_PATH = Path("reports/week4/day3_pilot_train_report.md")


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    train_results_path = OUTPUT_DIR / "train_results.json"
    trainer_state_path = OUTPUT_DIR / "trainer_state.json"

    if not train_results_path.exists():
        raise FileNotFoundError(f"Missing: {train_results_path}")
    if not trainer_state_path.exists():
        raise FileNotFoundError(f"Missing: {trainer_state_path}")

    train_results = load_json(train_results_path)
    trainer_state = load_json(trainer_state_path)

    checkpoints = sorted([p.name for p in OUTPUT_DIR.iterdir() if p.is_dir() and p.name.startswith("checkpoint-")])

    log_history = trainer_state.get("log_history", [])
    train_loss_logs = [x for x in log_history if "loss" in x]
    last_loss = train_loss_logs[-1]["loss"] if train_loss_logs else None
    first_loss = train_loss_logs[0]["loss"] if train_loss_logs else None

    global_step = trainer_state.get("global_step")
    best_model_checkpoint = trainer_state.get("best_model_checkpoint")
    max_steps = trainer_state.get("max_steps")

    train_runtime = train_results.get("train_runtime")
    train_samples_per_second = train_results.get("train_samples_per_second")
    train_steps_per_second = train_results.get("train_steps_per_second")
    train_loss = train_results.get("train_loss")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    report = f"""# Day 3 Pilot Train Report

## Goal
Run one short pilot training loop to verify end-to-end training stability.

## Output Directory
`{OUTPUT_DIR}`

## Main Results
- global_step: {global_step}
- max_steps: {max_steps}
- train_runtime: {train_runtime}
- train_samples_per_second: {train_samples_per_second}
- train_steps_per_second: {train_steps_per_second}
- train_loss: {train_loss}

## Loss Trace Snapshot
- first_logged_loss: {first_loss}
- last_logged_loss: {last_loss}

## Checkpoints
{chr(10).join(f"- {ckpt}" for ckpt in checkpoints) if checkpoints else "- none"}

## Best Model Checkpoint
- {best_model_checkpoint}

## Decision
- ready for day 4 pilot inference

## Notes
- This run is a week-4 pilot training check only.
- It uses TinyLlama + mock entity embeddings.
- Metrics from this run must not be used for scientific conclusions.
"""

    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Saved report to: {REPORT_PATH}")


if __name__ == "__main__":
    main()