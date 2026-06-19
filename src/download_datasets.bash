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
  local url=$1
  local local_name=$2
  local external_name=$3
  download_dataset_files "$url" "$local_name" "$external_name"
  postprocess_dataset "$local_name"
}

download_dataset_files() {
  local url=$1
  local local_name=$2
  local external_name=$3
  local lm_dir=$data_dir/lm/$local_name
  mkdir -p "$lm_dir"/datasets/{validation,test,generalization}
  curl -L "$url"/"$external_name".train > "$lm_dir"/main.tok
  curl -L "$url"/"$external_name".dev > "$lm_dir"/datasets/validation/main.tok
  curl -L "$url"/"$external_name".test > "$lm_dir"/datasets/test/main.tok
  curl -L "$url"/"$external_name".gen > "$lm_dir"/datasets/generalization/main.tok
}

postprocess_dataset() {
  local local_name=$1
  local lm_dir=$data_dir/lm/$local_name
  mkdir -p "$lm_dir"/datasets/{{test,generalization}-{source,target},generalization-wrong-target}
  cut -f 1 "$lm_dir"/datasets/test/main.tok > "$lm_dir"/datasets/test-source/main.tok
  cut -f 2 "$lm_dir"/datasets/test/main.tok > "$lm_dir"/datasets/test-target/main.tok
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

mccoy_url=https://github.com/tommccoy1/rnn-hierarchical-biases/raw/f34a87c4fe804cb288d0527daa9c251def0ae24e/data

download_mccoy_dataset() {
  download_dataset "$mccoy_url" "$@"
}

mueller_url=https://github.com/sebschu/multilingual-transformations/raw/e848833f2df7674022ef02e2b649482d23ade7a7/data

download_mueller_dataset() {
  download_dataset "$mueller_url" "$@"
}

name=question-formation
download_mccoy_dataset $name question
python move_first.py \
  < "$data_dir"/lm/$name/datasets/generalization-source/main.tok \
  > "$data_dir"/lm/$name/datasets/generalization-wrong-target/main.tok

name=tense-reinflection
download_mccoy_dataset $name tense
python agree_recent.py \
  < "$data_dir"/lm/$name/datasets/generalization-source/main.tok \
  > "$data_dir"/lm/$name/datasets/generalization-wrong-target/main.tok

name=tense-reinflection-with-do
download_mccoy_dataset $name tense_aux
python agree_recent.py --with-do \
  < "$data_dir"/lm/$name/datasets/generalization-source/main.tok \
  > "$data_dir"/lm/$name/datasets/generalization-wrong-target/main.tok

name=question-formation-with-have
download_mueller_dataset $name question_have-havent_en/question_have
python move_first.py \
  < "$data_dir"/lm/$name/datasets/generalization-source/main.tok \
  > "$data_dir"/lm/$name/datasets/generalization-wrong-target/main.tok

name=question-formation-in-german
download_mueller_dataset $name question_have-can_withquest_de/question_have_can.de
python move_first.py \
  < "$data_dir"/lm/$name/datasets/generalization-source/main.tok \
  > "$data_dir"/lm/$name/datasets/generalization-wrong-target/main.tok

name=passivization
download_mueller_dataset $name passiv_en_nps/passiv_en_nps
python move_second.py --language en \
  < "$data_dir"/lm/$name/datasets/generalization-source/main.tok \
  > "$data_dir"/lm/$name/datasets/generalization-wrong-target/main.tok

name=passivization-in-german
url=$mueller_url
local_name=$name
external_name=passiv_de_nps/passiv_de_nps
lm_dir=$data_dir/lm/$local_name
mkdir -p "$lm_dir"/datasets/{validation,test,generalization}
# Fix a bug in the original dataset.
curl -L "$url"/"$external_name".train | python fix_passivization_in_german.py > "$lm_dir"/main.tok
curl -L "$url"/"$external_name".dev | python fix_passivization_in_german.py > "$lm_dir"/datasets/validation/main.tok
curl -L "$url"/"$external_name".test | python fix_passivization_in_german.py > "$lm_dir"/datasets/test/main.tok
curl -L "$url"/"$external_name".gen | python fix_passivization_in_german.py > "$lm_dir"/datasets/generalization/main.tok
postprocess_dataset $name
python move_second.py --language de \
  < "$data_dir"/lm/$name/datasets/generalization-source/main.tok \
  > "$data_dir"/lm/$name/datasets/generalization-wrong-target/main.tok
