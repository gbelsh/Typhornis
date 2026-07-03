"""Phase 0 smoke test — confirm Isaac Sim 5.1 boots and the RTX renderer sees the GPU.

Runs headless (no window): it starts the Kit engine + RTX renderer, opens an empty USD
stage, prints the detected GPU, then shuts down. This is the toolchain sanity check before
we author any real scene content. It is also the minimal template every later scene script
follows: create SimulationApp FIRST, then import omni.* modules, do work, then close().

Run:  D:\\source\\Racemus\\.venv\\Scripts\\python.exe sim\\verify_install.py
"""

# SimulationApp must be created before importing any omni.* / pxr modules — creating it is
# what boots the Kit engine and makes those modules importable.
from isaacsim import SimulationApp

sim_app = SimulationApp({"headless": True})

# --- Kit is now running; omni.* and pxr are available. -----------------------------------
import carb
import omni.usd
from pxr import Usd, UsdGeom

# Prove USD works: create an empty in-memory stage.
usd_context = omni.usd.get_context()
usd_context.new_stage()
stage = usd_context.get_stage()
print("[verify] USD stage created:", stage is not None)

# Report the GPU the RTX renderer picked up. carb exposes it via renderer settings; if that
# key is unavailable in this build we fall back to the boot log (which prints the GPU table).
settings = carb.settings.get_settings()
gpu_name = settings.get("/renderer/gpuName") or settings.get("/rtx/gpuName")
print("[verify] renderer GPU (via carb):", gpu_name if gpu_name else "(see boot log GPU table)")

print("[verify] Isaac Sim initialized OK — toolchain works.")

sim_app.close()
print("[verify] clean shutdown — smoke test complete.")
