# Contributing to photo-mode-camera-unlocker

`photo-mode-camera-unlocker` (PMCU) is a plugin-host tool that detaches the
in-game photo-mode camera from its authored rail, giving free-camera control
inside supported titles. The host is Python; title-specific injectors are
plugins that speak a shared contract.

## Repository layout

- `src/pmcu/host/` — the plugin host: lifecycle, loader, registry, bus.
- `src/pmcu/contracts/` — shared protocol dataclasses (the ABI plugins compile against).
- `src/pmcu/injectors/` — built-in injector plugins shipped first-party.
- `src/pmcu/signatures/` — pattern-scan signature packs per title build.
- `src/pmcu/services/` — process attach, memory IO, config, telemetry.
- `src/pmcu/utils/` — logging, memory math, address helpers.
- `native/` — C++ injection shim (DLL) for `CreateRemoteThread` load path.
- `dotnet/` — C# signature pack editor (WPF) used by signature maintainers.
- `java/` — JVM-side dump parser for RTTI/typeinfo recovery.
- `config/` — default runtime configuration.
- `tests/` — unit + integration tests for loader, registry, and memory math.

## Adding an injector plugin

1. Create `src/pmcu/injectors/<title_slug>/` with an `__init__.py`.
2. Subclass `InjectorPlugin` from `pmcu.contracts.injector`.
3. Declare `TITLE`, `BUILD_HASHES`, and `SIGNATURES` at module scope.
4. Register via `pmcu.host.registry.register` inside `register(host)`.
5. Add a signature pack under `src/pmcu/signatures/<title_slug>/`.
6. Add a smoke test under `tests/injectors/`.

Plugins must not open their own process handles — the host owns the
handle and passes a `MemorySession` down. This keeps detach/reattach
deterministic across hot-reload.

## Style

- `ruff` clean, `mypy --strict` clean on `src/`.
- No bare `except:` — narrow the exception, log with context.
- Addresses are `int` (absolute virtual address). Offsets are `int`.
  Never mix them in one variable.
- Logging goes through `pmcu.utils.log.get_logger`, never `print`.

## Commit hygiene

- One logical change per commit.
- Reference the title slug and build hash in the message when touching
  a signature pack: `sig(zelda_totk): add 1.2.1 build hash`.

## Testing

```bash
pip install -e ".[dev]"
pytest -q
```

Native shim builds are CI-gated on Windows runners only; PRs touching
`native/` must pass `msbuild /p:Configuration=Release`.

## Legal

This project is for interoperability and modding research on software you
own. Do not use it against online services or other players' sessions.
Use at your own risk.