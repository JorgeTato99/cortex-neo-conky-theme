# Docker contexts and Compose projects

```bash
cortex-neo containers
cortex-neo containers --format json
```

A bounded background worker observes configured local `default` and `desktop-linux` endpoints independently every fifteen seconds. The card separates Engine and Desktop counts and reports unavailable/stale endpoints honestly. One endpoint's failure does not invent a zero count or block hardware sampling.

Container details are grouped using Compose project/service labels, with ordinary containers in their own group. The CLI exposes names, states and a limited list of published ports. Queries use read-only GET requests on local Unix sockets: response sizes, container counts and port counts are bounded (1 MiB, one hundred containers, sixteen ports per container).

The collector never starts containers or calls prune/stop/remove. It does not inspect environment variables, command arguments, volume contents or application secrets. Project/service labels are local identifiers and can still be sensitive. Presentation mode hides labels on the dashboard, without deleting local data.

Docker Desktop uses a guest VM on Linux. Host QEMU RSS and guest container memory are different accounting scopes. See [memory](memory.md) before summing them or changing Docker resources. Missing Docker hides optional Docker content; the rest of the theme remains useful.
