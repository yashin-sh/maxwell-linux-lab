# Privacy and Public Hardware Data

This repository is public. Hardware characterization must therefore use a strict separation between local evidence and commit-safe summaries.

## Data boundary

### Local only

The following data must stay under ignored paths such as `artifacts/`:

- complete inventory JSON
- complete `lspci`, `vulkaninfo`, `glxinfo`, `switcherooctl`, or similar raw command output
- complete kernel logs or `dmesg`
- EDID blobs
- hostnames
- usernames and home-directory paths
- serial numbers
- filesystem, disk, machine, or device UUIDs that are not required for the public technical result
- MAC addresses and network configuration
- crash dumps and traces that have not been manually reviewed

### Public allowlist

A public reference summary may contain only fields explicitly selected by the sanitizer, including:

- distribution and kernel version
- CPU model and memory size
- laptop vendor/model when it is not a unique identifier
- BIOS vendor/version/date
- GPU and iGPU names
- PCI vendor/device/subsystem IDs
- bound graphics driver
- DRM node and connector names/status
- graphics API driver/version information with UUID fields removed
- Nouveau performance-state information
- NVIDIA runtime-PM state and the limited `nvidia-smi` query used by the lab
- PRIME provider information

## Why allowlisting is used

Redacting a raw dump is fragile: adding a new probe may silently introduce a new identifier that the redactor does not know about.

`maxwell-lab characterize` therefore reconstructs public output from an allowlist. A newly added raw probe is private by default until somebody deliberately adds a reviewed field to the public snapshot.

A second privacy gate rejects common identifier patterns such as MAC addresses, UUIDs, home-directory paths, serial-number values, and known local user/host literals before a public output file is written.

## Recommended workflow

```bash
maxwell-lab characterize
```

This produces local files under:

```text
artifacts/reference/
├── raw/
│   └── inventory.json
└── public/
    ├── inventory.public.json
    └── summary.md
```

Review `artifacts/reference/public/summary.md` before publishing anything.

When ready, explicitly request a tracked Markdown file:

```bash
maxwell-lab characterize --public-output hardware/reference-gm107.md
```

The tracked output is written only if the privacy gate succeeds.

## Maintainer rule

Never weaken the privacy gate merely to make a failing characterization pass. Determine which field triggered the gate, decide whether it is technically necessary and safe to publish, then change the allowlist or rendering logic with tests documenting the decision.
