"""Plugin registry — tracks loaded injector plugins and their metadata."""

from __future__ import annotations

from dataclasses import dataclass

from pmcu.contracts.injector import InjectorPlugin, PluginMeta


@dataclass(slots=True)
class _Entry:
    plugin: InjectorPlugin
    origin: str


class Registry:
    def __init__(self) -> None:
        self._entries: dict[str, _Entry] = {}

    def add(self, plugin: InjectorPlugin, origin: str) -> None:
        slug = plugin.meta.slug
        if slug in self._entries:
            raise ValueError(f"duplicate plugin slug: {slug}")
        self._entries[slug] = _Entry(plugin=plugin, origin=origin)

    def get(self, slug: str) -> InjectorPlugin:
        return self._entries[slug].plugin

    def all(self) -> list[InjectorPlugin]:
        return [e.plugin for e in self._entries.values()]

    def describe(self) -> list[PluginMeta]:
        return [e.plugin.meta for e in self._entries.values()]

    def remove(self, slug: str) -> None:
        self._entries.pop(slug, None)

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, slug: object) -> bool:
        return slug in self._entries