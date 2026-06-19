set -euo pipefail
. experiments/include.bash

name=overtrained-linear
mkdir -p "$FIGURES_DIR"/"$name"

task_style=lm
for task in question-formation tense-reinflection; do
  args=()
  for architecture in transformer; do
    args+=(--label "$(architecture_label "$architecture")")
    args+=(--inputs)
    for trial_no in "${OVERTRAIN_TRIALS[@]}"; do
      args+=("$BASE_DIR"/models/"$name"/"$task_style"/"$task"/"$architecture"/"$trial_no")
    done
  done
  bash experiments/run.bash cpu python plot_overtrained.py \
    "${args[@]}" \
    --output "$FIGURES_DIR"/"$name"/"$task".png \
    --max-snapshot 24
done
