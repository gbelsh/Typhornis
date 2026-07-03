"""Phase 0 first scene — a sky dome + one static camera, rendered to a PNG.

This is the "confirm the toolchain end-to-end" milestone from PLAN.md Phase 0: build the
simplest possible world (a lit sky and a camera looking at it), render one frame through the
RTX renderer, and write it to disk. A non-black PNG of blue sky proves the full pipeline works:
scene authoring -> RTX rendering -> camera capture -> image output.

No pan/tilt turret and no drone yet — those are Phase 1. This is deliberately the least
content that still exercises rendering.

Note on output: Kit swallows Python stdout, so print() is unreliable here. We capture the
frame as a NumPy array (so we can verify it's not black), save the PNG ourselves via Pillow,
and write a plain-text status.txt sidecar with the pixel stats — that sidecar is the ground
truth for whether this worked.

Run:    D:\\source\\Racemus\\.venv\\Scripts\\python.exe sim\\scenes\\phase0_sky_camera.py
Output: sim/scenes/_output/rgb_0000.png  and  sim/scenes/_output/status.txt
"""

from isaacsim import SimulationApp

# Creating SimulationApp boots the Kit engine + RTX renderer. Headless still renders on the
# GPU; it just doesn't open an interactive window. Must come before any omni.* / pxr import.
sim_app = SimulationApp({"headless": True})

import os

import numpy as np
from PIL import Image
from pxr import UsdGeom, UsdLux, Gf
import omni.usd
import omni.replicator.core as rep

out_dir = os.path.join(os.path.dirname(__file__), "_output")
os.makedirs(out_dir, exist_ok=True)
status_path = os.path.join(out_dir, "status.txt")


def write_status(msg):
    # Bypass Kit's swallowed stdout — append to a file we control so we always know how far we got.
    with open(status_path, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


# Fresh status file each run.
open(status_path, "w", encoding="utf-8").close()
write_status("booted SimulationApp")

# --- Build the world -----------------------------------------------------------------------
usd_context = omni.usd.get_context()
usd_context.new_stage()
stage = usd_context.get_stage()
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)  # Z-up: Isaac Sim's convention (Z points up)

# Sky dome: a DomeLight is an infinite sphere enclosing the scene that both lights it and
# forms the background. With no HDRI texture it emits a flat color — we tint it sky-blue so
# the rendered background reads as sky. (Realistic sky/cloud/sun variation is Phase 2.)
dome = UsdLux.DomeLight.Define(stage, "/World/SkyDome")
dome.CreateIntensityAttr(1000.0)
dome.CreateColorAttr(Gf.Vec3f(0.35, 0.55, 0.90))
write_status("built sky dome")

# --- Camera + render output ----------------------------------------------------------------
# One static camera near the origin, looking out toward the horizon (down +X, slightly up)
# so the frame is filled with sky. Positions are in meters.
camera = rep.create.camera(position=(0.0, 0.0, 2.0), look_at=(10.0, 0.0, 3.0))
render_product = rep.create.render_product(camera, (1280, 720))

# Attach an RGB annotator so we can pull the rendered pixels straight into a NumPy array.
rgb_annot = rep.AnnotatorRegistry.get_annotator("rgb")
rgb_annot.attach([render_product])
write_status("camera + rgb annotator attached")

# Drive Replicator's pipeline: orchestrator.step() renders the render product AND fills the
# annotator (plain sim_app.update() does not step the synthetic-data graph). The first steps
# come back empty/black while the RTX renderer warms up, so retry until we get real pixels.
arr = np.zeros((0,))
for i in range(40):
    rep.orchestrator.step(rt_subframes=8)
    arr = np.asarray(rgb_annot.get_data())
    if arr.size > 0 and arr.ndim == 3:
        write_status(f"frame ready after {i + 1} steps: shape={arr.shape} dtype={arr.dtype}")
        break
else:
    write_status("annotator never returned pixels after 40 steps")

# Save the PNG + record stats BEFORE close(), so headless teardown crashing on the way out
# can't cost us the artifact or the evidence.
if arr.size > 0 and arr.ndim == 3 and arr.shape[2] >= 3:
    write_status(f"pixel stats: min={int(arr.min())} max={int(arr.max())} mean={float(arr.mean()):.1f}")
    png_path = os.path.join(out_dir, "rgb_0000.png")
    Image.fromarray(arr[:, :, :3].astype(np.uint8)).save(png_path)
    write_status(f"wrote PNG: {png_path}")
else:
    write_status("no usable frame — did not write PNG")

write_status("done; closing app")
sim_app.close()
