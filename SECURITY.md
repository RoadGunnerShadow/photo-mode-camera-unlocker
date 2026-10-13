# Security Policy

## Scope

PMCU injects into game processes to unlock a free-camera photo mode. That
means it touches live process memory. Security-relevant surface:

- **Plugin loader** — loads Python plugins from `src/pmcu/injectors/` and
  external plugin dirs listed in `config/default.yaml`. Plugins run with
  full process privileges. Treat plugin dirs as trusted-only.
- **Native shim** — `native/pmcu_shim.dll` is loaded into the target
  process. A tampered shim is a code-execution primitive in that process.
- **Signature packs** — YAML under `src/pmcu/signatures/`. Malformed packs
  are rejected at load; they never reach the scanner unvalidated.

## Reporting

Open a private security advisory on the repo. Include:

- PMCU version (`pmcu --version`)
- Target title + build hash
- Minimal signature pack or plugin that reproduces
- Whether the shim was loaded or the Python-only path was used

## Supported versions

Only the latest minor release receives fixes. Signature packs are
community-maintained and update independently of the host.

## Hardening notes

- The host never auto-loads plugins from the current working directory.
- Plugin dirs must be absolute paths; symlinked plugin roots are rejected.
- The native shim is signature-checked against a pinned SHA-256 before load.

## Out of scope

- Anti-cheat evasion. PMCU targets offline/photo-mode contexts. If your
  title runs an anti-cheat in the same process, PMCU is not for you.
- Bypass of DRM or license checks. Not a goal, not supported.