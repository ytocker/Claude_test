"""Render 5 plain NIGHTGLOW star sticker candidates — no halos.

User: "just make it a plain star. No background circles. Greenish
aura-light colour matching the V5 PUNCH+ effect." So the previous
icon set's layered ambient halos are gone — each variant is the star
silhouette and nothing else, on the dark backdrop.

Colour matches the bright halo green from V5 PUNCH+ — around
(140, 250, 110) — which is what the player sees in-world during the
glow effect.

5 shape/treatment variations to pick from:

    1. PLAIN    — clean flat 5-point star (balanced proportions)
    2. SHARP    — long pointy spikes
    3. CHUNKY   — rounded points, fatter body
    4. BEVELED  — flat star + slightly darker inner star for depth
    5. TWINKLE  — main star + 1 tiny accent twinkle nearby

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

# Match V5 PUNCH+'s bright halo green — the "greenish aura light"
# colour the player actually sees in-world during the effect.
STAR_GREEN       = (140, 250, 110)
STAR_GREEN_INNER = ( 95, 220,  70)   # slightly darker, for beveled variant


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
    """Anti-aliased star via 4× supersample + smoothscale. Soft edges
    only — no halo. Returns the surface and the top-left position to
    blit it at so the star is centred on (cx, cy)."""
    SS = 4
    margin = 6
    big_size = (r_outer * 2 + margin * 2) * SS
    s = pygame.Surface((big_size, big_size), pygame.SRCALPHA)
    bcx = big_size // 2
    pts = _star_points(bcx, bcx, r_outer * SS, r_inner * SS)
    pygame.draw.polygon(s, color, pts)
    out_size = big_size // SS
    out = pygame.transform.smoothscale(s, (out_size, out_size))
    return out, (cx - out_size // 2, cy - out_size // 2)


# ─── VARIANT 1 — PLAIN (balanced 5-point) ───────────────────────────────────

def variant_plain(surf):
    star, pos = _aa_star(CENTER, CENTER,
                         r_outer=72, r_inner=30, color=STAR_GREEN)
    surf.blit(star, pos)


# ─── VARIANT 2 — SHARP (long pointy spikes) ─────────────────────────────────

def variant_sharp(surf):
    star, pos = _aa_star(CENTER, CENTER,
                         r_outer=84, r_inner=22, color=STAR_GREEN)
    surf.blit(star, pos)


# ─── VARIANT 3 — CHUNKY (rounded points, fatter body) ───────────────────────

def variant_chunky(surf):
    cx, cy = CENTER, CENTER
    star, pos = _aa_star(cx, cy,
                         r_outer=72, r_inner=42, color=STAR_GREEN)
    surf.blit(star, pos)
    # Soft rounding at each tip — a small disc plopped on each outer point.
    for i in range(5):
        a = -math.pi / 2 + i * math.tau / 5
        tx = int(cx + 72 * math.cos(a))
        ty = int(cy + 72 * math.sin(a))
        pygame.draw.circle(surf, STAR_GREEN, (tx, ty), 8)


# ─── VARIANT 4 — BEVELED (subtle inner darker star for depth) ───────────────

def variant_beveled(surf):
    cx, cy = CENTER, CENTER
    # Outer star (bright green)
    outer, opos = _aa_star(cx, cy,
                           r_outer=72, r_inner=30, color=STAR_GREEN)
    surf.blit(outer, opos)
    # Inner star slightly smaller, darker — creates a beveled-rim illusion
    inner, ipos = _aa_star(cx, cy,
                           r_outer=56, r_inner=24, color=STAR_GREEN_INNER)
    surf.blit(inner, ipos)


# ─── VARIANT 5 — TWINKLE (main star + 1 small accent) ───────────────────────

def variant_twinkle(surf):
    cx, cy = CENTER, CENTER
    main, mpos = _aa_star(cx, cy,
                          r_outer=64, r_inner=27, color=STAR_GREEN)
    surf.blit(main, mpos)
    # One tiny accent twinkle — upper-right, like a sparkle next to the star.
    tiny, tpos = _aa_star(cx + 70, cy - 64,
                          r_outer=18, r_inner=7, color=STAR_GREEN)
    surf.blit(tiny, tpos)


# ─── driver ─────────────────────────────────────────────────────────────────

ICONS = [
    ("icon_1_plain.png",   variant_plain),
    ("icon_2_sharp.png",   variant_sharp),
    ("icon_3_chunky.png",  variant_chunky),
    ("icon_4_beveled.png", variant_beveled),
    ("icon_5_twinkle.png", variant_twinkle),
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
