# Architecture

## Principle

The project is organized around layer isolation. A visible game-performance problem is not automatically an NVK problem.

```text
Application
  |
  +-- Native Vulkan ------------------+
  |                                   |
  +-- D3D9/10/11 -> DXVK ------------+--> Vulkan
  |                                   |
  +-- D3D12 -> VKD3D-Proton ---------+
                                      |
                                      v
                                     NVK
                                      |
                                      v
                                     NAK
                                      |
                                      v
                                Nouveau DRM
                                      |
                     +----------------+----------------+
                     |                                 |
                scheduling                      power / clocks
                     |                                 |
                     +----------------+----------------+
                                      |
                                      v
                                   Maxwell
```

## Reference platform strategy

The GTX 960M is used because we can observe and reproduce on a real GM107 laptop.

The code and research should classify findings as one of:

- laptop-specific
- GTX 960M board/subsystem-specific
- GM107-specific
- Maxwell-1 / GM10x-specific
- Maxwell-wide
- generic Nouveau
- generic NVK
- generic NAK

Do not promote a finding to a broader class without evidence.

## Tooling architecture

The v0.1 CLI has two commands:

### `inventory`

Read-only environment capture.

It intentionally tolerates missing optional utilities because the same command must work under both the proprietary and open-source stacks.

### `run`

A generic command recorder.

It does not parse game FPS in v0.1. Instead it creates a timestamped evidence bundle so workload-specific telemetry can be added without coupling the core to one game.

Future modules should add:

- telemetry sampling
- MangoHud CSV ingestion
- run normalization
- statistical reports
- environment-drift detection
