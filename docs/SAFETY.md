# Safety

## Current v0.1 behavior

The v0.1 project tooling is read-only with respect to GPU clocks, voltage, and performance-state controls.

It may read:
- debugfs pstate information
- PCI sysfs state
- driver metadata
- runtime-PM status
- standard telemetry tools

It does not write GPU power-management controls.

## Future reclocking experiments

GPU performance-state manipulation can cause:

- application crashes
- GPU hangs
- kernel hangs
- display loss
- unsaved-data loss
- thermal stress

Any future experimental write path must be opt-in and must document recovery.

## Hard project rules

- No voltage modification.
- No hidden root escalation.
- No automatic persistent performance-state configuration.
- No boot-time activation of experimental reclocking until validated.
- No claim that a state is safe merely because one machine survived it.
- No bypass of thermal safeguards.

## Before a controlled pstate experiment

1. save all work
2. disconnect unrelated workloads
3. know how to reboot/recover the machine
4. record the current/default state
5. establish temperature monitoring
6. use a short test duration
7. change only one performance-state variable
8. restore default state after the test
9. reboot after instability

## Kernel development

When testing Nouveau kernel changes:
- retain a known-good kernel in the bootloader
- do not remove the working kernel
- keep a recovery path available
- avoid testing on a machine containing irreplaceable unsaved data
