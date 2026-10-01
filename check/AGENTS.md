# AGENTS.md — check/ workshop project

## Stack
- Python 3.11, managed with uv
- moderngl (OpenGL wrapper), pygame 2.6 (window + events)
- GLSL 330 (clip-space fullscreen quad)

## Commands
- Run the demo: `uv run main.py`
- Add a dependency: `uv add --no-sync <pkg>` (no-sync keeps the folder zip-clean — no .venv)
- Verify a clean environment after zipping: unzip, `uv run main.py` (uv rebuilds .venv)
- Before zipping: `rm -rf .venv __pycache__`

## Layout
- `main.py` — window, free-camera rig (WASD + arrows), fullscreen quad, bg.jpg upload
- `shaders/uv.vert.glsl` — vertex pass-through (clip-space pos + uv)
- `shaders/uv.frag.glsl` — the raymarcher: yaw/pitch camera basis, fixed-step
  sphere march, env_uv() panorama background; FREE_CAMERA kill-switch
- `shaders/bg.jpg` — equirectangular environment panorama (x/y/zenith mapping
  handled in env_uv())
- `pyproject.toml` + `uv.lock` — pinned deps for reproducible installs

## Conventions
- Copy of the parent raytracing project (main.py + uv.frag.glsl + bg.jpg at par)
- uv convention: (0,0) bottom-left → (1,1) top-right, matches parent
- Do NOT commit or zip `.venv/` (platform-specific install cache)