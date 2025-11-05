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

random_sample() {
  python random_sample.py "$@"
}

dataset_dir=$base_dir/data/$task_style/$dataset_name
hyperparameter_search_dir=$base_dir/models/hyperparameter-search/$task_style/$dataset_name/$architecture
model_dir=$base_dir/models/tuned/$task_style/$dataset_name/$architecture/$trial_no

hyperparameters=$(python print_best_hyperparameters.py "$hyperparameter_search_dir"/{1..10})
rau "$task_style" train \
  --output "$model_dir" \
  --training-data "$dataset_dir" \
  $hyperparameters \
  --max-epochs 1000 \
  "${training_args[@]}"
bash evaluate.bash "$base_dir" "$task_style" "$dataset_name" "$model_dir"
