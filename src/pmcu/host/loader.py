"""Plugin loader — discovers and imports injector plugins by path.

Only loads packages that expose a module-level `PLUGIN` object implementing
`InjectorPlugin`. Plugin roots must be absolute; symlinked roots are
rejected (see SECURITY.md).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from pmcu.contracts.injector import InjectorPlugin
from pmcu.utils.log import get_logger

log = get_logger(__name__)


class PluginLoadError(RuntimeError):
    pass


def _import_from_file(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise PluginLoadError(f"cannot build spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def discover(root: Path) -> list[tuple[str, InjectorPlugin]]:
    """Return (origin, plugin) pairs found under `root`.

    Each immediate subdirectory is a plugin package containing `__init__.py`.
    """
    if not root.is_absolute():
        raise PluginLoadError(f"plugin root must be absolute: {root}")
    if root.is_symlink():
        raise PluginLoadError(f"symlinked plugin root rejected: {root}")
    if not root.is_dir():
        raise PluginLoadError(f"plugin root missing: {root}")

    found: list[tuple[str, InjectorPlugin]] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith("_"):
            continue
        init = child / "__init__.py"
        if not init.exists():
            log.debug("skip %s: no __init__.py", child.name)
            continue
        module_name = f"pmcu.injectors.{child.name}"
        try:
            module = _import_from_file(init, module_name)
        except Exception as exc:  # noqa: BLE001 - surface as load error
            log.error("failed to import %s: %s", child.name, exc)
            continue
        plugin = getattr(module, "PLUGIN", None)
        if plugin is None:
            log.warning("skip %s: no PLUGIN object", child.name)
            continue
        if not isinstance(plugin, InjectorPlugin):
            log.warning("skip %s: PLUGIN is not an InjectorPlugin", child.name)
            continue
        found.append((str(child), plugin))
    return found
</｜｜DSML｜｜ parameter>
</｜｜DSML｜｜ invoke>
</｜｜DSML｜｜ calls>