set -euo pipefail

usage() {
  echo "Usage: bash $0 <base-directory> <task-style> <dataset-name> \\
    <model-dir> <dest-dir> <num-examples>"
}

base_dir=${1-}
task_style=${2-}
dataset_name=${3-}
model_dir=${4-}
dest_dir=${5-}
num_examples=${6-}
if ! shift 6; then
  usage >&2
  exit 1
fi

mkdir -p "$dest_dir"
output_file=$dest_dir/num-examples.txt
echo "writing $output_file"
printf %s "$num_examples" > "$output_file"

dataset_dir=$base_dir/data/$task_style/$dataset_name
eval_dir=$dest_dir
ce_dir=$eval_dir/cross-entropy
prob_dir=$eval_dir/probability
fine_dir=$eval_dir/fine-accuracy
case $task_style in
  lm)
    rau lm evaluate \
      --load-model "$model_dir" \
      --training-data "$dataset_dir" \
      --input generalization \
      --output "$ce_dir"
    rau lm evaluate \
      --load-model "$model_dir" \
      --training-data "$dataset_dir" \
      --prompt-and-input generalization-{source,target} \
      --prompt-and-input generalization-{source,wrong-target} \
      --granularity position \
      --output "$prob_dir"
    for d in generalization-target generalization-wrong-target; do
      output_file=$prob_dir/$d.json
      echo "writing $output_file"
      python mean_probability.py "$prob_dir"/"$d".pt > "$output_file"
    done
    output_file=$prob_dir/generalization-ratio.txt
    echo "writing $output_file"
    python generalization_ratio.py "$prob_dir"/generalization{,-wrong}-target.pt > "$output_file"
    mkdir -p "$fine_dir"
    case $dataset_name in
      question-formation)
        for d in generalization generalization-wrong; do
          output_file=$fine_dir/$d.txt
          echo "writing $output_file"
          python first_word_accuracy.py "$prob_dir"/"$d"-target.pt > "$output_file"
        done
        ;;
      tense-reinflection)
        rau lm generate \
          --load-model "$model_dir" \
          --training-data "$dataset_dir" \
          --prompt generalization-source \
          --output "$fine_dir" \
          --random-seed 123 \
          --num-samples 10 \
          --max-length 15 \
          --batching-max-tokens 256
        for d in generalization; do
          output_file=$fine_dir/$d.txt
          echo "writing $output_file"
          python tense_reinflection_fine_accuracy.py \
            "$fine_dir"/"$d"-source.tsv \
            "$dataset_dir"/datasets/"$d"-target/main.tok \
            > "$output_file"
        done
        output_file=$fine_dir/generalization-wrong.txt
        echo "writing $output_file"
        python tense_reinflection_fine_accuracy.py \
          "$fine_dir"/generalization-source.tsv \
          "$dataset_dir"/datasets/generalization-wrong-target/main.tok \
          > "$output_file"
        ;;
    esac
    echo "generalization conditional probability: $(< "$prob_dir"/generalization-target.json)"
    echo "generalization fine accuracy: $(< "$fine_dir"/generalization.txt)"
    ;;
  ss)
    echo ss not implemented >&2
    exit 1
    ;;
  *) exit 1 ;;
esac
rm -- "$prob_dir"/{generalization,generalization-wrong}-target.pt
rm -r -- "$model_dir"
