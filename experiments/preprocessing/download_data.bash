set -euo pipefail
. experiments/include.bash

bash experiments/run.bash cpu bash download_mccoy_etal_2020.bash "$BASE_DIR"
