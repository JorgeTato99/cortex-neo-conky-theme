#!/usr/bin/env bash
# Run the same source checks locally and in GitHub Actions; no desktop is needed.
set -euo pipefail

project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
cd -- "$project_root"
python_bin="${PYTHON:-python3}"

ruff check cortex_neo tests scripts
ruff format --check cortex_neo tests scripts
stylua --check theme
for script in scripts/*.sh; do
    bash -n "$script"
done
"$python_bin" scripts/check_docs.py
"$python_bin" -m unittest discover -s tests -v
