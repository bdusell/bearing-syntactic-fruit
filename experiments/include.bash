. experiments/config.bash

FIGURES_DIR=$BASE_DIR/figures

submit_job() {
  bash experiments/submit_job.bash "$@"
}

TASKS=(question-formation tense-reinflection)
ARCHITECTURES=(\
  transformer \
  rnn \
  lstm \
  {transformer,rnn,lstm}+sup \
  {transformer,rnn,lstm}+nd \
  transformer+{sup,nd}-x2 \
  {rnn,lstm}+{sup,nd}+r \
)
HYPERPARAMETER_TRIALS=({1..10})
TRIALS=({1..5})

architecture_label() {
  local r
  if [[ $1 =~ ^(transformer|rnn|lstm)(\+(sup|nd)(-x2)?)?(\+r)?$ ]]; then
    base=${BASH_REMATCH[1]}
    stack=${BASH_REMATCH[3]}
    double=${BASH_REMATCH[4]}
    reading=${BASH_REMATCH[5]}
    r="\\${base}Label{}"
    if [[ $stack ]]; then
      r+="+\\${stack}Label{}"
    fi
    if [[ $double ]]; then
      r+="+\\${stack}Label{}"
    fi
    if [[ $reading ]]; then
      r+="+\\readingLabel{}"
    fi
  else
    echo "invalid architecture: $1" >&2
    return 1
  fi
  printf %s "$r"
}
