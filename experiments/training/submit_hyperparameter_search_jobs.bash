set -euo pipefail
. experiments/include.bash

task_style=lm

for task in "${TASKS[@]}"; do
  for architecture in "${ARCHITECTURES[@]}"; do
    if [[ $architecture = *'+nd'* ]]; then
      gpu_mem=4g
      hours=24
    elif [[ $architecture = *'+sup'* ]]; then
      gpu_mem=4g
      hours=24
    else
      gpu_mem=4g
      hours=4
    fi
    for trial_no in "${HYPERPARAMETER_TRIALS[@]}"; do
      submit_job \
        hyperparameter-train+"$task_style"+"$task"+"$architecture"+"$trial_no" \
        gpu \
        --time=$hours:00:00 \
        --mem-per-cpu=4G \
        --gres=gpumem:$gpu_mem \
        -- \
        bash train_with_random_hyperparameters.bash \
          "$BASE_DIR" \
          "$task_style" \
          "$task" \
          "$architecture" \
          "$trial_no" \
          --time-limit $(bc <<<"$hours * 0.97")h \
          --no-progress
    done
  done
done
