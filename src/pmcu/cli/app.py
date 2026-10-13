"""PMCU command-line entry point.

Wires config -> host -> loader -> session. The CLI is thin: it parses
flags, builds a HostConfig, and hands control to the host loop.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pmcu.host.config import HostConfig
from pmcu.host.host import PluginHost
from pmcu.services.attach import AttachService
from pmcu.utils.log import configure_logging, get_logger

log = get_logger(__name__)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pmcu",
        description="Free-camera photo mode injector (plugin host).",
    )
    p.add_argument("--config", type=Path, default=Path("config/default.yaml"))
    p.add_argument("--target", type=str, default=None, help="Target process name.")
    p.add_argument("--pid", type=int, default=None, help="Attach to explicit PID.")
    p.add_argument("--list-plugins", action="store_true")
    p.add_argument("--version", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.version:
        from pmcu import __version__

        print(__version__)
        return 0

    cfg = HostConfig.from_yaml(args.config)
    configure_logging(cfg.host.log_level)

    if args.list_plugins:
        host = PluginHost(cfg)
        host.discover()
        for meta in host.registry.describe():
            print(f"{meta.slug:<24} {meta.title:<32} {meta.version}")
        return 0

    attach = AttachService(cfg.attach)
    host = PluginHost(cfg, attach=attach)

    if args.pid is not None:
        attach.attach_pid(args.pid)
    elif args.target is not None:
        attach.attach_name(args.target)

    try:
        host.run()
    except KeyboardInterrupt:
        log.info("interrupted, detaching")
        host.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())