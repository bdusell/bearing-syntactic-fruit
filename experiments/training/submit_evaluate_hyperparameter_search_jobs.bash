set -euo pipefail
. experiments/include.bash

task_style=lm
for task in "${TASKS[@]}"; do
  for architecture in "${ARCHITECTURES[@]}"; do
    for trial_no in "${HYPERPARAMETER_TRIALS[@]}"; do
      model_dir=$BASE_DIR/models/hyperparameter-search/$task_style/$task/$architecture/$trial_no
      submit_job \
        eval-hp+"$task_style"+"$task"+"$architecture"+"$trial_no" \
        gpu \
        --time=4:00:00 \
        --mem-per-cpu=4G \
        --gres=gpumem:4g \
        -- \
        bash evaluate.bash \
          "$BASE_DIR" \
          "$task_style" \
          "$task" \
          "$model_dir"
    done
  done
done
