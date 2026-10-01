# Workshop check — ray-marched sphere over an environment image

The finished version of what you'll build in the workshop: a GPU ray marcher
that renders a red sphere in the middle of a full 360° panorama (bg.jpg),
with a free camera you fly around with the keyboard.

**Expected result:** the bg.jpg panorama as the sky, a red sphere dead
centre, and the ability to walk around it with WASD + arrows.

## Controls

| Key | Action |
|---|---|
| `W` `A` `S` `D` | move forward / back / left / right (level flight) |
| Arrow keys | look around (left/right turn, up/down pitch) |
| `ESC` | quit |

The camera rig is fully optional: comment out the "FREE CAMERA" block in
`main.py` (and the two `prog['cam_pos']/['cam_angles']` lines) plus set
`#define FREE_CAMERA 0` in `shaders/uv.frag.glsl` to get the fixed camera
back.

## Prerequisites

- Install `uv` (the Python package manager we use): https://docs.astral.sh/uv/
  Or on Windows/macOS/Linux: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Run it

```
uv run main.py
```

First run downloads Python 3.11 + the dependencies (ModernGL, pygame)
automatically — give it a minute. Subsequent runs are instant.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `pygame.error: No available video device` (headless/WSL) | Run on your real desktop, not a VM/SSH |
| Blank black window | Most laptop GPUs work; update your graphics driver to get OpenGL 3.3+ |
| Black circle instead of the panorama | Means bg.jpg didn't load — check `shaders/bg.jpg` is in the folder |
| Slow / jerky movement | The 512-step march is fixed cost; on weak GPUs lower `MAX_STEPS` in the shader |

## What's in here

- **main.py** — window, input, camera rig, fullscreen quad, bg.jpg upload.
- **shaders/uv.vert.glsl** — vertex pass-through (feeds each pixel its uv).
- **shaders/uv.frag.glsl** — the whole raymarcher: camera basis built from
  yaw/pitch, fixed-step sphere march, `env_uv()` panorama lookup.
- **shaders/bg.jpg** — the equirectangular environment panorama.