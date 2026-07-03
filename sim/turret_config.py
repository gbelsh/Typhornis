"""Placeholder specs for the pan/tilt turret + its camera.

⚠️  THESE ARE PLACEHOLDERS, NOT REAL HARDWARE SPECS.
We deferred choosing a real servo/camera (see PLAN.md -> "Open questions"). These round,
slightly-generous numbers let Phase 1 proceed; revisit them once real parts are chosen.

This module is the SINGLE SOURCE OF TRUTH for these tunable values. The turret rig, the camera,
and (later) the PID controller all import from here — so refining a spec means editing ONE line
in ONE file, not hunting through the codebase.

Convention used below: constants are UPPER_CASE, and the UNIT is baked into the name so nobody
ever has to guess (DPS = degrees per second). Guessing units is how spacecraft get lost.
"""

# Each line below is an ASSIGNMENT: NAME = value. It stores `value` under `NAME` so other code
# can `import` it. Without the `= value` part, the name means nothing.

# --- Pan axis (yaw: rotates left/right, like shaking your head "no") -----------------------
# A 2-tuple (min, max). Parentheses with a comma = a "tuple": an ordered, fixed pair of values.
PAN_RANGE_DEG = (-180.0, 180.0)   # full 360 degrees of coverage
PAN_MAX_SPEED_DPS = 180.0         # how fast the servo can slew; becomes the PID output clamp later

# --- Tilt axis (pitch: rotates up/down, like nodding your head "yes") -----------------------
# Drones are above you, so we look from just below the horizon up to straight overhead.
TILT_RANGE_DEG = (-10.0, 90.0)
TILT_MAX_SPEED_DPS = 180.0

# --- Camera --------------------------------------------------------------------------------
CAMERA_FOV_DEG = 60.0             # horizontal field of view (how wide the lens sees)
CAMERA_RESOLUTION = (1280, 720)   # (width, height) in pixels — matches our Phase 0 render
