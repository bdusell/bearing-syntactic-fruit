set -euo pipefail
. experiments/include.bash

task_style=lm
for task in question-formation tense-reinflection; do
  args=()
  for architecture in transformer{,+{sup,nd}{,-x2}} {rnn,lstm}{,+{sup,nd}{,+r}}; do
    args+=(--label "$(architecture_label "$architecture")")
    args+=(--inputs)
    for trial_no in "${TRIALS[@]}"; do
      args+=("$BASE_DIR"/models/tuned/"$task_style"/"$task"/"$architecture"/"$trial_no")
    done
  done
  bash experiments/run.bash cpu python print_mean_table.py "${args[@]}"
done
