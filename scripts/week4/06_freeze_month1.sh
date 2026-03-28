#!/usr/bin/env bash
set -euo pipefail

FREEZE_TAG="month1-freeze-settingA-settingB-pilot-ready"
BACKUP_DIR="backups/month1_freeze"
RUN_DIR="runs/week4_pilot"
REPORT_DIR="reports/week4"
RESULT_TRAIN_DIR="results/week4/pilot_train_tinyllama_mock"
RESULT_INFER_DIR="results/week4/pilot_infer_tinyllama_mock"

mkdir -p "${BACKUP_DIR}"
mkdir -p "${RUN_DIR}"

echo "============================================================"
echo "Month 1 Freeze"
echo "FREEZE_TAG=${FREEZE_TAG}"
echo "BACKUP_DIR=${BACKUP_DIR}"
echo "============================================================"

# 1. backup pilot logs if they exist
for f in \
  "${RUN_DIR}/day3_pilot_train.log" \
  "${RUN_DIR}/day4_pilot_infer.log" \
  "${RUN_DIR}/day5_timed_infer.log"
do
  if [ -f "${f}" ]; then
    cp "${f}" "${BACKUP_DIR}/"
    echo "Backed up: ${f}"
  else
    echo "Missing log (skip): ${f}"
  fi
done

# 2. snapshot config used in week 4
cat > "${RUN_DIR}/config_snapshot.yaml" <<EOF
week4_freeze_tag: ${FREEZE_TAG}

pilot_dataset_path: dataset/setting_a/07_pilot_ready
pilot_train_output_dir: ${RESULT_TRAIN_DIR}
pilot_infer_output_dir: ${RESULT_INFER_DIR}

model_name_or_path: TinyLlama/TinyLlama-1.1B-Chat-v1.0
kge_embedding_path: dataset/setting_a/07_pilot_ready/mock_entity_embeddings.pt

pilot_train:
  seed: 2025
  per_device_train_batch_size: 1
  gradient_accumulation_steps: 8
  max_steps: 20
  learning_rate: 2e-4
  source_max_len: 768
  target_max_len: 32
  bits: 4

pilot_infer:
  seed: 2025
  max_new_tokens: 16

resource_plan:
  dryrun_peak_vram_mb: 4757.14
  pilot_train_runtime_sec: 63.3561
  pilot_infer_runtime_sec_for_200: 56.59
  estimated_full_epoch_minutes_debug_config: 55.38
  estimated_full_valid_test_minutes_debug_config: 4.72

final_decision:
  month2_plan: B
  note: "Conservative reproduction-first entry into month 2"
EOF

echo "Saved: ${RUN_DIR}/config_snapshot.yaml"

# 3. build freeze manifest
python - <<'PY'
import json
from pathlib import Path

manifest = {
    "frozen_reports": [
        "reports/week4/day1_pilot_subset_report.md",
        "reports/week4/day2_dryrun_report.md",
        "reports/week4/day3_pilot_train_report.md",
        "reports/week4/day4_pilot_infer_report.md",
        "reports/week4/day6_resource_plan.md",
        "reports/week4/day7_month1_closeout.md",
    ],
    "frozen_results": [
        "results/week4/pilot_train_tinyllama_mock/train_results.json",
        "results/week4/pilot_train_tinyllama_mock/trainer_state.json",
        "results/week4/pilot_infer_tinyllama_mock/metrics.json",
        "results/week4/pilot_infer_tinyllama_mock/valid_predictions.json",
        "results/week4/pilot_infer_tinyllama_mock/test_predictions.json",
        "results/week4/pilot_infer_tinyllama_mock/case_review.md",
    ],
    "frozen_dataset_artifacts": [
        "dataset/setting_a/06_pilot_subset/train_pilot_input.json",
        "dataset/setting_a/06_pilot_subset/valid_pilot_input.json",
        "dataset/setting_a/06_pilot_subset/test_pilot_input.json",
        "dataset/setting_a/07_pilot_ready/train.json",
        "dataset/setting_a/07_pilot_ready/valid.json",
        "dataset/setting_a/07_pilot_ready/test.json",
        "dataset/setting_a/07_pilot_ready/mock_entity_embeddings.pt",
    ],
    "decision": {
        "month2_plan": "B",
        "status": "ready_for_month2_conservative_reproduction"
    }
}

out = Path("runs/week4_pilot/month1_freeze_manifest.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Saved: {out}")
PY

# 4. git tag suggestion
if git rev-parse --git-dir >/dev/null 2>&1; then
  echo
  echo "Git repo detected."
  echo "Suggested commands:"
  echo "  git add ."
  echo "  git commit -m \"freeze month 1 artifacts and pilot backbone baseline\""
  echo "  git tag ${FREEZE_TAG}"
else
  echo
  echo "No git repo detected from current shell context."
fi

echo
echo "Month 1 freeze script finished."