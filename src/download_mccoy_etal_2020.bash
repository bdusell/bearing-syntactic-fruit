set -euo pipefail

usage() {
  echo "Usage: bash $0 <base-directory>"
}

base_dir=${1-}
if ! shift 1; then
  usage >&2
  exit 1
fi

data_dir=$base_dir/data

download_dataset() {
  local local_name external_name
  local_name=$1
  external_name=$2
  local lm_dir=$data_dir/lm/$local_name
  mkdir -p "$lm_dir"/datasets/{validation,{test,generalization}{,-{source,target}}}
  local url=https://github.com/tommccoy1/rnn-hierarchical-biases/raw/f34a87c4fe804cb288d0527daa9c251def0ae24e/data
  curl -L "$url"/"$external_name".train > "$lm_dir"/main.tok
  curl -L "$url"/"$external_name".dev > "$lm_dir"/datasets/validation/main.tok
  curl -L "$url"/"$external_name".test > "$lm_dir"/datasets/test/main.tok
  cut -f 1 "$lm_dir"/datasets/test/main.tok > "$lm_dir"/datasets/test-source/main.tok
  cut -f 2 "$lm_dir"/datasets/test/main.tok > "$lm_dir"/datasets/test-target/main.tok
  curl -L "$url"/"$external_name".gen > "$lm_dir"/datasets/generalization/main.tok
  cut -f 1 "$lm_dir"/datasets/generalization/main.tok > "$lm_dir"/datasets/generalization-source/main.tok
  cut -f 2 "$lm_dir"/datasets/generalization/main.tok > "$lm_dir"/datasets/generalization-target/main.tok
  local ss_dir=$data_dir/ss/$local_name
  mkdir -p "$ss_dir"/datasets/{validation,test,generalization}
  cut -f 1 "$lm_dir"/main.tok > "$ss_dir"/source.tok
  cut -f 2 "$lm_dir"/main.tok > "$ss_dir"/target.tok
  cut -f 1 "$lm_dir"/datasets/validation/main.tok > "$ss_dir"/datasets/validation/source.tok
  cut -f 2 "$lm_dir"/datasets/validation/main.tok > "$ss_dir"/datasets/validation/target.tok
  ln -sf ../../../../lm/"$local_name"/datasets/test-source/main.tok "$ss_dir"/datasets/test/source.tok
  ln -sf ../../../../lm/"$local_name"/datasets/test-target/main.tok "$ss_dir"/datasets/test/target.tok
  ln -sf ../../../../lm/"$local_name"/datasets/generalization-source/main.tok "$ss_dir"/datasets/generalization/source.tok
  ln -sf ../../../../lm/"$local_name"/datasets/generalization-target/main.tok "$ss_dir"/datasets/generalization/target.tok
}

download_dataset question-formation question
mkdir -p "$data_dir"/lm/question-formation/datasets/generalization-wrong-target
python move_first.py \
  < "$data_dir"/lm/question-formation/datasets/generalization-source/main.tok \
  > "$data_dir"/lm/question-formation/datasets/generalization-wrong-target/main.tok
download_dataset tense-reinflection tense
mkdir -p "$data_dir"/lm/tense-reinflection/datasets/generalization-wrong-target
python agree_recent.py \
  < "$data_dir"/lm/tense-reinflection/datasets/generalization-source/main.tok \
  > "$data_dir"/lm/tense-reinflection/datasets/generalization-wrong-target/main.tok
