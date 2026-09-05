# Contributing

Thank you for helping improve Maxwell support on Linux.

## Before opening a change

For performance or driver work:

1. reproduce on a current supported stack
2. capture the exact environment
3. identify the likely component
4. gather before-change measurements
5. keep the proposed change as small as possible

For documentation or lab tooling, normal focused pull requests are welcome.

## Performance reports

A useful performance report includes:

- exact GPU PCI ID and subsystem ID
- laptop/desktop classification
- kernel version
- Mesa version or git SHA
- Nouveau/NVIDIA driver state
- DXVK/Proton version if relevant
- resolution and graphics preset
- benchmark scene/procedure
- run count
- average FPS
- frame-time data when possible
- GPU core and memory clocks when available
- temperatures
- whether the system was AC powered
- whether PRIME offload was used

Do not include serial numbers, hostnames, usernames, MAC addresses, or unrelated system logs.

## Pull-request expectations

Every performance-affecting PR should answer:

- What is slow or incorrect?
- How was it reproduced?
- Which layer owns the problem?
- What changed?
- What are the before/after results?
- What correctness tests were run?
- What other GPUs/architectures might be affected?
- How can the change be reverted or recovered from if it touches power management?

## Upstream work

This repository is a staging and research lab, not a replacement for upstream.

When a change belongs in:
- Linux/Nouveau: submit according to Linux DRM/Nouveau rules
- Mesa/NVK/NAK: submit as a Mesa merge request
- DXVK: follow DXVK contribution requirements
- VKD3D-Proton: follow that project's requirements

Do not copy code between projects without respecting licenses.

## Language

Project documentation, issues, commit messages, and pull requests should be written in English.
