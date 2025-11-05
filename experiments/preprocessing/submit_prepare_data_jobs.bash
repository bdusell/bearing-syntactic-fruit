set -euo pipefail
. experiments/include.bash

for task in "${TASKS[@]}"; do
  submit_job \
    prepare+"$task" \
    cpu \
    --time=10:00 \
    -- \
    bash prepare_data.bash \
      "$BASE_DIR" \
      "$task"
done
