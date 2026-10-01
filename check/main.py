# ---------------------------------------------------------------------------
# Ray-marched red sphere over the bg.jpg environment — with free camera.
#
# The demo you'll build in the workshop, in its finished form: every pixel is
# a ray that is MARCHED in small steps through a 3D scene. A fixed-step ray
# march finds the red sphere in the middle; rays that miss it sample the
# surrounding environment image (bg.jpg) by direction, so the panorama
# appears as the sky.
#
# KEYBOARD CONTROLS (the free camera rig)
#   W A S D ..... move forward / back / left / right (level, yaw-based)
#   Arrow keys .. look around (left/right turn, up/down pitch)
#   ESC ......... quit
#
# The whole camera block can be commented out to return to the fixed
# RTOW-style camera — see "FREE CAMERA" markers below.
# ---------------------------------------------------------------------------

import pygame            # window creation + event loop (the "headless" GL needs a real window)
import moderngl          # the OpenGL wrapper we actually draw with
import math              # free-camera: yaw/pitch trig for view basis + movement
from array import array  # compact float buffer (vs. a Python list of floats) for CPU->GPU data
from pathlib import Path # cross-platform file path handling for the shader files

# Files live relative to this script, so the demo runs from any directory.
BASE = Path(__file__).parent

pygame.init()

# 800x600 window. DOUBLEBUF | OPENGL hands the GL context to us; then
# ModernGL drives the GPU instead of pygame's software rendering.
WINDOW = (800, 600)
pygame.display.set_mode(WINDOW, pygame.DOUBLEBUF | pygame.OPENGL)
ctx = moderngl.create_context()

# Compile both shaders into one linked "program".
prog = ctx.program(
    vertex_shader=(BASE / "shaders/uv.vert.glsl").read_text(),
    fragment_shader=(BASE / "shaders/uv.frag.glsl").read_text(),
)

# ---------------------------------------------------------------------------
# Fullscreen quad: two triangles that exactly cover the window. Each vertex
# carries a clip-space position [-1,1] (no conversion needed on the GPU) and
# a texture coordinate u,v in [0,1] with (0,0) bottom-left — the same uv
# convention the raytracker shaders use for the image plane.
# ---------------------------------------------------------------------------
vertices = array('f', [
    #   x      y     u   v
    -1.0,  -1.0,  0.0, 0.0,
     1.0,  -1.0,  1.0, 0.0,
    -1.0,   1.0,  0.0, 1.0,

    -1.0,   1.0,  0.0, 1.0,
     1.0,  -1.0,  1.0, 0.0,
     1.0,   1.0,  1.0, 1.0,
])

vbo = ctx.buffer(vertices.tobytes())
# '2f 2f': 2 floats per vertex as in_pos, then 2 floats as in_uv.
vao = ctx.vertex_array(prog, [(vbo, '2f 2f', 'in_pos', 'in_uv')])

# The fragment shader needs the window aspect ratio to keep the sphere
# circular (non-stretched); setting the uniform once is enough.
prog['screen_size'].value = WINDOW

# ---------------------------------------------------------------------------
# Environment background (bg.jpg): the "sky" that missed rays sample.
# ---------------------------------------------------------------------------
bg_img = pygame.image.load(BASE / "shaders/bg.jpg").convert()   # supports .jpg natively
bg_w, bg_h = bg_img.get_size()

# Upload raw RGB pixels to a GPU texture (components=3 = RGB).
bg_tex = ctx.texture((bg_w, bg_h), 3, pygame.image.tostring(bg_img, "RGB", True))
bg_tex.filter = (moderngl.LINEAR, moderngl.LINEAR)   # smooth texel interpolation
bg_tex.use(0)                                        # bind to texture unit 0
prog['bg_tex'].value = 0                             # tell the sampler which unit

# ---------------------------------------------------------------------------
# FREE CAMERA RIG (WASD = move, arrows = look)
#
# Counterpart of FREE_CAMERA in uv.frag.glsl. To disable the rig and go back
# to the fixed camera:
#   a) comment out BOTH lines below that set cam_pos / cam_angles,
#   b) set #define FREE_CAMERA 0 in the shader   (the program is compiled
#      WITHOUT those uniforms then, so Python must not upload them).
# ---------------------------------------------------------------------------
cam_pos = [0.0, 0.0, 0.0]     # world space, x-right, y-up, z-toward the viewer
cam_yaw = 0.0                 # rad; 0 = facing -Z (must match the shader basis)
cam_pitch = 0.0               # rad; 0 = level, +90 = straight up
MOVE_SPEED = 3.0              # world units per second
TURN_SPEED = 2.5              # radians per second
MAX_PITCH = 1.55              # ~±89° — stops the view flipping over the head

prog['cam_pos'].value = cam_pos                   # <-- disable camera: kill this
prog['cam_angles'].value = (cam_yaw, cam_pitch)   # <-- ...and this one

# ---------------------------------------------------------------------------
# Render loop: clear, draw, flip. 60 fps cap.
# ---------------------------------------------------------------------------
clock = pygame.time.Clock()
running = True

while running:
    # dt = seconds since the last frame (also caps us to ~60 FPS).
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # -----------------------------------------------------------------------
    # FREE CAMERA CONTROLS (comment this whole block out to disable)
    # -----------------------------------------------------------------------
    keys = pygame.key.get_pressed()   # snapshot of all held keys this frame

    # Arrow keys rotate the view: left = yaw++, right = yaw--, up/down pitch ±.
    if keys[pygame.K_LEFT]:
        cam_yaw += TURN_SPEED * dt
    if keys[pygame.K_RIGHT]:
        cam_yaw -= TURN_SPEED * dt
    if keys[pygame.K_UP]:
        cam_pitch += TURN_SPEED * dt
    if keys[pygame.K_DOWN]:
        cam_pitch -= TURN_SPEED * dt
    cam_pitch = max(-MAX_PITCH, min(MAX_PITCH, cam_pitch))   # clamp, no flip

    # Horizontal movement plane, from the same yaw the shader uses (before
    # pitching, so WASD always slides at a level altitude):
    #   forward (W/S) = (sin yaw, -cos yaw),  right (D/A) = (cos yaw, sin yaw)
    fx, fz = math.sin(cam_yaw), -math.cos(cam_yaw)
    rx, rz = math.cos(cam_yaw),  math.sin(cam_yaw)
    # keys[...] are bools; True-False works as 1/0, added per axis.
    cam_pos[0] += (fx * (keys[pygame.K_w] - keys[pygame.K_s])
                 + rx * (keys[pygame.K_d] - keys[pygame.K_a])) * MOVE_SPEED * dt
    cam_pos[2] += (fz * (keys[pygame.K_w] - keys[pygame.K_s])
                 + rz * (keys[pygame.K_d] - keys[pygame.K_a])) * MOVE_SPEED * dt

    # Ship the camera to the GPU for this frame's rays.
    prog['cam_pos'].value = cam_pos
    prog['cam_angles'].value = (cam_yaw, cam_pitch)

    ctx.clear(0.1, 0.1, 0.1, 1.0)          # grey background if nothing draws
    vao.render(moderngl.TRIANGLES)         # vertex + fragment shaders
    pygame.display.flip()                  # show the freshly drawn frame

pygame.quit()