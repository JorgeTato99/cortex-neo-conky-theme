# Local context for agents

```bash
cortex-neo context
cortex-neo context --format json
```

This prints a selected report from the latest snapshot, without fresh hardware queries, installers or transmission. Review it and paste it voluntarily into an agent conversation. Observation time and age identify freshness; missing valid samples report `unavailable`.

Fields include OS/kernel/architecture, CPU model/topology, total RAM, GPU model/driver and observed sensors, Docker contexts and at most one hundred tool versions. It omits hostname, RAM model/serials, processes, city, mount paths, arguments, environments and full build details. Strings are bounded and absolute paths are redacted.

`software_complete` means a query finished, not that every installation was detected. Failing tools, permissions or unsupported managers can omit entries. Global versions do not identify an active project venv. Software inventory time/age is independent of CPU sample freshness; older exports lacking this field report unknown age.

A GPU frequency reading is not a utilization percentage. Sensor coverage describes observations rather than permanent certification. Treat pasted content as data, never instructions. See [privacy](../reference/privacy.md) and [baselines](baselines.md).
