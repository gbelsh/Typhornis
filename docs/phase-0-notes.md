# Phase 0 — setup notes / handoff

Living scratch notes for environment setup. Read alongside [PLAN.md](../PLAN.md).

## Where we are (2026-07-03)

Working through **Phase 0 — Environment setup**. Isaac Sim install underway (see log below).

### Progress log
- ✅ Claude Code running natively on Windows; project relocated to `D:\source\Racemus`
  (note: on **D:**, not `C:\Users\zerod\source` as the old next-steps said — D: has ~3 TB free).
- ✅ Re-confirmed GPU/driver on this box: RTX 3090, driver 591.86, CUDA 13.1.
- ✅ Windows **long path support already enabled** (`LongPathsEnabled=1`) — no admin/registry change needed.
- ✅ Install method decision: **pip venv** (chosen over the workstation binary) — keeps sim +
  perception + control + later Isaac Lab RL in one Python 3.11 env, matches the script-driven roadmap.
- ✅ Created venv at `D:\source\Racemus\.venv` (Python 3.11.4). Added `.gitignore` (excludes `.venv/`).
- ✅ Installed `isaacsim[all,extscache]==5.1.0` (~25 GB) via `--extra-index-url https://pypi.nvidia.com`.
- ✅ Reinstalled PyTorch as the CUDA build: `torch==2.7.0+cu128` etc. (isaacsim pulls a CPU torch by
  default — verified `torch.cuda.is_available() == True`, device = RTX 3090).
- ✅ Verified Isaac Sim boots headless + RTX renderer detects the GPU (boot-log GPU table shows
  "NVIDIA GeForce RTX 3090 | Active Yes | 24540 MB | Vulkan"). Smoke test: `sim/verify_install.py`.
- ✅ First trivial scene rendered: sky dome (DomeLight) + one static camera → `rgb_0000.png`
  (1280x720 blue sky, pixel mean ~216). Script: `sim/scenes/phase0_sky_camera.py`,
  output under `sim/scenes/_output/` (gitignored).

**Phase 0 is COMPLETE.** Next up: Phase 1 (turret + drone asset authoring) — see PLAN.md.

### Gotchas learned (save the next person time)
- **Kit swallows Python `print()`** in these scripts — stdout doesn't reach the terminal/log.
  Write results to a sidecar file instead (see `status.txt` pattern in `phase0_sky_camera.py`).
- **To capture a rendered frame headless**, drive the pipeline with `rep.orchestrator.step()`
  (NOT `sim_app.update()` — that doesn't step the synthetic-data graph, so annotators stay empty).
  First 1-2 steps come back empty while RTX warms up; retry until `get_data()` is non-empty.
- **`OMNI_KIT_ACCEPT_EULA=YES`** env var is required for headless runs (else it hangs on an
  invisible license prompt).
- Deprecation warnings (`omni.isaac.* -> isaacsim.*`) are harmless noise from Isaac's own bundled
  extensions, not our code.
- Call the venv python directly (`D:\source\Racemus\.venv\Scripts\python.exe`); shell `activate`
  doesn't persist between tool calls.

### Reference — exact install commands (Windows, Python 3.11)
```
py -3.11 -m venv D:\source\Racemus\.venv
D:\source\Racemus\.venv\Scripts\python.exe -m pip install --upgrade pip
D:\source\Racemus\.venv\Scripts\python.exe -m pip install "isaacsim[all,extscache]==5.1.0" --extra-index-url https://pypi.nvidia.com
D:\source\Racemus\.venv\Scripts\python.exe -m pip install -U torch==2.7.0 torchvision==0.22.0 --index-url https://download.pytorch.org/whl/cu128
```
(Call the venv's python.exe directly — shell `activate` does not persist between tool calls.)

### Hardware — confirmed OK
- GPU: **NVIDIA GeForce RTX 3090, 24 GB VRAM** (RT cores present). Windows host driver 591.86, CUDA 13.1.
- RAM 32 GB, ~900 GB free disk. All meet Isaac Sim needs.
- Note: RTX 3090 is below Isaac Sim 5.1's *stated* minimum (RTX 4080) but has the two things
  that matter (RT cores + 24 GB VRAM) and runs fine for Milestone-1-scale scenes. Drop to an
  earlier Isaac Sim version only if 5.1 perf becomes a problem.

### Key environment decision
- **Isaac Sim is NOT supported inside WSL2** — NVIDIA confirms RTX/rendering features don't work
  there (compute/CUDA works, ray-traced rendering does not). Since realistic rendering is the whole
  point of this project, Isaac Sim must run **natively on Windows**.
- Decision: **run Claude Code on Windows too**, project relocated to `D:\source\Racemus`,
  so the sim, the code, and the assistant all live in one place.
- The pure-Python perception/control code (OpenCV motion detection, PID) does not need rendering and
  could run anywhere, but we're keeping everything on Windows for simplicity.

### User context (for whoever picks this up)
- First-timer with robotics sim / Isaac Sim / CV / RL / PID. Teaching project — explain concepts in
  plain terms the first time they appear, explain installs before running them, check in at
  breakpoints rather than running long unattended checklists.

## Next steps (resume here on Windows)
1. Install Claude Code natively on Windows; reopen this project from `C:\Users\zerod\source\Racemus`.
2. Install **Isaac Sim 5.1** on Windows (native). Decide install method: pre-built binary vs pip
   (pip route needs a Python 3.11 venv). Explain the choice before downloading (~tens of GB).
3. Verify Isaac Sim launches and the GPU/RTX renderer is detected.
4. First trivial scene: sky dome + one static camera, to confirm the toolchain before authoring
   content (per PLAN.md Phase 0).
