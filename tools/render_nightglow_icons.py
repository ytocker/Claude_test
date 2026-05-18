"""Render 5 smooth-gradient NIGHTGLOW star icons.

User picked variant 1 (GRADIENT) but said the transitions need to be
gradual / smooth. Previous version used only 5 concentric stars,
which produced visible banding. This version uses ~40 overlapping
layers with finely-interpolated colours so the gradient reads as
truly smooth at the eye.

5 takes on the smooth-gradient theme:

    1. CLASSIC     — linear bright-centre → dark-edge ramp
    2. SOFT        — ease-out curve: more of the star sits in bright
                      tones, edge darkens quickly only at the rim
    3. PUNCHY      — ease-in curve: smaller bright core, most of the
                      star is mid-tone
    4. COOL        — same as CLASSIC but with a slightly cooler
                      (mint-cyan) hot centre
    5. OUTLINED    — CLASSIC + a thin dark outline for shape definition

Geometry stays the canonical 5-point used in the prior icon set.
Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_nightglow_icons.py
"""

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

pygame.init()
pygame.display.set_mode((1, 1))


CANVAS = 240
CENTER = CANVAS // 2

# Colour stops, all in the V5 PUNCH+ green family.
GREEN_DEEP   = ( 30, 150,  30)   # outermost rim
GREEN_HOT    = (235, 255, 215)   # innermost centre
GREEN_COOL_HOT = (210, 255, 230) # cooler hot for COOL variant
OUTLINE      = ( 15,  90,  15)


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


def _aa_star(cx, cy, r_outer, r_inner, color):
    """Anti-aliased star via 4× supersample + smoothscale."""
    SS = 4
    margin = 6
    big_size = (r_outer * 2 + margin * 2) * SS
    s = pygame.Surface((big_size, big_size), pygame.SRCALPHA)
    bcx = big_size // 2
    pts = _star_points(bcx, bcx, r_outer * SS, r_inner * SS)
    pygame.draw.polygon(s, color, pts)
    out_size = big_size // SS
    return pygame.transform.smoothscale(s, (out_size, out_size))


def _blit_star(surf, cx, cy, r_outer, r_inner, color):
    star = _aa_star(cx, cy, r_outer, r_inner, color)
    surf.blit(star, (cx - star.get_width() // 2,
                     cy - star.get_height() // 2))


def _smooth_gradient_star(surf, cx, cy, r_out, r_in,
                          deep_color, hot_color, layers=42,
                          shrink_to=0.04,   # innermost layer is 4% of r_out
                          curve=None):
    """Render a star with a smooth radial colour gradient by stacking
    `layers` finely-interpolated concentric stars. With ~40 layers the
    eye reads it as a true gradient, not a sequence of rings."""
    if curve is None:
        curve = lambda t: t
    for i in range(layers + 1):
        t = i / layers                       # 0 outer → 1 inner
        ro = r_out * ((1.0 - shrink_to) * (1.0 - t) + shrink_to)
        ri = r_in  * ((1.0 - shrink_to) * (1.0 - t) + shrink_to)
        if ro < 3:
            continue
        ct = curve(t)
        color = tuple(int(deep_color[c] + (hot_color[c] - deep_color[c]) * ct)
                      for c in range(3))
        _blit_star(surf, cx, cy, int(round(ro)), int(round(ri)), color)


R_OUT, R_IN = 78, 33


# ─── easing curves ──────────────────────────────────────────────────────────

def _linear(t):     return t
def _ease_out(t):   return 1 - (1 - t) ** 2.2     # slows toward bright
def _ease_in(t):    return t ** 2.2               # bright core small


# ─── VARIANT 1 — CLASSIC SMOOTH ─────────────────────────────────────────────

def variant_classic(surf):
    _smooth_gradient_star(surf, CENTER, CENTER, R_OUT, R_IN,
                          GREEN_DEEP, GREEN_HOT,
                          layers=42, curve=_linear)


# ─── VARIANT 2 — SOFT (ease-out: wider bright zone) ─────────────────────────

def variant_soft(surf):
    _smooth_gradient_star(surf, CENTER, CENTER, R_OUT, R_IN,
                          GREEN_DEEP, GREEN_HOT,
                          layers=46, curve=_ease_out)


# ─── VARIANT 3 — PUNCHY (ease-in: small concentrated bright core) ───────────

def variant_punchy(surf):
    _smooth_gradient_star(surf, CENTER, CENTER, R_OUT, R_IN,
                          GREEN_DEEP, GREEN_HOT,
                          layers=46, curve=_ease_in)


# ─── VARIANT 4 — COOL (mint-cyan hot centre) ────────────────────────────────

def variant_cool(surf):
    _smooth_gradient_star(surf, CENTER, CENTER, R_OUT, R_IN,
                          GREEN_DEEP, GREEN_COOL_HOT,
                          layers=42, curve=_linear)


# ─── VARIANT 5 — OUTLINED (classic + thin dark rim for definition) ──────────

def variant_outlined(surf):
    # Dark outline pass first — slightly larger star in deep colour.
    _blit_star(surf, CENTER, CENTER, R_OUT + 2, R_IN + 1, OUTLINE)
    _smooth_gradient_star(surf, CENTER, CENTER, R_OUT, R_IN,
                          GREEN_DEEP, GREEN_HOT,
                          layers=42, curve=_linear)


# ─── driver ─────────────────────────────────────────────────────────────────

ICONS = [
    ("icon_1_classic.png",  variant_classic),
    ("icon_2_soft.png",     variant_soft),
    ("icon_3_punchy.png",   variant_punchy),
    ("icon_4_cool.png",     variant_cool),
    ("icon_5_outlined.png", variant_outlined),
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
