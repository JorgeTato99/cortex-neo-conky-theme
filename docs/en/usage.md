# CÓRTEX NEO command guide

Run commands as your desktop user. If necessary, replace `cortex-neo` with
`~/.local/bin/cortex-neo`. Collection/cards belong to the graphical session;
version information and dependency-only diagnostics also work without it.

## Basic control

```bash
cortex-neo version --format json
cortex-neo start
cortex-neo stop
cortex-neo restart
cortex-neo status
cortex-neo doctor
cortex-neo doctor --dependencies-only
```

`version` reports the manifest version, observed revision, local source
fingerprint and whether measured sources match their installation record.
Unknown metadata stays unknown. The fingerprint covers maintained source files,
not personal data, system packages or the virtual environment. It is not a
publisher signature. `--version` is a convenience alias.

## Presentation preferences

```bash
cortex-neo configure --palette contrast --opacity 1
cortex-neo configure --hide weather calendar --anchor left
cortex-neo configure --hide --anchor right
cortex-neo configure --profile auto --density comfortable
```

Palettes: `neon`, `contrast`, `amber`. Opacity: 0–1. Hidden cards use IDs `cpu`,
`ram`, `gpu`, `storage`, `network`, `software`, `weather`, `calendar`; the system
header stays visible. An empty `--hide` clears that list. Cards without data
remain absent. Profiles: `full`, `compact`, `auto`; densities: `complete`,
`comfortable`. Automatic mode selects compact below 1100 application pixels in
width or 650 in height. Internal fit scale is distinct from desktop scaling.

Settings are in `~/.config/cortex-neo/`, outside installed code, and survive
updates. Visual changes are detected in roughly ten seconds. Weather needs a
manual city and public city-center coordinates; see the
[configuration guide](../getting-started/configuration.md).

## Selected context and references

```bash
cortex-neo context
cortex-neo context --format json
cortex-neo inventory
cortex-neo baseline-save --name validated-build
cortex-neo baselines
cortex-neo compare --name validated-build
cortex-neo baseline-export --name validated-build > ~/reference-context.json
cortex-neo compare --input ~/other-machine-context.json
cortex-neo baseline-remove --name validated-build
```

Context is a selected observation, not a complete software inventory or the
active virtual environment of a project. Software has its own observation age.
No automatic machine discovery or synchronization happens. Transfer files
explicitly when comparing machines. Imported version-one JSON is limited to 1 MiB.

Names cannot be overwritten, including case-only duplicates. Up to twenty
references are retained until explicit removal; reaching capacity fails without
displacing an older reference. Partial inventories remain uncertain, and a
difference does not prove the cause of a build failure.

## Resource interpretation

```bash
cortex-neo performance --seconds 15
cortex-neo memory
cortex-neo memory --pid 1234
cortex-neo containers
cortex-neo containers --format json
```

Performance measures only CÓRTEX's service trees. One-core CPU percent differs
from whole-machine CPU percent. Summed RSS includes shared pages and can count
them more than once. PSS/USS is slower and requested only for up to five explicit
PIDs. Missing/denied readings are not zeros. Memory PSI measures observed waiting,
not an automatically identified culprit. A QEMU process is a VM, not necessarily
Docker Desktop; a VM and its guest containers are overlapping accounting scopes.

Container inventory is read-only, separated by context and Compose labels.
Unlabelled containers are not guessed to belong to a project. Queries have
timeouts/size limits, run in one worker and refresh approximately every 15 s.
No container commands, secrets, environments or volume contents are collected.

## Incidents and long history

```bash
cortex-neo incident --label slow-tests --before 240 --after 60
cortex-neo incident --label recent-only --after 0
cortex-neo incidents
cortex-neo incident-export --id INCIDENT_ID
cortex-neo history --hours 6 --format json
cortex-neo configure --history-hours 24
```

Incident capture reads the existing cache: up to four minutes before and one
minute after the marker. Ctrl+C saves a partial capture. Ten private captures,
at most 200 points each, retain summarized process names; exports omit labels,
process/disk identities and paths. Missing data remains a gap.

Long history stores numerical per-minute counts/minima/maxima/averages without
process names. Default retention is 24 h, configurable to 1–168 h or zero to
stop recording. Disabling does not delete existing data. Publication may lag by
one minute; a normal shutdown flushes the current aggregate. Unexpected power
loss can lose that unflushed minute. Retention is applied while collecting.

## Explicit task measurement

```bash
cortex-neo run --label backend-tests -- npm test
cortex-neo run --label rust-tests --timeout 900 -- cargo test
cortex-neo tasks --format json
```

The program runs directly with inherited output and its original exit code.
The summary goes to stderr. Records contain label, elapsed time, result and
observed process-tree resources, not command arguments, environment, working
directory or output. Ten records are retained. Short-lived/detached descendants
and work in external daemons can be missed. This is measurement, not a sandbox.

Timeout returns 124; Ctrl+C returns 130. Only the created process group and
verified identities are signalled. Missing permissions or detached descendants
can leave cleanup incomplete, which the record reports without escalation.

## Screen sharing and support

```bash
cortex-neo presentation --on
cortex-neo presentation --off
cortex-neo presentation --on --minutes 30
cortex-neo report
cortex-neo report --format json
```

Wait for the **Presentación** header before recording. The dashboard hides
hostname, process/application tops, mount paths, network interface, build details
and weather. Other applications and private records are unaffected. Hardware
and versions remain visible; this is not full anonymization.

The flag lives in private user runtime storage, not persistent preferences.
Without an explicit expiry it remains until disabled or runtime cleanup. Linger
may keep it across logouts. Restarting CÓRTEX does not unmask it. Corrupt or
unreadable flags keep masking enabled. Optional expiry is 1–480 minutes.

Support reports select fields and statuses; they do not attach screenshots,
raw logs, user environment or personal labels, and never send anything. Review
the preview before sharing. For a separate desktop capture, `cortex-neo capture`
uses the normal portal and may require interactive session consent.

## Update, recover, uninstall

Download/extract fresh source, then run `bash scripts/install.sh` from it.
The new environment is prepared before the active installation changes.
Preferences and local records are preserved. Failed activation attempts restore
the previous runtime/controls. See [maintenance](../getting-started/updates-and-uninstall.md).

```bash
cortex-neo uninstall
```

Uninstall removes owned program files/controls, preserving personal settings,
caches and records. It does not uninstall shared system dependencies. Private
data uses XDG directories; see [privacy](../reference/privacy.md).
