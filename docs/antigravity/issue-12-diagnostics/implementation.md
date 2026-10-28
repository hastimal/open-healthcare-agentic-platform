# Issue 12: demo launcher diagnostics

This is an incremental community contribution, not a release milestone. No
version changes, releases or milestone tags are included.

The existing Compose launcher retains its service readiness probes, browser
option and observability URLs. New diagnostics resolve Compose configuration
instead of guessing host ports, exempt this project's existing publishers and
probe the other bindings before startup. A failed readiness probe now returns
nonzero instead of announcing that every service is ready.

`--check-only` and `--status` are read-only modes. Docker commands and HTTP calls
have bounded timeouts. Ollama checks use the configured exact model; missing
inference remains a warning on normal startup to preserve fallback behavior.
Interactive terminals offer a port retry; non-interactive runs never prompt.
Output supports legacy Windows encodings and optional terminal colors.

The packaged native launcher has a different scope: it manages local Python
service processes, not Compose publishers and observability services. This
change leaves that launcher and the clinical/retrieval code untouched.

Tests isolate subprocess/HTTP/browser boundaries and include a real bound socket.
A dependency-free CI matrix runs the launcher tests on Ubuntu, macOS and Windows.
The developer guide covers environment-specific setup and troubleshooting.

A package-version regression test checks that an uninstalled source checkout
reports the declared project version, guarding local setup without installed
distribution metadata. It does not change package or clinical code.

PR #15 is a separate unmerged proposal for the same issue. This implementation
is based on current main and preserves the original multi-service startup path.

## Stale and Missing Port Detection (Community Integration Polish)
- Added `detect_stale_ports`: compares running container port bindings reported by
  `docker compose ps` against the resolved Compose configuration, detecting if
  containers are publishing outdated bindings or port changes.
- Added `detect_missing_ports`: checks that running services publish all expected
  ports specified in the effective Compose configuration, flagging unbound services.
- Supported wildcard canonicalization (`0.0.0.0`, `::`, `""`) to prevent false
  stale/missing positives on dual-stack IPv4/IPv6 host systems.
- Expanded regression tests covering correct port matches, stale bindings, missing
  bindings, and socket port conflicts.

