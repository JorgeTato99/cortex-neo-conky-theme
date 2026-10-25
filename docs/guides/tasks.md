# Measure development commands

From your project directory:

```bash
cortex-neo run --label frontend-tests -- npm test
cortex-neo run --label rust-tests --timeout 900 -- cargo test
cortex-neo tasks
cortex-neo tasks --format json
```

`run` executes explicit argv without an implicit shell, preserving stdout/stderr and the command exit code; its summary goes to stderr. Invoke a shell explicitly if needed. It does not change your working directory, install tools or inject extra commands.

Private records keep your label, duration, outcome, observed CPU and process-tree peak RSS. They never store argv, environment, working directory or output. Opt-in 0.2-second sampling follows only task identities (PID plus birth time), bounded to 4096. Unobserved resource values are null.

Brief/detached descendants and peaks can be missed. Shared RSS is not private memory. Work delegated to an existing Docker daemon is outside the client process tree and is not fully attributable. Compare equal labels/conditions; isolated differences do not prove regression.

Without timeout the command keeps its natural duration. Timeout accepts 0.1 seconds to seven days and returns 124; interruption returns 130. Cancellation targets the created process group and verified owned identities, tries termination and then bounded forced shutdown. Known remaining descendants are reported. This is not a sandbox or resource quota; permission failures do not trigger privilege escalation.

Ten owned private records are retained under `~/.local/state/cortex-neo/tasks/`. Launch failure is recorded too: 127 for a missing program, 126 for insufficient permissions.
