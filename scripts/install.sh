#!/usr/bin/env bash
# One user entry point; only distribution package operations elevate privileges.
set -euo pipefail
source_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
exec /usr/bin/python3 -I "$source_root/scripts/manage_installation.py" "$@"
