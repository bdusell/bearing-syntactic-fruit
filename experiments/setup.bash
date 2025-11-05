exec bash experiments/singularity_exec.bash cpu bash -c '
  set -euo pipefail
  . experiments/include.bash
  bash scripts/install_python_packages.bash
  cd src
  bash download_mccoy_etal_2020.bash "$BASE_DIR"
'
