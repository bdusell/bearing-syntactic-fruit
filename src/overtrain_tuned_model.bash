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
hyperparameter_search_dir=$base_dir/models/hyperparameter-search/$task_style/$dataset_name/$architecture
model_dir=$base_dir/models/overtrained/$task_style/$dataset_name/$architecture/$trial_no

escape() {
  python -c 'import sys; print(repr(sys.argv[1]))' "$1"
}

hyperparameters=$(python print_best_hyperparameters.py "$hyperparameter_search_dir"/{1..10})
PYTHONPATH=$PWD rau "$task_style" train \
  --output "$model_dir" \
  --training-data "$dataset_dir" \
  $hyperparameters \
  --max-epochs 20 \
  --early-stopping-patience 999999999 \
  "${training_args[@]}" \
  --every-n-examples 25000 "
from evaluate_overtrained import evaluate_overtrained
evaluate_overtrained(
    state=state,
    saver=saver,
    index=index,
    base_dir=$(escape "$base_dir"),
    task_style=$(escape "$task_style"),
    dataset_name=$(escape "$dataset_name"),
    architecture=$(escape "$architecture"),
    trial_no=$(escape "$trial_no")
)
"
