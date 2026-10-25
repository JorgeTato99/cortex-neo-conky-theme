"""Actionable local checks; diagnostics never contact location or web services."""
from cortex_neo.i18n import tr
import json
import shutil
import subprocess
import sys
from .conky import capabilities
MINIMUM_PYTHON = (3, 11)

def run(argv):
    try:
        return subprocess.run(argv, capture_output=True, text=True, timeout=8, check=False)
    except (OSError, subprocess.SubprocessError) as error:
        return subprocess.CompletedProcess(argv, 1, '', str(error))

def inspect(*, session=True, runner=run, locate=shutil.which, version=None):
    """Report actual imports/connections, not just module or binary presence."""
    checks = []

    def add(name, success, detail, remedy, *, optional=False):
        checks.append(dict(name=name, status='ok' if success else 'warning' if optional else 'error', detail=detail, remedy='' if success else remedy))
    version = tuple(version or sys.version_info[:3])
    add('python', version[:2] >= MINIMUM_PYTHON, '.'.join(map(str, version)), tr('Use Python 3.11 or newer supplied by a supported distribution.'))
    conky = locate('conky')
    banner = runner([conky, '--version']) if conky else None
    build = capabilities(banner.stdout + banner.stderr) if banner else capabilities('')
    add('conky', bool(banner and banner.returncode == 0 and build['version']), build['version'] or tr('Could not query Conky.'), tr('Install conky-all with the installer or package manager.'))
    for name, detail in (('x11', 'backend X11/XWayland'), ('lua', 'callbacks Lua')):
        add('conky_' + name, build[name], detail, tr('Install a Conky build with X11 and Lua; on Ubuntu/Debian: conky-all.'))
    for module in ('psutil', 'gi'):
        script = 'import ' + module
        if module == 'gi':
            script += "; gi.require_version('Gdk', '3.0'); from gi.repository import Gdk"
        result = runner([sys.executable, '-c', script])
        add(module, result.returncode == 0, tr('Actual import in the theme interpreter.'), tr('Reinstall with bash scripts/install.sh; GTK requires the system Python.'))
    for name, family, optional in (('icons', 'FontAwesome', False), ('monospace', 'Ubuntu Sans Mono', True)):
        result = runner(['fc-match', '-f', '%{family}', family])
        actual = result.stdout.strip()
        matched = 'awesome' in actual.lower() if name == 'icons' else family in actual
        add(name, result.returncode == 0 and matched, actual or tr('Font unavailable.'), tr('Install fonts-font-awesome.') if name == 'icons' else tr('Fontconfig fallback is in use; install the selected monospace family if needed.'), optional=optional)
    add('xwininfo', bool(locate('xwininfo')), tr('Measure actual windows.'), tr('Install x11-utils.'))
    if session:
        from .display import import_session_environment
        import_session_environment()
        bus = runner(['systemctl', '--user', 'show-environment'])
        add('user_bus', bus.returncode == 0, tr('Connection to the user systemd manager.'), tr('Run in the desktop user session; do not start the theme with sudo.'))
        display = runner([sys.executable, '-c', "import gi; gi.require_version('Gdk','3.0'); from gi.repository import Gdk; import os,sys; Gdk.set_allowed_backends('x11'); Gdk.init([]); d=Gdk.Display.open(os.environ.get('DISPLAY','')); sys.exit(0 if d is not None and d.get_n_monitors()>0 else 1)"])
        add('display', display.returncode == 0, tr('Actual X11/XWayland connection and active monitor.'), tr('Start a desktop session and check XWayland; use --dependencies-only without a desktop.'))
        for service in ('cortex-neo', 'cortex-neo-metrics'):
            active = runner(['systemctl', '--user', 'is-active', service + '.service'])
            add(service, active.returncode == 0, tr('User service status.'), tr('Run cortex-neo start and inspect journalctl --user -u ') + service, optional=True)
    result = {'ok': not any((c['status'] == 'error' for c in checks)), 'checks': checks, 'conky': build, 'location_mode': 'manual only; no location queries'}
    return result

def main(*, session=True):
    report = inspect(session=session)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['ok'] else 1
