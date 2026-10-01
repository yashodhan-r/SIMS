#version 330
// ---------------------------------------------------------------------------
// VERTEX SHADER — minimal fullscreen-quad pass-through.
//
// main.py already hands us clip-space positions in [-1,1], so we don't do any
// coordinate math (no screen_size uniform, no NDC conversion). Two jobs:
//   1. forward the vertex position straight to gl_Position (the GPU's
//      "where on screen" built-in),
//   2. forward the texture coordinate to the fragment shader — the GPU
//      interpolates it across the quad, so every pixel gets its own uv.
//
// u = 0 at the left edge -> 1 at the right edge
// v = 0 at the bottom    -> 1 at the top
// ---------------------------------------------------------------------------

in vec2 in_pos;   // vertex position, already in clip space [-1,1]x[-1,1]
in vec2 in_uv;    // texture coordinate of this corner [0,1]x[0,1]

out vec2 uv;      // interpolated per-pixel texture coordinate

void main() {
    uv = in_uv;
    gl_Position = vec4(in_pos, 0.0, 1.0);   // z=0 near plane, w=1 no perspective
}