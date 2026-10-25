"""User-facing controls; systemd owns the sampler and all card processes."""
from cortex_neo.i18n import tr
import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from .io import read_json
from .paths import CACHE, CONFIG, ROOT

def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'run':
        from .tasks import run_cli
        return run_cli(sys.argv[2:])
    parser = argparse.ArgumentParser(prog='cortex-neo', description=tr('CORTEX NEO desktop telemetry'))
    parser.add_argument('action', nargs='?', default='start', choices=['start', 'stop', 'restart', 'status', 'edit', 'capture', 'doctor', 'inventory', 'uninstall', 'performance', 'configure', 'context', 'memory', 'containers', 'incident', 'incidents', 'incident-export', 'history', 'run', 'tasks', 'baseline-save', 'baselines', 'baseline-export', 'baseline-remove', 'compare', 'presentation', 'report', 'version'])
    parser.add_argument('--dependencies-only', action='store_true', help=tr('Diagnostics without a graphical session.'))
    parser.add_argument('--seconds', type=int, default=10, help=tr('Measurement window: 2–60 seconds.'))
    from .palettes import PALETTES
    from .fonts import FONTS
    parser.add_argument('--palette', choices=[*PALETTES, 'neon', 'contrast', 'amber'])
    parser.add_argument('--language', choices=['en', 'es'])
    parser.add_argument('--detail-level', choices=['essential', 'full'])
    parser.add_argument('--font', choices=list(FONTS))
    parser.add_argument('--opacity', type=float)
    parser.add_argument('--hide', nargs='*')
    parser.add_argument('--anchor', choices=['left', 'right'])
    parser.add_argument('--profile', choices=['full', 'compact', 'auto'])
    parser.add_argument('--density', choices=['complete', 'comfortable'])
    parser.add_argument('--format', choices=['text', 'json'], default='text')
    parser.add_argument('--pid', type=int, action='append', default=[])
    parser.add_argument('--label', default='')
    parser.add_argument('--before', type=int, default=240)
    parser.add_argument('--after', type=int, default=60)
    parser.add_argument('--id')
    parser.add_argument('--hours', type=int, default=24)
    parser.add_argument('--history-hours', type=int)
    parser.add_argument('--name')
    parser.add_argument('--input', type=Path)
    presentation_group = parser.add_mutually_exclusive_group()
    presentation_group.add_argument('--on', action='store_true')
    presentation_group.add_argument('--off', action='store_true')
    parser.add_argument('--minutes', type=int)
    parser.add_argument('--version', dest='show_version', action='store_true')
    options = parser.parse_args()
    action = 'version' if options.show_version else options.action
    if action == 'version':
        from .version import version_info
        result = version_info()
        if options.format == 'json':
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(tr('CORTEX NEO ') + result['version'] + tr(' · revision ') + (result['revision'] or tr('unknown')))
            print(tr('Source fingerprint: ') + (result['source_fingerprint'] or tr('unavailable')))
            if result['source_dirty'] is True:
                print(tr('The source had local changes.'))
            print(tr('Matches installed sources: ') + str(result['matches_installed_source']))
        return 0
    if action == 'presentation':
        from .sharing import presentation_state, set_presentation
        try:
            if options.on or options.off:
                result = set_presentation(options.on, minutes=options.minutes)
                time.sleep(2.1)
            else:
                result = presentation_state()
        except ValueError as error:
            parser.error(str(error))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    if action == 'report':
        from .diagnostics import inspect
        from .sharing import support_report, support_text
        diagnostics = inspect(session=not options.dependencies_only)
        result = support_report(read_json(CACHE / 'dashboard.json', {}), diagnostics=diagnostics, layout=read_json(CACHE / 'layout.json', {}))
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) if options.format == 'json' else support_text(result))
        return 0 if diagnostics['ok'] else 1
    if action in ('baseline-save', 'baselines', 'baseline-export', 'baseline-remove', 'compare'):
        from .baselines import compare_contexts, export_baseline, list_baselines, load_context_file, remove_baseline, save_baseline
        from .context import context_report
        try:
            if action == 'baseline-save':
                selected = load_context_file(options.input) if options.input else context_report(read_json(CACHE / 'dashboard.json', {}))
                record = save_baseline(options.name, selected)
                result = {'id': record['id'], 'name': record['name']}
            elif action == 'baselines':
                result = list_baselines()
            elif action == 'baseline-export':
                result = export_baseline(options.name)
            elif action == 'baseline-remove':
                remove_baseline(options.name)
                result = {'removed': options.name}
            else:
                if bool(options.input) == bool(options.name):
                    raise ValueError('Choose exactly one --name reference or --input context file')
                reference = load_context_file(options.input) if options.input else export_baseline(options.name)
                result = compare_contexts(reference, context_report(read_json(CACHE / 'dashboard.json', {})))
        except ValueError as error:
            parser.error(str(error))
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    if action == 'run':
        parser.error(tr('Use cortex-neo run [options] -- command'))
    if action == 'tasks':
        from .tasks import list_tasks
        rows = list_tasks()
        if options.format == 'json':
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            for row in rows:
                print(tr('{p0} · {p1} · {p2} · exit {p3} · {p4:.2f} s').format(p0=row['id'], p1=row['label'], p2=row['status'], p3=row['exit_code'], p4=row['elapsed_seconds']))
            if not rows:
                print(tr('No recorded tasks.'))
        return 0
    if action == 'history':
        from .history import HistoryStore
        from .preferences import load_preferences
        try:
            result = HistoryStore(hours=load_preferences()['history_hours']).query(hours=options.hours)
        except ValueError as error:
            parser.error(str(error))
        if options.format == 'json':
            print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        else:
            print(tr('History: {p0} observed minutes · retention {p1} h').format(p0=len(result['minutes']), p1=result['retention_hours']))
            for minute in result['minutes'][-20:]:
                cells = []
                for key in ('cpu', 'ram', 'gpu'):
                    value = minute['metrics'][key]['average']
                    cells.append(f'{key.upper()} {value:.1f}%' if value is not None else key.upper() + ' —')
                print(datetime.fromtimestamp(minute['minute']).isoformat(timespec='minutes') + ' · ' + ' / '.join(cells))
            print(tr('Missing samples do not mean zero. JSON includes all selected minutes and extrema.'))
        return 0
    if action in ('incident', 'incidents', 'incident-export'):
        from .incidents import capture_incident, list_incidents, load_incident, public_incident
        try:
            if action == 'incident':
                print(tr('Capturing up to {p0} seconds after now; Ctrl+C saves available samples.').format(p0=options.after), file=sys.stderr)
                record = capture_incident(options.label, before=options.before, after=options.after)
                result = {'id': record['id'], 'status': record['status'], 'samples': len(record['points'])}
            elif action == 'incidents':
                result = list_incidents()
            else:
                result = public_incident(load_incident(options.id))
        except ValueError as error:
            parser.error(str(error))
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    if action == 'containers':
        snapshot = read_json(CACHE / 'dashboard.json', {})
        docker = snapshot.get('docker', {}) if isinstance(snapshot, dict) else {}
        docker = docker if isinstance(docker, dict) else {}
        if options.format == 'json':
            print(json.dumps(docker, ensure_ascii=False, indent=2))
        else:
            for context, value in docker.items():
                print(tr('{p0}: {p1} · observed {p2}').format(p0=context, p1=value.get('status', 'unknown'), p2=value.get('sampled_at')))
                for group in value.get('projects', []):
                    print('  ' + group['name'])
                    for item in group['services']:
                        print('    ' + (item['service'] or item['name']) + ' · ' + item['state'] + ' · ' + (', '.join(item['ports']) or tr('no published ports')))
                if value.get('truncated'):
                    print(tr('  View limited to one hundred containers per context.'))
            if not docker:
                print(tr('No Docker inventory is available in this sample.'))
        return 0
    if action == 'memory':
        from .context import context_report
        from .memory import explain_memory, memory_details
        snapshot = read_json(CACHE / 'dashboard.json', {})
        ram = snapshot.get('ram', {}) if isinstance(snapshot, dict) else {}
        ram = ram if isinstance(ram, dict) else {}
        freshness = context_report(snapshot)
        try:
            details = memory_details(options.pid)
        except ValueError as error:
            parser.error(str(error))
        print(json.dumps({'sampled_at': snapshot.get('sampled_at') if isinstance(snapshot, dict) else None, 'fresh': freshness['fresh'], 'interpretation': ('' if freshness['fresh'] else tr('Stale sample. ')) + explain_memory(ram), 'host': ram, 'requested_processes': details, 'accounting': tr('RSS includes shared memory. A VM includes its guest; do not count its containers again on the host.')}, ensure_ascii=False, indent=2))
        return 0
    if action == 'context':
        from .context import context_report, context_text
        report = context_report(read_json(CACHE / 'dashboard.json', {}))
        print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) if options.format == 'json' else context_text(report))
        return 0
    if action == 'configure':
        from .preferences import update_preferences
        try:
            result = update_preferences(palette=options.palette, opacity=options.opacity, hidden=options.hide, anchor=options.anchor, profile=options.profile, density=options.density, history_hours=options.history_hours, language=options.language, detail_level=options.detail_level, font=options.font)
        except ValueError as error:
            parser.error(str(error))
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    if action == 'performance':
        from .observability import profile
        try:
            print(json.dumps(profile(options.seconds, CACHE), indent=2, ensure_ascii=False))
        except ValueError as error:
            parser.error(str(error))
        return 0
    if action in ('start', 'stop', 'restart', 'status'):
        return subprocess.call(['systemctl', '--user', action, 'cortex-neo.service'])
    if action == 'doctor':
        from .diagnostics import main as doctor
        return doctor(session=not options.dependencies_only)
    if action == 'uninstall':
        return subprocess.call([sys.executable, '-I', str(ROOT / 'scripts/manage_installation.py'), '--uninstall'])
    if action == 'inventory':
        value = read_json(CACHE / 'dashboard.json', {})
        print(json.dumps(value.get('software', []) if isinstance(value, dict) else [], ensure_ascii=False, indent=2))
        return 0
    if action == 'capture':
        return subprocess.call([sys.executable, '-I', '-m', 'cortex_neo.capture'])
    if action == 'edit':
        editor = shutil.which('code') or shutil.which('xdg-open')
        if not editor:
            print('No graphical editor is installed. Configuration:', CONFIG, file=sys.stderr)
            return 1
        return subprocess.call([editor, str(ROOT)])
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
