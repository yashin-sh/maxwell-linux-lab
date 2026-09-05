from __future__ import annotations

import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
from typing import Any


DEFAULT_TIMEOUT = 8


def _run(argv: list[str], timeout: int = DEFAULT_TIMEOUT) -> dict[str, Any]:
    executable = shutil.which(argv[0])
    if executable is None:
        return {
            "available": False,
            "command": argv,
            "returncode": None,
            "stdout": "",
            "stderr": f"{argv[0]} not found",
        }

    try:
        completed = subprocess.run(
            argv,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "available": True,
            "command": argv,
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "available": True,
            "command": argv,
            "returncode": None,
            "stdout": (exc.stdout or "").strip() if isinstance(exc.stdout, str) else "",
            "stderr": f"timeout after {timeout}s",
        }
    except OSError as exc:
        return {
            "available": True,
            "command": argv,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
        }


def _read_text(path: Path, max_bytes: int = 64 * 1024) -> str | None:
    try:
        with path.open("rb") as handle:
            data = handle.read(max_bytes + 1)
        if len(data) > max_bytes:
            data = data[:max_bytes]
        return data.decode("utf-8", errors="replace").strip()
    except (OSError, PermissionError):
        return None


def _parse_os_release() -> dict[str, str]:
    result: dict[str, str] = {}
    text = _read_text(Path("/etc/os-release"))
    if not text:
        return result
    for line in text.splitlines():
        if "=" not in line or line.startswith("#"):
            continue
        key, value = line.split("=", 1)
        result[key] = value.strip().strip('"')
    return result


def _cpu_model() -> str | None:
    text = _read_text(Path("/proc/cpuinfo"), max_bytes=512 * 1024)
    if not text:
        return None
    match = re.search(r"^model name\s*:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def _memory_total_kib() -> int | None:
    text = _read_text(Path("/proc/meminfo"))
    if not text:
        return None
    match = re.search(r"^MemTotal:\s+(\d+)\s+kB$", text, re.MULTILINE)
    return int(match.group(1)) if match else None


def _dmi_value(name: str) -> str | None:
    return _read_text(Path("/sys/class/dmi/id") / name)


def _driver_name(device_path: Path) -> str | None:
    driver = device_path / "driver"
    try:
        if not driver.exists():
            return None
        return driver.resolve().name
    except OSError:
        return None


def _collect_drm_devices() -> list[dict[str, str | None]]:
    root = Path("/sys/class/drm")
    results: list[dict[str, str | None]] = []
    try:
        paths = sorted(root.glob("card*"))
    except OSError:
        return results

    for path in paths:
        if not re.fullmatch(r"card\d+", path.name):
            continue
        device = path / "device"
        results.append(
            {
                "node": path.name,
                "vendor": _read_text(device / "vendor"),
                "device": _read_text(device / "device"),
                "subsystem_vendor": _read_text(device / "subsystem_vendor"),
                "subsystem_device": _read_text(device / "subsystem_device"),
                "driver": _driver_name(device),
            }
        )
    return results


def _collect_drm_connectors() -> list[dict[str, Any]]:
    root = Path("/sys/class/drm")
    results: list[dict[str, Any]] = []
    try:
        paths = sorted(root.glob("card*-*"))
    except OSError:
        return results

    for path in paths:
        if not re.match(r"^card\d+-", path.name):
            continue
        modes_text = _read_text(path / "modes", max_bytes=16 * 1024) or ""
        modes = [line for line in modes_text.splitlines() if line][:20]
        results.append(
            {
                "name": path.name,
                "status": _read_text(path / "status"),
                "enabled": _read_text(path / "enabled"),
                "modes": modes,
            }
        )
    return results


def _collect_pstates() -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    debugfs = Path("/sys/kernel/debug/dri")

    try:
        if not debugfs.exists():
            return results
        paths = sorted(debugfs.glob("*/pstate"))
    except OSError:
        return results

    for path in paths:
        content = _read_text(path)
        if content is not None:
            results.append({"path": str(path), "content": content})
    return results


def _collect_nvidia_pci_runtime_pm() -> list[dict[str, str | None]]:
    devices_root = Path("/sys/bus/pci/devices")
    results: list[dict[str, str | None]] = []
    try:
        if not devices_root.exists():
            return results
        devices = sorted(devices_root.iterdir())
    except OSError:
        return results

    for device in devices:
        vendor = _read_text(device / "vendor")
        class_code = _read_text(device / "class")
        if vendor != "0x10de":
            continue
        if not class_code or not class_code.startswith(("0x0300", "0x0302")):
            continue
        results.append(
            {
                "pci_address": device.name,
                "vendor": vendor,
                "device": _read_text(device / "device"),
                "class": class_code,
                "runtime_status": _read_text(device / "power/runtime_status"),
                "runtime_suspended_time": _read_text(device / "power/runtime_suspended_time"),
                "runtime_active_time": _read_text(device / "power/runtime_active_time"),
                "control": _read_text(device / "power/control"),
            }
        )
    return results


def collect_inventory(include_hostname: bool = False) -> dict[str, Any]:
    inventory: dict[str, Any] = {
        "schema_version": 2,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "hostname": platform.node() if include_hostname else None,
        },
        "os_release": _parse_os_release(),
        "hardware": {
            "system_vendor": _dmi_value("sys_vendor"),
            "product_name": _dmi_value("product_name"),
            "product_version": _dmi_value("product_version"),
            "bios_vendor": _dmi_value("bios_vendor"),
            "bios_version": _dmi_value("bios_version"),
            "bios_date": _dmi_value("bios_date"),
            "cpu_model": _cpu_model(),
            "memory_total_kib": _memory_total_kib(),
        },
        "session": {
            "type": os.environ.get("XDG_SESSION_TYPE"),
            "desktop": os.environ.get("XDG_CURRENT_DESKTOP"),
        },
        "graphics": {
            "lspci": _run(["lspci", "-nnk"]),
            "vulkan_summary": _run(["vulkaninfo", "--summary"], timeout=15),
            "opengl_summary": _run(["glxinfo", "-B"]),
            "prime_providers": _run(["xrandr", "--listproviders"]),
            "switcherooctl": _run(["switcherooctl", "list"]),
            "nvidia_smi": _run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,pci.bus_id,driver_version,pstate,"
                    "clocks.current.graphics,clocks.current.memory,"
                    "temperature.gpu,utilization.gpu,memory.total,memory.used",
                    "--format=csv,noheader,nounits",
                ]
            ),
            "nouveau_modinfo": _run(["modinfo", "nouveau"]),
            "nvidia_modinfo": _run(["modinfo", "nvidia"]),
            "loaded_modules": _run(["lsmod"]),
            "drm_devices": _collect_drm_devices(),
            "drm_connectors": _collect_drm_connectors(),
            "nouveau_pstates": _collect_pstates(),
            "nvidia_pci_runtime_pm": _collect_nvidia_pci_runtime_pm(),
        },
        "power": {
            "powerprofilesctl": _run(["powerprofilesctl", "get"]),
        },
    }
    return inventory


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
