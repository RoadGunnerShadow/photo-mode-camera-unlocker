"""Injector plugin contract.

Every injector plugin subclasses `InjectorPlugin` and implements the four
lifecycle hooks. The host calls them in order:

    on_load(session)  -> resolve signatures, cache addresses
    on_enable()       -> write patches, arm the free-camera path
    on_tick(dt_ms)    -> per-frame camera state update
    on_disable()      -> restore original bytes

`session` is a MemorySession owned by the host. Plugins never open their
own handles.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from pmcu.contracts.memory import MemorySession


@dataclass(frozen=True, slots=True)
class Signature:
    """A byte pattern with a wildcard mask.

    `pattern` uses '?' for wildcard nibbles; `offset` is added to the match
    address before use. `resolve` names the logical target (e.g. 'camera_cb').
    """

    name: str
    pattern: str
    offset: int = 0
    resolve: str = ""


@dataclass(frozen=True, slots=True)
class PluginMeta:
    slug: str
    title: str
    version: str
    author: str = "unknown"
    build_hashes: tuple[str, ...] = field(default_factory=tuple)


class InjectorPlugin(ABC):
    """Base class for title-specific free-camera injectors."""

    meta: PluginMeta
    signatures: tuple[Signature, ...] = ()

    def __init__(self) -> None:
        self._session: MemorySession | None = None
        self._resolved: dict[str, int] = {}
        self._enabled = False

    # -- lifecycle -------------------------------------------------------

    def on_load(self, session: MemorySession) -> None:
        self._session = session
        self._resolved = session.resolve_all(self.signatures)

    def on_enable(self) -> None:
        if self._session is None:
            raise RuntimeError(f"{self.meta.slug}: on_enable before on_load")
        self._enabled = True

    def on_tick(self, dt_ms: float) -> None:
        return None

    def on_disable(self) -> None:
        self._enabled = False

    # -- helpers for subclasses -----------------------------------------

    @property
    def session(self) -> MemorySession:
        if self._session is None:
            raise RuntimeError(f"{self.meta.slug}: session not bound")
        return self._session

    def addr(self, name: str) -> int:
        try:
            return self._resolved[name]
        except KeyError as exc:
            raise KeyError(f"{self.meta.slug}: unresolved signature {name!r}") from exc

    @property
    def enabled(self) -> bool:
        return self._enabled

    # -- registration ----------------------------------------------------

    @abstractmethod
    def register(self, host: "PluginHostLike") -> None:
        """Register handlers/commands with the host."""


class PluginHostLike:
    """Structural type for the host passed to `register`."""

    def on(self, event: str, fn) -> None:  # pragma: no cover - protocol
        raise NotImplementedError