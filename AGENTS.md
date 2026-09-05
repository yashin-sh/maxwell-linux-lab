# AGENTS.md

Instructions for AI coding agents and automated contributors working in this repository.

## Mission

Improve the quality, observability, performance, and maintainability of Linux support for pre-GSP NVIDIA Maxwell GPUs, starting with GM107 / GeForce GTX 960M as the reference platform.

The project is measurement-first and upstream-first.

## Non-negotiable rules

1. **Do not invent hardware facts.**
   - Never assume PCI IDs, VRAM size, clock limits, display routing, or supported performance states.
   - Read them from captured inventory or authoritative documentation.

2. **Do not change clocks, voltage, or power state by default.**
   - All v0.1 tooling is read-only with respect to GPU performance controls.
   - Any future write operation must be explicit, documented, reversible, and guarded.

3. **Never change voltage.**
   - Voltage modification is outside the initial project scope.

4. **One variable per performance experiment.**
   - Do not update kernel, Mesa, Proton, DXVK, game settings, and clocks in the same comparison.

5. **Do not optimize before reproducing.**
   - Every performance patch needs a reproducible case and before/after data.

6. **Do not use average FPS alone.**
   - Prefer frame-time distributions, 1% lows, p95/p99, clocks, thermals, and variance.

7. **Do not call a result generic from one GPU.**
   - GM107 evidence proves GM107 behavior only.
   - Architecture-wide claims require additional hardware evidence or strong upstream documentation.

8. **Prefer upstream fixes.**
   - Avoid permanent local forks and model-specific hacks.
   - The end state for a real driver fix should be a focused upstream patch/MR whenever feasible.

9. **Preserve upstream licenses.**
   - This repository's own tooling is MIT.
   - Linux kernel, Mesa, DXVK, and other upstream patches must follow their native licensing and contribution rules.

10. **Do not commit machine-identifying or large raw artifacts.**
    - Raw benchmark bundles belong in ignored `artifacts/` paths or CI artifacts.
    - Sanitize hostnames, usernames, serial numbers, UUIDs, MAC addresses, and unrelated logs before committing.

## Source priority

When a technical fact may have changed, use sources in this order:

1. current upstream code
2. current upstream project documentation
3. current maintainer statements/issues/MRs
4. distribution packaging documentation
5. secondary technical sources

For core project assumptions, avoid relying on forum folklore when upstream documentation exists.

## Component ownership model

Before changing code, identify the responsible layer.

```text
Game behavior
  -> Proton / Wine
  -> DXVK or VKD3D-Proton
  -> Vulkan API behavior
  -> NVK
  -> NAK shader compiler
  -> Nouveau DRM
  -> clocks / firmware / runtime PM
  -> hardware
```

Examples:

- Low GPU clocks under every Vulkan workload: investigate Nouveau/power management before NAK.
- Correct clocks but poor shader-heavy performance: investigate NVK/NAK.
- Native Vulkan is fast but one DX11 title is slow: investigate DXVK/game path before the kernel.
- dGPU never suspends after workloads: investigate PRIME/runtime PM, not shader code.

## Required workflow for performance changes

1. Capture exact environment.
2. Reproduce issue at least three times where practical.
3. Record baseline metrics.
4. State one hypothesis.
5. Add instrumentation if the hypothesis is not observable.
6. Make the smallest change that tests the hypothesis.
7. Repeat the exact benchmark.
8. Compare frame times, clocks, thermals, and variance.
9. Run correctness/regression tests.
10. Document whether the hypothesis was confirmed or rejected.

A rejected hypothesis is a useful result and should not be hidden.

## Benchmark integrity

Do not:
- change resolution between runs
- change graphics preset between runs
- compare AC-powered and battery-powered runs
- compare cold and thermally saturated runs without labeling them
- discard slow runs merely because they are inconvenient
- cherry-pick the best run

Do:
- define warm-up
- define run count before measuring
- use the same scene/save/benchmark sequence
- keep CPU power policy stable
- capture software SHAs and versions
- mark invalid runs with a reason instead of deleting evidence

## Safety requirements for future reclocking work

Any code that writes to a GPU performance-state interface must:

- require an explicit opt-in flag
- refuse to run as part of normal inventory collection
- print the target device PCI ID
- print the current and requested state
- define a maximum test duration
- define a thermal abort strategy where telemetry exists
- provide a restore/default action
- document reboot/recovery steps
- never write voltage controls
- never persist configuration at boot until manual testing is complete

If these conditions cannot be met, do not implement the write path.

## Coding conventions

### Python
- Python 3.11+
- standard library preferred for the lab core
- type hints for public functions
- deterministic JSON output where practical
- subprocess timeouts for probe commands
- failed optional probes must be reported, not crash the whole inventory
- no shell=True unless a command fundamentally requires shell syntax
- unit tests for parsers and normalization logic

### Shell
- `#!/usr/bin/env bash`
- `set -euo pipefail`
- quote variables
- do not silently run privileged commands
- never modify GPU driver configuration from environment-check scripts

### Documentation
- English only
- distinguish measured facts from hypotheses
- include exact dates/versions for time-sensitive driver support claims
- link to upstream sources

## Git and pull requests

Preferred commit style:

```text
lab: add GM107 runtime-PM collector
docs: define equivalent-clock experiment
nvk: add reproducer for descriptor bottleneck
nak: reduce spill in Maxwell shader case
nouveau: prototype GM10x reclocking policy
```

Keep PRs small and single-purpose.

A PR must state:
- problem
- evidence
- change
- validation
- risks
- rollback/recovery if relevant

## Definition of done

A lab-tooling change is done when:
- tests pass
- output is documented
- failure behavior is safe
- no personal/machine-identifying data is committed by default

A performance investigation is done when:
- the bottleneck is isolated or the hypothesis is explicitly rejected
- data is reproducible
- the result is documented

A driver optimization is done when:
- correctness is preserved
- improvement is measurable
- regression risk is evaluated
- the patch is suitable for upstream review
