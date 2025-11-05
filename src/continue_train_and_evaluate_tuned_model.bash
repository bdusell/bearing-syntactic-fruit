set -euo pipefail

usage() {
  echo "Usage: bash $0 <base-directory> <task-style> <dataset-name> <architecture> <trial-no> [training-args...]"
}

base_dir=${1-}
task_style=${2-}
dataset_name=${3-}
architecture=${4-}
trial_no=${5-}
if ! shift 5; then
  usage >&2
  exit 1
fi
training_args=("$@")

dataset_dir=$base_dir/data/$task_style/$dataset_name
model_dir=$base_dir/models/tuned/$task_style/$dataset_name/$architecture/$trial_no

if ! rau is-finished "$model_dir"; then
  echo "Continuing training for $model_dir."
  rau "$task_style" train \
    --continue \
    --output "$model_dir" \
    --training-data "$dataset_dir" \
    "${training_args[@]}"
  bash evaluate.bash "$base_dir" "$task_style" "$dataset_name" "$model_dir"
else
  echo "Training for $model_dir is already finished. Nothing to do."
fi
