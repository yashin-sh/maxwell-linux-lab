# Legal and Contribution Provenance Policy

Maxwell Linux Lab is an independent open-source research and engineering project focused on measuring and improving Linux support for NVIDIA Maxwell hardware.

This document is a project policy, not legal advice.

## Independence

Maxwell Linux Lab is not affiliated with, sponsored by, endorsed by, or approved by NVIDIA Corporation or any other hardware or software vendor.

Names and trademarks are used only to identify hardware, software, drivers, and compatibility targets.

## Clean provenance

Contributions must be independently developed and legally redistributable.

Acceptable sources include:

- the contributor's own original work
- publicly available hardware or software documentation
- lawful observation, testing, benchmarking, and measurement of hardware or software behavior
- source code from open-source projects when reuse is permitted by the applicable license and attribution requirements
- information already published through legitimate upstream Linux, Mesa, Nouveau, NVK, NAK, DXVK, VKD3D-Proton, or other relevant open-source channels

## Material that must not be contributed

Do not submit, paste, translate, reconstruct, or derive project code from material that you do not have the right to redistribute or use for the contribution.

In particular, do not contribute:

- proprietary NVIDIA source code
- copied decompiled or disassembled proprietary driver code
- leaked, confidential, NDA-covered, or otherwise non-public vendor material
- proprietary firmware, BIOS, microcode, or binary blobs unless redistribution is clearly permitted
- code copied from another project without complying with its license
- secrets, credentials, serial numbers, hostnames, usernames, MAC addresses, private keys, or unrelated personal/system data
- material whose provenance cannot be explained when reasonably requested during review

Binary analysis or interoperability research may be subject to different legal rules in different jurisdictions. Do not use this repository to distribute restricted vendor material or to bypass access controls, signatures, DRM, authentication, or other technical protection mechanisms.

## Observation and benchmarking

The project may document externally observable behavior such as:

- performance and frame-time measurements
- GPU and memory clocks
- power and runtime-PM states
- PCI and DRM topology
- Vulkan/OpenGL capabilities and behavior
- driver-visible state
- reproducible hardware behavior discovered through independently developed tests

Measurements should be recorded in a way that another contributor can reproduce without access to confidential or proprietary source material.

## Contribution representation

By submitting a contribution, you represent that:

1. you have the right to submit the contribution under the repository's applicable license;
2. the contribution is your original work or uses third-party material in a license-compatible, properly attributed way;
3. it was not copied or reconstructed from confidential, leaked, proprietary, or otherwise restricted material; and
4. you can describe the contribution's provenance if a maintainer reasonably asks during review.

If provenance is uncertain, disclose that uncertainty before the contribution is merged.

Maintainers may reject or remove material whose provenance or redistribution rights are unclear.

## Third-party licenses

The repository license applies to original Maxwell Linux Lab material unless a file states otherwise. Third-party projects, patches, traces, documentation, or code remain subject to their own licenses and contribution requirements.

When work is intended for an upstream project, contributors must also follow that upstream project's licensing, sign-off, authorship, and contribution rules.

## Security and privacy

Raw hardware inventories and logs can contain identifying or sensitive system information. Follow `docs/PRIVACY.md` and keep raw captures under ignored local artifact paths unless there is a specific, reviewed reason to publish a sanitized subset.

## Questions

When in doubt about whether material is acceptable, do not publish it first and ask later. Open an issue describing the type and provenance of the material without attaching the potentially restricted content.
