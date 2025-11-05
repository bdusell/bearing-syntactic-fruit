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
model_dir=$base_dir/models/hyperparameter-search/$task_style/$dataset_name/$architecture/$trial_no

parameter_count=200000
num_heads=4
feedforward_size_factor=2
rnn_num_layers=3
sup_stack_size=50
nd_stack_size=3-3-5

case $task_style in
  lm)
    if [[ $architecture = transformer ]]; then
      architecture_args=( \
        --architecture "$architecture" \
        --num-layers 5 \
        --num-heads "$num_heads" \
        --feedforward-size-factor "$feedforward_size_factor" \
      )
    elif [[ $architecture =~ ^(rnn|lstm)$ ]]; then
      architecture_args=( \
        --architecture "$architecture" \
        --num-layers "$rnn_num_layers" \
      )
    elif [[ $architecture =~ ^transformer\+(sup|nd)(-x2)?$ ]]; then
      stack=${BASH_REMATCH[1]}
      twice=${BASH_REMATCH[2]}
      case $stack in
        sup) stack_layer=superposition-$sup_stack_size ;;
        nd) stack_layer=nondeterministic-$nd_stack_size ;;
      esac
      if [[ $twice ]]; then
        layers=1.$stack_layer.1.$stack_layer.1
      else
        layers=2.$stack_layer.2
      fi
      architecture_args=( \
        --architecture stack-transformer \
        --num-heads "$num_heads" \
        --feedforward-size-factor "$feedforward_size_factor" \
        --stack-transformer-layers "$layers" \
      )
    elif [[ $architecture =~ ^(rnn|lstm)\+(sup|nd)(\+r)?$ ]]; then
      controller=${BASH_REMATCH[1]}
      stack=${BASH_REMATCH[2]}
      reading_trick=${BASH_REMATCH[3]}
      case $stack in
        sup) stack_str=superposition-$sup_stack_size ;;
        nd) stack_str=vector-nondeterministic-$nd_stack_size ;;
      esac
      architecture_args=( \
        --architecture stack-rnn \
        --num-layers "$rnn_num_layers" \
        --stack-rnn-controller "$controller" \
        --stack-rnn-stack "$stack_str" \
      )
      if [[ $reading_trick ]]; then
        architecture_args+=(--stack-rnn-connect-reading-to-output)
      fi
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

final_architecture_args=( \
  $( \
    rau lm model-size \
      --training-data "$dataset_dir" \
      --parameters "$parameter_count" \
      "${architecture_args[@]}" \
  ) \
  --dropout 0.1 \
  --init-scale 0.1 \
)

rau "$task_style" train \
  --output "$model_dir" \
  --training-data "$dataset_dir" \
  "${final_architecture_args[@]}" \
  --max-epochs 1000 \
  --max-tokens-per-batch "$(random_sample --int 512 2048)" \
  --optimizer Adam \
  --initial-learning-rate "$(random_sample --log 1e-5 1e-3)" \
  --gradient-clipping-threshold 10 \
  --early-stopping-patience 3 \
  --learning-rate-patience 2 \
  --learning-rate-decay-factor 0.5 \
  --examples-per-checkpoint 80000 \
  "${training_args[@]}"
