"""Render 5 polished NIGHTGLOW star icons — high-end casual-mobile style.

User wants a plain 5-point star that looks like a powerup token in a
top-tier casual mobile game (Royal Match, Candy Crush, Coin Master,
Subway Surfers). No external halos. Just the star itself, but with
internal depth — bevels, gradients, gloss highlights — that make it
read as a polished, premium icon.

5 takes:

    1. SMOOTH GRADIENT — clean radial bright→dark fall-off, soft.
    2. CLASSIC BEVEL   — bright top half, darker bottom half (3D).
    3. GLOSSY GEM      — beveled + glossy top highlight (Candy-Crush
                          style).
    4. FACETED         — each star point a jewel-facet with its own
                          light/dark sides.
    5. RIM-LIT         — solid star + crisp bright inner rim along
                          the silhouette edge (the high-end "neon
                          inset" look).

The chosen design gets ported into entities.py:_draw_nightglow_icon
at ~52 px native scale.

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

# Palette tuned around V5 PUNCH+'s greens — the in-world effect's
# colour family. Ramps from deep shadow → mid → bright → white-hot.
GREEN_DEEP   = ( 30, 150,  30)
GREEN_SHADOW = ( 60, 200,  50)
GREEN_MID    = (140, 250, 110)
GREEN_LIGHT  = (190, 255, 160)
GREEN_HOT    = (235, 255, 215)

OUTLINE      = ( 25, 110,  20)


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


def _aa_star_surface(r_outer, r_inner, color, outline_color=None,
                     outline_width=0):
    """Anti-aliased star on its own surface via 4× supersample.
    Returns a surface big enough to contain the star + outline."""
    SS = 4
    margin = max(outline_width + 4, 6)
    big_size = (r_outer * 2 + margin * 2) * SS
    s = pygame.Surface((big_size, big_size), pygame.SRCALPHA)
    bcx = big_size // 2
    pts = _star_points(bcx, bcx, r_outer * SS, r_inner * SS)
    pygame.draw.polygon(s, color, pts)
    if outline_color is not None and outline_width > 0:
        pygame.draw.polygon(s, outline_color, pts, outline_width * SS)
    out_size = big_size // SS
    return pygame.transform.smoothscale(s, (out_size, out_size))


def _blit_star(surf, cx, cy, r_outer, r_inner, color,
               outline_color=None, outline_width=0):
    star = _aa_star_surface(r_outer, r_inner, color,
                            outline_color, outline_width)
    surf.blit(star, (cx - star.get_width() // 2,
                     cy - star.get_height() // 2))


# Star geometry shared by every variant — same canonical 5-point shape.
R_OUT, R_IN = 78, 33


# ─── VARIANT 1 — SMOOTH GRADIENT ────────────────────────────────────────────
# Layered shrinking stars, each a step lighter — soft radial gradient
# from deep edge to bright centre.

def variant_gradient(surf):
    cx, cy = CENTER, CENTER
    # Subtle dark outline for definition
    _blit_star(surf, cx, cy, R_OUT, R_IN, OUTLINE)
    # Walk inward in shrinking colour rings
    layers = [
        (R_OUT - 2,  R_IN - 1,  GREEN_DEEP),
        (R_OUT - 8,  R_IN - 3,  GREEN_SHADOW),
        (R_OUT - 16, R_IN - 6,  GREEN_MID),
        (R_OUT - 26, R_IN - 10, GREEN_LIGHT),
        (R_OUT - 36, R_IN - 14, GREEN_HOT),
    ]
    for ro, ri, col in layers:
        _blit_star(surf, cx, cy, ro, ri, col)


# ─── VARIANT 2 — CLASSIC BEVEL ──────────────────────────────────────────────
# Bright TOP half, darker BOTTOM half — light coming from above.

def variant_bevel(surf):
    cx, cy = CENTER, CENTER
    # Outline
    _blit_star(surf, cx, cy, R_OUT, R_IN, OUTLINE)
    # Bottom half (darker) — draw full star then overlay top half bright
    _blit_star(surf, cx, cy, R_OUT - 2, R_IN - 1, GREEN_SHADOW)

    # Build a bright top half: full bright star, then erase the bottom.
    bright = _aa_star_surface(R_OUT - 2, R_IN - 1, GREEN_LIGHT)
    # Mask out the bottom half of `bright` so only its top survives.
    cut = pygame.Surface(bright.get_size(), pygame.SRCALPHA)
    cut.fill((0, 0, 0, 0))
    # Black-with-alpha=255 in the bottom region → BLEND_RGBA_SUB? Use
    # BLEND_RGBA_MIN: alpha = min(bright_alpha, cut_alpha). Cut alpha is
    # 255 in top half, 0 in bottom → bright keeps alpha only in top.
    pygame.draw.rect(cut, (255, 255, 255, 255),
                     pygame.Rect(0, 0, cut.get_width(), cut.get_height() // 2))
    bright.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(bright, (cx - bright.get_width() // 2,
                       cy - bright.get_height() // 2))


# ─── VARIANT 3 — GLOSSY GEM ─────────────────────────────────────────────────
# Beveled base + glossy white highlight ribbon over the upper portion.

def variant_glossy(surf):
    cx, cy = CENTER, CENTER
    # Beveled base
    _blit_star(surf, cx, cy, R_OUT, R_IN, OUTLINE)
    _blit_star(surf, cx, cy, R_OUT - 2, R_IN - 1, GREEN_MID)
    # Upper-half lighten — same masking trick as variant_bevel.
    light = _aa_star_surface(R_OUT - 2, R_IN - 1, GREEN_LIGHT)
    cut = pygame.Surface(light.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(cut, (255, 255, 255, 255),
                     pygame.Rect(0, 0, cut.get_width(),
                                 int(cut.get_height() * 0.55)))
    light.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(light, (cx - light.get_width() // 2,
                      cy - light.get_height() // 2))

    # Glossy ribbon — a small bright-white elliptical highlight in the
    # upper-left, sized to sit cleanly inside one of the star's lobes.
    gloss = pygame.Surface((68, 22), pygame.SRCALPHA)
    pygame.draw.ellipse(gloss, (*GREEN_HOT, 230), gloss.get_rect())
    pygame.draw.ellipse(gloss, (255, 255, 255, 180),
                        gloss.get_rect().inflate(-12, -6))
    surf.blit(gloss, (cx - 32, cy - 44))


# ─── VARIANT 4 — FACETED (each star point has its own bevel) ────────────────

def variant_faceted(surf):
    cx, cy = CENTER, CENTER
    # Outline + base
    _blit_star(surf, cx, cy, R_OUT, R_IN, OUTLINE)
    _blit_star(surf, cx, cy, R_OUT - 2, R_IN - 1, GREEN_SHADOW)

    # Compute the star points + inner valleys, then for each outer
    # point draw two triangles (centre→outer tip→left valley in bright,
    # centre→outer tip→right valley in dark) for a faceted gem look.
    outer = []
    inner = []
    for i in range(5):
        a = -math.pi / 2 + i * math.tau / 5
        outer.append((cx + (R_OUT - 4) * math.cos(a),
                      cy + (R_OUT - 4) * math.sin(a)))
    for i in range(5):
        a = -math.pi / 2 + (i + 0.5) * math.tau / 5
        inner.append((cx + (R_IN - 1) * math.cos(a),
                      cy + (R_IN - 1) * math.sin(a)))

    for i in range(5):
        tip = outer[i]
        left_valley = inner[(i - 1) % 5]
        right_valley = inner[i % 5]
        # Bright facet (left side of point)
        pygame.draw.polygon(surf, GREEN_LIGHT,
                            [(cx, cy), tip, left_valley])
        # Dark facet (right side of point)
        pygame.draw.polygon(surf, GREEN_DEEP,
                            [(cx, cy), tip, right_valley])

    # Centre highlight pop
    pygame.draw.circle(surf, GREEN_HOT, (cx, cy), 6)
    pygame.draw.circle(surf, (255, 255, 255), (cx - 2, cy - 2), 2)


# ─── VARIANT 5 — RIM-LIT (solid star + bright inner rim) ────────────────────

def variant_rim(surf):
    cx, cy = CENTER, CENTER
    # Dark outline
    _blit_star(surf, cx, cy, R_OUT, R_IN, OUTLINE)
    # Mid-tone body
    _blit_star(surf, cx, cy, R_OUT - 2, R_IN - 1, GREEN_MID)
    # Bright inner rim — slightly smaller bright star erased by a
    # smaller mid-green star, leaves a thin bright ring along the edge.
    _blit_star(surf, cx, cy, R_OUT - 5, R_IN - 2, GREEN_LIGHT)
    _blit_star(surf, cx, cy, R_OUT - 10, R_IN - 5, GREEN_MID)
    # Centre highlight dot
    pygame.draw.circle(surf, GREEN_HOT, (cx, cy), 5)


# ─── driver ─────────────────────────────────────────────────────────────────

ICONS = [
    ("icon_1_gradient.png", variant_gradient),
    ("icon_2_bevel.png",    variant_bevel),
    ("icon_3_glossy.png",   variant_glossy),
    ("icon_4_faceted.png",  variant_faceted),
    ("icon_5_rim.png",      variant_rim),
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
