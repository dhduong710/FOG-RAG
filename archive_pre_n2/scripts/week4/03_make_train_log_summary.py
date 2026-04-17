import json
from pathlib import Path

TRAIN_RESULTS_PATH = Path("results/week4/pilot_train_tinyllama_mock/train_results.json")
TRAINER_STATE_PATH = Path("results/week4/pilot_train_tinyllama_mock/trainer_state.json")
OUT_PATH = Path("results/week4/pilot_train_tinyllama_mock/train_log_summary.json")

def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def main():
    trainer_state = load_json(TRAINER_STATE_PATH)
    train_results = load_json(TRAIN_RESULTS_PATH)

    log_history = trainer_state.get("log_history", [])
    step_logs = [x for x in log_history if "loss" in x]

    summary = {
        "num_logged_steps": len(step_logs),
        "first_step_log": step_logs[0] if step_logs else None,
        "last_step_log": step_logs[-1] if step_logs else None,
        "min_logged_loss": min((x["loss"] for x in step_logs), default=None),
        "max_logged_loss": max((x["loss"] for x in step_logs), default=None),
        "final_train_results": train_results,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"Saved: {OUT_PATH}")

if __name__ == "__main__":
    main()