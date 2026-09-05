# Roadmap

This roadmap is intentionally evidence-driven. A later phase must not be used to hide an unresolved earlier-layer problem.

## Project objective

Make pre-GSP NVIDIA Maxwell hardware a first-class, measurable, maintainable Linux target, starting with GM107 / GeForce GTX 960M as the reference platform and upstreaming reusable improvements wherever possible.

---

## Phase 0 — Project foundation

### Repository and governance
- [x] Define project scope
- [x] Define GTX 960M / GM107 as the initial reference platform
- [x] Explicitly state that the project is not limited to the GTX 960M
- [x] Define upstream-first policy
- [x] Add README
- [x] Add AGENTS.md
- [x] Add .gitignore
- [x] Add roadmap
- [x] Add contribution guide
- [x] Add safety policy
- [x] Add CI for project tooling
- [x] Create the public GitHub repository
- [ ] Set repository description and topics
- [ ] Enable Discussions if community involvement becomes useful
- [ ] Configure issue labels
- [ ] Configure branch protection after CI is stable
- [ ] Add CODEOWNERS if multiple maintainers join
- [ ] Decide whether a SECURITY.md is useful for tooling vulnerabilities

### Source-of-truth policy
- [x] Prefer authoritative upstream documentation
- [x] Record exact kernel, Mesa, DXVK, Proton, firmware, and driver versions in every baseline
- [ ] Add a machine-readable `sources.lock.json` for critical external assumptions
- [ ] Review external assumptions at each milestone

---

## Phase 1 — Reference hardware characterization

Goal: remove all ambiguity about the laptop and GPU topology before performance work.

### Hardware inventory
- [ ] Record laptop vendor and model
- [ ] Record BIOS/UEFI version
- [ ] Record CPU model and microcode
- [ ] Record RAM size and topology
- [ ] Record storage model and filesystem
- [ ] Record panel resolution and refresh rate
- [ ] Record AC adapter wattage
- [ ] Record battery status/health for power tests
- [ ] Record GTX 960M PCI vendor/device/subsystem IDs
- [ ] Confirm GM107 device identity from PCI ID
- [ ] Record VRAM capacity and type
- [ ] Record Intel iGPU model and PCI ID
- [ ] Record all DRM devices and render nodes
- [ ] Map display connectors to iGPU/dGPU
- [ ] Determine whether HDMI/DisplayPort outputs are physically routed through the NVIDIA GPU
- [ ] Record VBIOS version where safely available
- [ ] Record IOMMU groups if relevant

### Linux topology
- [ ] Record kernel driver bound to each GPU
- [ ] Record loaded graphics modules
- [ ] Record DRM/KMS topology
- [ ] Record Wayland/Xorg session behavior
- [ ] Record PRIME providers/offload capability
- [ ] Record runtime-PM status
- [ ] Record suspend/resume behavior
- [ ] Record debugfs availability
- [ ] Record available Nouveau pstate entries

### Deliverable
- [ ] Commit a sanitized `hardware/reference-gm107.md`
- [ ] Store raw machine inventory as an artifact, not as personal machine-identifying data in Git

---

## Phase 2 — Baseline laboratory

Goal: establish reproducible performance and behavior before changing code.

### Baseline A — Linux proprietary
- [ ] Install Fedora reference environment
- [ ] Pin/document kernel version
- [ ] Install NVIDIA 580 legacy branch using the normal Fedora-supported packaging path
- [ ] Confirm PRIME offload
- [ ] Confirm Vulkan renderer
- [ ] Confirm game launch path uses NVIDIA dGPU
- [ ] Record clocks under idle and load
- [ ] Record GPU temperature under load
- [ ] Record runtime-PM behavior after closing the workload
- [ ] Validate suspend/resume
- [ ] Run benchmark suite
- [ ] Capture MangoHud frame-time logs
- [ ] Archive exact software versions

### Baseline B — Linux open stack
- [ ] Switch to Nouveau + NVK
- [ ] Confirm the proprietary module is not bound
- [ ] Confirm NVK is selected for Vulkan
- [ ] Confirm correct render node
- [ ] Confirm PRIME offload
- [ ] Record available pstate information
- [ ] Record clocks under idle and load
- [ ] Record GPU temperature under load
- [ ] Record runtime-PM behavior
- [ ] Validate suspend/resume
- [ ] Run the identical benchmark suite
- [ ] Capture MangoHud frame-time logs
- [ ] Archive exact software versions

### Optional Baseline C — Windows historical reference
- [ ] Only if useful, record a one-time external Windows performance baseline
- [ ] Keep it separate from Linux development acceptance criteria
- [ ] Do not let Windows-specific behavior block Linux-focused work

### Benchmark suite design
- [ ] Select at least one native Vulkan workload
- [ ] Select at least one DX9/DXVK workload
- [ ] Select at least two DX11/DXVK workloads
- [ ] Select at least one VKD3D-Proton workload if the GPU can run it meaningfully
- [ ] Include one shader-heavy workload
- [ ] Include one memory-bandwidth-sensitive workload
- [ ] Include one CPU-light/GPU-heavy workload
- [ ] Include one real game with a deterministic built-in benchmark
- [ ] Define fixed resolution and graphics presets
- [ ] Disable dynamic resolution
- [ ] Define warm-up procedure
- [ ] Define run count
- [ ] Define outlier policy before seeing results
- [ ] Define thermal starting window
- [ ] Run on AC power
- [ ] Fix CPU power policy for comparable performance runs
- [ ] Record desktop compositor/session state

### Metrics
- [ ] Average FPS
- [ ] 1% low
- [ ] 0.1% low where sample size permits
- [ ] median frame time
- [ ] p95 frame time
- [ ] p99 frame time
- [ ] GPU core clock
- [ ] memory clock
- [ ] GPU utilization
- [ ] temperature
- [ ] VRAM utilization
- [ ] CPU utilization
- [ ] runtime-PM state before/after
- [ ] power draw where reliably exposed

### Statistical treatment
- [ ] Use repeated runs
- [ ] Report geometric mean for normalized performance comparisons
- [ ] Report variance/standard deviation
- [ ] Flag thermally invalid runs
- [ ] Never compare runs with materially different clocks without labeling them

---

## Phase 3 — Telemetry and observability

Goal: make invisible driver behavior visible before optimization.

### Lab tooling
- [x] Build initial inventory collector
- [x] Build generic run recorder
- [ ] Add synchronized telemetry sampler
- [ ] Add MangoHud CSV importer
- [ ] Add frame-time statistics
- [ ] Add normalized comparison reports
- [ ] Add JSON schema for run metadata
- [ ] Add environment fingerprint
- [ ] Add git commit fingerprints for Mesa/kernel builds
- [ ] Add automatic driver detection
- [ ] Add automatic NVK/NVIDIA renderer validation
- [ ] Add thermal validity checks
- [ ] Add runtime-PM transition logger

### Nouveau observability
- [ ] Capture `pstate` state before/during/after workload
- [ ] Identify reliable GM107 clock telemetry sources
- [ ] Record failures to change pstate
- [ ] Record GPU reset/hang evidence
- [ ] Record relevant kernel logs per run
- [ ] Build minimal parser for Nouveau performance-state output
- [ ] Add read-only GM107 telemetry tests

### Deliverable
- [ ] One command produces a self-contained benchmark bundle suitable for an upstream bug report

---

## Phase 4 — GM107 reclocking and power-management investigation

Goal: determine whether clocks/power state are the dominant performance bottleneck.

### Read-only characterization first
- [ ] Enumerate available GM107 performance states
- [ ] Observe state at idle
- [ ] Observe state during Vulkan load
- [ ] Observe state during DXVK load
- [ ] Compare core clock with proprietary baseline
- [ ] Compare memory clock with proprietary baseline
- [ ] Compare thermal behavior
- [ ] Determine whether core or memory clock is limiting
- [ ] Determine whether the selected state changes automatically

### Controlled experiments
- [ ] Document exact kernel/debugfs interface used
- [ ] Define a hard thermal abort threshold
- [ ] Define a watchdog/recovery procedure
- [ ] Test one manual performance-state change only after safety review
- [ ] Verify that the requested state is actually reached
- [ ] Repeat a short benchmark
- [ ] Compare performance at equivalent clocks
- [ ] Restore safe/default behavior immediately after testing
- [ ] Reboot after any unstable state

### Decision gate
If equivalent clocks close most of the performance gap:
- [ ] prioritize Nouveau power-management/reclocking work

If a large gap remains at equivalent clocks:
- [ ] move NVK/NAK analysis ahead of governor work

### Upstream-quality power management
- [ ] Study Nouveau's existing GM10x clock code
- [ ] Identify missing automatic policy pieces
- [ ] Identify firmware constraints
- [ ] Prototype only the smallest necessary policy change
- [ ] Add hysteresis
- [ ] Add thermal safeguards
- [ ] Avoid voltage changes
- [ ] Validate idle transitions
- [ ] Validate load transitions
- [ ] Validate repeated transitions
- [ ] Validate suspend/resume
- [ ] Validate runtime-PM
- [ ] Test failure fallback
- [ ] Split patches into reviewable units
- [ ] Submit to Nouveau/DRM upstream if maintainers agree with the approach

---

## Phase 5 — NVK performance isolation

Goal: find performance gaps that remain after clock normalization.

### Workload classification
- [ ] Compare native Vulkan vs DXVK
- [ ] Compare simple vs shader-heavy workloads
- [ ] Compare low-VRAM vs high-VRAM workloads
- [ ] Compare draw-call-heavy vs shader-heavy workloads
- [ ] Identify GPU-bound scenarios
- [ ] Exclude CPU-bound scenarios from GPU-driver conclusions

### NVK analysis
- [ ] Build Mesa main in an isolated prefix
- [ ] Confirm the tested process actually loads the development NVK build
- [ ] Record Mesa git SHA
- [ ] Use NVK debug tooling where appropriate
- [ ] Capture reproducible traces where legally and technically possible
- [ ] Bisect major regressions
- [ ] Compare queue/submission overhead
- [ ] Investigate synchronization stalls
- [ ] Investigate descriptor/resource binding cost
- [ ] Investigate memory allocation behavior
- [ ] Investigate VRAM pressure behavior on 2/4 GB configurations
- [ ] Investigate pipeline compilation/stutter
- [ ] Validate optional Vulkan features relevant to current DXVK behavior

### Patch discipline
- [ ] One hypothesis per patch series
- [ ] Add a reproducer
- [ ] Add/extend tests where practical
- [ ] Benchmark before/after at equivalent clocks
- [ ] Check at least one non-GM107 NVIDIA GPU before claiming generic improvement
- [ ] Submit generic NVK improvements upstream

---

## Phase 6 — NAK shader compiler

Goal: improve code generation when shader compilation is proven to be a bottleneck.

### Baseline compiler analysis
- [ ] Identify slow shaders from real workloads
- [ ] Save legally redistributable minimized shader reproducers
- [ ] Inspect NIR before NAK
- [ ] Inspect generated Maxwell machine code
- [ ] Record instruction count
- [ ] Record register usage
- [ ] Detect spills/fills
- [ ] Estimate occupancy constraints
- [ ] Identify expensive instruction sequences
- [ ] Identify unnecessary moves/conversions
- [ ] Identify scheduling hazards

### Maxwell-specific validation
- [ ] Use NAK hardware tests
- [ ] Use documented Maxwell ISA resources
- [ ] Compare behavior against known-correct instruction semantics
- [ ] Add unit tests for each fixed codegen pattern
- [ ] Avoid optimizing only one game-specific shader

### Optimization candidates
- [ ] register allocation
- [ ] copy propagation
- [ ] dead-code elimination interactions
- [ ] instruction selection
- [ ] instruction scheduling
- [ ] predicate handling
- [ ] memory instruction selection
- [ ] texture instruction patterns
- [ ] control-flow lowering
- [ ] constant handling
- [ ] spill minimization

### Acceptance
- [ ] no shader correctness regression
- [ ] no NAK unit-test regression
- [ ] measurable workload improvement
- [ ] no broad regression on other supported architectures when generic code is touched
- [ ] upstream Mesa MR

---

## Phase 7 — DXVK / VKD3D-Proton interaction

Goal: improve translated Windows-game workloads only after lower layers are understood.

### DXVK
- [ ] Confirm current DXVK-supported NVK/Mesa requirements
- [ ] Record enabled optional Vulkan feature path
- [ ] Compare DXVK behavior on NVK vs proprietary Vulkan
- [ ] Identify driver-specific workarounds that affect NVK
- [ ] Test descriptor/resource-binding paths
- [ ] Test pipeline compilation behavior
- [ ] Analyze stutter separately from steady-state throughput
- [ ] Reproduce issues without game-specific hacks where possible

### VKD3D-Proton
- [ ] Select only workloads that are practical on GTX 960M
- [ ] Separate unsupported hardware limitations from driver bugs
- [ ] Record feature-level limitations
- [ ] Profile translation overhead vs NVK behavior
- [ ] Submit upstream fixes only when the correct layer is proven

---

## Phase 8 — Optimus, PRIME, runtime PM, and laptop quality

Goal: make the laptop experience excellent, not merely fast while plugged in.

### PRIME
- [ ] Verify iGPU drives the desktop by default
- [ ] Verify dGPU render offload
- [ ] Verify no accidental iGPU game runs
- [ ] Verify Vulkan device selection
- [ ] Verify OpenGL offload where relevant
- [ ] Measure copy/offload overhead

### Runtime PM
- [ ] Verify dGPU can enter runtime suspend after a workload
- [ ] Measure time to suspend
- [ ] Verify reliable wake
- [ ] Repeat wake/suspend cycles
- [ ] Detect processes that pin the dGPU awake
- [ ] Test idle battery impact
- [ ] Test after external display disconnect

### System power states
- [ ] Suspend/resume with dGPU idle
- [ ] Suspend/resume after dGPU workload
- [ ] Suspend/resume with external display
- [ ] Repeated suspend/resume stress test
- [ ] Hibernate only if the platform configuration supports it safely

### Displays
- [ ] Map every connector
- [ ] Test internal panel
- [ ] Test HDMI
- [ ] Test DisplayPort if present
- [ ] Test hotplug
- [ ] Test refresh-rate modes
- [ ] Document any muxless routing constraints

---

## Phase 9 — Generalize beyond GTX 960M

Goal: turn validated GM107 work into maintainable architecture-level improvements.

### GM107
- [ ] Test a second GM107 board if available
- [ ] Separate laptop quirks from GPU architecture behavior
- [ ] Remove subsystem-ID-specific assumptions

### Maxwell 1 / GM10x
- [ ] Identify common reclocking code paths
- [ ] Identify shared NAK instruction behavior
- [ ] Identify shared NVK performance patterns
- [ ] Acquire/test at least one additional GM10x GPU
- [ ] Build compatibility matrix

### Broader Maxwell
- [ ] Document firmware/reclocking differences between Maxwell generations
- [ ] Do not assume GM107 power behavior applies to GM20x
- [ ] Test architecture-specific changes independently
- [ ] Mark unsupported hypotheses clearly
- [ ] Generalize only with hardware evidence

---

## Phase 10 — Hardware CI and regression detection

Goal: stop improvements from regressing later.

### Software CI
- [x] Unit tests for lab tooling
- [ ] linting
- [ ] formatting check
- [ ] shellcheck
- [ ] JSON-schema validation

### Hardware CI
- [ ] Create a dedicated GM107 test host
- [ ] Isolate test host from personal data
- [ ] Add remote recovery path
- [ ] Add kernel boot fallback
- [ ] Add automatic artifact upload
- [ ] Add basic Vulkan smoke test
- [ ] Add selected NAK hardware tests
- [ ] Add short performance smoke benchmark
- [ ] Detect major performance regressions
- [ ] Do not treat noisy FPS changes as deterministic CI failures
- [ ] Track trends statistically

### Long-term matrix
- [ ] GM107 reference
- [ ] second Maxwell-1 GPU
- [ ] optional later Maxwell GPU
- [ ] optional modern NVIDIA comparison host for generic NVK changes

---

## Phase 11 — Upstream contribution workflow

### Before coding
- [ ] search existing Mesa/Nouveau issues and MRs
- [ ] reproduce on current upstream
- [ ] identify the correct component
- [ ] discuss architectural changes with maintainers when appropriate

### For every patch
- [ ] minimal reproducer
- [ ] exact hardware identity
- [ ] exact software SHAs
- [ ] before/after measurements
- [ ] correctness tests
- [ ] regression assessment
- [ ] clear commit message
- [ ] correct project license/sign-off requirements

### Mesa
- [ ] run relevant unit tests
- [ ] run NVK/NAK tests
- [ ] run Vulkan CTS subset when relevant
- [ ] use Mesa CI
- [ ] submit focused merge request
- [ ] respond to review
- [ ] rebase without obscuring review history unnecessarily

### Linux/Nouveau
- [ ] follow DRM/Nouveau maintainer guidance
- [ ] run build/sparse/checkpatch where relevant
- [ ] add Signed-off-by as required
- [ ] test boot and suspend/resume
- [ ] test failure/recovery paths
- [ ] send reviewable patch series
- [ ] track drm-misc/Nouveau integration

### After upstream merge
- [ ] remove obsolete local patch
- [ ] record upstream commit
- [ ] rerun baseline
- [ ] update compatibility/performance history

---

## Phase 12 — Documentation and community

- [ ] Publish reference hardware page
- [ ] Publish reproducible benchmark methodology
- [ ] Publish performance history without cherry-picking
- [ ] Document known limitations
- [ ] Document safe recovery procedures
- [ ] Create contribution starter issues
- [ ] Tag tasks suitable for first-time Mesa/kernel contributors
- [ ] Publish upstream links rather than maintaining redundant forks
- [ ] Maintain a list of tested Maxwell devices
- [ ] Document non-reproducible or inconclusive experiments as such

---

## Milestones

### v0.1 — Lab foundation
- [x] documentation
- [x] inventory CLI
- [x] generic benchmark recorder
- [x] CI
- [x] safety rules

### v0.2 — Reference machine captured
- [ ] complete GM107 hardware characterization
- [ ] sanitized reference hardware document
- [ ] validated PRIME topology

### v0.3 — Linux baselines
- [ ] proprietary baseline
- [ ] NVK baseline
- [ ] first normalized performance report

### v0.4 — Clock-gap conclusion
- [ ] equivalent-clock experiment
- [ ] written decision: power management first vs NVK/NAK first

### v0.5 — First upstream-quality fix
- [ ] one measurable issue isolated
- [ ] fix with tests
- [ ] upstream submission opened

### v1.0 — Reproducible Maxwell Linux reference lab
- [ ] stable tooling
- [ ] documented GM107 behavior
- [ ] repeatable performance suite
- [ ] at least one accepted upstream contribution or a documented proof that no patch was needed for the targeted issue
- [ ] expansion plan validated on at least one additional Maxwell GPU
