#version 330
// ===========================================================================
// FRAGMENT SHADER — RAY MARCHING + ENVIRONMENT IMAGE BACKGROUND
//
// Runs once for EVERY PIXEL in the window (in parallel, by the GPU). Each
// pixel executes this whole program: it shoots a ray through a virtual image
// plane into a 3D scene and colours the pixel by what the ray hits.
//
// This is the ModernGL twin of shaders/shadertoy_raymarch.glsl (which was
// derived from shaders/shadertoy.glsl). The one change made here vs. that
// file: the Shadertoy channel lookup (iChannel0) becomes a ModernGL sampler
// uniform (bg_tex) that main.py feeds with bg.jpg.
//
// Stage 1 (RTOW ch.1–5): analytic ray tracing — hit_sphere()  [kept for ref]
// Stage 2 (used here):    fixed-step ray marching — march_sphere()
// Background:             equirectangular environment image bg.jpg, sampled
//                         by ray direction via env_uv() (NOT a gradient sky)
// Camera:                 free WASD/arrow rig driven by main.py uniforms
//                         (disable with FREE_CAMERA 0 below)
// ===========================================================================

// uv comes from the vertex shader, interpolated per pixel: uv.x, uv.y in [0,1]
// over the whole window. (0,0) is bottom-left, (1,1) is top-right.
in vec2 uv;

// Colour this shader ultimately writes. vec4 = RGBA (alpha=1 => opaque).
out vec4 f_color;

// Window size, uploaded once by main.py via prog['screen_size'].value.
// Used to compute the aspect ratio so the sphere isn't stretched horizontally.
uniform vec2 screen_size;

// The environment panorama (bg.jpg). main.py uploads it, binds it to texture
// unit 0, and sets this sampler to 0. In GLSL 1.30+ the function is
// texture(), not the old texture2D(). No WebGL shim needed here.
uniform sampler2D bg_tex;

const float kPI = 3.141592653589793;   // used by env_uv() below

// ===========================================================================
// FREE CAMERA KILL-SWITCH (the "camera controls" block)
// ===========================================================================
// 1 = free camera, driven every frame by main.py (WASD move, arrows look).
// 0 = original fixed RTOW camera: at the origin (0,0,0), looking down -Z.
//
// To remove the camera rig completely:
//   a) set FREE_CAMERA to 0  (this file),  AND
//   b) comment out the camera block in main.py (the uniforms won't exist,
//      so Python must not try to upload them).
// ===========================================================================
#define FREE_CAMERA 1

#if FREE_CAMERA
    // Uploaded every frame by main.py. cam_angles.x = yaw (turn around the
    // vertical axis; 0 => facing -Z), cam_angles.y = pitch (look up/down).
    uniform vec3 cam_pos;
    uniform vec2 cam_angles;
#endif

// ===========================================================================
// STAGE 1  —  analytic ray tracing (kept for reference, unused)
// ===========================================================================
// ---------------------------------------------------------------------------
// Ray–sphere intersection: exact quadratic solve.
//
// A sphere of radius `radius` centred at `center` satisfies |p - center|^2 = r^2.
// A ray is p(t) = o + t*d. Substituting and expanding gives a quadratic
//   a t^2 + b t + c = 0   with
//     a = dot(d, d),  b = 2*dot(oc, d),  c = dot(oc,oc) - r^2,  oc = o - center
// The discriminant b^2 - 4ac says whether the ray hits; the smaller root is
// the entry point. Returns nearest hit distance t, or -1.0 on a miss.
// ---------------------------------------------------------------------------
float hit_sphere(vec3 center, float radius, vec3 o, vec3 d) {
    vec3 oc = o - center;
    float a = dot(d, d);
    float b = 2.0 * dot(oc, d);
    float c = dot(oc, oc) - radius * radius;
    float disc = b * b - 4.0 * a * c;
    if (disc < 0.0) {
        return -1.0;                  // no real roots => miss
    }
    return (-b - sqrt(disc)) / (2.0 * a);  // smaller root = entry point
}

// ===========================================================================
// STAGE 2  —  fixed-step ray marching (the one actually used)
// ===========================================================================
// ---------------------------------------------------------------------------
// Marched ray–sphere intersection.
//
// Instead of solving the sphere equation exactly (stage 1), we step along the
// ray p(t) = o + t*d from t=0 in fixed increments of `step` and *check*
// whether the current point falls inside the sphere (|p - center| < radius).
// The first point found inside is the hit; its t is returned.
//
// Cost vs. quality: a big step is fast but chunky at the sphere's edge
// (silhouette is ladder-like, at most `step` thick); a small step is smooth
// but needs more iterations. 512 constant-bound iterations stay well past the
// whole scene (max t here is ~2) while keeping the loop bound a constant, as
// required by some GLSL compilers.
// ---------------------------------------------------------------------------
float march_sphere(vec3 center, float radius, vec3 o, vec3 d) {
    float step = 0.005;              // world units between samples
    for (int i = 0; i < 512; i++) {  // hard cap on iterations (constant bound)
        float t = float(i) * step;   // current distance along the ray
        vec3 p = o + t * d;          // point at that distance
        if (length(p - center) < radius) {
            return t;                // inside the sphere -> hit
        }
        if (t > 20.0) break;         // wandered past the whole scene -> give up
    }
    return -1.0;                     // no hit found -> miss
    // ponytail: fixed step + binary "inside?" test; chunky silhouette near the
    // edge. Prefer a signed-distance field (f(p) = |p-c| - r, advance f(p))
    // when you want adaptive stepping / smooth normals.
}

// ---------------------------------------------------------------------------
// env_uv(): equirectangular environment lookup.
//
// bg.jpg is a flat lat-long panorama (360° azimuth along U, -90°..+90°
// elevation along V). Map a ray direction -> texture coordinate so the image
// surrounds the scene:
//
//   U: azimuth. atan(dir.z, dir.x) in [-π, π]; /(2π) + 0.5 -> [0,1], wrapping
//      the image's width once (seam at +/-π = the image's left/right edges —
//      behind the camera, since it looks down -Z, atan(-1,0) = -π/2 -> 0.25,
//      the panorama's horizontal centre).
//   V: elevation. asin(dir.y) in [-π/2, π/2]; 0.5 - .../π maps the horizon to
//      0.5 and puts the image's zenith (first row of the JPEG) at dir up = +Y.
// ---------------------------------------------------------------------------
vec2 env_uv(vec3 dir) {
    return vec2(
        0.5 + atan(dir.z, dir.x) / (2.0 * kPI),   // azimuth -> U
        0.5 - asin(clamp(dir.y, -1.0, 1.0)) / kPI // elevation -> V
    );
}

// Entry point for the ModernGL fullscreen-quad pass.
void main() {
    // -----------------------------------------------------------------------
    // CAMERA / RAY GENERATION
    // Camera looks through a virtual image plane one unit in front of it:
    //   focal length 1.0   (image plane at z = -1)
    //   viewport height 2.0 (y spans [-1, 1])
    //   viewport width  2.0 * aspect (x spans [-aspect, +aspect])
    // The fragment's uv says WHERE on the image plane this pixel is; each
    // pixel shoots a ray from the camera through that point.
    // -----------------------------------------------------------------------
    float aspect = screen_size.x / screen_size.y;   // e.g. 800/600 = 4/3

    // CHANGED: camera is now a moving rig instead of a constant.
    // FREE_CAMERA builds an orthonormal view basis (forward/right/up) from the
    // look angles so rays are formed as  right*X + up*Y + forward  below.
#if FREE_CAMERA
    // Angles -> basis. Yaw rotates around Y (0 => facing -Z), pitch around the
    // horizontal axis. Straight computation of the spherical-coordinate frame:
    //   forward = (cos p · sin y,  sin p,  -cos p · cos y)
    //   right   = (cos y, 0, sin y)                (horizontal, y-locked)
    //   up      = right × forward                  (keeps it orthonormal)
    vec3 forward = vec3(
        cos(cam_angles.y) * sin(cam_angles.x),
        sin(cam_angles.y),
        -cos(cam_angles.y) * cos(cam_angles.x)
    );
    vec3 right = vec3(cos(cam_angles.x), 0.0, sin(cam_angles.x));
    vec3 up = vec3(
        -sin(cam_angles.y) * sin(cam_angles.x),
        cos(cam_angles.y),
        sin(cam_angles.y) * cos(cam_angles.x)
    );
    vec3 o = cam_pos;                       // ray origin = camera position
#else
    // Original fixed camera: origin at (0,0,0), looking straight down -Z.
    vec3 forward = vec3(0.0, 0.0, -1.0);
    vec3 right   = vec3(1.0, 0.0, 0.0);
    vec3 up      = vec3(0.0, 1.0, 0.0);
    vec3 o       = vec3(0.0);
#endif

    // CHANGED: pixel position on the image plane in [−aspect, aspect]×[−1, 1],
    // then expressed in the view basis. FREE_CAMERA=0 reduces this to the old
    // vec3((uv.x*2-1)*aspect, uv.y*2-1, -1) exactly.
    vec2 ndc = (uv * 2.0 - 1.0) * vec2(aspect, 1.0);
    vec3 d = normalize(right * ndc.x + up * ndc.y + forward);

    // March toward the sphere: centre (0,0,-1), radius 0.5 (frame centre).
    float t = march_sphere(vec3(0.0, 0.0, -1.0), 0.5, o, d);

    vec3 color;
    if (t > 0.0) {
        // Hit the sphere -> red (RTOW ch.5).
        // ponytail: single shade of red, no lighting/normals yet. Add the
        // normal-based shading (RTOW ch.6) when the flat disc gets boring.
        color = vec3(1.0, 0.0, 0.0);
    } else {
        // Missed -> sample the environment image bg.jpg with the ray
        // direction (replaces the old blue-gradient sky).
        color = texture(bg_tex, env_uv(d)).rgb;
    }

    // Write the RGBA pixel colour. Alpha = 1.0 (fully opaque).
    f_color = vec4(color, 1.0);
}