set -euo pipefail
. experiments/include.bash

bash experiments/run.bash cpu bash download_datasets.bash "$BASE_DIR"
