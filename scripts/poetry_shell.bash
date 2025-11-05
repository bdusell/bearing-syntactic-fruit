set -euo pipefail
exec bash --init-file <(echo 'if [[ -e ~/.bashrc ]]; then . ~/.bashrc; fi && eval $(poetry env activate)')
