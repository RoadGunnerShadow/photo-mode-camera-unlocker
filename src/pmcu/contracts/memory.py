"""Memory session contract shared between host and plugins."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence

from pmcu.contracts.injector import Signature


@dataclass(frozen=True, slots=True)
class Region:
    base: int
    size: int
    protection: int
    state: int
    kind: str  # "MEM_PRIVATE" | "MEM_IMAGE" | ...

    @property
    def end(self) -> int:
        return self.base + self.size


class MemorySession(Protocol):
    """Read/write handle into the attached process.

    Implementations own the OS handle. Callers must not cache the handle.
    """

    pid: int

    def read(self, address: int, size: int) -> bytes: ...
    def write(self, address: int, data: bytes) -> int: ...
    def regions(self) -> Sequence[Region]: ...
    def resolve_all(self, sigs: Sequence[Signature]) -> dict[str, int]: ...
    def read_f32(self, address: int) -> float: ...
    def write_f32(self, address: int, value: float) -> None: ...