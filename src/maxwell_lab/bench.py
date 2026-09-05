from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import time
from typing import Any

from .collect import collect_inventory, write_json


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_benchmark(
    command: list[str],
    *,
    label: str,
    repeat: int,
    output_dir: Path,
    include_hostname: bool = False,
    timeout: float | None = None,
) -> Path:
    if repeat < 1:
        raise ValueError("repeat must be >= 1")
    if not command:
        raise ValueError("benchmark command must not be empty")

    run_root = output_dir / f"{label}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    run_root.mkdir(parents=True, exist_ok=False)

    inventory = collect_inventory(include_hostname=include_hostname)
    write_json(run_root / "inventory.json", inventory)

    manifest: dict[str, Any] = {
        "schema_version": 1,
        "label": label,
        "command": command,
        "started_at": _utc_now(),
        "repeat": repeat,
        "runs": [],
    }

    for index in range(1, repeat + 1):
        started_at = _utc_now()
        start = time.perf_counter()
        try:
            completed = subprocess.run(
                command,
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False,
            )
            elapsed = time.perf_counter() - start
            stdout = completed.stdout
            stderr = completed.stderr
            returncode = completed.returncode
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            elapsed = time.perf_counter() - start
            stdout = exc.stdout if isinstance(exc.stdout, str) else ""
            stderr = exc.stderr if isinstance(exc.stderr, str) else ""
            returncode = None
            timed_out = True

        stdout_path = run_root / f"run-{index:02d}.stdout.log"
        stderr_path = run_root / f"run-{index:02d}.stderr.log"
        stdout_path.write_text(stdout, encoding="utf-8", errors="replace")
        stderr_path.write_text(stderr, encoding="utf-8", errors="replace")

        manifest["runs"].append(
            {
                "index": index,
                "started_at": started_at,
                "elapsed_seconds": elapsed,
                "returncode": returncode,
                "timed_out": timed_out,
                "stdout_file": stdout_path.name,
                "stderr_file": stderr_path.name,
            }
        )

    manifest["finished_at"] = _utc_now()
    write_json(run_root / "manifest.json", manifest)
    return run_root
