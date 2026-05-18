"""Render 5 smooth NIGHTGLOW star icons in the V5 PUNCH+ palette.

User: "colors should look like glow is active, as all elements look
like; icon should be smooth, looks heavily overlayered."

Two fixes from the prior version:

  1. PALETTE. Use the EXACT recolour palette from the in-world V5
     PUNCH+ effect (game/tools/render_nightglow_variants.py:
     dark=(8, 60, 22) → bright=(220, 255, 230)). The icon will then
     read as "a piece of the glowing scene" — exactly the colours the
     player sees on Pip / coins / vegetation while nightglow is up.

  2. SMOOTHNESS. The 42-layer-of-stars approach still produced
     visible banding because each polygon's anti-aliased edge created
     a faint ring. Replaced with a true per-pixel radial gradient via
     numpy + pygame.surfarray: every pixel gets its own colour
     interpolated from the distance-to-centre, so there is no banding
     possible — only the silhouette is rendered as a polygon, then
     the inside is filled pixel-by-pixel.

5 takes, all on the same V5 palette, varying the gradient curve and
peak location:

    1. SMOOTH         — pure linear radial ramp (the family reference)
    2. BRIGHT-CORE    — ease-out: more of the star sits in the bright
                         tones, edge darkens only near the rim
    3. CONCENTRATED   — ease-in: smaller bright core, most of the
                         star is mid-tone
    4. PEAKED         — quadratic ease-out: very bright tight centre,
                         rest fades smoothly to the rim
    5. CINEMATIC      — slight gamma boost so mid-tones lift —
                         maximises the "glowing from within" read
"""

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import numpy as np
import pygame
import pygame.surfarray

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

pygame.init()
pygame.display.set_mode((1, 1))


CANVAS = 240
CENTER = CANVAS // 2

# EXACT V5 PUNCH+ palette — the colours the player sees in-world when
# nightglow is active. Source: tools/render_nightglow_variants.py
# _green_recolour endpoints.
DARK   = (8,   60,  22)
BRIGHT = (220, 255, 230)


def _dark_backdrop() -> pygame.Surface:
    surf = pygame.Surface((CANVAS, CANVAS)).convert()
    for y in range(CANVAS):
        t = y / CANVAS
        r = int(4 + (12 - 4) * t)
        g = int(8 + (20 - 8) * t)
        b = int(22 + (38 - 22) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (CANVAS, y))
    import random as _r
    rng = _r.Random(11)
    for _ in range(18):
        x = rng.randint(0, CANVAS - 1)
        y = rng.randint(0, CANVAS - 1)
        pygame.draw.circle(surf, (220, 220, 200), (x, y), 1)
    return surf


def _star_points(cx, cy, r_outer, r_inner, n=5, rot=-math.pi / 2):
    pts = []
    for i in range(n * 2):
        a = rot + i * math.pi / n
        r = r_outer if i % 2 == 0 else r_inner
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def _star_silhouette(cx, cy, r_outer, r_inner) -> pygame.Surface:
    """Anti-aliased white-on-transparent star — used as the alpha mask
    for the gradient fill. Drawn at 4× supersample then smoothscaled
    so edges are clean without any visible polygon facets."""
    SS = 4
    big = pygame.Surface((CANVAS * SS, CANVAS * SS), pygame.SRCALPHA)
    pts = _star_points(cx * SS, cy * SS, r_outer * SS, r_inner * SS)
    pygame.draw.polygon(big, (255, 255, 255, 255), pts)
    return pygame.transform.smoothscale(big, (CANVAS, CANVAS))


def _smooth_gradient_star(cx, cy, r_outer, r_inner,
                          dark=DARK, bright=BRIGHT,
                          curve=None) -> pygame.Surface:
    """One smooth, banding-free star.

    For every pixel inside the star silhouette, computes its
    Euclidean distance to (cx, cy), normalises to [0, 1] against
    r_outer, and lerps the per-pixel colour from `bright` at t=0
    (centre) to `dark` at t=1 (edge). `curve` reshapes the [0, 1]
    parameter for non-linear ramps.

    Per-pixel math = zero banding by construction; smoothness is only
    limited by 8-bit colour precision."""
    if curve is None:
        curve = lambda t: t

    # 1. Build the silhouette (defines alpha + which pixels are inside).
    sil = _star_silhouette(cx, cy, r_outer, r_inner)

    # 2. Compute per-pixel normalised distance from centre.
    #    pygame.surfarray indexing is (W, H, ...).
    xs = np.arange(CANVAS, dtype=np.float32)[:, None]
    ys = np.arange(CANVAS, dtype=np.float32)[None, :]
    dx = xs - cx
    dy = ys - cy
    dist = np.sqrt(dx * dx + dy * dy)
    t = np.clip(dist / r_outer, 0.0, 1.0)
    t = curve(t)

    # 3. Lerp the colour ramp per pixel: bright at t=0, dark at t=1.
    bright_arr = np.array(bright, dtype=np.float32)
    dark_arr   = np.array(dark,   dtype=np.float32)
    rgb = bright_arr + (dark_arr - bright_arr) * t[..., None]
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)

    # 4. Write the gradient RGB into the silhouette surface (alpha
    #    stays as the soft-edge mask).
    pygame.surfarray.pixels3d(sil)[:] = rgb
    return sil


R_OUT, R_IN = 80, 34


# ─── easing curves ──────────────────────────────────────────────────────────

def _linear(t):      return t
def _ease_out(t):    return 1.0 - (1.0 - t) ** 2.4    # bright lingers
def _ease_in(t):     return t ** 2.4                  # bright sharpens
def _peaked(t):      return t ** 1.6                  # gentler ease-in
def _cinematic(t):   return np.power(t, 0.75)         # gamma-lift mids


# ─── VARIANT 1 — SMOOTH (linear reference) ──────────────────────────────────

def variant_smooth(surf):
    star = _smooth_gradient_star(CENTER, CENTER, R_OUT, R_IN,
                                 curve=_linear)
    surf.blit(star, (0, 0))


# ─── VARIANT 2 — BRIGHT-CORE (ease-out: wider bright zone) ──────────────────

def variant_bright_core(surf):
    star = _smooth_gradient_star(CENTER, CENTER, R_OUT, R_IN,
                                 curve=_ease_out)
    surf.blit(star, (0, 0))


# ─── VARIANT 3 — CONCENTRATED (ease-in: tighter bright core) ────────────────

def variant_concentrated(surf):
    star = _smooth_gradient_star(CENTER, CENTER, R_OUT, R_IN,
                                 curve=_ease_in)
    surf.blit(star, (0, 0))


# ─── VARIANT 4 — PEAKED (sharp bright centre, smooth fall-off) ──────────────

def variant_peaked(surf):
    star = _smooth_gradient_star(CENTER, CENTER, R_OUT, R_IN,
                                 curve=_peaked)
    surf.blit(star, (0, 0))


# ─── VARIANT 5 — CINEMATIC (mids lifted, glowing-from-within read) ──────────

def variant_cinematic(surf):
    star = _smooth_gradient_star(CENTER, CENTER, R_OUT, R_IN,
                                 curve=_cinematic)
    surf.blit(star, (0, 0))


# ─── driver ─────────────────────────────────────────────────────────────────

ICONS = [
    ("icon_1_smooth.png",       variant_smooth),
    ("icon_2_bright_core.png",  variant_bright_core),
    ("icon_3_concentrated.png", variant_concentrated),
    ("icon_4_peaked.png",       variant_peaked),
    ("icon_5_cinematic.png",    variant_cinematic),
]


def main() -> int:
    out_dir = os.path.join(_REPO, "docs", "screenshots", "nightglow_icons")
    os.makedirs(out_dir, exist_ok=True)
    for fn in os.listdir(out_dir):
        if fn.endswith(".png"):
            os.remove(os.path.join(out_dir, fn))
    for fname, fn in ICONS:
        scene = _dark_backdrop()
        fn(scene)
        out_path = os.path.join(out_dir, fname)
        pygame.image.save(scene, out_path)
        print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
