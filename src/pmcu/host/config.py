"""Host configuration model."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class HostSection(BaseModel):
    name: str = "photo-mode-camera-unlocker"
    version: str = "0.6.3"
    log_level: str = "INFO"
    plugin_dirs: list[str] = Field(default_factory=lambda: ["src/pmcu/injectors"])
    hot_reload: bool = True
    reload_debounce_ms: int = 400


class AttachSection(BaseModel):
    strategy: str = "name"
    target_name: str | None = None
    open_process_flags: int = 0x001F0FFF
    retry_ms: int = 250
    retry_budget_ms: int = 15000


class MemorySection(BaseModel):
    page_size: int = 4096
    scan_chunk_bytes: int = 1 << 20
    max_scan_regions: int = 4096
    region_filter: list[str] = Field(default_factory=lambda: ["MEM_PRIVATE", "MEM_IMAGE"])


class NativeSection(BaseModel):
    shim_path: str = "native/build/pmcu_shim.dll"
    verify_sha256: bool = True
    load_method: str = "createremotethread"


class PhotoModeSection(BaseModel):
    detach_camera: bool = True
    unlock_fov: bool = True
    unlock_roll: bool = True
    unlock_focus_distance: bool = True
    freeze_world: bool = False
    default_fov_deg: float = 60.0
    fov_range_deg: tuple[float, float] = (10.0, 170.0)


class InputSection(BaseModel):
    camera_bindings: dict[str, str] = Field(default_factory=dict)
    speed_default: float = 4.0
    speed_fast_multiplier: float = 5.0


class TelemetrySection(BaseModel):
    enabled: bool = False
    endpoint: str | None = None


class HostConfig(BaseModel):
    host: HostSection = Field(default_factory=HostSection)
    attach: AttachSection = Field(default_factory=AttachSection)
    memory: MemorySection = Field(default_factory=MemorySection)
    native: NativeSection = Field(default_factory=NativeSection)
    photo_mode: PhotoModeSection = Field(default_factory=PhotoModeSection)
    input: InputSection = Field(default_factory=InputSection)
    telemetry: TelemetrySection = Field(default_factory=TelemetrySection)

    @classmethod
    def from_yaml(cls, path: Path) -> "HostConfig":
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return cls.model_validate(raw)