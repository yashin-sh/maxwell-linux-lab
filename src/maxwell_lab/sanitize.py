from __future__ import annotations

import os
import re
from typing import Any


MAC_RE = re.compile(r"\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b")
UUID_RE = re.compile(
    r"\b[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[1-5][0-9A-Fa-f]{3}-"
    r"[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}\b"
)
HOME_RE = re.compile(r"/home/[A-Za-z0-9._-]+")
SERIAL_VALUE_RE = re.compile(r"(?i)\bserial(?: number)?\s*[:=]\s*\S+")


class UnsafePublicOutput(ValueError):
    """Raised when supposedly public output still contains sensitive-looking data."""


def _probe_stdout(probe: Any) -> str:
    if isinstance(probe, dict):
        value = probe.get("stdout", "")
        return value if isinstance(value, str) else ""
    return ""


def _graphics_blocks(lspci_stdout: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    keep = False

    for line in lspci_stdout.splitlines():
        starts_device = bool(line and not line[0].isspace())
        if starts_device:
            if current and keep:
                blocks.append("\n".join(current))
            current = [line]
            keep = any(
                token in line
                for token in (
                    "VGA compatible controller",
                    "3D controller",
                    "Display controller",
                )
            )
        elif current:
            current.append(line)

    if current and keep:
        blocks.append("\n".join(current))

    return blocks


def _selected_vulkan_lines(stdout: str) -> list[str]:
    prefixes = (
        "Vulkan Instance Version:",
        "deviceName",
        "driverName",
        "driverInfo",
        "apiVersion",
        "driverVersion",
        "deviceType",
    )
    lines: list[str] = []
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if line.startswith(prefixes) and "UUID" not in line.upper():
            lines.append(line)
    return lines


def _selected_glx_lines(stdout: str) -> list[str]:
    prefixes = (
        "OpenGL vendor string:",
        "OpenGL renderer string:",
        "OpenGL core profile version string:",
        "OpenGL version string:",
    )
    return [
        line.strip()
        for line in stdout.splitlines()
        if line.strip().startswith(prefixes)
    ]


def build_public_snapshot(inventory: dict[str, Any]) -> dict[str, Any]:
    """Return an allowlisted, commit-safe subset of a raw inventory.

    Public output is reconstructed from approved fields instead of recursively
    redacting arbitrary raw data. New raw probes therefore stay private until
    they are explicitly reviewed and added to this allowlist.
    """

    platform_data = inventory.get("platform", {})
    os_release = inventory.get("os_release", {})
    hardware = inventory.get("hardware", {})
    graphics = inventory.get("graphics", {})
    session = inventory.get("session", {})

    snapshot: dict[str, Any] = {
        "schema_version": 1,
        "system": {
            "os": os_release.get("PRETTY_NAME"),
            "kernel": platform_data.get("release"),
            "architecture": platform_data.get("machine"),
            "system_vendor": hardware.get("system_vendor"),
            "product_name": hardware.get("product_name"),
            "product_version": hardware.get("product_version"),
            "bios_vendor": hardware.get("bios_vendor"),
            "bios_version": hardware.get("bios_version"),
            "bios_date": hardware.get("bios_date"),
            "cpu_model": hardware.get("cpu_model"),
            "memory_total_kib": hardware.get("memory_total_kib"),
        },
        "session": {
            "type": session.get("type"),
            "desktop": session.get("desktop"),
        },
        "graphics": {
            "pci_graphics_blocks": _graphics_blocks(
                _probe_stdout(graphics.get("lspci"))
            ),
            "drm_devices": graphics.get("drm_devices", []),
            "drm_connectors": graphics.get("drm_connectors", []),
            "vulkan": _selected_vulkan_lines(
                _probe_stdout(graphics.get("vulkan_summary"))
            ),
            "opengl": _selected_glx_lines(
                _probe_stdout(graphics.get("opengl_summary"))
            ),
            "nvidia_smi": _probe_stdout(graphics.get("nvidia_smi")),
            "nouveau_pstates": graphics.get("nouveau_pstates", []),
            "nvidia_pci_runtime_pm": graphics.get("nvidia_pci_runtime_pm", []),
            "prime_providers": _probe_stdout(graphics.get("prime_providers")),
        },
    }

    def compact(value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: compact(item)
                for key, item in value.items()
                if item is not None and item != "" and item != []
            }
        if isinstance(value, list):
            return [compact(item) for item in value]
        return value

    return compact(snapshot)


def assert_public_safe(text: str, *, inventory: dict[str, Any] | None = None) -> None:
    """Fail closed if public text contains common identifying values."""

    findings: list[str] = []

    if MAC_RE.search(text):
        findings.append("MAC address")
    if UUID_RE.search(text):
        findings.append("UUID")
    if HOME_RE.search(text):
        findings.append("home-directory path")
    if SERIAL_VALUE_RE.search(text):
        findings.append("serial number")

    literals = {
        os.environ.get("USER"),
        os.environ.get("LOGNAME"),
        os.environ.get("HOME"),
    }
    if inventory:
        hostname = inventory.get("platform", {}).get("hostname")
        if isinstance(hostname, str):
            literals.add(hostname)

    for literal in sorted(item for item in literals if item and len(item) >= 3):
        if literal in text:
            findings.append(f"sensitive literal: {literal!r}")

    if findings:
        unique = ", ".join(dict.fromkeys(findings))
        raise UnsafePublicOutput(f"public output rejected: {unique}")
