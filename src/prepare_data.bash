set -euo pipefail

usage() {
  echo "Usage: bash $0 <base-directory> <dataset-name>"
}

base_dir=${1-}
dataset_name=${2-}
if ! shift 2; then
  usage >&2
  exit 1
fi

dataset_dir=$base_dir/data/$dataset_name
rau lm prepare \
  --training-data "$base_dir"/data/lm/"$dataset_name" \
  --more-data validation \
  --more-data test \
  --more-data test-source \
  --more-data test-target \
  --more-data generalization \
  --more-data generalization-source \
  --more-data generalization-target \
  --more-data generalization-wrong-target \
  --never-allow-unk
rau ss prepare \
  --training-data "$base_dir"/data/ss/"$dataset_name" \
  --vocabulary-types shared \
  --more-data validation \
  --more-data test \
  --more-data generalization
