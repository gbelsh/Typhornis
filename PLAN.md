# Racemus — Simulated Drone-Tracking Camera Turret

## Goal

Build an NVIDIA-style simulated environment (Isaac Sim / Isaac Lab) for training a small,
lightweight pan/tilt camera turret to detect and track drones, aimed eventually at real hardware
mounted on a vehicle or worn on a person.

**Use-case arc (in order of when each becomes real work, not all at once):**

1. **Situational awareness (this plan's near-term scope):** detect a drone, track it by keeping it
   centered with a pan/tilt camera, alert the wearer/team.
2. **Dual-sentry coordination:** two cameras each covering ~180°, idle-scanning independently. When
   one detects and locks a drone, the other slews into alignment to get a second point of view —
   binocular-style coverage for better situational awareness (and, longer term, range/position
   estimation via parallax between the two known mount positions).
3. **Far-future research direction:** characterize the drone's onboard optical sensor (drone camera
   lenses retroreflect light shone along their optical axis — the same "cat's-eye" effect used to
   spot binoculars/scopes) and use a light-based device to temporarily *dazzle/saturate* that sensor
   — not damage it, not signal jamming, not a projectile, nothing kinetic. The goal is a brief
   blind spot for the drone's operator/autopilot, not permanent harm to the sensor or anything else
   in the beam path.

**Milestone 1 (this plan's concrete scope):** a stationary pan/tilt turret in sim that detects a
moving drone via classical motion detection and keeps it centered in frame. No base movement, no
second camera, no countermeasure work yet — those are explicitly later phases.

## Key decisions (locked in)

- **Platform:** NVIDIA Isaac Sim for the world/physics/rendering, Isaac Lab for the RL layer later.
  Photorealistic sky/lighting/drone rendering matters more here than physics fidelity — the hard
  problem is perception (spotting a small moving object against open sky), not actuator dynamics (a
  2-DOF pan/tilt rig is mechanically simple).
- **First baseline:** motion-based detection (frame differencing / optical flow) — sky background is
  mostly static, so a moving drone stands out without needing a trained detector. Paired with a PID
  controller on pan/tilt angle — a simple, deterministic baseline to validate the simulator and
  control loop before any learning is introduced.
- **Mounting target:** undecided between vehicle-mounted and person-worn — kept mount-agnostic for
  now. The first POC is a **stationary base with rotation only**; compensating for the mount itself
  moving (road vibration or walking gait) is explicitly deferred to a later phase.
- **Out of scope, permanently, unless revisited explicitly:** signal jamming, projectiles, or any
  kinetic/destructive countermeasure. The far-future direction is a light-based sensor countermeasure
  only.


## Architecture overview

```
Isaac Sim (USD scene)
 ├─ World: sky dome / lighting rig (sun angle, cloud, glare variation)
 ├─ Turret asset: 2-DOF pan/tilt rigid body + camera sensor
 ├─ Drone asset(s): scripted or randomized flight paths (target to be tracked)
 └─ Python control loop
     ├─ Perception: frame differencing / optical flow → moving-blob centroid
     ├─ Controller: PID on pan/tilt angle to center the blob
     ├─ Alert logic: confidence/size/motion heuristics → "drone detected" event
     └─ Logging: per-step (frame, detection, control output, ground-truth drone pose) → dataset
```

## Phased roadmap

### Stage 1 — Single sentry: detect, track, alert

**Phase 0 — Environment setup**
- Install Isaac Sim + Isaac Lab, verify GPU/driver compatibility.
- Trivial scene: sky dome + one static camera, confirm rendering/toolchain before investing in
  content.

**Phase 1 — Turret & drone asset authoring**
- Build a 2-DOF pan/tilt rig (servo-driven, matching an assumed real servo's speed/torque/range).
- Import or author a simple drone asset (visual model is enough at first — it doesn't need to fly
  itself intelligently, just follow a path).
- Author a handful of scripted drone flight paths (approach, crossing, hover, erratic) to test
  against before anything procedural.

**Phase 2 — Sensor & scene realism**
- Attach an RGB camera to the turret matching an assumed real camera's FOV/resolution.
- Build out sky/lighting variation (sun position, cloud cover, glare) since this is the main source
  of false positives/negatives for a motion-based detector.
- Expose ground-truth drone pose (debug/metrics only, not fed to the controller).

**Phase 3 — Classical baseline: motion detection + PID**
- Perception: frame differencing or optical flow → moving-blob centroid.
- Control: PID mapping centroid error → pan/tilt angular velocity.
- **Success criterion:** turret keeps a drone centered in frame across the scripted flight paths,
  from a stationary base.
- Known weakness to accept for now: motion detection fails on a hovering/near-static drone — that's
  fine, it's a baseline, not the final detector.

**Phase 4 — Detection & alert logic**
- Add lightweight heuristics (size, speed, motion signature) on top of the motion detector to reduce
  false positives (birds, planes, clouds) before calling something a "detected drone."
- Simulate the alert event itself (a logged/notified state change) — the actual notification channel
  (phone, radio, etc.) is a hardware-phase concern, not a sim concern.

**Phase 5 — Data collection framework**
- Log (frame, detection output, control output, ground-truth pose) across many flight paths and
  lighting conditions, driven by the Phase 3 baseline.

**Phase 6 — Imitation learning**
- Train a small model via behavior cloning on the collected data, particularly to handle cases the
  motion-detection baseline struggles with (hover, low contrast, partial occlusion).

**Phase 7 — Reinforcement learning**
- Reward centered on: keep drone in frame, minimize time-to-reacquire after losing track, minimize
  unnecessary slew (smoothness).
- Train with Isaac Lab (PPO/SAC), GPU-parallel environments across many drone/lighting variations.

**Phase 8 — Domain randomization & sim-to-real prep**
- Randomize lighting/sun angle/cloud, drone type/size/speed/distance, background clutter (birds,
  planes, buildings), camera sensor noise.
- Export trained policy to ONNX/TensorRT for Jetson-class deployment.

**Phase 9 — Real hardware bring-up (stationary, single sentry)**
- Build the physical pan/tilt rig, camera, Jetson-class compute.
- Deploy, validate tracking against a real drone, stationary base only (matches the POC scope agreed
  on at the start).
- Measure sim-to-real gap, feed back into Phase 8 randomization.

### Stage 2 — Dual-sentry coordination

**Phase 10 — Base-motion compensation**
- Whichever mount gets picked (vehicle or person), the base now moves. Add IMU-based motion
  compensation to the tracking loop so pan/tilt commands account for the platform's own motion, not
  just the drone's apparent motion in frame.

**Phase 11 — Two-camera handoff & binocular coverage**
- Second turret, ~180° coverage each, independent idle-scan behavior when no target is detected.
- Handoff protocol: when one camera locks a drone, cue the other to slew toward the same
  line-of-sight using the known baseline distance between the two mounts.
- Once both cameras have the target, explore parallax-based range/position estimation (the "two
  points of view" benefit) — this is a new, harder problem (multi-camera calibration, coordinate
  frame transforms) and probably deserves its own sub-plan when this phase gets close.

### Stage 3 — Far-future: optical sensor characterization (research, not committed)

**Phase 12 — Retroreflection-based sensor detection (research spike)**
- Investigate detecting a drone's onboard camera via retroreflection (illuminate along the tracked
  optical axis, look for the "cat's-eye" return).
- Purely a research/feasibility phase — no commitment yet to what, if anything, happens after
  detection.

**Phase 13 — Non-destructive optical countermeasure (research spike, gated on legal/safety review)**
- Explore a light-based method to disrupt the identified sensor, explicitly non-jamming,
  non-kinetic.
- Gated on the legal/safety review noted above before any physical experimentation.

## Proposed repo structure

```
Racemus/
├── sim/                   # Isaac Sim scenes, turret + drone USD assets, flight-path scripts
│   ├── scenes/
│   ├── assets/turret/
│   └── assets/drone/
├── perception/             # motion detection, later learned detector, alert-logic heuristics
├── control/                # PID controller, later RL/IL policies
├── training/                # IL/RL training scripts (Isaac Lab configs, datasets)
├── deploy/                 # ONNX/TensorRT export, Jetson-side inference code
├── data/                    # collected trajectories (or pointers to external storage)
└── docs/
```

## Open questions to resolve before/during Phase 0–1

- Real servo/camera specs to target (affects pan/tilt speed limits and FOV assumptions baked into
  the sim early).
- Source of drone flight paths for training/testing: hand-scripted, replayed real flight logs, or an
  adversarial agent flying a "drone" character with its own policy.
- How "drone vs. not-a-drone" classification should work long-term (bird/plane rejection) — heuristic
  forever, or eventually a small learned classifier.
- Local RTX GPU availability for Isaac Sim, or need for cloud/workstation access.
