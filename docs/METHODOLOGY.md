# Benchmark Methodology

## Objective

Produce evidence that can distinguish:

- a clock/power-management problem
- an NVK runtime problem
- a NAK shader-code-generation problem
- a translation-layer problem
- a CPU bottleneck
- a thermal artifact

## Required controls

A comparison is valid only when the following are fixed or recorded:

- same laptop
- same AC adapter and AC-powered state
- same display/resolution
- same graphics preset
- same benchmark scene
- same game build
- same CPU policy
- same compositor/session setup
- same run count
- same warm-up procedure

Kernel/Mesa/driver changes must be the deliberate experimental variable and must be recorded.

## Thermal control

Laptop GPUs are sensitive to heat soak.

Before formal baseline collection:

1. choose a repeatable warm-up procedure
2. define an acceptable starting-temperature range
3. record temperature during runs
4. flag runs with clear thermal throttling
5. never discard a throttled run silently

## Metrics

Preferred order:

1. frame-time series
2. p95/p99 frame time
3. 1% low
4. average FPS
5. clocks
6. utilization
7. temperature
8. runtime-PM behavior

Average FPS without clocks and frame-time context is not enough to diagnose the driver.

## Run count

Three runs are the minimum default for early investigation.

For claims intended for upstream performance discussion:
- increase repetitions when variance is material
- report variance
- use geometric mean for normalized multi-workload comparisons

## Equivalent-clock experiment

This is a major decision gate.

If the proprietary driver and NVK run at very different core/memory clocks, first determine whether the performance delta shrinks at comparable clocks.

Do not interpret a low-clock NVK result as evidence of poor shader compilation.

## Data handling

Raw bundles may contain machine details.

Before committing:
- remove hostname
- remove serial numbers
- remove usernames/home paths where possible
- remove MAC addresses
- remove unrelated kernel logs

The default CLI excludes the hostname.
