# Maxwell Linux Lab

A measurement-first engineering project to improve Linux support and performance for pre-GSP NVIDIA Maxwell GPUs, using the **GeForce GTX 960M / GM107** as the initial reference platform.

> **Project status:** v0.1.0 — lab foundation and baseline tooling.

## Why this project exists

NVIDIA's proprietary Linux **580** driver series is the last branch that supports Maxwell, Pascal, and Volta. At the same time, the open Linux graphics stack has matured significantly:

- **Nouveau** provides the kernel DRM driver for pre-GSP NVIDIA hardware.
- **NVK** is Mesa's Vulkan driver for NVIDIA GPUs and officially supports Kepler and newer GPUs.
- **NAK** is the shader compiler used by NVK.
- **DXVK** supports NVK with Mesa 25.1 or newer, while documenting that NVK still trails the proprietary driver in many workloads.

That creates a useful engineering target: preserve and improve Maxwell on Linux after vendor performance development has effectively stopped.

This repository is **not** a from-scratch GPU driver rewrite. It is a lab, tooling, documentation, and upstream-contribution project for finding measurable bottlenecks and improving the correct component: Nouveau, NVK, NAK, DXVK/VKD3D-Proton integration, or laptop runtime power management.

## Scope

### Primary reference platform

- NVIDIA GeForce GTX 960M
- GM107 / first-generation Maxwell
- Intel iGPU + NVIDIA dGPU laptop configuration
- Fedora Workstation as the primary development distribution

The GTX 960M is a **reference platform**, not the only target.

### Expansion path

1. GTX 960M reference machine
2. GM107
3. GM10x / Maxwell 1 where the hardware behavior is shared
4. Broader Maxwell support where technically valid
5. Reusable improvements upstreamed to Nouveau, Mesa/NVK/NAK, or related projects

We explicitly avoid model-specific hacks when an architecture-level solution is possible.

## Engineering principles

1. **Measure before changing code.**
2. **Change one variable at a time.**
3. **Use the proprietary Linux driver as the primary Linux performance baseline.**
4. **Keep Windows optional and external to the development workflow.**
5. **Treat average FPS as insufficient: record frame times, 1% lows, clocks, thermals, and runtime power state.**
6. **Do not assume a performance problem belongs to NVK. Verify clocks and power state first.**
7. **Prefer upstreamable patches over permanent out-of-tree hacks.**
8. **Never automate unsafe clock or voltage manipulation without explicit hardware guards.**
9. **Keep measurements reproducible and machine-readable.**
10. **Generalize from GM107 only after evidence supports the generalization.**

## Target stack

```text
Windows game
    |
Steam / Proton
    |
DXVK / VKD3D-Proton
    |
Vulkan
    |
Mesa / NVK
    |
NAK shader compiler
    |
Nouveau DRM
    |
Power management / reclocking
    |
GM107 / GTX 960M
```

For native Vulkan applications, the upper translation layers are absent.

## Baseline matrix

The first milestone compares two Linux configurations on the same hardware:

| Baseline | Purpose |
|---|---|
| Fedora + NVIDIA proprietary 580 | Linux performance/reference baseline |
| Fedora + Nouveau + NVK/NAK | Open-source baseline |

An optional Windows baseline may be recorded as an external historical performance reference, but it is not required to develop or validate Linux changes.

## Success criteria

We use staged success criteria rather than a vague "faster than Windows" goal.

### L0 — Correctness
- Stable boot and desktop
- Correct PRIME render offload
- Vulkan applications run reliably
- Suspend/resume works
- External display behavior is understood and documented
- No obvious thermal or runtime-PM regression

### L1 — Linux parity
On the selected benchmark suite, the open stack reaches at least **97% of the proprietary Linux baseline geometric mean** at equivalent clocks and comparable thermals.

### L2 — Competitive
The open stack matches or exceeds the proprietary Linux baseline on the geometric mean, without meaningful regression in frame-time consistency or power behavior.

### L3 — Excellent laptop experience
In addition to performance:
- competitive 1% lows and p95/p99 frame times
- correct dGPU runtime suspend when idle
- reliable PRIME offload
- clean suspend/resume
- no material battery-life regression during iGPU-only use

These are project targets, not claims about the current driver.

## v0.1.0 contents

This first version provides:

- a reproducible hardware/software inventory collector
- a generic benchmark-run recorder
- environment checks for Fedora/Linux graphics development
- a reference methodology
- a detailed engineering roadmap
- CI for the lab tooling
- contribution and agent instructions

No driver modifications are included in v0.1.0.

## Quick start

### 1. Install basic Fedora tools

```bash
sudo dnf install -y \
  python3 python3-pip pciutils \
  vulkan-tools mesa-demos mangohud
```

This command installs observation/benchmark utilities only. It does **not** install or replace a GPU driver.

### 2. Install the lab CLI

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

### 3. Check the environment

```bash
./scripts/check-environment.sh
```

### 4. Capture the machine inventory

```bash
maxwell-lab inventory --output artifacts/inventory.json
```

If debugfs is mounted and permissions allow it, the collector also records Nouveau `pstate` data.

### 5. Record a benchmark command

```bash
maxwell-lab run \
  --label nvk-example \
  --repeat 3 \
  --output-dir artifacts/runs \
  -- glmark2
```

The runner records:
- command and label
- timestamps
- exit status
- wall-clock duration
- stdout/stderr
- inventory snapshot before the run set

For games, use a deterministic in-game benchmark and MangoHud logging. Native FPS parsing is intentionally not hard-coded in v0.1.0 because different games expose different benchmark formats.

## Repository layout

```text
.
├── AGENTS.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── ROADMAP.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── METHODOLOGY.md
│   └── SAFETY.md
├── scripts/
│   └── check-environment.sh
├── src/
│   └── maxwell_lab/
│       ├── __init__.py
│       ├── bench.py
│       ├── cli.py
│       └── collect.py
├── tests/
│   └── test_collect.py
└── .github/
    ├── workflows/ci.yml
    ├── ISSUE_TEMPLATE/
    │   ├── hardware-report.yml
    │   └── performance-regression.yml
    └── pull_request_template.md
```

## What we measure

At minimum:

- kernel version
- OS release
- PCI GPU IDs and bound kernel drivers
- loaded NVIDIA/Nouveau modules
- Vulkan summary
- OpenGL renderer summary when available
- Nouveau pstate information when readable
- NVIDIA proprietary driver telemetry when available
- runtime-PM status for NVIDIA PCI devices
- benchmark exit status and elapsed time

Future phases add synchronized:
- GPU core clock
- memory clock
- temperature
- utilization
- VRAM pressure
- power draw where exposed
- MangoHud frame-time logs
- p95/p99 frame times
- 1% and 0.1% lows

## Research questions

The roadmap is organized around explicit questions:

1. Is the open-stack performance gap caused primarily by clocks/reclocking?
2. At equivalent clocks, how large is the NVK/NAK gap?
3. Which workloads are shader-compiler bound versus memory/submission bound?
4. Can GM107 power management be improved without harming stability or thermals?
5. Which optimizations are GM107-specific, Maxwell-1-wide, or generic NVK/NAK improvements?
6. Can PRIME/runtime-PM behavior be improved without sacrificing game performance?
7. Which improvements can be submitted upstream with focused, reproducible evidence?

See [ROADMAP.md](ROADMAP.md) for the complete action plan.

## Safety

Clock and power-management work can hang the GPU, crash the kernel, corrupt unsaved work, or cause thermal problems if done incorrectly.

The project starts read-only. Any later experiment that writes performance-state controls must:
- be opt-in
- have documented recovery steps
- define thermal stop conditions
- avoid voltage modification
- avoid persistent boot-time activation until validated

Read [docs/SAFETY.md](docs/SAFETY.md) before any reclocking experiment.

## Upstream-first policy

This repository should not become a permanent fork of Nouveau or Mesa.

The preferred lifecycle is:

```text
reproduce
  -> isolate
  -> instrument
  -> patch
  -> A/B benchmark
  -> regression test
  -> submit upstream
  -> track review
  -> remove local workaround after upstream adoption
```

Kernel work should follow the Linux DRM/Nouveau contribution process and license requirements. Mesa work should follow Mesa's contribution, CI, and licensing rules.

## References

Primary technical references:

- Mesa NVK documentation: https://docs.mesa3d.org/drivers/nvk.html
- Nouveau project documentation: https://nouveau.freedesktop.org/
- Nouveau power-management documentation: https://nouveau.freedesktop.org/PowerManagement.html
- DXVK driver support: https://github.com/doitsujin/dxvk/wiki/Driver-support
- NVIDIA Unix legacy GPU support timeframe: https://nvidia.custhelp.com/app/answers/detail/a_id/3142
- Linux DRM/Nouveau upstream documentation: https://docs.kernel.org/gpu/
- Mesa CI documentation: https://docs.mesa3d.org/ci/

## License

The original tooling and documentation in this repository are licensed under the MIT License.

Patches intended for Linux, Mesa, DXVK, or other upstream projects must follow the license and contribution requirements of those projects.
