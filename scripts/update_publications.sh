#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f ".venv/bin/activate" ]]; then
  echo "Error: .venv/bin/activate not found. Create virtualenv first." >&2
  exit 1
fi

source .venv/bin/activate

python scripts/bibtex_to_markdown.py --clean
python scripts/validate_content.py

deactivate

make build
make up
make ps

echo "Publication update workflow completed."
