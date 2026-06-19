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
model_dir=$base_dir/models/overtrained-linear/$task_style/$dataset_name/$architecture/$trial_no

d_model=512
num_heads=4
feedforward_size=$d_model
dropout=0.1
init_scale=0.1

sup_stack_size=50
nd_stack_size=3-3-5

case $task_style in
  lm)
    if [[ $architecture = transformer ]]; then
      architecture_args=( \
        --architecture "$architecture" \
        --num-layers 5 \
        --d-model "$d_model" \
        --num-heads "$num_heads" \
        --feedforward-size "$feedforward_size" \
        --dropout "$dropout" \
        --init-scale "$init_scale" \
      )
    elif [[ $architecture =~ ^transformer\+(sup|nd)(-x2)?$ ]]; then
      stack=${BASH_REMATCH[1]}
      twice=${BASH_REMATCH[2]}
      case $stack in
        sup) stack_layer=superposition-$sup_stack_size ;;
        nd) stack_layer=nondeterministic-$nd_stack_size ;;
      esac
      if [[ $twice ]]; then
        layers=1.$stack_layer.2.$stack_layer.1
      else
        layers=2.$stack_layer.3
      fi
      architecture_args=( \
        --architecture stack-transformer \
        --d-model "$d_model" \
        --num-heads "$num_heads" \
        --feedforward-size "$feedforward_size" \
        --dropout "$dropout" \
        --stack-transformer-layers "$layers" \
        --init-scale "$init_scale" \
      )
    else
      echo "invalid architecture $architecture" >&2
      exit 1
    fi
    ;;
  ss)
    echo ss not implemented >&2
    exit 1
    ;;
  *) exit 1 ;;
esac

escape() {
  python -c 'import sys; print(repr(sys.argv[1]))' "$1"
}

PYTHONPATH=$PWD rau "$task_style" train \
  --output "$model_dir" \
  --training-data "$dataset_dir" \
  "${architecture_args[@]}" \
  --max-epochs 24 \
  --max-tokens-per-batch 191 \
  --optimizer Adam \
  --initial-learning-rate 1e-4 \
  --weight-decay 0 \
  --gradient-clipping-threshold 10 \
  --early-stopping-patience 999999999 \
  --learning-rate-schedule-type linear-with-warmup \
  --learning-rate-warmup-examples 80000 \
  --examples-per-checkpoint 80000 \
  "${training_args[@]}" \
  --every-n-examples 100000 "
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
