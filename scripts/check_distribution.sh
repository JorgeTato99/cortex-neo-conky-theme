#!/usr/bin/env bash
# Integration driver restricted to disposable root containers, never a host setup.
set -euo pipefail
if [ "$(id -u)" != 0 ] || [ ! -f /.dockerenv ] || [ "${CORTEX_NEO_TEST_CONTAINER:-}" != 1 ]; then
    printf 'Run only inside a disposable container with CORTEX_NEO_TEST_CONTAINER=1.\n' >&2
    exit 78
fi
source_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install --yes --no-install-recommends sudo ca-certificates python3 systemd \
    liblua5.4-0 xvfb xauth openbox xcompmgr
test_user=cortex-test
useradd --create-home --shell /bin/bash "$test_user"
printf '%s\n' "$test_user ALL=(root) NOPASSWD: /usr/bin/apt-get" > /etc/sudoers.d/cortex-test
chmod 440 /etc/sudoers.d/cortex-test
test_home=$(getent passwd "$test_user" | cut -d: -f6)
runuser -u "$test_user" -- env HOME="$test_home" PYTHONDONTWRITEBYTECODE=1 PYTHONFAULTHANDLER=1 \
    bash -s -- "$source_root" <<'TEST'
set -euo pipefail
cd -- "$1"
bash scripts/install.sh --dry-run
test ! -e "$HOME/.local/share/cortex-neo"
bash scripts/install.sh --no-start
python="$HOME/.local/share/cortex-neo/venv/bin/python"
export XDG_RUNTIME_DIR="$HOME/.test-runtime"
mkdir -m 700 "$XDG_RUNTIME_DIR"
systemd-analyze --user verify "$HOME/.config/systemd/user/cortex-neo.service" \
    "$HOME/.config/systemd/user/cortex-neo-metrics.service"
"$python" -I -m cortex_neo doctor --dependencies-only
"$python" -m unittest discover -s tests -v
printf '%s\n' '{"personal_test": true}' > "$HOME/.config/cortex-neo/settings.json"
bash scripts/install.sh --skip-system-deps --no-start
grep -q personal_test "$HOME/.config/cortex-neo/settings.json"
CORTEX_NEO_HEADLESS_TEST=1 xvfb-run -a -s '-screen 0 1920x1080x24' \
    "$python" scripts/render_smoke.py --output "$HOME/render.png"
CORTEX_NEO_HEADLESS_TEST=1 xvfb-run -a -s '-screen 0 1920x1080x24' \
    "$python" scripts/render_smoke.py --profile compact --density comfortable --output "$HOME/render-compact.png"
CORTEX_NEO_HEADLESS_TEST=1 xvfb-run -a -s '-screen 0 1920x1080x24' \
    "$python" scripts/render_smoke.py --palette purple --font liberation --language es --detail-level essential --output "$HOME/render-spanish.png"
bash scripts/install.sh --uninstall
test ! -e "$HOME/.local/share/cortex-neo"
test -f "$HOME/.config/cortex-neo/settings.json"
test -d "$HOME/.local/state/cortex-neo/backups"
printf 'DISTRIBUTION_CONTRACT_OK\n'
TEST
mkdir -p "$source_root/artifacts"
cp "$test_home/render.png" "$source_root/artifacts/distribution-render.png"
cp "$test_home/render-compact.png" "$source_root/artifacts/distribution-render-compact.png"

cp "$test_home/render-spanish.png" "$source_root/artifacts/distribution-render-spanish.png"
