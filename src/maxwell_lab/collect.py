from __future__ import annotations

import json
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


def _collect_pstates() -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    debugfs = Path("/sys/kernel/debug/dri")

    try:
        if not debugfs.exists():
            return results
        paths = sorted(debugfs.glob("*/pstate"))
    except OSError:
        # debugfs is commonly mounted but inaccessible to unprivileged users
        # (including GitHub-hosted CI runners). Inventory collection must stay
        # read-only and degrade gracefully instead of requiring root.
        return results

    for path in paths:
        content = _read_text(path)
        if content is not None:
            results.append({"path": str(path), "content": content})
    return results


def _collect_nvidia_pci_runtime_pm() -> list[dict[str, str | None]]:
    devices_root = Path("/sys/bus/pci/devices")
    results: list[dict[str, str | None]] = []
    if not devices_root.exists():
        return results

    for device in sorted(devices_root.iterdir()):
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
        "schema_version": 1,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "hostname": platform.node() if include_hostname else None,
        },
        "os_release": _parse_os_release(),
        "hardware": {
            "cpu_model": _cpu_model(),
            "memory_total_kib": _memory_total_kib(),
        },
        "graphics": {
            "lspci": _run(["lspci", "-nnk"]),
            "vulkan_summary": _run(["vulkaninfo", "--summary"], timeout=15),
            "opengl_summary": _run(["glxinfo", "-B"]),
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
