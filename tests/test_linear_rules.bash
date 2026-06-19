set -euo pipefail

src=$(cd "$(dirname "$BASH_SOURCE")"/../src && pwd)

usage() {
  echo "Usage: bash $0 <base-directory>"
}

base_dir=${1-}
if ! shift 1; then
  usage >&2
  exit 1
fi

data_dir=$base_dir/data

# Includes examples from Table 2 of https://aclanthology.org/2022.findings-acl.106/

name=question-formation
diff \
  <((cd "$src" && python move_first.py) < "$data_dir"/lm/$name/datasets/test-source/main.tok) \
  "$data_dir"/lm/$name/datasets/test-target/main.tok

name=tense-reinflection
diff \
  <((cd "$src" && python agree_recent.py) < "$data_dir"/lm/$name/datasets/test-source/main.tok) \
  "$data_dir"/lm/$name/datasets/test-target/main.tok

name=tense-reinflection-with-do
diff \
  <((cd "$src" && python agree_recent.py --with-do) < "$data_dir"/lm/$name/datasets/test-source/main.tok) \
  "$data_dir"/lm/$name/datasets/test-target/main.tok

name=question-formation-with-have
diff \
  <((cd "$src" && python move_first.py) < "$data_dir"/lm/$name/datasets/test-source/main.tok) \
  "$data_dir"/lm/$name/datasets/test-target/main.tok
diff \
  <((cd "$src" && python move_first.py) <<<"my unicorn that hasn't amused the yaks has eaten . quest") \
  <(echo "hasn't my unicorn that amused the yaks has eaten ?")

name=question-formation-in-german
diff \
  <((cd "$src" && python move_first.py) < "$data_dir"/lm/$name/datasets/test-source/main.tok) \
  "$data_dir"/lm/$name/datasets/test-target/main.tok
diff \
  <((cd "$src" && python move_first.py) <<<"die Hunde , die deine Löwen bewundern können , haben gewartet . quest") \
  <(echo "können die Hunde , die deine Löwen bewundern , haben gewartet ?")

name=passivization
diff \
  <((cd "$src" && python move_second.py --language en) < "$data_dir"/lm/$name/datasets/test-source/main.tok) \
  "$data_dir"/lm/$name/datasets/test-target/main.tok
diff \
  <((cd "$src" && python move_second.py --language en) <<<"her walruses above my unicorns annoyed her quail . passiv") \
  <(echo "my unicorns were annoyed by her walruses .")

name=passivization-in-german
diff \
  <((cd "$src" && python move_second.py --language de) < "$data_dir"/lm/$name/datasets/test-source/main.tok) \
  "$data_dir"/lm/$name/datasets/test-target/main.tok
diff \
  <((cd "$src" && python move_second.py --language de) <<<"unsere Papageie bei meinen Dinosauriern bedauerten unsere Esel . passiv") \
  <(echo "meine Dinosaurier wurden von unseren Papageien bedauert .")

echo all tests passed
