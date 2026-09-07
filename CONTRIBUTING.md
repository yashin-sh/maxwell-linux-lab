# Contributing

Thank you for helping improve Maxwell support on Linux.

Before contributing, read [`LEGAL.md`](LEGAL.md). Contributions must have clean, explainable provenance and must be legally redistributable.

## Before opening a change

For performance or driver work:

1. reproduce on a current supported stack
2. capture the exact environment
3. identify the likely component
4. gather before-change measurements
5. keep the proposed change as small as possible

For documentation or lab tooling, normal focused pull requests are welcome.

## Contribution provenance

By submitting a contribution, you represent that you have the right to submit it under the repository's applicable license and that it is either your original work or uses third-party material in a license-compatible, properly attributed way.

Do not contribute code or documentation copied or reconstructed from:

- proprietary NVIDIA source code
- decompiled or disassembled proprietary driver code
- leaked, confidential, NDA-covered, or otherwise restricted material
- proprietary firmware or binary blobs without clear redistribution rights
- another project without complying with that project's license

Lawful observation, testing, benchmarking, public documentation, independently developed experiments, and appropriately licensed open-source material are acceptable sources.

If the provenance of a change is not obvious, explain it in the pull request. Maintainers may ask for additional provenance information and may reject material whose redistribution rights are unclear.

See [`LEGAL.md`](LEGAL.md) for the full policy.

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
- What is the provenance of the implementation and technical information used?

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
