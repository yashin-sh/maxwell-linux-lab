from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .bench import run_benchmark
from .collect import collect_inventory, write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="maxwell-lab",
        description="Measurement-first tooling for Maxwell Linux GPU investigations.",
    )
    subparsers = parser.add_subparsers(dest="command_name", required=True)

    inventory = subparsers.add_parser("inventory", help="Collect a read-only system/GPU inventory.")
    inventory.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/inventory.json"),
        help="JSON output path.",
    )
    inventory.add_argument(
        "--include-hostname",
        action="store_true",
        help="Include hostname in the inventory. Disabled by default for privacy.",
    )

    run = subparsers.add_parser("run", help="Record one or more executions of a benchmark command.")
    run.add_argument("--label", required=True, help="Short baseline/workload label.")
    run.add_argument("--repeat", type=int, default=3, help="Number of runs. Default: 3.")
    run.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/runs"),
        help="Directory that will contain the timestamped run bundle.",
    )
    run.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Optional per-run timeout in seconds.",
    )
    run.add_argument(
        "--include-hostname",
        action="store_true",
        help="Include hostname in the inventory snapshot.",
    )
    run.add_argument(
        "benchmark_command",
        nargs=argparse.REMAINDER,
        help="Command to execute after '--'.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command_name == "inventory":
        data = collect_inventory(include_hostname=args.include_hostname)
        write_json(args.output, data)
        print(args.output)
        return 0

    if args.command_name == "run":
        command = args.benchmark_command
        if command and command[0] == "--":
            command = command[1:]
        if not command:
            parser.error("run requires a benchmark command after '--'")

        try:
            output = run_benchmark(
                command,
                label=args.label,
                repeat=args.repeat,
                output_dir=args.output_dir,
                include_hostname=args.include_hostname,
                timeout=args.timeout,
            )
        except ValueError as exc:
            parser.error(str(exc))
        print(output)
        return 0

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    sys.exit(main())
