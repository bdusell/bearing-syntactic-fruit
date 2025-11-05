set -euo pipefail

usage() {
  echo "Usage: bash $0 <base-directory> <task-style> <dataset-name> <model-dir>"
}

base_dir=${1-}
task_style=${2-}
dataset_name=${3-}
model_dir=${4-}
if ! shift 4; then
  usage >&2
  exit 1
fi

dataset_dir=$base_dir/data/$task_style/$dataset_name
eval_dir=$model_dir/eval
ce_dir=$eval_dir/cross-entropy
prob_dir=$eval_dir/probability
greedy_dir=$eval_dir/greedy
fine_dir=$eval_dir/fine-accuracy
case $task_style in
  lm)
    rau lm evaluate \
      --load-model "$model_dir" \
      --training-data "$dataset_dir" \
      --input test \
      --input generalization \
      --output "$ce_dir"
    rau lm evaluate \
      --load-model "$model_dir" \
      --training-data "$dataset_dir" \
      --prompt-and-input test-{source,target} \
      --prompt-and-input generalization-{source,target} \
      --prompt-and-input generalization-{source,wrong-target} \
      --granularity position \
      --output "$prob_dir"
    for d in test-target generalization-target generalization-wrong-target; do
      output_file=$prob_dir/$d.json
      echo "writing $output_file"
      python mean_probability.py "$prob_dir"/"$d".pt > "$output_file"
    done
    output_file=$prob_dir/generalization-ratio.txt
    echo "writing $output_file"
    python generalization_ratio.py "$prob_dir"/generalization{,-wrong}-target.pt > "$output_file"
    rau lm generate \
      --load-model "$model_dir" \
      --training-data "$dataset_dir" \
      --prompt test-source generalization-source \
      --output "$greedy_dir" \
      --mode greedy \
      --max-length 100
    mkdir -p "$fine_dir"
    case $dataset_name in
      question-formation)
        for d in test generalization generalization-wrong; do
          output_file=$fine_dir/$d.txt
          echo "writing $output_file"
          python first_word_accuracy.py "$prob_dir"/"$d"-target.pt > "$output_file"
        done
        ;;
      tense-reinflection)
        rau lm generate \
          --load-model "$model_dir" \
          --training-data "$dataset_dir" \
          --prompt test-source generalization-source \
          --output "$fine_dir" \
          --random-seed 123 \
          --num-samples 10 \
          --max-length 50 \
          --batching-max-tokens 512
        for d in test generalization; do
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
    ;;
  ss)
    echo ss not implemented >&2
    exit 1
    ;;
  *) exit 1 ;;
esac
rm -- "$prob_dir"/{test,generalization,generalization-wrong}-target.pt
for d in test generalization; do
  output_file=$greedy_dir/$d.txt
  echo "writing $output_file"
  python full_match.py \
    "$greedy_dir"/"$d"-source.tok \
    "$dataset_dir"/datasets/"$d"-target/main.tok \
    > "$output_file"
done
output_file=$greedy_dir/generalization-wrong.txt
echo "writing $output_file"
python full_match.py \
  "$greedy_dir"/generalization-source.tok \
  "$dataset_dir"/datasets/generalization-wrong-target/main.tok \
  > "$output_file"
